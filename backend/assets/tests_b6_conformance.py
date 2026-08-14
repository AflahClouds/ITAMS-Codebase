"""Conformance tests for the B6 Procurement, Vendor, and Catalog Masters baseline.

Each test carries a `Covers:` tag naming the requirements it demonstrates; those tags
feed docs/conformance/traceability-map.md.

B6 carried no conformance-gap register before this suite. The `expectedFailure` cases it
introduced created one — U-008 to U-015 in
`specs/002-procurement-vendor-catalog-baseline/spec.md` — and all eight are now closed,
so these tests assert the required behavior directly.
"""
from datetime import date, timedelta

from django.contrib.auth.models import User as AuthUser
from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Location, Permission, Role, User
from catalog.models import Brand, Category, Model, PurchaseMode, Vendor

from .models import (Asset, Procurement, ProcurementArrival, ProcurementAssetLink,
                     ServiceRecord)


def _client(username, codes=()):
    account = AuthUser.objects.create_user(username=username, password="test-password")
    role = Role.objects.create(name=f"{username} role")
    role.permissions.set([
        Permission.objects.get_or_create(code=c, defaults={"name": c})[0] for c in codes
    ])
    User.objects.create(account=account, user_name=username, emp_id=f"EMP-{username}",
                        email_id=f"{username}@example.com", role=role)
    client = APIClient()
    client.force_authenticate(account)
    return client


def _catalog():
    brand = Brand.objects.create(brand_name="Dell")
    return dict(
        category=Category.objects.create(category_name="Laptops"),
        brand=brand,
        model=Model.objects.create(model_name="Latitude", brand=brand),
        mode=PurchaseMode.objects.create(purchase_mode="Purchase"),
        vendor=Vendor.objects.create(name="Acme Supplies"),
        location=Location.objects.create(name="Head Office B6"),
    )


def _procurement(cat, invoice="INV-001", **extra):
    return Procurement.objects.create(
        mode_of_purchase=cat["mode"], vendor=cat["vendor"],
        purchase_date=date(2026, 1, 1), invoice_date=date(2026, 1, 2),
        invoice_number=invoice, **extra)


def _asset(asset_id, cat, **extra):
    return Asset.objects.create(
        asset_id=asset_id, tag_number=f"{asset_id}-T", serial_number=f"{asset_id}-S",
        category=cat["category"], brand=cat["brand"], model=cat["model"], **extra)


def _arrivals(cat, *assets):
    """The arrival evidence FR-009 requires for each linked Asset."""
    return [{"asset": asset.pk, "arrived_on": "2026-01-03",
             "location": cat["location"].pk} for asset in assets]


def _link_payload(cat, *assets, **extra):
    payload = {"asset_ids": [a.pk for a in assets], "attested": True,
               "arrivals": _arrivals(cat, *assets)}
    payload.update(extra)
    return payload


class VendorIdentityTests(TestCase):
    """B6 FR-003: one managed Vendor identity, shared rather than duplicated."""

    def setUp(self):
        self.cat = _catalog()

    def test_procurement_references_a_managed_vendor_not_free_text(self):
        """Covers: B6 FR-003, B6 FR-004."""
        proc = _procurement(self.cat)

        self.assertEqual(proc.vendor, self.cat["vendor"])
        self.assertIsInstance(proc.vendor, Vendor)

    def test_one_vendor_serves_both_procurement_and_service_record(self):
        """Covers: B6 FR-003."""
        proc = _procurement(self.cat)
        asset = _asset("VEN-1", self.cat, procurement=proc)
        record = ServiceRecord.objects.create(asset=asset, vendor=self.cat["vendor"])

        self.assertEqual(proc.vendor_id, record.vendor_id)
        self.assertEqual(Vendor.objects.filter(name="Acme Supplies").count(), 1)

    def test_vendor_contact_details_are_optional_and_outside_identity(self):
        """Covers: B6 FR-019."""
        bare = Vendor.objects.create(name="Contactless Ltd")

        self.assertEqual((bare.contact_person, bare.phone, bare.email), ("", "", ""))


class MasterIdentityTests(TestCase):
    """B6 FR-019 and FR-020: what makes a master record the same record."""

    def test_each_master_type_rejects_a_duplicate_name(self):
        """Covers: B6 FR-019."""
        brand = Brand.objects.create(brand_name="Shared")
        cases = (
            (Category, {"category_name": "Dup"}),
            (Brand, {"brand_name": "Dup"}),
            (Model, {"model_name": "Dup", "brand": brand}),
            (PurchaseMode, {"purchase_mode": "Dup"}),
            (Vendor, {"name": "Dup"}),
        )
        for cls, kwargs in cases:
            with self.subTest(model=cls.__name__):
                cls.objects.create(**kwargs)
                with self.assertRaises(IntegrityError):
                    with transaction.atomic():
                        cls.objects.create(**kwargs)

    def test_master_names_are_compared_case_insensitively_after_trimming(self):
        """Covers: B6 FR-019.

        FR-019 makes the name the identity, so "Acme", "acme", and "  ACME  " are one
        supplier typed carelessly rather than three suppliers.
        """
        Vendor.objects.create(name="Acme")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Vendor.objects.create(name="  ACME  ")

    def test_a_stored_name_keeps_its_display_text_but_loses_stray_whitespace(self):
        """Covers: B6 FR-019.

        Only the comparison is normalized. The operator's capitalisation is theirs to
        choose and is preserved exactly.
        """
        vendor = Vendor.objects.create(name="  Acme   Supply  Co  ")
        vendor.refresh_from_db()

        self.assertEqual(vendor.name, "Acme Supply Co")

    def test_a_model_belongs_to_exactly_one_brand(self):
        """Covers: B6 FR-020."""
        brand = Brand.objects.create(brand_name="Lenovo")
        model = Model.objects.create(model_name="ThinkPad", brand=brand)

        self.assertEqual(model.brand, brand)
        self.assertEqual(str(model), "Lenovo ThinkPad")

    def test_the_same_model_name_may_exist_under_two_brands(self):
        """Covers: B6 FR-020.

        Identity is the pair. Two manufacturers may both sell a "Pro 14", and forcing
        the name to be globally unique would make the second one unrecordable.
        """
        first = Brand.objects.create(brand_name="Alpha")
        second = Brand.objects.create(brand_name="Beta")

        Model.objects.create(model_name="Pro 14", brand=first)
        Model.objects.create(model_name="Pro 14", brand=second)

        self.assertEqual(Model.objects.filter(model_name="Pro 14").count(), 2)

    def test_a_brand_cannot_be_deleted_while_a_model_names_it(self):
        """Covers: B6 FR-020, B6 FR-007."""
        from django.db.models import ProtectedError
        brand = Brand.objects.create(brand_name="Protected")
        Model.objects.create(model_name="Held", brand=brand)

        with self.assertRaises(ProtectedError):
            brand.delete()


class ProcurementAssetLinkTests(TestCase):
    """B6 FR-012 and FR-013: linkage cardinality, and the trail a change leaves."""

    def setUp(self):
        self.cat = _catalog()
        self.client_it = _client("proc-it", ("asset_view", "asset_create", "asset_edit"))

    def test_an_asset_holds_at_most_one_current_procurement(self):
        """Covers: B6 FR-013."""
        first = _procurement(self.cat, invoice="INV-A")
        second = _procurement(self.cat, invoice="INV-B")
        asset = _asset("LINK-1", self.cat, procurement=first)

        response = self.client_it.patch(f"/procurement/{second.pk}/",
                                        _link_payload(self.cat, asset), format="json")

        self.assertEqual(response.status_code, 400)
        asset.refresh_from_db()
        self.assertEqual(asset.procurement_id, first.pk)

    def test_linking_an_unlinked_asset_succeeds(self):
        """Covers: B6 FR-013."""
        proc = _procurement(self.cat)
        asset = _asset("LINK-2", self.cat)

        response = self.client_it.patch(f"/procurement/{proc.pk}/",
                                        _link_payload(self.cat, asset), format="json")

        self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.procurement_id, proc.pk)

    def test_a_procurement_cannot_be_left_without_any_asset(self):
        """Covers: B6 FR-013.

        FR-013 bounds the link both ways. Without the lower bound a Procurement can be
        emptied and left describing nothing.
        """
        proc = _procurement(self.cat)
        asset = _asset("LINK-3", self.cat, procurement=proc)

        response = self.client_it.patch(
            f"/procurement/{proc.pk}/",
            {"asset_ids": [], "attested": True}, format="json")

        self.assertEqual(response.status_code, 400)
        asset.refresh_from_db()
        self.assertEqual(asset.procurement_id, proc.pk)

    def test_attaching_an_asset_records_who_did_it_and_why(self):
        """Covers: B6 FR-012."""
        proc = _procurement(self.cat)
        asset = _asset("HIST-1", self.cat)

        self.client_it.patch(
            f"/procurement/{proc.pk}/",
            _link_payload(self.cat, asset, link_reason="Invoice covers this unit"),
            format="json")

        entry = ProcurementAssetLink.objects.get(procurement=proc, asset=asset)
        self.assertEqual(entry.action, ProcurementAssetLink.ATTACHED)
        self.assertEqual(entry.reason, "Invoice covers this unit")
        self.assertIsNotNone(entry.actor)

    def test_detaching_an_asset_records_a_reason_and_a_history_entry(self):
        """Covers: B6 FR-012.

        FR-012 requires the trail to survive the change: after a detach, the Asset no
        longer points at the purchase, so the history entry is the only thing that says
        it ever did.
        """
        proc = _procurement(self.cat)
        kept = _asset("HIST-2", self.cat, procurement=proc)
        dropped = _asset("HIST-3", self.cat, procurement=proc)

        response = self.client_it.patch(
            f"/procurement/{proc.pk}/",
            _link_payload(self.cat, kept, link_reason="Wrong unit on the invoice"),
            format="json")

        self.assertEqual(response.status_code, 200)
        dropped.refresh_from_db()
        self.assertIsNone(dropped.procurement_id)
        entry = ProcurementAssetLink.objects.get(
            asset=dropped, action=ProcurementAssetLink.DETACHED)
        self.assertEqual(entry.reason, "Wrong unit on the invoice")
        self.assertEqual(entry.previous_procurement_id, proc.pk)
        self.assertIsNotNone(entry.actor)


class ProcurementArrivalTests(TestCase):
    """B6 FR-009: physical arrival is a precondition, enforced not assumed."""

    def setUp(self):
        self.cat = _catalog()
        self.client_it = _client("proc-arrival", ("asset_view", "asset_create", "asset_edit"))

    def _payload(self, asset, **extra):
        payload = {
            "mode_of_purchase": self.cat["mode"].pk, "vendor": self.cat["vendor"].pk,
            "purchase_date": "2026-01-01", "invoice_date": "2026-01-02",
            "invoice_number": "INV-ARR", "asset_ids": [asset.pk],
        }
        payload.update(extra)
        return payload

    def test_saving_a_procurement_requires_an_arrival_record_and_attestation(self):
        """Covers: B6 FR-009.

        Decision C7 resolved in favour of the system enforcing this rather than trusting
        that whoever typed the invoice had the goods in front of them.
        """
        asset = _asset("ARR-1", self.cat)

        response = self.client_it.post("/procurement/", self._payload(asset),
                                       format="json")

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Procurement.objects.filter(invoice_number="INV-ARR").exists())

    def test_an_arrival_without_the_attestation_is_still_refused(self):
        """Covers: B6 FR-009."""
        asset = _asset("ARR-2", self.cat)

        response = self.client_it.post(
            "/procurement/",
            self._payload(asset, arrivals=_arrivals(self.cat, asset)), format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("attested", response.data)

    def test_an_attested_arrival_records_its_date_location_and_attester(self):
        """Covers: B6 FR-009."""
        asset = _asset("ARR-3", self.cat)

        response = self.client_it.post(
            "/procurement/",
            self._payload(asset, attested=True, arrivals=_arrivals(self.cat, asset)),
            format="json")

        self.assertEqual(response.status_code, 201)
        arrival = ProcurementArrival.objects.get(asset=asset)
        self.assertEqual(arrival.arrived_on, date(2026, 1, 3))
        self.assertEqual(arrival.location_id, self.cat["location"].pk)
        self.assertIsNotNone(arrival.attested_by)
        self.assertIsNotNone(arrival.attested_at)


class ProcurementIdentityTests(TestCase):
    """B6 FR-017: invoice and PO identity."""

    def setUp(self):
        self.cat = _catalog()

    def test_an_invoice_number_is_not_reused_for_the_same_vendor(self):
        """Covers: B6 FR-017."""
        _procurement(self.cat, invoice="INV-UNIQUE")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                _procurement(self.cat, invoice="INV-UNIQUE")

    def test_the_same_invoice_number_is_allowed_for_a_different_vendor(self):
        """Covers: B6 FR-017.

        Invoice numbers are the supplier's, not ours. Two suppliers can each issue an
        invoice numbered "1", and a global constraint makes the second unrecordable.
        """
        other = Vendor.objects.create(name="Other Supplier")
        _procurement(self.cat, invoice="1")

        Procurement.objects.create(
            mode_of_purchase=self.cat["mode"], vendor=other,
            purchase_date=date(2026, 1, 1), invoice_date=date(2026, 1, 2),
            invoice_number="1")

        self.assertEqual(Procurement.objects.filter(invoice_number="1").count(), 2)

    def test_a_purchase_order_number_is_globally_unique_when_present(self):
        """Covers: B6 FR-017.

        A PO number is ours rather than the supplier's, so it is unique across the
        system.
        """
        _procurement(self.cat, invoice="INV-PO-1", po_number="PO-1")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                _procurement(self.cat, invoice="INV-PO-2", po_number="PO-1")

    def test_several_procurements_may_omit_the_purchase_order_number(self):
        """Covers: B6 FR-017.

        The PO number is optional, so the uniqueness rule must not turn "absent" into a
        value that collides with itself.
        """
        _procurement(self.cat, invoice="INV-NO-PO-1")
        _procurement(self.cat, invoice="INV-NO-PO-2")

        self.assertEqual(Procurement.objects.filter(po_number=None).count(), 2)


class ProcurementDateRuleTests(TestCase):
    """B6 FR-010: required dates and their ordering."""

    def setUp(self):
        self.cat = _catalog()
        self.client_it = _client("proc-dates", ("asset_view", "asset_create", "asset_edit"))

    def _post(self, asset, **dates):
        payload = {
            "mode_of_purchase": self.cat["mode"].pk, "vendor": self.cat["vendor"].pk,
            "invoice_number": f"INV-{asset.asset_id}", "asset_ids": [asset.pk],
            "attested": True, "arrivals": _arrivals(self.cat, asset),
        }
        payload.update(dates)
        return self.client_it.post("/procurement/", payload, format="json")

    def test_a_purchase_date_after_the_invoice_date_is_rejected(self):
        """Covers: B6 FR-010."""
        asset = _asset("DATE-1", self.cat)

        response = self._post(asset, purchase_date="2026-06-01",
                              invoice_date="2026-01-01")

        self.assertEqual(response.status_code, 400)

    def test_a_future_purchase_date_is_rejected(self):
        """Covers: B6 FR-010.

        A completed purchase cannot have been made after the moment it was recorded.
        """
        asset = _asset("DATE-2", self.cat)
        ahead = (date.today() + timedelta(days=30)).isoformat()

        response = self._post(asset, purchase_date=ahead, invoice_date=ahead)

        self.assertEqual(response.status_code, 400)

    def test_dates_in_the_accepted_order_are_recorded(self):
        """Covers: B6 FR-010, B6 FR-004."""
        asset = _asset("DATE-3", self.cat)

        response = self._post(asset, purchase_date="2026-01-01",
                              invoice_date="2026-01-02")

        self.assertEqual(response.status_code, 201)


class ProcurementRetentionTests(TestCase):
    """B6 FR-011: removal archives a purchase record rather than destroying it."""

    def setUp(self):
        self.cat = _catalog()
        self.client_it = _client("proc-retain",
                                 ("asset_view", "asset_create", "asset_edit", "asset_delete"))

    def test_removing_a_procurement_archives_it_rather_than_deleting_it(self):
        """Covers: B6 FR-011.

        The invoice, the dates, the Vendor, and the link history are the evidence that
        the organization bought the thing; a mistaken click must not erase it.
        """
        proc = _procurement(self.cat)
        _asset("ARCH-1", self.cat, procurement=proc)

        self.client_it.delete(f"/procurement/{proc.pk}/")

        proc.refresh_from_db()
        self.assertTrue(proc.archived)
        self.assertIsNotNone(proc.archived_at)
        self.assertEqual(proc.invoice_number, "INV-001")

    def test_an_archived_procurement_leaves_the_working_list_but_stays_readable(self):
        """Covers: B6 FR-011."""
        proc = _procurement(self.cat)
        _asset("ARCH-2", self.cat, procurement=proc)
        self.client_it.delete(f"/procurement/{proc.pk}/")

        listed = self.client_it.get("/procurement/").data
        archived = self.client_it.get("/procurement/", {"archived": "1"}).data

        self.assertNotIn(proc.pk, [row["id"] for row in listed])
        self.assertIn(proc.pk, [row["id"] for row in archived])
        self.assertEqual(self.client_it.get(f"/procurement/{proc.pk}/").status_code, 200)


class ProcurementAuthorizationTests(TestCase):
    """B6 ALR-002 and FR-016: denied mutations change nothing."""

    def setUp(self):
        self.cat = _catalog()

    def test_a_reader_without_the_write_code_cannot_create_a_procurement(self):
        """Covers: B6 FR-016, B6 ALR-002."""
        reader = _client("proc-reader", ("asset_view",))
        before = Procurement.objects.count()
        asset = _asset("AUTH-1", self.cat)

        response = reader.post("/procurement/", {
            "mode_of_purchase": self.cat["mode"].pk, "vendor": self.cat["vendor"].pk,
            "purchase_date": "2026-01-01", "invoice_date": "2026-01-02",
            "invoice_number": "INV-AUTH-1", "asset_ids": [asset.pk],
            "attested": True, "arrivals": _arrivals(self.cat, asset)}, format="json")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Procurement.objects.count(), before)
        asset.refresh_from_db()
        self.assertIsNone(asset.procurement_id)

    def test_a_rejected_link_leaves_every_association_untouched(self):
        """Covers: B6 ALR-002."""
        first = _procurement(self.cat, invoice="INV-R1")
        second = _procurement(self.cat, invoice="INV-R2")
        held = _asset("AUTH-2", self.cat, procurement=first)
        free = _asset("AUTH-3", self.cat)
        editor = _client("proc-editor", ("asset_view", "asset_edit"))

        response = editor.patch(f"/procurement/{second.pk}/",
                                _link_payload(self.cat, held, free), format="json")

        self.assertEqual(response.status_code, 400)
        held.refresh_from_db()
        free.refresh_from_db()
        self.assertEqual(held.procurement_id, first.pk)
        self.assertIsNone(free.procurement_id)
        self.assertFalse(ProcurementAssetLink.objects.exists())

    def test_master_writes_require_settings_access(self):
        """Covers: B6 FR-016, B6 ALR-002."""
        editor = _client("master-writer", ("asset_view", "asset_edit"))
        before = Vendor.objects.count()

        response = editor.post("/vendor/", {"name": "Unauthorized Vendor"}, format="json")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Vendor.objects.count(), before)
