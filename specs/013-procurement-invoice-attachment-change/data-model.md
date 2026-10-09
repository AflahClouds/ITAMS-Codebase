# Data Model: Procurement Purchase Invoice Attachment

**Date**: 2026-09-22  
**Feature**: [spec.md](spec.md)

## Existing Entity: Procurement

Procurement remains the completed-purchase aggregate root.

Relevant existing relationships:

- `Procurement 1 — 1..* Asset` through `Asset.procurement`
- `Procurement 1 — 0..* ProcurementInvoiceVersion`
- Zero versions means the purchase invoice has not been supplied.
- When versions exist, exactly one is current.

No existing Procurement requires a backfill.

## New Entity: ProcurementInvoiceVersion

| Field | Meaning | Rules |
| --- | --- | --- |
| `id` | Stable version identity | Generated identifier |
| `procurement` | Owning completed purchase | Required; cascade with Procurement under existing archival policy |
| `file` | Stored invoice content | Required; private storage outside public `MEDIA_ROOT`, with a server-controlled Procurement/version path and no public base URL |
| `file_name` | Original user-facing filename | Required after safe basename normalization; never used as an authorization decision |
| `version` | Monotonic order within Procurement | Positive integer; unique with Procurement |
| `is_current` | Current document marker | At most one true row per Procurement |
| `uploaded_by` | Accountable uploader | Nullable only if the User is later removed; set on upload |
| `uploaded_at` | Upload event time | Set on creation and immutable |

### Constraints

1. Unique `(procurement, version)`.
2. Conditional unique `procurement` where `is_current = true`.
3. `version >= 1`.
4. The file extension is in the existing document allowlist.
5. Uploaded size is at most 25 MB.
6. File names are reduced to a safe basename for display/storage; storage paths
   are server-controlled and must not allow path traversal.
7. Invoice storage is not mounted under the public media route; content is read
   only through an authorized application action.

## Derived Relationship: Asset Invoice Mapping

The mapping is not a table.

```text
Asset.procurement
        |
        v
Procurement.current_invoice_version
```

- A linked Asset exposes the current invoice identity and its protected
  Asset-context download route.
- A newly attached Asset gains exposure immediately because its Procurement
  relation changes.
- A detached Asset loses current exposure immediately.
- Historical ProcurementInvoiceVersion and ProcurementAssetLink rows remain.
- No AssetDocument row or copied file is created.

## State Transitions

```text
No invoice --initial upload--> Version 1 current
Version N current --replacement--> Version N retained + Version N+1 current
No invoice --edit without file--> No invoice
Version N current --edit without file--> Version N current
```

There is no remove-without-replacement transition in this feature.

## Transaction Boundaries

### Create with invoice

One database transaction covers:

1. Validate Procurement, Assets, arrivals, and invoice.
2. Create Procurement.
3. Link Assets and record required arrival/link evidence.
4. Create invoice version 1 as current.
5. Create the required AuditLog entry.

Any failure rolls back all database changes. If storage wrote a file before the
failure, the operation removes that new storage object.

### Add or replace during edit

One database transaction covers:

1. Lock the Procurement and current invoice row.
2. Validate Procurement edits, link changes, and optional invoice.
3. Persist Procurement and link/history changes.
4. If a file is supplied, demote the old current row and create the next current
   version.
5. Create the required AuditLog entry.

After commit only, a replacement (not an initial upload) triggers the existing
IT-Manager-equivalent Notification selection.

## Read Model

Procurement responses expose optional `current_invoice` metadata:

- `id`
- `file_name`
- `version`
- `uploaded_by_details`
- `uploaded_at`
- protected Procurement-context `download_url`

Asset responses expose optional `procurement_invoice` metadata with the same
identity/version fields and an Asset-context `download_url`. Neither response
contains the media storage URL.
