from django.contrib import admin

from .models import (Asset, AssetCheckout, AssetConditionLog, AssetTransfer,
                     Procurement)

admin.site.register(Asset)
admin.site.register(Procurement)
admin.site.register(AssetCheckout)
admin.site.register(AssetTransfer)
admin.site.register(AssetConditionLog)
