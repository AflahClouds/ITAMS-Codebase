from django.test import TestCase

from assets.models import AmcContract, Asset
from catalog.models import Brand, Category, Model

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
