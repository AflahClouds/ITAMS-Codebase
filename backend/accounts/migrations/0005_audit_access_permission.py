"""Grant AuditLog access by permission code rather than by Role name.

B8 ALR-003 grants global AuditLog view, filter, and export access to Admin **and IT
Manager**. The endpoint enforced an Admin-only test, so the IT Manager the policy names
was refused, and the report surface was later made to match the endpoint rather than the
policy. A dedicated code expresses the grant exactly and survives a Role rename, which a
Role-name test does not.
"""
from django.db import migrations

CODE = "audit_access"
NAME = "Audit Trail Access"
ROLES = ("Admin", "IT Manager")


def grant(apps, schema_editor):
    Permission = apps.get_model("accounts", "Permission")
    Role = apps.get_model("accounts", "Role")

    permission, _ = Permission.objects.get_or_create(code=CODE, defaults={"name": NAME})
    for role_name in ROLES:
        role = Role.objects.filter(name=role_name).first()
        if role is not None:
            role.permissions.add(permission)


def revoke(apps, schema_editor):
    Permission = apps.get_model("accounts", "Permission")
    Permission.objects.filter(code=CODE).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_rename_asset_transfer_permission"),
    ]

    operations = [migrations.RunPython(grant, revoke)]
