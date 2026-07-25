from django.db import models


class Notification(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=500)
    link = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=16, default="Unread")  # Unread / Read
    created = models.DateTimeField(auto_now_add=True)


class AuditLog(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    username = models.CharField(max_length=64, blank=True, default="")
    action = models.CharField(max_length=64)
    module = models.CharField(max_length=64)
    old_value = models.TextField(blank=True, default="")
    new_value = models.TextField(blank=True, default="")
    date = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=64, blank=True, default="")


class Setting(models.Model):
    key = models.CharField(unique=True, max_length=64)
    value = models.TextField(blank=True, default="")

    @staticmethod
    def get(key, default=None):
        row = Setting.objects.filter(key=key).first()
        return row.value if row and row.value is not None else default

    @staticmethod
    def set(key, value):
        Setting.objects.update_or_create(key=key, defaults={"value": value})
