from django.contrib import admin

from .models import Department, Location, Permission, Role, User

admin.site.register(Department)
admin.site.register(Location)
admin.site.register(Permission)
admin.site.register(Role)
admin.site.register(User)
