"""Audit logging and notification helpers."""
from .models import AuditLog, Notification


def get_profile(request):
    """Employee profile linked to the authenticated account (or None)."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return None
    return getattr(user, "profile", None)


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def log_action(request, action, module, old_value="", new_value=""):
    profile = get_profile(request)
    username = ""
    if getattr(request, "user", None) and request.user.is_authenticated:
        username = request.user.username
    AuditLog.objects.create(
        user=profile,
        username=username,
        action=action,
        module=module,
        old_value=old_value or "",
        new_value=new_value or "",
        ip_address=client_ip(request),
    )


def notify(profile, message, link=""):
    if profile is None:
        return
    Notification.objects.create(user=profile, message=message, link=link or "")
