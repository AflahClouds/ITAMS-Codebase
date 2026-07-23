import django.db.models.deletion
from django.db import migrations, models


def link_or_delete_orphan_procurements(apps, schema_editor):
    Procurement = apps.get_model('api', 'Procurement')
    Asset = apps.get_model('api', 'Asset')

    for procurement in Procurement.objects.all():
        asset = Asset.objects.filter(asset_id=procurement.asset_id).first()
        if asset:
            procurement.asset_link = asset
            procurement.save(update_fields=['asset_link'])
        else:
            # No matching Asset exists for this legacy asset_id string -
            # it was already a dangling reference, so it can't be linked.
            procurement.delete()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_procurement_invoice_number_and_more'),
    ]

    operations = [
        # Staged under a temporary name because the old CharField 'asset_id'
        # column must be dropped before a field named 'asset' can claim the
        # 'asset_id' column that Django generates for a FK/O2O by default.
        migrations.AddField(
            model_name='procurement',
            name='asset_link',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='procurement', to='api.asset'),
        ),
        migrations.RunPython(link_or_delete_orphan_procurements, noop),
        migrations.RemoveField(
            model_name='procurement',
            name='asset_id',
        ),
        migrations.RenameField(
            model_name='procurement',
            old_name='asset_link',
            new_name='asset',
        ),
        migrations.AlterField(
            model_name='procurement',
            name='asset',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='procurement', to='api.asset'),
        ),
    ]
