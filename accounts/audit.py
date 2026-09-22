from .models import AuditLog


def write_audit(actor, action, target=None, detail=""):
    """Record a portal event in the audit log (shared foundation)."""
    return AuditLog.objects.create(
        actor=actor,
        action=action,
        target_type=target.__class__.__name__ if target else "",
        target_id=str(target.pk) if target else "",
        detail=detail,
    )