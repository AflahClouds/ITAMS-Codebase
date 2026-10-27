from unittest.mock import patch
from django.test import TestCase
from .models import AuditLog, Setting
from .tests_b8_conformance import _client

class SettingMutationTests(TestCase):
    def setUp(self):
        self.client, _ = _client('setting-admin', role_name='Admin')
        self.key = 'standards_secret_key'
        self.setting = Setting.objects.create(key=self.key, value='old-secret')

    def mutate(self, method):
        url = '/setting/' if method in ('post', 'create') else f'/setting/{self.setting.pk}/'
        verb = 'post' if method == 'create' else method
        key = 'standards_created_key' if method == 'create' else self.key
        return getattr(self.client, verb)(url, {'key': key, 'value': 'new-secret'}, format='json')

    def test_all_supported_mutations_audit_once_without_setting_values(self):
        for method in ('create', 'post', 'put', 'patch', 'delete'):
            with self.subTest(method=method):
                before = AuditLog.objects.count()
                response = self.mutate(method)
                self.assertIn(response.status_code, (200, 201, 204))
                self.assertEqual(AuditLog.objects.count(), before + 1)
                audit = AuditLog.objects.latest('pk')
                self.assertEqual(audit.username, 'setting-admin')
                self.assertEqual(audit.module, 'Settings')
                self.assertIn('standards_', audit.old_value + audit.new_value)
                self.assertNotIn('old-secret', audit.old_value + audit.new_value)
                self.assertNotIn('new-secret', audit.old_value + audit.new_value)

    def test_required_audit_failure_rolls_back_every_mutation(self):
        self.client.raise_request_exception = False
        for method in ('create', 'post', 'put', 'patch', 'delete'):
            with self.subTest(method=method), patch('core.views.log_action', side_effect=RuntimeError('audit unavailable')):
                response = self.mutate(method)
                self.assertEqual(response.status_code, 500)
                self.setting.refresh_from_db()
                self.assertEqual(self.setting.value, 'old-secret')
                self.assertFalse(Setting.objects.filter(key='standards_created_key').exists())

    def test_nonadmin_mutations_remain_denied(self):
        self.client, _ = _client('setting-denied', ('settings_access',))
        for method in ('create', 'post', 'put', 'patch', 'delete'):
            with self.subTest(method=method):
                self.assertEqual(self.mutate(method).status_code, 403)
        self.setting.refresh_from_db()
        self.assertEqual(self.setting.value, 'old-secret')
