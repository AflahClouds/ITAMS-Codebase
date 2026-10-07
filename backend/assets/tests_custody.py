"""Observable tests for the ongoing custody slice (FR-001–003, ALR-001–005)."""
from unittest.mock import patch

from django.contrib.auth.models import User as AuthUser
from django.db import IntegrityError, transaction
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Department, Permission, Role, User
from catalog.models import Brand, Category, Model
from core.models import AuditLog, Notification

from .models import Asset, AssetAssignment, AssetCheckout, AssetConditionLog, AssetTransfer


class AssignCustodyTests(TestCase):
    def setUp(self):
        brand = Brand.objects.create(brand_name="Custody brand")
        self.catalog = dict(
            category=Category.objects.create(category_name="Custody category"),
            brand=brand,
            model=Model.objects.create(model_name="Custody model", brand=brand),
        )
        self.department = Department.objects.create(name="Custody department")
        self.operator = self.profile("operator", {"asset_custody_manage", "asset_view"})
        self.reader = self.profile("reader", {"asset_view"})
        self.employee = self.profile("employee", set(), department=self.department)
        self.other = self.profile("other", set())
        self.client = APIClient()
        self.client.force_authenticate(self.operator.account)
        self.asset = self.make_asset("CUS-001", condition="Good")

    def profile(self, name, codes, department=None, status="Active"):
        account = AuthUser.objects.create_user(username=name, password="test-password")
        role = Role.objects.create(name=f"Custody {name}")
        role.permissions.set([
            Permission.objects.get_or_create(code=code, defaults={"name": code})[0]
            for code in codes
        ])
        return User.objects.create(
            account=account, user_name=name, emp_id=f"CUS-{name}",
            email_id=f"{name}@example.com", role=role, department=department,
            status=status,
        )

    def make_asset(self, name, **kwargs):
        return Asset.objects.create(
            asset_id=name, tag_number=f"{name}-tag", serial_number=f"{name}-serial",
            **self.catalog, **kwargs,
        )

    def assign(self, *, asset=None, user=None, remarks="Everyday device"):
        return self.client.post("/assignment/", {
            "asset": (asset or self.asset).pk,
            "user": (user or self.employee).pk,
            "remarks": remarks,
        }, format="json")

    def take_back(self, assignment, **payload):
        return self.client.post(f"/assignment/{assignment.pk}/take-back/",
                                payload, format="json")

    def assigned_record(self, *, condition="Good"):
        self.asset.condition = condition
        self.asset.save(update_fields=["condition"])
        self.assertEqual(self.assign().status_code, 201)
        return AssetAssignment.objects.get(asset=self.asset, status="Open")

    def test_take_back_requires_explicit_canonical_condition_and_custody_permission(self):
        record = self.assigned_record()
        self.assertEqual(self.take_back(record).status_code, 400)
        self.assertEqual(self.take_back(record, condition="Broken").status_code, 400)
        self.client.force_authenticate(self.reader.account)
        self.assertEqual(self.take_back(record, condition="Good").status_code, 403)
        self.asset.refresh_from_db()
        record.refresh_from_db()
        self.assertEqual((self.asset.status, record.status), ("Assigned", "Open"))
        self.assertFalse(AssetConditionLog.objects.filter(asset=self.asset).exists())

    def test_take_back_inspects_actual_condition_and_clears_custody_even_when_damaged(self):
        record = self.assigned_record()
        with self.captureOnCommitCallbacks(execute=True):
            response = self.take_back(record, condition="Damaged", remarks="Screen cracked")
        self.assertEqual(response.status_code, 200, getattr(response, "data", None))
        self.asset.refresh_from_db()
        record.refresh_from_db()
        self.assertEqual((self.asset.status, self.asset.condition), ("Available", "Damaged"))
        self.assertIsNone(self.asset.custodian_id)
        self.assertIsNone(self.asset.department_id)
        self.assertEqual((record.status, record.closure_reason, record.return_condition,
                          record.return_remarks, record.closed_by_id),
                         ("Closed", "Take Back", "Damaged", "Screen cracked", self.operator.pk))
        self.assertIsNotNone(record.closed_at)
        log = AssetConditionLog.objects.get(asset=self.asset)
        self.assertEqual((log.condition, log.inspector_id), ("Damaged", self.operator.pk))
        self.assertEqual(AuditLog.objects.filter(action="Take Back", module="Assignments").count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.employee).count(), 1)
        self.assertEqual(self.client.get(f"/asset/{self.asset.pk}/").data["custody_type"], "None")

    def test_take_back_requires_deterioration_remarks_but_exempts_new_to_good(self):
        record = self.assigned_record()
        self.assertEqual(self.take_back(record, condition="Average").status_code, 400)
        self.asset.refresh_from_db()
        self.assertEqual((self.asset.status, self.asset.condition), ("Assigned", "Good"))
        self.assertFalse(AssetConditionLog.objects.filter(asset=self.asset).exists())
        self.assertEqual(self.take_back(record, condition="Repair Required",
                                        remarks="  Needs repair  ").status_code, 200)
        self.asset.refresh_from_db()
        self.assertEqual((self.asset.status, self.asset.condition), ("Available", "Repair Required"))

        fresh = self.make_asset("CUS-NEW", condition="New")
        self.assertEqual(self.assign(asset=fresh).status_code, 201)
        new_record = AssetAssignment.objects.get(asset=fresh, status="Open")
        self.assertEqual(self.take_back(new_record, condition="Good").status_code, 200)

    def test_disabled_former_holder_can_be_taken_back_without_notification(self):
        record = self.assigned_record()
        self.employee.status = "Disabled"
        self.employee.save(update_fields=["status"])
        with self.captureOnCommitCallbacks(execute=True):
            response = self.take_back(record, condition="Good")
        self.assertEqual(response.status_code, 200, getattr(response, "data", None))
        self.assertFalse(Notification.objects.filter(user=self.employee).exists())

    def test_pending_transfer_blocks_take_back_without_any_mutation(self):
        record = self.assigned_record()
        transfer = AssetTransfer.objects.create(asset=self.asset, previous_owner=self.employee,
                                                new_owner=self.other, status="Pending")
        response = self.take_back(record, condition="Good")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "Transfer request is not closed.")
        self.asset.refresh_from_db()
        record.refresh_from_db()
        transfer.refresh_from_db()
        self.assertEqual((self.asset.status, self.asset.condition, self.asset.custodian_id),
                         ("Assigned", "Good", self.employee.pk))
        self.assertEqual(self.asset.department_id, self.department.pk)
        self.assertEqual((record.status, transfer.status), ("Open", "Pending"))
        self.assertFalse(AssetConditionLog.objects.filter(asset=self.asset).exists())
        self.assertFalse(AuditLog.objects.filter(action="Take Back").exists())

    def test_stale_or_repeated_take_back_cannot_release_later_custody(self):
        old = self.assigned_record()
        self.assertEqual(self.take_back(old, condition="Good").status_code, 200)
        self.assertEqual(self.assign(user=self.other).status_code, 201)
        self.assertEqual(self.take_back(old, condition="Good").status_code, 400)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.custodian_id, self.other.pk)
        self.assertEqual(AssetAssignment.objects.filter(asset=self.asset, status="Open").count(), 1)

    def test_audit_failure_rolls_back_take_back_and_inspection(self):
        record = self.assigned_record()
        with patch("assets.custody.log_action", side_effect=RuntimeError("audit unavailable")):
            with self.assertRaises(RuntimeError):
                self.take_back(record, condition="Good")
        self.asset.refresh_from_db()
        record.refresh_from_db()
        self.assertEqual((self.asset.status, record.status), ("Assigned", "Open"))
        self.assertFalse(AssetConditionLog.objects.filter(asset=self.asset).exists())
        self.assertFalse(Notification.objects.filter(user=self.employee).exists())

    def test_inspection_failure_rolls_back_take_back_before_audit_or_notification(self):
        record = self.assigned_record()
        with patch("assets.custody.AssetConditionLog.objects.create",
                   side_effect=RuntimeError("inspection unavailable")):
            with self.assertRaises(RuntimeError):
                self.take_back(record, condition="Damaged", remarks="Screen cracked")
        self.asset.refresh_from_db()
        record.refresh_from_db()
        self.assertEqual((self.asset.status, self.asset.condition,
                          self.asset.custodian_id, self.asset.department_id),
                         ("Assigned", "Good", self.employee.pk, self.department.pk))
        self.assertEqual((record.status, record.closed_at, record.return_condition),
                         ("Open", None, ""))
        self.assertFalse(AssetConditionLog.objects.filter(asset=self.asset).exists())
        self.assertFalse(AuditLog.objects.filter(action="Take Back").exists())
        self.assertFalse(Notification.objects.filter(user=self.employee).exists())

    def test_notification_failure_does_not_undo_take_back(self):
        record = self.assigned_record()
        with patch("assets.custody.notify", side_effect=RuntimeError("delivery unavailable")):
            with self.captureOnCommitCallbacks(execute=True):
                response = self.take_back(record, condition="Good")
        self.assertEqual(response.status_code, 200, getattr(response, "data", None))
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, "Available")

    def test_assign_creates_one_ongoing_record_and_matching_asset_without_transfer(self):
        from .models import AssetAssignment

        with self.captureOnCommitCallbacks(execute=True):
            response = self.assign()

        self.assertEqual(response.status_code, 201, getattr(response, "data", None))
        self.asset.refresh_from_db()
        record = AssetAssignment.objects.get(asset=self.asset, status="Open")
        self.assertEqual(record.user_id, self.employee.pk)
        self.assertEqual(record.issue_condition, "Good")
        self.assertEqual(record.issued_by_id, self.operator.pk)
        self.assertEqual(record.remarks, "Everyday device")
        self.assertEqual(self.asset.status, "Assigned")
        self.assertEqual(self.asset.custodian_id, self.employee.pk)
        self.assertEqual(self.asset.department_id, self.department.pk)
        self.assertEqual(response.data["id"], record.pk)
        self.assertEqual(AssetCheckout.objects.filter(asset=self.asset).count(), 0)
        self.assertEqual(AssetTransfer.objects.filter(asset=self.asset).count(), 0)
        self.assertEqual(AuditLog.objects.filter(action="Assign", module="Assignments").count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.employee).count(), 1)
        detail = self.client.get(f"/asset/{self.asset.pk}/")
        self.assertEqual(detail.data["custody_type"], "Ongoing")

    def test_assign_to_employee_without_department_clears_stale_department(self):
        self.asset.department = self.department
        self.asset.save(update_fields=["department"])
        response = self.assign(user=self.other)
        self.assertEqual(response.status_code, 201, getattr(response, "data", None))
        self.asset.refresh_from_db()
        self.assertIsNone(self.asset.department_id)

    def test_duplicate_issue_cannot_create_second_active_arrangement(self):
        from .models import AssetAssignment

        self.assertEqual(self.assign().status_code, 201)
        second = self.assign(user=self.other)
        self.assertEqual(second.status_code, 400)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.custodian_id, self.employee.pk)
        self.assertEqual(AssetAssignment.objects.filter(asset=self.asset, status="Open").count(), 1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AssetAssignment.objects.create(asset=self.asset, user=self.other,
                                               issued_by=self.operator, issue_condition="Good")

    def test_current_custody_uses_record_identity_and_flags_cross_table_conflict(self):
        from .custody import custody_type
        from .models import AssetAssignment

        self.assertEqual(self.assign().status_code, 201)
        active = AssetAssignment.objects.get(asset=self.asset, status="Open")
        self.asset.refresh_from_db()
        self.assertEqual(custody_type(self.asset), "Ongoing")
        detail = self.client.get(f"/assignment/{active.pk}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["id"], active.pk)
        self.assertEqual(detail.data["user"], self.employee.pk)
        self.assertEqual(self.client.patch(f"/assignment/{active.pk}/", {
            "user": self.other.pk}, format="json").status_code, 405)
        self.assertEqual(self.client.delete(f"/assignment/{active.pk}/").status_code, 405)

        # A legacy overlap is disputed even when it names the same employee.
        AssetCheckout.objects.create(asset=self.asset, user=self.employee)
        self.assertEqual(custody_type(self.asset), "Conflicting")
        self.assertEqual(self.client.get(f"/asset/{self.asset.pk}/").data[
            "custody_type"], "Conflicting")

    def test_invalid_status_inactive_target_and_legacy_custody_are_rejected(self):
        inactive = self.profile("inactive", set(), status="Disabled")
        for status in ("In Storage", "Under Repair", "Sold", "Scrapped", "Lost"):
            asset = self.make_asset(f"CUS-{status.replace(' ', '')}", status=status)
            response = self.assign(asset=asset)
            self.assertEqual(response.status_code, 400, getattr(response, "data", None))
            asset.refresh_from_db()
            self.assertIsNone(asset.custodian_id)
        self.assertEqual(self.assign(user=inactive).status_code, 400)
        AssetCheckout.objects.create(asset=self.asset, user=self.employee)
        self.assertEqual(self.assign().status_code, 400)

    def test_permission_denial_preserves_business_state_for_custom_role(self):
        self.client.force_authenticate(self.reader.account)
        response = self.assign()
        self.assertEqual(response.status_code, 403)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, "Available")
        self.assertIsNone(self.asset.custodian_id)

    def test_audit_failure_rolls_back_asset_assignment_and_notification(self):
        from .models import AssetAssignment

        with patch("assets.custody.log_action", side_effect=RuntimeError("audit unavailable")):
            with self.assertRaises(RuntimeError):
                self.assign()
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, "Available")
        self.assertFalse(AssetAssignment.objects.filter(asset=self.asset).exists())
        self.assertFalse(Notification.objects.filter(user=self.employee).exists())

    def test_notification_failure_does_not_undo_committed_custody(self):
        from .models import AssetAssignment

        with patch("assets.custody.notify", side_effect=RuntimeError("delivery unavailable")):
            with self.captureOnCommitCallbacks(execute=True):
                response = self.assign()
        self.assertEqual(response.status_code, 201, getattr(response, "data", None))
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.custodian_id, self.employee.pk)
        self.assertTrue(AssetAssignment.objects.filter(asset=self.asset, status="Open").exists())

    def test_assignment_read_is_scoped_to_parties_for_employee_role(self):
        employee_role = Role.objects.get_or_create(name="Employee")[0]
        employee_role.permissions.add(
            Permission.objects.get_or_create(code="asset_view", defaults={"name": "Asset view"})[0])
        self.employee.role = employee_role
        self.employee.save(update_fields=["role"])
        self.assertEqual(self.assign().status_code, 201)
        other_asset = self.make_asset("CUS-OTHER")
        self.assertEqual(self.assign(asset=other_asset, user=self.other).status_code, 201)
        self.client.force_authenticate(self.employee.account)
        result = self.client.get("/assignment/")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0]["asset"], self.asset.pk)


class LegacyCheckoutMigrationTests(TransactionTestCase):
    def test_populated_open_checkout_stays_open_and_unclassified(self):
        """T004: historical issue facts survive without a fabricated return."""
        brand = Brand.objects.create(brand_name="Migration brand")
        category = Category.objects.create(category_name="Migration category")
        model = Model.objects.create(model_name="Migration model", brand=brand)
        account = AuthUser.objects.create_user("migration-holder", password="test-password")
        holder = User.objects.create(
            account=account, user_name="Migration holder", emp_id="MIG-holder",
            email_id="migration@example.com")
        asset = Asset.objects.create(
            asset_id="MIG-001", tag_number="MIG-tag", serial_number="MIG-serial",
            category=category, brand=brand, model=model,
            status="Assigned", custodian=holder)
        target_old = [('assets', '0012_assetcheckout_closed_as_interrupted_and_more')]
        target_new = [('assets', '0013_asset_assignment')]
        executor = MigrationExecutor(connection)
        executor.migrate(target_old)
        try:
            OldCheckout = executor.loader.project_state(target_old).apps.get_model(
                'assets', 'AssetCheckout')
            checkout = OldCheckout.objects.create(asset_id=asset.pk, user_id=holder.pk,
                                                  checkout_condition="Good")
            original_date = timezone.now().replace(microsecond=0)
            OldCheckout.objects.filter(pk=checkout.pk).update(checkout_date=original_date)
            historical = OldCheckout.objects.create(
                asset_id=asset.pk, user_id=holder.pk, status="Returned",
                checkout_condition="Good", return_condition="Good",
                return_date=original_date)
        finally:
            MigrationExecutor(connection).migrate(target_new)

        from .models import AssetAssignment
        checkout = AssetCheckout.objects.get(pk=checkout.pk)
        asset.refresh_from_db()
        self.assertEqual(checkout.classification, "Unclassified")
        self.assertEqual(checkout.status, "Open")
        self.assertEqual(checkout.checkout_date.replace(microsecond=0), original_date)
        self.assertIsNone(checkout.return_date)
        self.assertIsNone(checkout.closed_at)
        self.assertEqual(asset.custodian_id, holder.pk)
        self.assertEqual(asset.status, "Assigned")
        self.assertFalse(AssetAssignment.objects.filter(asset=asset).exists())
        historical = AssetCheckout.objects.get(pk=historical.pk)
        self.assertEqual(historical.classification, "Unknown")
        self.assertEqual(historical.return_date.replace(microsecond=0), original_date)
        fresh = AssetCheckout.objects.create(asset=asset, user=holder, status="Returned")
        self.assertEqual(fresh.classification, "Temporary")
