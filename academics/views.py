"""Faculty-side attendance API: session start/refresh/end + check-in."""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.shortcuts import get_object_or_404

from academics import qr
from academics.models import AttendanceSession, Attendance, Subject
from accounts.audit import write_audit
from accounts.decorators import role_required, approved_teacher_required

User = __import__("django.contrib.auth", fromlist=["get_user_model"]).get_user_model()


def _json_err(status, message, code=""):
    return JsonResponse(
        {"status": "error", "message": message, "code": code},
        status=status,
    )


@approved_teacher_required
def start_session(request):
    if request.method != "POST":
        return _json_err(405, "Method not allowed")

    subject = get_object_or_404(Subject, pk=request.POST.get("subject_id"))

    session = AttendanceSession.objects.create(
        subject=subject,
        teacher=request.user,
        expires_at=timezone.now() + timezone.timedelta(minutes=30),
    )
    write_audit(request.user, "ATTENDANCE_SESSION_STARTED", session,
                session.subject.code)

    return JsonResponse({"status": "ok", "session_id": session.pk,
                         "token": session.token})


@approved_teacher_required
def refresh_token(request):
    session = get_object_or_404(
        AttendanceSession, pk=request.GET.get("session")
    )

    if session.teacher != request.user:
        return _json_err(403, "Not your session", "forbidden")

    if not session.is_active or session.closed_at is not None:
        return _json_err(403, "Session is closed", "closed")

    if session.token_bucket != qr.current_bucket():
        qr.rotate(session)

    return JsonResponse({
        "status": "ok",
        "token": session.token,
        "rotates_in": qr.seconds_to_rotation(),
        "present": session.records.count(),
        "present_list": [
            {
                "name": r.student.fullname,
                "roll": r.student.roll_no,
                "time": r.marked_at.strftime("%H:%M:%S"),
            }
            for r in session.records.select_related(
                "student__user")[:40]
        ],
    })


@approved_teacher_required
def end_session(request, pk):
    if request.method != "POST":
        return _json_err(405, "Method not allowed")

    session = get_object_or_404(AttendanceSession, pk=pk)

    if session.teacher != request.user:
        return _json_err(403, "Not your session", "forbidden")

    session.is_active = False
    session.closed_at = timezone.now()
    session.save(update_fields=["is_active", "closed_at"])
    write_audit(request.user, "ATTENDANCE_SESSION_ENDED", session,
                session.subject.code)

    return JsonResponse({"status": "ok",
                         "present": session.records.count()})


@role_required(User.Roles.STUDENT)
def check_in(request):
    if request.method != "POST":
        return _json_err(405, "Method not allowed")

    session = get_object_or_404(
        AttendanceSession, pk=request.POST.get("session_id")
    )

    if not session.is_active or session.closed_at is not None:
        return _json_err(403, "Session is not live", "closed")

    ok_token, _reason = qr.verify(session, request.POST.get("token", ""))
    if not ok_token:
        return _json_err(403, "Invalid or expired token", "bad_token")

    if Attendance.objects.filter(
        session=session, student=request.user.student_profile
    ).exists():
        return _json_err(409, "Already checked in")

    Attendance.objects.create(
        session=session,
        student=request.user.student_profile,
        status="present",
    )
    write_audit(request.user, "ATTENDANCE_CHECKED_IN", session,
                session.subject.code)

    return JsonResponse({"status": "ok", "present": session.records.count()})
