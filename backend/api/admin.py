from django.contrib import admin

from .models import (Asset, AssetCheckout, AssetConditionLog, AssetTransfer,
                     AuditLog, Brand, Category, Department, Location, Model,
                     Notification, Permission, Procurement, PurchaseMode,
                     Role, Setting, User)

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Model)
admin.site.register(PurchaseMode)
admin.site.register(Department)
admin.site.register(Location)
admin.site.register(Permission)
admin.site.register(Role)
admin.site.register(User)
admin.site.register(Asset)
admin.site.register(Procurement)
admin.site.register(AssetCheckout)
admin.site.register(AssetTransfer)
admin.site.register(AssetConditionLog)
admin.site.register(Notification)
admin.site.register(AuditLog)
admin.site.register(Setting)
