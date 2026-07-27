from django.db import models

ASSET_STATUSES = ["Available", "Assigned", "Under Repair", "In Storage", "Sold", "Scrapped", "Lost"]
ASSET_CONDITIONS = ["New", "Good", "Average", "Damaged", "Repair Required"]
TERMINAL_STATUSES = ("Sold", "Scrapped", "Lost")


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
    has_amc = models.BooleanField(default=False)
    amc_start = models.DateField(null=True, blank=True)
    amc_end = models.DateField(null=True, blank=True)
    amc_status = models.CharField(max_length=16, default="Active")  # Active / Ended
    amc_end_reason = models.TextField(blank=True, default="")
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
    def amc_days_left(self):
        if not self.amc_end:
            return None
        from datetime import date
        return (self.amc_end - date.today()).days

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
    remarks = models.TextField(blank=True, default="")
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
