# Implementation Plan: Procurement Purchase Invoice Attachment

**Feature Directory**: `specs/013-procurement-invoice-attachment-change/`  
**Date**: 2026-09-22  
**Spec**: [spec.md](spec.md)

**Input**: Feature specification from
`specs/013-procurement-invoice-attachment-change/spec.md`

**Workflow**: Generated and completed through `$speckit-plan`.

## Summary

Add an optional Procurement-owned purchase invoice to Procurement create and
edit. Retain every upload as a version, enforce at most one current version,
and derive each Asset's invoice exposure from its current Procurement link so
one uploaded file serves all linked Assets without duplication. Extend the
existing Procurement multipart contract and add authorization-checked download
actions for Procurement and Asset contexts. Implement the workflow test-first
across the Django REST boundary and the React forms.

## Technical Context

**Backend**: Python with Django 6.0.5 and Django REST Framework 3.17.1, as pinned
in `backend/requirements.txt`

**Frontend**: React 19.2.6, Vite 8.0.12, Material UI 9.1.1, Axios 1.16.1,
Formik 2.4.9, and existing dependencies pinned in `frontend/package.json`

**Storage**: Existing Django database plus a private filesystem storage root
outside the public `MEDIA_ROOT` route; add one Procurement-invoice version model
and one migration, without copying files into AssetDocument

**Testing**: Django test runner with DRF APIClient integration tests; Vitest
3.2.7 and Testing Library for React form and Asset-detail behavior

**Target Platform**: Browser client and Django web service

**Performance Goals**: One upload and one retained version row per invoice
submission regardless of linked-Asset count; a five-Asset Procurement exposes
the current invoice without five file writes

**Constraints**: 25 MB maximum; existing document extension allowlist; safe
server-controlled storage path; `asset_create` for create-with-file,
`asset_edit` for later add/replace, existing record visibility for download;
atomic Procurement/document/current-version/mapping effects; audit in the
business transaction and replacement Notification only after commit; no Asset
lifecycle transition

**Scale/Scope**: One new version table and migration; two existing Procurement
forms, Asset detail, Procurement and Asset serializers/viewsets, and focused
backend/frontend integration tests. Existing Procurements need no backfill
because zero invoice versions is valid.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Domain and decisions — PASS**: Uses the canonical Procurement and Asset
  meanings from `CONTEXT.md`. ADR-0001 is relevant only to the existing managed
  Vendor and is not changed. No new lasting architecture decision requires an
  ADR.
- **Lifecycle and authorization — PASS**: No Asset transition occurs.
  Create-with-file requires `asset_create`; later add/replace requires
  `asset_edit`; the two download actions resolve through the existing
  Procurement or Asset scoped queryset. The save, invoice version switch, and
  AuditLog write share one transaction; replacement Notification dispatch is
  registered after commit.
- **Traceability — PASS**: US1/AS-001–AS-003 cover optional create; US2/AS-004–
  AS-006 cover later add/replace/no-change; US3/AS-007–AS-010 cover derived Asset
  exposure, link changes, and authorization. Tests carry `Covers: CHG-B6-01
  FR-xxx` tags.
- **Persistence and lineage — PASS**: This is a Draft Change specification and
  may be planned. It extends Draft B6 and explicitly supersedes only B6's prior
  invoice-file requiredness; Draft B6 contains the reciprocal link. No accepted
  baseline content is rewritten.
- **Test-first delivery — PASS**: Backend API/integration tests fail first for
  model invariants, create/edit atomicity, mapping, download authorization,
  audit, and Notification behavior. Frontend component tests fail first for the
  optional file control, multipart payload, retained current invoice, and Asset
  download surface.
- **Local execution — PASS**: `tasks.md` remains planning input. After review,
  publish tracer-bullet files under this feature's `issues/` directory with the
  repository's `to-tickets` workflow.

**Post-design re-check**: PASS. The data model, contracts, and validation guide
below preserve every gate. No exception or unjustified complexity is present.

## Project Structure

### Documentation (this feature)

```text
specs/013-procurement-invoice-attachment-change/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|-- checklists/
|-- tasks.md
`-- issues/
```

### Source Code (repository root)

```text
backend/
|-- accounts/
|-- assets/
|-- catalog/
|-- core/
|-- reporting/
|-- itams/
`-- manage.py

frontend/
|-- src/
|   |-- api/
|   |-- components/
|   `-- pages/
|-- package.json
`-- vite.config.js
```

**Structure Decision**: Keep the feature inside the existing `assets` Django
app because Procurement, Asset links, permissions, and file behavior already
live there. Add `backend/assets/procurement_invoices.py` as the authoritative
document operation so serializers and view actions do not duplicate versioning,
file cleanup, audit, or Notification rules. Reuse the existing Procurement
create/edit pages and Asset detail page; add no top-level module or dependency.

## Phase 0: Research

Research is complete in [research.md](research.md). There are no unresolved
technical clarifications. The selected design uses a Procurement invoice-version
entity, a derived Asset mapping, multipart Procurement writes, protected stream
actions, database constraints plus row locking for current-version integrity,
and post-commit replacement Notification delivery.

## Phase 1: Design and Contracts

The complete entity and invariant design is in [data-model.md](data-model.md).
The request/response and protected-download contract is in
[contracts/procurement-invoice.openapi.yaml](contracts/procurement-invoice.openapi.yaml).
End-to-end validation is in [quickstart.md](quickstart.md).

Implementation will:

1. Add `ProcurementInvoiceVersion` with Procurement ownership, version order,
   current marker, original filename, uploader, and upload time.
2. Add a partial unique database constraint for one current version per
   Procurement and a unique `(procurement, version)` constraint.
3. Store invoice content through a private storage backend with no public base
   URL, then centralize add/replace in `procurement_invoices.py`, lock the Procurement and
   current version during replacement, validate extension/size/name, preserve
   old versions, clean up failed file writes, and return current metadata.
4. Accept optional `invoice_file` on Procurement create/update multipart
   requests. Omission means no invoice change. Keep nested `asset_ids` and
   `arrivals` compatible by normalizing their multipart representation before
   serializer validation.
5. Expose current invoice metadata from Procurement and Asset serializers
   without exposing a public media URL. Stream content only through protected
   `invoice` actions on the Procurement and Asset viewsets.
6. Add file controls and current-file feedback to Procurement Create/Edit, and
   show a download action on Asset Detail when a mapped invoice exists.
7. Record create/add/replace AuditLog entries in the same database transaction.
   Queue the existing IT-Manager-equivalent replacement Notification after
   commit; an initial upload does not notify.

## Test Strategy

- **US1**: First add API tests in
  `backend/assets/tests_procurement_invoice.py` for create with one invoice and
  multiple Assets, create without a file, invalid extension/oversize rejection,
  unauthorized create, and rollback on document persistence failure. Add
  `frontend/src/pages/procurement/Create.test.jsx` for optional input and
  multipart submission. These tests must fail before the model/contract/UI work.
- **US2**: Add backend tests for later add, replacement/version retention,
  omitted-file no-op, concurrent current-version integrity, atomic audit, and
  post-commit replacement Notification. Add
  `frontend/src/pages/procurement/Edit.test.jsx` for current metadata,
  add/replace, omission, and error display before changing the form.
- **US3**: Add backend tests for shared identity across at least five Assets,
  automatic exposure after attach, removal after detach, scoped Asset access,
  denied Procurement/direct download, and no AssetDocument copies. Add
  `frontend/src/pages/asset/Detail.test.jsx` and extend
  `frontend/src/pages/procurement/Procurement.test.jsx` for the mapped Asset and
  Procurement download surfaces before changing either page.
- **Commands**: From `backend/`, run
  `python manage.py test assets.tests_procurement_invoice`, then the complete
  `python manage.py test`. From `frontend/`, run the focused Vitest files,
  followed by `npm test`, `npm run lint`, and `npm run build`.

## Complexity Tracking

> Fill only when a Constitution Check violation requires explicit justification.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --- | --- | --- |
| None | N/A | N/A |
