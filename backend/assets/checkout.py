"""Checkout lifecycle: an asset loops between Available and Assigned to one user."""
from django.utils import timezone

from core.services import notify

from .models import ASSET_CONDITIONS, AssetCheckout, LifecycleError


def check_out(asset, user, approved_by, *, checkout_condition=None,
              expected_return_date=None, purpose="", remarks=""):
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
