"""Feature 015 public catalog regressions (FR-001–003)."""
from django.test import TestCase
from django.db import IntegrityError
from unittest.mock import patch

from assets.models import Asset
from assets.tests_b6_conformance import _client
from .models import Brand, Category, Model
from .models import PurchaseMode, Vendor
from core.models import AuditLog


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


class CatalogIdentityTests(TestCase):
    def setUp(self):
        self.client = _client('identity-maintainer', ('settings_access', 'asset_view'))
        self.brand = Brand.objects.create(brand_name='Identity Brand')

    def masters(self):
        return [(Category, '/category/', 'category_name', {}),
                (Brand, '/brand/', 'brand_name', {}),
                (PurchaseMode, '/purchase_mode/', 'purchase_mode', {}),
                (Vendor, '/vendor/', 'name', {}),
                (Model, '/model/', 'model_name', {'brand': self.brand.pk})]

    def test_all_names_normalize_reject_conflicts_and_allow_self_updates(self):
        for model, url, field, extra in self.masters():
            with self.subTest(model=model.__name__):
                first = self.client.post(url, {field: ' Probe   Identity ', **extra})
                self.assertEqual(first.status_code, 201)
                self.assertEqual(first.data[field], 'Probe Identity')
                pk = first.data['id']
                for duplicate in ('probe identity', ' Probe   Identity ', 'Probe Identity'):
                    before = AuditLog.objects.count()
                    response = self.client.post(url, {field: duplicate, **extra})
                    self.assertEqual(response.status_code, 400)
                    self.assertIn(field, response.data)
                    self.assertEqual(AuditLog.objects.count(), before + 1)
                    audit = AuditLog.objects.latest('pk')
                    self.assertIn('Rejected', audit.action)
                    self.assertEqual(audit.username, 'identity-maintainer')
                    self.assertIn('Identity', audit.new_value)
                self.assertEqual(self.client.patch(f'{url}{pk}/', {field: ' Probe  Identity '}).status_code, 200)
                self.assertEqual(self.client.patch(f'{url}{pk}/', {field: 'Renamed Identity'}).status_code, 200)
                other = self.client.post(url, {field: 'Other Identity', **extra}).data['id']
                before = AuditLog.objects.count()
                response = self.client.patch(f'{url}{other}/', {field: ' renamed   IDENTITY '})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(AuditLog.objects.count(), before + 1)
                self.assertEqual(getattr(model.objects.get(pk=other), field), 'Other Identity')
                self.assertEqual(getattr(model.objects.get(pk=pk), field), 'Renamed Identity')
                self.assertEqual(self.client.post(url, {field: ' \t\n ', **extra}).status_code, 400)

    def test_models_scope_identity_to_brand_including_brand_change(self):
        other = Brand.objects.create(brand_name='Second Identity Brand')
        one = Model.objects.create(model_name='Shared', brand=self.brand)
        response = self.client.post('/model/', {'model_name': 'shared', 'brand': other.pk})
        self.assertEqual(response.status_code, 201)
        before = AuditLog.objects.count()
        response = self.client.patch(f'/model/{one.pk}/', {'brand': other.pk})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(AuditLog.objects.count(), before + 1)
        one.refresh_from_db()
        self.assertEqual(one.brand_id, self.brand.pk)

    def test_known_save_race_rolls_back_and_keeps_one_rejection_audit(self):
        for model, url, field, extra in self.masters():
            with self.subTest(model=model.__name__):
                original_save = model.save
                constraint = {'Category': 'uniq_category_name_ci', 'Brand': 'uniq_brand_name_ci',
                              'PurchaseMode': 'uniq_purchase_mode_ci', 'Vendor': 'uniq_vendor_name_ci',
                              'Model': 'uniq_model_per_brand_ci'}[model.__name__]
                def race(instance, *args, **kwargs):
                    original_save(instance, *args, **kwargs)
                    raise IntegrityError(f"UNIQUE constraint failed: index '{constraint}'")
                before = AuditLog.objects.count()
                with patch.object(model, 'save', race):
                    response = self.client.post(url, {field: 'Racing Identity', **extra})
                self.assertEqual(response.status_code, 400)
                self.assertFalse(model.objects.filter(**{field: 'Racing Identity'}).exists())
                self.assertEqual(AuditLog.objects.count(), before + 1)
                self.assertIn('Rejected', AuditLog.objects.latest('pk').action)

    def test_unrelated_integrity_errors_are_not_disguised_as_conflicts(self):
        self.client.raise_request_exception = False
        before = AuditLog.objects.count()
        with patch.object(Vendor, 'save', side_effect=IntegrityError('unrelated storage failure')):
            response = self.client.post('/vendor/', {'name': 'Unrelated Identity'})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(AuditLog.objects.count(), before)

    def test_conflict_audit_failure_fails_closed(self):
        Vendor.objects.create(name='Private Identity')
        self.client.raise_request_exception = False
        with patch('core.services.AuditLog.objects.create', side_effect=RuntimeError('audit unavailable')):
            response = self.client.post('/vendor/', {'name': 'private identity'})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(Vendor.objects.filter(name__iexact='Private Identity').count(), 1)

    def test_exact_conflict_has_durable_rejection_audit(self):
        Vendor.objects.create(name='Exact Identity')
        before = AuditLog.objects.count()
        response = self.client.post('/vendor/', {'name': 'Exact Identity'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(AuditLog.objects.count(), before + 1)

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
