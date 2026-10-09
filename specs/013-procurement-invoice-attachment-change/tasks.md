# Tasks: Procurement Purchase Invoice Attachment

**Input**: Design documents from
`specs/013-procurement-invoice-attachment-change/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/procurement-invoice.openapi.yaml`, `quickstart.md`

**Tests**: Tests are required before implementation for every behavior change,
in accordance with the ITAMS constitution.

**Organization**: Tasks are grouped into independently verifiable tracer-bullet
user-story slices.

**Publication boundary**: This file is planning and consistency-analysis input.
After review, publish implementation work with `to-tickets` as separate files
under this feature's `issues/` directory. Do not use `speckit-taskstoissues`.

**Persistence gate**: This is an active Draft Change specification. It does not
rewrite an accepted baseline and is eligible for delivery planning.

## Phase 1: Feature Setup

**Purpose**: Establish isolated test support for transactional file behavior in
the existing application.

- [X] T001 Add reusable Procurement, multi-Asset, uploaded-file, and temporary-media fixtures for this feature in `backend/assets/tests_procurement_invoice.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the versioned Procurement-owned document seam shared by all
three user stories.

**⚠️ CRITICAL**: Complete this phase before any user-story work.

- [X] T002 Add failing domain tests for per-Procurement version uniqueness, one-current-version integrity, 25 MB/extension/name validation, replacement ordering, and failed-storage cleanup in `backend/assets/tests_procurement_invoice.py`
- [X] T003 [P] Add failing reusable invoice-file-field tests for optional selection, filename display, replacement wording, allowed extensions, and 25 MB guidance in `frontend/src/components/forms/ProcurementInvoiceField.test.jsx`
- [X] T004 Add `MAX_DOCUMENT_UPLOAD_SIZE`, a non-public invoice storage root/backend, the `ProcurementInvoiceVersion` model, server-controlled upload path, constraints, and migration in `backend/itams/settings.py`, `backend/assets/storage.py`, `backend/assets/models.py`, and `backend/assets/migrations/0013_procurementinvoiceversion.py`
- [X] T005 Implement the authoritative validated initial-upload/replacement operation with Procurement row locking, current-version switching, retained history, and failed-file cleanup in `backend/assets/procurement_invoices.py`
- [X] T006 [P] Implement the reusable optional invoice selector/current-file presentation in `frontend/src/components/forms/ProcurementInvoiceField.jsx`

**Checkpoint**: The storage/versioning seam is green under its focused tests;
no API or page yet exposes it.

---

## Phase 3: User Story 1 — Optionally Attach Invoice During Creation (Priority: P1) 🎯 MVP

**Goal**: Create Procurement with or without one invoice, atomically linking all
selected Assets and exposing one Procurement-owned current version.

**Independent Test**: Submit valid multi-Asset Procurement twice—once with a
valid invoice and once without—and observe both succeeding, with exactly one
version only in the first case.

### Tests for User Story 1

- [X] T007 [P] [US1] Add failing API integration tests for multi-Asset create with one invoice, create without a file, invalid extension, oversize file, denied `asset_create`, atomic rollback, and same-transaction AuditLog in `backend/assets/tests_procurement_invoice.py`
- [X] T008 [P] [US1] Add failing page tests for the optional invoice input, multipart create payload, successful no-file submission, and actionable upload errors in `frontend/src/pages/procurement/Create.test.jsx`

### Implementation for User Story 1

- [X] T009 [US1] Add optional `invoice_file` multipart normalization, current-invoice response metadata, and atomic create-with-audit integration in `backend/assets/serializers.py` and `backend/assets/views.py`
- [X] T010 [US1] Integrate `ProcurementInvoiceField` and FormData submission without making the file required in `frontend/src/pages/procurement/Create.jsx`

**Checkpoint**: US1 passes independently and is the deployable MVP.

---

## Phase 4: User Story 2 — Add or Replace Invoice During Editing (Priority: P1)

**Goal**: Add a missing invoice or replace the current version from Procurement
edit; omission preserves current state and replacement retains history.

**Independent Test**: Start from an existing Procurement without an invoice,
add version 1, save an edit without a file, then replace with version 2 and
observe version 1 retained and version 2 current.

### Tests for User Story 2

- [X] T011 [P] [US2] Add failing API integration tests for later add, replacement, retained versions, omitted-file no-op, concurrent replacements, denied `asset_edit`, atomic AuditLog, and post-commit replacement Notification in `backend/assets/tests_procurement_invoice.py`
- [X] T012 [P] [US2] Add failing page tests for current invoice metadata, add/replace selection, omitted-file preservation, multipart update, and error display in `frontend/src/pages/procurement/Edit.test.jsx`

### Implementation for User Story 2

- [X] T013 [US2] Integrate optional add/replace into Procurement update and partial-update with atomic audit plus post-commit IT-Manager-equivalent replacement Notification in `backend/assets/serializers.py` and `backend/assets/views.py`
- [X] T014 [US2] Integrate current-invoice display and optional add/replace FormData submission in `frontend/src/pages/procurement/Edit.jsx`

**Checkpoint**: US2 passes independently against an existing Procurement and
does not require Procurement creation through US1 in its test setup.

---

## Phase 5: User Story 3 — Access the Invoice Through Linked Assets (Priority: P2)

**Goal**: Let authorized readers discover and download the same current invoice
from every currently linked Asset, with mapping following later link changes and
without raw-media exposure or AssetDocument copies.

**Independent Test**: Give one Procurement five Assets and one invoice, access
the same identity through all five, attach and detach Assets, and exercise both
allowed and denied contextual download routes.

### Tests for User Story 3

- [X] T015 [P] [US3] Add failing API tests for five-Asset shared identity, automatic exposure after attach, loss after detach, absence of AssetDocument copies, Procurement-context access, own-Asset scoped access, denied out-of-scope/direct-file reads, and streamed content in `backend/assets/tests_procurement_invoice.py`
- [X] T016 [P] [US3] Add failing UI tests for Procurement and Asset mapped-invoice metadata, protected download actions, no-invoice state, and reader visibility in `frontend/src/pages/procurement/Procurement.test.jsx` and `frontend/src/pages/asset/Detail.test.jsx`

### Implementation for User Story 3

- [X] T017 [US3] Add Procurement and Asset invoice projections plus authorization-checked streaming actions that expose no raw media URL in `backend/assets/serializers.py` and `backend/assets/views.py`
- [X] T018 [US3] Render protected current-invoice download actions on the Procurement list and Asset detail without an Asset-owned upload/delete control in `frontend/src/pages/procurement/Procurement.jsx` and `frontend/src/pages/asset/Detail.jsx`

**Checkpoint**: All user stories are independently demonstrable and the same
stored invoice is visible through each authorized context.

---

## Phase 6: Polish & Cross-Cutting Validation

**Purpose**: Confirm schema, contracts, full-suite safety, and delivery evidence.

- [X] T019 [P] Reconcile final request/response names and error cases with `specs/013-procurement-invoice-attachment-change/contracts/procurement-invoice.openapi.yaml` and `specs/013-procurement-invoice-attachment-change/data-model.md`
- [X] T020 Run migration consistency, the focused invoice suite, and the complete Django suite from `backend/manage.py`, recording any justified deviations in `specs/013-procurement-invoice-attachment-change/quickstart.md`
- [X] T021 Run focused and complete Vitest suites, ESLint, and the production build from `frontend/package.json`, recording any justified deviations in `specs/013-procurement-invoice-attachment-change/quickstart.md`
- [X] T022 Execute every end-to-end scenario and authorization/failure check in `specs/013-procurement-invoice-attachment-change/quickstart.md` and record review evidence in `specs/013-procurement-invoice-attachment-change/checklists/invoice-attachment.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1** has no dependencies.
- **Phase 2** depends on T001 and blocks every user story.
- **US1, US2, and US3** begin after Phase 2. US2 and US3 use direct database
  setup in their tests, so each remains independently verifiable even if the
  other page slice is not delivered.
- **Phase 6** depends on the desired user stories being complete.

### Task Dependencies

- T002 follows T001; T004 and T005 follow the failing T002 tests.
- T006 follows the failing T003 component tests.
- T009 follows T005 and failing T007; T010 follows T006 and failing T008.
- T013 follows T005 and failing T011; T014 follows T006 and failing T012.
- T017 follows T005 and failing T015; T018 follows failing T016.
- T019–T022 follow all selected story implementations.

### Requirement-to-Task Traceability

| Requirement group | Primary tasks |
| --- | --- |
| FR-001–FR-002, FR-006–FR-007, FR-011–FR-012, ALR-001 | T002, T004–T010 |
| FR-003–FR-005, FR-010–FR-012, ALR-002, ALR-004 | T002, T004–T006, T011–T014 |
| FR-007–FR-009, FR-013–FR-015, ALR-003 | T015–T018 |
| SC-001–SC-006 and complete regression validation | T020–T022 |

### Parallel Opportunities

- T003 can run alongside T002 because it touches only frontend component tests.
- T006 can run alongside backend T004–T005 after T003 fails as expected.
- Within each story, backend and frontend test-writing tasks marked `[P]` can
  run together.
- Once Phase 2 is green, different developers can take US1, US2, and US3, but
  backend integration tasks T009, T013, and T017 must be serialized when they
  overlap `serializers.py` or `views.py`.
- T019 can run alongside either validation command; T020 and T021 run
  sequentially because both may record deviations in `quickstart.md`.

## Parallel Examples

### Foundation

```text
Task T002: Backend domain tests in backend/assets/tests_procurement_invoice.py
Task T003: Frontend field tests in frontend/src/components/forms/ProcurementInvoiceField.test.jsx
```

### User Story 1

```text
Task T007: Backend create integration tests
Task T008: Frontend Procurement Create page tests
```

### User Story 2

```text
Task T011: Backend later-add/replacement integration tests
Task T012: Frontend Procurement Edit page tests
```

### User Story 3

```text
Task T015: Backend mapping/download authorization tests
Task T016: Frontend Asset Detail tests
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete US1 tests before US1 implementation.
3. Validate US1 independently: create with one invoice and with no invoice.
4. Stop for review or publish the US1 tracer-bullet ticket.

### Incremental Delivery

1. **Foundation**: versioned Procurement-owned document operation.
2. **US1**: optional capture during create.
3. **US2**: later add and replacement with retained versions.
4. **US3**: Asset-context discovery and protected download.
5. **Polish**: contract reconciliation and full validation.

### Local Issue Publication

After `speckit-analyze` and reviewer approval, use the repository's `to-tickets`
workflow to publish one local Markdown issue per independently verifiable slice
under `specs/013-procurement-invoice-attachment-change/issues/`. Do not implement
directly from this unreviewed task list.

## Notes

- Every behavior task places a failing test before its implementation task.
- `[P]` is used only where tasks touch different files or are read-only command
  validation with no dependency on another incomplete task.
- All implementation descriptions name exact repository paths.
