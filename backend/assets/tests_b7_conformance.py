"""Conformance tests for the B7 Warranty and AMC baseline.

Each test carries a `Covers:` tag naming the requirements it demonstrates; those tags
feed docs/conformance/traceability-map.md.

Requirements the implementation does not yet satisfy are written as `expectedFailure`
rather than omitted, so the requirement stays executable and the runner reports an
unexpected success the moment a gap is closed. Most cite a row of the U-006 register in
`specs/008-warranty-amc-baseline/spec.md`; the two atomicity cases in
`AmcAtomicityTests` do not, and are registered as U-007 by this suite.
"""
import unittest
from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth.models import User as AuthUser
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Permission, Role, User
from catalog.models import Brand, Category, Model, Vendor
from core.models import Notification
from reporting.views import _report_amc_expiry

from .alerts import check_expiring_dates
from .models import AmcContract, Asset, ServiceRecord


def _profile(username, codes=(), status="Active"):
    account = AuthUser.objects.create_user(username=username, password="test-password")
    role = Role.objects.create(name=f"{username} role")
    role.permissions.set([
        Permission.objects.get_or_create(code=c, defaults={"name": c})[0] for c in codes
    ])
    profile = User.objects.create(
        account=account, user_name=username, emp_id=f"EMP-{username}",
        email_id=f"{username}@example.com", role=role, status=status)
    return account, profile


def _client(username, codes=()):
    account, _ = _profile(username, codes)
    client = APIClient()
    client.force_authenticate(account)
    return client


def _catalog():
    return dict(
        category=Category.objects.create(category_name="Laptops"),
        brand=Brand.objects.create(brand_name="Dell"),
        model=Model.objects.create(model_name="Latitude"),
    )


def _asset(asset_id, cat, **extra):
    extra.setdefault("status", "Available")
    return Asset.objects.create(
        asset_id=asset_id, tag_number=f"{asset_id}-T", serial_number=f"{asset_id}-S",
        category=cat["category"], brand=cat["brand"], model=cat["model"], **extra)


def _asset_payload(asset_id, cat, **extra):
    payload = {"asset_id": asset_id, "tag_number": f"{asset_id}-T",
               "serial_number": f"{asset_id}-S", "category": cat["category"].pk,
               "brand": cat["brand"].pk, "model": cat["model"].pk}
    payload.update(extra)
    return payload


class WarrantyRepresentationTests(TestCase):
    """B7 FR-001 to FR-003: Warranty is dates, and nothing more."""

    def setUp(self):
        self.cat = _catalog()

    def test_an_asset_records_warranty_as_a_start_and_an_end_date(self):
        """Covers: B7 FR-001."""
        asset = _asset("WAR-1", self.cat, warranty_start=date(2026, 1, 1),
                       warranty_end=date(2027, 1, 1))
        asset.refresh_from_db()

        self.assertEqual(asset.warranty_start, date(2026, 1, 1))
        self.assertEqual(asset.warranty_end, date(2027, 1, 1))

    def test_warranty_and_amc_are_separate_and_neither_is_derived_from_the_other(self):
        """Covers: B7 FR-001, B7 FR-002."""
        asset = _asset("WAR-2", self.cat, warranty_start=date(2026, 1, 1),
                       warranty_end=date(2027, 1, 1))

        self.assertFalse(asset.has_amc)
        self.assertIsNone(asset.amc_end)

        AmcContract.objects.create(asset=asset, start_date=date(2026, 6, 1),
                                   end_date=date(2027, 6, 1), status="Active")
        asset.refresh_from_db()

        self.assertTrue(asset.has_amc)
        self.assertEqual(asset.amc_end, date(2027, 6, 1))
        self.assertEqual(asset.warranty_end, date(2027, 1, 1), "AMC moved the Warranty")

    def test_warranty_carries_no_status_and_no_lifecycle_workflow(self):
        """Covers: B7 FR-003."""
        names = {f.name for f in Asset._meta.get_fields()}

        self.assertEqual(names & {"warranty_status", "warranty_end_reason"}, set())

        asset = _asset("WAR-3", self.cat, warranty_start=date(2026, 1, 1),
                       warranty_end=date(2027, 1, 1))
        AmcContract.objects.create(asset=asset, start_date=date(2026, 1, 1),
                                   end_date=date(2027, 1, 1), status="Active")
        client = _client("war-editor", ("asset_view", "asset_edit"))

        client.post(f"/asset/{asset.pk}/end_amc_support/", {"reason": "Not renewing"},
                    format="json")

        asset.refresh_from_db()
        self.assertEqual(asset.warranty_end, date(2027, 1, 1),
                         "ending AMC support altered the Warranty")

    def test_a_warranty_start_alone_yields_no_alert_and_stays_distinguishable(self):
        """Covers: B7 FR-036."""
        _profile("war-watcher", ("asset_custody_manage",))
        open_ended = _asset("WAR-4", self.cat, warranty_start=date(2026, 1, 1))
        lapsed = _asset("WAR-5", self.cat, warranty_end=date.today() - timedelta(days=5))

        check_expiring_dates()

        self.assertEqual(Notification.objects.count(), 0)
        self.assertIsNone(open_ended.warranty_days_left)
        self.assertLess(lapsed.warranty_days_left, 0)


    def test_a_warranty_end_before_its_start_is_rejected(self):
        """Covers: B7 FR-031."""
        client = _client("war-writer", ("asset_view", "asset_create"))

        response = client.post("/asset/", _asset_payload(
            "WAR-6", self.cat, warranty_start="2027-01-01", warranty_end="2026-01-01"),
            format="json")

        self.assertEqual(response.status_code, 400)


class AmcCoverageDataTests(TestCase):
    """B7 FR-004, FR-005, FR-013: coverage is queryable data with a current contract."""

    def setUp(self):
        self.cat = _catalog()

    def test_amc_coverage_is_queryable_by_date_rather_than_only_a_document(self):
        """Covers: B7 FR-004."""
        asset = _asset("AMC-1", self.cat)
        AmcContract.objects.create(asset=asset, start_date=date(2026, 1, 1),
                                   end_date=date(2026, 12, 31), status="Active")

        expiring = AmcContract.objects.filter(status="Active",
                                              end_date__lte=date(2027, 1, 1))

        self.assertEqual([c.asset_id for c in expiring], [asset.pk])

    def test_a_lapsed_contract_stays_active_and_reads_as_expired_not_ended(self):
        """Covers: B7 FR-013, B7 ALR-005."""
        lapsed = _asset("AMC-2", self.cat)
        AmcContract.objects.create(asset=lapsed, start_date=date(2020, 1, 1),
                                   end_date=date.today() - timedelta(days=1),
                                   status="Active")
        deliberate = _asset("AMC-3", self.cat)
        AmcContract.objects.create(asset=deliberate, start_date=date(2020, 1, 1),
                                   end_date=date.today() - timedelta(days=1),
                                   status="Ended", end_reason="Vendor withdrew")

        check_expiring_dates()

        _, rows = _report_amc_expiry()
        by_asset = {r[0]: r for r in rows}
        self.assertEqual(by_asset["AMC-2"][-2:], ["Active", "Expired"])
        self.assertEqual(by_asset["AMC-3"][-2:], ["Ended", "Ended"])


    def test_the_current_contract_is_chosen_by_dates_not_by_creation_order(self):
        """Covers: B7 FR-005, B7 ALR-004.

        FR-005 and ALR-004 ask which contract is *current*, which is a question about
        coverage rather than data-entry order.
        """
        asset = _asset("AMC-4", self.cat)
        AmcContract.objects.create(asset=asset, start_date=date(2026, 1, 1),
                                   end_date=date(2027, 1, 1), status="Active")
        AmcContract.objects.create(asset=asset, start_date=date(2019, 1, 1),
                                   end_date=date(2020, 1, 1), status="Active")
        asset.refresh_from_db()

        self.assertEqual(asset.amc_end, date(2027, 1, 1))


    def test_initial_amc_entry_enforces_the_same_date_rules_as_renewal(self):
        """Covers: B7 FR-030.

        FR-030 exists because the same values were accepted by the Asset write path and
        refused by `renew_amc`, so which rules applied depended on how the operator got
        there.
        """
        client = _client("amc-writer", ("asset_view", "asset_create"))

        response = client.post("/asset/", _asset_payload(
            "AMC-5", self.cat, has_amc=True, amc_start="2027-01-01",
            amc_end="2026-01-01"), format="json")

        self.assertEqual(response.status_code, 400)


    def test_initial_amc_entry_requires_a_managed_vendor_once_it_has_dates(self):
        """Covers: B7 FR-032.

        FR-032 requires a managed B6 Vendor on any dated contract. Renewal already did;
        initial entry recorded none, so an Asset whose AMC was never renewed reported no
        maintainer at all.
        """
        client = _client("amc-vendorless", ("asset_view", "asset_create"))

        response = client.post("/asset/", _asset_payload(
            "AMC-6", self.cat, has_amc=True, amc_start="2026-01-01",
            amc_end="2027-01-01"), format="json")

        self.assertEqual(response.status_code, 400)


class AmcDecisionSafetyTests(TestCase):
    """B7 FR-011, FR-034, ALR-003: decisions are guarded and history is legible."""

    def setUp(self):
        self.cat = _catalog()
        self.vendor = Vendor.objects.create(name="Maintainer Ltd")
        self.client_it = _client("amc-decider", ("asset_view", "asset_edit"))

    def test_renewal_is_rejected_for_a_terminal_asset_and_changes_nothing(self):
        """Covers: B7 FR-011, B7 ALR-003."""
        asset = _asset("DEC-1", self.cat, status="Scrapped")
        AmcContract.objects.create(asset=asset, start_date=date(2026, 1, 1),
                                   end_date=date(2027, 1, 1), status="Active")

        response = self.client_it.post(f"/asset/{asset.pk}/renew_amc/", {
            "amc_start": "2027-01-01", "amc_end": "2028-01-01",
            "vendor": self.vendor.pk}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(AmcContract.objects.filter(asset=asset).count(), 1)
        self.assertEqual(AmcContract.objects.get(asset=asset).status, "Active")

    def test_a_denied_renewal_leaves_every_contract_untouched(self):
        """Covers: B7 ALR-001, B7 ALR-003, B7 ALR-008."""
        asset = _asset("DEC-2", self.cat)
        AmcContract.objects.create(asset=asset, start_date=date(2026, 1, 1),
                                   end_date=date(2027, 1, 1), status="Active")
        reader = _client("amc-reader", ("asset_view",))

        response = reader.post(f"/asset/{asset.pk}/renew_amc/", {
            "amc_start": "2027-01-01", "amc_end": "2028-01-01",
            "vendor": self.vendor.pk}, format="json")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AmcContract.objects.filter(asset=asset).count(), 1)
        self.assertEqual(AmcContract.objects.get(asset=asset).end_date, date(2027, 1, 1))

    def test_reading_amc_history_requires_asset_view(self):
        """Covers: B7 FR-023, B7 ALR-008."""
        asset = _asset("DEC-3", self.cat)
        nobody = _client("amc-nobody", ())

        self.assertEqual(nobody.get(f"/asset/{asset.pk}/history/").status_code, 403)
        self.assertEqual(self.client_it.get(f"/asset/{asset.pk}/history/").status_code, 200)


    def test_end_support_is_rejected_for_a_terminal_asset(self):
        """Covers: B7 FR-011, B7 ALR-003.

        FR-011 and ALR-003: renewal guarded against terminal Assets and End Support did
        not, so support could be ended on an Asset that had left circulation.
        """
        asset = _asset("DEC-4", self.cat, status="Sold")
        AmcContract.objects.create(asset=asset, start_date=date(2026, 1, 1),
                                   end_date=date(2027, 1, 1), status="Active")

        response = self.client_it.post(f"/asset/{asset.pk}/end_amc_support/",
                                       {"reason": "Sold on"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(AmcContract.objects.get(asset=asset).status, "Active")


    def test_the_supersede_marker_is_held_apart_from_the_operator_reason(self):
        """Covers: B7 FR-034.

        FR-034: renewal wrote the literal string "Renewed" into `end_reason`, the same
        field an operator's End Support reason occupies. The marker is now a flag, so
        "this was replaced" and "an operator decided to stop" stay distinguishable.
        """
        asset = _asset("DEC-5", self.cat)
        AmcContract.objects.create(asset=asset, start_date=date(2026, 1, 1),
                                   end_date=date(2027, 1, 1), status="Active")

        self.client_it.post(f"/asset/{asset.pk}/renew_amc/", {
            "amc_start": "2027-01-01", "amc_end": "2028-01-01",
            "vendor": self.vendor.pk}, format="json")

        superseded = AmcContract.objects.filter(asset=asset, status="Ended").first()
        self.assertEqual(superseded.end_reason, "",
                         "the automatic supersede marker occupies the operator's field")

    def test_renewal_preserves_the_superseded_contract_in_history(self):
        """Covers: B7 FR-015, B7 ALR-004."""
        asset = _asset("DEC-6", self.cat)
        AmcContract.objects.create(asset=asset, start_date=date(2026, 1, 1),
                                   end_date=date(2027, 1, 1), status="Active")

        self.client_it.post(f"/asset/{asset.pk}/renew_amc/", {
            "amc_start": "2027-01-01", "amc_end": "2028-01-01",
            "vendor": self.vendor.pk}, format="json")

        old = AmcContract.objects.get(asset=asset, status="Ended")
        self.assertEqual((old.start_date, old.end_date),
                         (date(2026, 1, 1), date(2027, 1, 1)))
        self.assertEqual(AmcContract.objects.filter(asset=asset).count(), 2)


class AmcAtomicityTests(TestCase):
    """B7 ALR-002 and ALR-007: the audit entry commits with the decision, or neither does.

    NEW FINDING — registered as U-007 by this suite. The U-006 register records that
    AMC audit entries are *thin* (row 13); it does not record that they are written
    outside the transaction that carries the contract change.
    """

    def setUp(self):
        self.cat = _catalog()
        self.vendor = Vendor.objects.create(name="Atomic Ltd")
        self.client_it = _client("amc-atomic", ("asset_view", "asset_edit"))

    def test_a_failed_audit_write_rolls_back_the_renewal(self):
        """Covers: B7 FR-014, B7 ALR-002, B7 ALR-007.

        Gap U-007. `log_action` is called after the `transaction.atomic()` block in
        `AssetViewSet.renew_amc`, so a failing AuditLog write leaves the superseded
        contract closed and the new contract created with no record of who did it.
        """
        asset = _asset("ATOM-1", self.cat)
        AmcContract.objects.create(asset=asset, start_date=date(2026, 1, 1),
                                   end_date=date(2027, 1, 1), status="Active")

        with patch("assets.views.log_action", side_effect=RuntimeError("audit down")):
            with self.assertRaises(RuntimeError):
                self.client_it.post(f"/asset/{asset.pk}/renew_amc/", {
                    "amc_start": "2027-01-01", "amc_end": "2028-01-01",
                    "vendor": self.vendor.pk}, format="json")

        self.assertEqual(AmcContract.objects.filter(asset=asset).count(), 1)
        self.assertEqual(AmcContract.objects.get(asset=asset).status, "Active")

    def test_a_failed_audit_write_rolls_back_the_end_support(self):
        """Covers: B7 FR-014, B7 ALR-002, B7 ALR-007.

        Gap U-007. `end_amc_support` has no transaction at all: it saves the contract,
        then logs, then notifies. A failing audit write leaves the contract `Ended`
        with the reason recorded and no audit entry.
        """
        asset = _asset("ATOM-2", self.cat)
        AmcContract.objects.create(asset=asset, start_date=date(2026, 1, 1),
                                   end_date=date(2027, 1, 1), status="Active")

        with patch("assets.views.log_action", side_effect=RuntimeError("audit down")):
            with self.assertRaises(RuntimeError):
                self.client_it.post(f"/asset/{asset.pk}/end_amc_support/",
                                    {"reason": "Vendor withdrew"}, format="json")

        self.assertEqual(AmcContract.objects.get(asset=asset).status, "Active")


class ExpiryAlertTests(TestCase):
    """B7 FR-016 to FR-020, ALR-006: the sweep reads, notifies, and changes nothing."""

    def setUp(self):
        self.cat = _catalog()
        _, self.watcher = _profile("alert-watcher", ("asset_custody_manage",))

    def test_an_alert_is_delivered_in_app_and_addressed_to_a_specific_user(self):
        """Covers: B7 FR-017, B7 FR-035."""
        asset = _asset("ALT-1", self.cat,
                       warranty_end=date.today() + timedelta(days=30))

        check_expiring_dates()

        notice = Notification.objects.get(user=self.watcher)
        self.assertIn("ALT-1", notice.message)
        self.assertEqual(notice.link, f"/asset/{asset.pk}")

    def test_the_expiry_sweep_changes_no_asset_and_no_contract(self):
        """Covers: B7 ALR-006, B7 ALR-005."""
        asset = _asset("ALT-2", self.cat,
                       warranty_end=date.today() + timedelta(days=15))
        contract = AmcContract.objects.create(
            asset=asset, start_date=date(2026, 1, 1),
            end_date=date.today() + timedelta(days=15), status="Active")
        before = (asset.status, asset.warranty_end, contract.status,
                  contract.end_date, contract.end_reason)

        check_expiring_dates()

        asset.refresh_from_db()
        contract.refresh_from_db()
        self.assertEqual((asset.status, asset.warranty_end, contract.status,
                          contract.end_date, contract.end_reason), before)

    def test_a_date_short_of_a_threshold_is_silent(self):
        """Covers: B7 FR-016."""
        _asset("ALT-3", self.cat, warranty_end=date.today() + timedelta(days=21))

        check_expiring_dates()

        self.assertEqual(Notification.objects.count(), 0)


    def test_a_terminal_asset_generates_no_warranty_alert(self):
        """Covers: B7 FR-020.

        FR-020: the Warranty sweep filtered on `warranty_end` alone with no status
        condition, so a terminal Asset raised alerts that offered no action to take.
        """
        _asset("ALT-4", self.cat, status="Scrapped",
               warranty_end=date.today() + timedelta(days=30))

        check_expiring_dates()

        self.assertEqual(Notification.objects.count(), 0)


class DecisionNotificationTests(TestCase):
    """B7 FR-021 and FR-039: decision notices follow permission, and reach the living."""

    def setUp(self):
        self.cat = _catalog()
        self.vendor = Vendor.objects.create(name="Notify Ltd")
        self.client_it = _client("notif-actor", ("asset_view", "asset_edit"))

    def test_only_active_holders_of_the_manager_grant_are_notified(self):
        """Covers: B7 FR-021, B7 FR-039."""
        _, live = _profile("notif-live", ("asset_delete",))
        _, gone = _profile("notif-gone", ("asset_delete",), status="Disabled")
        _, bystander = _profile("notif-bystander", ("asset_view",))
        asset = _asset("NOT-1", self.cat)
        AmcContract.objects.create(asset=asset, start_date=date(2026, 1, 1),
                                   end_date=date(2027, 1, 1), status="Active")

        self.client_it.post(f"/asset/{asset.pk}/renew_amc/", {
            "amc_start": "2027-01-01", "amc_end": "2028-01-01",
            "vendor": self.vendor.pk}, format="json")

        notified = set(Notification.objects.values_list("user_id", flat=True))
        self.assertIn(live.pk, notified)
        self.assertNotIn(gone.pk, notified)
        self.assertNotIn(bystander.pk, notified)

    def test_the_end_support_notice_carries_the_recorded_reason(self):
        """Covers: B7 FR-012, B7 FR-021."""
        _, manager = _profile("notif-manager", ("asset_delete",))
        asset = _asset("NOT-2", self.cat)
        AmcContract.objects.create(asset=asset, start_date=date(2026, 1, 1),
                                   end_date=date(2027, 1, 1), status="Active")

        self.client_it.post(f"/asset/{asset.pk}/end_amc_support/",
                            {"reason": "Vendor withdrew"}, format="json")

        notice = Notification.objects.get(user=manager)
        self.assertIn("NOT-2", notice.message)
        self.assertIn("Vendor withdrew", notice.message)


class CoverageBoundaryTests(TestCase):
    """B7 FR-026: repair activity is not coverage evidence."""

    def test_a_service_record_neither_creates_nor_implies_amc_coverage(self):
        """Covers: B7 FR-026."""
        cat = _catalog()
        vendor = Vendor.objects.create(name="Repairer Ltd")
        asset = _asset("BND-1", cat)

        ServiceRecord.objects.create(asset=asset, vendor=vendor)
        asset.refresh_from_db()

        self.assertEqual(AmcContract.objects.filter(asset=asset).count(), 0)
        self.assertFalse(asset.has_amc)
        self.assertIsNone(asset.amc_end)
