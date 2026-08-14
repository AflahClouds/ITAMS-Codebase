"""Audit logging and notification helpers."""
import logging

from django.conf import settings
from django.db import transaction

from .models import AuditLog, Notification, NotificationFailure

logger = logging.getLogger(__name__)

DELIVERY_ATTEMPTS = 2


def get_profile(request):
    """Employee profile linked to the authenticated account (or None)."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return None
    return getattr(user, "profile", None)


def client_ip(request):
    """The caller's address, treating a forwarded header as hearsay by default.

    B8 FR-023: `X-Forwarded-For` is client-supplied on any request that does not pass
    through a proxy we control, so trusting it unconditionally lets a caller choose the
    address recorded against their own actions. It is honoured only when the direct peer
    is a configured trusted proxy; otherwise the peer address is recorded.
    """
    peer = request.META.get("REMOTE_ADDR", "")
    trusted = getattr(settings, "ITAMS_TRUSTED_PROXIES", ())
    if peer and peer in trusted:
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return peer


def log_action(request, action, module, old_value="", new_value=""):
    """Write the audit entry for a business action.

    B8 FR-011 and ALR-005 make the entry and its business change one operation. That
    boundary is the request transaction (`ATOMIC_REQUESTS`), not anything this function
    does: if the write here fails, the exception propagates and the business change
    rolls back with it. Callers must therefore not swallow it.
    """
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


def log_denial(request, action, module, detail=""):
    """Audit a rejected attempt without disclosing what was refused.

    B8 FR-014 requires security-relevant rejections to be audited, and FR-016 requires
    it for every rejected AuditLog access attempt — the case that matters most, since an
    unaudited denial means probing the audit trail leaves no trace in it.
    """
    log_action(request, action, module, new_value=detail)


def _deliver(rows):
    # A savepoint, so a failed delivery cannot poison the surrounding request
    # transaction that the business change is committing in.
    with transaction.atomic():
        Notification.objects.bulk_create(rows)


def _record_failure(rows, error, attempts):
    try:
        with transaction.atomic():
            NotificationFailure.objects.bulk_create([
                NotificationFailure(recipient=row.user, message=row.message,
                                    link=row.link, error=str(error)[:500],
                                    attempts=attempts)
                for row in rows])
    except Exception:  # pragma: no cover - the failure record is best-effort
        logger.exception("Could not record a Notification delivery failure")


def notify(profile, message, link=""):
    if profile is None:
        return []
    return notify_many([profile], message, link=link)


def notify_many(profiles, message, link=""):
    """Deliver one message to a group, and never fail the caller's business action.

    Two rules from B8 shape this. FR-012 and ALR-005 put delivery outside the atomic
    boundary: a delivery failure must leave completed business work intact, retry
    without creating duplicates, and stay visible to an operator until resolved. So this
    retries within a savepoint — the rows from a failed attempt were rolled back, so a
    retry cannot duplicate them — and records a `NotificationFailure` rather than
    raising once the attempts are spent.

    It also issues one INSERT rather than one per recipient: the daily expiry sweep fans
    out over assets x recipients, which makes a per-recipient create cost the product of
    the two.
    """
    rows = [Notification(user=profile, message=message, link=link or "")
            for profile in profiles if profile is not None]
    if not rows:
        return []

    last_error = None
    for attempt in range(1, DELIVERY_ATTEMPTS + 1):
        try:
            _deliver(rows)
            return rows
        except Exception as exc:
            last_error = exc
            logger.warning("Notification delivery attempt %s of %s failed: %s",
                           attempt, DELIVERY_ATTEMPTS, exc)

    _record_failure(rows, last_error, DELIVERY_ATTEMPTS)
    return []
