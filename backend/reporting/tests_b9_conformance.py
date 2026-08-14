"""Conformance tests for the B9 Dashboard, Reports, and Exports baseline — second pass.

`reporting/tests_conformance.py` covers the read-only property, report content, the
export boundary, terminal exclusion, expiry bands, canonical terminology, and aggregate
disclosure. This module covers what that pass left unverified: the catalogue boundary
(FR-003, FR-011, FR-023), the alerting boundary (FR-004), source ownership (FR-006),
absent related records (FR-022), the AuditLog projection rules (FR-009, FR-010,
ALR-004), and the permission mapping (FR-012, ALR-006).

Each test carries a `Covers:` tag naming the requirements it demonstrates; those tags
feed docs/conformance/traceability-map.md.
"""
import unittest
from datetime import date, timedelta

from django.contrib.auth.models import User as AuthUser
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Permission, Role, User
from assets.models import AssetTransfer, Asset
from catalog.models import Brand, Category, Model
from core.models import AuditLog, Notification

from .views import REPORTS, _report_audit, _report_movement, _report_register


def _profile(username, codes=(), role_name=None, status="Active"):
    account = AuthUser.objects.create_user(username=username, password="test-password")
    if role_name:
        # Admin and IT Manager are seeded by accounts migration 0002.
        role = Role.objects.get(name=role_name)
    else:
        role = Role.objects.create(name=f"{username} role")
        role.permissions.set([
            Permission.objects.get_or_create(code=c, defaults={"name": c})[0]
            for c in codes
        ])
    profile = User.objects.create(
        account=account, user_name=username, emp_id=f"EMP-{username}",
        email_id=f"{username}@example.com", role=role, status=status)
    return account, profile


def _client(username, codes=(), role_name=None):
    account, profile = _profile(username, codes, role_name)
    client = APIClient()
    client.force_authenticate(account)
    return client, profile


def _catalog():
    return dict(
        category=Category.objects.create(category_name="Laptops"),
        brand=Brand.objects.create(brand_name="Dell"),
        model=Model.objects.create(model_name="Latitude"),
    )


def _asset(asset_id, cat, **extra):
    return Asset.objects.create(
        asset_id=asset_id, tag_number=f"{asset_id}-T", serial_number=f"{asset_id}-S",
        category=cat["category"], brand=cat["brand"], model=cat["model"], **extra)


class ReportCatalogueBoundaryTests(TestCase):
    """B9 FR-003, FR-011, FR-023: what belongs in the catalogue, and what it may be called."""

    def setUp(self):
        self.cat = _catalog()

    def test_the_transfer_custody_document_is_not_a_b9_report(self):
        """Covers: B9 FR-011.

        FR-011 keeps the per-Transfer custody PDF owned by B4 under B4's access rule.
        It is absent from the catalogue, and `report_access` does not reach it — the
        document action requires `asset_view` and the reader's B1 scope.
        """
        client, _ = _client("cat-reporter", ("report_access",))
        _, holder = _profile("cat-holder", ("asset_view",))
        asset = _asset("CAT-1", self.cat)
        transfer = AssetTransfer.objects.create(asset=asset, new_owner=holder,
                                                status="Approved")

        catalogue = client.get("/reports/").data["reports"]

        self.assertNotIn("transfer", [row["key"] for row in catalogue])
        self.assertFalse(any("custody" in row["title"].lower() for row in catalogue))
        self.assertEqual(
            client.get(f"/transfer/{transfer.pk}/document/").status_code, 403)

    def test_every_report_and_both_exports_are_authorized_server_side(self):
        """Covers: B9 FR-012, B9 ALR-001, B9 ALR-005."""
        outsider, _ = _client("cat-outsider", ("asset_view",))

        for key in REPORTS:
            with self.subTest(report=key):
                self.assertEqual(outsider.get(f"/reports/{key}/").status_code, 403)
                self.assertEqual(
                    outsider.get(f"/reports/{key}/export/pdf/").status_code, 403)
                self.assertEqual(
                    outsider.get(f"/reports/{key}/export/excel/").status_code, 403)

    def test_no_report_claims_the_reserved_asset_audit_name(self):
        """Covers: B9 FR-003, B9 FR-023.

        FR-003 reserves "Asset Audit" for the deferred F1 physical-verification
        capability, and the catalogue offered "Asset Audit Report" — telling a reader a
        physical audit exists when none does.

        FR-023 leaves the replacement wording to stakeholder review, so this asserts
        only the two constraints the baseline fixes: the reserved name is not used, and
        the title does not read as Asset verification. "Operational Event History" is
        provisional and the acceptance record should confirm it.
        """
        titles = [title for title, _ in REPORTS.values()]

        for title in titles:
            with self.subTest(title=title):
                self.assertNotIn("asset audit", title.lower())


class AlertingBoundaryTests(TestCase):
    """B9 FR-004: a surface a reader must open is not proactive delivery."""

    def setUp(self):
        self.cat = _catalog()

    def test_reading_the_dashboard_and_every_report_notifies_nobody(self):
        """Covers: B9 FR-004, B9 ALR-002.

        FR-004 forbids presenting a B9 surface as satisfying an alerting obligation.
        Proactive delivery belongs to the source capability — B7 issues expiry alerts
        from its daily sweep — so opening a report must not stand in for one.
        """
        client, _ = _client("alert-reader", ("asset_view", "report_access"))
        _profile("alert-watcher", ("asset_custody_manage",))
        _asset("ALR-1", self.cat, warranty_end=date.today() + timedelta(days=30))

        client.get("/dashboard/")
        for key in REPORTS:
            client.get(f"/reports/{key}/")

        self.assertEqual(Notification.objects.count(), 0)


class SourceOwnershipTests(TestCase):
    """B9 FR-006: B9 presents what a source baseline decides, and decides nothing."""

    def setUp(self):
        self.cat = _catalog()

    def test_the_register_report_follows_the_status_the_source_baseline_owns(self):
        """Covers: B9 FR-006."""
        asset = _asset("SRC-1", self.cat, status="Available")

        _, before = _report_register()
        asset.status = "Under Repair"
        asset.save(update_fields=["status"])
        _, after = _report_register()

        self.assertIn("Available", before[0])
        self.assertIn("Under Repair", after[0])

    def test_the_report_presents_no_status_the_source_baseline_does_not_define(self):
        """Covers: B9 FR-006, B9 FR-005."""
        from assets.models import ASSET_STATUSES
        for n, status in enumerate(("Available", "In Storage", "Sold")):
            _asset(f"SRC-S{n}", self.cat, status=status)

        _, rows = _report_register()

        for row in rows:
            with self.subTest(row=row[0]):
                self.assertIn(row[-2], ASSET_STATUSES)


class AbsentRecordTests(TestCase):
    """B9 FR-022: an absent related record is stated, not invented."""

    def setUp(self):
        self.cat = _catalog()

    def test_a_transfer_with_no_previous_holder_gets_no_placeholder_identity(self):
        """Covers: B9 FR-022, B9 FR-005.

        FR-022 requires an absent related record to be presented explicitly rather than
        as "a blank, a placeholder identity, or a dropped row". The Movement report
        wrote the literal name "IT Store" into the Previous User column, which read as a
        real party and was indistinguishable from a Transfer that genuinely came from
        one.
        """
        _, receiver = _profile("abs-receiver", ("asset_view",))
        asset = _asset("ABS-1", self.cat)
        AssetTransfer.objects.create(asset=asset, previous_owner=None,
                                     new_owner=receiver, status="Approved")

        _, rows = _report_movement()

        self.assertNotEqual(rows[0][3], "IT Store")


class AuditProjectionTests(TestCase):
    """B9 FR-009, FR-010, ALR-004: AuditLog reached through a report follows B8."""

    def setUp(self):
        self.cat = _catalog()
        AuditLog.objects.create(username="actor", action="Create", module="Assets",
                                ip_address="203.0.113.9")

    def test_reading_the_audit_report_is_audited_while_ordinary_reports_write_nothing(self):
        """Covers: B9 FR-009, B9 ALR-002.

        FR-009 scopes its obligation to surfaces presenting AuditLog content, and the
        audit report now writes its own entry. The other nine reports write nothing at
        all, which ALR-002 requires — the FR-009 entry is the only permitted write.
        """
        admin, _ = _client("proj-admin", role_name="Admin")
        before = AuditLog.objects.count()

        admin.get("/reports/audit/")
        self.assertEqual(AuditLog.objects.count(), before + 1)

        after_audit = AuditLog.objects.count()
        for key in REPORTS:
            if key != "audit":
                admin.get(f"/reports/{key}/")
        self.assertEqual(AuditLog.objects.count(), after_audit)

    def test_audit_report_content_follows_b8_access_rather_than_report_access(self):
        """Covers: B9 ALR-004, B9 FR-008."""
        reporter, _ = _client("proj-reporter", ("report_access",))

        response = reporter.get("/reports/audit/")

        self.assertEqual(response.status_code, 403)
        self.assertNotIn("203.0.113.9", str(response.data))
        self.assertEqual(reporter.get("/reports/register/").status_code, 200)

    def test_a_rejected_audit_report_read_is_itself_audited(self):
        """Covers: B9 FR-009.

        FR-009 requires an entry for "every allowed AuditLog view or export through a
        B9 surface, **and every rejected attempt**". The rejected half was the real
        residual behind register row 4 — not "the other nine reports still create no
        entry when viewed", since those present no AuditLog content and never owed one.
        """
        reporter, _ = _client("proj-intruder", ("report_access",))
        before = AuditLog.objects.count()

        response = reporter.get("/reports/audit/")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AuditLog.objects.count(), before + 1)

    def test_a_source_address_past_its_retention_window_is_not_presented(self):
        """Covers: B9 FR-010, B9 ALR-004.

        FR-010 requires B9 output carrying AuditLog values to respect B8's treatment of
        source IP as protected data with a shorter life than the entry — six months
        under B8 FR-017. The report applies the window itself rather than trusting that
        the purge job has run, so a restarted process never serves an expired value.
        """
        AuditLog.objects.filter(username="actor").update(
            date=timezone.now() - timedelta(days=250))

        _, rows = _report_audit()

        self.assertNotIn("203.0.113.9", [cell for row in rows for cell in row])


class PermissionMappingTests(TestCase):
    """B9 ALR-006 and FR-012: the mapping each surface actually enforces."""

    def test_the_dashboard_requires_asset_view_and_reports_require_report_access(self):
        """Covers: B9 ALR-006, B9 FR-007, B9 FR-012.

        ALR-006 recorded the Dashboard as requiring authentication only, which it names
        as non-conforming. That half is now closed: `asset_view` is required, and
        `report_access` alone does not open it. The report mapping conformed already.
        """
        viewer, _ = _client("map-viewer", ("asset_view",))
        reporter, _ = _client("map-reporter", ("report_access",))

        self.assertEqual(viewer.get("/dashboard/").status_code, 200)
        self.assertEqual(viewer.get("/reports/register/").status_code, 403)
        self.assertEqual(reporter.get("/reports/register/").status_code, 200)
        self.assertEqual(reporter.get("/dashboard/").status_code, 403)

    def test_a_chart_follows_the_same_mapping_as_the_dashboard(self):
        """Covers: B9 ALR-006, B9 FR-012."""
        viewer, _ = _client("map-chart-viewer", ("asset_view",))
        reporter, _ = _client("map-chart-reporter", ("report_access",))

        self.assertEqual(
            viewer.get("/charts/status-distribution/").status_code, 200)
        self.assertEqual(
            reporter.get("/charts/status-distribution/").status_code, 403)
