"""Checkout lifecycle: an asset loops between Available and Assigned to one user."""
from django.db import transaction
from django.utils import timezone

from core.services import notify

from .models import (ASSET_CONDITIONS, Asset, AssetCheckout, AssetConditionLog,
                     LifecycleError)


def close_all_open_checkouts(asset, note=""):
    """Close out every Open checkout on asset — the same effect check_in() has, without
    touching asset.status (the caller owns that). Used when something other than a normal
    check-in pulls the asset out from under an active checkout, so no return_condition
    input is available — unlike check_in(), it reuses the asset's current condition."""
    closed = []
    for checkout in asset.checkouts.filter(status="Open"):
        checkout.return_date = timezone.now()
        checkout.return_condition = asset.condition
        checkout.return_remarks = (
            f"{checkout.return_remarks} " if checkout.return_remarks else "") + note
        checkout.status = "Returned"
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
        if asset.status != "Available":
            raise LifecycleError("This asset is not available for checkout.")

        checkout = AssetCheckout.objects.create(
            asset=asset,
            user=user,
            approved_by=approved_by,
            checkout_condition=checkout_condition or asset.condition,
            expected_return_date=expected_return_date,
            purpose=purpose or "",
            remarks=remarks or "",
        )
        asset.status = "Assigned"
        asset.custodian = user
        # B3 FR-006: department follows the holder. If the new holder has none, the
        # previous holder's department must not be left in place — it would file the
        # Asset under a department that no longer has anything to do with it.
        asset.department = user.department
        asset.save()

    notify(user, f"Asset {asset.asset_id} has been checked out to you.",
           link=f"/asset/{asset.id}")
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
    if checkout.status == "Returned":
        raise LifecycleError("This checkout is already closed.")
    if not condition:
        raise LifecycleError("A return condition is required to check in this asset.")
    if condition not in ASSET_CONDITIONS:
        raise LifecycleError(f"Condition must be one of {ASSET_CONDITIONS}")
    # B3 FR-014: an Asset coming back worse than it went out is the one case where the
    # operator has something to say, and the one case where silence loses it.
    if (condition_worsened(checkout.checkout_condition, condition)
            and not (remarks or "").strip()):
        raise LifecycleError(
            "This asset is being returned in a worse condition than it went out. "
            "Record what happened in the return remarks.")

    with transaction.atomic():
        checkout.return_date = timezone.now()
        checkout.return_condition = condition
        checkout.return_remarks = (remarks or "").strip()
        checkout.status = "Returned"
        checkout.save()

        asset = checkout.asset
        asset.status = "Available"
        asset.custodian = None
        # Department follows custody: it was set from the holder at checkout, so it
        # clears with them rather than leaving the asset filed under a department
        # that no longer holds it.
        asset.department = None
        asset.condition = condition
        asset.save()

        # A check-in is an inspection — record it whether or not the condition moved,
        # so the history shows the asset was looked at on return.
        AssetConditionLog.objects.create(
            asset=asset, inspector=performed_by, condition=condition,
            notes="Recorded at check-in.")

    notify(checkout.user, f"Asset {asset.asset_id} check-in recorded. Thank you.",
           link=f"/asset/{asset.id}")
    return checkout
