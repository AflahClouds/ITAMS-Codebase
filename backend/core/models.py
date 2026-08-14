from django.db import models
from django.utils import timezone


class Notification(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=500)
    link = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=16, default="Unread")  # Unread / Read
    created = models.DateTimeField(auto_now_add=True)
    # B8 FR-017 removes a Read Notification 90 days after it became Read, which is not
    # computable from the creation time. B8 FR-019 therefore requires the transition
    # time to be retained; it is set once and never cleared, because the transition is
    # one-way.
    read_at = models.DateTimeField(null=True, blank=True)

    def mark_read(self):
        """Idempotent Unread -> Read. Re-marking does not restart the retention clock."""
        if self.status == "Read":
            return False
        self.status = "Read"
        self.read_at = timezone.now()
        self.save(update_fields=['status', 'read_at'])
        return True


class NotificationFailure(models.Model):
    """An in-app delivery that could not be retained, kept for an operator to see.

    B8 FR-012 puts Notification delivery outside the atomic boundary of the business
    action: a failure must not roll the business work back, must retry without creating
    duplicates, and must stay visible until delivered or explicitly resolved. A row here
    is that visibility — without it a failed delivery is silent.
    """
    recipient = models.ForeignKey('accounts.User', on_delete=models.CASCADE,
                                  null=True, blank=True,
                                  related_name="failed_notifications")
    message = models.CharField(max_length=500)
    link = models.CharField(max_length=255, blank=True, default="")
    error = models.TextField(blank=True, default="")
    attempts = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)


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
