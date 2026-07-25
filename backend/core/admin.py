from django.contrib import admin

from .models import AuditLog, Notification, Setting

admin.site.register(Notification)
admin.site.register(AuditLog)
admin.site.register(Setting)
