from datetime import date as date_cls

from django.utils import timezone
from django.db import transaction
from django.db.models import Max, Prefetch, Q
from rest_framework import status as http_status
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from catalog.models import Vendor
from core.exports import build_transfer_pdf
from core.models import Setting
from core.permissions import HasRolePermission, NotOwnRecordsScope
from core.services import get_profile, log_action, notify_many

from .barcodes import generate_asset_barcode
from .checkout import check_in, check_out
from .custody import assign, classify_legacy_checkout, reconcile_legacy_checkout, take_back
from .models import (ASSET_CONDITIONS, TERMINAL_STATUSES, AmcContract, Asset,
                     AssetAssignment, AssetCheckout, AssetConditionLog, AssetDocument, AssetImage,
                     AssetTransfer, LifecycleError, Procurement, ServiceRecord)
from .serializers import (AmcContractSerializer, AssignmentSerializer, AssetDocumentSerializer,
                          AssetImageSerializer, AssetSerializer,
                          CheckoutSerializer, ConditionLogSerializer,
                          ProcurementSerializer, ServiceRecordSerializer,
                          TransferSerializer)
from .service import close_service, open_service
from .transfer import approve as approve_transfer
from .transfer import reject as reject_transfer
from .transfer import request_transfer


# ---------- Assets ----------

def scoped_profile(request):
    """The profile whose own records bound this request, or None when the reader is
    global. B1 scopes the named Employee Role to its own Assets and the lifecycle
    records it is party to; every other Role reads globally (decision C6).
    """
    profile = get_profile(request)
    if profile is not None and profile.has_own_records_scope():
        return profile
    return None


def _notify_it_managers(message, link=""):
    """Notify the operators who decide AMC contracts.

    Selected by permission code, not by Role display name: a custom Role holding
    `asset_delete` is an IT-Manager-equivalent under B1's custom-Role policy, and a
    Role merely renamed "IT Manager" is not automatically one.
    """
    from accounts.models import users_with_permission
    notify_many(users_with_permission("asset_delete"), message, link=link)


class AssetViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"list": "asset_view", "retrieve": "asset_view",
                      "create": "asset_create", "update": "asset_edit",
                      "partial_update": "asset_edit", "destroy": "asset_delete",
                      "add_condition": "asset_edit", "history": "asset_view",
                      "renew_amc": "asset_edit", "end_amc_support": "asset_edit"}
    queryset = Asset.objects.all().select_related(
        'category', 'brand', 'model', 'location', 'custodian', 'department',
        'procurement').prefetch_related(
        Prefetch('assignments', queryset=AssetAssignment.objects.filter(status="Open"),
                 to_attr='active_assignments'),
        Prefetch('checkouts', queryset=AssetCheckout.objects.filter(status="Open"),
                 to_attr='active_checkouts'),
    ).order_by('-id')
    serializer_class = AssetSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        profile = scoped_profile(self.request)
        if profile is not None:
            # Scopes list, retrieve, and every detail action that resolves through
            # get_object(), so an Employee cannot reach a colleague's asset by id.
            qs = qs.filter(custodian=profile)
        p = self.request.query_params
        if p.get('status'):
            qs = qs.filter(status=p['status'])
        if p.get('category'):
            qs = qs.filter(category_id=p['category'])
        if p.get('q'):
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
        try:
            amc_start = date_cls.fromisoformat(str(amc_start))
            amc_end = date_cls.fromisoformat(str(amc_end))
        except ValueError:
            return Response({"detail": "amc_start and amc_end must be valid dates (YYYY-MM-DD)."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        if amc_end <= amc_start:
            return Response({"detail": "amc_end must be after amc_start."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        # A dated contract is with somebody: vendor-grouped AMC reporting is the point
        # of Vendor being a managed entity. Only an Incomplete contract may lack one.
        vendor_id = request.data.get('vendor')
        if not vendor_id:
            return Response({"detail": "A vendor is required to renew an AMC."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        vendor = Vendor.objects.filter(pk=vendor_id).first()
        if vendor is None:
            return Response({"detail": "That vendor does not exist."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            # The supersede marker is a flag, not text in the operator's reason field
            # (FR-034): "this was replaced" and "an operator decided to stop" are
            # different events and must stay distinguishable.
            AmcContract.objects.filter(asset=asset, status__in=("Active", "Incomplete")).update(
                status="Ended", superseded_by_renewal=True)
            AmcContract.objects.create(
                asset=asset, vendor=vendor, start_date=amc_start, end_date=amc_end,
                status="Active")
        description = f"AMC renewed for {asset.asset_id}: {amc_start} to {amc_end}"
        log_action(request, "AMC Renewed", "Assets", new_value=description)
        _notify_it_managers(description)
        return Response(AssetSerializer(asset).data)

    @action(detail=True, methods=['post'])
    def end_amc_support(self, request, pk=None):
        asset = self.get_object()
        # Renewal already refuses a terminal Asset; End Support must too (FR-011,
        # ALR-003). A Sold, Scrapped, or Lost Asset has left circulation, and there is
        # no support decision left to take on it.
        if asset.status in TERMINAL_STATUSES:
            return Response(
                {"detail": f"Cannot end AMC support on a {asset.status} asset."},
                status=http_status.HTTP_400_BAD_REQUEST)
        reason = (request.data.get('reason') or "").strip()
        if not reason:
            return Response({"detail": "A reason is required to end AMC support."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        contract = asset.amc_contracts.filter(
            status__in=("Active", "Incomplete")).order_by('-id').first()
        if not contract:
            return Response({"detail": "This asset has no active AMC to end."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        contract.status = "Ended"
        contract.end_reason = reason
        contract.save(update_fields=['status', 'end_reason'])
        description = f"AMC support ended for {asset.asset_id}: {reason}"
        log_action(request, "AMC Ended", "Assets", new_value=description)
        _notify_it_managers(description)
        return Response(AssetSerializer(asset).data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        asset = self.get_object()
        return Response({
            "assignments": AssignmentSerializer(
                asset.assignments.order_by('-issued_at'), many=True).data,
            "checkouts": CheckoutSerializer(
                asset.checkouts.order_by('-checkout_date'), many=True).data,
            "transfers": TransferSerializer(
                asset.transfers.order_by('-transfer_date'), many=True).data,
            "condition_logs": ConditionLogSerializer(
                asset.condition_logs.order_by('-inspection_date'), many=True).data,
            "services": ServiceRecordSerializer(
                asset.service_records.order_by('-sent_date'), many=True).data,
            "amc_contracts": AmcContractSerializer(
                asset.amc_contracts.order_by('-id'), many=True).data,
        })


class ProcurementViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission, NotOwnRecordsScope]
    permission_map = {"list": "asset_view", "retrieve": "asset_view",
                      "create": "asset_create", "update": "asset_edit",
                      "partial_update": "asset_edit", "destroy": "asset_delete"}
    queryset = Procurement.objects.all().select_related('mode_of_purchase', 'vendor').order_by('-id')
    serializer_class = ProcurementSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Archived purchases stay readable by asking for them, but they are not part of
        # the working list (FR-011).
        if self.action == "list" and self.request.query_params.get('archived') != '1':
            qs = qs.filter(archived=False)
        return qs

    def perform_create(self, serializer):
        proc = serializer.save()
        log_action(self.request, "Create", "Procurement", new_value=proc.invoice_number)

    def perform_update(self, serializer):
        proc = serializer.save()
        log_action(self.request, "Update", "Procurement", new_value=proc.invoice_number)

    def perform_destroy(self, instance):
        """Archive rather than delete.

        B6 FR-011 forbids destroying a purchase record: the invoice, the dates, the
        Vendor, and the link history are the evidence that the organization bought the
        thing, and a mistaken click should not be able to erase it. The Assets stay
        linked, so the purchase they came from remains answerable.
        """
        instance.archived = True
        instance.archived_at = timezone.now()
        instance.archive_reason = (self.request.data.get('reason') or "").strip()
        instance.save(update_fields=['archived', 'archived_at', 'archive_reason'])
        log_action(self.request, "Archive", "Procurement",
                   old_value=instance.invoice_number,
                   new_value=instance.archive_reason or "no reason given")


# ---------- Service Records ----------

class ServiceRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"list": "asset_view", "retrieve": "asset_view",
                      "create": "asset_custody_manage", "close": "asset_custody_manage",
                      "*": "__admin__"}
    queryset = ServiceRecord.objects.all().select_related(
        'asset', 'vendor', 'opened_by', 'closed_by').order_by('-sent_date')
    serializer_class = ServiceRecordSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        profile = scoped_profile(self.request)
        if profile is not None:
            # A Service Record names no User, so it is visible through the Asset:
            # the repair history of something the Employee currently holds. Opening a
            # Service Record clears custody, so an in-flight repair is not visible.
            qs = qs.filter(asset__custodian=profile)
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
        profile = scoped_profile(self.request)
        if profile is not None:
            # Files inherit their Asset's visibility — otherwise the register is
            # scoped but everything attached to it is not.
            qs = qs.filter(asset__custodian=profile)
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
        profile = scoped_profile(self.request)
        if profile is not None:
            qs = qs.filter(asset__custodian=profile)
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


# ---------- Ongoing Assignments ----------

class AssignmentViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"list": "asset_view", "retrieve": "asset_view",
                      "create": "asset_custody_manage", "take_back": "asset_custody_manage"}
    serializer_class = AssignmentSerializer
    queryset = AssetAssignment.objects.all().select_related(
        'asset', 'user', 'issued_by', 'closed_by').order_by('-issued_at', '-id')

    def get_queryset(self):
        qs = super().get_queryset()
        profile = scoped_profile(self.request)
        if profile is not None:
            qs = qs.filter(user=profile)
        asset_id = self.request.query_params.get('asset')
        if asset_id:
            qs = qs.filter(asset_id=asset_id)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            assignment = assign(
                data['asset'], data['user'], get_profile(request),
                remarks=data.get('remarks', ""), request=request,
            )
        except LifecycleError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(assignment).data,
                        status=http_status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='take-back')
    def take_back(self, request, pk=None):
        assignment = self.get_object()
        try:
            result = take_back(assignment, request.data.get('condition'),
                               get_profile(request), remarks=request.data.get('remarks', ''),
                               request=request)
        except LifecycleError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(result).data)


# ---------- Checkouts ----------

class CheckoutViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"list": "asset_view", "retrieve": "asset_view",
                      "create": "asset_custody_manage", "checkin": "asset_custody_manage",
                      "classify": "asset_custody_manage", "reconcile": "asset_custody_manage",
                      "*": "__admin__"}
    queryset = AssetCheckout.objects.all().select_related(
        'asset', 'user', 'approved_by').prefetch_related(
        Prefetch('asset__assignments',
                 queryset=AssetAssignment.objects.filter(status="Open"),
                 to_attr='active_assignments'),
        Prefetch('asset__checkouts',
                 queryset=AssetCheckout.objects.filter(status="Open"),
                 to_attr='active_checkouts'),
    ).order_by('-checkout_date')
    serializer_class = CheckoutSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        profile = scoped_profile(self.request)
        if profile is not None:
            # A Checkout directly involves the Employee it was issued to.
            qs = qs.filter(user=profile)
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
        try:
            checkout = check_in(checkout, request.data.get('condition'),
                                request.data.get('remarks'),
                                performed_by=get_profile(request))
        except LifecycleError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        asset = checkout.asset
        log_action(request, "Check-in", "Checkouts",
                   new_value=f"{asset.asset_id} returned by {checkout.user.user_name} (usage session ended)")
        return Response(self.get_serializer(checkout).data)

    @action(detail=True, methods=['post'])
    def classify(self, request, pk=None):
        checkout = self.get_object()
        try:
            checkout = classify_legacy_checkout(
                checkout, request.data.get('custody_type'), get_profile(request),
                remarks=request.data.get('remarks', ''), request=request)
        except LifecycleError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(checkout).data)

    @action(detail=True, methods=['post'])
    def reconcile(self, request, pk=None):
        checkout = self.get_object()
        try:
            transfer = AssetTransfer.objects.get(pk=request.data.get('approved_transfer'))
            checkout = reconcile_legacy_checkout(
                checkout, transfer, request.data.get('custody_type'),
                get_profile(request), remarks=request.data.get('remarks', ''),
                request=request)
        except (AssetTransfer.DoesNotExist, ValueError, TypeError):
            return Response({"detail": "Select a recorded approved Transfer."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        except LifecycleError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(checkout).data)


# ---------- Transfers ----------

class TransferViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"list": "asset_view", "retrieve": "asset_view",
                      "create": "transfer_request", "approve": "asset_custody_manage",
                      "reject": "asset_custody_manage", "document": "asset_view",
                      "*": "__admin__"}
    queryset = AssetTransfer.objects.all().select_related(
        'asset', 'previous_owner', 'new_owner', 'previous_department',
        'new_department', 'requested_by', 'approved_by').order_by('-transfer_date')
    serializer_class = TransferSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        profile = scoped_profile(self.request)
        if profile is not None:
            # A Transfer is a record the Employee is party to only when it moves custody
            # to or from them. This scopes the list and, through get_object(), the
            # Transfer document — `asset_view` opens the PDF for the records a reader
            # can already see, not for every Transfer in the system.
            qs = qs.filter(Q(previous_owner=profile) | Q(new_owner=profile))
        if self.request.query_params.get('status'):
            qs = qs.filter(status=self.request.query_params['status'])
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        asset = data['asset']
        new_owner = data['new_owner']
        try:
            transfer = request_transfer(
                asset, new_owner, get_profile(request),
                new_department=data.get('new_department'),
                condition=data.get('condition'),
                remarks=data.get('remarks', ""),
                request=request,
            )
        except LifecycleError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(transfer).data, status=http_status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        transfer = self.get_object()
        try:
            transfer = approve_transfer(transfer, get_profile(request), request=request)
        except LifecycleError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(transfer).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        transfer = self.get_object()
        try:
            transfer = reject_transfer(transfer, get_profile(request), request=request)
        except LifecycleError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(transfer).data)

    @action(detail=True, methods=['get'], url_path='document')
    def document(self, request, pk=None):
        from django.http import FileResponse
        transfer = self.get_object()
        company = Setting.get("company_name", "Cloud Shoe Factory")
        pdf = build_transfer_pdf(transfer, company_name=company)
        return FileResponse(pdf, as_attachment=True, content_type='application/pdf',
                            filename=f"transfer_TRF-{transfer.id:05d}.pdf")
