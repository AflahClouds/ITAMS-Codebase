"""Conformance tests for the B8 Notifications and AuditLog baseline.

Each test carries a `Covers:` tag naming the requirements it demonstrates; those tags
feed docs/conformance/traceability-map.md.

Requirements the implementation does not yet satisfy are written here as
`expectedFailure` rather than omitted. That way the requirement is documented and
executable, the suite stays green against known gaps, and the moment someone closes a
gap the runner reports an unexpected success — which is the signal to remove the marker
and record the conformance change.
"""
import unittest

from django.contrib.auth.models import User as AuthUser
from django.core import mail
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.models import Permission, Role, User
from assets.models import Asset
from catalog.models import Brand, Category, Model

from .models import AuditLog, Notification
from .services import client_ip, log_action, notify, notify_many


def _profile(username, codes=(), role_name=None):
    account = AuthUser.objects.create_user(username=username, password="test-password")
    if role_name:
        role = Role.objects.get(name=role_name)
    else:
        role = Role.objects.create(name=f"{username} role")
        role.permissions.set([
            Permission.objects.get_or_create(code=c, defaults={"name": c})[0] for c in codes
        ])
    profile = User.objects.create(
        account=account, user_name=username, emp_id=f"EMP-{username}",
        email_id=f"{username}@example.com", role=role)
    return account, profile


def _client_for(account):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=account).key}")
    return client


class NotificationRecipientIsolationTests(TestCase):
    """A recipient reaches their own Notifications and no one else's."""

    def setUp(self):
        self.account, self.profile = _profile("recipient")
        self.other_account, self.other = _profile("bystander")
        self.client_a = _client_for(self.account)

    def test_a_recipient_reads_only_their_own_notifications(self):
        """Covers: B8 ALR-002, B8 FR-020."""
        notify(self.profile, "yours")
        notify(self.other, "theirs")

        messages = [row["message"] for row in self.client_a.get("/notification/").data]

        self.assertEqual(messages, ["yours"])

    def test_the_unread_count_counts_only_the_readers_own_unread_records(self):
        """Covers: B8 FR-019, B8 ALR-002."""
        notify(self.profile, "mine one")
        notify(self.profile, "mine two")
        notify(self.other, "not mine")

        self.assertEqual(self.client_a.get("/notification/unread_count/").data["count"], 2)

    def test_a_recipient_cannot_mark_another_users_notification_read(self):
        """Covers: B8 ALR-002."""
        theirs = Notification.objects.create(user=self.other, message="theirs")

        response = self.client_a.post(f"/notification/{theirs.pk}/mark_read/")

        self.assertEqual(response.status_code, 404)
        theirs.refresh_from_db()
        self.assertEqual(theirs.status, "Unread")

    def test_an_empty_notification_list_is_a_normal_outcome(self):
        """Covers: B8 FR-020."""
        response = self.client_a.get("/notification/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.data), [])


class NotificationReadStateTests(TestCase):
    """B8 FR-019: two states, a one-way transition, and an idempotent re-mark."""

    def setUp(self):
        self.account, self.profile = _profile("reader")
        self.client_a = _client_for(self.account)

    def test_a_notification_is_created_unread(self):
        """Covers: B8 FR-019."""
        notify(self.profile, "fresh")

        self.assertEqual(Notification.objects.get().status, "Unread")

    def test_marking_read_moves_unread_to_read(self):
        """Covers: B8 FR-019."""
        row = Notification.objects.create(user=self.profile, message="m")

        self.client_a.post(f"/notification/{row.pk}/mark_read/")

        row.refresh_from_db()
        self.assertEqual(row.status, "Read")

    def test_marking_an_already_read_notification_is_idempotent(self):
        """Covers: B8 FR-019."""
        row = Notification.objects.create(user=self.profile, message="m", status="Read")

        response = self.client_a.post(f"/notification/{row.pk}/mark_read/")

        self.assertEqual(response.status_code, 200)
        row.refresh_from_db()
        self.assertEqual(row.status, "Read")

    def test_mark_all_read_clears_the_unread_count(self):
        """Covers: B8 FR-019."""
        for i in range(3):
            notify(self.profile, f"m{i}")

        self.client_a.post("/notification/mark_all_read/")

        self.assertEqual(self.client_a.get("/notification/unread_count/").data["count"], 0)

    @unittest.expectedFailure
    def test_the_time_a_notification_became_read_is_retained(self):
        """Covers: B8 FR-019, B8 FR-017.

        Known gap. `Notification` stores a creation time but no read time, so FR-017's
        "Read Notifications MUST be removed 90 days after becoming Read" cannot be
        evaluated. Recorded under FR-019 in the specification.
        """
        row = Notification.objects.create(user=self.profile, message="m")
        self.client_a.post(f"/notification/{row.pk}/mark_read/")
        row.refresh_from_db()

        self.assertTrue(any("read" in f.name and "date" in f.get_internal_type().lower()
                            for f in Notification._meta.get_fields()))


class NotificationChannelTests(TestCase):
    """B8 FR-008: in-app only in this version; email is deferred."""

    def test_delivering_a_notification_sends_no_email(self):
        """Covers: B8 FR-008."""
        _, profile = _profile("channel")
        mail.outbox = []

        notify(profile, "in-app only")

        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_group_delivery_sends_no_email_either(self):
        """Covers: B8 FR-008."""
        _, a = _profile("group-a")
        _, b = _profile("group-b")
        mail.outbox = []

        notify_many([a, b], "in-app only")

        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(len(mail.outbox), 0)


class NotificationSideEffectTests(TestCase):
    """B8 ALR-004: shared delivery never changes capability state on its own."""

    def test_delivering_a_notification_changes_no_asset_state(self):
        """Covers: B8 ALR-004, B8 ALR-001."""
        category = Category.objects.create(category_name="C")
        brand = Brand.objects.create(brand_name="B")
        model = Model.objects.create(model_name="M")
        asset = Asset.objects.create(
            asset_id="B8-A", tag_number="B8-T", serial_number="B8-S",
            category=category, brand=brand, model=model, status="Available")
        _, profile = _profile("side-effect")
        before = (asset.status, asset.custodian_id, asset.department_id, asset.condition)

        notify(profile, f"Asset {asset.asset_id} changed", link=f"/asset/{asset.id}")

        asset.refresh_from_db()
        self.assertEqual(before,
                         (asset.status, asset.custodian_id, asset.department_id, asset.condition))


class AuditLogFilterContractTests(TestCase):
    """B8 FR-021: the accepted filter contract."""

    def setUp(self):
        account = AuthUser.objects.create_user(username="audit-admin", password="x")
        User.objects.create(account=account, user_name="audit admin", emp_id="EMP-aa",
                            email_id="aa@example.com", role=Role.objects.get(name="Admin"))
        self.client_admin = _client_for(account)
        for module, username in (("Assets", "alice"), ("Assets", "BOB"), ("Auth", "alice")):
            AuditLog.objects.create(action="Act", module=module, username=username)

    def test_module_filtering_is_an_exact_match(self):
        """Covers: B8 FR-021."""
        rows = self.client_admin.get("/audit/", {"module": "Assets"}).data

        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r["module"] == "Assets" for r in rows))

    def test_username_filtering_is_case_insensitive_and_partial(self):
        """Covers: B8 FR-021."""
        rows = self.client_admin.get("/audit/", {"username": "bo"}).data

        self.assertEqual([r["username"] for r in rows], ["BOB"])

    def test_supplying_both_filters_narrows_to_entries_satisfying_both(self):
        """Covers: B8 FR-021."""
        rows = self.client_admin.get("/audit/", {"module": "Auth", "username": "alice"}).data

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["module"], "Auth")

    def test_results_are_ordered_newest_first(self):
        """Covers: B8 FR-021."""
        dates = [r["date"] for r in self.client_admin.get("/audit/").data]

        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_a_filter_matching_nothing_returns_empty_rather_than_everything(self):
        """Covers: B8 FR-021."""
        rows = self.client_admin.get("/audit/", {"module": "NoSuchModule"}).data

        self.assertEqual(list(rows), [])


class AuditLogPrivacyTests(TestCase):
    """B8 FR-015: minimization, and no credentials in any field."""

    def test_a_password_change_records_no_credential_material(self):
        """Covers: B8 FR-015."""
        account = AuthUser.objects.create_user(username="pw-privacy", password="Str0ng-Passphrase!")
        User.objects.create(account=account, user_name="pw", emp_id="EMP-pwp",
                            email_id="pwp@example.com")
        client = APIClient()
        client.force_authenticate(account)

        client.post("/auth/change-password/", {
            "old_password": "Str0ng-Passphrase!",
            "new_password": "quartz-lantern-98-oxide"}, format="json")

        blob = " ".join(
            f"{e.action} {e.module} {e.old_value} {e.new_value}" for e in AuditLog.objects.all())
        for secret in ("Str0ng-Passphrase!", "quartz-lantern-98-oxide", "pbkdf2"):
            self.assertNotIn(secret, blob)

    def test_a_failed_login_records_the_attempt_without_the_password(self):
        """Covers: B8 FR-014, B8 FR-015."""
        AuthUser.objects.create_user(username="known", password="Str0ng-Passphrase!")

        APIClient().post("/auth/login/",
                         {"username": "known", "password": "wrong-secret-value"}, format="json")

        entry = AuditLog.objects.get(action="Login Failed")
        self.assertNotIn("wrong-secret-value", f"{entry.old_value} {entry.new_value}")


class AuditLogSourceAddressTests(TestCase):
    """B8 FR-023: a source address is indicative, never authoritative."""

    @unittest.expectedFailure
    def test_a_forwarded_header_is_not_trusted_from_an_untrusted_peer(self):
        """Covers: B8 FR-023.

        Known gap. `client_ip` reads `HTTP_X_FORWARDED_FOR` unconditionally, so a caller
        not behind a trusted proxy can choose the address recorded against their own
        actions. Recorded as a conformance gap under FR-023.
        """
        class _Request:
            META = {"HTTP_X_FORWARDED_FOR": "203.0.113.9", "REMOTE_ADDR": "10.0.0.5"}

        self.assertEqual(client_ip(_Request()), "10.0.0.5")


class AuditLogRetentionTests(TestCase):
    """B8 FR-017: retention periods for AuditLog, source IP, and Notifications."""

    def test_notifications_are_removed_when_their_recipient_is_deleted(self):
        """Covers: B8 FR-017.

        This half of FR-017 conforms: the cascade on `Notification.user` removes every
        Notification addressed to a deleted User.
        """
        _, profile = _profile("to-delete")
        notify(profile, "addressed to a User about to be deleted")
        self.assertEqual(Notification.objects.count(), 1)

        profile.delete()

        self.assertEqual(Notification.objects.count(), 0)

    def test_an_audit_entry_outlives_its_actor(self):
        """Covers: B8 FR-017.

        FR-017 requires AuditLog actor identity to remain minimized and readable until
        the entry's two-year limit, so deleting a User must not delete their audit
        history. `AuditLog.user` is SET_NULL and the username snapshot is retained.
        """
        _, profile = _profile("audited-actor")
        AuditLog.objects.create(user=profile, username="audited-actor",
                                action="Act", module="Assets")

        profile.delete()

        entry = AuditLog.objects.get()
        self.assertIsNone(entry.user_id)
        self.assertEqual(entry.username, "audited-actor")

    @unittest.expectedFailure
    def test_expired_records_are_purged_on_their_retention_schedule(self):
        """Covers: B8 FR-017.

        Known gap. FR-017 sets four retention periods — AuditLog 2 years, source IP
        6 months, Read Notifications 90 days, Unread Notifications 1 year — and no
        scheduled removal implements any of them. `core.scheduler` registers only the
        Warranty/AMC expiry sweep. Nothing here can pass until a purge job exists.
        """
        import io

        from . import scheduler

        source = io.open(scheduler.__file__, encoding="utf-8").read().lower()
        self.assertIn("retention", source)
