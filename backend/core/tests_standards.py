"""Feature 015 required audit API regressions (FR-004–006)."""
from unittest.mock import patch

from django.test import TestCase

from .models import AuditLog, Setting
from .tests_b8_conformance import _client


class DirectAuditReadTests(TestCase):
    def setUp(self):
        self.client, _ = _client('direct-reader', ('audit_access',))
        self.event = AuditLog.objects.create(username='private-actor', action='Private event',
                                             module='PrivateModule', new_value='protected payload',
                                             ip_address='203.0.113.91')

    def test_list_filtered_empty_and_detail_add_exactly_one_private_access_audit(self):
        for url in ('/audit/', '/audit/?module=PrivateModule', '/audit/?module=NoMatchingModule',
                    f'/audit/{self.event.pk}/'):
            with self.subTest(url=url):
                before = AuditLog.objects.count()
                response = self.client.get(url, REMOTE_ADDR='198.51.100.8',
                                           HTTP_X_FORWARDED_FOR='spoofed')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(AuditLog.objects.count(), before + 1)
                audit = AuditLog.objects.latest('pk')
                self.assertEqual(audit.username, 'direct-reader')
                self.assertEqual(audit.module, 'Audit')
                self.assertIn('Access', audit.action)
                self.assertEqual(audit.ip_address, '198.51.100.8')
                self.assertNotIn('protected payload', audit.old_value + audit.new_value)
                self.assertNotIn('203.0.113.91', audit.old_value + audit.new_value)
                self.assertNotIn('spoofed', audit.old_value + audit.new_value)

    def test_required_access_audit_failure_exposes_no_payload(self):
        self.client.raise_request_exception = False
        for url in ('/audit/', f'/audit/{self.event.pk}/'):
            with self.subTest(url=url), patch('core.views.log_action', side_effect=RuntimeError('audit unavailable')):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 500)
                self.assertNotIn(b'protected payload', response.content)

    def test_limit_and_existing_denial_remain(self):
        AuditLog.objects.bulk_create([AuditLog(action='Prior', module='Limit') for _ in range(1001)])
        response = self.client.get('/audit/?module=Limit')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total'], 1001)
        self.assertEqual(response.data['omitted'], 1)
        self.assertEqual(len(response.data['results']), 1000)
        denied, _ = _client('direct-denied', ('asset_view',))
        before = AuditLog.objects.count()
        self.assertEqual(denied.get('/audit/').status_code, 403)
        self.assertEqual(AuditLog.objects.count(), before + 1)
        self.assertEqual(AuditLog.objects.latest('pk').action, 'Audit Access Denied')
