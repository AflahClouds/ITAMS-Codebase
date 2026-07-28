from datetime import date, timedelta

from django.contrib.auth.models import User as AuthUser
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Department
from accounts.tests import _create_profile
from catalog.models import Brand, Category, Model, PurchaseMode, Vendor

from .alerts import check_expiring_dates
from .checkout import check_in, check_out
from .models import AmcContract, Asset, LifecycleError, Procurement
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
        for master in (self.category, self.brand, self.model, self.purchase_mode, self.vendor):
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
        from core.models import Notification
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
        _, self.approver = _create_profile("transfer-approver", ("asset_custody_manage",))
        self.asset = _create_asset(
            "TRF-ASSET-001", category, brand, model, procurement,
            status="Assigned", custodian=self.previous_owner, department=self.dept_a)

    def test_request_transfer_notifies_users_with_approval_permission(self):
        from core.models import Notification
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

    def test_request_transfer_rejects_a_terminal_asset(self):
        self.asset.status = "Sold"
        self.asset.save(update_fields=["status"])

        with self.assertRaises(LifecycleError):
            request_transfer(self.asset, self.new_owner, self.previous_owner)

    def test_approve_rejects_an_asset_that_turned_terminal_after_the_request(self):
        transfer = request_transfer(self.asset, self.new_owner, self.previous_owner)
        self.asset.status = "Scrapped"
        self.asset.save(update_fields=["status"])

        with self.assertRaises(LifecycleError):
            approve(transfer, self.approver)

    def test_request_transfer_rejects_an_asset_under_repair(self):
        self.asset.status = "Under Repair"
        self.asset.custodian = None
        self.asset.save(update_fields=["status", "custodian"])

        with self.assertRaises(LifecycleError):
            request_transfer(self.asset, self.new_owner, self.previous_owner)

    def test_approve_rejects_an_asset_sent_for_service_after_the_request(self):
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
        record = open_service(self.asset, self.vendor, self.user, reason="Screen flicker")

        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, "Under Repair")
        self.assertIsNone(self.asset.custodian)
        self.assertEqual(record.vendor, self.vendor)
        self.assertEqual(record.status, "Open")

    def test_open_service_notifies_the_previous_custodian(self):
        from core.models import Notification
        open_service(self.asset, self.vendor, self.user)

        self.assertTrue(Notification.objects.filter(user=self.user).exists())

    def test_open_service_closes_the_open_checkout_it_interrupts(self):
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
        self.asset.status = "Under Repair"
        self.asset.save(update_fields=["status"])

        with self.assertRaises(LifecycleError):
            open_service(self.asset, self.vendor, self.user)

    def test_open_service_rejects_a_terminal_asset(self):
        self.asset.status = "Scrapped"
        self.asset.save(update_fields=["status"])

        with self.assertRaises(LifecycleError):
            open_service(self.asset, self.vendor, self.user)

    def test_close_service_returns_asset_to_available_without_reassigning_custodian(self):
        record = open_service(self.asset, self.vendor, self.user)

        record = close_service(record, self.user, cost=1500, remarks="Replaced screen")

        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, "Available")
        self.assertIsNone(self.asset.custodian)
        self.assertEqual(record.status, "Closed")
        self.assertEqual(record.cost, 1500)
        self.assertIsNotNone(record.returned_date)

    def test_close_service_rejects_an_already_closed_record(self):
        record = open_service(self.asset, self.vendor, self.user)
        close_service(record, self.user)

        with self.assertRaises(LifecycleError):
            close_service(record, self.user)


class ServiceRecordEndpointTests(TestCase):
    """Thin smoke tests: routing and permission_map wiring."""

    def setUp(self):
        category, brand, model, procurement = _create_catalog("SVC-EP-INV-001")
        self.asset = _create_asset("SVC-EP-ASSET-001", category, brand, model, procurement)
        self.vendor = Vendor.objects.create(name="Endpoint Repair Co")

    def test_service_create_requires_asset_custody_manage_permission(self):
        account, _ = _create_profile("no-service-permission")
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(
            "/service/", {"asset": self.asset.pk, "vendor": self.vendor.pk})

        self.assertEqual(response.status_code, 403)

    def test_service_open_and_close_round_trip(self):
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
        from core.models import Notification
        account, _ = _create_profile("amc-operator", ("asset_edit",))
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(f"/asset/{self.asset.pk}/renew_amc/",
                               {"amc_start": "2026-01-01", "amc_end": "2027-01-01"})

        self.assertEqual(response.status_code, 200)
        self.asset.refresh_from_db()
        self.assertTrue(self.asset.has_amc)
        self.assertEqual(self.asset.amc_status, "Active")
        self.assertTrue(Notification.objects.filter(user=self.manager).exists())

    def test_renew_amc_rejects_a_terminal_asset(self):
        self.asset.status = "Sold"
        self.asset.save(update_fields=["status"])
        account, _ = _create_profile("amc-operator-terminal", ("asset_edit",))
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(f"/asset/{self.asset.pk}/renew_amc/",
                               {"amc_start": "2026-01-01", "amc_end": "2027-01-01"})

        self.assertEqual(response.status_code, 400)
        self.asset.refresh_from_db()
        self.assertFalse(self.asset.has_amc)

    def test_renew_amc_rejects_an_unparseable_date(self):
        account, _ = _create_profile("amc-operator-baddate", ("asset_edit",))
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(f"/asset/{self.asset.pk}/renew_amc/",
                               {"amc_start": "not-a-date", "amc_end": "2027-01-01"})

        self.assertEqual(response.status_code, 400)
        self.asset.refresh_from_db()
        self.assertFalse(self.asset.has_amc)

    def test_renew_amc_rejects_end_before_start(self):
        account, _ = _create_profile("amc-operator-order", ("asset_edit",))
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(f"/asset/{self.asset.pk}/renew_amc/",
                               {"amc_start": "2027-01-01", "amc_end": "2026-01-01"})

        self.assertEqual(response.status_code, 400)
        self.asset.refresh_from_db()
        self.assertFalse(self.asset.has_amc)

    def test_end_amc_support_requires_a_reason(self):
        account, _ = _create_profile("amc-operator-2", ("asset_edit",))
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(f"/asset/{self.asset.pk}/end_amc_support/", {"reason": ""})

        self.assertEqual(response.status_code, 400)

    def test_end_amc_support_rejects_when_no_active_amc(self):
        account, _ = _create_profile("amc-operator-none", ("asset_edit",))
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(f"/asset/{self.asset.pk}/end_amc_support/",
                               {"reason": "Vendor discontinued support"})

        self.assertEqual(response.status_code, 400)

    def test_end_amc_support_sets_status_and_notifies_it_manager(self):
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
        AmcContract.objects.create(
            asset=self.asset, start_date=date(2025, 1, 1), end_date=date(2026, 1, 1), status="Active")
        account, _ = _create_profile("amc-operator-renew-history", ("asset_edit",))
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(f"/asset/{self.asset.pk}/renew_amc/",
                               {"amc_start": "2026-01-01", "amc_end": "2027-01-01"})

        self.assertEqual(response.status_code, 200)
        contracts = list(AmcContract.objects.filter(asset=self.asset).order_by('start_date'))
        self.assertEqual(len(contracts), 2)
        self.assertEqual(contracts[0].status, "Ended")
        self.assertEqual(contracts[0].end_reason, "Renewed")
        self.assertEqual(contracts[1].status, "Active")


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
        asset = self._asset("STATUS-ASSET-001", status="Sold")

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "Available"})

        self.assertEqual(response.status_code, 400)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Sold")

    def test_entering_sold_clears_custodian_even_if_payload_keeps_it(self):
        asset = self._asset("STATUS-ASSET-002", status="Assigned", custodian=self.holder)

        response = self.client.patch(
            f"/asset/{asset.pk}/", {"status": "Sold", "custodian": self.holder.pk})

        self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Sold")
        self.assertIsNone(asset.custodian)

    def test_entering_lost_retains_custodian_even_if_payload_clears_it(self):
        asset = self._asset("STATUS-ASSET-003", status="Assigned", custodian=self.holder)

        response = self.client.patch(
            f"/asset/{asset.pk}/", {"status": "Lost", "custodian": None},
            format="json")

        self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Lost")
        self.assertEqual(asset.custodian, self.holder)

    def test_administrative_status_edits_are_unaffected(self):
        asset = self._asset("STATUS-ASSET-004", status="Available")

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "In Storage"})

        self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "In Storage")

    def test_editing_unrelated_fields_without_a_status_change_is_unaffected(self):
        asset = self._asset("STATUS-ASSET-005", status="Assigned", custodian=self.holder)

        response = self.client.patch(f"/asset/{asset.pk}/", {"notes": "checked screen"})

        self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Assigned")
        self.assertEqual(asset.custodian, self.holder)
        self.assertEqual(asset.notes, "checked screen")

    def test_cannot_enter_assigned_by_direct_edit(self):
        asset = self._asset("STATUS-ASSET-006", status="Available")

        response = self.client.patch(
            f"/asset/{asset.pk}/", {"status": "Assigned", "custodian": self.holder.pk})

        self.assertEqual(response.status_code, 400)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Available")
        self.assertIsNone(asset.custodian)

    def test_cannot_enter_under_repair_by_direct_edit(self):
        asset = self._asset("STATUS-ASSET-007", status="Available")

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "Under Repair"})

        self.assertEqual(response.status_code, 400)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Available")

    def test_cannot_leave_assigned_by_direct_edit(self):
        asset = self._asset("STATUS-ASSET-008", status="Assigned", custodian=self.holder)

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "Available"})

        self.assertEqual(response.status_code, 400)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Assigned")

    def test_cannot_leave_under_repair_by_direct_edit(self):
        asset = self._asset("STATUS-ASSET-009", status="Under Repair")

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "Available"})

        self.assertEqual(response.status_code, 400)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Under Repair")

    def test_cannot_move_directly_between_assigned_and_under_repair(self):
        asset = self._asset("STATUS-ASSET-010", status="Assigned", custodian=self.holder)

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "Under Repair"})

        self.assertEqual(response.status_code, 400)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Assigned")

    def test_disposal_is_still_allowed_directly_from_assigned(self):
        asset = self._asset("STATUS-ASSET-011", status="Assigned", custodian=self.holder)

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "Sold"})

        self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Sold")
        self.assertIsNone(asset.custodian)

    def test_lost_is_still_allowed_directly_from_under_repair(self):
        asset = self._asset("STATUS-ASSET-012", status="Under Repair")

        response = self.client.patch(f"/asset/{asset.pk}/", {"status": "Lost"})

        self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.status, "Lost")


class ExpiryAlertTests(TestCase):
    def setUp(self):
        category, brand, model, procurement = _create_catalog("ALERT-INV-001")
        self.category, self.brand, self.model, self.procurement = category, brand, model, procurement
        _, self.it_staff = _create_profile("alert-it-staff", ("asset_custody_manage",))

    def test_warranty_at_a_threshold_notifies_recipients(self):
        from core.models import Notification
        target = date.today() + timedelta(days=30)
        asset = _create_asset("ALERT-WARR-001", self.category, self.brand, self.model,
                              self.procurement, warranty_end=target)

        check_expiring_dates()

        self.assertTrue(Notification.objects.filter(
            user=self.it_staff, message__icontains=asset.asset_id).exists())

    def test_warranty_not_at_a_threshold_is_silent(self):
        from core.models import Notification
        off_threshold = date.today() + timedelta(days=29)
        _create_asset("ALERT-WARR-002", self.category, self.brand, self.model,
                      self.procurement, warranty_end=off_threshold)

        check_expiring_dates()

        self.assertFalse(Notification.objects.filter(user=self.it_staff).exists())

    def test_active_amc_at_a_threshold_notifies_recipients(self):
        from core.models import Notification
        target = date.today() + timedelta(days=7)
        asset = _create_asset("ALERT-AMC-001", self.category, self.brand, self.model, self.procurement)
        AmcContract.objects.create(
            asset=asset, start_date=date(2026, 1, 1), end_date=target, status="Active")

        check_expiring_dates()

        self.assertTrue(Notification.objects.filter(
            user=self.it_staff, message__icontains=asset.asset_id).exists())

    def test_ended_amc_at_a_threshold_is_silent(self):
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
        account, _ = _create_profile("no-permissions")
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(
            "/checkout/", {"asset": self.checkout_asset.pk, "user": self.holder.pk})

        self.assertEqual(response.status_code, 403)

    def test_checkout_create_and_checkin_round_trip(self):
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
        account, _ = _create_profile("no-transfer-permission")
        client = APIClient()
        client.force_authenticate(account)

        response = client.post(
            "/transfer/", {"asset": self.transfer_asset.pk, "new_owner": self.new_owner.pk})

        self.assertEqual(response.status_code, 403)

    def test_transfer_request_and_approve_round_trip(self):
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
        account, _ = _create_profile("transfer-rejecter", ("transfer_request", "asset_custody_manage"))
        client = APIClient()
        client.force_authenticate(account)

        create_response = client.post(
            "/transfer/", {"asset": self.transfer_asset.pk, "new_owner": self.new_owner.pk})

        reject_response = client.post(f"/transfer/{create_response.data['id']}/reject/")
        self.assertEqual(reject_response.status_code, 200)
        self.assertEqual(reject_response.data["status"], "Rejected")
