from django.conf import settings as django_settings
from django.db import models


class Department(models.Model):
    name = models.CharField(unique=True, max_length=128)
    description = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(unique=True, max_length=128)
    address = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.name


class Permission(models.Model):
    code = models.CharField(unique=True, max_length=64)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.code


class Role(models.Model):
    name = models.CharField(unique=True, max_length=64)
    description = models.CharField(max_length=255, blank=True, default="")
    permissions = models.ManyToManyField(Permission, blank=True, related_name="roles")

    def has_permission(self, code):
        if self.name == "Admin":
            return True
        return self.permissions.filter(code=code).exists()

    def __str__(self):
        return self.name


class User(models.Model):
    """Employee profile. Login credentials live on the linked auth account."""
    account = models.OneToOneField(
        django_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="profile")
    user_name = models.CharField(max_length=100)
    emp_id = models.CharField(unique=True, max_length=100)
    email_id = models.EmailField(unique=True, max_length=100)
    mob_no = models.CharField(max_length=20, blank=True, default="")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.CharField(max_length=128, blank=True, default="")
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=16, default="Active")  # Active / Disabled

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def can(self, permission_code):
        if self.role and self.role.name == "Admin":
            return True
        return self.role.has_permission(permission_code) if self.role else False

    def __str__(self):
        return self.user_name


def users_with_permission(code):
    """Active employee profiles whose role grants the permission (Admins included)."""
    return [u for u in User.objects.filter(status="Active").select_related("role") if u.can(code)]
