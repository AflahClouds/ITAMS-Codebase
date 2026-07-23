from django.conf import settings as django_settings
from django.db import models

ASSET_STATUSES = ["Available", "Assigned", "Under Repair", "In Storage", "Disposed", "Scrapped"]
ASSET_CONDITIONS = ["New", "Good", "Average", "Damaged", "Repair Required", "Scrapped"]


class Category(models.Model):
    category_name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.category_name


class Brand(models.Model):
    brand_name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.brand_name


class Model(models.Model):
    model_name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.model_name


class PurchaseMode(models.Model):
    purchase_mode = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.purchase_mode


class Department(models.Model):
    name = models.CharField(unique=True, max_length=128)
    description = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(unique=True, max_length=128)
    address = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.name


class Permission(models.Model):
    code = models.CharField(unique=True, max_length=64)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.code


class Role(models.Model):
    name = models.CharField(unique=True, max_length=64)
    description = models.CharField(max_length=255, blank=True, default="")
    permissions = models.ManyToManyField(Permission, blank=True, related_name="roles")

    def has_permission(self, code):
        if self.name == "Admin":
            return True
        return self.permissions.filter(code=code).exists()

    def __str__(self):
        return self.name


class Procurement(models.Model):
    mode_of_purchase = models.ForeignKey(PurchaseMode, on_delete=models.PROTECT)
    vendor_name = models.CharField(max_length=100)
    purchase_date = models.DateField()
    invoice_date = models.DateField()
    invoice_number = models.CharField(unique=True, max_length=100)
    po_number = models.CharField(max_length=100, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.invoice_number


class User(models.Model):
    """Employee profile. Login credentials live on the linked auth account."""
    account = models.OneToOneField(
        django_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="profile")
    user_name = models.CharField(max_length=100)
    emp_id = models.CharField(unique=True, max_length=100)
    email_id = models.EmailField(unique=True, max_length=100)
    mob_no = models.CharField(max_length=20, blank=True, default="")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.CharField(max_length=128, blank=True, default="")
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=16, default="Active")  # Active / Disabled

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def can(self, permission_code):
        if self.role and self.role.name == "Admin":
            return True
        return self.role.has_permission(permission_code) if self.role else False

    def __str__(self):
        return self.user_name


class Asset(models.Model):
    asset_id = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=200, blank=True, default="")
    tag_number = models.CharField(unique=True, max_length=100)
    serial_number = models.CharField(unique=True, max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    model = models.ForeignKey(Model, on_delete=models.PROTECT)
    procurement = models.ForeignKey(Procurement, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    purchase_cost = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    depreciation_rate = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True)
    asset_life = models.IntegerField(null=True, blank=True)

    status = models.CharField(max_length=32, default="Available")
    condition = models.CharField(max_length=32, default="New")
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    custodian = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="held_assets")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
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
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)


class AssetDocument(models.Model):
    DOCUMENT_TYPES = ["Purchase Invoice", "Warranty Card", "AMC Document", "PO Document",
                      "Asset Agreement", "Transfer Document", "Other"]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=64, default="Other")
    file = models.FileField(upload_to=asset_document_path)
    file_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    version = models.IntegerField(default=1)


class AssetCheckout(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="checkouts")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="checkouts")
    checkout_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_checkouts")
    purpose = models.CharField(max_length=255, blank=True, default="")
    checkout_condition = models.CharField(max_length=32, blank=True, default="")
    return_condition = models.CharField(max_length=32, blank=True, default="")
    remarks = models.TextField(blank=True, default="")
    status = models.CharField(max_length=16, default="Open")  # Open / Returned

    def __str__(self):
        return f"{self.asset.asset_id} -> {self.user.user_name}"


class AssetTransfer(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="transfers")
    previous_owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="transfers_out")
    new_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transfers_in")
    previous_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    new_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    transfer_date = models.DateTimeField(auto_now_add=True)
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="requested_transfers")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_transfers")
    status = models.CharField(max_length=16, default="Pending")  # Pending / Approved / Rejected
    remarks = models.TextField(blank=True, default="")
    condition = models.CharField(max_length=32, blank=True, default="")

    def __str__(self):
        return f"TRF-{self.id:05d}"


class AssetConditionLog(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="condition_logs")
    inspection_date = models.DateTimeField(auto_now_add=True)
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    condition = models.CharField(max_length=32)
    notes = models.TextField(blank=True, default="")


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=500)
    link = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=16, default="Unread")  # Unread / Read
    created = models.DateTimeField(auto_now_add=True)


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    username = models.CharField(max_length=64, blank=True, default="")
    action = models.CharField(max_length=64)
    module = models.CharField(max_length=64)
    old_value = models.TextField(blank=True, default="")
    new_value = models.TextField(blank=True, default="")
    date = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=64, blank=True, default="")


class Setting(models.Model):
    key = models.CharField(unique=True, max_length=64)
    value = models.TextField(blank=True, default="")

    @staticmethod
    def get(key, default=None):
        row = Setting.objects.filter(key=key).first()
        return row.value if row and row.value is not None else default

    @staticmethod
    def set(key, value):
        Setting.objects.update_or_create(key=key, defaults={"value": value})


def users_with_permission(code):
    """Active employee profiles whose role grants the permission (Admins included)."""
    return [u for u in User.objects.filter(status="Active").select_related("role") if u.can(code)]
