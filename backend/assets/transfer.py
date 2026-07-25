"""Transfer lifecycle: an asset moves to a new custodian through an approval gate."""
from django.utils import timezone

from accounts.models import users_with_permission
from core.services import notify

from .models import AssetTransfer, LifecycleError


def request_transfer(asset, new_owner, requested_by, *, new_department=None,
                      condition=None, remarks=""):
    transfer = AssetTransfer.objects.create(
        asset=asset,
        previous_owner=asset.custodian,
        previous_department=asset.department,
        new_owner=new_owner,
        new_department=new_department or new_owner.department,
        requested_by=requested_by,
        condition=condition or asset.condition,
        remarks=remarks or "",
    )
    for approver in users_with_permission("asset_transfer"):
        notify(approver, f"Transfer request for {asset.asset_id} awaiting approval.",
               link="/transfer?status=Pending")
    return transfer


def approve(transfer, approved_by):
    if transfer.status != "Pending":
        raise LifecycleError("This transfer has already been processed.")

    transfer.status = "Approved"
    transfer.approved_by = approved_by
    transfer.transfer_date = timezone.now()
    transfer.save()

    asset = transfer.asset
    asset.custodian = transfer.new_owner
    asset.department = transfer.new_department or asset.department
    asset.status = "Assigned"
    if transfer.condition:
        asset.condition = transfer.condition
    asset.save()

    notify(transfer.new_owner, f"Asset {asset.asset_id} has been transferred to you.",
           link=f"/asset/{asset.id}")
    if transfer.previous_owner:
        notify(transfer.previous_owner,
               f"Asset {asset.asset_id} has been transferred from your custody.",
               link=f"/asset/{asset.id}")
    return transfer


def reject(transfer, approved_by):
    if transfer.status != "Pending":
        raise LifecycleError("This transfer has already been processed.")

    transfer.status = "Rejected"
    transfer.approved_by = approved_by
    transfer.save()

    if transfer.requested_by:
        notify(transfer.requested_by,
               f"Transfer request TRF-{transfer.id:05d} was rejected.", link="/transfer")
    return transfer
