import os, sys, django, io
REPO = r"C:\Users\adilz\AppData\Local\Temp\opencode\college-portal-fix"
sys.path.insert(0, REPO)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "collegePortal.settings")
django.setup()

from django.test.client import Client, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone

from academics import qr, grading
from academics.models import (Department, Course, Subject, AttendanceSession, Attendance,
                              Grade)
from faculty.models import faculty_profile
from students.models import student_profile
from accounts.audit import write_audit

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
teacher = User.objects.create_user("tfacB", "tfacB@x.com", "pass12345", role=User.Roles.TEACHER)
fprof = faculty_profile.objects.update_or_create(user=teacher, defaults=dict(fullname="Dr Tea", is_approved=True, department="CSE"))
teacher_other = User.objects.create_user("tfacB2", "tfacB2@x.com", "pass12345",
                                         role=User.Roles.TEACHER)
faculty_profile.objects.update_or_create(user=teacher_other, defaults=dict(fullname="Other Prof", is_approved=True, department="CSE"))

def mkstudent(name, roll, sem=5):
    u = User.objects.create_user(name.lower(), name.lower() + "@x.com", "pass12345",
                                 role=User.Roles.STUDENT)
    return student_profile.objects.create(user=u, fullname=name, department="CSE",
                                          sem=sem, roll_no=roll, ktu_id="KTU" + str(roll))

s1 = mkstudent("Alpha", 1)
s2 = mkstudent("Beta", 2)
s3 = mkstudent("Gamma", 3, sem=4)

c = Client(SERVER_NAME="127.0.0.1")
c.login(username="tfacB", password="pass12345")

c2 = Client(SERVER_NAME="127.0.0.1")
c2.login(username="tfacB2", password="pass12345")

# ------------- dashboard -------------
r = c.get("/facultydash/")
ok(r.status_code == 200, "faculty dashboard 200")
body = r.content.decode("utf-8", "ignore")
ok("at-risk" in body, "dashboard shows at-risk section")

# ------------- start session (POST) -------------
r = c.post("/attendance/start/", {"subject_id": subject.pk,
                                  "duration_minutes": 20})
ok(r.status_code == 200, "attendance_start returns 200")
ok(r["Content-Type"].startswith("application/json"), "start returns JSON")
sid = r.json()["session_id"]
sess = AttendanceSession.objects.get(pk=sid)
ok(sess.token, "session token auto-generated on create")
ok(sess.is_active and not sess.closed_at, "session active + not closed")
token1 = sess.token

ok(qr.decode_payload(qr.encode_payload(sess)) == (sess.pk, sess.token),
   "qr payload roundtrip")

# ------------- owner guard on refresh/end ---------------- 
r = c2.get("/attendance/refresh/?session=" + str(sid))
ok(r.status_code == 403, "stranger refresh blocked (403)")
r = c2.post("/attendance/end/" + str(sid) + "/", {})
ok(r.status_code == 403, "stranger end blocked (403)")
r = c2.get("/attendance/" + str(sid) + "/")
ok(r.status_code == 403, "stranger session display blocked")

# ------------- refresh (owner) -------------
r = c.get("/attendance/refresh/?session=" + str(sid))
ok(r.status_code == 200, "owner refresh 200")
d = r.json()
ok(d["status"] == "ok", "refresh ok")
ok("token" in d and "present_list" in d and "rotates_in" in d,
   "refresh payload has token/present_list/rotates_in")
ok(d["present"] == 0, "no presents yet")
sess.refresh_from_db()
ok(bool(sess.token), "token persisted")

# ------------- checkin flow -------------
tok = sess.token
sc = Client(SERVER_NAME="127.0.0.1")
sc.login(username="alpha", password="pass12345")
r = sc.post("/attendance/checkin/", {"session_id": sid, "token": tok})
ok(r.status_code == 200, "checkin 200")
ok(r.json().get("status") == "ok", "checkin ok")
att = Attendance.objects.filter(session=sess, student=s1).first()
ok(att is not None and att.status == "present", "Attendance record created")

# duplicate
r = sc.post("/attendance/checkin/", {"session_id": sid, "token": tok})
ok(r.status_code == 409, "duplicate checkin 409")

# st flash token
r = sc.post("/attendance/checkin/", {"session_id": sid, "token": "cpatt:9999:bad"})
ok(r.status_code == 403, "bad token rejected 403")

# refresh sees present
r = c.get("/attendance/refresh/?session=" + str(sid))
d = r.json()
ok(d["present"] == 1, "refresh sees 1 present")
ok(len(d["present_list"]) == 1, "present_list has 1")
ok(d["present_list"][0]["roll"] == 1, "present_list roll matches")

# ------------- session display (owner) -------------
r = c.get("/attendance/" + str(sid) + "/")
ok(r.status_code == 200, "session display 200")
ok(b"Alpha" in r.content and b"PRESENT" in r.content.upper() or
   b"PRESENT" in r.content, "session page shows present student")
ok("cpatt:" in r.content.decode("utf-8", "ignore")
   or "cpatt" in r.content.decode("utf-8", "ignore"),
   "session page references cpatt payload")

# ------------- end session -------------
r = c.post("/attendance/end/" + str(sid) + "/", {})
ok(r.status_code == 200, "end session 200")
sess.refresh_from_db()
ok(sess.is_active is False and sess.closed_at is not None, "session closed")
r = c.get("/attendance/refresh/?session=" + str(sid))
ok(r.status_code == 403, "refresh after close blocked")

# ------------- grades -------------
r = c.get("/grades/?subject=" + str(subject.pk) + "&sem=5")
ok(r.status_code == 200, "grade entry 200")
ok(b"Alpha" in r.content and b"Beta" in r.content, "roster lists students")
ok(b"Gamma" not in r.content, "roster filters by sem")

# upsert save
r = c.post("/grades/save/", {
    "subject": str(subject.pk),
    "sem": "5",
    "marks_" + str(s1.pk): "91",
    "marks_" + str(s2.pk): "82",
})
ok(r.status_code == 302, "grade save redirects")
g1 = Grade.objects.filter(student=s1, subject=subject, sem=5).first()
g2 = Grade.objects.filter(student=s2, subject=subject, sem=5).first()
ok(g1 is not None and g1.marks == 91.0 and g1.grade == "S", "g1 grade S/91")
ok(g2 is not None and g2.marks == 82.0 and g2.grade == "A+", "g2 grade A+/82")

# update existing
r = c.post("/grades/save/", {
    "subject": str(subject.pk),
    "sem": "5",
    "marks_" + str(s1.pk): "95",
})
g1.refresh_from_db()
ok(g1.marks == 95.0 and g1.grade == "S", "grade updated on re-save")
ok(Grade.objects.count() == 2, "no duplicate grades created")

# grade_for_marks boundaries
ok(grading.grade_for_marks(100) == "S", "100 -> S")
ok(grading.grade_for_marks(90) == "S", "90 -> S")
ok(grading.grade_for_marks(89.9) == "A+", "89.9 -> A+")
ok(grading.grade_for_marks(49) == "F", "49 -> F")

print(f"\nRESULT: {len(passed)} passed, {len(failed)} failed")
for f in failed:
    print("  FAIL -", f)
sys.exit(1 if failed else 0)
