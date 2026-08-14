"""Audit coverage for master-data viewsets.

B8 FR-014 requires an AuditLog entry for *every* successful business-data mutation.
Catalog masters, Departments, and Locations were writing none, though a Vendor is
business data by B6's and B7's own rules — B6 protects it from deletion while
referenced, and B7 records it on every dated AMC contract.
"""
from core.services import log_action


class AuditedMutationMixin:
    """Records create/update/delete against the viewset's `audit_module`.

    The value written is the record's own string form, which is its name for every
    master type. That is the minimum needed to explain the event and carries no data
    beyond it, as B8 FR-015 requires.
    """
    audit_module = "Masters"

    def perform_create(self, serializer):
        super().perform_create(serializer)
        log_action(self.request, "Create", self.audit_module,
                   new_value=str(serializer.instance))

    def perform_update(self, serializer):
        before = str(serializer.instance)
        super().perform_update(serializer)
        log_action(self.request, "Update", self.audit_module,
                   old_value=before, new_value=str(serializer.instance))

    def perform_destroy(self, instance):
        described = str(instance)
        super().perform_destroy(instance)
        log_action(self.request, "Delete", self.audit_module, old_value=described)
