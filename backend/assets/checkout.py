"""Checkout lifecycle: an asset loops between Available and Assigned to one user."""
from django.db import transaction
from django.utils import timezone

from core.services import notify

from .models import ASSET_CONDITIONS, Asset, AssetCheckout, LifecycleError


def close_all_open_checkouts(asset, note=""):
    """Close out every Open checkout on asset — the same effect check_in() has, without
    touching asset.status (the caller owns that). Used when something other than a normal
    check-in pulls the asset out from under an active checkout, so no return_condition
    input is available — unlike check_in(), it reuses the asset's current condition."""
    closed = []
    for checkout in asset.checkouts.filter(status="Open"):
        checkout.return_date = timezone.now()
        checkout.return_condition = asset.condition
        checkout.remarks = (f"{checkout.remarks} " if checkout.remarks else "") + note
        checkout.status = "Returned"
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
        if user.department:
            asset.department = user.department
        asset.save()

    notify(user, f"Asset {asset.asset_id} has been checked out to you.",
           link=f"/asset/{asset.id}")
    return checkout


def check_in(checkout, condition, remarks=""):
    if checkout.status == "Returned":
        raise LifecycleError("This checkout is already closed.")
    if condition not in ASSET_CONDITIONS:
        raise LifecycleError(f"Condition must be one of {ASSET_CONDITIONS}")

    with transaction.atomic():
        checkout.return_date = timezone.now()
        checkout.return_condition = condition
        checkout.remarks = (remarks or "").strip()
        checkout.status = "Returned"
        checkout.save()

        asset = checkout.asset
        asset.status = "Available"
        asset.custodian = None
        asset.condition = condition
        asset.save()

    notify(checkout.user, f"Asset {asset.asset_id} check-in recorded. Thank you.",
           link=f"/asset/{asset.id}")
    return checkout
