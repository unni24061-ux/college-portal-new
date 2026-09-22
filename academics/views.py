from datetime import timedelta

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from accounts.audit import write_audit
from accounts.decorators import approved_teacher_required, role_required
from accounts.models import User

from . import qr
from .models import Attendance, AttendanceSession, Subject


def _json_err(status, message, code=""):
    return JsonResponse(
        {"status": "error", "code": code, "message": message},
        status=status,
    )


@approved_teacher_required
def start_session(request):
    if request.method != "POST":
        return _json_err(405, "Method not allowed")

    subject_id = request.POST.get("subject_id")
    try:
        minutes = int(request.POST.get("duration_minutes", 60))
    except (TypeError, ValueError):
        minutes = 60

    if minutes < 1 or minutes > 240:
        return _json_err(400, "Invalid duration", "invalid_duration")

    subject = get_object_or_404(Subject, pk=subject_id)

    session = AttendanceSession.objects.create(
        subject=subject,
        teacher=request.user,
        expires_at=timezone.now() + timedelta(minutes=minutes),
    )
    token = qr.new_token(session)
    write_audit(request.user, "ATTENDANCE_SESSION_STARTED", session, subject.code)

    return JsonResponse({
        "status": "ok",
        "session_id": session.pk,
        "subject": {"id": subject.pk, "name": subject.name, "code": subject.code},
        "token": token,
        "ttl": qr.ROTATION_SECONDS,
        "rotates_in": qr.seconds_to_rotation(),
        "expires_at": session.expires_at.isoformat(),
    })


@approved_teacher_required
def refresh_token(request):
    session = get_object_or_404(AttendanceSession, pk=request.GET.get("session"))

    if not session.is_live():
        return _json_err(403, "Session is closed", "closed")
    if session.expires_at <= timezone.now():
        return _json_err(410, "Session has expired", "expired")

    if session.token_bucket != qr.current_bucket():
        qr.rotate(session)

    return JsonResponse({
        "status": "ok",
        "session_id": session.pk,
        "token": session.token,
        "ttl": qr.ROTATION_SECONDS,
        "rotates_in": qr.seconds_to_rotation(),
        "present": session.records.count(),
    })


@approved_teacher_required
def end_session(request, pk):
    if request.method != "POST":
        return _json_err(405, "Method not allowed")

    session = get_object_or_404(AttendanceSession, pk=pk)
    session.is_active = False
    session.closed_at = timezone.now()
    session.save(update_fields=['is_active', 'closed_at'])
    write_audit(request.user, "ATTENDANCE_SESSION_ENDED", session, session.subject.code)

    return JsonResponse({"status": "ok", "present": session.records.count()})


@role_required(User.Roles.STUDENT)
def check_in(request):
    if request.method != "POST":
        return _json_err(405, "Method not allowed")

    session = get_object_or_404(AttendanceSession, pk=request.POST.get("session_id"))
    token = request.POST.get("token", "")

    if not session.is_live():
        return _json_err(403, "Attendance session is closed", "closed")
    if session.expires_at <= timezone.now():
        return _json_err(410, "Attendance session has expired", "expired")

    ok, reason = qr.verify(session, token)
    if not ok:
        return _json_err(400, "Invalid or expired QR token", reason)
    if token != session.token:
        return _json_err(400, "Invalid or expired QR token", "stale")

    profile = request.user.student_profile

    if Attendance.objects.filter(session=session, student=profile).exists():
        return JsonResponse(
            {"status": "error", "code": "already_marked", "message": "Already marked present"},
            status=409,
        )

    record = Attendance.objects.create(session=session, student=profile)
    write_audit(request.user, "ATTENDANCE_CHECKIN", record, session.subject.code)

    return JsonResponse({
        "status": "ok",
        "session_id": session.pk,
        "subject": session.subject.code,
    })
