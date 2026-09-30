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
    # Invoice numbers are the supplier's, not ours: two suppliers can each issue an
    # invoice numbered "1", so uniqueness is scoped to the Vendor (B6 FR-017). A PO
    # number is ours, so it is unique across the system when present.
    invoice_number = models.CharField(max_length=100)
    po_number = models.CharField(max_length=100, null=True, blank=True)
    # B6 FR-011 forbids destroying a purchase record. Removal archives it instead, so
    # the purchase details and their history stay readable.
    archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    archive_reason = models.TextField(blank=True, default="")

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['vendor', 'invoice_number'],
                                    name='uniq_invoice_per_vendor'),
            models.UniqueConstraint(fields=['po_number'], name='uniq_po_number',
                                    condition=~models.Q(po_number=None)),
        ]

    def __str__(self):
        return self.invoice_number


class ProcurementAssetLink(models.Model):
    """An append-only record of an Asset being attached to or detached from a purchase.

    B6 FR-012 requires every attachment and detachment to carry a reason and leave an
    immutable entry naming the actor, the time, and the association before and after.
    Without it a link change is invisible: the Asset simply points somewhere else, and
    nothing says who moved it or why.
    """
    ATTACHED = "Attached"
    DETACHED = "Detached"

    procurement = models.ForeignKey(Procurement, on_delete=models.CASCADE,
                                    related_name="link_history")
    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE,
                              related_name="procurement_link_history")
    action = models.CharField(max_length=16)  # Attached / Detached
    reason = models.TextField(blank=True, default="")
    actor = models.ForeignKey('accounts.User', on_delete=models.SET_NULL,
                              null=True, blank=True)
    previous_procurement = models.ForeignKey(
        Procurement, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="link_history_as_previous")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created', '-id']

    def __str__(self):
        return f"{self.asset_id} {self.action} {self.procurement_id}"


class ProcurementArrival(models.Model):
    """Evidence that a purchased Asset physically arrived (B6 FR-009).

    Decision C7 resolved in favour of the system enforcing this rather than trusting
    that whoever typed the invoice had the goods in front of them: a Procurement cannot
    be saved until every linked Asset has an arrival record with a date and a Location,
    and the person saving it has attested to that.
    """
    procurement = models.ForeignKey(Procurement, on_delete=models.CASCADE,
                                    related_name="arrivals")
    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE,
                              related_name="arrivals")
    arrived_on = models.DateField()
    location = models.ForeignKey('accounts.Location', on_delete=models.PROTECT)
    attested_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL,
                                    null=True, blank=True)
    attested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['procurement', 'asset'],
                                               name='uniq_arrival_per_asset')]

    def __str__(self):
        return f"{self.asset_id} arrived {self.arrived_on}"


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
        """The Asset's *current* AMC contract, or the newest closed one if none is open.

        B7 FR-005 and ALR-004 make this a question about coverage, not about data entry
        order: a contract entered later but covering an earlier period is not the current
        one. So a current contract (`Active` or `Incomplete`) always wins over an `Ended`
        one, and within each group the latest end date decides.

        Creation order still breaks ties, and it carries `Incomplete` contracts on its
        own: those have no dates yet, and NULLs sort last in a descending SQLite
        ORDER BY, which would otherwise hide a brand-new Incomplete contract behind an
        older fully-dated one.
        """
        current = self.amc_contracts.filter(status__in=("Active", "Incomplete"))
        return (current.order_by(models.F('end_date').desc(nulls_first=True), '-id').first()
                or self.amc_contracts.order_by(
                    models.F('end_date').desc(nulls_last=True), '-id').first())

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
    def amc_vendor_current(self):
        """The Vendor on the current contract, for a form that needs to prefill it.

        `amc_vendor` on the serializer is write-only, so without this an edit form has
        no way to show which Vendor the contract already names.
        """
        contract = self.latest_amc
        return contract.vendor_id if contract else None

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
    # B3 FR-028: a Checkout ended because something else took the Asset away is not a
    # return. Without the marker, "Returned" covers both and the two read alike.
    closed_as_interrupted = models.BooleanField(default=False)
    classification = models.CharField(max_length=16, default="Temporary")
    closure_reason = models.CharField(max_length=32, blank=True, default="")
    closed_at = models.DateTimeField(null=True, blank=True)
    classified_at = models.DateTimeField(null=True, blank=True)
    classified_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name="classified_checkouts")
    superseded_by_transfer = models.ForeignKey('AssetTransfer', on_delete=models.SET_NULL,
                                               null=True, blank=True, related_name="superseded_checkouts")

    class Meta:
        constraints = [
            # B3 FR-001 and FR-007: an Asset is held by at most one person at a time.
            # This was only ever enforced by a status check the database did not know
            # about, and `select_for_update` is a no-op on SQLite, so two concurrent
            # checkouts could both pass it.
            models.UniqueConstraint(fields=['asset'], condition=models.Q(status="Open"),
                                    name='uniq_open_checkout_per_asset'),
        ]

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


class AssetAssignment(models.Model):
    """One continuous period of ongoing employee custody."""

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="assignments")
    user = models.ForeignKey('accounts.User', on_delete=models.PROTECT,
                             related_name="asset_assignments")
    issued_at = models.DateTimeField(auto_now_add=True)
    issued_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name="issued_assignments")
    issue_condition = models.CharField(max_length=32)
    remarks = models.TextField(blank=True, default="")
    status = models.CharField(max_length=16, default="Open")
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name="closed_assignments")
    closure_reason = models.CharField(max_length=32, blank=True, default="")
    return_condition = models.CharField(max_length=32, blank=True, default="")
    return_remarks = models.TextField(blank=True, default="")
    source_transfer = models.ForeignKey(AssetTransfer, on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name="target_assignments")
    source_checkout = models.ForeignKey(AssetCheckout, on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name="classified_assignments")
    superseded_by_transfer = models.ForeignKey(AssetTransfer, on_delete=models.SET_NULL,
                                               null=True, blank=True, related_name="source_assignments")
    provenance = models.CharField(max_length=32, blank=True, default="")
    date_basis = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['asset'], condition=models.Q(status="Open"),
                                    name='uniq_open_assignment_per_asset'),
        ]

    def __str__(self):
        return f"{self.asset.asset_id} -> {self.user.user_name} (ongoing)"


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
    # Opening notes and closing notes record different events, so a closure adds its
    # own rather than replacing what the sender wrote (B5 FR-030).
    closing_remarks = models.TextField(blank=True, default="")
    opened_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="opened_services")
    closed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="closed_services")
    status = models.CharField(max_length=16, default="Open")  # Open / Closed
    # B5 FR-015: same distinction as B3 FR-028 — a repair cut short by something else
    # taking the Asset is not a completed repair.
    closed_as_interrupted = models.BooleanField(default=False)

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
    # The operator's own words when they End Support, and nothing else. B7 FR-034 keeps
    # this apart from the automatic supersede marker below, so the two are
    # distinguishable without reading their text.
    end_reason = models.TextField(blank=True, default="")
    superseded_by_renewal = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def closure_reason(self):
        """How this contract closed, for display. Renewal is not an operator reason."""
        if self.status != "Ended":
            return ""
        return "Superseded by renewal" if self.superseded_by_renewal else self.end_reason

    def __str__(self):
        return f"{self.asset.asset_id} AMC {self.start_date}–{self.end_date}"
