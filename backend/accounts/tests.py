from django.contrib.auth.models import User as AuthUser
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Setting

from .models import Permission, Role, User


def _create_profile(username, permission_codes=()):
    account = AuthUser.objects.create_user(username=username, password="test-password")
    role = Role.objects.create(name=f"{username} role")
    permissions = [
        Permission.objects.get_or_create(code=code, defaults={"name": code})[0]
        for code in permission_codes
    ]
    role.permissions.set(permissions)
    profile = User.objects.create(
        account=account,
        user_name=f"{username} profile",
        emp_id=f"EMP-{username}",
        email_id=f"{username}@example.com",
        role=role,
    )
    return account, profile


class PrivacyAuthorizationTests(TestCase):
    def test_ordinary_user_cannot_read_privileged_apis(self):
        account, profile = _create_profile("ordinary")
        Setting.objects.create(key="smtp_server", value="private.example.com")
        client = APIClient()
        client.force_authenticate(account)

        paths = (
            "/user/",
            f"/user/{profile.pk}/",
            "/role/",
            "/permission/",
            "/setting/",
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(client.get(path).status_code, 403)

    def test_user_manager_can_read_full_user_records(self):
        account, profile = _create_profile("user-manager", ("user_management",))
        client = APIClient()
        client.force_authenticate(account)

        response = client.get(f"/user/{profile.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email_id"], profile.email_id)
        self.assertEqual(response.data["login_username"], account.username)

    def test_asset_user_gets_only_minimal_active_user_directory(self):
        account, _ = _create_profile("asset-user", ("asset_view",))
        _, disabled_profile = _create_profile("disabled", ("asset_view",))
        disabled_profile.status = "Disabled"
        disabled_profile.save(update_fields=["status"])
        client = APIClient()
        client.force_authenticate(account)

        response = client.get("/user/directory/")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(disabled_profile.pk, [row["id"] for row in response.data])
        self.assertTrue(response.data)
        self.assertEqual(
            set(response.data[0]),
            {"id", "user_name", "emp_id", "department_name"},
        )

    def test_settings_access_does_not_expose_admin_configuration(self):
        account, _ = _create_profile("master-manager", ("settings_access",))
        client = APIClient()
        client.force_authenticate(account)

        self.assertEqual(client.get("/setting/").status_code, 403)
