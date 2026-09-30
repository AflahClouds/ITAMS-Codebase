"""Current custody identity and the transactional ongoing issue operation."""
import logging
from types import SimpleNamespace

from django.db import transaction
from django.utils import timezone

from core.services import log_action, notify

from .models import Asset, AssetAssignment, AssetCheckout, LifecycleError


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
