# Research: Procurement Purchase Invoice Attachment

**Date**: 2026-09-22  
**Feature**: [spec.md](spec.md)

## Decision 1: Store invoice versions under Procurement

**Decision**: Add a Procurement-owned invoice-version entity. Keep all versions
and mark exactly one current when any version exists.

**Rationale**: The invoice describes the purchase shared by all linked Assets.
Procurement ownership directly satisfies single storage and replacement history,
while a partial uniqueness constraint can protect the current-version invariant.

**Alternatives considered**:

- Copy one `AssetDocument` per Asset: rejected because file storage, version
  state, audit behavior, and cleanup would diverge with Asset count.
- Put one FileField directly on Procurement: rejected because it cannot retain
  version metadata and history without a second mechanism.

## Decision 2: Derive Asset mapping from the current Procurement link

**Decision**: Do not persist a separate mapping table. An Asset exposes the
current invoice of `asset.procurement`; attaching or detaching an Asset changes
the derived exposure automatically.

**Rationale**: The existing Asset-to-Procurement foreign key is already the
authoritative current association. A second mapping can become stale and would
need synchronization on every link mutation.

**Alternatives considered**:

- Many-to-many mapping rows: rejected as duplicated relationship state.
- Per-Asset document rows pointing to one file: rejected because the rows still
  duplicate version/current metadata and complicate deletion semantics.

## Decision 3: Extend Procurement writes with optional multipart input

**Decision**: Accept an optional `invoice_file` in Procurement create, update,
and partial-update requests using multipart form data. File omission means no
document change. Normalize repeated/JSON-encoded complex fields before existing
serializer validation.

**Rationale**: A single business request permits atomic create-with-invoice and
keeps the UI as one workflow. Existing JSON clients continue to work because the
file is optional and existing parsers remain supported.

**Alternatives considered**:

- Upload through a second request after create: rejected because create could
  succeed while the requested invoice fails, contradicting AS-003.
- Base64 inside JSON: rejected because it increases payload size and bypasses
  normal uploaded-file handling.

## Decision 4: Protect file reads with record-scoped actions

**Decision**: Store Procurement invoices under a private filesystem root that
has no public base URL. Return invoice metadata and authorized download routes,
not a storage URL. Provide Procurement and Asset `invoice` actions that resolve
the parent through each viewset's authorized queryset and stream the current
file.

**Rationale**: Procurement has no Employee surface, while an Employee may view
an Asset they hold. Two contextual routes preserve those existing visibility
rules and prevent a public media URL from becoming an authorization bypass.

**Alternatives considered**:

- Store under or expose `MEDIA_URL`: rejected because the current development
  media route is unauthenticated and the constitution requires backend
  enforcement even when a storage path is guessed.
- One Procurement-only route: rejected because it would deny the required
  Asset-context access for readers whose scope permits the Asset but not the
  standalone Procurement surface.

## Decision 5: Enforce current-version integrity in storage and operation

**Decision**: Use unique constraints on `(procurement, version)` and one
conditional current row per Procurement. Lock the Procurement/current row,
calculate the next version, demote the old current row, and create the new row
in one database transaction.

**Rationale**: Application checks alone are insufficient under concurrent
replacement. Database constraints protect the invariant even if two requests
race.

**Alternatives considered**:

- Calculate `MAX(version) + 1` without a lock: rejected because concurrent
  uploads can choose the same number.
- Overwrite the current file: rejected because replacement history is required.

## Decision 6: Align file, audit, and Notification failure boundaries

**Decision**: Validate the extension, safe storage name, and 25 MB size before
mutation. Wrap Procurement/document/current-version/AuditLog database changes in
one transaction, delete a newly written file when the transaction fails, and
dispatch replacement Notification through `transaction.on_commit`.

**Rationale**: Database rollback does not automatically remove a storage object.
Explicit cleanup avoids orphans. Audit is required to be atomic with the
successful mutation, while the existing B8 policy keeps Notification delivery
outside the business transaction.

**Alternatives considered**:

- Notify inside the transaction: rejected because a delivery failure must not
  undo completed business work.
- Rely on transaction rollback for the uploaded file: rejected because Django
  storage writes are not transactional with the database.

## Decision 7: Reuse the existing application stack

**Decision**: Use the pinned Django 6.0.5 / DRF 3.17.1 backend, React 19.2.6 /
Vite 8.0.12 / Material UI frontend, Django test runner, and Vitest/Testing
Library. Add no dependency.

**Rationale**: The existing stack already supports multipart uploads, file
streaming, database constraints, transactions, form controls, and the required
test seams.

**Alternatives considered**: A separate document service or client-side upload
provider was rejected as unnecessary scope and operational complexity.
