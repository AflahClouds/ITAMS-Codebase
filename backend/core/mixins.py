"""Shared ViewSet mixins/constants used by master-data viewsets across apps."""
from django.db.models.deletion import ProtectedError
from rest_framework import status as http_status
from rest_framework.response import Response

MASTER_WRITE = {"create": "settings_access", "update": "settings_access",
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
