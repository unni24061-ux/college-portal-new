from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone

from accounts.decorators import role_required
from accounts.models import User
from academics.models import AttendanceSession, Grade

from .models import student_profile
from . import reporting
from academics.analytics import rank_students


def _profile(request):
    return student_profile.objects.filter(user=request.user).first()


@role_required(User.Roles.STUDENT)
def dashboard(request):
    profile = _profile(request)
    gpa_sems = reporting.gpa_by_sem(profile) if profile else []
    attendance = reporting.attendance_by_subject(profile) if profile else []

    my_rank = None
    if profile:
        table = rank_students(sem=profile.sem)
        for row in table:
            if row['student'].user_id == profile.user_id:
                my_rank = {'rank': row['rank'], 'total': len(table)}
                break

    return render(request, 'students/student_dash.html', {
        'profile': profile,
        'gpa_sems': gpa_sems,
        'attendance': attendance,
        'my_rank': my_rank,
        'attendance_risk': [r for r in attendance if r['at_risk']],
        'overall_cgpa': reporting.overall_cgpa(profile) if profile else None,
        'attendance_overall': reporting.attendance_overall(profile) if profile else None,
        'badge_count': len(reporting.earned_badges(profile)) if profile else 0,
    })


@role_required(User.Roles.STUDENT)
def s_profile(request):
    profile = student_profile.objects.get(user=request.user)
    return render(request, 'students/stud_myprofile.html', {'profile': profile})


@role_required(User.Roles.STUDENT)
def edit_profile(request):

    profile = student_profile.objects.get(user=request.user)

    if request.method == "POST":

        # Full Name
        fullname = request.POST.get("fullname", "").strip()

        if fullname:
            profile.fullname = fullname

        # Department
        department = request.POST.get("department", "").strip()

        if department:
            profile.department = department

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

        messages.success(
            request,
            "Profile updated successfully!"
        )

        return redirect("stud_profile")

    return redirect("stud_profile")


@role_required(User.Roles.STUDENT)
def grade_report(request):
    profile = student_profile.objects.get(user=request.user)

    grades = list(
        Grade.objects
        .filter(student=profile)
        .select_related('subject', 'updated_by')
        .order_by('sem', 'subject__code')
    )

    by_sem = {}
    for g in grades:
        by_sem.setdefault(g.sem, []).append(g)

    sems = []
    total_credits = 0
    for sem in sorted(by_sem):
        pts = [reporting._points(g.grade) for g in by_sem[sem]]
        total_credits += sum((g.subject.credits or 1) for g in by_sem[sem])
        sems.append({
            'sem': sem,
            'grades': by_sem[sem],
            'gpa': round(sum(pts) / len(pts), 2),
        })

    return render(request, 'students/grade_report.html', {
        'profile': profile,
        'sems': sems,
        'overall_cgpa': reporting.overall_cgpa(profile),
        'total_credits': total_credits,
    })


@role_required(User.Roles.STUDENT)
def attendance_history(request):
    profile = student_profile.objects.get(user=request.user)
    attendance = reporting.attendance_by_subject(profile)

    return render(request, 'students/attendance_history.html', {
        'profile': profile,
        'attendance': attendance,
        'attendance_overall': reporting.attendance_overall(profile),
        'at_risk': [r for r in attendance if r['at_risk']],
    })


@role_required(User.Roles.STUDENT)
def attendance_scan(request):
    active_sessions = (
        AttendanceSession.objects
        .filter(is_active=True, expires_at__gt=timezone.now())
        .select_related('subject')
        .order_by('-started_at')
    )
    return render(request, 'students/attendance_scan.html', {
        'active_sessions': active_sessions,
    })


@role_required(User.Roles.STUDENT)
def my_badges(request):
    profile = student_profile.objects.get(user=request.user)
    badges = reporting.earned_badges(profile)
    return render(request, 'students/badges.html', {
        'profile': profile,
        'badges': badges,
        'overall_cgpa': reporting.overall_cgpa(profile),
        'attendance_overall': reporting.attendance_overall(profile),
    })