from django.contrib.auth.models import User as AuthUser
from django.test import TestCase
from rest_framework.authtoken.models import Token
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


class MasterDataAccessTests(TestCase):
    """Master reads need a permission, but either the code that consumes the data or
    the code that maintains it will do."""

    def test_asset_view_may_read_master_data(self):
        account, _ = _create_profile("master-consumer", ("asset_view",))
        client = APIClient()
        client.force_authenticate(account)

        self.assertEqual(client.get("/category/").status_code, 200)

    def test_settings_access_may_read_the_master_data_it_maintains(self):
        account, _ = _create_profile("master-maintainer", ("settings_access",))
        client = APIClient()
        client.force_authenticate(account)

        self.assertEqual(client.get("/category/").status_code, 200)
        self.assertEqual(client.get("/vendor/").status_code, 200)

    def test_a_role_with_neither_code_is_denied(self):
        account, _ = _create_profile("master-nobody")
        client = APIClient()
        client.force_authenticate(account)

        self.assertEqual(client.get("/category/").status_code, 403)

    def test_the_employee_role_gets_no_b6_surface(self):
        account, profile = _create_profile("master-employee", ("asset_view",))
        profile.role = Role.objects.get(name="Employee")
        profile.save(update_fields=["role"])
        client = APIClient()
        client.force_authenticate(account)

        self.assertEqual(client.get("/vendor/").status_code, 403)


class PasswordPolicyTests(TestCase):
    """Password changes go through AUTH_PASSWORD_VALIDATORS, not a local length floor."""

    def _client(self):
        account = AuthUser.objects.create_user(username="pw-user", password="Str0ng-Passphrase!")
        User.objects.create(account=account, user_name="pw", emp_id="EMP-pw",
                            email_id="pw@example.com")
        client = APIClient()
        client.force_authenticate(account)
        return client

    def test_a_common_password_is_rejected_even_though_it_is_long_enough(self):
        response = self._client().post("/auth/change-password/", {
            "old_password": "Str0ng-Passphrase!", "new_password": "password123"}, format="json")

        self.assertEqual(response.status_code, 400)

    def test_a_strong_password_is_accepted(self):
        response = self._client().post("/auth/change-password/", {
            "old_password": "Str0ng-Passphrase!",
            "new_password": "quartz-lantern-98-oxide"}, format="json")

        self.assertEqual(response.status_code, 200)


class PermissionLookupTests(TestCase):
    """users_with_permission runs on every Transfer request and every expiry sweep, so
    it must not scale its query count with the size of the directory."""

    def test_recipients_resolve_in_a_constant_number_of_queries(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        from .models import users_with_permission

        # The seeded System Administrator already qualifies: Admins are recipients.
        baseline = len(users_with_permission("asset_custody_manage"))

        for i in range(15):
            _create_profile(f"bulk-{i}", ("asset_custody_manage",))
        with CaptureQueriesContext(connection) as small:
            self.assertEqual(len(users_with_permission("asset_custody_manage")),
                             baseline + 15)

        for i in range(15, 45):
            _create_profile(f"bulk-{i}", ("asset_custody_manage",))
        with CaptureQueriesContext(connection) as large:
            self.assertEqual(len(users_with_permission("asset_custody_manage")),
                             baseline + 45)

        self.assertEqual(len(small.captured_queries), len(large.captured_queries))


class TokenRevocationOnDeactivationTests(TestCase):
    """Deactivating a profile must drop its login tokens, not merely rely on every
    endpoint re-checking profile status on each request."""

    def test_disabling_through_the_api_revokes_the_token(self):
        admin_account, _ = _create_profile("token-admin", ("user_management",))
        target_account, target = _create_profile("to-disable", ("asset_view",))
        token = Token.objects.create(user=target_account)
        client = APIClient()
        client.force_authenticate(admin_account)

        response = client.patch(f"/user/{target.pk}/", {"status": "Disabled"}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Token.objects.filter(key=token.key).exists())

    def test_disabling_outside_the_api_revokes_the_token(self):
        account, profile = _create_profile("shell-disabled", ("asset_view",))
        Token.objects.create(user=account)

        profile.status = "Disabled"
        profile.save(update_fields=["status"])

        self.assertFalse(Token.objects.filter(user=account).exists())

    def test_revoked_token_no_longer_authenticates(self):
        account, profile = _create_profile("revoked", ("asset_view",))
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=account).key}")
        self.assertEqual(client.get("/dashboard/").status_code, 200)

        profile.status = "Disabled"
        profile.save(update_fields=["status"])

        self.assertEqual(client.get("/dashboard/").status_code, 401)

    def test_an_active_profile_keeps_its_token(self):
        account, profile = _create_profile("stays-active", ("asset_view",))
        token = Token.objects.create(user=account)

        profile.designation = "Technician"
        profile.save()

        self.assertTrue(Token.objects.filter(key=token.key).exists())

    def test_a_profile_without_a_login_account_can_be_disabled(self):
        profile = User.objects.create(
            user_name="no-login", emp_id="EMP-no-login", email_id="no-login@example.com")

        profile.status = "Disabled"
        profile.save(update_fields=["status"])

        self.assertEqual(User.objects.get(pk=profile.pk).status, "Disabled")
