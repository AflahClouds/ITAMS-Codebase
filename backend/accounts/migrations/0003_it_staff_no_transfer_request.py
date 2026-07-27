from django.db import migrations


def remove_transfer_request(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    Permission = apps.get_model("accounts", "Permission")
    try:
        role = Role.objects.get(name="IT Staff")
        permission = Permission.objects.get(code="transfer_request")
    except (Role.DoesNotExist, Permission.DoesNotExist):
        return
    role.permissions.remove(permission)


def restore_transfer_request(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    Permission = apps.get_model("accounts", "Permission")
    try:
        role = Role.objects.get(name="IT Staff")
        permission = Permission.objects.get(code="transfer_request")
    except (Role.DoesNotExist, Permission.DoesNotExist):
        return
    role.permissions.add(permission)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_seed_rbac_and_org"),
    ]

    operations = [
        migrations.RunPython(remove_transfer_request, restore_transfer_request),
    ]
