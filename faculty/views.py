from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . models import faculty_profile, Announcement
from students.models import student_profile
from django.contrib import messages
from django.db.models import Q, Count
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.db.models.functions import TruncDate

from academics.models import AttendanceSession, Attendance, Subject, Grade
from academics import grading
from accounts.audit import write_audit
from academics import qr, analytics


# Create your views here.
@login_required(login_url='login_p')
def dashboard(request):

    profile = faculty_profile.objects.filter(user=request.user).first()

    # Live sessions I own
    live = AttendanceSession.objects.filter(
        teacher=request.user, is_active=True, closed_at__isnull=True
    )

    # Attendance marked today for my subjects
    present_today = Attendance.objects.filter(
        session__teacher=request.user,
        marked_at__date=timezone.localdate(),
    )

    # Sessions + subjects I teach
    subs = AttendanceSession.objects.filter(teacher=request.user) \
        .values('subject__code', 'subject__name') \
        .annotate(sessions=Count('id'))

    # Present count by subject (all time, mine)
    att_by_subject = []
    for s in subs:
        total = Attendance.objects.filter(
            session__teacher=request.user,
            session__subject__code=s['subject__code'],
        ).count()
        att_by_subject.append({
            'code': s['subject__code'],
            'name': s['subject__name'],
            'sessions': s['sessions'],
            'present': total,
        })

    # Shared analytics: 14-day trend, at-risk students, rankings, grade dist
    trend = analytics.attendance_trend(request.user, 14)
    at_risk = analytics.at_risk_students(request.user)
    rankings = analytics.rank_students()[:5]
    grade_dist = analytics.grade_distribution
    subjects = Subject.objects.all()

    dist_for = None
    if subjects:
        dist_for = grade_dist(subjects.first(), subjects.first().sem)

    return render(request, 'faculty/faculty_dash.html', {
        'profile': profile,
        'live_sessions': live,
        'subjects': subjects,
        'present_today': present_today.count(),
        'att_by_subject': att_by_subject,
        'trend': trend,
        'at_risk': at_risk,
        'rankings': rankings,
        'grade_dist': dist_for,
        'announcement_count': Announcement.objects.count(),
    })


@login_required(login_url='login_p')
def f_profile(request):
    profile = faculty_profile.objects.get(user=request.user)
    return render(request, 'faculty/faculty_myprofile.html', {'profile': profile})


@login_required(login_url='login_p')
def f_edit_profile(request):

    profile = faculty_profile.objects.get(user=request.user)

    if request.method == "POST":

        fullname = request.POST.get("fullname", "").strip()

        if fullname:
            profile.fullname = fullname

        department = request.POST.get("department", "").strip()

        if department:
            profile.department = department
        else:
            profile.department = None

        designation = request.POST.get("designation", "").strip()

        if designation:
            profile.designation = designation
        else:
            profile.designation = None

        ph_no = request.POST.get("phone_number", "").strip()

        if ph_no:
            profile.ph_no = ph_no
        else:
            profile.ph_no = None

        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")

        profile.save()

        email = request.POST.get("email", "").strip()

        if email:
            request.user.email = email
            request.user.save()

        messages.success(request, "Profile updated successfully!")

        return redirect("facu_profile")

    return redirect("facu_profile")


@login_required(login_url='login_p')
def stud_manage(request):
    students = student_profile.objects.all()

    search = request.GET.get('search', '').strip()

    if search:
        q = (
            Q(fullname__icontains=search) |
            Q(user__email__icontains=search) |
            Q(department__icontains=search) |
            Q(ktu_id__icontains=search)
        )

        if search.isdigit():
            q = q | Q(roll_no__exact=int(search))

        students = students.filter(q)

    department = request.GET.get('department')

    if department:
        students = students.filter(department__iexact=department)

    sem = request.GET.get('sem')

    if sem:
        students = students.filter(sem=sem)

    return render(request, 'faculty/student_manage.html', {'students': students})


@login_required(login_url='login_p')
def preview(request, id):
    student = student_profile.objects.get(id=id)
    return render(request, 'faculty/preview_pro.html', {'student': student})


@login_required(login_url='login_p')
def edit_pro_f(request, id):

    profile = student_profile.objects.get(id=id)

    if request.method == "POST":

        # Full Name
        fullname = request.POST.get("fullname", "").strip()

        if fullname:
            profile.fullname = fullname

        # Department
        department = request.POST.get("department", "").strip()

        if department:
            profile.department = department
        else:
            profile.department = None

        # Semester
        sem = request.POST.get("sem", "").strip()

        if sem in ("", "None", "null"):
            profile.sem = None
        else:
            profile.sem = int(sem)

        # KTU ID
        ktu_id = request.POST.get("ktu_id", "").strip()

        if ktu_id:
            profile.ktu_id = ktu_id
        else:
            profile.ktu_id = None

        # Phone Number
        ph_no = request.POST.get("ph_no", "").strip()

        if ph_no:
            profile.ph_no = ph_no
        else:
            profile.ph_no = None

        # Roll Number
        roll_no = request.POST.get("roll_no", "").strip()

        if roll_no in ("", "None", "null"):
            profile.roll_no = None
        else:
            profile.roll_no = int(roll_no)

        # Date of Birth
        dob = request.POST.get("dob", "").strip()

        if dob:
            profile.dob = dob
        else:
            profile.dob = None

        # CGPA
        cgpa = request.POST.get("cgpa", "").strip()

        if cgpa in ("", "None", "null"):
            profile.cgpa = None
        else:
            profile.cgpa = float(cgpa)

        # Profile Image
        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")

        profile.save()

        messages.success(request, "Profile updated successfully!")

        return redirect("preview", id=id)

    return redirect("preview", id=id)


@login_required(login_url='login_p')
def campus_connect(request):
    role = request.GET.get('role', 'student')

    if role == 'faculty':
        directory = faculty_profile.objects.all()
    else:
        role = 'student'
        directory = student_profile.objects.all()

    search = request.GET.get('search', '').strip()

    if search:
        q = (
            Q(fullname__icontains=search) |
            Q(user__email__icontains=search) |
            Q(department__icontains=search)
        )

        if role == 'student':
            q = q | Q(ktu_id__icontains=search)
            if search.isdigit():
                q = q | Q(roll_no__exact=int(search))

        directory = directory.filter(q)

    department = request.GET.get('department')

    if department:
        directory = directory.filter(department__icontains=department)

    if role == 'student':
        sem = request.GET.get('sem')

        if sem:
            directory = directory.filter(sem=sem)

    return render(request, 'faculty/campus_connect.html', {
        'directory': directory,
        'role': role,
    })


@login_required(login_url='login_p')
def announcement(request):

    if request.method == "POST":

        title = request.POST.get("title")
        message = request.POST.get("message")

        if title and message:

            Announcement.objects.create(
                title=title,
                message=message,
                created_by=request.user
            )

            messages.success(request, "Announcement published successfully!")

            return redirect("f_notification")

    return render(request, 'faculty/announcement.html')


@login_required(login_url='login_p')
def notification(request):

    announcements = Announcement.objects.all().order_by(
        '-created_at'
    )

    return render(
        request,
        'faculty/notification.html',
        {
            'announcements': announcements
        }
    )


# ---------------------------------------------------------------------------
# Developer B - QR attendance + grade entry

@login_required(login_url='login_p')
def rankings(request):
    """Class performance rankings by CGPA, grouped by semester."""
    sem_values = [s for s in student_profile.objects.values_list('sem', flat=True).distinct() if s is not None]
    tables = []
    for sem in sorted(sem_values, reverse=True):
        tables.append({
            'sem': sem,
            'rows': analytics.rank_students(sem=sem),
        })
    return render(request, 'faculty/rankings.html', {
        'tables': tables,
        'sectors': analytics.grade_distribution,
    })

# ---------------------------------------------------------------------------

@login_required(login_url='login_p')
def attendance_manager(request):
    live = AttendanceSession.objects.filter(
        teacher=request.user, is_active=True, closed_at__isnull=True
    )
    recent = AttendanceSession.objects.filter(teacher=request.user) \
        .order_by('-started_at')[:12]

    return render(request, 'faculty/attendance_manage.html', {
        'subjects': Subject.objects.all(),
        'live_sessions': live,
        'recent_sessions': recent,
    })


@login_required(login_url='login_p')
def session_display(request, pk):
    session = AttendanceSession.objects.filter(pk=pk).first()

    if session is None or session.teacher != request.user:
        return HttpResponseForbidden("Not your session.")

    return render(request, 'faculty/session_display.html', {
        'session': session,
        'records': session.records.select_related('student__user')[:40],
        'live': session.is_live(),
    })


@login_required(login_url='login_p')
def grade_entry(request):
    subject_id = request.GET.get('subject')
    sem = request.GET.get('sem')

    if subject_id:
        subject = Subject.objects.filter(pk=subject_id).first()
    else:
        subject = None

    rows = []

    if subject and sem:
        sem_int = int(sem) if str(sem).isdigit() else None
        subject_obj = subject

        if sem_int:
            roster = student_profile.objects.filter(sem=sem_int).order_by('roll_no', 'fullname')
            semester = sem_int
        else:
            roster = student_profile.objects.all().order_by('roll_no', 'fullname')
            semester = subject.sem

        for s in roster:
            existing = None

            if semester:
                existing = Grade.objects.filter(
                    student=s, subject=subject_obj, sem=semester
                ).first()

            rows.append({
                'student': s,
                'existing': existing,
            })

    return render(request, 'faculty/grade_entry.html', {
        'subjects': Subject.objects.all(),
        'subject': subject,
        'sem': sem,
        'rows': rows,
        'live_sessions': AttendanceSession.objects.filter(
            teacher=request.user, is_active=True, closed_at__isnull=True
        ),
    })


@login_required(login_url='login_p')
def grade_save(request):
    if request.method != "POST":
        return redirect('f_grade')

    subject_id = request.POST.get('subject')
    sem = request.POST.get('sem')

    subject = Subject.objects.filter(pk=subject_id).first() if subject_id else None

    if subject is None or not str(sem).isdigit():
        messages.error(request, "Pick a subject and a semester first.")
        return redirect('f_grade')

    semester = int(sem)
    saved = 0

    for key, value in request.POST.items():
        if not key.startswith('marks_'):
            continue

        try:
            sid = int(key.split('_', 1)[1])
        except ValueError:
            continue

        marks_text = (value or '').strip()

        if not marks_text:
            continue

        try:
            marks = float(marks_text)
        except ValueError:
            continue

        marks = max(0.0, min(100.0, marks))
        letter = grading.grade_for_marks(marks)
        profile = student_profile.objects.filter(pk=sid).first()

        if profile is None:
            continue

        existing = Grade.objects.filter(
            student=profile, subject=subject, sem=semester
        ).first()

        if existing:
            existing.marks = marks
            existing.grade = letter
            existing.updated_by = request.user
            existing.save()
        else:
            existing = Grade.objects.create(
                student=profile, subject=subject, sem=semester,
                marks=marks, grade=letter, updated_by=request.user,
            )

        write_audit(request.user, "GRADE_SAVED", existing,
                    f"{profile.user.username}:{subject.code}:{letter}")
        saved += 1

    messages.success(request, f"Saved/updated grades for {saved} student(s).")
    return redirect(f"{request.path}?subject={subject.pk}&sem={semester}")
