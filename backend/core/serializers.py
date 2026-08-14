from rest_framework import serializers

from .models import AuditLog, Notification, Setting


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'message', 'link', 'status', 'created')


class AuditLogSerializer(serializers.ModelSerializer):
    ip_address = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = "__all__"

    def get_ip_address(self, obj):
        """Withhold a source address past its six-month window (B8 FR-017).

        The scheduled purge clears these, but presentation must not depend on the job
        having run — a restarted process must never serve a value whose retention
        period has already expired.
        """
        from .retention import ip_is_expired
        return "" if ip_is_expired(obj.date) else obj.ip_address


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = ('id', 'key', 'value')
