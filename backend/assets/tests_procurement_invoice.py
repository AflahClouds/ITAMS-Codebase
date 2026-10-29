"""Integration coverage for CHG-B6-01 Procurement purchase invoices.

The public seams are the authoritative invoice operation, the Procurement API,
and the protected Procurement/Asset download actions. Files are written to an
isolated temporary storage root for every test.
"""
from io import BytesIO
import json
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth.models import User as AuthUser
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import Location, Permission, Role, User
from catalog.models import Brand, Category, Model, PurchaseMode, Vendor
from core.models import AuditLog, Notification

from .models import Asset, Procurement, ProcurementInvoiceVersion
from .procurement_invoices import InvoiceValidationError, record_procurement_invoice


def _client_profile(username, codes=()):
    account = AuthUser.objects.create_user(username=username, password="test-password")
    role = Role.objects.create(name=f"{username} role")
    role.permissions.set([
        Permission.objects.get_or_create(code=code, defaults={"name": code})[0]
        for code in codes
    ])
    profile = User.objects.create(
        account=account,
        user_name=username,
        emp_id=f"EMP-{username}",
        email_id=f"{username}@example.com",
        role=role,
    )
    return account, profile


def _catalog():
    brand = Brand.objects.create(brand_name="Dell")
    return {
        "category": Category.objects.create(category_name="Laptops"),
        "brand": brand,
        "model": Model.objects.create(model_name="Latitude", brand=brand),
        "mode": PurchaseMode.objects.create(purchase_mode="Purchase"),
        "vendor": Vendor.objects.create(name="Invoice Supplies"),
        "location": Location.objects.create(name="Invoice Store"),
    }


def _procurement(catalog, invoice_number="INV-DOC-001"):
    return Procurement.objects.create(
        mode_of_purchase=catalog["mode"],
        vendor=catalog["vendor"],
        purchase_date="2026-01-01",
        invoice_date="2026-01-02",
        invoice_number=invoice_number,
    )


def _asset(asset_id, catalog, **extra):
    return Asset.objects.create(
        asset_id=asset_id,
        tag_number=f"{asset_id}-T",
        serial_number=f"{asset_id}-S",
        category=catalog["category"],
        brand=catalog["brand"],
        model=catalog["model"],
        **extra,
    )


def _pdf(name="purchase-invoice.pdf", content=b"%PDF-1.4 invoice"):
    return SimpleUploadedFile(name, content, content_type="application/pdf")


class ProcurementInvoiceStorageTestCase(TestCase):
    """Base fixture that never writes uploaded content into the repository."""

    def setUp(self):
        super().setUp()
        self.private_root = Path(settings.BASE_DIR) / "private_documents" / "test-storage"
        self.private_root.mkdir(parents=True, exist_ok=True)
        self.file_field = ProcurementInvoiceVersion._meta.get_field("file")
        self.original_storage = self.file_field.storage
        self.file_field.storage = FileSystemStorage(
            location=self.private_root, base_url=None)
        self.catalog = _catalog()
        _account, self.actor = _client_profile("invoice-operator")

    def tearDown(self):
        for path in self.private_root.rglob("*.*"):
            path.unlink(missing_ok=True)
        self.file_field.storage = self.original_storage
        super().tearDown()


class ProcurementInvoiceDomainTests(ProcurementInvoiceStorageTestCase):
    def test_an_initial_upload_creates_one_current_version_in_private_storage(self):
        """Covers: CHG-B6-01 FR-006, FR-010, FR-011."""
        procurement = _procurement(self.catalog)

        invoice = record_procurement_invoice(procurement, _pdf(), self.actor)

        self.assertEqual(invoice.version, 1)
        self.assertTrue(invoice.is_current)
        self.assertEqual(invoice.file_name, "purchase-invoice.pdf")
        self.assertEqual(procurement.invoice_versions.count(), 1)
        self.assertTrue(Path(invoice.file.path).is_file())
        self.assertTrue(Path(invoice.file.path).is_relative_to(self.private_root))

    def test_a_replacement_retains_the_old_version_and_has_one_current_version(self):
        """Covers: CHG-B6-01 FR-006, FR-010."""
        procurement = _procurement(self.catalog)
        first = record_procurement_invoice(procurement, _pdf("first.pdf"), self.actor)

        second = record_procurement_invoice(procurement, _pdf("corrected.pdf"), self.actor)

        first.refresh_from_db()
        self.assertFalse(first.is_current)
        self.assertTrue(second.is_current)
        self.assertEqual(second.version, 2)
        self.assertEqual(
            list(procurement.invoice_versions.order_by("version").values_list(
                "file_name", "version", "is_current")),
            [("first.pdf", 1, False), ("corrected.pdf", 2, True)],
        )

    def test_the_database_rejects_two_current_versions_for_one_procurement(self):
        """Covers: CHG-B6-01 FR-006, FR-012."""
        procurement = _procurement(self.catalog)
        record_procurement_invoice(procurement, _pdf("first.pdf"), self.actor)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProcurementInvoiceVersion.objects.create(
                    procurement=procurement,
                    file="duplicate.pdf",
                    file_name="duplicate.pdf",
                    version=2,
                    is_current=True,
                    uploaded_by=self.actor,
                )

    def test_an_unsupported_extension_is_rejected_without_a_version_or_file(self):
        """Covers: CHG-B6-01 FR-011, FR-012."""
        procurement = _procurement(self.catalog)

        with self.assertRaisesMessage(InvoiceValidationError, "Unsupported document type"):
            record_procurement_invoice(
                procurement,
                SimpleUploadedFile("invoice.exe", b"unsafe"),
                self.actor,
            )

        self.assertFalse(procurement.invoice_versions.exists())
        self.assertEqual(list(self.private_root.rglob("*.*")), [])


class ProcurementInvoiceApiTests(ProcurementInvoiceStorageTestCase):
    def setUp(self):
        super().setUp()
        self.account, self.actor = _client_profile(
            "procurement-api", ("asset_view", "asset_create", "asset_edit"))
        self.client = APIClient()
        self.client.force_authenticate(self.account)
        self.asset_a = _asset("INV-ASSET-A", self.catalog)
        self.asset_b = _asset("INV-ASSET-B", self.catalog)

    def _payload(self, assets=None, **overrides):
        assets = assets or [self.asset_a, self.asset_b]
        payload = {
            "mode_of_purchase": self.catalog["mode"].pk,
            "vendor": self.catalog["vendor"].pk,
            "purchase_date": "2026-01-01",
            "invoice_date": "2026-01-02",
            "invoice_number": "API-INV-001",
            "po_number": "API-PO-001",
            "asset_ids": [asset.pk for asset in assets],
            "attested": "true",
            "arrivals": json.dumps([
                {"asset": asset.pk, "arrived_on": "2026-01-03",
                 "location": self.catalog["location"].pk}
                for asset in assets
            ]),
        }
        payload.update(overrides)
        return payload

    def test_create_with_optional_invoice_maps_one_version_to_all_assets(self):
        response = self.client.post(
            reverse("procurement-list"),
            self._payload(invoice_file=_pdf()), format="multipart")

        self.assertEqual(response.status_code, 201, response.data)
        procurement = Procurement.objects.get(pk=response.data["id"])
        self.asset_a.refresh_from_db()
        self.asset_b.refresh_from_db()
        self.assertEqual(self.asset_a.procurement, procurement)
        self.assertEqual(self.asset_b.procurement, procurement)
        self.assertEqual(procurement.invoice_versions.count(), 1)
        self.assertEqual(response.data["current_invoice"]["version"], 1)
        self.assertNotIn("file", response.data["current_invoice"])
        self.assertTrue(AuditLog.objects.filter(
            module="Procurement", action="Create").exists())

    def test_create_without_invoice_remains_valid(self):
        response = self.client.post(
            reverse("procurement-list"), self._payload(), format="multipart")

        self.assertEqual(response.status_code, 201, response.data)
        self.assertIsNone(response.data["current_invoice"])
        self.assertFalse(ProcurementInvoiceVersion.objects.exists())

    def test_invalid_invoice_rolls_back_procurement_assets_and_audit(self):
        response = self.client.post(
            reverse("procurement-list"),
            self._payload(invoice_file=SimpleUploadedFile("invoice.exe", b"bad")),
            format="multipart")

        self.assertEqual(response.status_code, 400)
        self.assertIn("invoice_file", response.data)
        self.assertFalse(Procurement.objects.exists())
        self.assertFalse(AuditLog.objects.filter(module="Procurement").exists())
        self.asset_a.refresh_from_db()
        self.assertIsNone(self.asset_a.procurement_id)

    def test_denied_create_does_not_store_any_invoice(self):
        denied_account, _profile = _client_profile("invoice-reader", ("asset_view",))
        self.client.force_authenticate(denied_account)

        response = self.client.post(
            reverse("procurement-list"),
            self._payload(invoice_file=_pdf()), format="multipart")

        self.assertEqual(response.status_code, 403)
        self.assertFalse(ProcurementInvoiceVersion.objects.exists())

    def test_audit_failure_rolls_back_database_and_removes_the_stored_file(self):
        self.client.raise_request_exception = False
        with patch("assets.views.log_action", side_effect=RuntimeError("audit failed")):
            response = self.client.post(
                reverse("procurement-list"),
                self._payload(invoice_file=_pdf()), format="multipart")

        self.assertEqual(response.status_code, 500)
        self.assertFalse(Procurement.objects.exists())
        self.assertEqual(list(self.private_root.rglob("*.*")), [])

    def test_edit_adds_then_replaces_invoice_and_omission_preserves_it(self):
        procurement = _procurement(self.catalog, "EDIT-INV")
        self.asset_a.procurement = procurement
        self.asset_a.save(update_fields=["procurement"])
        base = self._payload(
            assets=[self.asset_a], invoice_number="EDIT-INV", po_number="EDIT-PO")
        url = reverse("procurement-detail", args=[procurement.pk])

        added = self.client.put(url, {**base, "invoice_file": _pdf("first.pdf")},
                                format="multipart")
        omitted = self.client.put(url, base, format="multipart")
        replaced = self.client.put(url, {**base, "invoice_file": _pdf("second.pdf")},
                                   format="multipart")

        self.assertEqual(added.status_code, 200, added.data)
        self.assertEqual(omitted.status_code, 200, omitted.data)
        self.assertEqual(replaced.status_code, 200, replaced.data)
        self.assertEqual(replaced.data["current_invoice"]["version"], 2)
        self.assertEqual(
            list(procurement.invoice_versions.order_by("version").values_list(
                "file_name", "is_current")),
            [("first.pdf", False), ("second.pdf", True)],
        )

    def test_partial_update_can_add_an_invoice_without_resending_asset_links(self):
        procurement = _procurement(self.catalog, "PATCH-INV")
        self.asset_a.procurement = procurement
        self.asset_a.save(update_fields=["procurement"])

        response = self.client.patch(
            reverse("procurement-detail", args=[procurement.pk]),
            {"invoice_file": _pdf("patched.pdf")}, format="multipart")

        self.assertEqual(response.status_code, 200, response.data)
        self.asset_a.refresh_from_db()
        self.assertEqual(self.asset_a.procurement_id, procurement.pk)
        self.assertEqual(response.data["current_invoice"]["file_name"], "patched.pdf")

    def test_update_audit_failure_keeps_the_previous_current_file(self):
        procurement = _procurement(self.catalog, "ROLLBACK-INV")
        self.asset_a.procurement = procurement
        self.asset_a.save(update_fields=["procurement"])
        old = record_procurement_invoice(procurement, _pdf("old.pdf"), self.actor)
        old_files = set(self.private_root.rglob("*.*"))
        self.client.raise_request_exception = False

        with patch("assets.views.log_action", side_effect=RuntimeError("audit failed")):
            response = self.client.put(
                reverse("procurement-detail", args=[procurement.pk]),
                {**self._payload(assets=[self.asset_a], invoice_number="ROLLBACK-INV",
                                 po_number="ROLLBACK-PO"),
                 "invoice_file": _pdf("new.pdf")},
                format="multipart")

        self.assertEqual(response.status_code, 500)
        old.refresh_from_db()
        self.assertTrue(old.is_current)
        self.assertEqual(procurement.invoice_versions.count(), 1)
        self.assertEqual(set(self.private_root.rglob("*.*")), old_files)

    def test_replacement_notifies_it_manager_equivalents_after_commit(self):
        _manager_account, manager = _client_profile("invoice-manager", ("asset_delete",))
        procurement = _procurement(self.catalog, "NOTIFY-INV")
        self.asset_a.procurement = procurement
        self.asset_a.save(update_fields=["procurement"])
        record_procurement_invoice(procurement, _pdf("old.pdf"), self.actor)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.put(
                reverse("procurement-detail", args=[procurement.pk]),
                {**self._payload(assets=[self.asset_a], invoice_number="NOTIFY-INV",
                                 po_number="NOTIFY-PO"),
                 "invoice_file": _pdf("new.pdf")},
                format="multipart")

        self.assertEqual(response.status_code, 200, response.data)
        self.assertTrue(Notification.objects.filter(
            user=manager, message__icontains="invoice replaced").exists())

    def test_same_current_invoice_is_exposed_and_streamed_through_linked_assets(self):
        procurement = _procurement(self.catalog, "MAPPED-INV")
        linked_assets = [
            self.asset_a,
            self.asset_b,
            _asset("INV-ASSET-C", self.catalog),
            _asset("INV-ASSET-D", self.catalog),
            _asset("INV-ASSET-E", self.catalog),
        ]
        Asset.objects.filter(pk__in=[asset.pk for asset in linked_assets]).update(
            procurement=procurement)
        invoice = record_procurement_invoice(
            procurement, _pdf("mapped.pdf", b"%PDF mapped content"), self.actor)

        procurement_response = self.client.get(
            reverse("procurement-detail", args=[procurement.pk]))
        asset_responses = [
            self.client.get(reverse("asset-detail", args=[asset.pk]))
            for asset in linked_assets
        ]
        procurement_download = self.client.get(
            reverse("procurement-invoice", args=[procurement.pk]))
        asset_download = self.client.get(
            reverse("asset-procurement-invoice", args=[self.asset_a.pk]))

        self.assertEqual(procurement_response.data["current_invoice"]["id"], invoice.pk)
        self.assertTrue(all(
            response.data["procurement_invoice"]["id"] == invoice.pk
            for response in asset_responses))
        self.assertEqual(b"".join(procurement_download.streaming_content), b"%PDF mapped content")
        self.assertEqual(b"".join(asset_download.streaming_content), b"%PDF mapped content")
        procurement_download.close()
        asset_download.close()
        self.assertFalse(Asset.objects.filter(
            pk__in=[asset.pk for asset in linked_assets],
            documents__document_type="Purchase Invoice").exists())

        self.asset_a.procurement = None
        self.asset_a.save(update_fields=["procurement"])
        detached = self.client.get(reverse("asset-detail", args=[self.asset_a.pk]))
        missing_download = self.client.get(
            reverse("asset-procurement-invoice", args=[self.asset_a.pk]))
        self.assertIsNone(detached.data["procurement_invoice"])
        self.assertEqual(missing_download.status_code, 404)

    def test_assigned_asset_keeps_its_linked_invoice_and_custody_projection(self):
        """D integration: an invoice-linked Asset remains readable after assignment."""
        self.actor.role.permissions.add(Permission.objects.get(
            code="asset_custody_manage"))
        _account, holder = _client_profile("invoice-assignee")
        procurement = _procurement(self.catalog, "CUSTODY-INV")
        self.asset_a.procurement = procurement
        self.asset_a.status = 'Available'  # Established, purchased stock for this custody fixture.
        self.asset_a.save(update_fields=["procurement", "status"])
        invoice = record_procurement_invoice(
            procurement, _pdf("custody.pdf", b"%PDF custody invoice"), self.actor)

        assigned = self.client.post(reverse("assignment-list"), {
            "asset": self.asset_a.pk, "user": holder.pk,
            "remarks": "Primary device",
        }, format="json")
        self.assertEqual(assigned.status_code, 201, assigned.data)

        detail = self.client.get(reverse("asset-detail", args=[self.asset_a.pk]))
        download = self.client.get(reverse(
            "asset-procurement-invoice", args=[self.asset_a.pk]))
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["custody_type"], "Ongoing")
        self.assertEqual(detail.data["custodian"], holder.pk)
        self.assertEqual(detail.data["procurement_invoice"]["id"], invoice.pk)
        self.assertEqual(download.status_code, 200)
        self.assertEqual(b"".join(download.streaming_content), b"%PDF custody invoice")
        download.close()

    def test_employee_scope_allows_own_asset_route_but_denies_procurement_and_other_asset(self):
        employee_account = AuthUser.objects.create_user(
            username="scoped-employee", password="test-password")
        employee_role, _created = Role.objects.get_or_create(name="Employee")
        employee_role.permissions.add(Permission.objects.get(code="asset_view"))
        employee = User.objects.create(
            account=employee_account, user_name="Scoped Employee", emp_id="EMP-SCOPE",
            email_id="scope@example.com", role=employee_role)
        procurement = _procurement(self.catalog, "SCOPE-INV")
        self.asset_a.procurement = procurement
        self.asset_a.custodian = employee
        self.asset_a.save(update_fields=["procurement", "custodian"])
        self.asset_b.procurement = procurement
        self.asset_b.save(update_fields=["procurement"])
        record_procurement_invoice(procurement, _pdf("scope.pdf"), self.actor)
        self.client.force_authenticate(employee_account)

        own = self.client.get(reverse("asset-procurement-invoice", args=[self.asset_a.pk]))
        other = self.client.get(reverse("asset-procurement-invoice", args=[self.asset_b.pk]))
        procurement_route = self.client.get(
            reverse("procurement-invoice", args=[procurement.pk]))

        self.assertEqual(own.status_code, 200)
        self.assertEqual(other.status_code, 404)
        self.assertEqual(procurement_route.status_code, 403)
        own.close()

    def test_a_file_over_25_mb_is_rejected_without_reading_that_much_content(self):
        """Covers: CHG-B6-01 FR-011, FR-012."""
        procurement = _procurement(self.catalog)
        upload = InMemoryUploadedFile(
            BytesIO(b"%PDF"),
            field_name="invoice_file",
            name="large.pdf",
            content_type="application/pdf",
            size=(25 * 1024 * 1024) + 1,
            charset=None,
        )

        with self.assertRaisesMessage(InvoiceValidationError, "25 MB"):
            record_procurement_invoice(procurement, upload, self.actor)

        self.assertFalse(procurement.invoice_versions.exists())

    def test_a_partial_storage_failure_leaves_no_version_or_file(self):
        """Covers: CHG-B6-01 FR-012."""
        procurement = _procurement(self.catalog)

        class PartialFailureStorage(FileSystemStorage):
            def _save(storage_self, name, content):
                saved_name = super()._save(name, content)
                raise OSError(f"storage interrupted after {saved_name}")

        self.file_field.storage = PartialFailureStorage(
            location=self.private_root, base_url=None)

        with self.assertRaisesMessage(OSError, "storage interrupted"):
            record_procurement_invoice(procurement, _pdf(), self.actor)

        self.assertFalse(procurement.invoice_versions.exists())
        self.assertEqual(list(self.private_root.rglob("*.*")), [])
