"""Conformance tests for the B9 Dashboard, Reports, and Exports baseline.

Each test carries a `Covers:` tag naming the requirements it demonstrates; those tags
feed docs/conformance/traceability-map.md.

Requirements the implementation does not yet satisfy are written as `expectedFailure`
rather than omitted, so the requirement stays executable and the runner reports an
unexpected success the moment a gap is closed.
"""
import unittest
from datetime import date, timedelta

from django.contrib.auth.models import User as AuthUser
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.models import Permission, Role, User
from assets.models import AmcContract, Asset, ServiceRecord
from catalog.models import Brand, Category, Model, Vendor
from core.models import AuditLog


def _profile(username, codes=()):
    account = AuthUser.objects.create_user(username=username, password="test-password")
    role = Role.objects.create(name=f"{username} role")
    role.permissions.set([
        Permission.objects.get_or_create(code=c, defaults={"name": c})[0] for c in codes
    ])
    User.objects.create(account=account, user_name=username, emp_id=f"EMP-{username}",
                        email_id=f"{username}@example.com", role=role)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=account).key}")
    return client


def _catalog():
    return (Category.objects.create(category_name="C"),
            Brand.objects.create(brand_name="B"),
            Model.objects.create(model_name="M"))


def _asset(asset_id, cat, brand, model, **extra):
    return Asset.objects.create(
        asset_id=asset_id, tag_number=f"{asset_id}-T", serial_number=f"{asset_id}-S",
        category=cat, brand=brand, model=model, **extra)


class ReadOnlySurfaceTests(TestCase):
    """B9 ALR-002 / FR-013: reading or exporting changes no business record."""

    def setUp(self):
        self.cat, self.brand, self.model = _catalog()
        _asset("RO-1", self.cat, self.brand, self.model, status="Available", purchase_cost=100)
        self.client_r = _profile("read-only", ("asset_view", "report_access"))

    def _business_snapshot(self):
        return (
            list(Asset.objects.values_list("id", "status", "condition", "custodian_id")),
            ServiceRecord.objects.count(),
            AmcContract.objects.count(),
        )

    def test_reading_the_dashboard_and_charts_mutates_nothing(self):
        """Covers: B9 ALR-002, B9 FR-013."""
        before = self._business_snapshot()

        self.client_r.get("/dashboard/")
        for chart in ("status-distribution", "category-distribution", "warranty-timeline"):
            self.client_r.get(f"/charts/{chart}/")

        self.assertEqual(before, self._business_snapshot())

    def test_running_and_exporting_every_report_mutates_nothing(self):
        """Covers: B9 ALR-002, B9 FR-013."""
        before = self._business_snapshot()

        for key in ("register", "movement", "warranty", "purchase", "employee",
                    "in_service", "vendor_service", "amc_expiry", "lost"):
            self.assertEqual(self.client_r.get(f"/reports/{key}/").status_code, 200)
            self.assertEqual(self.client_r.get(f"/reports/{key}/export/excel/").status_code, 200)

        self.assertEqual(before, self._business_snapshot())


class ReportContentTests(TestCase):
    """The accepted meaning of specific reports."""

    def setUp(self):
        self.cat, self.brand, self.model = _catalog()
        self.client_r = _profile("report-reader", ("asset_view", "report_access"))

    def test_the_lost_report_presents_lost_assets_with_their_retained_custodian(self):
        """Covers: B9 FR-002."""
        holder = User.objects.create(user_name="holder", emp_id="EMP-h",
                                     email_id="h@example.com")
        _asset("LOST-1", self.cat, self.brand, self.model, status="Lost", custodian=holder)
        _asset("AVAIL-1", self.cat, self.brand, self.model, status="Available")

        rows = self.client_r.get("/reports/lost/").data["rows"]

        self.assertEqual([r[0] for r in rows], ["LOST-1"])
        self.assertIn("holder", rows[0])

    def test_vendor_service_reporting_groups_by_vendor(self):
        """Covers: B9 FR-001."""
        v1 = Vendor.objects.create(name="Repairer One")
        v2 = Vendor.objects.create(name="Repairer Two")
        a = _asset("VS-1", self.cat, self.brand, self.model)
        ServiceRecord.objects.create(asset=a, vendor=v1, status="Open")
        ServiceRecord.objects.create(asset=a, vendor=v1, status="Open")
        ServiceRecord.objects.create(asset=a, vendor=v2, status="Open")

        rows = self.client_r.get("/reports/vendor_service/").data["rows"]

        by_vendor = {r[0]: r[1] for r in rows}
        self.assertEqual(by_vendor["Repairer One"], 2)
        self.assertEqual(by_vendor["Repairer Two"], 1)

    def test_a_report_with_no_matching_records_returns_an_empty_row_set(self):
        """Covers: B9 FR-021."""
        response = self.client_r.get("/reports/lost/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["rows"], [])
        self.assertTrue(response.data["headers"])


class ExportBoundaryTests(TestCase):
    """B9 ALR-005: an export carries exactly what the on-screen report carries."""

    def setUp(self):
        self.cat, self.brand, self.model = _catalog()
        for i in range(3):
            _asset(f"EX-{i}", self.cat, self.brand, self.model, status="Available")
        self.client_r = _profile("exporter", ("asset_view", "report_access"))

    def test_both_export_formats_are_produced_server_side_under_authorization(self):
        """Covers: B9 ALR-005, B9 ALR-001."""
        for fmt, ctype in (("pdf", "application/pdf"),
                           ("excel", "application/vnd.openxmlformats-officedocument"
                                     ".spreadsheetml.sheet")):
            response = self.client_r.get(f"/reports/register/export/{fmt}/")
            self.assertEqual(response.status_code, 200, fmt)
            self.assertEqual(response["Content-Type"], ctype)

    def test_an_unauthorized_reader_receives_neither_report_nor_export(self):
        """Covers: B9 ALR-001, B9 ALR-005."""
        outsider = _profile("no-reports", ("asset_view",))

        self.assertEqual(outsider.get("/reports/register/").status_code, 403)
        self.assertEqual(outsider.get("/reports/register/export/excel/").status_code, 403)

    @unittest.expectedFailure
    def test_csv_export_is_produced_server_side_like_the_other_formats(self):
        """Covers: B9 ALR-005, B9 ALR-001.

        Known gap (§U-007 row 8). CSV is generated in the browser from data already on
        screen, so it never passes through the server's authorization check and creates
        no audit entry, unlike the PDF and Excel paths.
        """
        response = self.client_r.get("/reports/register/export/csv/")

        self.assertEqual(response.status_code, 200)


class TerminalExclusionTests(TestCase):
    """B9 FR-017 and FR-020: terminal Assets leave circulation and leave the figures."""

    def setUp(self):
        self.cat, self.brand, self.model = _catalog()
        _asset("LIVE-1", self.cat, self.brand, self.model, status="Available",
               purchase_cost=100)
        _asset("SOLD-1", self.cat, self.brand, self.model, status="Sold", purchase_cost=500)
        self.client_r = _profile("metrics", ("asset_view", "report_access"))

    @unittest.expectedFailure
    def test_total_value_counts_only_assets_the_organization_still_holds(self):
        """Covers: B9 FR-017, B9 FR-020.

        Known gap (§U-007 row 9). Terminal Assets are still counted everywhere,
        including total portfolio value, which overstates it — here by the 500 of a
        `Sold` Asset.
        """
        kpis = self.client_r.get("/dashboard/").data["kpis"]

        self.assertEqual(kpis["total_assets"], 1)
        self.assertEqual(kpis["total_value"], 100.0)


class ExpiryBandTests(TestCase):
    """B9 FR-018 and FR-019: expiry figures are disjoint bands, not cumulative."""

    def setUp(self):
        self.cat, self.brand, self.model = _catalog()
        _asset("WAR-1", self.cat, self.brand, self.model, status="Available",
               warranty_end=date.today() + timedelta(days=5))
        self.client_r = _profile("bands", ("asset_view", "report_access"))

    @unittest.expectedFailure
    def test_one_asset_appears_in_exactly_one_expiry_band(self):
        """Covers: B9 FR-018, B9 FR-019.

        Known gap (§U-007 row 10). The 7/15/30-day figures are cumulative, so an Asset
        five days from expiry is counted in all three at once. FR-018 requires disjoint
        bands and FR-019 fixes their boundaries.
        """
        kpis = self.client_r.get("/dashboard/").data["kpis"]

        counted = sum(kpis[f"warranty_expiring_{d}"] for d in (7, 15, 30))
        self.assertEqual(counted, 1)


class CanonicalTerminologyTests(TestCase):
    """B9 FR-005: every label and column heading uses the canonical vocabulary."""

    def setUp(self):
        self.client_r = _profile("terminology", ("asset_view", "report_access"))

    @unittest.expectedFailure
    def test_the_register_report_names_the_custodian_column_canonically(self):
        """Covers: B9 FR-005.

        Known gap (§U-007 row 6). The Asset Register report heads the custody column
        "Owner"; `CONTEXT.md` makes **Custodian** the canonical term.
        """
        headers = self.client_r.get("/reports/register/").data["headers"]

        self.assertIn("Custodian", headers)
        self.assertNotIn("Owner", headers)

    def test_no_report_catalogue_entry_uses_the_rejected_assignment_term(self):
        """Covers: B9 FR-005."""
        titles = " ".join(row["title"] for row in self.client_r.get("/reports/").data["reports"])

        self.assertNotIn("Assignment", titles)
        self.assertNotIn("Disposed", titles)


class AggregateDisclosureTests(TestCase):
    """B9 ALR-003 and FR-016: no aggregate summarizes records the reader cannot read."""

    def test_a_reader_scoped_dashboard_counts_only_their_visible_assets(self):
        """Covers: B9 ALR-003, B9 FR-016, B9 FR-007."""
        cat, brand, model = _catalog()
        employee_account = AuthUser.objects.create_user(username="emp-agg", password="x")
        employee = User.objects.create(
            account=employee_account, user_name="emp-agg", emp_id="EMP-agg",
            email_id="agg@example.com", role=Role.objects.get(name="Employee"))
        client = APIClient()
        client.credentials(
            HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=employee_account).key}")
        _asset("MINE", cat, brand, model, status="Assigned", custodian=employee)
        _asset("THEIRS-1", cat, brand, model, status="Available")
        _asset("THEIRS-2", cat, brand, model, status="Available")

        kpis = client.get("/dashboard/").data["kpis"]

        self.assertEqual(kpis["total_assets"], 1)


class ReportAuditTests(TestCase):
    """B9 FR-009: an AuditLog-derived export is itself audited."""

    def test_exporting_a_report_creates_an_audit_entry(self):
        """Covers: B9 FR-009, B8 FR-014."""
        client = _profile("audited-exporter", ("asset_view", "report_access"))
        before = AuditLog.objects.filter(action="Report Export").count()

        client.get("/reports/register/export/excel/")

        self.assertEqual(AuditLog.objects.filter(action="Report Export").count(), before + 1)
