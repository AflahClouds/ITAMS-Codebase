from django.db import migrations

PERMISSIONS = [
    ("asset_create", "Asset Create"),
    ("asset_edit", "Asset Edit"),
    ("asset_delete", "Asset Delete"),
    ("transfer_request", "Asset Transfer Request"),
    ("asset_transfer", "Asset Transfer Approval & Checkout"),
    ("asset_view", "Asset View"),
    ("user_management", "User Management"),
    ("report_access", "Report Access"),
    ("settings_access", "Settings Access"),
]

ROLES = {
    "Admin": "Full system access",
    "IT Manager": "Manage assets, approve transfers & checkouts, view all reports",
    "IT Staff": "Day-to-day asset operations, approve transfers & checkouts",
    "HR": "Request asset transfers between employees/departments",
    "Employee": "View own assets and raise requests",
    "Viewer": "Read-only access",
}

ROLE_PERMISSION_MAP = {
    "IT Manager": ["asset_create", "asset_edit", "asset_delete", "transfer_request",
                   "asset_transfer", "asset_view", "report_access"],
    "IT Staff": ["asset_create", "asset_edit", "transfer_request", "asset_transfer",
                 "asset_view", "report_access"],
    "HR": ["asset_view", "transfer_request"],
    "Employee": ["asset_view"],
    "Viewer": ["asset_view", "report_access"],
}

DEPARTMENTS = ["IT", "Finance", "HR", "Production", "Sales & Marketing",
               "E-Commerce", "Logistics", "Administration"]

LOCATIONS = ["Head Office", "Factory Unit 1", "Factory Unit 2", "Warehouse", "Retail Store"]


def seed(apps, schema_editor):
    Permission = apps.get_model("accounts", "Permission")
    Role = apps.get_model("accounts", "Role")
    Department = apps.get_model("accounts", "Department")
    Location = apps.get_model("accounts", "Location")
    Profile = apps.get_model("accounts", "User")
    AuthUser = apps.get_model("auth", "User")

    perms = {}
    for code, name in PERMISSIONS:
        perms[code], _ = Permission.objects.get_or_create(code=code, defaults={"name": name})

    roles = {}
    for name, desc in ROLES.items():
        roles[name], _ = Role.objects.get_or_create(name=name, defaults={"description": desc})

    for role_name, codes in ROLE_PERMISSION_MAP.items():
        role = roles[role_name]
        if not role.permissions.exists():
            role.permissions.set([perms[c] for c in codes])

    for name in DEPARTMENTS:
        Department.objects.get_or_create(name=name)
    for name in LOCATIONS:
        Location.objects.get_or_create(name=name)

    # Seed administrator account + linked employee profile.
    #
    # No password is written into this file. A credential committed to the repository is
    # public the moment the repository is shared, and a seed one is worse than most
    # because every install has it and nobody remembers to change it. The password comes
    # from ITAMS_ADMIN_PASSWORD if the deployment supplies one; otherwise the account is
    # created with an unusable password and cannot be logged into until an operator sets
    # one deliberately:
    #
    #     python manage.py changepassword admin
    #
    # The profile and Role wiring are created either way, so the account is ready to use
    # the moment it has a password.
    if not AuthUser.objects.filter(username="admin").exists():
        import os

        from django.contrib.auth.hashers import make_password
        seed_password = os.environ.get("ITAMS_ADMIN_PASSWORD") or None
        account = AuthUser.objects.create(
            username="admin",
            email="admin@cloudshoefactory.com",
            # make_password(None) produces an unusable hash that no input can match.
            password=make_password(seed_password),
            is_active=True,
        )
        it_dept = Department.objects.filter(name="IT").first()
        Profile.objects.create(
            account=account,
            user_name="System Administrator",
            emp_id="ADMIN",
            email_id="admin@cloudshoefactory.com",
            designation="Administrator",
            department=it_dept,
            role=roles["Admin"],
            status="Active",
        )


def unseed(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
