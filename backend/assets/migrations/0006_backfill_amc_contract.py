from django.db import migrations


def backfill(apps, schema_editor):
    Asset = apps.get_model("assets", "Asset")
    AmcContract = apps.get_model("assets", "AmcContract")

    for asset in Asset.objects.filter(has_amc=True):
        if not asset.amc_start or not asset.amc_end:
            # Never fully filled in — nothing coherent to carry forward.
            continue
        AmcContract.objects.create(
            asset=asset,
            start_date=asset.amc_start,
            end_date=asset.amc_end,
            status=asset.amc_status or "Active",
            end_reason=asset.amc_end_reason or "",
        )


def unbackfill(apps, schema_editor):
    AmcContract = apps.get_model("assets", "AmcContract")
    AmcContract.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("assets", "0005_amc_contract"),
    ]

    operations = [
        migrations.RunPython(backfill, unbackfill),
    ]
