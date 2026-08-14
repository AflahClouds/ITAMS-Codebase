from datetime import date as date_cls

from django.db import transaction
from rest_framework import serializers

from core.services import get_profile

from accounts.serializers import DepartmentSerializer, LocationSerializer, UserLiteSerializer
from catalog.models import Vendor
from catalog.serializers import (BrandSerializer, CategorySerializer,
                                 ModelSerializer, PurchaseModeSerializer,
                                 VendorSerializer)

from .checkout import close_all_open_checkouts
from .models import (ASSET_CONDITIONS, ASSET_STATUSES, LIFECYCLE_MANAGED_STATUSES,
                     TERMINAL_STATUSES, AmcContract, Asset, AssetCheckout,
                     AssetConditionLog, AssetDocument, AssetImage, AssetTransfer,
                     Procurement, ProcurementArrival, ProcurementAssetLink,
                     ServiceRecord)
from .service import close_all_open_service_records


class ProcurementLiteSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)

    class Meta:
        model = Procurement
        fields = ('id', 'invoice_number', 'vendor_name', 'purchase_date')


class AssetImageSerializer(serializers.ModelSerializer):
    uploaded_by_details = UserLiteSerializer(source='uploaded_by', read_only=True)

    class Meta:
        model = AssetImage
        fields = ('id', 'asset', 'file', 'file_name', 'uploaded_by_details', 'upload_date')
        read_only_fields = ('file_name', 'upload_date')


class AssetDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_details = UserLiteSerializer(source='uploaded_by', read_only=True)

    class Meta:
        model = AssetDocument
        fields = ('id', 'asset', 'document_type', 'file', 'file_name',
                  'uploaded_by_details', 'upload_date', 'version')
        read_only_fields = ('file_name', 'upload_date', 'version')


class AssetSerializer(serializers.ModelSerializer):
    category_details = CategorySerializer(source='category', read_only=True)
    brand_details = BrandSerializer(source='brand', read_only=True)
    model_details = ModelSerializer(source='model', read_only=True)
    location_details = LocationSerializer(source='location', read_only=True)
    department_details = DepartmentSerializer(source='department', read_only=True)
    custodian_details = UserLiteSerializer(source='custodian', read_only=True)
    procurement_details = ProcurementLiteSerializer(source='procurement', read_only=True)
    has_procurement = serializers.SerializerMethodField()
    warranty_days_left = serializers.ReadOnlyField()
    has_amc = serializers.BooleanField(required=False, default=False)
    amc_start = serializers.DateField(required=False, allow_null=True)
    amc_end = serializers.DateField(required=False, allow_null=True)
    amc_vendor = serializers.PrimaryKeyRelatedField(
        queryset=Vendor.objects.all(), required=False, allow_null=True, write_only=True)
    amc_status = serializers.ReadOnlyField()
    amc_vendor_current = serializers.ReadOnlyField()
    amc_end_reason = serializers.ReadOnlyField()
    amc_days_left = serializers.ReadOnlyField()
    barcode_url = serializers.SerializerMethodField()
    images = AssetImageSerializer(many=True, read_only=True)
    documents = AssetDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Asset
        fields = "__all__"
        read_only_fields = ('barcode_path',)

    def get_has_procurement(self, obj):
        return obj.procurement_id is not None

    def get_barcode_url(self, obj):
        if not obj.barcode_path:
            return None
        from django.conf import settings
        url = f"{settings.MEDIA_URL}{obj.barcode_path}"
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else url

    def validate_status(self, value):
        if value not in ASSET_STATUSES:
            raise serializers.ValidationError(f"Status must be one of {ASSET_STATUSES}")
        return value

    def validate_condition(self, value):
        if value not in ASSET_CONDITIONS:
            raise serializers.ValidationError(f"Condition must be one of {ASSET_CONDITIONS}")
        return value

    def _validate_coverage_dates(self, attrs):
        """Warranty and initial-AMC date rules (B7 FR-030, FR-031, FR-032).

        FR-030 exists because the same values were accepted here and refused by
        `renew_amc`: one route validated, the other did not, so which rules applied
        depended on how the operator got there. The rules are stated once and applied
        to both.
        """
        def _resolve(field):
            if field in attrs:
                return attrs[field]
            return getattr(self.instance, field, None) if self.instance else None

        warranty_start = _resolve('warranty_start')
        warranty_end = _resolve('warranty_end')
        # Either Warranty date may stand alone — partially known manufacturer coverage
        # stays enterable (FR-031) — but an end before its start is not a date we can
        # make sense of.
        if warranty_start and warranty_end and warranty_end <= warranty_start:
            raise serializers.ValidationError(
                {"warranty_end": "Warranty end date must be after the start date."})

        if not attrs.get('has_amc'):
            return
        amc_start, amc_end = attrs.get('amc_start'), attrs.get('amc_end')
        if bool(amc_start) != bool(amc_end):
            raise serializers.ValidationError(
                {"amc_end": "Supply both AMC dates or neither; supplying neither "
                            "records the contract as Incomplete."})
        if amc_start and amc_end and amc_end <= amc_start:
            raise serializers.ValidationError(
                {"amc_end": "AMC end date must be after the start date."})
        if amc_start and amc_end and not attrs.get('amc_vendor'):
            # A dated contract is held with somebody, and vendor-grouped AMC reporting
            # is the point of Vendor being a managed entity (FR-032). Only an
            # Incomplete contract may omit one.
            raise serializers.ValidationError(
                {"amc_vendor": "A vendor is required once the AMC has dates."})

    def validate(self, attrs):
        self._validate_coverage_dates(attrs)
        if self.instance is None:
            # A new asset enters the register unheld. Custody is only ever granted by
            # the operation that records it, so creation cannot short-circuit into a
            # lifecycle-managed status or hand the asset to someone (decision C2).
            new_status = attrs.get('status') or "Available"
            if new_status not in ("Available", "In Storage"):
                raise serializers.ValidationError(
                    {"status": "A new asset may only be created as Available or "
                               "In Storage; use Checkout or a Service Record to move it."})
            if attrs.get('custodian') is not None:
                raise serializers.ValidationError(
                    {"custodian": "A new asset cannot be created with a Custodian; "
                                  "use Checkout or Transfer to assign custody."})
        if self.instance is not None:
            current_status = self.instance.status
            new_status = attrs.get('status', current_status)
            if ('custodian' in attrs and attrs['custodian'] != self.instance.custodian
                    and new_status not in TERMINAL_STATUSES):
                # Otherwise the creation guard above is bypassable by saving the asset
                # and editing a Custodian in. Terminal transitions are exempt: update()
                # clears or retains the Custodian itself for Sold/Scrapped and Lost.
                raise serializers.ValidationError(
                    {"custodian": "Custody changes through Checkout or Transfer, "
                                  "not a direct edit."})
            if new_status != current_status:
                if current_status in TERMINAL_STATUSES:
                    raise serializers.ValidationError(
                        {"status": f"This asset is {current_status} and cannot change status further."})
                if new_status in LIFECYCLE_MANAGED_STATUSES:
                    action = "Checkout" if new_status == "Assigned" else "a Service Record"
                    raise serializers.ValidationError(
                        {"status": f"Use {action} to move this asset to {new_status} — "
                                   "it can't be set directly."})
                if current_status in LIFECYCLE_MANAGED_STATUSES and new_status not in TERMINAL_STATUSES:
                    action = "Check-in" if current_status == "Assigned" else "closing its Service Record"
                    raise serializers.ValidationError(
                        {"status": f"This asset is {current_status}; use {action} before "
                                   "changing its status directly."})
        return attrs

    def create(self, validated_data):
        has_amc = validated_data.pop('has_amc', False)
        amc_start = validated_data.pop('amc_start', None)
        amc_end = validated_data.pop('amc_end', None)
        amc_vendor = validated_data.pop('amc_vendor', None)
        asset = super().create(validated_data)
        if has_amc:
            if amc_start and amc_end:
                AmcContract.objects.create(
                    asset=asset, vendor=amc_vendor, start_date=amc_start,
                    end_date=amc_end, status="Active")
            else:
                # has_amc checked but dates not entered yet — a deliberate, distinct
                # state (CONTEXT.md), not silently dropped.
                AmcContract.objects.create(asset=asset, status="Incomplete")
        return asset

    def update(self, instance, validated_data):
        has_amc = validated_data.pop('has_amc', None)
        amc_start = validated_data.pop('amc_start', None)
        amc_end = validated_data.pop('amc_end', None)
        amc_vendor = validated_data.pop('amc_vendor', None)

        old_status = instance.status
        new_status = validated_data.get('status', old_status)
        entering_status = new_status != old_status
        if entering_status and new_status in ("Sold", "Scrapped"):
            # Terminal — the org no longer has custody-tracking obligations for this asset.
            validated_data['custodian'] = None
        elif entering_status and new_status == "Lost":
            # Custodian is retained for accountability (who had it when it went missing) —
            # ignore any custodian value the client sent along with this transition.
            validated_data.pop('custodian', None)

        with transaction.atomic():
            instance = super().update(instance, validated_data)

            if entering_status and new_status in TERMINAL_STATUSES and old_status in LIFECYCLE_MANAGED_STATUSES:
                # Going straight from Assigned/Under Repair to a terminal status is the
                # one legitimate direct transition (you can't check in a lost or sold
                # asset) — but whichever record was managing that status must still be
                # closed out, or it's left dangling "Open" forever.
                note = f"Auto-closed: asset marked {new_status}."
                close_all_open_checkouts(instance, note=note)
                close_all_open_service_records(instance, note=note)

            # Initial AMC entry, or a correction to the still-open contract — not a
            # renewal. Renewals (closing the old contract, opening a new one) go through
            # the dedicated renew_amc action so the history stays intact.
            if has_amc:
                contract = instance.latest_amc
                if amc_start and amc_end:
                    if contract and contract.status in ("Active", "Incomplete"):
                        contract.start_date = amc_start
                        contract.end_date = amc_end
                        contract.vendor = amc_vendor
                        contract.status = "Active"
                        contract.save(update_fields=['start_date', 'end_date', 'vendor',
                                                     'status'])
                    else:
                        AmcContract.objects.create(
                            asset=instance, vendor=amc_vendor, start_date=amc_start,
                            end_date=amc_end, status="Active")
                elif not contract or contract.status == "Ended":
                    AmcContract.objects.create(asset=instance, status="Incomplete")
        return instance


class AssetLiteSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category_name', read_only=True)

    class Meta:
        model = Asset
        fields = ('id', 'asset_id', 'name', 'tag_number', 'serial_number',
                  'status', 'condition', 'category_name')


class ProcurementArrivalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcurementArrival
        fields = ('id', 'asset', 'arrived_on', 'location', 'attested_by', 'attested_at')
        read_only_fields = ('attested_by', 'attested_at')


class ProcurementLinkHistorySerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.user_name', read_only=True)
    asset_label = serializers.CharField(source='asset.asset_id', read_only=True)

    class Meta:
        model = ProcurementAssetLink
        fields = ('id', 'asset', 'asset_label', 'action', 'reason', 'actor',
                  'actor_name', 'previous_procurement', 'created')


class ProcurementSerializer(serializers.ModelSerializer):
    mode_of_purchase_details = PurchaseModeSerializer(source='mode_of_purchase', read_only=True)
    vendor_details = VendorSerializer(source='vendor', read_only=True)
    assets = AssetSerializer(many=True, read_only=True)
    asset_ids = serializers.PrimaryKeyRelatedField(
        queryset=Asset.objects.all(), many=True, write_only=True
    )
    # B6 FR-009: one arrival per linked Asset, each with a date and a Location, plus an
    # explicit attestation from whoever is saving the record.
    arrivals = ProcurementArrivalSerializer(many=True, write_only=True, required=False)
    arrival_records = ProcurementArrivalSerializer(source='arrivals', many=True,
                                                   read_only=True)
    attested = serializers.BooleanField(write_only=True, required=False, default=False)
    link_reason = serializers.CharField(write_only=True, required=False,
                                        allow_blank=True, default="")
    link_history = ProcurementLinkHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Procurement
        fields = "__all__"
        read_only_fields = ('archived', 'archived_at', 'archive_reason')

    def validate_asset_ids(self, assets):
        current_id = self.instance.id if self.instance else None
        conflicting = [
            asset for asset in assets
            if asset.procurement_id and asset.procurement_id != current_id
        ]
        if conflicting:
            labels = ", ".join(asset.asset_id for asset in conflicting)
            raise serializers.ValidationError(
                f"These assets are already linked to another procurement: {labels}"
            )
        # FR-013 bounds the link both ways. The upper bound was enforced above; without
        # the lower bound a Procurement can be emptied and left describing nothing.
        if not assets:
            raise serializers.ValidationError(
                "A procurement must keep at least one asset linked to it.")
        return assets

    def validate(self, attrs):
        purchase = attrs.get('purchase_date') or getattr(self.instance, 'purchase_date', None)
        invoice = attrs.get('invoice_date') or getattr(self.instance, 'invoice_date', None)
        today = date_cls.today()
        # FR-010 orders the three dates a completed purchase has: it was bought, then
        # invoiced, and both happened before we wrote it down.
        if purchase and invoice and purchase > invoice:
            raise serializers.ValidationError(
                {"purchase_date": "Purchase date cannot be after the invoice date."})
        if purchase and purchase > today:
            raise serializers.ValidationError(
                {"purchase_date": "Purchase date cannot be in the future."})
        if invoice and invoice > today:
            raise serializers.ValidationError(
                {"invoice_date": "Invoice date cannot be in the future."})

        assets = attrs.get('asset_ids')
        if assets is not None:
            arrivals = attrs.get('arrivals') or []
            if not attrs.get('attested'):
                raise serializers.ValidationError(
                    {"attested": "Confirm that the listed assets have physically "
                                 "arrived before saving this purchase."})
            arrived = {a['asset'].pk if hasattr(a['asset'], 'pk') else a['asset']
                       for a in arrivals}
            existing = set()
            if self.instance is not None:
                existing = set(self.instance.arrivals.values_list('asset_id', flat=True))
            missing = [a.asset_id for a in assets if a.pk not in arrived | existing]
            if missing:
                raise serializers.ValidationError(
                    {"arrivals": "An arrival record with a date and a location is "
                                 f"required for: {', '.join(missing)}"})
        return attrs

    def _actor(self):
        request = self.context.get('request')
        return get_profile(request) if request else None

    def _record_links(self, procurement, assets, previous, reason):
        actor = self._actor()
        rows = []
        current = {asset.pk for asset in assets}
        for asset in assets:
            if asset.pk not in previous:
                rows.append(ProcurementAssetLink(
                    procurement=procurement, asset=asset,
                    action=ProcurementAssetLink.ATTACHED, reason=reason, actor=actor))
        for asset in Asset.objects.filter(pk__in=previous - current):
            rows.append(ProcurementAssetLink(
                procurement=procurement, asset=asset,
                action=ProcurementAssetLink.DETACHED, reason=reason, actor=actor,
                previous_procurement=procurement))
        if rows:
            ProcurementAssetLink.objects.bulk_create(rows)

    def _record_arrivals(self, procurement, arrivals):
        actor = self._actor()
        for row in arrivals:
            ProcurementArrival.objects.update_or_create(
                procurement=procurement, asset=row['asset'],
                defaults={"arrived_on": row['arrived_on'], "location": row['location'],
                          "attested_by": actor})

    def create(self, validated_data):
        assets = validated_data.pop('asset_ids', [])
        arrivals = validated_data.pop('arrivals', [])
        reason = validated_data.pop('link_reason', "") or "Recorded with the purchase"
        validated_data.pop('attested', None)
        with transaction.atomic():
            procurement = Procurement.objects.create(**validated_data)
            Asset.objects.filter(id__in=[a.id for a in assets]).update(procurement=procurement)
            self._record_arrivals(procurement, arrivals)
            self._record_links(procurement, assets, set(), reason)
        return procurement

    def update(self, instance, validated_data):
        assets = validated_data.pop('asset_ids', None)
        arrivals = validated_data.pop('arrivals', [])
        reason = validated_data.pop('link_reason', "") or "Purchase record edited"
        validated_data.pop('attested', None)
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if assets is not None:
                previous = set(Asset.objects.filter(procurement=instance)
                               .values_list('id', flat=True))
                asset_ids = [asset.id for asset in assets]
                Asset.objects.filter(procurement=instance).exclude(
                    id__in=asset_ids).update(procurement=None)
                Asset.objects.filter(id__in=asset_ids).update(procurement=instance)
                self._record_arrivals(instance, arrivals)
                self._record_links(instance, assets, previous, reason)

        return instance


class CheckoutSerializer(serializers.ModelSerializer):
    asset_details = AssetLiteSerializer(source='asset', read_only=True)
    user_details = UserLiteSerializer(source='user', read_only=True)
    approved_by_details = UserLiteSerializer(source='approved_by', read_only=True)

    class Meta:
        model = AssetCheckout
        fields = "__all__"
        # return_condition and return_remarks are written by check_in, not by a
        # client PATCH — the checkout record is created with intake data only.
        read_only_fields = ('checkout_date', 'return_date', 'approved_by',
                            'return_condition', 'return_remarks', 'status')


class TransferSerializer(serializers.ModelSerializer):
    asset_details = AssetLiteSerializer(source='asset', read_only=True)
    previous_owner_details = UserLiteSerializer(source='previous_owner', read_only=True)
    new_owner_details = UserLiteSerializer(source='new_owner', read_only=True)
    previous_department_details = DepartmentSerializer(source='previous_department', read_only=True)
    new_department_details = DepartmentSerializer(source='new_department', read_only=True)
    requested_by_details = UserLiteSerializer(source='requested_by', read_only=True)
    approved_by_details = UserLiteSerializer(source='approved_by', read_only=True)
    transfer_code = serializers.SerializerMethodField()

    class Meta:
        model = AssetTransfer
        fields = "__all__"
        read_only_fields = ('previous_owner', 'previous_department', 'transfer_date',
                            'requested_by', 'approved_by', 'status')

    def get_transfer_code(self, obj):
        return f"TRF-{obj.id:05d}"


class ConditionLogSerializer(serializers.ModelSerializer):
    inspector_details = UserLiteSerializer(source='inspector', read_only=True)

    class Meta:
        model = AssetConditionLog
        fields = "__all__"


class ServiceRecordSerializer(serializers.ModelSerializer):
    asset_details = AssetLiteSerializer(source='asset', read_only=True)
    vendor_details = VendorSerializer(source='vendor', read_only=True)
    opened_by_details = UserLiteSerializer(source='opened_by', read_only=True)
    closed_by_details = UserLiteSerializer(source='closed_by', read_only=True)

    class Meta:
        model = ServiceRecord
        fields = "__all__"
        read_only_fields = ('sent_date', 'returned_date', 'opened_by', 'closed_by',
                            'cost', 'status')


class AmcContractSerializer(serializers.ModelSerializer):
    vendor_details = VendorSerializer(source='vendor', read_only=True)

    class Meta:
        model = AmcContract
        fields = "__all__"
