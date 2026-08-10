from django.contrib.auth.models import User as AuthUser
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.models import Permission, Role, User
from assets.models import AmcContract, Asset
from catalog.models import Brand, Category, Model
from core.models import AuditLog

from .views import _report_amc_expiry


class AmcExpiryReportTests(TestCase):
    def test_report_does_not_crash_on_a_contract_ended_before_dates_were_entered(self):
        category = Category.objects.create(category_name="Report Cat")
        brand = Brand.objects.create(brand_name="Report Brand")
        model = Model.objects.create(model_name="Report Model")
        asset = Asset.objects.create(
            asset_id="RPT-AMC-001", tag_number="RPT-TAG-001", serial_number="RPT-SER-001",
            category=category, brand=brand, model=model)
        AmcContract.objects.create(asset=asset, status="Ended", end_reason="Cancelled")

        headers, rows = _report_amc_expiry()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "RPT-AMC-001")
        self.assertIn("Cancelled before dates were entered", rows[0][-1])


def _profile(username, permission_codes=(), status="Active"):
    account = AuthUser.objects.create_user(username=username, password="test-password")
    role = Role.objects.create(name=f"{username} role")
    role.permissions.set([
        Permission.objects.get_or_create(code=code, defaults={"name": code})[0]
        for code in permission_codes
    ])
    profile = User.objects.create(
        account=account, user_name=f"{username} profile", emp_id=f"EMP-{username}",
        email_id=f"{username}@example.com", role=role, status=status)
    return account, profile


def _client_for(account):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=account).key}")
    return client


class DashboardAuthorizationTests(TestCase):
    """The Dashboard and charts summarize the whole Asset register, so they must sit
    behind the same permission gate as the records they aggregate. They were previously
    plain @api_view functions, which authenticated the caller but checked no permission
    and no profile status."""

    def test_asset_viewer_may_read_dashboard_and_charts(self):
        account, _ = _profile("viewer", ("asset_view",))
        client = _client_for(account)

        self.assertEqual(client.get("/dashboard/").status_code, 200)
        self.assertEqual(client.get("/charts/status-distribution/").status_code, 200)

    def test_user_without_asset_view_is_denied(self):
        account, _ = _profile("nobody")
        client = _client_for(account)

        self.assertEqual(client.get("/dashboard/").status_code, 403)
        self.assertEqual(client.get("/charts/status-distribution/").status_code, 403)

    def test_disabled_profile_is_denied_even_with_a_live_token(self):
        account, _ = _profile("disabled", ("asset_view",), status="Disabled")
        client = _client_for(account)

        self.assertEqual(client.get("/dashboard/").status_code, 403)
        self.assertEqual(client.get("/charts/status-distribution/").status_code, 403)

    def test_anonymous_request_is_rejected(self):
        self.assertEqual(APIClient().get("/dashboard/").status_code, 401)

    def test_unknown_chart_still_returns_404_for_a_permitted_reader(self):
        account, _ = _profile("chart-reader", ("asset_view",))
        client = _client_for(account)

        self.assertEqual(client.get("/charts/no-such-chart/").status_code, 404)


class AuditReportAccessTests(TestCase):
    """The audit report serves the same rows as the Admin-only /audit/ endpoint, so
    report_access alone must not reach it — otherwise it is a way around that gate."""

    def _admin_client(self):
        account = AuthUser.objects.create_user(username="rep-admin", password="test-password")
        # The Admin role is seeded by accounts migration 0002, not created here.
        role = Role.objects.get(name="Admin")
        User.objects.create(account=account, user_name="rep admin", emp_id="EMP-rep-admin",
                            email_id="rep-admin@example.com", role=role)
        return _client_for(account)

    def test_report_access_alone_cannot_read_the_audit_report(self):
        account, _ = _profile("reporter", ("report_access",))
        client = _client_for(account)

        self.assertEqual(client.get("/reports/audit/").status_code, 403)
        self.assertEqual(client.get("/audit/").status_code, 403)

    def test_report_access_alone_cannot_export_the_audit_report(self):
        account, _ = _profile("exporter", ("report_access",))
        client = _client_for(account)

        self.assertEqual(client.get("/reports/audit/export/pdf/").status_code, 403)
        self.assertEqual(client.get("/reports/audit/export/excel/").status_code, 403)

    def test_the_audit_report_is_hidden_from_the_catalog_it_cannot_open(self):
        account, _ = _profile("catalog-reader", ("report_access",))
        client = _client_for(account)

        keys = [row["key"] for row in client.get("/reports/").data["reports"]]

        self.assertNotIn("audit", keys)
        self.assertIn("register", keys)

    def test_admin_reads_lists_and_exports_the_audit_report(self):
        client = self._admin_client()

        self.assertEqual(client.get("/reports/audit/").status_code, 200)
        self.assertEqual(client.get("/reports/audit/export/pdf/").status_code, 200)
        self.assertIn("audit", [row["key"] for row in client.get("/reports/").data["reports"]])

    def test_reading_the_audit_report_is_itself_audited(self):
        client = self._admin_client()
        before = AuditLog.objects.filter(action="Report View").count()

        client.get("/reports/audit/")

        self.assertEqual(AuditLog.objects.filter(action="Report View").count(), before + 1)

    def test_ordinary_reports_remain_open_to_report_access(self):
        account, _ = _profile("ordinary-reporter", ("report_access",))
        client = _client_for(account)

        self.assertEqual(client.get("/reports/register/").status_code, 200)
        self.assertEqual(client.get("/reports/register/export/excel/").status_code, 200)
