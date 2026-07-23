from datetime import date

from django.contrib.auth.models import User as AuthUser
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from rest_framework.test import APIClient

from .models import (Asset, Brand, Category, Model, Permission, Procurement,
                     PurchaseMode, Role, Setting, User)


class ProtectedMasterDataTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(category_name="Protected category")
        self.brand = Brand.objects.create(brand_name="Protected brand")
        self.model = Model.objects.create(model_name="Protected model")
        self.purchase_mode = PurchaseMode.objects.create(purchase_mode="Protected mode")
        self.procurement = Procurement.objects.create(
            mode_of_purchase=self.purchase_mode,
            vendor_name="Test vendor",
            purchase_date=date(2026, 1, 1),
            invoice_date=date(2026, 1, 1),
            invoice_number="PROTECTED-INV-001",
        )
        self.asset = Asset.objects.create(
            asset_id="PROTECTED-ASSET-001",
            tag_number="PROTECTED-TAG-001",
            serial_number="PROTECTED-SERIAL-001",
            category=self.category,
            brand=self.brand,
            model=self.model,
            procurement=self.procurement,
        )

    def test_referenced_master_records_cannot_delete_operational_data(self):
        for master in (self.category, self.brand, self.model, self.purchase_mode):
            with self.subTest(master=master):
                with self.assertRaises(ProtectedError):
                    master.delete()

        self.assertTrue(Asset.objects.filter(pk=self.asset.pk).exists())
        self.assertTrue(Procurement.objects.filter(pk=self.procurement.pk).exists())

    def test_delete_api_returns_conflict_for_referenced_master_records(self):
        account = AuthUser.objects.create_superuser(
            username="master-delete-admin",
            email="master-delete@example.com",
            password="test-password",
        )
        client = APIClient()
        client.force_authenticate(account)

        paths = (
            f"/category/{self.category.pk}/",
            f"/brand/{self.brand.pk}/",
            f"/model/{self.model.pk}/",
            f"/purchase_mode/{self.purchase_mode.pk}/",
        )
        for path in paths:
            with self.subTest(path=path):
                response = client.delete(path)
                self.assertEqual(response.status_code, 409)
                self.assertEqual(
                    response.data["detail"],
                    "Cannot delete this master record because it is in use.",
                )

        self.assertTrue(Asset.objects.filter(pk=self.asset.pk).exists())
        self.assertTrue(Procurement.objects.filter(pk=self.procurement.pk).exists())

    def test_unused_master_records_can_still_be_deleted(self):
        unused_records = (
            Category.objects.create(category_name="Unused category"),
            Brand.objects.create(brand_name="Unused brand"),
            Model.objects.create(model_name="Unused model"),
            PurchaseMode.objects.create(purchase_mode="Unused mode"),
        )

        for master in unused_records:
            with self.subTest(master=master):
                model_class = type(master)
                master_id = master.pk
                master.delete()
                self.assertFalse(model_class.objects.filter(pk=master_id).exists())


class PrivacyAuthorizationTests(TestCase):
    def create_profile(self, username, permission_codes=()):
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

    def test_ordinary_user_cannot_read_privileged_apis(self):
        account, profile = self.create_profile("ordinary")
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
        account, profile = self.create_profile("user-manager", ("user_management",))
        client = APIClient()
        client.force_authenticate(account)

        response = client.get(f"/user/{profile.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email_id"], profile.email_id)
        self.assertEqual(response.data["login_username"], account.username)

    def test_asset_user_gets_only_minimal_active_user_directory(self):
        account, _ = self.create_profile("asset-user", ("asset_view",))
        _, disabled_profile = self.create_profile("disabled", ("asset_view",))
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
        account, _ = self.create_profile("master-manager", ("settings_access",))
        client = APIClient()
        client.force_authenticate(account)

        self.assertEqual(client.get("/setting/").status_code, 403)
