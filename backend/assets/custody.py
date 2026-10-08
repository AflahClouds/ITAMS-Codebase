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

TEMPORARY_HOLDER_ERROR = (
    "This asset is being temporarily held by another employee. "
    "IT must record Check-in before a new Checkout or Assign."
)


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


def confirmed_temporary_holder(asset, target):
    """Only name temporary custody when the snapshot and sole open record agree."""
    return (asset.status == "Assigned" and asset.custodian_id != target.pk and
            custody_type(asset) == "Temporary")


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
        if confirmed_temporary_holder(current, user):
            raise LifecycleError(TEMPORARY_HOLDER_ERROR)
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


def classify_legacy_checkout(checkout, custody_choice, actor, *, remarks="", request=None):
    """Classify one matching old Checkout without recording a physical return."""
    if (actor is None or actor.status != "Active" or not actor.account_id
            or not actor.account.is_active or not actor.can("asset_custody_manage")):
        raise LifecycleError("You cannot classify Checkout custody.")
    if custody_choice not in ("Temporary", "Ongoing"):
        raise LifecycleError("Choose Temporary or Ongoing custody for this Checkout.")
    remarks = (remarks or "").strip()

    with transaction.atomic():
        current = Asset.objects.select_for_update().get(pk=checkout.asset_id)
        record = AssetCheckout.objects.select_for_update().select_related(
            "user", "approved_by").get(pk=checkout.pk)
        # A successful retry returns the same decision, never another arrangement.
        if record.classification == custody_choice and record.classified_at:
            if (custody_choice == "Temporary" and record.status == "Open" and
                    custody_type(current) == "Temporary"):
                return record
            if (custody_choice == "Ongoing" and record.status == "Returned" and
                    record.closure_reason == "Reclassified" and
                    AssetAssignment.objects.filter(
                        asset=current, source_checkout=record, status="Open",
                        user_id=current.custodian_id).count() == 1 and
                    custody_type(current) == "Ongoing"):
                return record
        if record.status != "Open" or record.classification != "Unclassified":
            raise LifecycleError("This legacy Checkout has already been classified or closed.")
        if (current.status != "Assigned" or current.custodian_id != record.user_id or
                custody_type(current) != "Unclassified" or
                AssetAssignment.objects.filter(asset=current, status="Open").exists() or
                AssetCheckout.objects.filter(asset=current, status="Open").exclude(
                    pk=record.pk).exists()):
            raise LifecycleError(
                "Conflicting custody records: Checkout and Asset must name the same "
                "current holder. Investigate or use verified Transfer reconciliation.")

        now = timezone.now()
        updates = {
            "classification": custody_choice,
            "classified_at": now,
            "classified_by": actor,
            "classification_remarks": remarks,
        }
        if custody_choice == "Ongoing":
            updates.update(status="Returned", closure_reason="Reclassified",
                           closed_at=now)
        changed = AssetCheckout.objects.filter(
            pk=record.pk, status="Open", classification="Unclassified").update(**updates)
        if changed != 1:
            raise LifecycleError("This legacy Checkout changed. Reload and try again.")
        if custody_choice == "Ongoing":
            assignment = AssetAssignment.objects.create(
                asset=current, user=record.user, issued_by=record.approved_by,
                issue_condition=record.checkout_condition,
                remarks=record.remarks, source_checkout=record,
                provenance="Legacy Checkout classification",
                date_basis="Original Checkout issue date",
            )
            AssetAssignment.objects.filter(pk=assignment.pk).update(
                issued_at=record.checkout_date)
        log_action(
            request or SimpleNamespace(user=actor.account, META={}),
            "Classify Checkout", "Checkouts",
            old_value=(f"{current.asset_id} | Assigned | {record.user.user_name} | "
                       f"Unclassified | Checkout {record.pk}"),
            new_value=(f"{current.asset_id} | Assigned | {record.user.user_name} | "
                       f"{custody_choice} | Checkout {record.pk} | "
                       f"{('Reclassified, no physical return' if custody_choice == 'Ongoing' else 'Open')} "
                       f"| by {actor.user_name} | {remarks}"),
        )
    record.refresh_from_db()
    return record


def _verified_approved_handoff_chain(asset, checkout, final_transfer):
    """Verify every approved handoff after the old issue reaches the current holder."""
    transfers = list(AssetTransfer.objects.filter(
        asset=asset, status="Approved",
        transfer_date__gte=checkout.checkout_date,
    ).order_by("transfer_date", "pk"))
    if not transfers or transfers[-1].pk != final_transfer.pk:
        raise LifecycleError("Approved Transfer history does not establish current custody.")
    holder_id = checkout.user_id
    department_id = None
    for transfer in transfers:
        if (not transfer.approved_by_id or transfer.previous_owner_id != holder_id or
                not transfer.new_owner_id or transfer.new_owner_id == holder_id or
                (department_id is not None and
                 transfer.previous_department_id != department_id)):
            raise LifecycleError("Approved Transfer history has a conflicting handoff.")
        holder_id = transfer.new_owner_id
        department_id = transfer.new_department_id
    if holder_id != asset.custodian_id or department_id != asset.department_id:
        raise LifecycleError("Approved Transfer history does not match current custody.")


def reconcile_legacy_checkout(checkout, final_transfer, custody_choice, actor,
                              *, remarks="", request=None):
    """Supersede A and record B only when approved handoffs prove current custody."""
    if (actor is None or actor.status != "Active" or not actor.account_id or
            not actor.account.is_active or not actor.can("asset_custody_manage")):
        raise LifecycleError("You cannot reconcile Checkout custody.")
    if custody_choice not in ("Temporary", "Ongoing"):
        raise LifecycleError("Choose Temporary or Ongoing custody for reconciliation.")
    remarks = (remarks or "").strip()

    with transaction.atomic():
        current = Asset.objects.select_for_update().get(pk=checkout.asset_id)
        record = AssetCheckout.objects.select_for_update().select_related("user").get(
            pk=checkout.pk)
        final = AssetTransfer.objects.select_for_update().get(pk=final_transfer.pk)
        if (current.status != "Assigned" or not current.custodian_id or
                current.custodian_id == record.user_id or
                final.asset_id != current.pk or final.status != "Approved" or
                record.return_date is not None or record.return_condition):
            raise LifecycleError("Conflicting custody records lack a verified handoff.")
        _verified_approved_handoff_chain(current, record, final)

        assignments = list(AssetAssignment.objects.select_for_update().filter(
            asset=current, status="Open"))
        other_checkouts = list(AssetCheckout.objects.select_for_update().filter(
            asset=current, status="Open").exclude(pk=record.pk))
        arrangement = None
        if custody_choice == "Ongoing" and not other_checkouts and len(assignments) <= 1:
            if assignments:
                arrangement = assignments[0]
                if (arrangement.user_id != current.custodian_id or
                        arrangement.source_transfer_id not in (None, final.pk) or
                        arrangement.source_checkout_id not in (None, record.pk)):
                    raise LifecycleError("Current holder has a conflicting active arrangement.")
        elif custody_choice == "Temporary" and not assignments and len(other_checkouts) <= 1:
            if other_checkouts:
                arrangement = other_checkouts[0]
                if (arrangement.user_id != current.custodian_id or
                        arrangement.classification != "Temporary" or
                        arrangement.source_transfer_id != final.pk or
                        arrangement.source_checkout_id != record.pk):
                    raise LifecycleError("Current holder has a conflicting active arrangement.")
        else:
            raise LifecycleError("Current holder has a conflicting active arrangement.")
        if record.status == "Returned" and record.closure_reason == "Superseded":
            if (record.superseded_by_transfer_id == final.pk and record.classified_at and
                    arrangement is not None and
                    arrangement.source_checkout_id == record.pk and
                    arrangement.source_transfer_id == final.pk):
                return record
            raise LifecycleError("This legacy Checkout was already reconciled differently.")
        if record.status != "Open" or record.classification != "Unclassified":
            raise LifecycleError("This legacy Checkout is no longer open and unclassified.")
        if arrangement is not None and custody_choice == "Temporary":
            raise LifecycleError("Current holder has a conflicting active arrangement.")

        now = timezone.now()
        changed = AssetCheckout.objects.filter(
            pk=record.pk, status="Open", classification="Unclassified").update(
            status="Returned", closure_reason="Superseded", closed_at=now,
            superseded_by_transfer=final, classified_by=actor,
            classified_at=now, classification_remarks=remarks)
        if changed != 1:
            raise LifecycleError("This legacy Checkout changed. Reload and try again.")
        date_basis = "Legacy Transfer event date (event type unverified)"
        if custody_choice == "Ongoing":
            if arrangement is None:
                arrangement = AssetAssignment.objects.create(
                    asset=current, user=current.custodian, issue_condition="",
                    source_checkout=record, source_transfer=final,
                    provenance="Administrative reconstruction", date_basis=date_basis)
                AssetAssignment.objects.filter(pk=arrangement.pk).update(
                    issued_at=final.transfer_date)
            else:
                linked = AssetAssignment.objects.filter(pk=arrangement.pk, status="Open").update(
                    source_checkout=record, source_transfer=final)
                if linked != 1:
                    raise LifecycleError("The current Assignment changed. Reload and try again.")
        else:
            arrangement = AssetCheckout.objects.create(
                asset=current, user=current.custodian, classification="Temporary",
                source_checkout=record, source_transfer=final,
                provenance="Administrative reconstruction", date_basis=date_basis)
            AssetCheckout.objects.filter(pk=arrangement.pk).update(
                checkout_date=final.transfer_date)
        log_action(
            request or SimpleNamespace(user=actor.account, META={}),
            "Reconcile Checkout", "Checkouts",
            old_value=(f"{current.asset_id} | Checkout {record.pk} Open | "
                       f"{record.user.user_name} | current holder {current.custodian_id}"),
            new_value=(f"{current.asset_id} | Checkout {record.pk} Superseded by "
                       f"TRF-{final.pk:05d} | {custody_choice} arrangement {arrangement.pk} "
                       f"| actor {actor.user_name} | no physical Check-in | {remarks}"),
        )
    record.refresh_from_db()
    return record
