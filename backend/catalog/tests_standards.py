"""Feature 015 public catalog regressions (FR-001–003)."""
from django.test import TestCase

from assets.models import Asset
from assets.tests_b6_conformance import _client
from .models import Brand, Category, Model


class ModelBrandTests(TestCase):
    def setUp(self):
        self.client = _client("brand-maintainer", ("settings_access", "asset_view"))
        self.brand = Brand.objects.create(brand_name="Dell")

    def test_create_read_update_retains_brand(self):
        response = self.client.post('/model/', {'model_name': 'Latitude', 'brand': self.brand.pk})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get('brand'), self.brand.pk)
        pk = response.data['id']
        self.assertEqual(self.client.get(f'/model/{pk}/').data['brand'], self.brand.pk)
        other = Brand.objects.create(brand_name='HP')
        response = self.client.patch(f'/model/{pk}/', {'brand': other.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Model.objects.get(pk=pk).brand_id, other.pk)

    def test_new_models_require_valid_nonnull_brand(self):
        for extra in ({}, {'brand': None}, {'brand': 999999}):
            with self.subTest(extra=extra):
                response = self.client.post('/model/', {'model_name': 'Invalid', **extra}, format='json')
                self.assertEqual(response.status_code, 400)
                self.assertIn('brand', response.data)
        self.assertFalse(Model.objects.exists())

    def test_legacy_correction_preserves_identity_references_and_rejects_clear(self):
        legacy = Model.objects.create(model_name='Legacy')
        category = Category.objects.create(category_name='Legacy test laptop')
        asset = Asset.objects.create(asset_id='LEGACY', tag_number='L-T', serial_number='L-S',
                                     category=category, brand=self.brand, model=legacy)
        self.assertIsNone(self.client.get(f'/model/{legacy.pk}/').data.get('brand'))
        response = self.client.patch(f'/model/{legacy.pk}/', {'brand': self.brand.pk})
        self.assertEqual(response.status_code, 200)
        legacy.refresh_from_db()
        asset.refresh_from_db()
        self.assertEqual(legacy.brand_id, self.brand.pk)
        self.assertEqual(asset.model_id, legacy.pk)
        self.assertEqual(self.client.patch(f'/model/{legacy.pk}/', {'brand': None}, format='json').status_code, 400)

    def test_catalog_write_permission_is_preserved(self):
        denied = _client('brand-reader', ('asset_view',))
        self.assertEqual(denied.post('/model/', {'model_name': 'Denied', 'brand': self.brand.pk}).status_code, 403)
        self.assertFalse(Model.objects.exists())
