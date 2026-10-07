"""Current custody identity and transactional ongoing issue/return operations."""
import logging
from types import SimpleNamespace

from django.db import transaction
from django.utils import timezone

from core.services import log_action, notify

from .checkout import condition_worsened
from .models import (ASSET_CONDITIONS, Asset, AssetAssignment, AssetCheckout,
                     AssetConditionLog, AssetTransfer, LifecycleError)


logger = logging.getLogger(__name__)


def custody_type(asset):
    """Describe the current record without changing legacy or disputed custody."""
    assignments = getattr(asset, 'active_assignments', None)
    if assignments is None:
        assignments = list(asset.assignments.filter(status="Open"))
    checkouts = getattr(asset, 'active_checkouts', None)
    if checkouts is None:
        checkouts = list(asset.checkouts.filter(status="Open"))
    if len(assignments) + len(checkouts) > 1:
        return "Conflicting"
    if assignments:
        assignment = assignments[0]
        return ("Ongoing" if asset.status == "Assigned" and
                asset.custodian_id == assignment.user_id else "Conflicting")
    if checkouts:
        checkout = checkouts[0]
        if asset.status != "Assigned" or asset.custodian_id != checkout.user_id:
            return "Conflicting"
        return (checkout.classification if checkout.classification in
                ("Temporary", "Unclassified") else "Conflicting")
    if asset.status == "Assigned" or (asset.custodian_id and asset.status != "Lost"):
        return "Conflicting"
    return "None"


def _notify_assignee(user, asset):
    try:
        notify(user, f"Asset {asset.asset_id} has been assigned to you.",
               link=f"/asset/{asset.pk}")
    except Exception:
        # Delivery is deliberately outside the business transaction. The shared
        # notification service already retries and records ordinary failures.
        logger.exception("Could not notify assignee for asset %s", asset.pk)


def _notify_return(user, asset):
    try:
        notify(user, f"Asset {asset.asset_id} Take Back recorded. Thank you.",
               link=f"/asset/{asset.pk}")
    except Exception:
        logger.exception("Could not notify former custodian for asset %s", asset.pk)


def assign(asset, user, actor, *, remarks="", request=None):
    """Issue one Available Asset directly, with its current history and audit."""
    if (actor is None or actor.status != "Active" or not actor.account_id
            or not actor.account.is_active or not actor.can("asset_custody_manage")):
        raise LifecycleError("You cannot assign assets.")
    with transaction.atomic():
        current = Asset.objects.select_for_update().get(pk=asset.pk)
        if current.status != "Available" or current.custodian_id is not None:
            raise LifecycleError("This asset is not available for assignment.")
        if (AssetAssignment.objects.filter(asset=current, status="Open").exists() or
                AssetCheckout.objects.filter(asset=current, status="Open").exists()):
            raise LifecycleError("This asset already has active custody history.")
        target = type(user).objects.select_for_update().get(pk=user.pk)
        if target.status != "Active" or not target.account_id or not target.account.is_active:
            raise LifecycleError("The employee must be active to receive an asset.")

        # A conditional write also guards SQLite, where select_for_update is a no-op.
        updated = Asset.objects.filter(
            pk=current.pk, status="Available", custodian__isnull=True,
        ).update(status="Assigned", custodian=target, department=target.department,
                 modified=timezone.now())
        if updated != 1:
            raise LifecycleError("This asset's custody changed. Reload and try again.")
        current.refresh_from_db()
        assignment = AssetAssignment.objects.create(
            asset=current, user=target, issued_by=actor,
            issue_condition=current.condition, remarks=(remarks or "").strip(),
        )
        audit_request = request or SimpleNamespace(user=actor.account, META={})
        log_action(
            audit_request, "Assign", "Assignments",
            old_value=f"{current.asset_id} | Available | no custodian | no custody",
            new_value=(f"{current.asset_id} | Assigned | {target.user_name} "
                       f"| Ongoing | Assignment {assignment.pk} | "
                       f"condition {current.condition} | {assignment.remarks}"),
        )
        transaction.on_commit(lambda: _notify_assignee(target, current))
    return assignment


def take_back(assignment, condition, actor, *, remarks="", request=None):
    """Record physical receipt of the exact current ongoing arrangement."""
    if (actor is None or actor.status != "Active" or not actor.account_id
            or not actor.account.is_active or not actor.can("asset_custody_manage")):
        raise LifecycleError("You cannot take back assets.")
    if not condition:
        raise LifecycleError("A return condition is required to take back this asset.")
    if condition not in ASSET_CONDITIONS:
        raise LifecycleError(f"Condition must be one of {ASSET_CONDITIONS}")
    remarks = (remarks or "").strip()

    with transaction.atomic():
        # Lock the snapshot first, consistently with Assign and other custody actions.
        current = Asset.objects.select_for_update().get(pk=assignment.asset_id)
        record = AssetAssignment.objects.select_for_update().select_related('user').get(
            pk=assignment.pk)
        if (record.status != "Open" or current.status != "Assigned" or
                current.custodian_id != record.user_id or
                AssetAssignment.objects.filter(asset=current, status="Open").exclude(
                    pk=record.pk).exists() or
                AssetCheckout.objects.filter(asset=current, status="Open").exists()):
            raise LifecycleError("This Assignment is no longer the current custody.")
        if AssetTransfer.objects.filter(asset=current, status="Pending").exists():
            raise LifecycleError("Transfer request is not closed.")
        if condition_worsened(record.issue_condition, condition) and not remarks:
            raise LifecycleError(
                "This asset is being returned in a worse condition than it went out. "
                "Record what happened in the return remarks.")

        prior_condition = current.condition
        now = timezone.now()
        # Conditional writes guard SQLite, where select_for_update is a no-op.
        updated = Asset.objects.filter(
            pk=current.pk, status="Assigned", custodian_id=record.user_id,
        ).update(status="Available", condition=condition, custodian=None,
                 department=None, modified=now)
        if updated != 1:
            raise LifecycleError("This asset's custody changed. Reload and try again.")
        closed = AssetAssignment.objects.filter(pk=record.pk, status="Open").update(
            status="Closed", closed_at=now, closed_by=actor,
            closure_reason="Take Back", return_condition=condition,
            return_remarks=remarks)
        if closed != 1:
            raise LifecycleError("This Assignment is no longer open.")
        AssetConditionLog.objects.create(
            asset=current, inspector=actor, condition=condition,
            notes=remarks or "Recorded at Take Back.")
        audit_request = request or SimpleNamespace(user=actor.account, META={})
        log_action(
            audit_request, "Take Back", "Assignments",
            old_value=(f"{current.asset_id} | Assigned | {record.user.user_name} | "
                       f"Ongoing | Assignment {record.pk} | condition {prior_condition}"),
            new_value=(f"{current.asset_id} | Available | no custodian | no custody | "
                       f"Assignment {record.pk} closed by {actor.user_name} | "
                       f"return condition {condition} | {remarks}"),
        )
        if record.user.status == "Active" and record.user.account_id and record.user.account.is_active:
            transaction.on_commit(lambda: _notify_return(record.user, current))
    record.refresh_from_db()
    return record
