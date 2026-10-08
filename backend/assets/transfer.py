"""Transfer lifecycle for one exact ongoing Assignment."""
import logging
from types import SimpleNamespace

from django.db import transaction
from django.utils import timezone

from accounts.models import User, users_with_permission
from core.services import log_action, notify, notify_many

from .custody import TEMPORARY_HOLDER_ERROR, confirmed_temporary_holder, custody_type
from .models import (Asset, AssetAssignment, AssetCheckout, AssetTransfer,
                     LifecycleError, TERMINAL_STATUSES)

# Under Repair means an open Service Record has custody (asset.custodian is already
# cleared) — unlike Checkout, Transfer has no business interrupting that; there's no
# current holder to hand off from, and the asset is physically at the vendor, not with
# whoever the transfer would name as previous_owner.
NOT_TRANSFERABLE_STATUSES = ("Under Repair",) + TERMINAL_STATUSES
logger = logging.getLogger(__name__)


def _require_actor(actor, permission):
    if (actor is None or actor.status != "Active" or not actor.account_id
            or not actor.account.is_active or not actor.can(permission)):
        raise LifecycleError("You cannot perform this Transfer action.")


def _audit_request(actor, request):
    return request or SimpleNamespace(user=actor.account, META={})


def _notify_request(asset):
    try:
        notify_many(users_with_permission("asset_custody_manage"),
                    f"Transfer request for {asset.asset_id} awaiting approval.",
                    link="/transfer?status=Pending")
    except Exception:
        logger.exception("Could not notify approvers for asset %s", asset.pk)


def _notify_decision(transfer, approved):
    try:
        if approved:
            notify(transfer.new_owner,
                   f"Asset {transfer.asset.asset_id} has been transferred to you.",
                   link=f"/asset/{transfer.asset_id}")
            if transfer.previous_owner and transfer.previous_owner.status == "Active":
                notify(transfer.previous_owner,
                       f"Asset {transfer.asset.asset_id} has been transferred from your custody.",
                       link=f"/asset/{transfer.asset_id}")
        elif transfer.requested_by:
            notify(transfer.requested_by,
                   f"Transfer request TRF-{transfer.pk:05d} was rejected.", link="/transfer")
    except Exception:
        logger.exception("Could not notify parties for Transfer %s", transfer.pk)


def request_transfer(asset, new_owner, requested_by, *, new_department=None,
                      condition=None, remarks="", request=None):
    _require_actor(requested_by, "transfer_request")
    with transaction.atomic():
        current = Asset.objects.select_for_update().get(pk=asset.pk)
        if confirmed_temporary_holder(current, new_owner):
            raise LifecycleError(TEMPORARY_HOLDER_ERROR)
        if current.status in NOT_TRANSFERABLE_STATUSES:
            raise LifecycleError(f"This asset is {current.status} and cannot be transferred.")
        if custody_type(current) != "Ongoing":
            raise LifecycleError("This asset needs one confirmed ongoing Assignment before Transfer. Classify or resolve conflicting custody first.")
        if current.custodian_id == new_owner.pk:
            raise LifecycleError("This asset is already in that user's custody.")
        if AssetTransfer.objects.filter(asset=current, status="Pending").exists():
            raise LifecycleError("This asset already has a transfer request awaiting approval.")
        target = User.objects.select_for_update().get(pk=new_owner.pk)
        if target.status != "Active" or not target.account_id or not target.account.is_active:
            raise LifecycleError("The employee must be active to receive an asset.")
        source = AssetAssignment.objects.get(asset=current, status="Open")
        transfer = AssetTransfer.objects.create(
            asset=current, source_assignment=source,
            previous_owner=source.user, previous_department=current.department,
            new_owner=target, new_department=new_department or target.department,
            requested_by=requested_by, condition=condition or current.condition,
            remarks=(remarks or "").strip(),
        )
        log_action(
            _audit_request(requested_by, request), "Transfer Request", "Transfers",
            old_value=f"{current.asset_id} | Assigned | {source.user.user_name} | Ongoing | Assignment {source.pk}",
            new_value=f"TRF-{transfer.pk:05d} | Pending | {target.user_name} | source Assignment {source.pk} | {transfer.remarks}",
        )
        transaction.on_commit(lambda: _notify_request(current))
    return transfer


def approve(transfer, approved_by, *, request=None):
    _require_actor(approved_by, "asset_custody_manage")
    with transaction.atomic():
        asset = Asset.objects.select_for_update().get(pk=transfer.asset_id)
        transfer = AssetTransfer.objects.select_for_update().select_related(
            "source_assignment", "previous_owner", "new_owner").get(pk=transfer.pk)
        if transfer.status != "Pending":
            raise LifecycleError("This transfer has already been processed.")
        if asset.status in NOT_TRANSFERABLE_STATUSES:
            raise LifecycleError(f"This asset is {asset.status} and cannot be transferred.")
        if custody_type(asset) == "Temporary":
            raise LifecycleError(
                "This asset is in temporary Checkout. Record Check-in before Transfer approval.")
        if custody_type(asset) != "Ongoing" or not transfer.source_assignment_id:
            raise LifecycleError("The source Assignment is no longer confirmed ongoing custody.")
        source = AssetAssignment.objects.select_for_update().get(
            pk=transfer.source_assignment_id)
        if (source.asset_id != asset.pk or source.status != "Open" or
                source.user_id != transfer.previous_owner_id or
                asset.custodian_id != source.user_id or
                asset.department_id != transfer.previous_department_id or
                AssetAssignment.objects.filter(asset=asset, status="Open").exclude(
                    pk=source.pk).exists() or
                AssetCheckout.objects.filter(asset=asset, status="Open").exists()):
            raise LifecycleError("This Transfer's source Assignment or department changed.")
        target = User.objects.select_for_update().get(pk=transfer.new_owner_id)
        if (target.pk == source.user_id or target.status != "Active" or
                not target.account_id or not target.account.is_active):
            raise LifecycleError("The target employee is no longer eligible for Transfer.")

        now = timezone.now()
        updated = Asset.objects.filter(
            pk=asset.pk, status="Assigned", custodian_id=source.user_id,
            department_id=transfer.previous_department_id,
        ).update(custodian=target, department=transfer.new_department,
                 condition=transfer.condition or asset.condition, modified=now)
        if updated != 1:
            raise LifecycleError("This asset's custody changed. Reload and try again.")
        closed = AssetAssignment.objects.filter(pk=source.pk, status="Open").update(
            status="Closed", closed_at=now, closed_by=approved_by,
            closure_reason="Transfer", superseded_by_transfer=transfer)
        if closed != 1:
            raise LifecycleError("The source Assignment is no longer open.")
        target_assignment = AssetAssignment.objects.create(
            asset=asset, user=target, issued_by=approved_by,
            issue_condition=transfer.condition or asset.condition,
            remarks=transfer.remarks, source_transfer=transfer)
        transfer.status = "Approved"
        transfer.approved_by = approved_by
        transfer.save(update_fields=["status", "approved_by"])
        log_action(
            _audit_request(approved_by, request), "Transfer Approved", "Transfers",
            old_value=f"{asset.asset_id} | Assigned | {source.user.user_name} | Ongoing | Assignment {source.pk}",
            new_value=(f"{asset.asset_id} | Assigned | {target.user_name} | Ongoing | "
                       f"Assignment {target_assignment.pk} | TRF-{transfer.pk:05d} | "
                       f"condition {transfer.condition or asset.condition} | {transfer.remarks}"),
        )
        transaction.on_commit(lambda: _notify_decision(transfer, True))
    return transfer


def reject(transfer, approved_by, *, request=None):
    _require_actor(approved_by, "asset_custody_manage")
    with transaction.atomic():
        record = AssetTransfer.objects.select_for_update().get(pk=transfer.pk)
        if record.status != "Pending":
            raise LifecycleError("This transfer has already been processed.")
        record.status = "Rejected"
        record.approved_by = approved_by
        record.save(update_fields=["status", "approved_by"])
        log_action(
            _audit_request(approved_by, request), "Transfer Rejected", "Transfers",
            old_value=f"TRF-{record.pk:05d} | Pending | Assignment {record.source_assignment_id}",
            new_value=f"TRF-{record.pk:05d} | Rejected | custody unchanged",
        )
        transaction.on_commit(lambda: _notify_decision(record, False))
    return record
