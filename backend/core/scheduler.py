"""In-app background scheduler for periodic jobs (Warranty/AMC expiry alerts).

Known limitation: this runs inside the Django process itself, so under a multi-worker
WSGI deployment it would fire once per worker, and it only runs while the process is up.
Accepted for now — the next version should move this to a management command triggered by
an external scheduler instead.
"""
import logging

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

_scheduler = None


def start():
    global _scheduler
    if _scheduler is not None:
        return

    from assets.alerts import check_expiring_dates

    from .retention import purge_expired

    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.add_job(check_expiring_dates, trigger="cron", hour=7, minute=0,
                       id="check_expiring_dates", replace_existing=True)
    # B8 FR-017 retention: AuditLog entries at 2 years, their source IP at 6 months,
    # Read Notifications 90 days after becoming Read, Unread ones a year after
    # creation. Runs after the alert sweep so a purge never races an alert.
    _scheduler.add_job(purge_expired, trigger="cron", hour=3, minute=30,
                       id="retention_purge", replace_existing=True)
    _scheduler.start()
    logger.info("Background scheduler started: check_expiring_dates daily at 07:00, "
                "retention purge daily at 03:30.")
