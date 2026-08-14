"""Retire the seeded `admin` / `admin123` credential on installs that still carry it.

B1 finding 11. Migration 0002 originally wrote a known password into the repository, so
every install created before this change shares one publicly-readable administrator
credential. 0002 no longer writes a password at all, but editing it does not help an
install where it has already run — the account is already there.

This checks the existing account and acts only if the password is still the committed
default. A deployment that has already rotated it keeps whatever it set: the point is to
close a known hole, not to lock anyone out of their own system.

Where the default is still in place the password is made unusable rather than replaced
with another fixed value. An operator restores access deliberately with:

    python manage.py changepassword admin

That is a visible, one-line recovery, and it is the outcome the finding asked for -
rotation rather than a written exception.
"""
from django.contrib.auth.hashers import check_password, make_password
from django.db import migrations

RETIRED_DEFAULT = "admin123"


def retire(apps, schema_editor):
    AuthUser = apps.get_model("auth", "User")

    account = AuthUser.objects.filter(username="admin").first()
    if account is None:
        return
    if not account.password or not check_password(RETIRED_DEFAULT, account.password):
        # Already rotated, or already unusable. Leave it exactly as it is.
        return

    account.password = make_password(None)
    account.save(update_fields=["password"])


def unretire(apps, schema_editor):
    """Deliberately not reversible.

    Restoring a known shared credential is the defect this migration exists to remove,
    so reversing it is a no-op. Use `changepassword` to set a password you choose.
    """


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_audit_access_permission"),
    ]

    operations = [migrations.RunPython(retire, unretire)]
