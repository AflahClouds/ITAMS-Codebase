from django.db import migrations

OLD_CODE = "asset_transfer"
NEW_CODE = "asset_custody_manage"
NEW_NAME = "Asset Custody Management (Checkout / Transfer / Service)"
OLD_NAME = "Asset Transfer Approval & Checkout"


def rename_forward(apps, schema_editor):
    Permission = apps.get_model("accounts", "Permission")
    # Update in place (same row/PK) so every Role's M2M grant follows the rename automatically —
    # nothing else needs touching.
    Permission.objects.filter(code=OLD_CODE).update(code=NEW_CODE, name=NEW_NAME)


def rename_backward(apps, schema_editor):
    Permission = apps.get_model("accounts", "Permission")
    Permission.objects.filter(code=NEW_CODE).update(code=OLD_CODE, name=OLD_NAME)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_it_staff_no_transfer_request"),
    ]

    operations = [
        migrations.RunPython(rename_forward, rename_backward),
    ]
