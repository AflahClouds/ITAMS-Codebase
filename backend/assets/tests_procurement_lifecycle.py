"""Feature 016 API journeys and transaction/private-storage boundary regressions."""
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.models import AuditLog

from .models import Asset, Procurement, ProcurementInvoiceVersion
from .tests_b6_conformance import _asset, _catalog, _client, _link_payload, _procurement


class ProcurementLifecycleTests(TestCase):
    def setUp(self):
        self.cat = _catalog()
        self.client = _client('lifecycle', ('asset_view', 'asset_create', 'asset_edit',
                                           'asset_delete', 'asset_custody_manage'))
        self.private = TemporaryDirectory()
        self.addCleanup(self.private.cleanup)
        field = ProcurementInvoiceVersion._meta.get_field('file')
        original = field.storage
        field.storage = FileSystemStorage(location=self.private.name)
        self.addCleanup(setattr, field, 'storage', original)

    def register(self, **extra):
        data = dict(asset_id='NEW', tag_number='NEW-T', serial_number='NEW-S',
                    category=self.cat['category'].pk, brand=self.cat['brand'].pk,
                    model=self.cat['model'].pk)
        return self.client.post('/asset/', data | extra, format='json')

    def purchase(self, *assets, **extra):
        data = dict(mode_of_purchase=self.cat['mode'].pk, vendor=self.cat['vendor'].pk,
                    purchase_date='2026-01-01', invoice_date='2026-01-02',
                    invoice_number='NEW-P') | _link_payload(self.cat, *assets) | extra
        return self.client.post('/procurement/', data, format='json')

    def read_asset(self, asset):
        response = self.client.get(f'/asset/{asset.pk}/')
        self.assertEqual(response.status_code, 200)
        return response.data

    def test_registration_starts_storage_and_rejects_explicit_available(self):
        response = self.register()
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['status'], 'In Storage')
        self.assertIsNone(response.data['procurement'])
        self.assertIsNone(response.data['custodian'])
        self.assertIsNone(response.data['department'])
        Asset.objects.all().delete()
        self.assertEqual(self.register(status='Available').status_code, 400)

    def test_model_registration_default_is_storage(self):
        self.assertEqual(_asset('DEFAULT', self.cat).status, 'In Storage')

    def test_new_batch_purchase_makes_staged_assets_available_without_invoice(self):
        assets = [_asset(name, self.cat, status='In Storage') for name in ('A', 'B')]
        response = self.purchase(*assets)
        self.assertEqual(response.status_code, 201, response.data)
        self.assertIsNone(response.data['current_invoice'])
        for asset in assets:
            data = self.read_asset(asset)
            self.assertEqual((data['status'], data['procurement']),
                             ('Available', response.data['id']))

    def test_attach_to_existing_purchase_and_metadata_preserves_other_states(self):
        proc = _procurement(self.cat)
        held = _asset('OLD', self.cat, procurement=proc, status='Under Repair')
        staged = _asset('STAGED', self.cat, status='In Storage')
        response = self.client.patch(f'/procurement/{proc.pk}/',
            _link_payload(self.cat, held, staged, link_reason='Arrival recorded'), format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(self.read_asset(staged)['status'], 'Available')
        self.assertEqual(self.read_asset(held)['status'], 'Under Repair')
        self.assertEqual(self.client.patch(f'/procurement/{proc.pk}/',
            {'po_number': 'NEW-PO'}, format='json').status_code, 200)
        self.assertEqual(self.read_asset(held)['status'], 'Under Repair')

    def test_direct_asset_link_and_unprocured_promotion_are_rejected(self):
        proc = _procurement(self.cat)
        self.assertEqual(self.register(procurement=proc.pk).status_code, 400)
        staged = _asset('STAGED', self.cat, status='In Storage')
        for change in ({'procurement': proc.pk}, {'status': 'Available'}):
            self.assertEqual(self.client.patch(f'/asset/{staged.pk}/', change,
                                              format='json').status_code, 400)
        self.assertEqual(self.read_asset(staged)['status'], 'In Storage')

    def test_protected_asset_cannot_be_newly_attached(self):
        for state in ('Assigned', 'Under Repair', 'Sold', 'Scrapped', 'Lost'):
            asset = _asset(state, self.cat, status=state)
            self.assertEqual(self.purchase(asset, invoice_number=state).status_code, 400)
            self.assertIsNone(self.read_asset(asset)['procurement'])

    def test_failed_arrival_or_denied_purchase_leaves_staged_asset_untouched(self):
        asset = _asset('STAGED', self.cat, status='In Storage')
        self.assertEqual(self.purchase(asset, arrivals=[]).status_code, 400)
        denied = _client('viewer', ('asset_view',))
        self.assertEqual(denied.post('/procurement/', {}, format='json').status_code, 403)
        self.assertEqual(self.read_asset(asset)['status'], 'In Storage')
        self.assertEqual(Procurement.objects.count(), 0)

    def test_purchase_audit_failure_rolls_back_link_status_and_purchase(self):
        asset = _asset('STAGED', self.cat, status='In Storage')
        with patch('assets.views.log_action', side_effect=RuntimeError('audit unavailable')):
            with self.assertRaisesMessage(RuntimeError, 'audit unavailable'):
                self.purchase(asset)
        data = self.read_asset(asset)
        self.assertEqual((data['status'], data['procurement']), ('In Storage', None))
        self.assertEqual(Procurement.objects.count(), 0)


class DetachBeforeDeleteTests(ProcurementLifecycleTests):
    # Reuse fixture methods, while inherited US1 cases keep each checkpoint covered.
    def test_linked_asset_deletion_is_blocked_including_archived_purchase(self):
        proc = _procurement(self.cat)
        asset = _asset('LINKED', self.cat, procurement=proc, status='Available')
        for archived in (False, True):
            proc.archived = archived
            proc.save()
            response = self.client.delete(f'/asset/{asset.pk}/')
            self.assertEqual(response.status_code, 400, response.data)
            self.assertIn('Procurement', str(response.data))
            self.assertEqual(self.read_asset(asset)['procurement'], proc.pk)

    def test_detach_requires_reason_then_retains_purchase_and_allows_separate_delete(self):
        proc = _procurement(self.cat)
        removed = _asset('REMOVED', self.cat, procurement=proc, status='Available')
        kept = _asset('KEPT', self.cat, procurement=proc, status='Available')
        url = f'/procurement/{proc.pk}/'
        response = self.client.patch(url, _link_payload(self.cat, kept), format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.read_asset(removed)['procurement'], proc.pk)

        response = self.client.patch(url,
            _link_payload(self.cat, kept, link_reason='Wrong unit on invoice'), format='json')
        self.assertEqual(response.status_code, 200, response.data)
        data = self.read_asset(removed)
        self.assertEqual((data['procurement'], data['status']), (None, 'In Storage'))
        self.assertEqual(self.read_asset(kept)['procurement'], proc.pk)
        self.assertTrue(any(row['action'] == 'Detached' and row['reason'] == 'Wrong unit on invoice'
                            for row in response.data['link_history']))
        self.assertEqual(self.client.delete(f'/asset/{removed.pk}/').status_code, 204)
        self.assertEqual(self.read_asset(kept)['procurement'], proc.pk)

    def test_protected_detach_and_edit_denial_preserve_purchase(self):
        proc = _procurement(self.cat)
        removed = _asset('PROTECTED', self.cat, procurement=proc, status='Under Repair')
        kept = _asset('KEPT', self.cat, procurement=proc, status='Available')
        payload = _link_payload(self.cat, kept, link_reason='Correction')
        self.assertEqual(self.client.patch(f'/procurement/{proc.pk}/', payload,
                                          format='json').status_code, 400)
        denied = _client('no-edit', ('asset_view',))
        self.assertEqual(denied.patch(f'/procurement/{proc.pk}/', payload,
                                     format='json').status_code, 403)
        self.assertEqual(self.read_asset(removed)['procurement'], proc.pk)


