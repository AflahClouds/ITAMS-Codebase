from rest_framework import status as http_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.utils import timezone

from .models import AuditLog, Notification, Setting
from .permissions import HasRolePermission, can_read_audit
from .retention import ip_is_expired
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
        self.get_object().mark_read()
        return Response({"detail": "ok"})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        # Only Unread rows are touched, so an already-Read record keeps its original
        # transition time and its 90-day retention clock does not restart (FR-019).
        self.get_queryset().filter(status="Unread").update(
            status="Read", read_at=timezone.now())
        return Response({"detail": "ok"})


# ---------- Audit ----------

AUDIT_VIEW_LIMIT = 1000


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """The Audit Trail, readable by the Roles B8 ALR-003 names.

    Access is `audit_access` (Admin and IT Manager), not the Admin-only test this
    endpoint used to apply — the policy always named both, and the report surface was
    made to match the endpoint rather than the policy.
    """
    permission_classes = [HasRolePermission]
    permission_map = {"*": "audit_access"}
    serializer_class = AuditLogSerializer

    def _filtered(self):
        qs = AuditLog.objects.all().order_by('-date')
        p = self.request.query_params
        if p.get('module'):
            qs = qs.filter(module=p['module'])
        if p.get('username'):
            qs = qs.filter(username__icontains=p['username'])
        return qs

    def get_queryset(self):
        return self._filtered()[:AUDIT_VIEW_LIMIT]

    def list(self, request, *args, **kwargs):
        """Disclose the limit and any omission rather than truncating silently.

        B8 FR-022: an audit surface that appears complete while omitting evidence
        misrepresents the record, so the response states the cap, the number of matching
        entries, and how many were left out.
        """
        total = self._filtered().count()
        rows = self.get_serializer(self.get_queryset(), many=True).data
        return Response({
            "limit": AUDIT_VIEW_LIMIT,
            "total": total,
            "omitted": max(0, total - AUDIT_VIEW_LIMIT),
            "results": rows,
        })


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
