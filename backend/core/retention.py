"""Retention periods required by B8 FR-017, and the job that enforces them.

Four periods, each measured from a different event:

* AuditLog entries: 2 years from the event.
* Source IP on an AuditLog entry: 6 months, removed **without deleting the entry** —
  the address is protected data with a shorter life than the accountability record it
  sits on.
* Read Notifications: 90 days from becoming Read (hence `Notification.read_at`).
* Unread Notifications: 1 year from creation.

`purge_expired` is idempotent and safe to run repeatedly; the scheduler calls it daily.
Presentation code should also call `ip_is_expired` rather than trusting that the job has
run, so a value past its window is never served just because the process restarted.
"""
import logging

from django.utils import timezone

from .models import AuditLog, Notification

logger = logging.getLogger(__name__)

AUDIT_ENTRY_DAYS = 730       # 2 years
AUDIT_IP_DAYS = 183          # 6 months
READ_NOTIFICATION_DAYS = 90
UNREAD_NOTIFICATION_DAYS = 365


def _cutoff(days):
    return timezone.now() - timezone.timedelta(days=days)


def ip_is_expired(when):
    """True once a captured source address has passed its six-month window."""
    return when is not None and when < _cutoff(AUDIT_IP_DAYS)


def purge_expired():
    """Apply every FR-017 period. Returns a count per rule, for the operator log."""
    counts = {
        "audit_entries": AuditLog.objects.filter(
            date__lt=_cutoff(AUDIT_ENTRY_DAYS)).delete()[0],
        # The entry survives; only the address is cleared.
        "audit_ips": AuditLog.objects.filter(
            date__lt=_cutoff(AUDIT_IP_DAYS)).exclude(ip_address="").update(ip_address=""),
        "read_notifications": Notification.objects.filter(
            status="Read", read_at__lt=_cutoff(READ_NOTIFICATION_DAYS)).delete()[0],
        "unread_notifications": Notification.objects.filter(
            status="Unread", created__lt=_cutoff(UNREAD_NOTIFICATION_DAYS)).delete()[0],
    }
    logger.info("Retention purge: %s", counts)
    return counts
