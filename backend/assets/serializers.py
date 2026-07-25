from rest_framework import serializers

from accounts.serializers import DepartmentSerializer, LocationSerializer, UserLiteSerializer
from catalog.serializers import (BrandSerializer, CategorySerializer,
                                 ModelSerializer, PurchaseModeSerializer,
                                 VendorSerializer)

from .models import (ASSET_CONDITIONS, ASSET_STATUSES, Asset, AssetCheckout,
                     AssetConditionLog, AssetDocument, AssetImage,
                     AssetTransfer, Procurement, ServiceRecord)


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


class AssetLiteSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category_name', read_only=True)

    class Meta:
        model = Asset
        fields = ('id', 'asset_id', 'name', 'tag_number', 'serial_number',
                  'status', 'condition', 'category_name')


class ProcurementSerializer(serializers.ModelSerializer):
    mode_of_purchase_details = PurchaseModeSerializer(source='mode_of_purchase', read_only=True)
    vendor_details = VendorSerializer(source='vendor', read_only=True)
    assets = AssetSerializer(many=True, read_only=True)
    asset_ids = serializers.PrimaryKeyRelatedField(
        queryset=Asset.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = Procurement
        fields = "__all__"

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
        return assets

    def create(self, validated_data):
        assets = validated_data.pop('asset_ids', [])
        procurement = Procurement.objects.create(**validated_data)
        Asset.objects.filter(id__in=[asset.id for asset in assets]).update(procurement=procurement)
        return procurement

    def update(self, instance, validated_data):
        assets = validated_data.pop('asset_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if assets is not None:
            asset_ids = [asset.id for asset in assets]
            Asset.objects.filter(procurement=instance).exclude(id__in=asset_ids).update(procurement=None)
            Asset.objects.filter(id__in=asset_ids).update(procurement=instance)

        return instance


class CheckoutSerializer(serializers.ModelSerializer):
    asset_details = AssetLiteSerializer(source='asset', read_only=True)
    user_details = UserLiteSerializer(source='user', read_only=True)
    approved_by_details = UserLiteSerializer(source='approved_by', read_only=True)

    class Meta:
        model = AssetCheckout
        fields = "__all__"
        read_only_fields = ('checkout_date', 'return_date', 'approved_by',
                            'return_condition', 'status')


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
