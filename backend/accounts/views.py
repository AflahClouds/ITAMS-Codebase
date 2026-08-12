from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import status as http_status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import MASTER_WRITE
from core.models import AuditLog
from core.permissions import HasRolePermission
from core.services import get_profile, log_action

from .models import Department, Location, Permission, Role, User
from .serializers import (DepartmentSerializer, LocationSerializer,
                          PermissionSerializer, RoleSerializer,
                          UserLiteSerializer, UserSerializer)


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
        # Defer to AUTH_PASSWORD_VALIDATORS rather than a local length floor, so the
        # configured policy (length, common passwords, similarity to the username)
        # is what actually applies.
        try:
            validate_password(new, user=request.user)
        except DjangoValidationError as exc:
            return Response({"detail": " ".join(exc.messages)},
                            status=http_status.HTTP_400_BAD_REQUEST)
        request.user.set_password(new)
        request.user.save()
        Token.objects.filter(user=request.user).delete()
        token = Token.objects.create(user=request.user)
        log_action(request, "Change Password", "Auth")
        return Response({"detail": "Password changed.", "token": token.key})


# ---------- Org structure masters ----------

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
        profile = get_profile(request)
        if profile is not None and profile.has_own_records_scope():
            # The directory is a cross-User listing, which Employee scope excludes
            # entirely — not merely filtered down to themselves (decision C6).
            return Response({"detail": "You do not have permission to browse the user directory."},
                            status=http_status.HTTP_403_FORBIDDEN)
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
