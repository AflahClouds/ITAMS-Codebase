"""Role-based permission checks for the API.

Each view/viewset declares a ``permission_map`` of DRF action name -> required
permission code. Special values:
  - None        : any authenticated active user
  - "__admin__" : only the Admin role (or a Django superuser)
A "*" key acts as the fallback for actions not listed explicitly.
"""
from rest_framework.permissions import BasePermission


class HasRolePermission(BasePermission):
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        profile = getattr(user, "profile", None)
        if profile is None or profile.status != "Active":
            return False

        is_admin = profile.role is not None and profile.role.name == "Admin"
        if is_admin:
            return True

        perm_map = getattr(view, "permission_map", {})
        action = getattr(view, "action", None)
        if action is not None and action in perm_map:
            code = perm_map[action]
        elif "*" in perm_map:
            code = perm_map["*"]
        else:
            code = getattr(view, "required_permission", None)

        if code is None:
            return True
        if code == "__admin__":
            return False
        return profile.can(code)
