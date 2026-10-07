from datetime import date, timedelta

from django.contrib.auth.models import User as AuthUser
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Department, Role
from accounts.tests import _create_profile
from catalog.models import Brand, Category, Model, PurchaseMode, Vendor

from .alerts import check_expiring_dates
from .checkout import check_in, check_out
from .models import (AmcContract, Asset, AssetCheckout, AssetConditionLog,
                     AssetDocument, AssetImage, LifecycleError, Procurement,
                     ServiceRecord)
from .service import close_service, open_service
from .transfer import approve, reject, request_transfer


def _create_catalog(invoice_number):
    category = Category.objects.create(category_name="Laptops")
    brand = Brand.objects.create(brand_name="Dell")
    model = Model.objects.create(model_name="Latitude")
    purchase_mode = PurchaseMode.objects.create(purchase_mode="Purchase")
    vendor, _ = Vendor.objects.get_or_create(name="Vendor")
    procurement = Procurement.objects.create(
        mode_of_purchase=purchase_mode,
        vendor=vendor,
        purchase_date=date(2026, 1, 1),
        invoice_date=date(2026, 1, 1),
        invoice_number=invoice_number,
    )
    return category, brand, model, procurement


def _amc_vendor():
    """A dated AMC contract records the Vendor it is with (B7)."""
    return Vendor.objects.get_or_create(name="AMC Vendor")[0]


class ServiceClosureContractTests(TestCase):
    """B5: closing is where cost becomes known and where custody operators learn the
    asset is back."""

    def setUp(self):
        category, brand, model, procurement = _create_catalog("SVC-CLOSE-001")
        self.asset = _create_asset("SVC-CLOSE-A", category, brand, model, procurement)
        self.vendor = Vendor.objects.create(name="Closing Vendor")
        _, self.operator = _create_profile("svc-operator", ("asset_custody_manage",))
        _, self.watcher = _create_profile("svc-watcher", ("asset_custody_manage",))

    def _open(self):
        return open_service(self.asset, self.vendor, self.operator)

    def test_closing_without_a_cost_is_rejected(self):
        """Covers: B5 FR-011, B5 ALR-006."""
        record = self._open()

        with self.assertRaises(LifecycleError):
            close_service(record, self.operator)

        record.refresh_from_db()
        self.assertEqual(record.status, "Open")

    def test_zero_cost_means_no_charge_and_is_accepted(self):
        """Covers: B5 FR-011."""
        record = close_service(self._open(), self.operator, cost=0)

        self.assertEqual(record.status, "Closed")
        self.assertEqual(record.cost, 0)

    def test_a_negative_cost_is_rejected(self):
        """Covers: B5 FR-011, B5 ALR-006."""
        with self.assertRaises(LifecycleError):
            close_service(self._open(), self.operator, cost=-5)

    def test_closing_notifies_every_custody_operator(self):
        """Covers: B5 FR-021, B5 FR-022."""
        from core.models import Notification
        before = Notification.objects.filter(user=self.watcher).count()

        close_service(self._open(), self.operator, cost=250)

        self.assertGreater(Notification.objects.filter(user=self.watcher).count(), before)


class AmcContractPartyTests(TestCase):
    """B7: a dated contract names its Vendor, and decision notices are addressed by
    permission rather than by Role display name."""

    def setUp(self):
        category, brand, model, procurement = _create_catalog("AMC-PARTY-001")
        self.asset = _create_asset("AMC-PARTY-A", category, brand, model, procurement)
        self.account, _ = _create_profile("amc-party-operator", ("asset_edit",))
        self.client_op = APIClient()
        self.client_op.force_authenticate(self.account)

    def test_renewal_without_a_vendor_is_rejected(self):
        response = self.client_op.post(
            f"/asset/{self.asset.pk}/renew_amc/",
            {"amc_start": "2026-01-01", "amc_end": "2027-01-01"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertFalse(AmcContract.objects.filter(asset=self.asset).exists())

    def test_renewal_records_the_vendor_on_the_new_contract(self):
        vendor = _amc_vendor()

        response = self.client_op.post(
            f"/asset/{self.asset.pk}/renew_amc/",
            {"amc_start": "2026-01-01", "amc_end": "2027-01-01", "vendor": vendor.pk},
            format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.asset.latest_amc.vendor, vendor)

    def test_an_unknown_vendor_is_rejected(self):
        response = self.client_op.post(
            f"/asset/{self.asset.pk}/renew_amc/",
            {"amc_start": "2026-01-01", "amc_end": "2027-01-01", "vendor": 9999},
            format="json")

        self.assertEqual(response.status_code, 400)

    def test_decision_notices_follow_the_permission_not_the_role_name(self):
        from core.models import Notification
        # Holds the manager-level code under a Role named something else.
        _, by_permission = _create_profile("amc-by-permission", ("asset_delete",))
        # Named "IT Manager" but granted nothing.
        _, by_name = _create_profile("amc-by-name")
        by_name.role.name = "IT Manager Renamed"
        by_name.role.save(update_fields=["name"])
        AmcContract.objects.create(asset=self.asset, vendor=_amc_vendor(),
                                   start_date=date(2026, 1, 1), end_date=date(2027, 1, 1))

        self.client_op.post(f"/asset/{self.asset.pk}/end_amc_support/",
                            {"reason": "Vendor exited"}, format="json")

        self.assertTrue(Notification.objects.filter(user=by_permission).exists())
        self.assertFalse(Notification.objects.filter(user=by_name).exists())


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
        self.vendor = Vendor.objects.create(name="Protected vendor")
        self.procurement = Procurement.objects.create(
            mode_of_purchase=self.purchase_mode,
            vendor=self.vendor,
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
        """Covers: B6 FR-006, B6 FR-007, B6 ALR-003."""
        for master in (self.category, self.brand, self.model, self.purchase_mode, self.vendor):
            with self.subTest(master=master):
                with self.assertRaises(ProtectedError):
                    master.delete()

        self.assertTrue(Asset.objects.filter(pk=self.asset.pk).exists())
        self.assertTrue(Procurement.objects.filter(pk=self.procurement.pk).exists())

    def test_delete_api_returns_conflict_for_referenced_master_records(self):
        """Covers: B6 FR-007, B6 ALR-003."""
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
            f"/vendor/{self.vendor.pk}/",
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
        """Covers: B6 FR-008."""
        unused_records = (
            Category.objects.create(category_name="Unused category"),
            Brand.objects.create(brand_name="Unused brand"),
            Model.objects.create(model_name="Unused model"),
            PurchaseMode.objects.create(purchase_mode="Unused mode"),
            Vendor.objects.create(name="Unused vendor"),
        )

        for master in unused_records:
            with self.subTest(master=master):
                model_class = type(master)
                master_id = master.pk
                master.delete()
                self.assertFalse(model_class.objects.filter(pk=master_id).exists())


class CheckoutLifecycleTests(TestCase):
    def setUp(self):
        category, brand, model, procurement = _create_catalog("CHK-INV-001")
        self.department = Department.objects.create(name="Engineering")
        self.asset = _create_asset("CHK-ASSET-001", category, brand, model, procurement)
        _, self.user = _create_profile("checkout-holder")
        self.user.department = self.department
        self.user.save(update_fields=["department"])

    def test_check_out_assigns_asset_to_user_and_their_department(self):
        """Covers: B3 FR-001, B3 FR-004, B3 FR-006, B2 FR-006."""
        checkout = check_out(self.asset, self.user, self.user)

        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, "Assigned")
        self.assertEqual(self.asset.custodian, self.user)
        self.assertEqual(self.asset.department, self.department)
        self.assertEqual(checkout.checkout_condition, self.asset.condition)

    def test_check_out_persists_intake_remarks(self):
        """Covers: B3 FR-014."""
        checkout = check_out(self.asset, self.user, self.user, remarks="Assigned for onboarding")

        self.assertEqual(checkout.remarks, "Assigned for onboarding")

    def test_check_out_notifies_the_new_custodian(self):
        """Covers: B3 FR-020."""
        from core.models import Notification
        with self.captureOnCommitCallbacks(execute=True):
            check_out(self.asset, self.user, self.user)

        self.assertTrue(Notification.objects.filter(user=self.user).exists())

    def test_check_out_rejects_an_unavailable_asset(self):
        """Covers: B3 FR-008, B3 ALR-004."""
        self.asset.status = "Assigned"
        self.asset.save(update_fields=["status"])

        with self.assertRaises(LifecycleError):
            check_out(self.asset, self.user, self.user)

    def test_check_in_returns_asset_to_available_with_new_condition(self):
        """Covers: B3 FR-002, B3 FR-014, B3 FR-023, B2 FR-006."""
        checkout = check_out(self.asset, self.user, self.user,
                             remarks="Issued with charger")

        checkout = check_in(checkout, "Damaged", remarks="Screen cracked")

        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, "Available")
        self.assertIsNone(self.asset.custodian)
        self.assertEqual(self.asset.condition, "Damaged")
        self.assertEqual(checkout.status, "Returned")
        # Return notes are their own field; the intake note survives the check-in.
        self.assertEqual(checkout.return_remarks, "Screen cracked")
        self.assertEqual(checkout.remarks, "Issued with charger")

    def test_check_in_rejects_an_already_closed_checkout(self):
        """Covers: B3 FR-009, B3 FR-012, B3 ALR-004."""
        checkout = check_out(self.asset, self.user, self.user)
        check_in(checkout, "Good")

        with self.assertRaises(LifecycleError):
            check_in(checkout, "Good")

    def test_check_in_rejects_an_invalid_condition(self):
        """Covers: B3 FR-010, B3 ALR-004, B2 FR-011."""
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
        _, self.approver = _create_profile("transfer-approver", ("asset_custody_manage",))
        self.asset = _create_asset(
            "TRF-ASSET-001", category, brand, model, procurement,
            status="Assigned", custodian=self.previous_owner, department=self.dept_a)

    def test_request_transfer_notifies_users_with_approval_permission(self):
        """Covers: B4 FR-016, B4 FR-017."""
        from core.models import Notification
        request_transfer(self.asset, self.new_owner, self.previous_owner)

        self.assertTrue(Notification.objects.filter(user=self.approver).exists())

    def test_request_transfer_captures_the_current_owner_and_department(self):
        """Covers: B4 FR-005, B4 FR-007."""
        transfer = request_transfer(self.asset, self.new_owner, self.previous_owner,
                                    new_department=self.dept_b)

        self.assertEqual(transfer.status, "Pending")
        self.assertEqual(transfer.previous_owner, self.previous_owner)
        self.assertEqual(transfer.previous_department, self.dept_a)
        self.assertEqual(transfer.new_department, self.dept_b)

    def test_approve_reassigns_custodian_department_and_condition(self):
        """Covers: B4 FR-008, B4 ALR-002, B2 FR-006, B2 ALR-004."""
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
        """Covers: B4 ALR-003, B4 ALR-004."""
        transfer = request_transfer(self.asset, self.new_owner, self.previous_owner)
        approve(transfer, self.approver)

        with self.assertRaises(LifecycleError):
            approve(transfer, self.approver)

    def test_reject_leaves_the_asset_untouched(self):
        """Covers: B4 FR-008, B4 ALR-003."""
        transfer = request_transfer(self.asset, self.new_owner, self.previous_owner)

        transfer = reject(transfer, self.approver)

        self.asset.refresh_from_db()
        self.assertEqual(self.asset.custodian, self.previous_owner)
        self.assertEqual(self.asset.department, self.dept_a)
        self.assertEqual(transfer.status, "Rejected")

    def test_reject_rejects_an_already_processed_transfer(self):
        """Covers: B4 ALR-003, B4 ALR-004."""
        transfer = request_transfer(self.asset, self.new_owner, self.previous_owner)
        reject(transfer, self.approver)

        with self.assertRaises(LifecycleError):
            reject(transfer, self.approver)

    def test_request_transfer_rejects_a_terminal_asset(self):
        """Covers: B4 FR-009, B4 ALR-003."""
        self.asset.status = "Sold"
        self.asset.save(update_fields=["status"])

        with self.assertRaises(LifecycleError):
            request_transfer(self.asset, self.new_owner, self.previous_owner)

    def test_approve_rejects_an_asset_that_turned_terminal_after_the_request(self):
        """Covers: B4 FR-010, B4 ALR-003."""
        transfer = request_transfer(self.asset, self.new_owner, self.previous_owner)
        self.asset.status = "Scrapped"
        self.asset.save(update_fields=["status"])

        with self.assertRaises(LifecycleError):
            approve(transfer, self.approver)

    def test_request_transfer_rejects_an_asset_under_repair(self):
        """Covers: B4 FR-009, B4 ALR-003."""
        self.asset.status = "Under Repair"
        self.asset.custodian = None
        self.asset.save(update_fields=["status", "custodian"])

        with self.assertRaises(LifecycleError):
            request_transfer(self.asset, self.new_owner, self.previous_owner)

    def test_approve_rejects_an_asset_sent_for_service_after_the_request(self):
        """Covers: B4 FR-010, B4 ALR-003."""
        transfer = request_transfer(self.asset, self.new_owner, self.previous_owner)
        self.asset.status = "Under Repair"
        self.asset.custodian = None
        self.asset.save(update_fields=["status", "custodian"])

        with self.assertRaises(LifecycleError):
            approve(transfer, self.approver)


class ServiceRecordLifecycleTests(TestCase):
    def setUp(self):
        category, brand, model, procurement = _create_catalog("SVC-INV-001")
        self.department = Department.objects.create(name="Engineering")
        _, self.user = _create_profile("service-holder")
        self.vendor = Vendor.objects.create(name="Repair Co")
        self.asset = _create_asset(
            "SVC-ASSET-001", category, brand, model, procurement,
            status="Assigned", custodian=self.user, department=self.department)

    def test_open_service_clears_custodian_and_marks_under_repair(self):
        """Covers: B5 FR-003, B5 FR-004, B2 FR-007, B2 ALR-005."""
        record = open_service(self.asset, self.vendor, self.user, reason="Screen flicker")

        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, "Under Repair")
        self.assertIsNone(self.asset.custodian)
        self.assertEqual(record.vendor, self.vendor)
        self.assertEqual(record.status, "Open")

    def test_open_service_notifies_the_previous_custodian(self):
        """Covers: B5 FR-021."""
        from core.models import Notification
        open_service(self.asset, self.vendor, self.user)

        self.assertTrue(Notification.objects.filter(user=self.user).exists())

    def test_open_service_closes_the_open_checkout_it_interrupts(self):
        """Covers: B5 FR-014, B5 ALR-007, B3 FR-015, B3 FR-028."""
        asset = _create_asset("SVC-CHECKOUT-ASSET-001", self.asset.category, self.asset.brand,
                              self.asset.model, self.asset.procurement)
        checkout = check_out(asset, self.user, self.user)

        open_service(asset, self.vendor, self.user, reason="Cracked screen")

        checkout.refresh_from_db()
        self.assertEqual(checkout.status, "Returned")
        self.assertIsNotNone(checkout.return_date)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Under Repair")
        self.assertIsNone(asset.custodian)

    def test_open_service_rejects_an_asset_already_under_repair(self):
        """Covers: B5 FR-007, B5 ALR-006."""
        self.asset.status = "Under Repair"
        self.asset.save(update_fields=["status"])

        with self.assertRaises(LifecycleError):
            open_service(self.asset, self.vendor, self.user)

    def test_open_service_rejects_a_terminal_asset(self):
        """Covers: B5 FR-007, B5 FR-008, B5 ALR-006."""
        self.asset.status = "Scrapped"
        self.asset.save(update_fields=["status"])

        with self.assertRaises(LifecycleError):
            open_service(self.asset, self.vendor, self.user)

    def test_close_service_returns_asset_to_available_without_reassigning_custodian(self):
        """Covers: B5 FR-010, B5 FR-012, B2 FR-007."""
        record = open_service(self.asset, self.vendor, self.user)

        record = close_service(record, self.user, cost=1500, remarks="Replaced screen")

        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, "Available")
        self.assertIsNone(self.asset.custodian)
        self.assertEqual(record.status, "Closed")
        self.assertEqual(record.cost, 1500)
        self.assertIsNotNone(record.returned_date)

    def test_close_service_rejects_an_already_closed_record(self):
        """Covers: B5 FR-013, B5 ALR-006."""
        record = open_service(self.asset, self.vendor, self.user)
        close_service(record, self.user, cost=0)

        with self.assertRaises(LifecycleError):
            close_service(record, self.user, cost=0)


class ServiceRecordEndpointTests(TestCase):
    """Thin smoke tests: routing and permission_map wiring."""

    def setUp(self):
        category, brand, model, procurement = _create_catalog("SVC-EP-INV-001")
        self.asset = _create_asset("SVC-EP-ASSET-001", category, brand, model, procurement)
        self.vendor = Vendor.objects.create(name="Endpoint Repair Co")

    def test_service_create_requires_asset_custody_manage_permission(self):
        """Covers: B5 ALR-001, B5 ALR-003, B1 FR-006."""
        account, _ = _create_profile("no-service-permission")
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(
            "/service/", {"asset": self.asset.pk, "vendor": self.vendor.pk})

        self.assertEqual(response.status_code, 403)

    def test_service_open_and_close_round_trip(self):
        """Covers: B5 FR-003, B5 FR-010."""
        account, _ = _create_profile("service-operator", ("asset_custody_manage",))
        client = APIClient()
        client.force_authenticate(account)

        create_response = client.post(
            "/service/", {"asset": self.asset.pk, "vendor": self.vendor.pk})
        self.assertEqual(create_response.status_code, 201)

        close_response = client.post(
            f"/service/{create_response.data['id']}/close/", {"cost": "250.00"})
        self.assertEqual(close_response.status_code, 200)
        self.assertEqual(close_response.data["status"], "Closed")


class AmcActionTests(TestCase):
    def setUp(self):
        category, brand, model, procurement = _create_catalog("AMC-INV-001")
        self.asset = _create_asset("AMC-ASSET-001", category, brand, model, procurement)
        _, self.manager = _create_profile("amc-it-manager")
        from accounts.models import Role
        manager_role, _ = Role.objects.get_or_create(name="IT Manager")
        self.manager.role = manager_role
        self.manager.save(update_fields=["role"])

    def test_renew_amc_sets_dates_and_notifies_it_manager(self):
        """Covers: B7 FR-009, B7 FR-021, B7 FR-033."""
        from core.models import Notification
        account, _ = _create_profile("amc-operator", ("asset_edit",))
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(f"/asset/{self.asset.pk}/renew_amc/",
                               {"amc_start": "2026-01-01", "amc_end": "2027-01-01",
                                "vendor": _amc_vendor().pk})

        self.assertEqual(response.status_code, 200)
        self.asset.refresh_from_db()
        self.assertTrue(self.asset.has_amc)
        self.assertEqual(self.asset.amc_status, "Active")
        self.assertTrue(Notification.objects.filter(user=self.manager).exists())

    def test_renew_amc_rejects_a_terminal_asset(self):
        """Covers: B7 FR-011, B7 ALR-003."""
        self.asset.status = "Sold"
        self.asset.save(update_fields=["status"])
        account, _ = _create_profile("amc-operator-terminal", ("asset_edit",))
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(f"/asset/{self.asset.pk}/renew_amc/",
                               {"amc_start": "2026-01-01", "amc_end": "2027-01-01",
                                "vendor": _amc_vendor().pk})

        self.assertEqual(response.status_code, 400)
        self.asset.refresh_from_db()
        self.assertFalse(self.asset.has_amc)

    def test_renew_amc_rejects_an_unparseable_date(self):
        """Covers: B7 FR-010, B7 ALR-003."""
        account, _ = _create_profile("amc-operator-baddate", ("asset_edit",))
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(f"/asset/{self.asset.pk}/renew_amc/",
                               {"amc_start": "not-a-date", "amc_end": "2027-01-01"})

        self.assertEqual(response.status_code, 400)
        self.asset.refresh_from_db()
        self.assertFalse(self.asset.has_amc)

    def test_renew_amc_rejects_end_before_start(self):
        """Covers: B7 FR-010, B7 ALR-003."""
        account, _ = _create_profile("amc-operator-order", ("asset_edit",))
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(f"/asset/{self.asset.pk}/renew_amc/",
                               {"amc_start": "2027-01-01", "amc_end": "2026-01-01"})

        self.assertEqual(response.status_code, 400)
        self.asset.refresh_from_db()
        self.assertFalse(self.asset.has_amc)

    def test_end_amc_support_requires_a_reason(self):
        """Covers: B7 FR-012, B7 ALR-003."""
        account, _ = _create_profile("amc-operator-2", ("asset_edit",))
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(f"/asset/{self.asset.pk}/end_amc_support/", {"reason": ""})

        self.assertEqual(response.status_code, 400)

    def test_end_amc_support_rejects_when_no_active_amc(self):
        """Covers: B7 FR-012, B7 ALR-003."""
        account, _ = _create_profile("amc-operator-none", ("asset_edit",))
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(f"/asset/{self.asset.pk}/end_amc_support/",
                               {"reason": "Vendor discontinued support"})

        self.assertEqual(response.status_code, 400)

    def test_end_amc_support_sets_status_and_notifies_it_manager(self):
        """Covers: B7 FR-012, B7 FR-021."""
        from core.models import Notification
        AmcContract.objects.create(
            asset=self.asset, start_date=date(2026, 1, 1), end_date=date(2027, 1, 1), status="Active")
        account, _ = _create_profile("amc-operator-3", ("asset_edit",))
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(f"/asset/{self.asset.pk}/end_amc_support/",
                               {"reason": "Vendor discontinued support"})

        self.assertEqual(response.status_code, 200)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.amc_status, "Ended")
        self.assertEqual(self.asset.amc_end_reason, "Vendor discontinued support")
        self.assertTrue(Notification.objects.filter(user=self.manager).exists())

    def test_renew_amc_ends_previous_contract_and_creates_new_one(self):
        """Covers: B7 FR-009, B7 FR-015, B7 ALR-004."""
        AmcContract.objects.create(
            asset=self.asset, start_date=date(2025, 1, 1), end_date=date(2026, 1, 1), status="Active")
        account, _ = _create_profile("amc-operator-renew-history", ("asset_edit",))
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(f"/asset/{self.asset.pk}/renew_amc/",
                               {"amc_start": "2026-01-01", "amc_end": "2027-01-01",
                                "vendor": _amc_vendor().pk})

        self.assertEqual(response.status_code, 200)
        contracts = list(AmcContract.objects.filter(asset=self.asset).order_by('start_date'))
        self.assertEqual(len(contracts), 2)
        self.assertEqual(contracts[0].status, "Ended")
        # The supersede marker is its own flag, and the operator's reason field stays
        # empty because no operator gave one (B7 FR-034).
        self.assertTrue(contracts[0].superseded_by_renewal)
        self.assertEqual(contracts[0].end_reason, "")
        self.assertEqual(contracts[1].status, "Active")


class AmcIncompleteStateTests(TestCase):
    """Covers the AMC 'Incomplete' contract state (CONTEXT.md): has_amc=True with no
    dates yet must be representable, not silently dropped."""

    def setUp(self):
        category, brand, model, procurement = _create_catalog("AMC-INC-INV-001")
        self.asset = _create_asset("AMC-INC-ASSET-001", category, brand, model, procurement)
        self.account, _ = _create_profile("amc-incomplete-operator", ("asset_edit",))
        self.client = APIClient()
        self.client.force_authenticate(self.account)

    def test_checking_has_amc_without_dates_creates_an_incomplete_contract(self):
        """Covers: B7 FR-007."""
        response = self.client.patch(
            f"/asset/{self.asset.pk}/", {"has_amc": True}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["has_amc"])
        self.assertEqual(response.data["amc_status"], "Incomplete")
        self.assertIsNone(response.data["amc_start"])
        contract = AmcContract.objects.get(asset=self.asset)
        self.assertEqual(contract.status, "Incomplete")
        self.assertIsNone(contract.start_date)

    def test_supplying_dates_later_completes_the_incomplete_contract(self):
        """Covers: B7 FR-008."""
        self.client.patch(f"/asset/{self.asset.pk}/", {"has_amc": True}, format="json")

        # Supplying dates completes the contract, and a dated contract needs its
        # Vendor (B7 FR-032) — the same rule renewal has always applied.
        response = self.client.patch(
            f"/asset/{self.asset.pk}/",
            {"has_amc": True, "amc_start": "2026-01-01", "amc_end": "2027-01-01",
             "amc_vendor": _amc_vendor().pk},
            format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AmcContract.objects.filter(asset=self.asset).count(), 1)
        contract = AmcContract.objects.get(asset=self.asset)
        self.assertEqual(contract.status, "Active")
        self.assertEqual(str(contract.start_date), "2026-01-01")
        self.assertIsNotNone(contract.vendor_id)

    def test_renew_amc_supersedes_an_incomplete_contract(self):
        """Covers: B7 FR-009, B7 FR-015."""
        AmcContract.objects.create(asset=self.asset, status="Incomplete")

        response = self.client.post(f"/asset/{self.asset.pk}/renew_amc/",
                                    {"amc_start": "2026-01-01", "amc_end": "2027-01-01",
                                "vendor": _amc_vendor().pk})

        self.assertEqual(response.status_code, 200)
        contracts = list(AmcContract.objects.filter(asset=self.asset).order_by('id'))
        self.assertEqual(len(contracts), 2)
        self.assertEqual(contracts[0].status, "Ended")
        self.assertEqual(contracts[1].status, "Active")

    def test_end_amc_support_can_end_an_incomplete_contract(self):
        """Covers: B7 FR-012."""
        AmcContract.objects.create(asset=self.asset, status="Incomplete")

        response = self.client.post(f"/asset/{self.asset.pk}/end_amc_support/",
                                    {"reason": "Decided against AMC after all"})

        self.assertEqual(response.status_code, 200)
        contract = AmcContract.objects.get(asset=self.asset)
        self.assertEqual(contract.status, "Ended")

    def test_incomplete_contract_created_after_an_ended_one_is_correctly_latest(self):
        """Covers: B7 FR-005, B7 FR-006."""
        # latest_amc must not fall back to a stale, fully-dated Ended contract just
        # because the new Incomplete row has no start_date to sort by.
        AmcContract.objects.create(
            asset=self.asset, start_date=date(2023, 1, 1), end_date=date(2024, 1, 1),
            status="Ended")

        response = self.client.patch(
            f"/asset/{self.asset.pk}/", {"has_amc": True}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["amc_status"], "Incomplete")
        self.assertIsNone(response.data["amc_start"])
        self.assertEqual(AmcContract.objects.filter(asset=self.asset).count(), 2)


class AssetStatusTransitionTests(TestCase):
    """Covers the update() guard in AssetSerializer that closes the direct-PATCH loophole
    flagged in review: reversing a disposal, and status/custodian getting out of sync."""

    def setUp(self):
        category, brand, model, procurement = _create_catalog("STATUS-INV-001")
        self.category, self.brand, self.model, self.procurement = category, brand, model, procurement
        _, self.holder = _create_profile("status-holder")
        self.account, _ = _create_profile("status-operator", ("asset_edit",))
        self.client = APIClient()
        self.client.force_authenticate(self.account)

    def _asset(self, asset_id, **extra):
        return _create_asset(asset_id, self.category, self.brand, self.model,
                             self.procurement, **extra)

    def test_cannot_reverse_out_of_a_terminal_status(self):
        """Covers: B2 FR-008, B2 ALR-006."""
        asset = self._asset("STATUS-ASSET-001", status="Sold")

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "Available"})

        self.assertEqual(response.status_code, 400)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Sold")

    def test_entering_sold_clears_custodian_even_if_payload_keeps_it(self):
        """Covers: B2 FR-009, B2 ALR-006."""
        asset = self._asset("STATUS-ASSET-002", status="Assigned", custodian=self.holder)

        response = self.client.patch(
            f"/asset/{asset.pk}/", {"status": "Sold", "custodian": self.holder.pk})

        self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Sold")
        self.assertIsNone(asset.custodian)

    def test_entering_lost_retains_custodian_even_if_payload_clears_it(self):
        """Covers: B2 FR-009, B2 ALR-006."""
        asset = self._asset("STATUS-ASSET-003", status="Assigned", custodian=self.holder)

        response = self.client.patch(
            f"/asset/{asset.pk}/", {"status": "Lost", "custodian": None},
            format="json")

        self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Lost")
        self.assertEqual(asset.custodian, self.holder)

    def test_administrative_status_edits_are_unaffected(self):
        """Covers: B2 FR-002."""
        asset = self._asset("STATUS-ASSET-004", status="Available")

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "In Storage"})

        self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "In Storage")

    def test_editing_unrelated_fields_without_a_status_change_is_unaffected(self):
        """Covers: B2 FR-002."""
        asset = self._asset("STATUS-ASSET-005", status="Assigned", custodian=self.holder)

        response = self.client.patch(f"/asset/{asset.pk}/", {"notes": "checked screen"})

        self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Assigned")
        self.assertEqual(asset.custodian, self.holder)
        self.assertEqual(asset.notes, "checked screen")

    def test_cannot_enter_assigned_by_direct_edit(self):
        """Covers: B2 FR-012, B2 ALR-004, B3 FR-007."""
        asset = self._asset("STATUS-ASSET-006", status="Available")

        response = self.client.patch(
            f"/asset/{asset.pk}/", {"status": "Assigned", "custodian": self.holder.pk})

        self.assertEqual(response.status_code, 400)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Available")
        self.assertIsNone(asset.custodian)

    def test_cannot_enter_under_repair_by_direct_edit(self):
        """Covers: B2 FR-012, B2 ALR-005, B5 FR-006."""
        asset = self._asset("STATUS-ASSET-007", status="Available")

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "Under Repair"})

        self.assertEqual(response.status_code, 400)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Available")

    def test_cannot_leave_assigned_by_direct_edit(self):
        """Covers: B2 FR-012, B2 ALR-004, B3 FR-007."""
        asset = self._asset("STATUS-ASSET-008", status="Assigned", custodian=self.holder)

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "Available"})

        self.assertEqual(response.status_code, 400)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Assigned")

    def test_cannot_leave_under_repair_by_direct_edit(self):
        """Covers: B2 FR-012, B2 ALR-005, B5 FR-006."""
        asset = self._asset("STATUS-ASSET-009", status="Under Repair")

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "Available"})

        self.assertEqual(response.status_code, 400)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Under Repair")

    def test_cannot_move_directly_between_assigned_and_under_repair(self):
        """Covers: B2 FR-012, B2 ALR-004, B2 ALR-005."""
        asset = self._asset("STATUS-ASSET-010", status="Assigned", custodian=self.holder)

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "Under Repair"})

        self.assertEqual(response.status_code, 400)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Assigned")

    def test_disposal_is_still_allowed_directly_from_assigned(self):
        """Covers: B2 FR-014."""
        asset = self._asset("STATUS-ASSET-011", status="Assigned", custodian=self.holder)

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "Sold"})

        self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Sold")
        self.assertIsNone(asset.custodian)

    def test_lost_is_still_allowed_directly_from_under_repair(self):
        """Covers: B2 FR-014."""
        asset = self._asset("STATUS-ASSET-012", status="Under Repair")

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "Lost"})

        self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Lost")

    def test_entering_terminal_status_closes_the_open_checkout(self):
        """Covers: B2 ALR-006, B3 FR-016."""
        asset = self._asset("STATUS-ASSET-013")
        checkout = check_out(asset, self.holder, self.holder)

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "Sold"})

        self.assertEqual(response.status_code, 200)
        checkout.refresh_from_db()
        self.assertEqual(checkout.status, "Returned")
        self.assertIsNotNone(checkout.return_date)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Sold")

    def test_entering_terminal_status_closes_the_open_service_record(self):
        """Covers: B2 ALR-006, B5 FR-016."""
        vendor = Vendor.objects.create(name="Status Repair Co")
        asset = self._asset("STATUS-ASSET-014")
        record = open_service(asset, vendor, self.holder)

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "Scrapped"})

        self.assertEqual(response.status_code, 200)
        record.refresh_from_db()
        self.assertEqual(record.status, "Closed")
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Scrapped")


class ExpiryAlertTests(TestCase):
    def setUp(self):
        category, brand, model, procurement = _create_catalog("ALERT-INV-001")
        self.category, self.brand, self.model, self.procurement = category, brand, model, procurement
        _, self.it_staff = _create_profile("alert-it-staff", ("asset_custody_manage",))

    def test_warranty_at_a_threshold_notifies_recipients(self):
        """Covers: B7 FR-016, B7 FR-017, B7 FR-018."""
        from core.models import Notification
        target = date.today() + timedelta(days=30)
        asset = _create_asset("ALERT-WARR-001", self.category, self.brand, self.model,
                              self.procurement, warranty_end=target)

        check_expiring_dates()

        self.assertTrue(Notification.objects.filter(
            user=self.it_staff, message__icontains=asset.asset_id).exists())

    def test_warranty_not_at_a_threshold_is_silent(self):
        """Covers: B7 FR-016."""
        from core.models import Notification
        off_threshold = date.today() + timedelta(days=29)
        _create_asset("ALERT-WARR-002", self.category, self.brand, self.model,
                      self.procurement, warranty_end=off_threshold)

        check_expiring_dates()

        self.assertFalse(Notification.objects.filter(user=self.it_staff).exists())

    def test_active_amc_at_a_threshold_notifies_recipients(self):
        """Covers: B7 FR-016, B7 FR-018."""
        from core.models import Notification
        target = date.today() + timedelta(days=7)
        asset = _create_asset("ALERT-AMC-001", self.category, self.brand, self.model, self.procurement)
        AmcContract.objects.create(
            asset=asset, start_date=date(2026, 1, 1), end_date=target, status="Active")

        check_expiring_dates()

        self.assertTrue(Notification.objects.filter(
            user=self.it_staff, message__icontains=asset.asset_id).exists())

    def test_ended_amc_at_a_threshold_is_silent(self):
        """Covers: B7 FR-019."""
        from core.models import Notification
        target = date.today() + timedelta(days=15)
        asset = _create_asset("ALERT-AMC-002", self.category, self.brand, self.model, self.procurement)
        AmcContract.objects.create(
            asset=asset, start_date=date(2026, 1, 1), end_date=target, status="Ended")

        check_expiring_dates()

        self.assertFalse(Notification.objects.filter(user=self.it_staff).exists())


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

    def test_checkout_create_requires_asset_custody_manage_permission(self):
        """Covers: B3 ALR-001, B3 ALR-003, B1 FR-006."""
        account, _ = _create_profile("no-permissions")
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(
            "/checkout/", {"asset": self.checkout_asset.pk, "user": self.holder.pk})

        self.assertEqual(response.status_code, 403)

    def test_checkout_create_and_checkin_round_trip(self):
        """Covers: B3 FR-001, B3 FR-002."""
        account, _ = _create_profile("checkout-operator", ("asset_custody_manage",))
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
        """Covers: B4 FR-002, B4 ALR-001, B1 FR-007."""
        account, _ = _create_profile("no-transfer-permission")
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(
            "/transfer/", {"asset": self.transfer_asset.pk, "new_owner": self.new_owner.pk})

        self.assertEqual(response.status_code, 403)

    def test_transfer_request_and_approve_round_trip(self):
        """Covers: B4 FR-005, B4 FR-008."""
        account, _ = _create_profile("transfer-requester", ("transfer_request", "asset_custody_manage"))
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
        """Covers: B4 FR-008."""
        account, _ = _create_profile("transfer-rejecter", ("transfer_request", "asset_custody_manage"))
        client = APIClient()
        client.force_authenticate(account)

        create_response = client.post(
            "/transfer/", {"asset": self.transfer_asset.pk, "new_owner": self.new_owner.pk})

        reject_response = client.post(f"/transfer/{create_response.data['id']}/reject/")
        self.assertEqual(reject_response.status_code, 200)
        self.assertEqual(reject_response.data["status"], "Rejected")


class BaselineConformanceTests(TestCase):
    """Covers decisions the roadmap records as resolved but the implementation did
    not enforce: C2 creation limits, C4 AMC flag semantics, C6 Employee scope,
    C8 Transfer document access, and the B3/B4 lifecycle rules."""

    def setUp(self):
        self.category, self.brand, self.model, self.procurement = _create_catalog("CONF-1")
        self.department = Department.objects.create(name="Conformance Dept")
        _, self.employee = _create_profile("conf-employee")
        # The named Employee Role is seeded by accounts migration 0002 and already
        # carries asset_view; scope comes from the Role, not from the permission.
        self.employee.role = Role.objects.get(name="Employee")
        self.employee.department = self.department
        self.employee.save(update_fields=["role", "department"])
        _, self.colleague = _create_profile("conf-colleague", ("asset_view",))
        self.operator_account, self.operator = _create_profile(
            "conf-operator", ("asset_view", "asset_create", "asset_edit",
                              "asset_custody_manage", "transfer_request"))
        self.client_op = APIClient()
        self.client_op.force_authenticate(self.operator_account)

    def _asset(self, asset_id, **extra):
        return _create_asset(asset_id, self.category, self.brand, self.model,
                             self.procurement, **extra)

    # --- C2: creation cannot short-circuit custody ---

    def test_create_rejects_a_lifecycle_managed_status(self):
        """Covers: B2 FR-013, B2 ALR-007."""
        response = self.client_op.post("/asset/", {
            "asset_id": "C2-A", "tag_number": "C2-A-T", "serial_number": "C2-A-S",
            "category": self.category.pk, "brand": self.brand.pk, "model": self.model.pk,
            "status": "Assigned"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("status", response.data)

    def test_create_rejects_a_custodian(self):
        """Covers: B2 FR-013, B2 ALR-007."""
        response = self.client_op.post("/asset/", {
            "asset_id": "C2-B", "tag_number": "C2-B-T", "serial_number": "C2-B-S",
            "category": self.category.pk, "brand": self.brand.pk, "model": self.model.pk,
            "custodian": self.employee.pk}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("custodian", response.data)

    def test_edit_cannot_assign_a_custodian_directly(self):
        """Covers: B2 ALR-007."""
        asset = self._asset("C2-EDIT")

        response = self.client_op.patch(
            f"/asset/{asset.pk}/", {"custodian": self.employee.pk}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("custodian", response.data)

    def test_marking_an_asset_lost_still_retains_its_custodian(self):
        """Covers: B2 FR-009."""
        asset = self._asset("C2-LOST", status="Assigned", custodian=self.employee)

        response = self.client_op.patch(
            f"/asset/{asset.pk}/", {"status": "Lost"}, format="json")

        self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.custodian, self.employee)

    def test_create_still_accepts_available_and_in_storage(self):
        """Covers: B2 FR-013."""
        for i, status_value in enumerate(("Available", "In Storage")):
            response = self.client_op.post("/asset/", {
                "asset_id": f"C2-OK{i}", "tag_number": f"C2-OK{i}-T",
                "serial_number": f"C2-OK{i}-S", "category": self.category.pk,
                "brand": self.brand.pk, "model": self.model.pk,
                "status": status_value}, format="json")
            self.assertEqual(response.status_code, 201, status_value)

    # --- C6: Employee reads only its own custodial records ---

    def test_employee_sees_only_assets_it_holds(self):
        """Covers: B1 FR-008, B1 FR-012, B2 ALR-009."""
        mine = self._asset("C6-MINE", status="Assigned", custodian=self.employee)
        self._asset("C6-THEIRS", status="Assigned", custodian=self.colleague)
        client = APIClient()
        client.force_authenticate(self.employee.account)

        rows = client.get("/asset/").data

        self.assertEqual([row["asset_id"] for row in rows], [mine.asset_id])

    def test_employee_cannot_reach_another_holders_asset_by_id(self):
        """Covers: B1 ALR-005, B2 ALR-009."""
        theirs = self._asset("C6-BYID", status="Assigned", custodian=self.colleague)
        client = APIClient()
        client.force_authenticate(self.employee.account)

        self.assertEqual(client.get(f"/asset/{theirs.pk}/").status_code, 404)

    def test_employee_is_denied_the_user_directory(self):
        """Covers: B1 FR-012, B1 ALR-005."""
        client = APIClient()
        client.force_authenticate(self.employee.account)

        self.assertEqual(client.get("/user/directory/").status_code, 403)

    def test_a_non_employee_role_still_reads_globally(self):
        """Covers: B1 FR-012, B2 ALR-009."""
        self._asset("C6-GLOBAL", status="Assigned", custodian=self.colleague)
        client = APIClient()
        client.force_authenticate(self.colleague.account)

        self.assertTrue(client.get("/asset/").data)
        self.assertEqual(client.get("/user/directory/").status_code, 200)

    def _employee_client(self):
        client = APIClient()
        client.force_authenticate(self.employee.account)
        return client

    def test_employee_sees_only_its_own_checkouts(self):
        """Covers: B1 FR-012."""
        mine = self._asset("C6-CO-MINE")
        theirs = self._asset("C6-CO-THEIRS")
        self.client_op.post("/checkout/", {"asset": mine.pk, "user": self.employee.pk},
                            format="json")
        self.client_op.post("/checkout/", {"asset": theirs.pk, "user": self.colleague.pk},
                            format="json")

        rows = self._employee_client().get("/checkout/").data

        self.assertEqual([row["asset_details"]["asset_id"] for row in rows], [mine.asset_id])

    def test_employee_sees_service_records_only_for_assets_it_holds(self):
        """Covers: B1 FR-012, B5 ALR-002."""
        held = self._asset("C6-SVC-MINE", status="Assigned", custodian=self.employee)
        other = self._asset("C6-SVC-OTHER")
        vendor, _ = Vendor.objects.get_or_create(name="Vendor")
        ServiceRecord.objects.create(asset=held, vendor=vendor)
        ServiceRecord.objects.create(asset=other, vendor=vendor)

        rows = self._employee_client().get("/service/").data

        self.assertEqual([row["asset_details"]["asset_id"] for row in rows], [held.asset_id])

    def test_employee_sees_files_only_for_assets_it_holds(self):
        """Covers: B1 FR-012."""
        held = self._asset("C6-DOC-MINE", status="Assigned", custodian=self.employee)
        other = self._asset("C6-DOC-OTHER", status="Assigned", custodian=self.colleague)
        AssetDocument.objects.create(asset=held, file="a.pdf", file_name="mine.pdf")
        AssetDocument.objects.create(asset=other, file="b.pdf", file_name="theirs.pdf")
        AssetImage.objects.create(asset=other, file="c.png", file_name="theirs.png")
        client = self._employee_client()

        self.assertEqual([d["file_name"] for d in client.get("/asset_document/").data],
                         ["mine.pdf"])
        self.assertEqual(client.get("/asset_image/").data, [])

    def test_employee_is_denied_procurement_entirely(self):
        """Covers: B6 FR-015, B1 FR-012."""
        client = self._employee_client()

        self.assertEqual(client.get("/procurement/").status_code, 403)
        self.assertEqual(
            client.get(f"/procurement/{self.procurement.pk}/").status_code, 403)

    def test_employee_dashboard_counts_only_its_own_assets(self):
        """Covers: B9 FR-007, B1 FR-012."""
        self._asset("C6-DASH-MINE", status="Assigned", custodian=self.employee)
        self._asset("C6-DASH-A")
        self._asset("C6-DASH-B")
        client = self._employee_client()

        kpis = client.get("/dashboard/").data["kpis"]
        chart = client.get("/charts/status-distribution/").data

        self.assertEqual(kpis["total_assets"], 1)
        self.assertEqual(sum(chart["data"]), 1)

    def test_a_global_reader_still_sees_every_record(self):
        """Covers: B1 FR-012."""
        held = self._asset("C6-ALL-MINE", status="Assigned", custodian=self.employee)
        other = self._asset("C6-ALL-OTHER")
        vendor, _ = Vendor.objects.get_or_create(name="Vendor")
        ServiceRecord.objects.create(asset=held, vendor=vendor)
        ServiceRecord.objects.create(asset=other, vendor=vendor)
        AssetDocument.objects.create(asset=held, file="a.pdf", file_name="mine.pdf")
        self.client_op.post("/checkout/", {"asset": other.pk, "user": self.colleague.pk},
                            format="json")

        self.assertEqual(len(self.client_op.get("/service/").data), 2)
        self.assertEqual(len(self.client_op.get("/asset_document/").data), 1)
        self.assertEqual(len(self.client_op.get("/checkout/").data), 1)
        self.assertEqual(self.client_op.get("/procurement/").status_code, 200)
        self.assertEqual(self.client_op.get("/dashboard/").data["kpis"]["total_assets"],
                         Asset.objects.count())

    # --- B3: check-in records an inspection and preserves intake data ---

    def test_check_in_requires_a_return_condition(self):
        """Covers: B3 FR-024, B3 ALR-004."""
        asset = self._asset("B3-COND", department=self.department)
        checkout = self.client_op.post(
            "/checkout/", {"asset": asset.pk, "user": self.employee.pk}, format="json")

        response = self.client_op.post(
            f"/checkout/{checkout.data['id']}/checkin/", {}, format="json")

        self.assertEqual(response.status_code, 400)

    def test_check_in_clears_department_and_logs_the_inspection(self):
        """Covers: B3 FR-023, B3 FR-025, B2 FR-015."""
        asset = self._asset("B3-DEPT", department=self.department)
        checkout = self.client_op.post(
            "/checkout/", {"asset": asset.pk, "user": self.employee.pk,
                           "remarks": "Issued with charger"}, format="json")
        logs_before = AssetConditionLog.objects.filter(asset=asset).count()

        response = self.client_op.post(
            f"/checkout/{checkout.data['id']}/checkin/",
            {"condition": "Damaged", "remarks": "Screen cracked"}, format="json")

        self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertIsNone(asset.department)
        self.assertIsNone(asset.custodian)
        self.assertEqual(AssetConditionLog.objects.filter(asset=asset).count(),
                         logs_before + 1)
        record = AssetCheckout.objects.get(pk=checkout.data["id"])
        self.assertEqual(record.remarks, "Issued with charger")
        self.assertEqual(record.return_remarks, "Screen cracked")

    def test_an_interrupting_closure_also_preserves_intake_remarks(self):
        """Covers: B3 FR-014, B3 FR-028."""
        asset = self._asset("B3-INT")
        self.client_op.post("/checkout/", {"asset": asset.pk, "user": self.employee.pk,
                                           "remarks": "Issued with dock"}, format="json")
        vendor, _ = Vendor.objects.get_or_create(name="Vendor")

        self.client_op.post("/service/", {"asset": asset.pk, "vendor": vendor.pk},
                            format="json")

        record = asset.checkouts.get()
        self.assertEqual(record.status, "Returned")
        self.assertEqual(record.remarks, "Issued with dock")
        self.assertIn("Auto-closed", record.return_remarks)

    # --- B4: a transfer needs two parties and one open request ---

    def test_transfer_rejects_the_current_custodian_as_target(self):
        """Covers: B4 FR-001, B4 ALR-007."""
        asset = self._asset("B4-SAME", status="Assigned", custodian=self.employee)

        response = self.client_op.post(
            "/transfer/", {"asset": asset.pk, "new_owner": self.employee.pk}, format="json")

        self.assertEqual(response.status_code, 400)

    def test_transfer_rejects_a_second_pending_request(self):
        """Covers: B4 FR-005, B4 ALR-007."""
        asset = self._asset("B4-DUP", status="Assigned", custodian=self.employee)
        first = self.client_op.post(
            "/transfer/", {"asset": asset.pk, "new_owner": self.colleague.pk}, format="json")
        self.assertEqual(first.status_code, 201)

        second = self.client_op.post(
            "/transfer/", {"asset": asset.pk, "new_owner": self.colleague.pk}, format="json")

        self.assertEqual(second.status_code, 400)

    def test_a_new_request_is_allowed_once_the_previous_one_is_decided(self):
        """Covers: B4 ALR-007."""
        asset = self._asset("B4-AFTER", status="Assigned", custodian=self.employee)
        first = self.client_op.post(
            "/transfer/", {"asset": asset.pk, "new_owner": self.colleague.pk}, format="json")
        self.client_op.post(f"/transfer/{first.data['id']}/reject/", format="json")

        second = self.client_op.post(
            "/transfer/", {"asset": asset.pk, "new_owner": self.colleague.pk}, format="json")

        self.assertEqual(second.status_code, 201)

    # --- C8: Transfer document access, limited to records visible under B1 ---

    def test_asset_view_holder_may_download_the_transfer_document(self):
        """Covers: B4 FR-015."""
        asset = self._asset("C8-PDF", status="Assigned", custodian=self.employee)
        transfer = self.client_op.post(
            "/transfer/", {"asset": asset.pk, "new_owner": self.colleague.pk}, format="json")
        client = APIClient()
        client.force_authenticate(self.colleague.account)

        response = client.get(f"/transfer/{transfer.data['id']}/document/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_employee_may_download_the_document_for_a_transfer_it_is_party_to(self):
        """Covers: B4 FR-015, B1 FR-012."""
        asset = self._asset("C8-MINE", status="Assigned", custodian=self.employee)
        transfer = self.client_op.post(
            "/transfer/", {"asset": asset.pk, "new_owner": self.colleague.pk}, format="json")
        client = APIClient()
        client.force_authenticate(self.employee.account)

        response = client.get(f"/transfer/{transfer.data['id']}/document/")

        self.assertEqual(response.status_code, 200)

    def test_employee_cannot_download_someone_elses_transfer_document(self):
        """Covers: B4 FR-015, B1 ALR-005."""
        asset = self._asset("C8-THEIRS", status="Assigned", custodian=self.colleague)
        transfer = self.client_op.post(
            "/transfer/", {"asset": asset.pk, "new_owner": self.operator.pk}, format="json")
        client = APIClient()
        client.force_authenticate(self.employee.account)

        self.assertEqual(
            client.get(f"/transfer/{transfer.data['id']}/document/").status_code, 404)

    def test_employee_lists_only_transfers_it_is_party_to(self):
        """Covers: B4 FR-004, B1 FR-012."""
        mine = self._asset("C8-LIST-MINE", status="Assigned", custodian=self.employee)
        theirs = self._asset("C8-LIST-THEIRS", status="Assigned", custodian=self.colleague)
        self.client_op.post("/transfer/", {"asset": mine.pk, "new_owner": self.colleague.pk},
                            format="json")
        self.client_op.post("/transfer/", {"asset": theirs.pk, "new_owner": self.operator.pk},
                            format="json")
        client = APIClient()
        client.force_authenticate(self.employee.account)

        rows = client.get("/transfer/").data

        self.assertEqual([row["asset_details"]["asset_id"] for row in rows],
                         [mine.asset_id])

    def test_a_non_employee_role_still_sees_every_transfer(self):
        """Covers: B4 FR-004."""
        mine = self._asset("C8-ALL-A", status="Assigned", custodian=self.employee)
        theirs = self._asset("C8-ALL-B", status="Assigned", custodian=self.colleague)
        self.client_op.post("/transfer/", {"asset": mine.pk, "new_owner": self.colleague.pk},
                            format="json")
        self.client_op.post("/transfer/", {"asset": theirs.pk, "new_owner": self.operator.pk},
                            format="json")
        client = APIClient()
        client.force_authenticate(self.colleague.account)

        self.assertEqual(len(client.get("/transfer/").data), 2)

    # --- C4: the AMC flag describes the current contract only ---

    def test_has_amc_is_false_once_the_contract_is_ended(self):
        """Covers: B7 FR-006."""
        asset = self._asset("C4-END")
        contract = AmcContract.objects.create(
            asset=asset, start_date=date(2026, 1, 1), end_date=date(2027, 1, 1))
        self.assertTrue(asset.has_amc)

        contract.status = "Ended"
        contract.save(update_fields=["status"])

        self.assertFalse(asset.has_amc)
        self.assertEqual(asset.amc_status, "Ended")

    def test_has_amc_is_true_while_a_contract_is_incomplete(self):
        """Covers: B7 FR-006, B7 FR-007."""
        asset = self._asset("C4-INC")
        AmcContract.objects.create(asset=asset, status="Incomplete")

        self.assertTrue(asset.has_amc)

    def test_renewing_after_an_ended_contract_reports_has_amc_again(self):
        """Covers: B7 FR-006, B7 FR-037."""
        asset = self._asset("C4-RENEW")
        AmcContract.objects.create(asset=asset, status="Ended", end_reason="Lapsed")

        response = self.client_op.post(
            f"/asset/{asset.pk}/renew_amc/",
            {"amc_start": "2026-01-01", "amc_end": "2027-01-01",
             "vendor": _amc_vendor().pk}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(asset.has_amc)
        self.assertEqual(asset.amc_contracts.count(), 2)
