"""Request-level concerns that cannot be handled inside a view.

`AuditDenialMiddleware` records refused attempts to reach AuditLog data.

It has to live out here rather than in the viewset. `ATOMIC_REQUESTS` wraps the view in
a transaction, and DRF's exception handler calls `set_rollback()` for every handled API
exception — so an entry written while refusing a request is created and then discarded
with the rest of the transaction. Middleware runs after the response is produced, once
that transaction has closed, which is the only place the write survives.
"""
import logging

logger = logging.getLogger(__name__)

# Surfaces that serve AuditLog content. Both are named because B8 FR-016 and B9 FR-009
# apply the same policy to the direct trail and to its report projection.
AUDIT_PATHS = ("/audit", "/reports/audit")

DENIED = (401, 403)


def _is_audit_path(path):
    return any(path == p or path.startswith(p + "/") for p in AUDIT_PATHS)


class AuditDenialMiddleware:
    """Audits a rejected AuditLog access without disclosing what was refused.

    B8 FR-014 requires security-relevant rejections to be audited and FR-016 requires it
    for every rejected AuditLog access attempt — the case that matters most, because
    otherwise probing the audit trail is the one action that leaves no trace in it. The
    entry records who was refused and which surface, and no AuditLog content.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code in DENIED and _is_audit_path(request.path):
            self._record(request, response)
        return response

    def _record(self, request, response):
        from .services import log_action
        try:
            log_action(request, "Audit Access Denied", "Audit",
                       new_value=f"{request.method} {request.path} -> {response.status_code}")
        except Exception:  # pragma: no cover - auditing must not break the response
            logger.exception("Could not record a refused AuditLog access")
