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


def can_read_audit(request):
    """True for a reader B8 ALR-003 grants global AuditLog access.

    The policy names Admin **and IT Manager**. It is expressed as the `audit_access`
    permission code rather than a Role-name test, so a renamed Role does not silently
    lose access and a custom Role can be granted it deliberately — the same reason
    every other recipient and access rule in this system is permission-based.
    """
    if is_admin(request):
        return True
    profile = getattr(getattr(request, "user", None), "profile", None)
    if profile is None or profile.status != "Active":
        return False
    return profile.can("audit_access")


class NotOwnRecordsScope(BasePermission):
    """Denies a reader whose visibility is bounded to its own records.

    Some data has no own-records subset to fall back on: B6 Procurement is purchase
    administration, and decision C9 puts no Procurement surface in front of the
    Employee Role at all. Filtering it to nothing would answer 200 with an empty
    list and imply the data merely does not exist.
    """

    message = "You do not have permission to view this data."

    def has_permission(self, request, view):
        profile = getattr(getattr(request, "user", None), "profile", None)
        return not (profile is not None and profile.has_own_records_scope())


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
        if isinstance(code, (tuple, list)):
            # Several codes reach the same data by different routes — master data is
            # readable both by the roles that consume it (`asset_view`) and by the role
            # that maintains it (`settings_access`). Holding any one of them is enough.
            return any(profile.can(c) for c in code)
        return profile.can(code)
