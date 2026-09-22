"""Shared QR attendance engine.

A 30-second rotating, HMAC-signed token that lets a student prove they are
looking at the teacher's live screen. The current token is stored on the
``AttendanceSession`` row so it survives serverless deployments; client JS
re-polls a refresh endpoint before each rotation.
"""
import hashlib
import hmac
import time

from django.conf import settings

ROTATION_SECONDS = 30


def _sign(session_id, bucket):
    msg = f"{session_id}|{bucket}".encode("utf-8")
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        msg,
        hashlib.sha256,
    ).hexdigest()


def current_bucket():
    return int(time.time() // ROTATION_SECONDS)


def rotate(session):
    """Store a fresh token for the current time bucket."""
    session.token_bucket = current_bucket()
    session.token = f"{session.token_bucket}.{_sign(session.pk, session.token_bucket)}"
    session.save(update_fields=['token', 'token_bucket'])
    return session.token


def new_token(session):
    return rotate(session)


def seconds_to_rotation():
    return max(1, ROTATION_SECONDS - int(time.time() % ROTATION_SECONDS))


def verify(session, token):
    """Validate a presented token. Returns (ok, reason)."""
    try:
        bucket_str, sig = token.split(".", 1)
        bucket = int(bucket_str)
    except (ValueError, AttributeError):
        return False, "malformed"

    cur = current_bucket()
    # Accept the current bucket or the previous one to tolerate clock/network lag.
    if bucket not in (cur, cur - 1):
        return False, "expired"

    if not hmac.compare_digest(_sign(session.pk, bucket), sig):
        return False, "invalid"

    return True, "ok"