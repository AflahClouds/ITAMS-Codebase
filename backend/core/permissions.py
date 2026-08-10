"""Role-based permission checks for the API.

Each view/viewset declares a ``permission_map`` of DRF action name -> required
permission code. Special values:
  - None        : any authenticated active user
  - "__admin__" : only the Admin role (or a Django superuser)
A "*" key acts as the fallback for actions not listed explicitly.
"""
from rest_framework.permissions import BasePermission


def is_admin(request):
    """True for a Django superuser or an Active profile holding the Admin role.

    Exposed so a view can gate one action on administrative authority without
    re-deriving the test — the ``"__admin__"`` permission_map value covers whole
    viewsets, but a single entry inside a view (an Admin-only report among
    ordinary ones) needs the same check inline.
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profile = getattr(user, "profile", None)
    if profile is None or profile.status != "Active":
        return False
    return profile.role is not None and profile.role.name == "Admin"


class HasRolePermission(BasePermission):
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if is_admin(request):
            return True

        profile = getattr(user, "profile", None)
        if profile is None or profile.status != "Active":
            return False

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
