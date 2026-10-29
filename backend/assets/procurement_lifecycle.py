"""Atomic Procurement association transitions; custody operations retain ownership."""
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Asset, Procurement


def lock_purchase(instance):
    """Serialize purchase edits before locking affected Assets in primary-key order."""
    try:
        current = Procurement.objects.select_for_update().get(pk=instance.pk)
    except Procurement.DoesNotExist:
        raise ValidationError('This Procurement changed. Reload and try again.')
    if current.modified != instance.modified:
        raise ValidationError('This Procurement changed. Reload and try again.')
    return current


def _eligible(asset):
    if (asset.status not in ('In Storage', 'Available') or asset.custodian_id is not None
            or asset.department_id is not None
            or asset.assignments.filter(status='Open').exists()
            or asset.checkouts.filter(status='Open').exists()
            or asset.service_records.filter(status='Open').exists()
            or asset.transfers.filter(status='Pending').exists()):
        raise ValidationError(
            f'Asset {asset.asset_id} has protected lifecycle or custody state; '
            'resolve it before changing Procurement.')


@transaction.atomic
def associate(procurement, assets):
    """Attach new selections, preserving already-linked lifecycle states.

    Caller owns the purchase lock, arrival/history writes and outer transaction.
    Conditional updates additionally protect SQLite where row locks are a no-op.
    """
    selected = {asset.pk: asset for asset in assets}
    previous = set(Asset.objects.filter(procurement=procurement).values_list('pk', flat=True))
    current = list(Asset.objects.select_for_update().filter(
        pk__in=set(selected) | previous).order_by('pk'))
    if len(current) != len(set(selected) | previous):
        raise ValidationError('An Asset changed. Reload and try again.')
    for asset in current:
        snapshot = selected.get(asset.pk)
        if snapshot and (asset.procurement_id != snapshot.procurement_id
                         or asset.status != snapshot.status
                         or asset.modified != snapshot.modified):
            raise ValidationError('An Asset changed. Reload and try again.')
        if asset.pk in previous and asset.pk in selected:
            continue
        _eligible(asset)
        attaching = asset.pk in selected
        if attaching and asset.procurement_id is not None:
            raise ValidationError('This Asset is already linked to another Procurement.')
        changed = Asset.objects.filter(
            pk=asset.pk, procurement_id=asset.procurement_id, status=asset.status,
            modified=asset.modified, custodian__isnull=True, department__isnull=True,
        ).update(procurement=procurement if attaching else None,
                 status='Available' if attaching else 'In Storage', modified=timezone.now())
        if changed != 1:
            raise ValidationError('An Asset changed. Reload and try again.')
    return previous
