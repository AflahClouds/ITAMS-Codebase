from datetime import date

from django.contrib.auth.models import User as AuthUser
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from rest_framework.test import APIClient

from .checkout import check_in, check_out
from .models import (Asset, Brand, Category, Department, LifecycleError,
                     Model, Notification, Permission, Procurement,
                     PurchaseMode, Role, Setting, User)
from .transfer import approve, reject, request_transfer


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


def _create_catalog(invoice_number):
    category = Category.objects.create(category_name="Laptops")
    brand = Brand.objects.create(brand_name="Dell")
    model = Model.objects.create(model_name="Latitude")
    purchase_mode = PurchaseMode.objects.create(purchase_mode="Purchase")
    procurement = Procurement.objects.create(
        mode_of_purchase=purchase_mode,
        vendor_name="Vendor",
        purchase_date=date(2026, 1, 1),
        invoice_date=date(2026, 1, 1),
        invoice_number=invoice_number,
    )
    return category, brand, model, procurement


def _create_asset(asset_id, category, brand, model, procurement, **extra):
    return Asset.objects.create(
        asset_id=asset_id,
        tag_number=f"{asset_id}-TAG",
        serial_number=f"{asset_id}-SERIAL",
        category=category,
        brand=brand,
        model=model,
        procurement=procurement,
        **extra,
    )


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


class CheckoutLifecycleTests(TestCase):
    def setUp(self):
        category, brand, model, procurement = _create_catalog("CHK-INV-001")
        self.department = Department.objects.create(name="Engineering")
        self.asset = _create_asset("CHK-ASSET-001", category, brand, model, procurement)
        _, self.user = _create_profile("checkout-holder")
        self.user.department = self.department
        self.user.save(update_fields=["department"])

    def test_check_out_assigns_asset_to_user_and_their_department(self):
        checkout = check_out(self.asset, self.user, self.user)

        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, "Assigned")
        self.assertEqual(self.asset.custodian, self.user)
        self.assertEqual(self.asset.department, self.department)
        self.assertEqual(checkout.checkout_condition, self.asset.condition)

    def test_check_out_persists_intake_remarks(self):
        checkout = check_out(self.asset, self.user, self.user, remarks="Assigned for onboarding")

        self.assertEqual(checkout.remarks, "Assigned for onboarding")

    def test_check_out_notifies_the_new_custodian(self):
        check_out(self.asset, self.user, self.user)

        self.assertTrue(Notification.objects.filter(user=self.user).exists())

    def test_check_out_rejects_an_unavailable_asset(self):
        self.asset.status = "Assigned"
        self.asset.save(update_fields=["status"])

        with self.assertRaises(LifecycleError):
            check_out(self.asset, self.user, self.user)

    def test_check_in_returns_asset_to_available_with_new_condition(self):
        checkout = check_out(self.asset, self.user, self.user)

        checkout = check_in(checkout, "Damaged", remarks="Screen cracked")

        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, "Available")
        self.assertIsNone(self.asset.custodian)
        self.assertEqual(self.asset.condition, "Damaged")
        self.assertEqual(checkout.status, "Returned")
        self.assertEqual(checkout.remarks, "Screen cracked")

    def test_check_in_rejects_an_already_closed_checkout(self):
        checkout = check_out(self.asset, self.user, self.user)
        check_in(checkout, "Good")

        with self.assertRaises(LifecycleError):
            check_in(checkout, "Good")

    def test_check_in_rejects_an_invalid_condition(self):
        checkout = check_out(self.asset, self.user, self.user)

        with self.assertRaises(LifecycleError):
            check_in(checkout, "Not A Real Condition")


class TransferLifecycleTests(TestCase):
    def setUp(self):
        category, brand, model, procurement = _create_catalog("TRF-INV-001")
        self.dept_a = Department.objects.create(name="Engineering")
        self.dept_b = Department.objects.create(name="Sales")
        _, self.previous_owner = _create_profile("transfer-previous-owner")
        _, self.new_owner = _create_profile("transfer-new-owner")
        _, self.approver = _create_profile("transfer-approver", ("asset_transfer",))
        self.asset = _create_asset(
            "TRF-ASSET-001", category, brand, model, procurement,
            status="Assigned", custodian=self.previous_owner, department=self.dept_a)

    def test_request_transfer_notifies_users_with_approval_permission(self):
        request_transfer(self.asset, self.new_owner, self.previous_owner)

        self.assertTrue(Notification.objects.filter(user=self.approver).exists())

    def test_request_transfer_captures_the_current_owner_and_department(self):
        transfer = request_transfer(self.asset, self.new_owner, self.previous_owner,
                                    new_department=self.dept_b)

        self.assertEqual(transfer.status, "Pending")
        self.assertEqual(transfer.previous_owner, self.previous_owner)
        self.assertEqual(transfer.previous_department, self.dept_a)
        self.assertEqual(transfer.new_department, self.dept_b)

    def test_approve_reassigns_custodian_department_and_condition(self):
        transfer = request_transfer(self.asset, self.new_owner, self.previous_owner,
                                    new_department=self.dept_b, condition="Average")

        transfer = approve(transfer, self.approver)

        self.asset.refresh_from_db()
        self.assertEqual(self.asset.custodian, self.new_owner)
        self.assertEqual(self.asset.department, self.dept_b)
        self.assertEqual(self.asset.status, "Assigned")
        self.assertEqual(self.asset.condition, "Average")
        self.assertEqual(transfer.status, "Approved")

    def test_approve_rejects_an_already_processed_transfer(self):
        transfer = request_transfer(self.asset, self.new_owner, self.previous_owner)
        approve(transfer, self.approver)

        with self.assertRaises(LifecycleError):
            approve(transfer, self.approver)

    def test_reject_leaves_the_asset_untouched(self):
        transfer = request_transfer(self.asset, self.new_owner, self.previous_owner)

        transfer = reject(transfer, self.approver)

        self.asset.refresh_from_db()
        self.assertEqual(self.asset.custodian, self.previous_owner)
        self.assertEqual(self.asset.department, self.dept_a)
        self.assertEqual(transfer.status, "Rejected")

    def test_reject_rejects_an_already_processed_transfer(self):
        transfer = request_transfer(self.asset, self.new_owner, self.previous_owner)
        reject(transfer, self.approver)

        with self.assertRaises(LifecycleError):
            reject(transfer, self.approver)


class CheckoutTransferEndpointTests(TestCase):
    """Thin smoke tests: routing and permission_map wiring, not the invariants above."""

    def setUp(self):
        category, brand, model, procurement = _create_catalog("EP-INV-001")
        self.checkout_asset = _create_asset("EP-CHK-ASSET-001", category, brand, model, procurement)
        self.transfer_asset = _create_asset(
            "EP-TRF-ASSET-001", category, brand, model, procurement, status="Assigned")
        _, self.holder = _create_profile("endpoint-holder")
        _, self.new_owner = _create_profile("endpoint-new-owner")
        self.transfer_asset.custodian = self.holder
        self.transfer_asset.save(update_fields=["custodian"])

    def test_checkout_create_requires_asset_transfer_permission(self):
        account, _ = _create_profile("no-permissions")
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(
            "/checkout/", {"asset": self.checkout_asset.pk, "user": self.holder.pk})

        self.assertEqual(response.status_code, 403)

    def test_checkout_create_and_checkin_round_trip(self):
        account, _ = _create_profile("checkout-operator", ("asset_transfer",))
        client = APIClient()
        client.force_authenticate(account)

        create_response = client.post(
            "/checkout/", {"asset": self.checkout_asset.pk, "user": self.holder.pk})
        self.assertEqual(create_response.status_code, 201)

        checkin_response = client.post(
            f"/checkout/{create_response.data['id']}/checkin/", {"condition": "Good"})
        self.assertEqual(checkin_response.status_code, 200)
        self.assertEqual(checkin_response.data["status"], "Returned")

    def test_transfer_request_requires_transfer_request_permission(self):
        account, _ = _create_profile("no-transfer-permission")
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(
            "/transfer/", {"asset": self.transfer_asset.pk, "new_owner": self.new_owner.pk})

        self.assertEqual(response.status_code, 403)

    def test_transfer_request_and_approve_round_trip(self):
        account, _ = _create_profile("transfer-requester", ("transfer_request", "asset_transfer"))
        client = APIClient()
        client.force_authenticate(account)

        create_response = client.post(
            "/transfer/", {"asset": self.transfer_asset.pk, "new_owner": self.new_owner.pk})
        self.assertEqual(create_response.status_code, 201)

        approve_response = client.post(f"/transfer/{create_response.data['id']}/approve/")
        self.assertEqual(approve_response.status_code, 200)
        self.assertEqual(approve_response.data["transfer_code"],
                         f"TRF-{create_response.data['id']:05d}")

    def test_transfer_reject_round_trip(self):
        account, _ = _create_profile("transfer-rejecter", ("transfer_request", "asset_transfer"))
        client = APIClient()
        client.force_authenticate(account)

        create_response = client.post(
            "/transfer/", {"asset": self.transfer_asset.pk, "new_owner": self.new_owner.pk})

        reject_response = client.post(f"/transfer/{create_response.data['id']}/reject/")
        self.assertEqual(reject_response.status_code, 200)
        self.assertEqual(reject_response.data["status"], "Rejected")
