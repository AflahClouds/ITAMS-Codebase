"""Temporary Checkout and physical Check-in lifecycle."""
import logging

from django.db import transaction
from django.utils import timezone

from core.services import notify

from .models import (ASSET_CONDITIONS, Asset, AssetCheckout, AssetConditionLog,
                     LifecycleError)


logger = logging.getLogger(__name__)


def _notify_checkout(user, asset):
    try:
        notify(user, f"Asset {asset.asset_id} has been checked out to you.",
               link=f"/asset/{asset.id}")
    except Exception:
        logger.exception("Could not notify temporary custodian for asset %s", asset.pk)


def _notify_checkin(user, asset):
    try:
        notify(user, f"Asset {asset.asset_id} check-in recorded. Thank you.",
               link=f"/asset/{asset.id}")
    except Exception:
        logger.exception("Could not notify former temporary custodian for asset %s", asset.pk)


def close_all_open_checkouts(asset, note=""):
    """End displaced Checkout records without asserting a physical Check-in."""
    closed = []
    for checkout in asset.checkouts.filter(status="Open"):
        checkout.status = "Returned"
        checkout.closure_reason = "Interrupted"
        checkout.closed_at = timezone.now()
        # B3 FR-028: this closure was not a return. Marking it keeps an interrupted
        # Checkout distinguishable from one an operator actually checked back in.
        checkout.closed_as_interrupted = True
        checkout.save()
        closed.append(checkout)
    return closed


def check_out(asset, user, approved_by, *, checkout_condition=None,
              expected_return_date=None, purpose="", remarks=""):
    with transaction.atomic():
        # select_for_update() is a no-op on the project's current SQLite backend (no
        # row locking support) — this guards against the TOCTOU race once/if the
        # project moves to Postgres/MySQL; harmless here either way.
        asset = Asset.objects.select_for_update().get(pk=asset.pk)
        # Keep the shared current-custody interpretation authoritative. A legacy
        # active record can conflict even when the Asset snapshot says Available.
        from .custody import custody_type
        if (asset.status != "Available" or asset.custodian_id is not None or
                custody_type(asset) != "None"):
            raise LifecycleError("This asset is not available for checkout.")

        updated = Asset.objects.filter(
            pk=asset.pk, status="Available", custodian__isnull=True,
        ).update(status="Assigned", custodian=user, department=user.department,
                 modified=timezone.now())
        if updated != 1:
            raise LifecycleError("This asset's custody changed. Reload and try again.")
        checkout = AssetCheckout.objects.create(
            asset=asset,
            user=user,
            approved_by=approved_by,
            checkout_condition=checkout_condition or asset.condition,
            expected_return_date=expected_return_date,
            purpose=purpose or "",
            remarks=remarks or "",
            classification="Temporary",
        )
        transaction.on_commit(lambda: _notify_checkout(user, asset))
    return checkout


# Best to worst. A return that moves an Asset down this list needs an explanation.
CONDITION_RANK = {name: rank for rank, name in enumerate(ASSET_CONDITIONS)}


def condition_worsened(before, after):
    """Whether a return needs explaining.

    `New` -> `Good` is excluded. "New" describes an Asset that has not been used yet
    rather than a level of care, so the first return of a new Asset in good order is the
    expected outcome, not a deterioration. Demanding a note there would put a
    justification prompt on the most ordinary check-in in the system and teach operators
    to type nothing into it.
    """
    if before not in CONDITION_RANK or after not in CONDITION_RANK:
        return False
    if before == "New" and after == "Good":
        return False
    return CONDITION_RANK[after] > CONDITION_RANK[before]


def check_in(checkout, condition, remarks="", performed_by=None):
    if not condition:
        raise LifecycleError("A return condition is required to check in this asset.")
    if condition not in ASSET_CONDITIONS:
        raise LifecycleError(f"Condition must be one of {ASSET_CONDITIONS}")
    remarks = (remarks or "").strip()
    with transaction.atomic():
        asset = Asset.objects.select_for_update().get(pk=checkout.asset_id)
        record = AssetCheckout.objects.select_for_update().select_related('user').get(
            pk=checkout.pk)
        if record.status != "Open":
            raise LifecycleError("This checkout is already closed.")
        if record.classification != "Temporary":
            raise LifecycleError("Classify this legacy Checkout before Check-in.")
        from .custody import custody_type
        if (asset.status != "Assigned" or asset.custodian_id != record.user_id or
                custody_type(asset) != "Temporary"):
            raise LifecycleError("This Checkout is no longer the current temporary custody.")
        # B3 FR-014 compares against the fresh issue record, not stale input.
        if condition_worsened(record.checkout_condition, condition) and not remarks:
            raise LifecycleError(
                "This asset is being returned in a worse condition than it went out. "
                "Record what happened in the return remarks.")

        now = timezone.now()
        updated = Asset.objects.filter(
            pk=asset.pk, status="Assigned", custodian_id=record.user_id,
        ).update(status="Available", custodian=None, department=None,
                 condition=condition, modified=now)
        if updated != 1:
            raise LifecycleError("This asset's custody changed. Reload and try again.")
        closed = AssetCheckout.objects.filter(
            pk=record.pk, status="Open", classification="Temporary",
        ).update(return_date=now, closed_at=now, return_condition=condition,
                 return_remarks=remarks, status="Returned", closure_reason="Returned")
        if closed != 1:
            raise LifecycleError("This Checkout is no longer open.")

        # A check-in is an inspection — record it whether or not the condition moved,
        # so the history shows the asset was looked at on return.
        AssetConditionLog.objects.create(
            asset=asset, inspector=performed_by, condition=condition,
            notes="Recorded at check-in.")
        transaction.on_commit(lambda: _notify_checkin(record.user, asset))
    record.refresh_from_db()
    return record
