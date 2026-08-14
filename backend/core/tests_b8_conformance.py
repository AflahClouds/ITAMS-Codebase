"""Conformance tests for the B8 Notifications and Audit baseline — second pass.

`core/tests.py` covers recipient isolation, read state, the in-app channel, the
AuditLog filter contract, audit privacy, and retention. This module covers what that
pass left unverified: the shared-facility boundary (FR-001 to FR-004), audit event
coverage (FR-014), AuditLog access (ALR-003, ALR-006), the result limit (FR-022), and
the failure boundaries (FR-011, FR-012, ALR-005).

Each test carries a `Covers:` tag naming the requirements it demonstrates; those tags
feed docs/conformance/traceability-map.md.

B8 records its gaps as prose under each requirement and as CAND observations rather
than as a numbered register, so each `expectedFailure` below cites the passage that
already describes it in `specs/004-notifications-audit-baseline/spec.md`.
"""
import unittest
from datetime import date
from unittest.mock import patch

from django.contrib.auth.models import User as AuthUser
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Location, Permission, Role, User
from assets.models import Asset
from catalog.models import Brand, Category, Model, PurchaseMode, Vendor

from .models import AuditLog, Notification, NotificationFailure
from .services import notify, notify_many


def _profile(username, codes=(), role_name=None, status="Active"):
    account = AuthUser.objects.create_user(username=username, password="test-password")
    if role_name:
        # Admin, IT Manager, and Employee are seeded by accounts migration 0002.
        role = Role.objects.get(name=role_name)
    else:
        role = Role.objects.create(name=f"{username} role")
        role.permissions.set([
            Permission.objects.get_or_create(code=c, defaults={"name": c})[0]
            for c in codes
        ])
    profile = User.objects.create(
        account=account, user_name=username, emp_id=f"EMP-{username}",
        email_id=f"{username}@example.com", role=role, status=status)
    return account, profile


def _client(username, codes=(), role_name=None):
    account, profile = _profile(username, codes, role_name)
    client = APIClient()
    client.force_authenticate(account)
    return client, profile


def _catalog():
    return dict(
        category=Category.objects.create(category_name="Laptops"),
        brand=Brand.objects.create(brand_name="Dell"),
        model=Model.objects.create(model_name="Latitude"),
    )


def _asset(asset_id, cat, **extra):
    return Asset.objects.create(
        asset_id=asset_id, tag_number=f"{asset_id}-T", serial_number=f"{asset_id}-S",
        category=cat["category"], brand=cat["brand"], model=cat["model"], **extra)


def _asset_payload(asset_id, cat):
    return {"asset_id": asset_id, "tag_number": f"{asset_id}-T",
            "serial_number": f"{asset_id}-S", "category": cat["category"].pk,
            "brand": cat["brand"].pk, "model": cat["model"].pk}


class SharedFacilityTests(TestCase):
    """B8 FR-001 and ALR-001: B8 stores what a capability hands it, and decides nothing."""

    def test_the_facility_retains_a_notification_for_the_recipient_the_capability_chose(self):
        """Covers: B8 FR-001, B8 ALR-002."""
        _, chosen = _profile("shared-chosen", ("asset_view",))
        _, other = _profile("shared-other", ("asset_view",))

        notify(chosen, "Transfer approved", link="/asset/7")

        record = Notification.objects.get(user=chosen)
        self.assertEqual(record.message, "Transfer approved")
        self.assertEqual(record.link, "/asset/7")
        self.assertFalse(Notification.objects.filter(user=other).exists())

    def test_the_facility_authorizes_nothing_of_its_own(self):
        """Covers: B8 ALR-001.

        The recipient holds no permission at all. B8 stores the record anyway: deciding
        who may trigger the action, and who should hear about it, belongs to the owning
        capability, not to the shared facility.
        """
        _, powerless = _profile("shared-powerless", ())

        notify(powerless, "You are named on a Transfer")

        self.assertEqual(Notification.objects.filter(user=powerless).count(), 1)

    def test_delivery_to_an_absent_recipient_is_a_no_op_rather_than_an_error(self):
        """Covers: B8 FR-001."""
        notify(None, "Nobody to tell")

        self.assertEqual(Notification.objects.count(), 0)


class CapabilityBoundaryTests(TestCase):
    """B8 FR-003 and FR-004: B2 and B6 actions are audited but raise no Notification."""

    def setUp(self):
        self.cat = _catalog()
        self.client_it, _ = _client(
            "bnd-it", ("asset_view", "asset_create", "asset_edit", "asset_delete"))
        _profile("bnd-manager", ("asset_delete",))

    def test_an_asset_mutation_is_audited_and_raises_no_notification(self):
        """Covers: B8 FR-003, B8 FR-014."""
        response = self.client_it.post("/asset/", _asset_payload("BND-1", self.cat),
                                       format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            AuditLog.objects.filter(module="Assets", action="Create").count(), 1)
        self.assertEqual(Notification.objects.count(), 0)

    def test_an_asset_update_and_delete_are_each_audited_without_notifying(self):
        """Covers: B8 FR-003, B8 FR-014."""
        asset = _asset("BND-2", self.cat)

        self.client_it.patch(f"/asset/{asset.pk}/", {"status": "In Storage"},
                             format="json")
        self.client_it.delete(f"/asset/{asset.pk}/")

        actions = set(AuditLog.objects.filter(module="Assets")
                      .values_list("action", flat=True))
        self.assertEqual(actions, {"Update", "Delete"})
        self.assertEqual(Notification.objects.count(), 0)

    def test_a_procurement_mutation_is_audited_and_raises_no_notification(self):
        """Covers: B8 FR-004, B8 FR-014."""
        vendor = Vendor.objects.create(name="Boundary Supplies")
        mode = PurchaseMode.objects.create(purchase_mode="Purchase")
        location = Location.objects.create(name="Boundary Store")
        asset = _asset("BND-3", self.cat)

        response = self.client_it.post("/procurement/", {
            "mode_of_purchase": mode.pk, "vendor": vendor.pk,
            "purchase_date": "2026-01-01", "invoice_date": "2026-01-02",
            "invoice_number": "INV-BND-3", "asset_ids": [asset.pk],
            # B6 FR-009 requires arrival evidence and an attestation before a purchase
            # record can be saved.
            "attested": True,
            "arrivals": [{"asset": asset.pk, "arrived_on": "2026-01-03",
                          "location": location.pk}]}, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            AuditLog.objects.filter(module="Procurement", action="Create").count(), 1)
        self.assertEqual(Notification.objects.count(), 0)


class AuditEventCoverageTests(TestCase):
    """B8 FR-014: the shared minimum of audited events, and what must stay unaudited."""

    def setUp(self):
        self.cat = _catalog()

    def test_notification_reads_create_no_audit_entries(self):
        """Covers: B8 FR-014."""
        client, profile = _client("aud-reader", ("asset_view",))
        Notification.objects.create(user=profile, message="Something happened")

        client.get("/notification/")
        client.get("/notification/unread_count/")
        client.post("/notification/mark_all_read/")

        self.assertEqual(AuditLog.objects.count(), 0)

    def test_a_failed_login_is_audited(self):
        """Covers: B8 FR-014."""
        _profile("aud-victim", ("asset_view",))

        APIClient().post("/auth/login/", {"username": "aud-victim", "password": "wrong"},
                         format="json")

        self.assertTrue(AuditLog.objects.exists())

    def test_a_catalog_master_mutation_is_audited(self):
        """Covers: B8 FR-014.

        Was gap G-a. FR-014 requires an entry for *every* successful business-data
        mutation, and a Vendor is business data: B6 protects it from deletion while
        referenced and B7 records it on every dated AMC contract.
        """
        client, _ = _client("aud-master", ("settings_access",))

        response = client.post("/vendor/", {"name": "Audited Vendor"}, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(AuditLog.objects.count(), 1)

    def test_a_rejected_audit_access_is_itself_audited(self):
        """Covers: B8 FR-014, B8 FR-016.

        Was gap G-b. FR-016: "Every allowed view/export and every rejected access
        attempt MUST create the FR-014 AuditLog entry without exposing AuditLog data to
        a rejected actor." The rejected half is the one that matters for detecting
        someone probing the audit trail.
        """
        client, _ = _client("aud-intruder", ("report_access",))

        response = client.get("/audit/")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AuditLog.objects.count(), 1)


class AuditAccessTests(TestCase):
    """B8 ALR-003 and ALR-006: who may read the audit trail, enforced at the data."""

    def setUp(self):
        AuditLog.objects.create(username="someone", action="Create", module="Assets")

    def test_an_ordinary_role_is_denied_at_the_data_boundary(self):
        """Covers: B8 ALR-003, B8 ALR-006."""
        client, _ = _client("acc-ordinary", ("asset_view", "report_access"))

        response = client.get("/audit/")

        self.assertEqual(response.status_code, 403)
        self.assertNotIn("someone", str(response.data))

    def test_an_admin_reads_the_audit_trail_globally(self):
        """Covers: B8 ALR-003, B8 FR-016."""
        client, _ = _client("acc-admin", role_name="Admin")

        response = client.get("/audit/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_an_anonymous_request_reaches_no_audit_data(self):
        """Covers: B8 ALR-003, B8 ALR-006."""
        self.assertEqual(APIClient().get("/audit/").status_code, 401)

    def test_an_it_manager_reads_the_audit_trail_globally(self):
        """Covers: B8 ALR-003, B8 FR-016.

        ALR-003's grant is to Admin **and IT Manager**. The endpoint admitted Admin
        only; both surfaces now apply the `audit_access` code, which the seed grants to
        exactly those two Roles.
        """
        client, _ = _client("acc-manager", role_name="IT Manager")

        response = client.get("/audit/")

        self.assertEqual(response.status_code, 200)


class AuditResultLimitTests(TestCase):
    """B8 FR-022: an audit view that omits evidence must say so."""

    def test_a_truncated_audit_view_discloses_the_limit_and_the_omission(self):
        """Covers: B8 FR-022.

        FR-022 names the failure directly: an audit surface that appears complete while
        omitting evidence misrepresents the record. The response now states the cap, the
        number of matching entries, and how many were left out.
        """
        AuditLog.objects.bulk_create([
            AuditLog(username="bulk", action="Create", module="Assets",
                     new_value=f"row {n}") for n in range(1100)])
        client, _ = _client("lim-admin", role_name="Admin")

        response = client.get("/audit/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["limit"], 1000)
        self.assertEqual(response.data["total"], 1100)
        self.assertEqual(response.data["omitted"], 100)
        self.assertEqual(len(response.data["results"]), 1000)


class FailureBoundaryTests(TestCase):
    """B8 FR-011, FR-012, ALR-005: what a failed audit or delivery must do."""

    def setUp(self):
        self.cat = _catalog()
        self.client_it, _ = _client(
            "fail-it", ("asset_view", "asset_create", "asset_edit"))

    def test_a_notification_failure_leaves_completed_business_work_intact(self):
        """Covers: B8 ALR-005, B8 FR-012.

        ALR-005 puts delivery outside the atomic boundary that FR-011 draws around the
        audit entry. The renewal below completes, is audited, and the operator is simply
        not told — which is the outcome the requirement asks for, because undoing a
        committed AMC decision because a message could not be stored would be worse.

        The failure is injected at the storage layer rather than at `_notify_it_managers`
        because the facility no longer lets a delivery failure reach its caller at all.
        """
        from assets.models import AmcContract
        asset = _asset("FAIL-1", self.cat)
        AmcContract.objects.create(asset=asset, start_date=date(2026, 1, 1),
                                   end_date=date(2027, 1, 1), status="Active")
        vendor = Vendor.objects.create(name="Failure Ltd")

        with patch("core.services.Notification.objects.bulk_create",
                   side_effect=RuntimeError("delivery down")):
            response = self.client_it.post(f"/asset/{asset.pk}/renew_amc/", {
                "amc_start": "2027-01-01", "amc_end": "2028-01-01",
                "vendor": vendor.pk}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AmcContract.objects.filter(asset=asset).count(), 2)
        self.assertEqual(
            AmcContract.objects.filter(asset=asset, status="Active").count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="AMC Renewed").count(), 1)
        self.assertTrue(NotificationFailure.objects.exists())

    def test_a_failed_audit_write_rejects_the_business_action(self):
        """Covers: B8 FR-011, B8 ALR-005.

        This was the shared statement of B7's U-007. Call sites write the entry either
        side of the change depending on the caller — `perform_create` logs after saving,
        `perform_destroy` logs before deleting — so the guarantee could not live in
        `log_action`. `ATOMIC_REQUESTS` makes the request the boundary, which covers
        every call site including ones not yet written.
        """
        with patch("assets.views.log_action", side_effect=RuntimeError("audit down")):
            with self.assertRaises(RuntimeError):
                self.client_it.post("/asset/", _asset_payload("FAIL-2", self.cat),
                                    format="json")

        self.assertFalse(Asset.objects.filter(asset_id="FAIL-2").exists())

    def test_a_transient_delivery_failure_is_retried_without_duplicating(self):
        """Covers: B8 FR-012."""
        _, recipient = _profile("fail-recipient", ("asset_view",))
        calls = []
        real = Notification.objects.bulk_create

        def once(rows, *args, **kwargs):
            calls.append(1)
            if len(calls) == 1:
                raise RuntimeError("storage down")
            return real(rows, *args, **kwargs)

        with patch("core.services.Notification.objects.bulk_create", side_effect=once):
            notify_many([recipient], "Retry me")

        self.assertEqual(len(calls), 2, "the failed delivery was never retried")
        self.assertEqual(Notification.objects.filter(user=recipient).count(), 1)
        self.assertFalse(NotificationFailure.objects.exists())

    def test_a_delivery_that_cannot_be_retained_stays_visible_to_an_operator(self):
        """Covers: B8 FR-012.

        Once the attempts are spent the failure must not vanish. A `NotificationFailure`
        row is that visibility — FR-012 requires the failed delivery to "remain visible
        to an operator until delivered or explicitly resolved".
        """
        _, recipient = _profile("lost-recipient", ("asset_view",))

        with patch("core.services.Notification.objects.bulk_create",
                   side_effect=RuntimeError("storage down")):
            delivered = notify_many([recipient], "You will not see this")

        self.assertEqual(delivered, [])
        self.assertEqual(Notification.objects.count(), 0)
        failure = NotificationFailure.objects.get()
        self.assertEqual(failure.recipient_id, recipient.pk)
        self.assertEqual(failure.message, "You will not see this")
        self.assertFalse(failure.resolved)
        self.assertIn("storage down", failure.error)


class ReadStateTransitionTests(TestCase):
    """B8 FR-019: `Unread` → `Read` is the only transition the surface offers."""

    def test_no_operation_returns_a_read_notification_to_unread(self):
        """Covers: B8 FR-019.

        FR-019 records the one-way transition as unverified: "nothing currently prevents
        a write returning a record to `Unread`." At the API boundary nothing offers to.
        The Notification surface is read-only apart from the two mark-read actions, so
        there is no route back — which is where the guarantee has to hold, since the
        model itself imposes none.
        """
        client, profile = _client("state-owner", ("asset_view",))
        record = Notification.objects.create(user=profile, message="Read me")
        client.post(f"/notification/{record.pk}/mark_read/")

        writes = [client.patch(f"/notification/{record.pk}/", {"status": "Unread"},
                               format="json"),
                  client.put(f"/notification/{record.pk}/", {"status": "Unread"},
                             format="json"),
                  client.post(f"/notification/{record.pk}/mark_unread/")]

        for response in writes:
            self.assertIn(response.status_code, (404, 405))
        record.refresh_from_db()
        self.assertEqual(record.status, "Read")


class ScopeIntegrityTests(TestCase):
    """B8 FR-007: the AuditLog is operational history, not physical verification."""

    def test_the_audit_record_carries_no_physical_verification_semantics(self):
        """Covers: B8 FR-007.

        FR-007 forbids treating AuditLog or Audit Trail as a physical Asset audit. The
        record holds only event fields, and writing one asserts nothing about an Asset
        having been seen or checked.
        """
        cat = _catalog()
        asset = _asset("SCP-1", cat, condition="Good")
        AuditLog.objects.create(username="someone", action="Update", module="Assets",
                                old_value="SCP-1 | In Use | Good",
                                new_value="SCP-1 | In Use | Good")

        names = {f.name for f in AuditLog._meta.get_fields()}
        self.assertEqual(
            names & {"verified", "verified_by", "physical_check", "sighted"}, set())
        asset.refresh_from_db()
        self.assertEqual(asset.condition, "Good")
