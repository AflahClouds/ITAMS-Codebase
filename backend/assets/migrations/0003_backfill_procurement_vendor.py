from django.db import migrations


def backfill(apps, schema_editor):
    Procurement = apps.get_model("assets", "Procurement")
    Vendor = apps.get_model("catalog", "Vendor")

    vendors = {}
    for proc in Procurement.objects.all():
        name = (proc.vendor_name or "").strip() or "Unknown Vendor"
        if name not in vendors:
            vendor, _ = Vendor.objects.get_or_create(name=name)
            vendors[name] = vendor
        proc.vendor = vendors[name]
        proc.save(update_fields=["vendor"])


def unbackfill(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("assets", "0002_asset_amc_end_asset_amc_end_reason_asset_amc_start_and_more"),
        ("catalog", "0003_vendor"),
    ]

    operations = [
        migrations.RunPython(backfill, unbackfill),
    ]
