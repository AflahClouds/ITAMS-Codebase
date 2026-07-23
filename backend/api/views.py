from datetime import date, timedelta

from django.contrib.auth import authenticate
from django.db.models.deletion import ProtectedError
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import status as http_status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (ASSET_CONDITIONS, ASSET_STATUSES, Asset, AssetCheckout,
                     AssetConditionLog, AssetDocument, AssetImage,
                     AssetTransfer, AuditLog, Brand, Category, Department,
                     Location, Model, Notification, Permission, Procurement,
                     PurchaseMode, Role, Setting, User, users_with_permission)
from .permissions import HasRolePermission
from .serializers import (AssetDocumentSerializer, AssetImageSerializer,
                          AssetSerializer, AuditLogSerializer, BrandSerializer,
                          CategorySerializer, CheckoutSerializer,
                          ConditionLogSerializer, DepartmentSerializer,
                          LocationSerializer, ModelSerializer,
                          NotificationSerializer, PermissionSerializer,
                          ProcurementSerializer, PurchaseModeSerializer,
                          RoleSerializer, SettingSerializer,
                          TransferSerializer, UserLiteSerializer,
                          UserSerializer)
from .services import generate_asset_barcode, get_profile, log_action, notify

MASTER_WRITE = {"create": "settings_access", "update": "settings_access",
                "partial_update": "settings_access", "destroy": "settings_access"}


def _permissions_for(profile):
    if profile is None:
        return []
    if profile.role and profile.role.name == "Admin":
        return list(Permission.objects.values_list("code", flat=True))
    if profile.role:
        return list(profile.role.permissions.values_list("code", flat=True))
    return []


def _auth_payload(account, token):
    profile = getattr(account, "profile", None)
    return {
        "token": token.key,
        "user": {
            "id": profile.id if profile else None,
            "username": account.username,
            "user_name": profile.user_name if profile else account.username,
            "emp_id": profile.emp_id if profile else "",
            "email": profile.email_id if profile else account.email,
            "designation": profile.designation if profile else "",
            "department": profile.department.name if profile and profile.department else None,
            "role": profile.role.name if profile and profile.role else None,
            "permissions": _permissions_for(profile),
            "is_admin": bool(profile and profile.role and profile.role.name == "Admin")
                        or account.is_superuser,
        },
    }


# ---------- Auth ----------

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        password = request.data.get("password") or ""
        account = authenticate(username=username, password=password)
        if account is None:
            AuditLog.objects.create(username=username, action="Login Failed",
                                    module="Auth", new_value="Invalid credentials")
            return Response({"detail": "Invalid username or password."},
                            status=http_status.HTTP_401_UNAUTHORIZED)
        profile = getattr(account, "profile", None)
        if profile is not None and profile.status != "Active":
            return Response({"detail": "This account is disabled."},
                            status=http_status.HTTP_403_FORBIDDEN)
        account.last_login = timezone.now()
        account.save(update_fields=["last_login"])
        token, _ = Token.objects.get_or_create(user=account)
        AuditLog.objects.create(user=profile, username=account.username,
                                action="Login", module="Auth")
        return Response(_auth_payload(account, token))


class LogoutView(APIView):
    def post(self, request):
        log_action(request, "Logout", "Auth")
        Token.objects.filter(user=request.user).delete()
        return Response({"detail": "Logged out."})


class MeView(APIView):
    def get(self, request):
        token, _ = Token.objects.get_or_create(user=request.user)
        return Response(_auth_payload(request.user, token))


class ChangePasswordView(APIView):
    def post(self, request):
        old = request.data.get("old_password") or ""
        new = request.data.get("new_password") or ""
        if not request.user.check_password(old):
            return Response({"detail": "Current password is incorrect."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        if len(new) < 6:
            return Response({"detail": "New password must be at least 6 characters."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        request.user.set_password(new)
        request.user.save()
        Token.objects.filter(user=request.user).delete()
        token = Token.objects.create(user=request.user)
        log_action(request, "Change Password", "Auth")
        return Response({"detail": "Password changed.", "token": token.key})


# ---------- Masters ----------

class ProtectedMasterDeleteMixin:
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return Response(
                {"detail": "Cannot delete this master record because it is in use."},
                status=http_status.HTTP_409_CONFLICT,
            )
        return Response(status=http_status.HTTP_204_NO_CONTENT)


class CategoryViewSet(ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = MASTER_WRITE
    queryset = Category.objects.all().order_by('category_name')
    serializer_class = CategorySerializer


class BrandViewSet(ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = MASTER_WRITE
    queryset = Brand.objects.all().order_by('brand_name')
    serializer_class = BrandSerializer


class ModelViewSet(ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = MASTER_WRITE
    queryset = Model.objects.all().order_by('model_name')
    serializer_class = ModelSerializer


class PurchaseModeViewSet(ProtectedMasterDeleteMixin, viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = MASTER_WRITE
    queryset = PurchaseMode.objects.all().order_by('purchase_mode')
    serializer_class = PurchaseModeSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = MASTER_WRITE
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer


class LocationViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = MASTER_WRITE
    queryset = Location.objects.all().order_by('name')
    serializer_class = LocationSerializer


# ---------- RBAC admin ----------

class RoleViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"*": "__admin__"}
    queryset = Role.objects.all().order_by('id')
    serializer_class = RoleSerializer

    def perform_create(self, serializer):
        role = serializer.save()
        log_action(self.request, "Create Role", "Roles", new_value=role.name)

    def perform_update(self, serializer):
        role = serializer.save()
        codes = ", ".join(role.permissions.values_list("code", flat=True)) or "none"
        log_action(self.request, "Update Role Permissions", "Roles",
                   new_value=f"{role.name}: {codes}")

    def perform_destroy(self, instance):
        log_action(self.request, "Delete Role", "Roles", old_value=instance.name)
        instance.delete()


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"*": "__admin__"}
    queryset = Permission.objects.all().order_by('id')
    serializer_class = PermissionSerializer


# ---------- Users ----------

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"list": "user_management", "retrieve": "user_management",
                      "create": "user_management", "update": "user_management",
                      "partial_update": "user_management", "destroy": "__admin__",
                      "directory": "asset_view"}
    queryset = User.objects.all().select_related('department', 'role').order_by('id')
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'])
    def directory(self, request):
        users = User.objects.filter(status="Active").select_related(
            'department').order_by('user_name')
        return Response(UserLiteSerializer(users, many=True).data)

    def perform_create(self, serializer):
        user = serializer.save()
        log_action(self.request, "Create User", "Users", new_value=user.user_name)

    def perform_update(self, serializer):
        old = serializer.instance
        old_desc = f"{old.user_name}|{old.role.name if old.role else '-'}|{old.status}"
        user = serializer.save()
        log_action(self.request, "Update User", "Users", old_value=old_desc,
                   new_value=f"{user.user_name}|{user.role.name if user.role else '-'}|{user.status}")

    def destroy(self, request, pk=None):
        user = self.get_object()
        me = get_profile(request)
        if me and me.id == user.id:
            return Response({"detail": "You cannot delete your own account."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        if user.held_assets.exists():
            return Response({"detail": "Cannot delete: this user still holds assets. Transfer them first."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        log_action(request, "Delete User", "Users", old_value=user.user_name)
        if user.account:
            user.account.delete()
        user.delete()
        return Response(status=http_status.HTTP_204_NO_CONTENT)


# ---------- Assets ----------

class AssetViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"list": "asset_view", "retrieve": "asset_view",
                      "create": "asset_create", "update": "asset_edit",
                      "partial_update": "asset_edit", "destroy": "asset_delete",
                      "add_condition": "asset_edit", "history": "asset_view"}
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
        })


class ProcurementViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"list": "asset_view", "retrieve": "asset_view",
                      "create": "asset_create", "update": "asset_edit",
                      "partial_update": "asset_edit", "destroy": "asset_delete"}
    queryset = Procurement.objects.all().select_related('mode_of_purchase').order_by('-id')
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
        from django.db.models import Max
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
        asset = serializer.validated_data['asset']
        if asset.status != "Available":
            return Response({"detail": "This asset is not available for checkout."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data['user']
        checkout = serializer.save(
            approved_by=get_profile(request),
            checkout_condition=serializer.validated_data.get('checkout_condition') or asset.condition)
        asset.status = "Assigned"
        asset.custodian = user
        if user.department:
            asset.department = user.department
        asset.save()
        log_action(request, "Checkout", "Checkouts",
                   new_value=f"{asset.asset_id} -> {user.user_name} (usage session started)")
        notify(user, f"Asset {asset.asset_id} has been checked out to you.",
               link=f"/asset/{asset.id}")
        return Response(self.get_serializer(checkout).data, status=http_status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def checkin(self, request, pk=None):
        checkout = self.get_object()
        if checkout.status == "Returned":
            return Response({"detail": "This checkout is already closed."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        condition = request.data.get('condition') or "Good"
        if condition not in ASSET_CONDITIONS:
            return Response({"detail": f"Condition must be one of {ASSET_CONDITIONS}"},
                            status=http_status.HTTP_400_BAD_REQUEST)
        checkout.return_date = timezone.now()
        checkout.return_condition = condition
        checkout.remarks = (request.data.get('remarks') or "").strip()
        checkout.status = "Returned"
        checkout.save()
        asset = checkout.asset
        asset.status = "Available"
        asset.custodian = None
        asset.condition = condition
        asset.save()
        log_action(request, "Check-in", "Checkouts",
                   new_value=f"{asset.asset_id} returned by {checkout.user.user_name} (usage session ended)")
        notify(checkout.user, f"Asset {asset.asset_id} check-in recorded. Thank you.",
               link=f"/asset/{asset.id}")
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
        asset = serializer.validated_data['asset']
        new_owner = serializer.validated_data['new_owner']
        transfer = serializer.save(
            previous_owner=asset.custodian,
            previous_department=asset.department,
            new_department=serializer.validated_data.get('new_department') or new_owner.department,
            requested_by=get_profile(request),
            condition=serializer.validated_data.get('condition') or asset.condition,
        )
        log_action(request, "Transfer Request", "Transfers",
                   new_value=f"{asset.asset_id} -> {new_owner.user_name}")
        for approver in users_with_permission("asset_transfer"):
            notify(approver, f"Transfer request for {asset.asset_id} awaiting approval.",
                   link="/transfer?status=Pending")
        return Response(self.get_serializer(transfer).data, status=http_status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        transfer = self.get_object()
        if transfer.status != "Pending":
            return Response({"detail": "This transfer has already been processed."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        transfer.status = "Approved"
        transfer.approved_by = get_profile(request)
        transfer.transfer_date = timezone.now()
        transfer.save()
        asset = transfer.asset
        asset.custodian = transfer.new_owner
        asset.department = transfer.new_department or asset.department
        asset.status = "Assigned"
        if transfer.condition:
            asset.condition = transfer.condition
        asset.save()
        log_action(request, "Transfer Approved", "Transfers",
                   new_value=f"{asset.asset_id} -> {transfer.new_owner.user_name}")
        notify(transfer.new_owner,
               f"Asset {asset.asset_id} has been transferred to you.", link=f"/asset/{asset.id}")
        if transfer.previous_owner:
            notify(transfer.previous_owner,
                   f"Asset {asset.asset_id} has been transferred from your custody.",
                   link=f"/asset/{asset.id}")
        return Response(self.get_serializer(transfer).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        transfer = self.get_object()
        if transfer.status != "Pending":
            return Response({"detail": "This transfer has already been processed."},
                            status=http_status.HTTP_400_BAD_REQUEST)
        transfer.status = "Rejected"
        transfer.approved_by = get_profile(request)
        transfer.save()
        log_action(request, "Transfer Rejected", "Transfers",
                   old_value=f"TRF-{transfer.id:05d}")
        if transfer.requested_by:
            notify(transfer.requested_by,
                   f"Transfer request TRF-{transfer.id:05d} was rejected.", link="/transfer")
        return Response(self.get_serializer(transfer).data)

    @action(detail=True, methods=['get'], url_path='document')
    def document(self, request, pk=None):
        from django.http import FileResponse
        from .exports import build_transfer_pdf
        transfer = self.get_object()
        company = Setting.get("company_name", "Cloud Shoe Factory")
        pdf = build_transfer_pdf(transfer, company_name=company)
        return FileResponse(pdf, as_attachment=True, content_type='application/pdf',
                            filename=f"transfer_TRF-{transfer.id:05d}.pdf")


# ---------- Notifications ----------

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"*": None}
    serializer_class = NotificationSerializer

    def get_queryset(self):
        profile = get_profile(self.request)
        if profile is None:
            return Notification.objects.none()
        return profile.notifications.order_by('-created')

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        return Response({"count": self.get_queryset().filter(status="Unread").count()})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        n = self.get_object()
        n.status = "Read"
        n.save(update_fields=['status'])
        return Response({"detail": "ok"})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().filter(status="Unread").update(status="Read")
        return Response({"detail": "ok"})


# ---------- Audit ----------

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"*": "__admin__"}
    serializer_class = AuditLogSerializer

    def get_queryset(self):
        qs = AuditLog.objects.all().order_by('-date')
        p = self.request.query_params
        if p.get('module'):
            qs = qs.filter(module=p['module'])
        if p.get('username'):
            qs = qs.filter(username__icontains=p['username'])
        return qs[:1000]


# ---------- Settings ----------

class SettingViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRolePermission]
    permission_map = {"*": "__admin__"}
    queryset = Setting.objects.all().order_by('key')
    serializer_class = SettingSerializer

    def create(self, request, *args, **kwargs):
        """Upsert by key so the settings page can save key/value pairs directly."""
        key = request.data.get('key')
        if not key:
            return Response({"detail": "key is required"}, status=http_status.HTTP_400_BAD_REQUEST)
        Setting.set(key, request.data.get('value') or "")
        log_action(request, "Update Setting", "Settings", new_value=key)
        return Response(SettingSerializer(Setting.objects.get(key=key)).data)


# ---------- Dashboard / charts / reports ----------

@api_view(['GET'])
def dashboard(request):
    today = date.today()
    soon = today + timedelta(days=30)
    qs = Asset.objects
    kpis = {
        "total_assets": qs.count(),
        "active": qs.filter(status__in=["Available", "Assigned"]).count(),
        "available": qs.filter(status="Available").count(),
        "assigned": qs.filter(status="Assigned").count(),
        "repair": qs.filter(status="Under Repair").count(),
        "expiring": qs.filter(warranty_end__range=(today, soon)).count(),
        "expired": qs.filter(warranty_end__lt=today).count(),
        "total_value": float(qs.aggregate(v=Sum('purchase_cost'))['v'] or 0),
        "open_checkouts": AssetCheckout.objects.filter(status="Open").count(),
        "pending_transfers": AssetTransfer.objects.filter(status="Pending").count(),
    }
    from .serializers import AssetLiteSerializer
    recent_transfers = TransferSerializer(
        AssetTransfer.objects.select_related('asset', 'new_owner', 'previous_owner')
        .order_by('-transfer_date')[:5], many=True).data
    open_checkouts = CheckoutSerializer(
        AssetCheckout.objects.filter(status="Open").select_related('asset', 'user')
        .order_by('-checkout_date')[:5], many=True).data
    expiring_assets = AssetSerializer(
        Asset.objects.filter(warranty_end__range=(today, soon))
        .order_by('warranty_end')[:5], many=True).data
    return Response({"kpis": kpis, "recent_transfers": recent_transfers,
                     "open_checkouts": open_checkouts, "expiring_assets": expiring_assets})


def _last_12_months():
    months = []
    first = date.today().replace(day=1)
    for i in range(11, -1, -1):
        y, m = first.year, first.month - i
        while m <= 0:
            m += 12
            y -= 1
        months.append((y, m))
    return months


@api_view(['GET'])
def charts(request, name):
    if name == "category-distribution":
        rows = (Category.objects.annotate(n=Count('asset')).filter(n__gt=0)
                .values_list('category_name', 'n'))
        return Response({"labels": [r[0] for r in rows], "data": [r[1] for r in rows]})

    if name == "status-distribution":
        rows = Asset.objects.values('status').annotate(n=Count('id')).order_by()
        return Response({"labels": [r['status'] for r in rows],
                         "data": [r['n'] for r in rows]})

    if name == "department-usage":
        rows = (Department.objects.annotate(n=Count('asset')).values_list('name', 'n'))
        return Response({"labels": [r[0] for r in rows], "data": [r[1] for r in rows]})

    if name == "purchase-trend":
        labels, data = [], []
        for y, m in _last_12_months():
            start = date(y, m, 1)
            end = date(y + (m == 12), (m % 12) + 1, 1)
            total = (Asset.objects
                     .filter(procurement__purchase_date__gte=start,
                             procurement__purchase_date__lt=end)
                     .aggregate(v=Sum('purchase_cost'))['v'] or 0)
            labels.append(start.strftime("%b %y"))
            data.append(round(float(total), 2))
        return Response({"labels": labels, "data": data})

    if name == "transfer-trend":
        labels, data = [], []
        for y, m in _last_12_months():
            start = date(y, m, 1)
            end = date(y + (m == 12), (m % 12) + 1, 1)
            count = AssetTransfer.objects.filter(
                transfer_date__date__gte=start, transfer_date__date__lt=end,
                status="Approved").count()
            labels.append(start.strftime("%b %y"))
            data.append(count)
        return Response({"labels": labels, "data": data})

    if name == "warranty-timeline":
        today = date.today()
        buckets = [("Expired", None, None), ("0-30 days", 0, 30), ("31-60 days", 31, 60),
                   ("61-90 days", 61, 90), ("90+ days", 91, None)]
        labels, data = [], []
        for label, lo, hi in buckets:
            q = Asset.objects.filter(warranty_end__isnull=False)
            if label == "Expired":
                q = q.filter(warranty_end__lt=today)
            else:
                q = q.filter(warranty_end__gte=today + timedelta(days=lo))
                if hi is not None:
                    q = q.filter(warranty_end__lte=today + timedelta(days=hi))
            labels.append(label)
            data.append(q.count())
        return Response({"labels": labels, "data": data})

    return Response({"detail": "Unknown chart."}, status=http_status.HTTP_404_NOT_FOUND)


def _report_register():
    rows = []
    for a in Asset.objects.select_related('category', 'custodian', 'department', 'location').order_by('id'):
        rows.append([a.asset_id, a.tag_number, a.name or "-",
                     a.category.category_name if a.category else "-",
                     a.serial_number,
                     a.custodian.user_name if a.custodian else "-",
                     a.department.name if a.department else "-",
                     a.location.name if a.location else "-",
                     a.status, float(a.purchase_cost or 0)])
    return (["Asset ID", "Tag No", "Name", "Category", "Serial No", "Owner",
             "Department", "Location", "Status", "Value"], rows)


def _report_movement():
    rows = []
    for t in AssetTransfer.objects.select_related('asset', 'previous_owner', 'new_owner', 'approved_by').order_by('-transfer_date'):
        rows.append([f"TRF-{t.id:05d}", t.asset.asset_id, t.asset.name or "-",
                     t.previous_owner.user_name if t.previous_owner else "IT Store",
                     t.new_owner.user_name if t.new_owner else "-",
                     t.transfer_date.strftime("%d-%b-%Y") if t.transfer_date else "-",
                     t.approved_by.user_name if t.approved_by else "-", t.status])
    return (["Transfer ID", "Asset ID", "Asset", "Previous User", "New User",
             "Date", "Approved By", "Status"], rows)


def _report_warranty():
    rows = []
    for a in Asset.objects.filter(warranty_end__isnull=False).select_related('category').order_by('warranty_end'):
        days = a.warranty_days_left
        rows.append([a.asset_id, a.name or "-",
                     a.category.category_name if a.category else "-",
                     a.warranty_start.strftime("%d-%b-%Y") if a.warranty_start else "-",
                     a.warranty_end.strftime("%d-%b-%Y"),
                     "Expired" if days < 0 else f"{days} days left"])
    return (["Asset ID", "Name", "Category", "Warranty Start", "Warranty End", "Status"], rows)


def _report_purchase():
    rows = []
    for a in Asset.objects.filter(procurement__isnull=False).select_related('procurement', 'brand', 'model').order_by('-procurement__purchase_date'):
        rows.append([a.asset_id, a.name or "-", a.procurement.vendor_name,
                     a.procurement.purchase_date.strftime("%d-%b-%Y"),
                     float(a.purchase_cost or 0),
                     a.brand.brand_name if a.brand else "-",
                     a.model.model_name if a.model else "-"])
    return (["Asset ID", "Name", "Vendor", "Purchase Date", "Cost", "Brand", "Model"], rows)


def _report_employee():
    rows = []
    for u in User.objects.filter(status="Active").select_related('department').order_by('user_name'):
        for a in u.held_assets.select_related('category'):
            rows.append([u.user_name, u.department.name if u.department else "-",
                         a.asset_id, a.name or "-",
                         a.category.category_name if a.category else "-",
                         a.status, a.condition])
    return (["Employee", "Department", "Asset ID", "Asset", "Category", "Status", "Condition"], rows)


def _report_audit():
    rows = []
    for log in AuditLog.objects.order_by('-date')[:1000]:
        rows.append([log.date.strftime("%d-%b-%Y %H:%M"), log.username, log.action,
                     log.module, log.old_value or "-", log.new_value or "-",
                     log.ip_address or "-"])
    return (["Date", "User", "Action", "Module", "Old Value", "New Value", "IP Address"], rows)


REPORTS = {
    "register": ("Asset Register Report", _report_register),
    "movement": ("Asset Movement Report", _report_movement),
    "warranty": ("Warranty Expiry Report", _report_warranty),
    "purchase": ("Purchase Report", _report_purchase),
    "employee": ("Employee Asset Report", _report_employee),
    "audit": ("Asset Audit Report", _report_audit),
}


class ReportView(APIView):
    permission_classes = [HasRolePermission]
    required_permission = "report_access"

    def get(self, request, key=None):
        if key is None:
            return Response({"reports": [
                {"key": k, "title": title} for k, (title, _) in REPORTS.items()]})
        if key not in REPORTS:
            return Response({"detail": "Unknown report."}, status=http_status.HTTP_404_NOT_FOUND)
        title, fn = REPORTS[key]
        headers, rows = fn()
        return Response({"key": key, "title": title, "headers": headers, "rows": rows})


class ReportExportView(APIView):
    permission_classes = [HasRolePermission]
    required_permission = "report_access"

    def get(self, request, key, fmt):
        from django.http import FileResponse
        from .exports import build_excel, build_table_pdf
        if key not in REPORTS or fmt not in ("pdf", "excel"):
            return Response({"detail": "Unknown report or format."},
                            status=http_status.HTTP_404_NOT_FOUND)
        title, fn = REPORTS[key]
        headers, rows = fn()
        company = Setting.get("company_name", "Cloud Shoe Factory")
        log_action(request, "Report Export", "Reports", new_value=f"{key} ({fmt})")
        if fmt == "pdf":
            buf = build_table_pdf(title, headers, rows, company_name=company)
            return FileResponse(buf, as_attachment=True, content_type='application/pdf',
                                filename=f"{key}_report.pdf")
        buf = build_excel(title, headers, rows, company_name=company)
        return FileResponse(
            buf, as_attachment=True,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=f"{key}_report.xlsx")
