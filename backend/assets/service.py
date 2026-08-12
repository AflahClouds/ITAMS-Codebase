"""Service Record lifecycle: an asset goes to a Vendor for repair, then comes back Available."""
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from accounts.models import users_with_permission
from core.services import notify, notify_many

from .checkout import close_all_open_checkouts
from .models import Asset, LifecycleError, ServiceRecord, TERMINAL_STATUSES

TERMINAL_OR_ACTIVE_SERVICE_STATUSES = ("Under Repair",) + TERMINAL_STATUSES


def close_all_open_service_records(asset, note=""):
    """Close out every Open service record on asset without touching asset.status —
    the caller owns that. Used when something other than a normal close pulls the asset
    out from under an active repair, so — unlike close_service() — no closed_by/cost is
    recorded; there's no operator confirming the repair actually finished."""
    closed = []
    for record in asset.service_records.filter(status="Open"):
        record.status = "Closed"
        record.returned_date = timezone.now()
        record.remarks = (f"{record.remarks} " if record.remarks else "") + note
        record.save()
        closed.append(record)
    return closed


def open_service(asset, vendor, opened_by, *, expected_return_date=None, reason="", remarks=""):
    with transaction.atomic():
        asset = Asset.objects.select_for_update().get(pk=asset.pk)
        if asset.status in TERMINAL_OR_ACTIVE_SERVICE_STATUSES:
            raise LifecycleError(f"This asset cannot be sent for service while {asset.status}.")

        previous_custodian = asset.custodian

        # Sending a checked-out asset straight to service mirrors Checkout's check-in
        # (ADR 0001) — so any open checkout it interrupts must be closed the same way
        # check_in() would, or it's left dangling "Open" with no asset to check back in.
        close_all_open_checkouts(asset, note="Auto-closed: asset sent for service.")

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
    if cost is None or str(cost).strip() == "":
        # Closing is where the repair's price becomes known. Zero is a valid answer
        # (in-warranty, goodwill); absent is not, or vendor spend can never be totalled.
        raise LifecycleError(
            "A cost is required to close this service record. Enter 0 for no charge.")
    try:
        cost = Decimal(str(cost))
    except (InvalidOperation, ValueError):
        raise LifecycleError("Cost must be a number.")
    if cost < 0:
        raise LifecycleError("Cost cannot be negative.")

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

    notify_many(users_with_permission("asset_custody_manage"),
                f"Asset {asset.asset_id} has returned from {record.vendor.name} "
                f"and is Available.",
                link=f"/asset/{asset.id}")
    return record
