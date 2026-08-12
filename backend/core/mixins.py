"""Shared ViewSet mixins/constants used by master-data viewsets across apps."""
from django.db.models.deletion import ProtectedError
from rest_framework import status as http_status
from rest_framework.response import Response

# Reads are listed explicitly: with no "list"/"retrieve" key and no "*" fallback,
# HasRolePermission finds no required code and admits any authenticated user. They
# accept either code, because a Role that maintains master data does not necessarily
# also hold `asset_view`.
MASTER_READ_CODES = ("asset_view", "settings_access")

MASTER_WRITE = {"list": MASTER_READ_CODES, "retrieve": MASTER_READ_CODES,
                "create": "settings_access", "update": "settings_access",
                "partial_update": "settings_access", "destroy": "settings_access"}


class ProtectedMasterDeleteMixin:
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return Response(
                {"detail": "Cannot delete this master record because it is in use."},
                status=http_status.HTTP_409_CONFLICT,
            )
        return Response(status=http_status.HTTP_204_NO_CONTENT)
