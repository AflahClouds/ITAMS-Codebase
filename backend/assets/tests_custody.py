"""Observable tests for ongoing and legacy custody."""
from datetime import date, timedelta
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

    def checkout(self, *, asset=None, user=None):
        return self.client.post("/checkout/", {
            "asset": (asset or self.asset).pk,
            "user": (user or self.employee).pk,
            "purpose": "On-call spare",
            "expected_return_date": "2026-11-01",
        }, format="json")

    def request_ongoing_transfer(self, *, target=None, department=None):
        self.operator.role.permissions.add(Permission.objects.get_or_create(
            code="transfer_request", defaults={"name": "Transfer request"})[0])
        payload = {"asset": self.asset.pk, "new_owner": (target or self.other).pk}
        if department is not None:
            payload["new_department"] = department.pk
        return self.client.post("/transfer/", payload, format="json")

    def test_transfer_request_binds_exact_source_and_pending_or_rejected_leaves_custody(self):
        source = self.assigned_record()
        requested = self.request_ongoing_transfer()
        self.assertEqual(requested.status_code, 201, getattr(requested, "data", None))
        transfer = AssetTransfer.objects.get(pk=requested.data["id"])
        self.assertEqual(transfer.source_assignment_id, source.pk)
        self.asset.refresh_from_db()
        source.refresh_from_db()
        self.assertEqual((self.asset.custodian_id, source.status, transfer.status),
                         (self.employee.pk, "Open", "Pending"))
        rejected = self.client.post(f"/transfer/{transfer.pk}/reject/", {}, format="json")
        self.assertEqual(rejected.status_code, 200, getattr(rejected, "data", None))
        self.asset.refresh_from_db()
        source.refresh_from_db()
        self.assertEqual((self.asset.custodian_id, source.status), (self.employee.pk, "Open"))
        self.assertFalse(AssetAssignment.objects.filter(source_transfer=transfer).exists())

    def test_transfer_approval_atomically_ends_source_and_opens_target(self):
        source = self.assigned_record()
        target_department = Department.objects.create(name="Target department")
        requested = self.request_ongoing_transfer(department=target_department)
        self.assertEqual(requested.status_code, 201, getattr(requested, "data", None))
        transfer = AssetTransfer.objects.get(pk=requested.data["id"])
        with self.captureOnCommitCallbacks(execute=True):
            approved = self.client.post(f"/transfer/{transfer.pk}/approve/", {}, format="json")
        self.assertEqual(approved.status_code, 200, getattr(approved, "data", None))
        source.refresh_from_db()
        target = AssetAssignment.objects.get(source_transfer=transfer)
        self.asset.refresh_from_db()
        self.assertEqual((source.status, source.closure_reason, source.closed_by_id,
                          source.superseded_by_transfer_id),
                         ("Closed", "Transfer", self.operator.pk, transfer.pk))
        self.assertIsNotNone(source.closed_at)
        self.assertEqual((target.status, target.user_id, target.issued_by_id,
                          target.issue_condition),
                         ("Open", self.other.pk, self.operator.pk, self.asset.condition))
        self.assertEqual((self.asset.status, self.asset.custodian_id,
                          self.asset.department_id),
                         ("Assigned", self.other.pk, target_department.pk))
        self.assertEqual(AuditLog.objects.filter(action="Transfer Approved").count(), 1)
        self.assertEqual(self.client.get(f"/asset/{self.asset.pk}/").data["custody_type"], "Ongoing")
        repeated = self.client.post(f"/transfer/{transfer.pk}/approve/", {}, format="json")
        self.assertEqual(repeated.status_code, 400)
        self.assertEqual(AssetAssignment.objects.filter(source_transfer=transfer).count(), 1)

    def test_transfer_rejects_later_same_employee_arrangement_and_department_change(self):
        source = self.assigned_record()
        requested = self.request_ongoing_transfer()
        self.assertEqual(requested.status_code, 201)
        transfer = AssetTransfer.objects.get(pk=requested.data["id"])
        source.status = "Closed"
        source.save(update_fields=["status"])
        later = AssetAssignment.objects.create(asset=self.asset, user=self.employee,
                                               issued_by=self.operator, issue_condition="Good")
        stale = self.client.post(f"/transfer/{transfer.pk}/approve/", {}, format="json")
        self.assertEqual(stale.status_code, 400)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.custodian_id, self.employee.pk)
        self.assertEqual(AssetAssignment.objects.get(pk=later.pk).status, "Open")
        transfer.refresh_from_db()
        self.assertEqual(transfer.status, "Pending")
        later.status = "Closed"
        later.save(update_fields=["status"])
        source.status = "Open"
        source.save(update_fields=["status"])
        changed_department = Department.objects.create(name="Changed department")
        self.asset.department = changed_department
        self.asset.save(update_fields=["department"])
        self.assertEqual(self.client.post(f"/transfer/{transfer.pk}/approve/", {},
                                          format="json").status_code, 400)
        self.assertFalse(AssetAssignment.objects.filter(source_transfer=transfer).exists())

    def test_transfer_rejects_unclassified_conflicting_and_inactive_target(self):
        self.assigned_record()
        AssetCheckout.objects.create(asset=self.asset, user=self.employee,
                                     classification="Unclassified")
        self.assertEqual(self.request_ongoing_transfer().status_code, 400)
        self.assertFalse(AssetTransfer.objects.filter(asset=self.asset).exists())
        AssetCheckout.objects.filter(asset=self.asset).delete()
        self.other.status = "Disabled"
        self.other.save(update_fields=["status"])
        self.assertEqual(self.request_ongoing_transfer().status_code, 400)
        self.assertFalse(AssetTransfer.objects.filter(asset=self.asset).exists())

    def test_transfer_approval_audit_failure_rolls_back_all_custody(self):
        source = self.assigned_record()
        requested = self.request_ongoing_transfer()
        self.assertEqual(requested.status_code, 201)
        transfer = AssetTransfer.objects.get(pk=requested.data["id"])
        with patch("assets.transfer.log_action", side_effect=RuntimeError("audit unavailable")):
            with self.assertRaises(RuntimeError):
                self.client.post(f"/transfer/{transfer.pk}/approve/", {}, format="json")
        self.asset.refresh_from_db()
        source.refresh_from_db()
        transfer.refresh_from_db()
        self.assertEqual((self.asset.custodian_id, source.status, transfer.status),
                         (self.employee.pk, "Open", "Pending"))
        self.assertFalse(AssetAssignment.objects.filter(source_transfer=transfer).exists())

    def test_transfer_permission_denials_and_same_holder_do_not_create_requests(self):
        source = self.assigned_record()
        self.client.force_authenticate(self.reader.account)
        denied = self.client.post("/transfer/", {
            "asset": self.asset.pk, "new_owner": self.other.pk,
        }, format="json")
        self.assertEqual(denied.status_code, 403)
        self.client.force_authenticate(self.operator.account)
        self.assertEqual(self.request_ongoing_transfer(target=self.employee).status_code, 400)
        self.assertFalse(AssetTransfer.objects.filter(asset=self.asset).exists())
        self.assertEqual(source.status, "Open")
        requested = self.request_ongoing_transfer()
        self.assertEqual(requested.status_code, 201)
        self.client.force_authenticate(self.reader.account)
        self.assertEqual(self.client.post(f"/transfer/{requested.data['id']}/approve/",
                                          {}, format="json").status_code, 403)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.custodian_id, self.employee.pk)
        self.assertEqual(AssetTransfer.objects.get(pk=requested.data["id"]).status, "Pending")

    def test_transfer_duplicate_pending_and_disabled_target_at_approval_are_safe(self):
        source = self.assigned_record()
        requested = self.request_ongoing_transfer()
        self.assertEqual(requested.status_code, 201)
        self.assertEqual(self.request_ongoing_transfer().status_code, 400)
        self.other.status = "Disabled"
        self.other.save(update_fields=["status"])
        rejected = self.client.post(f"/transfer/{requested.data['id']}/approve/",
                                    {}, format="json")
        self.assertEqual(rejected.status_code, 400)
        self.asset.refresh_from_db()
        source.refresh_from_db()
        self.assertEqual((self.asset.custodian_id, source.status),
                         (self.employee.pk, "Open"))
        self.assertEqual(AssetTransfer.objects.get(pk=requested.data["id"]).status, "Pending")

    def test_transfer_request_audit_failure_does_not_leave_pending_record(self):
        self.assigned_record()
        with patch("assets.transfer.log_action", side_effect=RuntimeError("audit unavailable")):
            with self.assertRaises(RuntimeError):
                self.request_ongoing_transfer()
        self.assertFalse(AssetTransfer.objects.filter(asset=self.asset).exists())
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.custodian_id, self.employee.pk)

    def test_transfer_notification_failure_after_commit_preserves_handoff(self):
        self.assigned_record()
        requested = self.request_ongoing_transfer()
        self.assertEqual(requested.status_code, 201)
        transfer = AssetTransfer.objects.get(pk=requested.data["id"])
        with patch("assets.transfer.notify", side_effect=RuntimeError("delivery unavailable")):
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(f"/transfer/{transfer.pk}/approve/",
                                            {}, format="json")
        self.assertEqual(response.status_code, 200, getattr(response, "data", None))
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.custodian_id, self.other.pk)
        self.assertTrue(AssetAssignment.objects.filter(source_transfer=transfer,
                                                       status="Open").exists())

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

    def test_new_checkout_is_temporary_and_checkin_is_physical_return(self):
        response = self.checkout()
        self.assertEqual(response.status_code, 201, getattr(response, "data", None))
        self.asset.refresh_from_db()
        record = AssetCheckout.objects.get(pk=response.data["id"])
        self.assertEqual((record.classification, record.purpose,
                          str(record.expected_return_date)),
                         ("Temporary", "On-call spare", "2026-11-01"))
        self.assertEqual((self.asset.status, self.asset.custodian_id,
                          self.asset.department_id),
                         ("Assigned", self.employee.pk, self.department.pk))
        self.assertFalse(AssetAssignment.objects.filter(asset=self.asset).exists())
        self.assertEqual(self.client.get(f"/asset/{self.asset.pk}/").data[
            "custody_type"], "Temporary")

        self.assertEqual(self.client.post(f"/checkout/{record.pk}/checkin/", {
            "condition": "Damaged"}, format="json").status_code, 400)
        result = self.client.post(f"/checkout/{record.pk}/checkin/", {
            "condition": "Damaged", "remarks": "Screen cracked"}, format="json")
        self.assertEqual(result.status_code, 200, getattr(result, "data", None))
        self.asset.refresh_from_db()
        record.refresh_from_db()
        self.assertEqual((record.status, record.closure_reason,
                          record.return_condition, record.return_remarks),
                         ("Returned", "Returned", "Damaged", "Screen cracked"))
        self.assertIsNotNone(record.return_date)
        self.assertEqual((self.asset.status, self.asset.condition,
                          self.asset.custodian_id, self.asset.department_id),
                         ("Available", "Damaged", None, None))
        self.assertEqual(AssetConditionLog.objects.filter(asset=self.asset,
                                                         inspector=self.operator).count(), 1)
        self.assertFalse(AuditLog.objects.filter(action="Take Back").exists())

    def test_confirmed_temporary_holder_blocks_assign_to_another_employee(self):
        self.assertEqual(self.checkout().status_code, 201)
        rejected_assign = self.assign(user=self.other)
        self.assertEqual(rejected_assign.status_code, 400)
        self.assertIn("temporarily held by another employee",
                      rejected_assign.data["detail"])
        self.asset.refresh_from_db()
        self.assertEqual((self.asset.status, self.asset.custodian_id,
                          self.asset.department_id),
                         ("Assigned", self.employee.pk, self.department.pk))
        self.assertEqual(AssetCheckout.objects.filter(asset=self.asset,
                                                      status="Open").count(), 1)
        self.assertFalse(AssetAssignment.objects.filter(asset=self.asset).exists())

    def test_confirmed_temporary_holder_blocks_transfer_without_pending_request(self):
        self.assertEqual(self.checkout().status_code, 201)
        requester = self.profile("requester", {"transfer_request"})
        self.client.force_authenticate(requester.account)
        rejected_transfer = self.client.post("/transfer/", {
            "asset": self.asset.pk, "new_owner": self.other.pk,
        }, format="json")
        self.assertEqual(rejected_transfer.status_code, 400)
        self.assertIn("temporarily held by another employee",
                      rejected_transfer.data["detail"])
        self.asset.refresh_from_db()
        self.assertEqual((self.asset.status, self.asset.custodian_id,
                          self.asset.department_id),
                         ("Assigned", self.employee.pk, self.department.pk))
        self.assertEqual(AssetCheckout.objects.filter(asset=self.asset,
                                                      status="Open").count(), 1)
        self.assertFalse(AssetAssignment.objects.filter(asset=self.asset).exists())
        self.assertFalse(AssetTransfer.objects.filter(asset=self.asset).exists())

    def test_pending_transfer_cannot_be_approved_after_asset_enters_temporary_custody(self):
        pending = AssetTransfer.objects.create(
            asset=self.asset, previous_owner=self.employee,
            new_owner=self.other, status="Pending")
        self.assertEqual(self.checkout().status_code, 201)
        result = self.client.post(f"/transfer/{pending.pk}/approve/", {}, format="json")
        self.assertEqual(result.status_code, 400)
        pending.refresh_from_db()
        self.asset.refresh_from_db()
        self.assertEqual(pending.status, "Pending")
        self.assertEqual(self.asset.custodian_id, self.employee.pk)
        self.assertTrue(AssetCheckout.objects.filter(asset=self.asset,
                                                     user=self.employee,
                                                     status="Open").exists())

    def test_checkout_notification_failure_does_not_undo_committed_temporary_custody(self):
        with patch("assets.checkout.notify", side_effect=RuntimeError("delivery unavailable")):
            with self.captureOnCommitCallbacks(execute=True):
                response = self.checkout()
        self.assertEqual(response.status_code, 201, getattr(response, "data", None))
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.custodian_id, self.employee.pk)
        self.assertTrue(AssetCheckout.objects.filter(asset=self.asset,
                                                     status="Open").exists())

    def test_stale_temporary_checkin_does_not_release_later_custody(self):
        response = self.checkout()
        self.assertEqual(response.status_code, 201)
        record = AssetCheckout.objects.get(pk=response.data["id"])
        Asset.objects.filter(pk=self.asset.pk).update(custodian=self.other,
                                                       department=None)
        AssetAssignment.objects.create(asset=self.asset, user=self.other,
                                       issued_by=self.operator,
                                       issue_condition="Good")
        result = self.client.post(f"/checkout/{record.pk}/checkin/", {
            "condition": "Good"}, format="json")
        self.assertEqual(result.status_code, 400)
        self.asset.refresh_from_db()
        record.refresh_from_db()
        self.assertEqual((self.asset.status, self.asset.custodian_id,
                          record.status, record.return_date),
                         ("Assigned", self.other.pk, "Open", None))
        self.assertFalse(AssetConditionLog.objects.filter(asset=self.asset).exists())

    def test_checkout_rejects_conflicting_active_assignment_even_if_snapshot_says_available(self):
        AssetAssignment.objects.create(asset=self.asset, user=self.employee,
                                       issued_by=self.operator,
                                       issue_condition="Good")
        result = self.checkout(user=self.other)
        self.assertEqual(result.status_code, 400)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, "Available")
        self.assertIsNone(self.asset.custodian_id)
        self.assertFalse(AssetCheckout.objects.filter(asset=self.asset).exists())

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


class LegacyClassificationTests(TestCase):
    def setUp(self):
        brand = Brand.objects.create(brand_name="Legacy classification brand")
        category = Category.objects.create(category_name="Legacy classification category")
        model = Model.objects.create(model_name="Legacy classification model", brand=brand)
        self.department = Department.objects.create(name="Legacy classification department")
        self.operator = self.profile("classify-operator", {"asset_custody_manage", "asset_view"})
        self.reader = self.profile("classify-reader", {"asset_view"})
        self.issuer = self.profile("classify-issuer", set())
        self.holder = self.profile("classify-holder", set(), department=self.department)
        self.other = self.profile("classify-other", {"asset_view"})
        self.asset = Asset.objects.create(
            asset_id="LEG-CLASS-001", tag_number="LEG-CLASS-tag",
            serial_number="LEG-CLASS-serial", brand=brand, category=category,
            model=model, status="Assigned", custodian=self.holder,
            department=self.department, condition="Average")
        self.checkout = AssetCheckout.objects.create(
            asset=self.asset, user=self.holder, approved_by=self.issuer,
            classification="Unclassified", checkout_condition="Good",
            expected_return_date=date(2026, 11, 1), purpose="Everyday laptop",
            remarks="Original issue notes")
        self.original_issue = timezone.now().replace(microsecond=0) - timedelta(days=45)
        AssetCheckout.objects.filter(pk=self.checkout.pk).update(
            checkout_date=self.original_issue)
        self.checkout.refresh_from_db()
        self.client = APIClient()
        self.client.force_authenticate(self.operator.account)

    def profile(self, name, codes, department=None):
        account = AuthUser.objects.create_user(username=name, password="test-password")
        role = Role.objects.create(name=f"Legacy {name}")
        role.permissions.set([
            Permission.objects.get_or_create(code=code, defaults={"name": code})[0]
            for code in codes
        ])
        return User.objects.create(
            account=account, user_name=name, emp_id=f"LEG-{name}",
            email_id=f"{name}@example.com", role=role, department=department)

    def classify(self, custody_type="Temporary", remarks="Verified actual use"):
        return self.client.post(f"/checkout/{self.checkout.pk}/classify/", {
            "custody_type": custody_type, "remarks": remarks,
        }, format="json")

    def test_matching_legacy_temporary_classification_preserves_issue_and_is_idempotent(self):
        self.assertEqual(self.client.get("/checkout/").data[0]["current_custody_type"],
                         "Unclassified")
        response = self.classify("Temporary")
        self.assertEqual(response.status_code, 200, getattr(response, "data", None))
        self.checkout.refresh_from_db()
        self.asset.refresh_from_db()
        self.assertEqual((self.checkout.status, self.checkout.classification,
                          self.checkout.classified_by_id,
                          self.checkout.classification_remarks),
                         ("Open", "Temporary", self.operator.pk, "Verified actual use"))
        self.assertIsNotNone(self.checkout.classified_at)
        self.assertEqual(self.checkout.checkout_date.replace(microsecond=0), self.original_issue)
        self.assertEqual(self.checkout.expected_return_date, date(2026, 11, 1))
        self.assertEqual((self.checkout.approved_by_id, self.checkout.checkout_condition,
                          self.checkout.purpose, self.checkout.remarks),
                         (self.issuer.pk, "Good", "Everyday laptop", "Original issue notes"))
        self.assertIsNone(self.checkout.return_date)
        self.assertEqual(self.checkout.return_condition, "")
        self.assertEqual((self.asset.status, self.asset.custodian_id,
                          self.asset.department_id, self.asset.condition),
                         ("Assigned", self.holder.pk, self.department.pk, "Average"))
        self.assertEqual(self.client.get(f"/asset/{self.asset.pk}/").data["custody_type"],
                         "Temporary")
        self.assertEqual(self.client.get("/checkout/").data[0]["current_custody_type"],
                         "Temporary")
        self.assertFalse(AssetAssignment.objects.filter(asset=self.asset).exists())
        self.assertFalse(AssetConditionLog.objects.filter(asset=self.asset).exists())
        first_classified_at = self.checkout.classified_at
        self.assertEqual(self.classify("Temporary").status_code, 200)
        self.checkout.refresh_from_db()
        self.assertEqual(self.checkout.classified_at, first_classified_at)
        self.assertEqual(AuditLog.objects.filter(action="Classify Checkout").count(), 1)

    def test_matching_legacy_ongoing_classification_preserves_original_issue_facts(self):
        response = self.classify("Ongoing")
        self.assertEqual(response.status_code, 200, getattr(response, "data", None))
        self.checkout.refresh_from_db()
        self.asset.refresh_from_db()
        assignment = AssetAssignment.objects.get(source_checkout=self.checkout)
        self.assertEqual((self.checkout.status, self.checkout.classification,
                          self.checkout.closure_reason, self.checkout.classified_by_id,
                          self.checkout.classification_remarks),
                         ("Returned", "Ongoing", "Reclassified", self.operator.pk,
                          "Verified actual use"))
        self.assertIsNotNone(self.checkout.closed_at)
        self.assertIsNotNone(self.checkout.classified_at)
        self.assertEqual(self.checkout.checkout_date.replace(microsecond=0), self.original_issue)
        self.assertEqual(self.checkout.expected_return_date, date(2026, 11, 1))
        self.assertIsNone(self.checkout.return_date)
        self.assertEqual((self.checkout.return_condition, self.checkout.return_remarks),
                         ("", ""))
        self.assertEqual((assignment.status, assignment.user_id, assignment.issued_by_id,
                          assignment.issue_condition, assignment.remarks),
                         ("Open", self.holder.pk, self.issuer.pk, "Good",
                          "Original issue notes"))
        self.assertEqual(assignment.issued_at.replace(microsecond=0), self.original_issue)
        self.assertTrue(assignment.provenance)
        self.assertTrue(assignment.date_basis)
        self.assertEqual((self.asset.status, self.asset.custodian_id,
                          self.asset.department_id, self.asset.condition),
                         ("Assigned", self.holder.pk, self.department.pk, "Average"))
        self.assertEqual(self.client.get(f"/asset/{self.asset.pk}/").data["custody_type"],
                         "Ongoing")
        self.assertFalse(AssetConditionLog.objects.filter(asset=self.asset).exists())
        self.assertEqual(self.classify("Ongoing").status_code, 200)
        self.assertEqual(AssetAssignment.objects.filter(source_checkout=self.checkout).count(), 1)
        self.assertEqual(self.classify("Temporary").status_code, 400)
        self.assertEqual(AuditLog.objects.filter(action="Classify Checkout").count(), 1)

    def test_unknown_original_issue_condition_is_not_inferred_from_current_asset(self):
        self.checkout.checkout_condition = ""
        self.checkout.save(update_fields=["checkout_condition"])
        self.assertEqual(self.classify("Ongoing").status_code, 200)
        assignment = AssetAssignment.objects.get(source_checkout=self.checkout)
        self.assertEqual(assignment.issue_condition, "")
        self.assertEqual(self.asset.condition, "Average")

    def test_mismatch_permission_and_conflict_cannot_classify_or_guess_temporary(self):
        self.client.force_authenticate(self.reader.account)
        self.assertEqual(self.classify("Temporary").status_code, 403)
        self.client.force_authenticate(self.operator.account)
        self.asset.custodian = self.other
        self.asset.save(update_fields=["custodian"])
        conflict = self.classify("Temporary")
        self.assertEqual(conflict.status_code, 400)
        self.assertIn("conflict", conflict.data["detail"].lower())
        self.assertNotIn("temporarily held", conflict.data["detail"].lower())
        self.checkout.refresh_from_db()
        self.asset.refresh_from_db()
        self.assertEqual(self.checkout.classification, "Unclassified")
        self.assertIsNone(self.checkout.classified_at)
        self.assertEqual(self.asset.custodian_id, self.other.pk)
        self.assertEqual(self.client.get("/checkout/").data[0]["current_custody_type"],
                         "Conflicting")
        self.assertFalse(AssetAssignment.objects.filter(asset=self.asset).exists())
        self.assertFalse(AuditLog.objects.filter(action="Classify Checkout").exists())

    def test_unclassified_cannot_checkin_or_enter_transfer_and_audit_failure_rolls_back(self):
        self.assertEqual(self.client.post(f"/checkout/{self.checkout.pk}/checkin/", {
            "condition": "Good"}, format="json").status_code, 400)
        requester = self.profile("classify-requester", {"transfer_request"})
        self.client.force_authenticate(requester.account)
        attempted = self.client.post("/transfer/", {
            "asset": self.asset.pk, "new_owner": self.other.pk,
        }, format="json")
        self.assertEqual(attempted.status_code, 400)
        self.assertIn("Classify", attempted.data["detail"])
        self.assertFalse(AssetTransfer.objects.filter(asset=self.asset).exists())
        self.client.force_authenticate(self.operator.account)
        with patch("assets.custody.log_action", side_effect=RuntimeError("audit unavailable")):
            with self.assertRaises(RuntimeError):
                self.classify("Ongoing")
        self.checkout.refresh_from_db()
        self.assertEqual((self.checkout.status, self.checkout.classification),
                         ("Open", "Unclassified"))
        self.assertFalse(AssetAssignment.objects.filter(asset=self.asset).exists())


class LegacyReconciliationTests(TestCase):
    def setUp(self):
        brand = Brand.objects.create(brand_name="Reconciliation brand")
        category = Category.objects.create(category_name="Reconciliation category")
        model = Model.objects.create(model_name="Reconciliation model", brand=brand)
        self.department_a = Department.objects.create(name="Reconciliation A")
        self.department_middle = Department.objects.create(name="Reconciliation middle")
        self.department_b = Department.objects.create(name="Reconciliation B")
        self.operator = self.profile("reconcile-operator", {"asset_custody_manage", "asset_view"})
        self.reader = self.profile("reconcile-reader", {"asset_view"})
        self.a = self.profile("reconcile-a", set(), self.department_a)
        self.middle = self.profile("reconcile-middle", set(), self.department_middle)
        self.b = self.profile("reconcile-b", set(), self.department_b)
        self.asset = Asset.objects.create(
            asset_id="LEG-RECON-001", tag_number="LEG-RECON-tag",
            serial_number="LEG-RECON-serial", brand=brand, category=category,
            model=model, status="Assigned", condition="Average",
            custodian=self.b, department=self.department_b)
        self.checkout = AssetCheckout.objects.create(
            asset=self.asset, user=self.a, approved_by=self.operator,
            classification="Unclassified", checkout_condition="Good",
            expected_return_date=date(2026, 12, 1), purpose="Original loan",
            remarks="Original issue notes")
        self.original_issue = timezone.now().replace(microsecond=0) - timedelta(days=90)
        AssetCheckout.objects.filter(pk=self.checkout.pk).update(
            checkout_date=self.original_issue)
        self.checkout.refresh_from_db()
        self.client = APIClient()
        self.client.force_authenticate(self.operator.account)

    def profile(self, name, codes, department=None):
        account = AuthUser.objects.create_user(username=name, password="test-password")
        role = Role.objects.create(name=f"Legacy {name}")
        role.permissions.set([
            Permission.objects.get_or_create(code=code, defaults={"name": code})[0]
            for code in codes
        ])
        return User.objects.create(
            account=account, user_name=name, emp_id=f"LEG-{name}",
            email_id=f"{name}@example.com", role=role, department=department)

    def approved_handoff(self, source, target, request_date):
        transfer = AssetTransfer.objects.create(
            asset=self.asset, previous_owner=source, new_owner=target,
            previous_department=source.department,
            new_department=target.department, status="Approved",
            requested_by=self.operator, approved_by=self.operator,
            condition="Average")
        AssetTransfer.objects.filter(pk=transfer.pk).update(transfer_date=request_date)
        transfer.refresh_from_db()
        return transfer

    def reconcile(self, transfer, custody_choice="Ongoing"):
        return self.client.post(f"/checkout/{self.checkout.pk}/reconcile/", {
            "approved_transfer": transfer.pk, "custody_type": custody_choice,
            "remarks": "Verified historical handoff",
        }, format="json")

    def test_verified_chain_reconstructs_one_ongoing_arrangement_without_return(self):
        first_date = self.original_issue + timedelta(days=30)
        final_date = self.original_issue + timedelta(days=60)
        self.approved_handoff(self.a, self.middle, first_date)
        final = self.approved_handoff(self.middle, self.b, final_date)
        original_snapshot = (self.asset.status, self.asset.custodian_id,
                             self.asset.department_id, self.asset.condition)

        response = self.reconcile(final)
        self.assertEqual(response.status_code, 200, getattr(response, "data", None))
        self.checkout.refresh_from_db()
        self.asset.refresh_from_db()
        assignment = AssetAssignment.objects.get(asset=self.asset, status="Open")
        self.assertEqual((self.checkout.status, self.checkout.closure_reason,
                          self.checkout.superseded_by_transfer_id,
                          self.checkout.classified_by_id),
                         ("Returned", "Superseded", final.pk, self.operator.pk))
        self.assertIsNotNone(self.checkout.closed_at)
        self.assertIsNotNone(self.checkout.classified_at)
        self.assertEqual(self.checkout.checkout_date.replace(microsecond=0),
                         self.original_issue)
        self.assertEqual(self.checkout.expected_return_date, date(2026, 12, 1))
        self.assertIsNone(self.checkout.return_date)
        self.assertEqual((self.checkout.return_condition, self.checkout.return_remarks),
                         ("", ""))
        self.assertEqual((assignment.user_id, assignment.source_checkout_id,
                          assignment.source_transfer_id),
                         (self.b.pk, self.checkout.pk, final.pk))
        self.assertEqual(assignment.issue_condition, "")
        self.assertEqual(assignment.issued_at.replace(microsecond=0), final_date)
        self.assertEqual(assignment.provenance, "Administrative reconstruction")
        self.assertEqual(assignment.date_basis,
                         "Legacy Transfer event date (event type unverified)")
        self.assertEqual((self.asset.status, self.asset.custodian_id,
                          self.asset.department_id, self.asset.condition), original_snapshot)
        self.assertFalse(AssetConditionLog.objects.filter(asset=self.asset).exists())
        self.assertEqual(AuditLog.objects.filter(action="Reconcile Checkout").count(), 1)
        self.assertIn("Superseded", self.client.get(
            f"/asset/{self.asset.pk}/history/").data["checkouts"][0]["closure_reason"])
        self.assertEqual(self.reconcile(final).status_code, 200)
        self.assertEqual(AssetAssignment.objects.filter(asset=self.asset).count(), 1)

    def test_verified_handoff_reconstructs_temporary_without_purpose_or_due_date(self):
        request_date = self.original_issue + timedelta(days=40)
        final = self.approved_handoff(self.a, self.b, request_date)
        response = self.reconcile(final, "Temporary")
        self.assertEqual(response.status_code, 200, getattr(response, "data", None))
        self.checkout.refresh_from_db()
        active = AssetCheckout.objects.get(asset=self.asset, status="Open")
        self.assertEqual((active.user_id, active.classification,
                          active.source_checkout_id, active.source_transfer_id),
                         (self.b.pk, "Temporary", self.checkout.pk, final.pk))
        self.assertEqual(active.checkout_date.replace(microsecond=0), request_date)
        self.assertEqual((active.purpose, active.expected_return_date,
                          active.checkout_condition, active.return_date),
                         ("", None, "", None))
        self.assertEqual(active.provenance, "Administrative reconstruction")
        self.assertEqual(active.date_basis,
                         "Legacy Transfer event date (event type unverified)")
        self.assertFalse(AssetAssignment.objects.filter(asset=self.asset).exists())
        self.assertEqual(self.client.get(f"/asset/{self.asset.pk}/").data["custody_type"],
                         "Temporary")
        self.assertEqual(self.reconcile(final, "Temporary").status_code, 200)
        self.assertEqual(AssetCheckout.objects.filter(asset=self.asset, status="Open").count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="Reconcile Checkout").count(), 1)

    def test_existing_matching_ongoing_record_is_linked_without_duplicate(self):
        self.approved_handoff(
            self.a, self.middle, self.original_issue + timedelta(days=20))
        final = self.approved_handoff(
            self.middle, self.b, self.original_issue + timedelta(days=40))
        existing = AssetAssignment.objects.create(
            asset=self.asset, user=self.b, issue_condition="Average",
            issued_by=self.operator, source_transfer=final)
        response = self.reconcile(final)
        self.assertEqual(response.status_code, 200, getattr(response, "data", None))
        existing.refresh_from_db()
        self.assertEqual(existing.source_checkout_id, self.checkout.pk)
        self.assertEqual(AssetAssignment.objects.filter(asset=self.asset).count(), 1)
        self.assertEqual(existing.provenance, "")
        self.assertEqual(self.reconcile(final).status_code, 200)
        self.assertEqual(AuditLog.objects.filter(action="Reconcile Checkout").count(), 1)

    def test_broken_approved_chain_or_department_cannot_supersede_checkout(self):
        self.approved_handoff(
            self.a, self.middle, self.original_issue + timedelta(days=20))
        final = self.approved_handoff(
            self.a, self.b, self.original_issue + timedelta(days=40))
        existing = AssetAssignment.objects.create(
            asset=self.asset, user=self.b, issue_condition="Average",
            issued_by=self.operator, source_transfer=final)
        self.assertEqual(self.reconcile(final).status_code, 400)
        final.previous_owner = self.middle
        final.new_department = self.department_middle
        final.save(update_fields=["previous_owner", "new_department"])
        self.assertEqual(self.reconcile(final).status_code, 400)
        self.checkout.refresh_from_db()
        existing.refresh_from_db()
        self.assertEqual(self.checkout.status, "Open")
        self.assertIsNone(existing.source_checkout_id)
        self.assertFalse(AuditLog.objects.filter(action="Reconcile Checkout").exists())

    def test_unapproved_wrong_chain_and_unauthorized_reconciliation_do_not_mutate(self):
        final = self.approved_handoff(
            self.a, self.b, self.original_issue + timedelta(days=40))
        self.client.force_authenticate(self.reader.account)
        self.assertEqual(self.reconcile(final).status_code, 403)
        self.client.force_authenticate(self.operator.account)
        final.status = "Pending"
        final.save(update_fields=["status"])
        self.assertEqual(self.reconcile(final).status_code, 400)
        final.status = "Approved"
        final.previous_owner = self.middle
        final.save(update_fields=["status", "previous_owner"])
        self.assertEqual(self.reconcile(final).status_code, 400)
        self.checkout.refresh_from_db()
        self.assertEqual((self.checkout.status, self.checkout.classification),
                         ("Open", "Unclassified"))
        self.assertFalse(AssetAssignment.objects.filter(asset=self.asset).exists())
        self.assertFalse(AuditLog.objects.filter(action="Reconcile Checkout").exists())

    def test_reconciliation_audit_failure_rolls_back_all_custody_writes(self):
        final = self.approved_handoff(
            self.a, self.b, self.original_issue + timedelta(days=40))
        existing = AssetAssignment.objects.create(
            asset=self.asset, user=self.b, issue_condition="Average",
            issued_by=self.operator, source_transfer=final)
        with patch("assets.custody.log_action", side_effect=RuntimeError("audit unavailable")):
            with self.assertRaises(RuntimeError):
                self.reconcile(final)
        self.checkout.refresh_from_db()
        self.assertEqual(self.checkout.status, "Open")
        existing.refresh_from_db()
        self.assertIsNone(existing.source_checkout_id)
        self.assertEqual(AssetAssignment.objects.filter(asset=self.asset).count(), 1)
        self.assertFalse(AssetConditionLog.objects.filter(asset=self.asset).exists())
        self.asset.refresh_from_db()
        self.assertEqual((self.asset.status, self.asset.custodian_id,
                          self.asset.department_id),
                         ("Assigned", self.b.pk, self.department_b.pk))

    def test_reconstruction_audit_failure_rolls_back_new_arrangement(self):
        final = self.approved_handoff(
            self.a, self.b, self.original_issue + timedelta(days=40))
        with patch("assets.custody.log_action", side_effect=RuntimeError("audit unavailable")):
            with self.assertRaises(RuntimeError):
                self.reconcile(final, "Temporary")
        self.checkout.refresh_from_db()
        self.assertEqual(self.checkout.status, "Open")
        self.assertEqual(AssetCheckout.objects.filter(asset=self.asset).count(), 1)
        self.assertFalse(AssetAssignment.objects.filter(asset=self.asset).exists())


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
        target_latest = [('assets', '0016_assetcheckout_reconciliation_provenance')]
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
            executor = MigrationExecutor(connection)
            executor.migrate(target_new)
            NewCheckout = executor.loader.project_state(target_new).apps.get_model(
                'assets', 'AssetCheckout')
            checkout = NewCheckout.objects.get(pk=checkout.pk)
            asset.refresh_from_db()
            self.assertEqual(checkout.classification, "Unclassified")
            self.assertEqual(checkout.status, "Open")
            self.assertEqual(checkout.checkout_date.replace(microsecond=0), original_date)
            self.assertIsNone(checkout.return_date)
            self.assertIsNone(checkout.closed_at)
            self.assertEqual(asset.custodian_id, holder.pk)
            self.assertEqual(asset.status, "Assigned")
            self.assertFalse(AssetAssignment.objects.filter(asset=asset).exists())
            historical = NewCheckout.objects.get(pk=historical.pk)
            self.assertEqual(historical.classification, "Unknown")
            self.assertEqual(historical.return_date.replace(microsecond=0), original_date)
            fresh = NewCheckout.objects.create(asset_id=asset.pk, user_id=holder.pk,
                                               status="Returned")
            self.assertEqual(fresh.classification, "Temporary")
        finally:
            MigrationExecutor(connection).migrate(target_latest)
