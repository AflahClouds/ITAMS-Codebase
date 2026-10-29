"""Feature 016 API journeys and transaction/private-storage boundary regressions."""
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from core.models import AuditLog
from rest_framework.exceptions import ValidationError

from .models import Asset, Procurement, ProcurementInvoiceVersion
from .tests_b6_conformance import _asset, _catalog, _client, _link_payload, _procurement
from .serializers import AssetSerializer, ProcurementSerializer


class ProcurementLifecycleTests(TestCase):
    def setUp(self):
        self.cat = _catalog()
        self.client = _client('lifecycle', ('asset_view', 'asset_create', 'asset_edit',
                                           'asset_delete', 'asset_custody_manage'))
        self.private = TemporaryDirectory()
        self.addCleanup(self.private.cleanup)
        self.enterContext(override_settings(MEDIA_ROOT=self.private.name))
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



class PermanentReleaseTests(ProcurementLifecycleTests):
    def singleton(self):
        asset = _asset('ONLY', self.cat, status='In Storage')
        response = self.purchase(asset)
        self.assertEqual(response.status_code, 201, response.data)
        return asset, Procurement.objects.get(pk=response.data['id'])

    def test_empty_edit_explains_complete_deletion_without_mutation(self):
        asset, proc = self.singleton()
        response = self.client.patch(f'/procurement/{proc.pk}/',
            {'asset_ids': [], 'attested': True, 'link_reason': 'Release last'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('permanently delete', str(response.data).lower())
        self.assertEqual(self.read_asset(asset)['procurement'], proc.pk)

    def test_singleton_release_deletes_purchase_owned_rows_files_and_retains_audit_asset(self):
        asset, proc = self.singleton()
        invoices = []
        for version in (1, 2):
            if version == 2:
                proc.invoice_versions.update(is_current=False)
            invoices.append(ProcurementInvoiceVersion.objects.create(
                procurement=proc, file=SimpleUploadedFile(f'invoice-{version}.pdf', b'%PDF-1.4'),
                file_name=f'invoice-{version}.pdf', version=version))
        storage = invoices[0].file.storage
        names = [invoice.file.name for invoice in invoices]
        # File bytes stay until the outer request transaction commits.
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(f'/procurement/{proc.pk}/permanent-delete/', {}, format='json')
            self.assertEqual(response.status_code, 204, getattr(response, 'data', response.content))
            self.assertTrue(all(storage.exists(name) for name in names))
        self.assertTrue(all(not storage.exists(name) for name in names))
        self.assertEqual(self.client.get(f'/procurement/{proc.pk}/').status_code, 404)
        self.assertEqual(ProcurementInvoiceVersion.objects.count(), 0)
        self.assertEqual(asset.arrivals.count(), 0)
        self.assertEqual(asset.procurement_link_history.count(), 0)
        data = self.read_asset(asset)
        self.assertEqual((data['procurement'], data['status']), (None, 'In Storage'))
        audit = AuditLog.objects.get(action='Permanent Delete', module='Procurement')
        self.assertIn(proc.invoice_number, audit.old_value)
        self.assertIn(asset.asset_id, audit.new_value)
        self.assertEqual(audit.username, 'lifecycle')
        notifications = self.client.get('/notification/')
        self.assertEqual(notifications.status_code, 200)
        releases = [row for row in notifications.data if 'permanently deleted' in row['message']]
        self.assertEqual(len(releases), 1)
        self.assertEqual(releases[0]['link'], f'/asset/detail/{asset.pk}')
        self.assertEqual(self.client.delete(f'/asset/{asset.pk}/').status_code, 204)

    def test_release_denied_multi_asset_and_protected_states_preserve_data(self):
        asset, proc = self.singleton()
        url = f'/procurement/{proc.pk}/permanent-delete/'
        editor = _client('only-edit', ('asset_view', 'asset_edit'))
        self.assertEqual(editor.post(url, {}, format='json').status_code, 403)
        second = _asset('SECOND', self.cat, procurement=proc, status='Available')
        self.assertEqual(self.client.post(url, {}, format='json').status_code, 400)
        second.delete()
        for state in ('Assigned', 'Under Repair', 'Sold', 'Scrapped', 'Lost'):
            Asset.objects.filter(pk=asset.pk).update(status=state)
            self.assertEqual(self.client.post(url, {}, format='json').status_code, 400)
            self.assertEqual(self.read_asset(asset)['procurement'], proc.pk)

    def test_failed_audit_preserves_purchase_history_asset_and_private_files(self):
        asset, proc = self.singleton()
        invoice = ProcurementInvoiceVersion.objects.create(
            procurement=proc, file=SimpleUploadedFile('invoice.pdf', b'%PDF-1.4'),
            file_name='invoice.pdf', version=1)
        with self.captureOnCommitCallbacks(execute=True):
            with patch('assets.views.log_action', side_effect=RuntimeError('audit unavailable')):
                with self.assertRaisesMessage(RuntimeError, 'audit unavailable'):
                    self.client.post(f'/procurement/{proc.pk}/permanent-delete/', {}, format='json')
        self.assertTrue(invoice.file.storage.exists(invoice.file.name))
        self.assertEqual(self.read_asset(asset)['procurement'], proc.pk)
        self.assertEqual(self.read_asset(asset)['status'], 'Available')
        self.assertEqual(proc.arrivals.count(), 1)
        self.assertEqual(proc.link_history.count(), 1)
        self.assertEqual(proc.invoice_versions.count(), 1)

    def test_ordinary_archive_retains_asset_association_and_purchase(self):
        asset, proc = self.singleton()
        self.assertEqual(self.client.delete(f'/procurement/{proc.pk}/').status_code, 204)
        self.assertEqual(self.read_asset(asset)['procurement'], proc.pk)
        self.assertTrue(self.client.get(f'/procurement/{proc.pk}/').data['archived'])

    def test_stale_asset_form_cannot_restore_a_link_after_release(self):
        asset, proc = self.singleton()
        asset.refresh_from_db()
        form = AssetSerializer(asset, data={'notes': 'Earlier form', 'procurement': proc.pk}, partial=True)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(self.client.post(f'/procurement/{proc.pk}/permanent-delete/', {}, format='json').status_code, 204)
        with self.assertRaises(ValidationError):
            form.save()
        data = self.read_asset(asset)
        self.assertEqual((data['procurement'], data['status']), (None, 'In Storage'))

    def test_stale_purchase_selection_cannot_reclaim_an_asset(self):
        proc = _procurement(self.cat)
        kept = _asset('KEPT', self.cat, procurement=proc, status='Available')
        staged = _asset('STAGED', self.cat, status='In Storage')
        form = ProcurementSerializer(proc, data=_link_payload(self.cat, kept, staged), partial=True)
        self.assertTrue(form.is_valid(), form.errors)
        other = self.purchase(staged)
        self.assertEqual(other.status_code, 201, other.data)
        with self.assertRaises(ValidationError):
            form.save()
        self.assertEqual(self.read_asset(staged)['procurement'], other.data['id'])
        self.assertEqual(self.read_asset(kept)['procurement'], proc.pk)

    def test_detached_asset_with_returned_custody_history_still_cannot_be_deleted(self):
        from accounts.models import User
        asset, proc = self.singleton()
        holder = User.objects.get(user_name='lifecycle')
        issued = self.client.post('/assignment/', {'asset': asset.pk, 'user': holder.pk}, format='json')
        self.assertEqual(issued.status_code, 201, issued.data)
        returned = self.client.post(f"/assignment/{issued.data['id']}/take-back/",
                                   {'condition': 'Good'}, format='json')
        self.assertEqual(returned.status_code, 200, returned.data)
        kept = _asset('KEPT', self.cat, procurement=proc, status='Available')
        self.assertEqual(self.client.patch(f'/procurement/{proc.pk}/',
            _link_payload(self.cat, kept, link_reason='Correct invoice'), format='json').status_code, 200)
        self.assertEqual(self.read_asset(asset)['status'], 'In Storage')
        response = self.client.delete(f'/asset/{asset.pk}/')
        self.assertEqual(response.status_code, 400)
        self.assertIn('custody history', str(response.data))
