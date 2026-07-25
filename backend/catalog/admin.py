from django.contrib import admin

from .models import Brand, Category, Model, PurchaseMode

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Model)
admin.site.register(PurchaseMode)
