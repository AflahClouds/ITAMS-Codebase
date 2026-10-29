# Tasks: Asset Procurement Lifecycle

**Input**: Design documents in specs/016-asset-procurement-lifecycle/.
**Prerequisites**: spec.md, plan.md, research.md, data-model.md, contracts/lifecycle.md.
**Tests**: Mandatory fail-before/permanent regressions under constitution IV.
**Organization**: Complete vertical user-story slices; one sole native builder.
**Publication boundary**: Planning input only. Execute published issues/01–04.
**Persistence gate**: Accepted Change; all three stage/sprint approvals verified.

## Format: [ID] [P?] [Story] Description

No [P] writer tasks: shared domain/serializer/form files require sequential work.

## Path Conventions

Backend under backend/assets; frontend under frontend/src/pages. Evidence under
this feature's issues. No deployment or user-database mutation.

## Phase 1: Feature Setup

- [X] T001 Verify accepted authority/branch/baseline and preserve unrelated state; record starting evidence in specs/016-asset-procurement-lifecycle/issues/01-stage-and-link.md.

## Phase 2: Foundational

- [X] T002 Add focused API fixture helpers with explicit status/procurement and private temporary storage in backend/assets/tests_procurement_lifecycle.py; reuse existing harnesses, no production changes.

## Phase 3: User Story 1 - Stage Until Procurement (P1)

Goal: New registration Storage, valid new association Available.
Independent test: AS-001–005 through API and actual create/purchase forms.

- [X] T003 [US1] Add/execute failing API regressions for default/explicit create, singleton/batch/existing purchase attach, optional invoice, failed rollback, direct procurement/status bypass and metadata preservation in backend/assets/tests_procurement_lifecycle.py (FR-001/002, ALR-001–005).
- [X] T004 [US1] Add/execute failing creation/association form regressions in frontend/src/pages/asset/ and frontend/src/pages/procurement/Procurement.test.jsx (FR-008).
- [X] T005 [US1] Implement authoritative association/status seam in backend/assets/procurement_lifecycle.py, route serializers through it, change model default with default-only migration under backend/assets/migrations/, and block direct bypass in backend/assets/serializers.py (FR-001/002, ALR-002/003).
- [X] T006 [US1] Update frontend/src/pages/asset/Create.jsx and relevant Edit.jsx state controls plus Procurement create/edit flow to reflect staging/association contract; keep historical rows unchanged (FR-008).
- [X] T007 [US1] Prove focused green tests, update superseded default assumptions only in relevant backend/assets/tests*.py and UI fixtures, record red/green and checkpoint in specs/016-asset-procurement-lifecycle/issues/01-stage-and-link.md.

## Phase 4: User Story 2 - Detach Before Asset Deletion (P1)

Goal: Linked Asset protected; reasoned multi-Asset removal returns Storage.
Independent test: AS-006–009, including archived links/custody-history protections.

- [X] T008 [US2] Add/execute failing linked/archived Asset deletion, reasoned detachment, separate eligible deletion, protected state and permission API/UI regressions in backend/assets/tests_procurement_lifecycle.py and frontend/src/pages/asset/ deletion tests (FR-003/004/008).
- [X] T009 [US2] Implement locked/revalidated detach and linked-delete guard in backend/assets/procurement_lifecycle.py and backend/assets/views.py, preserving custody history and durable audit/notification obligations (ALR-001–005).
- [X] T010 [US2] Update frontend/src/pages/asset/Delete.jsx and procurement/Edit.jsx to show server rejection, Procurement navigation and reasoned detachment/status refresh (FR-008).
- [X] T011 [US2] Run focused regressions, prove surviving purchase/Assets unchanged, and record red/green/checkpoint in specs/016-asset-procurement-lifecycle/issues/02-detach-before-delete.md.

## Phase 5: User Story 3 - Release Last Asset (P1)

Goal: Explicit permanent singleton purchase deletion retains Asset Storage.
Independent test: AS-010–013 and owned files/history plus rollback.

- [X] T012 [US3] Add/execute failing singleton-only permanent deletion, owned history/invoice rows and physical file cleanup, empty-edit guidance, protected/stale/cardinality/permission/audit rollback and ordinary archive API/UI regressions in backend/assets/tests_procurement_lifecycle.py and frontend/src/pages/procurement/ tests.
- [X] T013 [US3] Implement explicit asset_delete-mapped singleton action in backend/assets/views.py and authoritative permanent release in backend/assets/procurement_lifecycle.py, including commit-safe exact private-file cleanup and retained audit (FR-005–007, ALR-001–005).
- [X] T014 [US3] Implement explicit confirmed permanent-delete UI/navigation/error handling in frontend/src/pages/procurement/{Procurement,Edit,Delete}.jsx while retaining ordinary archive behavior (FR-008).
- [X] T015 [US3] Run focused green regressions, retain permanent failure protection, and record red/green/checkpoint in specs/016-asset-procurement-lifecycle/issues/03-release-last-asset.md.

## Phase 6: Polish and Cross-Cutting Concerns

- [X] T016 Remove proven superseded status/link/delete duplicate paths and stale current comments in backend/assets/ and frontend/src/pages/, add predecessor lineage metadata in specs/001-asset-register-lifecycle-baseline/spec.md, specs/002-procurement-vendor-catalog-baseline/spec.md, specs/013-procurement-invoice-attachment-change/spec.md and specs/014-asset-assignments/spec.md; retain historical requirements and ordinary archive/custody tests.
- [X] T017 Run full Django suite, serial frontend suite, lint, build and migration drift check per specs/016-asset-procurement-lifecycle/quickstart.md; retain each process handle to terminal exit and record commands/counts in issues/04-verification.md (SC-001–004).
- [X] T018 Complete one combined repository-wide stale-material/reference and self-description/resume review of current tree, update necessary current docs/context and verified evidence, verify unrelated state preserved, create/push final ordinary checkpoint, and freeze candidate in specs/016-asset-procurement-lifecycle/issues/04-verification.md.

## Dependencies and Execution Order

T001 → T002 → US1 (T003–007) → US2 (T008–011) → US3 (T012–015)
→ polish/verification (T016–018). US2's detach uses US1's shared seam; US3 uses
the same eligibility and guard. Tickets are 01 → 02 → 03 → 04.

Within each slice write/observe intended red tests first; implement; focused green;
checkpoint. New uncovered defects get permanent regressions before repair.
Independent research was read-only and completed before writer dispatch.

## Parallel Opportunities and Examples

US1 backend/UI failure cases could be inspected independently; US2 error-copy
and custody assertions could be reviewed separately; US3 file/audit rollback
oracles could be inspected separately. No parallel writers are authorized.
During delivery builder and reviewer are strictly sequential on a frozen candidate.

## Implementation Strategy

US1 is the independently demoable MVP, followed by complete US2 then US3.
Current full-sprint authority covers all stories and final checks; do not stop
after MVP or request routine ticket approval. Execute local issues, record evidence,
and finish every task before independent review. Reviewer is read-only; findings
return to same builder, followed by same reviewer re-review. Guide-owned canonical
consolidation/review and post-closeout checks stay outside this ledger.
