import django.db.models.deletion
from django.db import migrations, models


def migrate_procurement_fields_to_assets(apps, schema_editor):
    Procurement = apps.get_model('api', 'Procurement')
    Asset = apps.get_model('api', 'Asset')

    for procurement in Procurement.objects.all():
        linked_asset_pk = procurement.asset_id
        if not linked_asset_pk:
            continue
        Asset.objects.filter(pk=linked_asset_pk).update(
            procurement=procurement,
            purchase_cost=procurement.purchase_cost,
            depreciation_rate=procurement.depreciation_rate,
            asset_life=procurement.asset_life,
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_procurement_asset_onetoone'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='procurement',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assets', to='api.procurement'),
        ),
        migrations.AddField(
            model_name='asset',
            name='purchase_cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='asset',
            name='depreciation_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='asset',
            name='asset_life',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.RunPython(migrate_procurement_fields_to_assets, noop),
        migrations.RemoveField(
            model_name='procurement',
            name='asset',
        ),
        migrations.RemoveField(
            model_name='procurement',
            name='purchase_cost',
        ),
        migrations.RemoveField(
            model_name='procurement',
            name='depreciation_rate',
        ),
        migrations.RemoveField(
            model_name='procurement',
            name='asset_life',
        ),
        migrations.AlterField(
            model_name='procurement',
            name='po_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
