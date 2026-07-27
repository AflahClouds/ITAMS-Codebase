"""Proactive Warranty/AMC expiry alerts, run daily by core.scheduler."""
from datetime import date, timedelta

from accounts.models import users_with_permission
from core.services import notify

from .models import AmcContract, Asset

THRESHOLD_DAYS = (30, 15, 7)


def check_expiring_dates():
    """Notify IT Manager + IT Staff when a Warranty or AMC hits 30/15/7 days to expiry.

    Exact-date match (not a range): since this runs once a day, each threshold fires
    exactly once per asset as the countdown passes through it.
    """
    recipients = users_with_permission("asset_custody_manage")  # IT Manager + IT Staff (+ Admin)
    if not recipients:
        return

    for days in THRESHOLD_DAYS:
        target = date.today() + timedelta(days=days)

        for asset in Asset.objects.filter(warranty_end=target):
            message = f"Warranty for {asset.asset_id} expires in {days} days."
            for user in recipients:
                notify(user, message, link=f"/asset/{asset.id}")

        for contract in AmcContract.objects.filter(status="Active", end_date=target).select_related('asset'):
            asset = contract.asset
            message = f"AMC for {asset.asset_id} expires in {days} days."
            for user in recipients:
                notify(user, message, link=f"/asset/{asset.id}")
