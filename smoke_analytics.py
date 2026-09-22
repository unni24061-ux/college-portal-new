import os, sys, django, io
REPO = r"C:\Users\adilz\AppData\Local\Temp\opencode\college-portal-fix"
sys.path.insert(0, REPO)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "collegePortal.settings")
django.setup()

from django.test.client import Client
from django.contrib.auth import get_user_model
from django.utils import timezone

from academics import analytics, grading
from academics.models import (Department, Course, Subject, AttendanceSession, Attendance,
                              Grade)
from faculty.models import faculty_profile
from students.models import student_profile

User = get_user_model()

passed, failed = [], []

def ok(cond, name):
    (passed if cond else failed).append(name)
    if not cond:
        print("FAIL:", name)

# ------------- seed -------------
User.objects.all().delete()
dept, _ = Department.objects.get_or_create(code="CSE", defaults=dict(name="Computer Science"))
course, _ = Course.objects.get_or_create(code="CSE", defaults=dict(name="Computer Science", duration_sems=8, department=dept))
subject, _ = Subject.objects.get_or_create(code="CS301", defaults=dict(name="Databases", sem=5, course=course))
teacher = User.objects.create_user("tfacA", "tfacA@x.com", "pass12345", role=User.Roles.TEACHER)
faculty_profile.objects.update_or_create(user=teacher, defaults=dict(fullname="Dr Tea", is_approved=True, department="CSE"))

def mkstudent(name, roll, sem=5):
    u = User.objects.create_user(name.lower(), name.lower() + "@x.com", "pass12345",
                                 role=User.Roles.STUDENT)
    return student_profile.objects.create(user=u, fullname=name, department="CSE",
                                          sem=sem, roll_no=roll, ktu_id="KTU" + str(roll))

s1 = mkstudent("Alpha", 1)
s2 = mkstudent("Beta", 2)
s3 = mkstudent("Gamma", 3, sem=4)

# grades: Alpha 91 -> S (gpa 10), Beta 82 -> A+ (gpa 9)
Grade.objects.create(student=s1, subject=subject, sem=5, marks=91.0, grade="S", updated_by=teacher)
Grade.objects.create(student=s2, subject=subject, sem=5, marks=82.0, grade="A+", updated_by=teacher)

# attendance: Alpha present in sess1 only => 50%, both at-risk
end = timezone.now() + timezone.timedelta(minutes=30)
sess1 = AttendanceSession.objects.create(subject=subject, teacher=teacher, expires_at=end, is_active=True)
Attendance.objects.create(session=sess1, student=s1)
Attendance.objects.create(session=sess1, student=s2)
sess2 = AttendanceSession.objects.create(subject=subject, teacher=teacher, expires_at=end, is_active=True)

c = Client(SERVER_NAME="127.0.0.1")
c.login(username="tfacA", password="pass12345")
sc = Client(SERVER_NAME="127.0.0.1")
sc.login(username="alpha", password="pass12345")

# ------------- shared analytics layer -------------
ok(analytics.overall_cgpa(s1) == 10.0, "cgpa Alpha = 10 (S)")
ok(analytics.overall_cgpa(s2) == 9.0, "cgpa Beta = 9 (A+)")
ok(analytics.overall_cgpa(s3) is None, "cgpa Gamma None (no grades)")
ok([x['sem'] for x in analytics.gpa_by_sem(s1)] == [5], "gpa_by_sem sem list")

att = analytics.attendance_by_subject(s1)
ok(att and att[0]['percent'] == 50.0, "attendance_by_subject 50%")
ok(att[0]['at_risk'] is True, "attendance_by_subject flags at_risk")
ok(analytics.attendance_overall(s1) == 50.0, "attendance_overall 50%")

tr = analytics.attendance_trend(teacher, days=14)
ok(len(tr) == 14, "trend covers 14 days")
ok(sum(t['present'] for t in tr) == 2, "trend sums to 2 presents")

at_risk = analytics.at_risk_students(teacher)
ok({x.fullname for x in at_risk} == {"Alpha", "Beta"}, "at_risk catches Alpha+Beta")

dist = analytics.grade_distribution(subject, 5)
ok({'grade': 'S', 'count': 1} in dist and {'grade': 'A+', 'count': 1} in dist,
   "grade_distribution counts match")

ranks = analytics.rank_students(sem=5)
ok(ranks[0]['rank'] == 1 and ranks[0]['student'].fullname == "Alpha", "rank1 Alpha")
ok(ranks[1]['rank'] == 2 and ranks[1]['student'].fullname == "Beta", "rank2 Beta")
ok(ranks[0]['cgpa'] > ranks[1]['cgpa'], "ranked by CGPA desc")
ok(len(analytics.rank_students()) >= 3, "all-sem rankings include Gamma")

# ------------- rollover guard: reporting delegates -------------
from students import reporting
ok(reporting.overall_cgpa(s1) == 10.0, "reporting delegates cgpa to analytics")
ok(reporting.attendance_overall(s1) == 50.0, "reporting delegates attendance")

# ------------- faculty dashboard: analytics sections -------------
r = c.get("/facultydash/")
ok(r.status_code == 200, "faculty dashboard 200")
body = r.content.decode("utf-8", "ignore")
ok("at-risk" in body, "dash shows at-risk section")
ok("Alpha" in body and "Beta" in body, "dash at-risk lists students")
ok("trend-data" in body, "dash embeds trend-data")
ok("subject-data" in body, "dash embeds subject-data")
ok("chart.js" in body.lower() or "chart.umd.min.js" in body, "dash loads chart.js")
ok("Top Performers" in body, "dash shows top performers")
ok("#1" in body and "Alpha" in body, "dash top performer rank #1")
ok("/rankings/" in body, "dash links to rankings page")

# ------------- rankings page -------------
r = c.get("/rankings/")
ok(r.status_code == 200, "rankings page 200")
body = r.content.decode("utf-8", "ignore")
ok("PERFORMANCE RANKINGS" in body, "rankings header present")
ok("SEMESTER 5" in body, "rankings lists semester 5")
ok("Alpha" in body and "Beta" in body, "rankings rows include students")
ok("#1" in body and "Alpha" in body, "rankings rank #1")
ok("10.0" in body and "9.0" in body, "rankings show CGPAs")

# ------------- student dashboard: class rank -------------
r = sc.get("/studash/")
ok(r.status_code == 200, "student dashboard 200")
body = r.content.decode("utf-8", "ignore")
ok("Class Rank" in body, "student dash shows class rank")
ok("#1" in body and "/ 2" in body, "student dash rank 1/2")
ok(analytics.overall_cgpa(s1) == 10.0, "student context keeps overall cgpa")

print(f"\nRESULT: {len(passed)} passed, {len(failed)} failed")
for f in failed:
    print("  FAIL -", f)
sys.exit(1 if failed else 0)