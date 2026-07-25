from rest_framework import status as http_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AuditLog, Notification, Setting
from .permissions import HasRolePermission
from .serializers import AuditLogSerializer, NotificationSerializer, SettingSerializer
from .services import get_profile, log_action


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
