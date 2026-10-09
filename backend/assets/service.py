"""Service Record lifecycle: an asset goes to a Vendor for repair, then comes back Available."""
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from accounts.models import users_with_permission
from core.services import notify, notify_many

from .custody import interrupt_active_custody
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
        # B5 FR-015: closed because something else took the Asset, not because the
        # repair finished. A vendor return date would claim a return not observed.
        record.closed_as_interrupted = True
        record.closing_remarks = (
            f"{record.closing_remarks} " if record.closing_remarks else "") + note
        record.save()
        closed.append(record)
    return closed


def open_service(asset, vendor, opened_by, *, expected_return_date=None, reason="", remarks=""):
    with transaction.atomic():
        asset = Asset.objects.select_for_update().get(pk=asset.pk)
        if asset.status in TERMINAL_OR_ACTIVE_SERVICE_STATUSES:
            raise LifecycleError(f"This asset cannot be sent for service while {asset.status}.")
        # B5 FR-008: an Asset in storage is not in use and has no fault to report. It
        # must be brought back into circulation before it can be sent for repair.
        if asset.status == "In Storage":
            raise LifecycleError(
                "This asset is In Storage; return it to Available before sending it "
                "for service.")

        previous_custodian = asset.custodian

        interrupt_active_custody(asset, "Service", opened_by)

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
        # B5 FR-005: department follows custody. The Asset is with a vendor, not with
        # the department that was using it.
        asset.department = None
        asset.save()

    if previous_custodian:
        notify(previous_custodian,
               f"Asset {asset.asset_id} has been sent to {vendor.name} for service.",
               link=f"/asset/{asset.id}")
    return record


def close_service(record, closed_by, *, cost=None, remarks=""):
    if record.status == "Closed":
        raise LifecycleError("This service record is already closed.")
    # B5 FR-010 and ALR-005: the Asset must still be the one this record is about. If
    # something else moved it since, closing here would put it back to Available from a
    # state this record knows nothing about. Read the status fresh — a `record.asset`
    # loaded earlier in the request would report what was true when it was fetched,
    # which is exactly the staleness this check exists to catch.
    current_status = Asset.objects.filter(pk=record.asset_id).values_list(
        'status', flat=True).first()
    if current_status != "Under Repair":
        raise LifecycleError(
            f"This asset is {current_status}, not Under Repair; this service "
            "record can no longer be closed against it.")
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
        # Closing notes are their own record. Replacing `remarks` destroyed what the
        # sender wrote about why the Asset went out (B5 FR-030).
        record.closing_remarks = (remarks or "").strip()
        record.save()

        asset = record.asset
        asset.status = "Available"
        asset.save()

    notify_many(users_with_permission("asset_custody_manage"),
                f"Asset {asset.asset_id} has returned from {record.vendor.name} "
                f"and is Available.",
                link=f"/asset/{asset.id}")
    return record
