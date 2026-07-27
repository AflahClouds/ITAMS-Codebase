from django.db.models import Max
from rest_framework import status as http_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.exports import build_transfer_pdf
from core.models import Setting
from core.permissions import HasRolePermission
from core.services import get_profile, log_action, notify

from .barcodes import generate_asset_barcode
from .checkout import check_in, check_out
from .models import (ASSET_CONDITIONS, TERMINAL_STATUSES, Asset, AssetCheckout,
                     AssetConditionLog, AssetDocument, AssetImage,
                     AssetTransfer, LifecycleError, Procurement, ServiceRecord)
from .serializers import (AssetDocumentSerializer, AssetImageSerializer,
                          AssetSerializer, CheckoutSerializer,
                          ConditionLogSerializer, ProcurementSerializer,
                          ServiceRecordSerializer, TransferSerializer)
from .service import close_service, open_service
from .transfer import approve as approve_transfer
from .transfer import reject as reject_transfer
from .transfer import request_transfer


# ---------- Assets ----------

def _notify_it_managers(message, link=""):
    from accounts.models import User
    for manager in User.objects.filter(role__name="IT Manager", status="Active"):
        notify(manager, message, link=link)


class AssetViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"list": "asset_view", "retrieve": "asset_view",
                      "create": "asset_create", "update": "asset_edit",
                      "partial_update": "asset_edit", "destroy": "asset_delete",
                      "add_condition": "asset_edit", "history": "asset_view",
                      "renew_amc": "asset_edit", "end_amc_support": "asset_edit"}
    queryset = Asset.objects.all().select_related(
        'category', 'brand', 'model', 'location', 'custodian', 'department',
        'procurement').order_by('-id')
    serializer_class = AssetSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('status'):
            qs = qs.filter(status=p['status'])
        if p.get('category'):
            qs = qs.filter(category_id=p['category'])
        if p.get('q'):
            from django.db.models import Q
            like = p['q']
            qs = qs.filter(Q(asset_id__icontains=like) | Q(name__icontains=like) |
                           Q(tag_number__icontains=like) | Q(serial_number__icontains=like))
        return qs

    def perform_create(self, serializer):
        asset = serializer.save()
        asset.barcode_path = generate_asset_barcode(asset)
        asset.save(update_fields=['barcode_path'])
        log_action(self.request, "Create", "Assets",
                   new_value=f"{asset.asset_id} - {asset.name or asset.serial_number}")

    def perform_update(self, serializer):
        old = serializer.instance
        old_desc = f"{old.asset_id} | {old.status} | {old.condition}"
        asset = serializer.save()
        asset.barcode_path = generate_asset_barcode(asset)
        asset.save(update_fields=['barcode_path'])
        log_action(self.request, "Update", "Assets", old_value=old_desc,
                   new_value=f"{asset.asset_id} | {asset.status} | {asset.condition}")

    def perform_destroy(self, instance):
        log_action(self.request, "Delete", "Assets",
                   old_value=f"{instance.asset_id} - {instance.name or instance.serial_number}")
        instance.delete()

    @action(detail=True, methods=['post'])
    def add_condition(self, request, pk=None):
        asset = self.get_object()
        condition = request.data.get('condition')
        notes = (request.data.get('notes') or "").strip()
        if condition not in ASSET_CONDITIONS:
            return Response({"detail": f"Condition must be one of {ASSET_CONDITIONS}"},
                            status=http_status.HTTP_400_BAD_REQUEST)
        AssetConditionLog.objects.create(
            asset=asset, inspector=get_profile(request), condition=condition, notes=notes)
        old = asset.condition
        asset.condition = condition
        asset.save(update_fields=['condition', 'modified'])
        log_action(request, "Condition Update", "Assets", old_value=old, new_value=condition)
        return Response(AssetSerializer(asset).data)

    @action(detail=True, methods=['post'])
    def renew_amc(self, request, pk=None):
        asset = self.get_object()
        if asset.status in TERMINAL_STATUSES:
            return Response(
                {"detail": f"Cannot renew AMC on a {asset.status} asset."},
                status=http_status.HTTP_400_BAD_REQUEST)
        amc_start = request.data.get('amc_start')
        amc_end = request.data.get('amc_end')
        if not amc_start or not amc_end:
            return Response({"detail": "amc_start and amc_end are required."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        asset.has_amc = True
        asset.amc_start = amc_start
        asset.amc_end = amc_end
        asset.amc_status = "Active"
        asset.amc_end_reason = ""
        asset.save(update_fields=['has_amc', 'amc_start', 'amc_end', 'amc_status',
                                  'amc_end_reason', 'modified'])
        description = f"AMC renewed for {asset.asset_id}: {amc_start} to {amc_end}"
        log_action(request, "AMC Renewed", "Assets", new_value=description)
        _notify_it_managers(description)
        return Response(AssetSerializer(asset).data)

    @action(detail=True, methods=['post'])
    def end_amc_support(self, request, pk=None):
        asset = self.get_object()
        reason = (request.data.get('reason') or "").strip()
        if not reason:
            return Response({"detail": "A reason is required to end AMC support."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        asset.amc_status = "Ended"
        asset.amc_end_reason = reason
        asset.save(update_fields=['amc_status', 'amc_end_reason', 'modified'])
        description = f"AMC support ended for {asset.asset_id}: {reason}"
        log_action(request, "AMC Ended", "Assets", new_value=description)
        _notify_it_managers(description)
        return Response(AssetSerializer(asset).data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        asset = self.get_object()
        return Response({
            "checkouts": CheckoutSerializer(
                asset.checkouts.order_by('-checkout_date'), many=True).data,
            "transfers": TransferSerializer(
                asset.transfers.order_by('-transfer_date'), many=True).data,
            "condition_logs": ConditionLogSerializer(
                asset.condition_logs.order_by('-inspection_date'), many=True).data,
            "services": ServiceRecordSerializer(
                asset.service_records.order_by('-sent_date'), many=True).data,
        })


class ProcurementViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"list": "asset_view", "retrieve": "asset_view",
                      "create": "asset_create", "update": "asset_edit",
                      "partial_update": "asset_edit", "destroy": "asset_delete"}
    queryset = Procurement.objects.all().select_related('mode_of_purchase', 'vendor').order_by('-id')
    serializer_class = ProcurementSerializer

    def perform_create(self, serializer):
        proc = serializer.save()
        log_action(self.request, "Create", "Procurement", new_value=proc.invoice_number)

    def perform_update(self, serializer):
        proc = serializer.save()
        log_action(self.request, "Update", "Procurement", new_value=proc.invoice_number)

    def perform_destroy(self, instance):
        log_action(self.request, "Delete", "Procurement", old_value=instance.invoice_number)
        instance.delete()


# ---------- Service Records ----------

class ServiceRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"list": "asset_view", "retrieve": "asset_view",
                      "create": "asset_transfer", "close": "asset_transfer",
                      "*": "__admin__"}
    queryset = ServiceRecord.objects.all().select_related(
        'asset', 'vendor', 'opened_by', 'closed_by').order_by('-sent_date')
    serializer_class = ServiceRecordSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('status'):
            qs = qs.filter(status=self.request.query_params['status'])
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        asset = data['asset']
        vendor = data['vendor']
        try:
            record = open_service(
                asset, vendor, get_profile(request),
                expected_return_date=data.get('expected_return_date'),
                reason=data.get('reason', ""),
                remarks=data.get('remarks', ""),
            )
        except LifecycleError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        log_action(request, "Service Opened", "Service Records",
                   new_value=f"{asset.asset_id} -> {vendor.name}")
        return Response(self.get_serializer(record).data, status=http_status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        record = self.get_object()
        try:
            record = close_service(
                record, get_profile(request),
                cost=request.data.get('cost'), remarks=request.data.get('remarks'))
        except LifecycleError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        log_action(request, "Service Closed", "Service Records",
                   new_value=f"{record.asset.asset_id} returned from {record.vendor.name}")
        return Response(self.get_serializer(record).data)


# ---------- Asset files ----------

def _validate_extension(filename, allowed):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in allowed


class AssetImageViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"list": "asset_view", "retrieve": "asset_view",
                      "create": "asset_edit", "destroy": "asset_delete",
                      "*": "__admin__"}
    serializer_class = AssetImageSerializer

    def get_queryset(self):
        qs = AssetImage.objects.all().select_related('uploaded_by').order_by('-upload_date')
        if self.request.query_params.get('asset'):
            qs = qs.filter(asset_id=self.request.query_params['asset'])
        return qs

    def create(self, request, *args, **kwargs):
        from django.conf import settings as dj
        upload = request.FILES.get('file')
        if not upload:
            return Response({"detail": "Please choose a file to upload."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        if not _validate_extension(upload.name, dj.ALLOWED_IMAGE_EXTENSIONS):
            return Response({"detail": "Unsupported image type. Allowed: jpg, jpeg, png, webp."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.save(uploaded_by=get_profile(request), file_name=upload.name)
        log_action(request, "Image Upload", "Assets",
                   new_value=f"{upload.name} for {image.asset.asset_id}")
        return Response(self.get_serializer(image).data, status=http_status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        log_action(self.request, "Image Delete", "Assets", old_value=instance.file_name)
        instance.file.delete(save=False)
        instance.delete()


class AssetDocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"list": "asset_view", "retrieve": "asset_view",
                      "create": "asset_edit", "destroy": "asset_delete",
                      "*": "__admin__"}
    serializer_class = AssetDocumentSerializer

    def get_queryset(self):
        qs = AssetDocument.objects.all().select_related('uploaded_by').order_by('-upload_date')
        if self.request.query_params.get('asset'):
            qs = qs.filter(asset_id=self.request.query_params['asset'])
        return qs

    def create(self, request, *args, **kwargs):
        from django.conf import settings as dj
        upload = request.FILES.get('file')
        if not upload:
            return Response({"detail": "Please choose a file to upload."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        if not _validate_extension(upload.name, dj.ALLOWED_DOCUMENT_EXTENSIONS):
            return Response({"detail": "Unsupported document type."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        asset = serializer.validated_data['asset']
        doc_type = serializer.validated_data.get('document_type') or "Other"
        version = (AssetDocument.objects.filter(asset=asset, document_type=doc_type)
                   .aggregate(m=Max('version'))['m'] or 0) + 1
        document = serializer.save(uploaded_by=get_profile(request),
                                   file_name=upload.name, version=version)
        log_action(request, "Document Upload", "Assets",
                   new_value=f"{doc_type} v{version} for {asset.asset_id}")
        return Response(self.get_serializer(document).data, status=http_status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        log_action(self.request, "Document Delete", "Assets", old_value=instance.file_name)
        instance.file.delete(save=False)
        instance.delete()


# ---------- Checkouts ----------

class CheckoutViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"list": "asset_view", "retrieve": "asset_view",
                      "create": "asset_transfer", "checkin": "asset_transfer",
                      "*": "__admin__"}
    queryset = AssetCheckout.objects.all().select_related(
        'asset', 'user', 'approved_by').order_by('-checkout_date')
    serializer_class = CheckoutSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('status'):
            qs = qs.filter(status=self.request.query_params['status'])
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        asset = data['asset']
        user = data['user']
        try:
            checkout = check_out(
                asset, user, get_profile(request),
                checkout_condition=data.get('checkout_condition'),
                expected_return_date=data.get('expected_return_date'),
                purpose=data.get('purpose', ""),
                remarks=data.get('remarks', ""),
            )
        except LifecycleError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        log_action(request, "Checkout", "Checkouts",
                   new_value=f"{asset.asset_id} -> {user.user_name} (usage session started)")
        return Response(self.get_serializer(checkout).data, status=http_status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def checkin(self, request, pk=None):
        checkout = self.get_object()
        condition = request.data.get('condition') or "Good"
        try:
            checkout = check_in(checkout, condition, request.data.get('remarks'))
        except LifecycleError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        asset = checkout.asset
        log_action(request, "Check-in", "Checkouts",
                   new_value=f"{asset.asset_id} returned by {checkout.user.user_name} (usage session ended)")
        return Response(self.get_serializer(checkout).data)


# ---------- Transfers ----------

class TransferViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"list": "asset_view", "retrieve": "asset_view",
                      "create": "transfer_request", "approve": "asset_transfer",
                      "reject": "asset_transfer", "*": "__admin__"}
    queryset = AssetTransfer.objects.all().select_related(
        'asset', 'previous_owner', 'new_owner', 'previous_department',
        'new_department', 'requested_by', 'approved_by').order_by('-transfer_date')
    serializer_class = TransferSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('status'):
            qs = qs.filter(status=self.request.query_params['status'])
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        asset = data['asset']
        new_owner = data['new_owner']
        transfer = request_transfer(
            asset, new_owner, get_profile(request),
            new_department=data.get('new_department'),
            condition=data.get('condition'),
            remarks=data.get('remarks', ""),
        )
        log_action(request, "Transfer Request", "Transfers",
                   new_value=f"{asset.asset_id} -> {new_owner.user_name}")
        return Response(self.get_serializer(transfer).data, status=http_status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        transfer = self.get_object()
        try:
            transfer = approve_transfer(transfer, get_profile(request))
        except LifecycleError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        asset = transfer.asset
        log_action(request, "Transfer Approved", "Transfers",
                   new_value=f"{asset.asset_id} -> {transfer.new_owner.user_name}")
        return Response(self.get_serializer(transfer).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        transfer = self.get_object()
        try:
            transfer = reject_transfer(transfer, get_profile(request))
        except LifecycleError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        log_action(request, "Transfer Rejected", "Transfers",
                   old_value=f"TRF-{transfer.id:05d}")
        return Response(self.get_serializer(transfer).data)

    @action(detail=True, methods=['get'], url_path='document')
    def document(self, request, pk=None):
        from django.http import FileResponse
        transfer = self.get_object()
        company = Setting.get("company_name", "Cloud Shoe Factory")
        pdf = build_transfer_pdf(transfer, company_name=company)
        return FileResponse(pdf, as_attachment=True, content_type='application/pdf',
                            filename=f"transfer_TRF-{transfer.id:05d}.pdf")
