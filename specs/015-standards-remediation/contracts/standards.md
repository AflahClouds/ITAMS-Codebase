# Standards Remediation Contracts

## Catalog maintenance

Existing /category/, /brand/, /model/, /purchase_mode/, /vendor/ routes and permissions remain. /model/ responses expose Brand identity; create requires a valid Brand and the master form sends/displays it. Invalid/blank/duplicate normalized names return a useful field-level 400 response, including save-time duplicate races. Self-update is allowed; Model names may repeat under different Brands. Existing IDs and references survive rename/correction. Each rejected identity conflict has one durable audit outcome. Unrelated storage errors are not disguised as validation failures.

## Audit Trail

Existing /audit/ list envelope, module/username filters, 1,000-row omission disclosure, source-IP minimization and audit_access gate remain. Successful list/filter/empty-list and /audit/{id}/ reads add one access AuditLog record. Required audit failure returns no protected event payload. Logging does not recursively log its own write; denied reads keep existing denial handling.

## Settings

Existing Admin-only /setting/ POST/upsert and /setting/{id}/ PUT/PATCH/DELETE remain. Every successful mutation yields one minimized audit entry identifying the key/action/actor without the Setting value. Required audit failure leaves the pre-request Setting state intact. Unauthorized calls stay denied.

## Exports

Existing report PDF/Excel and Transfer-document PDF routes retain permissions and scope. PDF company text, headings, cells and details render user strings literally: '<b>broken', 'A & B', and image-like text cause neither markup execution nor resource loads. XLSX string cells preserve '=1+1', '+x', '-x', '@x' literally and are never formulas; numbers 0 and -1, booleans, dates and nulls remain non-text typed values. Generated files are verified through the public delivery boundary and existing libraries. CSV and the separate Spec findings are excluded.
