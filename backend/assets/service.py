"""Service Record lifecycle: an asset goes to a Vendor for repair, then comes back Available."""
from django.db import transaction
from django.utils import timezone

from core.services import notify

from .models import LifecycleError, ServiceRecord, TERMINAL_STATUSES

TERMINAL_OR_ACTIVE_SERVICE_STATUSES = ("Under Repair",) + TERMINAL_STATUSES


def open_service(asset, vendor, opened_by, *, expected_return_date=None, reason="", remarks=""):
    if asset.status in TERMINAL_OR_ACTIVE_SERVICE_STATUSES:
        raise LifecycleError(f"This asset cannot be sent for service while {asset.status}.")

    previous_custodian = asset.custodian

    with transaction.atomic():
        # Sending a checked-out asset straight to service mirrors Checkout's check-in
        # (ADR 0001) — so any open checkout it interrupts must be closed the same way
        # check_in() would, or it's left dangling "Open" with no asset to check back in.
        open_checkout = asset.checkouts.filter(status="Open").order_by('-checkout_date').first()
        if open_checkout:
            open_checkout.status = "Returned"
            open_checkout.return_date = timezone.now()
            open_checkout.return_condition = asset.condition
            open_checkout.remarks = (
                f"{open_checkout.remarks} " if open_checkout.remarks else ""
            ) + "Auto-closed: asset sent for service."
            open_checkout.save()

        record = ServiceRecord.objects.create(
            asset=asset,
            vendor=vendor,
            opened_by=opened_by,
            expected_return_date=expected_return_date,
            reason=reason or "",
            remarks=remarks or "",
        )
        asset.status = "Under Repair"
        asset.custodian = None
        asset.save()

    if previous_custodian:
        notify(previous_custodian,
               f"Asset {asset.asset_id} has been sent to {vendor.name} for service.",
               link=f"/asset/{asset.id}")
    return record


def close_service(record, closed_by, *, cost=None, remarks=""):
    if record.status == "Closed":
        raise LifecycleError("This service record is already closed.")

    with transaction.atomic():
        record.status = "Closed"
        record.returned_date = timezone.now()
        record.closed_by = closed_by
        record.cost = cost
        record.remarks = remarks or record.remarks
        record.save()

        asset = record.asset
        asset.status = "Available"
        asset.save()

    return record
