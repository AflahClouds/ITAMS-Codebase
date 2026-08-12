from django.db import models

ASSET_STATUSES = ["Available", "Assigned", "Under Repair", "In Storage", "Sold", "Scrapped", "Lost"]
ASSET_CONDITIONS = ["New", "Good", "Average", "Damaged", "Repair Required"]
TERMINAL_STATUSES = ("Sold", "Scrapped", "Lost")
# Entered/left only via check_out/check_in (Checkout) or open_service/close_service
# (Service Record) — never directly, so those lifecycle functions' preconditions,
# custodian handling, and audit trail (AssetCheckout/ServiceRecord rows) can't be skipped.
LIFECYCLE_MANAGED_STATUSES = ("Assigned", "Under Repair")


class LifecycleError(Exception):
    """An asset checkout/transfer state transition isn't allowed."""


class Procurement(models.Model):
    mode_of_purchase = models.ForeignKey('catalog.PurchaseMode', on_delete=models.PROTECT)
    vendor = models.ForeignKey('catalog.Vendor', on_delete=models.PROTECT)
    purchase_date = models.DateField()
    invoice_date = models.DateField()
    invoice_number = models.CharField(unique=True, max_length=100)
    po_number = models.CharField(max_length=100, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.invoice_number


class Asset(models.Model):
    asset_id = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=200, blank=True, default="")
    tag_number = models.CharField(unique=True, max_length=100)
    serial_number = models.CharField(unique=True, max_length=100)
    category = models.ForeignKey('catalog.Category', on_delete=models.PROTECT)
    brand = models.ForeignKey('catalog.Brand', on_delete=models.PROTECT)
    model = models.ForeignKey('catalog.Model', on_delete=models.PROTECT)
    procurement = models.ForeignKey(Procurement, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    purchase_cost = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    depreciation_rate = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True)
    asset_life = models.IntegerField(null=True, blank=True)

    status = models.CharField(max_length=32, default="Available")
    condition = models.CharField(max_length=32, default="New")
    location = models.ForeignKey('accounts.Location', on_delete=models.SET_NULL, null=True, blank=True)
    custodian = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="held_assets")
    department = models.ForeignKey('accounts.Department', on_delete=models.SET_NULL, null=True, blank=True)
    warranty_start = models.DateField(null=True, blank=True)
    warranty_end = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    barcode_path = models.CharField(max_length=255, blank=True, default="")

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @property
    def warranty_days_left(self):
        if not self.warranty_end:
            return None
        from datetime import date
        return (self.warranty_end - date.today()).days

    @property
    def latest_amc(self):
        """The most recently created AMC contract, active/ended/incomplete. None if AMC
        was never set up. Ordered by id, not start_date — an Incomplete contract has no
        start_date yet, and NULLs sort last in a descending SQLite ORDER BY, which would
        otherwise hide it behind an older, fully-dated contract."""
        return self.amc_contracts.order_by('-id').first()

    @property
    def has_amc(self):
        """True while a current AMC contract exists — `Active` or `Incomplete`.

        An `Ended` contract stays in history but reports False, so the flag answers
        "is this asset under AMC now" rather than "was it ever" (ROADMAP.md decision
        C4). CONTEXT.md still describes has_amc as a deliberate no-AMC marker; that
        glossary reconciliation is outstanding.
        """
        contract = self.latest_amc
        return contract is not None and contract.status in ("Active", "Incomplete")

    @property
    def amc_start(self):
        contract = self.latest_amc
        return contract.start_date if contract else None

    @property
    def amc_end(self):
        contract = self.latest_amc
        return contract.end_date if contract else None

    @property
    def amc_status(self):
        contract = self.latest_amc
        return contract.status if contract else None

    @property
    def amc_end_reason(self):
        contract = self.latest_amc
        return contract.end_reason if contract else ""

    @property
    def amc_days_left(self):
        end = self.amc_end
        if not end:
            return None
        from datetime import date
        return (end - date.today()).days

    def __str__(self):
        return self.asset_id


def asset_image_path(instance, filename):
    return f"assets/images/{instance.asset_id}/{filename}"


def asset_document_path(instance, filename):
    return f"assets/documents/{instance.asset_id}/{filename}"


class AssetImage(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="images")
    file = models.FileField(upload_to=asset_image_path)
    file_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)


class AssetDocument(models.Model):
    DOCUMENT_TYPES = ["Purchase Invoice", "Warranty Card", "AMC Document", "PO Document",
                      "Asset Agreement", "Transfer Document", "Other"]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=64, default="Other")
    file = models.FileField(upload_to=asset_document_path)
    file_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    version = models.IntegerField(default=1)


class AssetCheckout(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="checkouts")
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name="checkouts")
    checkout_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_checkouts")
    purpose = models.CharField(max_length=255, blank=True, default="")
    checkout_condition = models.CharField(max_length=32, blank=True, default="")
    return_condition = models.CharField(max_length=32, blank=True, default="")
    # Intake and return notes are separate records of separate events: a check-in
    # must not overwrite what was recorded when the asset went out.
    remarks = models.TextField(blank=True, default="")
    return_remarks = models.TextField(blank=True, default="")
    status = models.CharField(max_length=16, default="Open")  # Open / Returned

    def __str__(self):
        return f"{self.asset.asset_id} -> {self.user.user_name}"


class AssetTransfer(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="transfers")
    previous_owner = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="transfers_out")
    new_owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name="transfers_in")
    previous_department = models.ForeignKey('accounts.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    new_department = models.ForeignKey('accounts.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    transfer_date = models.DateTimeField(auto_now_add=True)
    requested_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="requested_transfers")
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_transfers")
    status = models.CharField(max_length=16, default="Pending")  # Pending / Approved / Rejected
    remarks = models.TextField(blank=True, default="")
    condition = models.CharField(max_length=32, blank=True, default="")

    def __str__(self):
        return f"TRF-{self.id:05d}"


class AssetConditionLog(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="condition_logs")
    inspection_date = models.DateTimeField(auto_now_add=True)
    inspector = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    condition = models.CharField(max_length=32)
    notes = models.TextField(blank=True, default="")


class ServiceRecord(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="service_records")
    vendor = models.ForeignKey('catalog.Vendor', on_delete=models.PROTECT)
    sent_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateField(null=True, blank=True)
    returned_date = models.DateTimeField(null=True, blank=True)
    reason = models.CharField(max_length=255, blank=True, default="")
    cost = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    remarks = models.TextField(blank=True, default="")
    opened_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="opened_services")
    closed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="closed_services")
    status = models.CharField(max_length=16, default="Open")  # Open / Closed

    def __str__(self):
        return f"{self.asset.asset_id} -> {self.vendor.name}"


class AmcContract(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="amc_contracts")
    vendor = models.ForeignKey('catalog.Vendor', on_delete=models.PROTECT, null=True, blank=True)
    # Null while "Incomplete": has_amc was set but the actual contract dates haven't
    # been entered yet — a deliberate state per CONTEXT.md, not a partially-filled error.
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=16, default="Active")  # Incomplete / Active / Ended
    end_reason = models.TextField(blank=True, default="")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.asset.asset_id} AMC {self.start_date}–{self.end_date}"
