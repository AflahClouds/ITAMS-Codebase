"""Conformance tests for register rows closed in the B3 and B5 baselines.

B3 (Checkout/Check-in) and B5 (Service Record) recorded their gaps in numbered
registers but never made them executable, so nothing reported when one was closed or
silently reopened. These cover the rows that are baseline delivery obligations.

Each test carries a `Covers:` tag naming the requirements it demonstrates; those tags
feed docs/conformance/traceability-map.md.
"""
from django.contrib.auth.models import User as AuthUser
from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import Department, Permission, Role, User
from catalog.models import Brand, Category, Model, Vendor

from .checkout import check_in, check_out, close_all_open_checkouts
from .models import (Asset, AssetCheckout, LifecycleError, ServiceRecord)
from .service import close_service, open_service


def _profile(username, department=None):
    account = AuthUser.objects.create_user(username=username, password="test-password")
    role, _ = Role.objects.get_or_create(name=f"{username} role")
    role.permissions.set([
        Permission.objects.get_or_create(
            code="asset_custody_manage", defaults={"name": "Custody"})[0]])
    return User.objects.create(
        account=account, user_name=username, emp_id=f"EMP-{username}",
        email_id=f"{username}@example.com", role=role, department=department)


def _catalog():
    brand = Brand.objects.create(brand_name="Dell")
    return dict(category=Category.objects.create(category_name="Laptops"),
                brand=brand,
                model=Model.objects.create(model_name="Latitude", brand=brand))


def _asset(asset_id, cat, **extra):
    return Asset.objects.create(
        asset_id=asset_id, tag_number=f"{asset_id}-T", serial_number=f"{asset_id}-S",
        category=cat["category"], brand=cat["brand"], model=cat["model"], **extra)


class CheckoutDepartmentTests(TestCase):
    """B3 FR-006: the Asset's department follows whoever holds it."""

    def setUp(self):
        self.cat = _catalog()
        self.finance = Department.objects.create(name="Finance B3")

    def test_checkout_to_a_user_with_no_department_clears_the_previous_one(self):
        """Covers: B3 FR-006.

        Register row 2. The department was only ever overwritten when the new holder had
        one, so an Asset handed to someone with no department stayed filed under the
        last department that held it — and a departmental report kept counting it.
        """
        holder = _profile("dept-holder", department=self.finance)
        unaffiliated = _profile("dept-none")
        asset = _asset("DEP-1", self.cat)

        checkout = check_out(asset, holder, holder)
        asset.refresh_from_db()
        self.assertEqual(asset.department_id, self.finance.pk)

        check_in(checkout, "Good", performed_by=holder)
        check_out(asset, unaffiliated, unaffiliated)
        asset.refresh_from_db()

        self.assertIsNone(asset.department_id)


class CheckInRemarksTests(TestCase):
    """B3 FR-014: a worse return is explained, not silently recorded."""

    def setUp(self):
        self.cat = _catalog()
        self.holder = _profile("remarks-holder")

    def test_a_return_in_a_worse_condition_requires_return_remarks(self):
        """Covers: B3 FR-014.

        Register row 5, second half. An Asset coming back damaged is the one case where
        the operator has something to say and the one case where silence loses it.
        """
        asset = _asset("REM-1", self.cat, condition="Good")
        checkout = check_out(asset, self.holder, self.holder, checkout_condition="Good")

        with self.assertRaises(LifecycleError):
            check_in(checkout, "Damaged", performed_by=self.holder)

        checkout.refresh_from_db()
        self.assertEqual(checkout.status, "Open")

    def test_a_worse_return_is_accepted_once_it_is_explained(self):
        """Covers: B3 FR-014."""
        asset = _asset("REM-2", self.cat, condition="Good")
        checkout = check_out(asset, self.holder, self.holder, checkout_condition="Good")

        check_in(checkout, "Damaged", remarks="Dropped in the car park",
                 performed_by=self.holder)

        checkout.refresh_from_db()
        self.assertEqual(checkout.status, "Returned")
        self.assertEqual(checkout.return_remarks, "Dropped in the car park")

    def test_returning_a_new_asset_in_good_order_needs_no_explanation(self):
        """Covers: B3 FR-014.

        "New" describes an Asset that has not been used rather than a level of care, so
        the first return of a new Asset in good order is expected. Prompting for a
        justification here would put one on the most ordinary check-in in the system.
        """
        asset = _asset("REM-3", self.cat, condition="New")
        checkout = check_out(asset, self.holder, self.holder, checkout_condition="New")

        check_in(checkout, "Good", performed_by=self.holder)

        checkout.refresh_from_db()
        self.assertEqual(checkout.status, "Returned")

    def test_an_improved_condition_needs_no_explanation(self):
        """Covers: B3 FR-014."""
        asset = _asset("REM-4", self.cat, condition="Damaged")
        checkout = check_out(asset, self.holder, self.holder,
                             checkout_condition="Damaged")

        check_in(checkout, "Good", performed_by=self.holder)

        checkout.refresh_from_db()
        self.assertEqual(checkout.status, "Returned")

    def test_unclassified_legacy_checkout_requires_classification_before_checkin(self):
        """Covers: feature 014 FR-007/011; legacy history is not assumed temporary."""
        asset = _asset("REM-LEGACY", self.cat, condition="Good")
        checkout = check_out(asset, self.holder, self.holder)
        AssetCheckout.objects.filter(pk=checkout.pk).update(classification="Unclassified")

        with self.assertRaisesMessage(LifecycleError,
                                      "Classify this legacy Checkout before Check-in."):
            check_in(checkout, "Good", performed_by=self.holder)

        asset.refresh_from_db()
        checkout.refresh_from_db()
        self.assertEqual((asset.status, asset.custodian_id, checkout.status,
                          checkout.return_date),
                         ("Assigned", self.holder.pk, "Open", None))


class SingleOpenCheckoutTests(TestCase):
    """B3 FR-001 and FR-007: one holder at a time, enforced by the database."""

    def setUp(self):
        self.cat = _catalog()

    def test_an_asset_cannot_have_two_open_checkouts(self):
        """Covers: B3 FR-001, B3 FR-007, B3 FR-011.

        Register rows 14 and 15. The rule was enforced only by a status check the
        database knew nothing about, and the row lock meant to close the race
        (`select_for_update`) is a no-op on SQLite — so two concurrent checkouts could
        both pass it. A partial unique index holds regardless of engine or timing.
        """
        asset = _asset("ONE-1", self.cat)
        first = _profile("one-first")
        second = _profile("one-second")
        AssetCheckout.objects.create(asset=asset, user=first, status="Open")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AssetCheckout.objects.create(asset=asset, user=second, status="Open")

    def test_a_returned_checkout_does_not_block_the_next_one(self):
        """Covers: B3 FR-001, B3 FR-007."""
        asset = _asset("ONE-2", self.cat)
        holder = _profile("one-holder")
        AssetCheckout.objects.create(asset=asset, user=holder, status="Returned")

        AssetCheckout.objects.create(asset=asset, user=holder, status="Open")

        self.assertEqual(AssetCheckout.objects.filter(asset=asset).count(), 2)


class InterruptedClosureTests(TestCase):
    """B3 FR-028 and B5 FR-015: a closure that was not a completion says so."""

    def setUp(self):
        self.cat = _catalog()
        self.holder = _profile("interrupt-holder")
        self.vendor = Vendor.objects.create(name="Interrupt Repairs")

    def test_an_interrupted_checkout_is_marked_as_such(self):
        """Covers: B3 FR-028.

        Register row 10. Both a real return and a closure forced by something else left
        the record as "Returned", so the two were indistinguishable — and an Asset
        nobody checked in read as though somebody had.
        """
        asset = _asset("INT-1", self.cat)
        checkout = check_out(asset, self.holder, self.holder)

        close_all_open_checkouts(asset, note="Auto-closed: asset sent for service.")

        checkout.refresh_from_db()
        self.assertEqual(checkout.status, "Returned")
        self.assertTrue(checkout.closed_as_interrupted)

    def test_a_genuine_check_in_is_not_marked_as_interrupted(self):
        """Covers: B3 FR-028."""
        asset = _asset("INT-2", self.cat)
        checkout = check_out(asset, self.holder, self.holder)

        check_in(checkout, "Good", performed_by=self.holder)

        checkout.refresh_from_db()
        self.assertFalse(checkout.closed_as_interrupted)

    def test_an_interrupted_service_record_is_marked_as_such(self):
        """Covers: B5 FR-015.

        Register row 4, the same distinction on the repair side.
        """
        asset = _asset("INT-3", self.cat)
        record = open_service(asset, self.vendor, self.holder)

        from .service import close_all_open_service_records
        close_all_open_service_records(asset, note="Auto-closed: asset marked Lost.")

        record.refresh_from_db()
        self.assertEqual(record.status, "Closed")
        self.assertTrue(record.closed_as_interrupted)


class ServiceLifecycleTests(TestCase):
    """B5 FR-005, FR-008, FR-010, FR-030: what opening and closing a repair must check."""

    def setUp(self):
        self.cat = _catalog()
        self.operator = _profile("svc-operator")
        self.vendor = Vendor.objects.create(name="Service Repairs")

    def test_an_in_storage_asset_is_refused_for_service(self):
        """Covers: B5 FR-008.

        Register row 9. An Asset in storage is not in use and has no fault to report;
        it has to come back into circulation before it can be sent for repair.
        """
        asset = _asset("SVC-1", self.cat, status="In Storage")

        with self.assertRaises(LifecycleError):
            open_service(asset, self.vendor, self.operator)

        asset.refresh_from_db()
        self.assertEqual(asset.status, "In Storage")
        self.assertEqual(ServiceRecord.objects.count(), 0)

    def test_opening_a_service_record_clears_the_department(self):
        """Covers: B5 FR-005.

        Registers rows 1 and 2. The Asset is with a vendor, not with the department
        that was using it.
        """
        finance = Department.objects.create(name="Finance B5")
        asset = _asset("SVC-2", self.cat, department=finance)

        open_service(asset, self.vendor, self.operator)

        asset.refresh_from_db()
        self.assertIsNone(asset.department_id)

    def test_closing_re_checks_that_the_asset_is_still_under_repair(self):
        """Covers: B5 FR-010, B5 ALR-005.

        Register row 10. Without the re-check, closing put the Asset back to Available
        from whatever state something else had since moved it into.
        """
        asset = _asset("SVC-3", self.cat)
        record = open_service(asset, self.vendor, self.operator)
        Asset.objects.filter(pk=asset.pk).update(status="Lost")

        with self.assertRaises(LifecycleError):
            close_service(record, self.operator, cost=100)

        record.refresh_from_db()
        asset.refresh_from_db()
        self.assertEqual(record.status, "Open")
        self.assertEqual(asset.status, "Lost")

    def test_closing_remarks_do_not_overwrite_the_reason_it_was_sent(self):
        """Covers: B5 FR-030.

        Register row 3. Opening notes and closing notes record different events;
        replacing one with the other destroyed what the sender wrote.
        """
        asset = _asset("SVC-4", self.cat)
        record = open_service(asset, self.vendor, self.operator,
                              remarks="Screen flickering under load")

        close_service(record, self.operator, cost=250,
                      remarks="Panel replaced under warranty")

        record.refresh_from_db()
        self.assertEqual(record.remarks, "Screen flickering under load")
        self.assertEqual(record.closing_remarks, "Panel replaced under warranty")
        self.assertFalse(record.closed_as_interrupted)
