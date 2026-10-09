"""Private file storage used by authorization-checked Asset APIs."""
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateInvoiceStorage(FileSystemStorage):
    """Filesystem storage deliberately lacking a public base URL."""

    def __init__(self):
        super().__init__(location=settings.PRIVATE_DOCUMENT_ROOT, base_url=None)

    @property
    def base_url(self):
        """Private documents never have a directly addressable media URL."""
        return None

    def url(self, name):
        raise ValueError("Private invoice files are only available through protected API actions.")


private_invoice_storage = PrivateInvoiceStorage()
