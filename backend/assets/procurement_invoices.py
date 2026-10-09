"""Authoritative Procurement purchase-invoice operation (CHG-B6-01)."""
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.db.models import Max

from .models import (Procurement, ProcurementInvoiceVersion,
                     procurement_invoice_path)


class InvoiceValidationError(ValueError):
    """The submitted invoice violates the documented upload contract."""


def validate_invoice_upload(upload):
    if upload is None:
        raise InvoiceValidationError("Please choose a purchase invoice to upload.")

    safe_name = Path(upload.name or "").name
    extension = safe_name.rsplit('.', 1)[-1].lower() if '.' in safe_name else ''
    if extension not in settings.ALLOWED_DOCUMENT_EXTENSIONS:
        raise InvoiceValidationError("Unsupported document type.")
    if upload.size > settings.MAX_DOCUMENT_UPLOAD_SIZE:
        raise InvoiceValidationError("Purchase invoices must be 25 MB or smaller.")
    return safe_name


def record_procurement_invoice(procurement, upload, actor):
    """Add or replace the current invoice and return the newly current version.

    The database transaction owns version/current integrity. File storage is not
    transactional, so any new object is explicitly removed when the operation fails.
    """
    safe_name = validate_invoice_upload(upload)
    file_field = ProcurementInvoiceVersion._meta.get_field('file')
    storage = file_field.storage
    stored_name = None
    target_name = None

    try:
        with transaction.atomic():
            locked = Procurement.objects.select_for_update().get(pk=procurement.pk)
            current = (locked.invoice_versions.select_for_update()
                       .filter(is_current=True).first())
            next_version = ((locked.invoice_versions.aggregate(Max('version'))
                             ['version__max'] or 0) + 1)
            invoice = ProcurementInvoiceVersion(
                procurement=locked,
                file_name=safe_name,
                version=next_version,
                is_current=True,
                uploaded_by=actor,
            )
            target_name = procurement_invoice_path(invoice, safe_name)
            if hasattr(upload, 'seek'):
                upload.seek(0)
            stored_name = storage.save(target_name, upload)
            invoice.file.name = stored_name

            if current is not None:
                current.is_current = False
                current.save(update_fields=['is_current'])
            invoice.save(force_insert=True)
            return invoice
    except Exception:
        # `stored_name` is known after a successful storage write. `target_name`
        # also covers a storage backend that writes a partial object before raising.
        cleanup_name = stored_name or target_name
        if cleanup_name and storage.exists(cleanup_name):
            storage.delete(cleanup_name)
        raise
