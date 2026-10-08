# Tasks: Ongoing Asset Assignments and Temporary Checkout

**Input**: [spec.md](spec.md), [plan.md](plan.md), [data-model.md](data-model.md), [custody API contract](contracts/custody-api.md)

**Tests**: Required before every behavior change by constitution IV. Capture the expected red result, then the green result and relevant broader checks in the local issue.

**Organization**: One sequential writer implements independently verifiable user-story slices. This planning file is published into separate local issues before implementation. No new dependency or project initialization is required.

## Phase 1: Feature setup and shared custody boundary

**Goal**: Establish the single custody invariant and schema without changing a user workflow yet.

- [x] T001 Add failing API/domain tests for incompatible concurrent or stale custody changes, partial-write rollback, custom-role permission denial, and exact active-arrangement identity in `backend/assets/tests_custody.py` (FR-003, ALR-001–003).
- [x] T002 Add the `AssetAssignment` record and Checkout administrative-closure/classification metadata described in `data-model.md`, with an additive migration and no physical-return backfill, in `backend/assets/models.py` and `backend/assets/migrations/0013_asset_assignment.py` (FR-003, FR-010–011).
- [x] T003 Implement one transactional custody transition boundary and read-only custody-type resolver, including current-holder checks, row locking where supported, uniqueness, audit coupling and safe notification scheduling, in `backend/assets/custody.py` (FR-003, ALR-002–004).
- [x] T004 Verify red-to-green foundational tests and migration compatibility on a populated legacy Checkout fixture in `backend/assets/tests_custody.py` and `backend/assets/migrations/0013_asset_assignment.py` (FR-003, FR-011).

## Phase 2: User Story 1 — Assign an everyday Asset (P1)

**Independent test**: Authorized IT Assigns an Available Asset to an active employee; current Asset, ongoing history, audit and notification agree, without Checkout or Transfer.

- [x] T005 [US1] Add failing Assign API integration tests for AS-001–004, department-null, In Storage and terminal rejection, duplicate issue, custom-role permission and notification outcomes in `backend/assets/tests_custody.py` (FR-001–003, ALR-001–005).
- [x] T006 [US1] Implement Assign with explicit issue condition, active-user check, atomic Asset/Assignment/audit update, and `/assignment/` endpoint in `backend/assets/custody.py`, `backend/assets/serializers.py`, `backend/assets/views.py` and `backend/assets/urls.py` (FR-002–003, ALR-001–005).
- [x] T007 [US1] Add failing UI test for Assign form, eligibility, permission-gated action and ongoing label in `frontend/src/pages/transfer/Assignments.test.jsx` (FR-001–003).
- [x] T008 [US1] Add Assign action to the existing Transfer area and current-custody display in `frontend/src/pages/transfer/Transfers.jsx`, `frontend/src/pages/transfer/Create.jsx` and `frontend/src/pages/asset/Detail.jsx`; verify the UI test turns green (FR-001, FR-013).

## Phase 3: User Story 2 — Take Back a physical return (P1)

**Independent test**: IT physically receives an ongoing Asset, explicitly records its actual condition, and sees Available with no Custodian, including Damaged/Repair Required.

- [x] T009 [US2] Add failing Take Back API tests for AS-005–008/018/022, including no preselected condition, deterioration remarks with New-to-Good exception, disabled employee, Pending Transfer, stale Assignment, repeated action and audit/inspection/notification rollback in `backend/assets/tests_custody.py` (FR-004–006, ALR-001–004).
- [x] T010 [US2] Implement transactional Take Back and `/assignment/{id}/take-back/`, preserving physical inspection fields only for real receipt and returning the exact Pending Transfer error, in `backend/assets/custody.py`, `backend/assets/serializers.py`, `backend/assets/views.py` and `backend/assets/urls.py` (FR-004–006).
- [x] T011 [US2] Add failing Take Back UI test for required explicit condition, deterioration remarks, pending-request error and `Available` plus actual condition in `frontend/src/pages/transfer/Assignments.test.jsx` (FR-004–006).
- [x] T012 [US2] Add permission-gated Take Back controls, current Assignment identity, actual condition and inspection result in `frontend/src/pages/transfer/Transfers.jsx` and `frontend/src/pages/asset/Detail.jsx`; verify UI test turns green (FR-001, FR-004–006, FR-013).

## Phase 4: User Story 3 — Preserve temporary Checkout (P1)

**Independent test**: A new Checkout is visibly Temporary; Check-in alone physically returns it; Assign and Transfer to another employee fail while it is held.

- [x] T013 [US3] Add failing Checkout/Check-in, temporary-custody conflict and distinct list/reporting tests for AS-009–011/019 in `backend/assets/tests_custody.py` and `backend/assets/tests_b3_b5_conformance.py` (FR-007, FR-009, FR-013–014).
- [x] T014 [US3] Set new Checkout classification to Temporary; route Checkout/Check-in through the custody boundary and block Assign/Transfer with the confirmed temporary-holder error in `backend/assets/checkout.py`, `backend/assets/transfer.py` and `backend/assets/custody.py` (FR-003, FR-007, FR-009).
- [x] T015 [US3] Add failing UI test for temporary label, purpose, optional expected-return date and Check-in versus Take Back choices in `frontend/src/pages/checkout/Checkouts.test.jsx` (FR-001, FR-007, FR-013).
- [x] T016 [US3] Make the temporary path clear in `frontend/src/pages/checkout/Create.jsx`, `frontend/src/pages/checkout/Checkouts.jsx` and `frontend/src/pages/asset/Detail.jsx`; verify UI test turns green (FR-001, FR-007, FR-013–014).

## Phase 5: User Story 4 — Approval-gated ongoing Transfer (P1)

**Independent test**: Pending leaves A in custody; approval ends A's exact Assignment and opens B's atomically; rejection leaves custody unchanged.

- [x] T017 [US4] Add failing request/approval/rejection tests for AS-012–015, source-arrangement identity, same-holder and Pending restrictions, temporary/unclassified rejection, changed department and service/terminal stale approval in `backend/assets/tests_custody.py` (FR-008–009, FR-012, ALR-001–003).
- [x] T018 [US4] Capture exact source Assignment in new Transfer requests and make approval atomically close A/open B with audit and unchanged rejection semantics in `backend/assets/transfer.py`, `backend/assets/custody.py`, `backend/assets/models.py` and the additive migration (FR-003, FR-008–009).
- [x] T019 [US4] Add failing UI test for Pending/Approved/Rejected history and Transfer PDF reflecting a real employee handoff in `frontend/src/pages/transfer/Assignments.test.jsx` (FR-001, FR-008, FR-013).
- [x] T020 [US4] Show the three distinct actions and valid ongoing Transfer state in `frontend/src/pages/transfer/Transfers.jsx`, `frontend/src/pages/transfer/Create.jsx` and `frontend/src/pages/asset/Detail.jsx`; keep existing PDF handoff meaning and verify UI test turns green (FR-001, FR-008, FR-013).

## Phase 6: User Story 5 — Classify and reconcile legacy custody (P1)

**Independent test**: IT classifies matching open Checkouts; for a verified approved A-to-B Transfer, reconciliation supersedes A's stale Checkout without physical Check-in and preserves B.

- [ ] T021 [US5] Add failing migration/classification tests for AS-016/017/020/021: legacy rows start Unclassified, matching Temporary stays Open, matching Ongoing becomes an Assignment, mismatch blocks, original issue/expected-return dates remain and physical return fields stay empty in `backend/assets/tests_custody.py` (FR-010–011).
- [ ] T022 [US5] Implement authorized `/checkout/{id}/classify/` with idempotent single-arrangement behavior, classification actor/time and administrative Reclassified closure in `backend/assets/custody.py`, `backend/assets/checkout.py`, `backend/assets/serializers.py`, `backend/assets/views.py` and `backend/assets/urls.py` (FR-010–011, ALR-001–003).
- [ ] T023 [US5] Add failing reconciliation API tests for AS-023/024: verified approved Transfer chain from A to B, unchanged B snapshot, preserved A dates, no return date/inspection, source links, atomic B classification as Temporary or Ongoing, explicit administrative reconstruction/date basis, invalid/unapproved chain rejection and repeat safety in `backend/assets/tests_custody.py` (FR-011, ALR-001–003).
- [ ] T024 [US5] Implement authorized `/checkout/{id}/reconcile/` and approved-chain verification; close A as Superseded with distinct administrative metadata and classify B's current custody atomically, marking any reconstructed B arrangement and Transfer request-date basis rather than inventing a physical issue time, in `backend/assets/custody.py`, `backend/assets/checkout.py`, `backend/assets/serializers.py`, `backend/assets/views.py` and `backend/assets/urls.py` (FR-011, ALR-001–003).
- [ ] T025 [US5] Add failing UI test for classify/reconcile controls, conflict explanation, Transfer evidence and no physical Check-in wording in `frontend/src/pages/checkout/Checkouts.test.jsx` (FR-010–011, FR-013).
- [ ] T026 [US5] Show Unclassified/Conflicting custody and authorized classification/reconciliation in `frontend/src/pages/checkout/Checkouts.jsx`, `frontend/src/pages/transfer/Transfers.jsx` and `frontend/src/pages/asset/Detail.jsx`; verify UI test turns green (FR-010–011, FR-013).

## Phase 7: Cross-cutting lifecycle, reporting and closeout

- [ ] T027 Add failing integration tests for service interruption/close, Lost accountability, Sold/Scrapped eligibility, stale return/approval and exact current holder/type across detail/list/PDF/report output in `backend/assets/tests_custody.py` and `backend/assets/tests_b3_b5_conformance.py` (FR-012–014, ALR-002–005).
- [ ] T028 Route service and terminal transitions through the custody boundary and update read serializers/report queries without changing existing availability rules in `backend/assets/service.py`, `backend/assets/views.py`, `backend/assets/serializers.py` and `backend/assets/custody.py` (FR-012–014).
- [ ] T029 Update the accepted domain language and post-service deliberate reissue rule in `CONTEXT.md` and `docs/adr/0001-service-record-lifecycle.md`; add only reciprocal lineage metadata to accepted predecessor specs and retain `specs/014-asset-assignments/spec.md` (FR-001, FR-007–012).
- [ ] T030 Run focused and complete Django tests with terminal exits, plus frontend Vitest, lint and build, following `specs/014-asset-assignments/quickstart.md`; record results and any unverified paths in the relevant `specs/014-asset-assignments/issues/*.md` (all FR and ALR).
- [ ] T031 Run repository-wide self-description and stale-material inspection; converge remaining verified work, keep the durable feature directory and refresh the official managed context in `AGENTS.md` and `.specify/feature.json` without adopting `specs/living` (constitution III and closeout).

## Dependencies and execution

- T001–T004 establish the shared invariant. T005–T008 (US1) make ongoing custody issuable. T009–T012 (US2) add physical return. T013–T016 (US3) preserve temporary lending. T017–T020 (US4) require the ongoing arrangement. T021–T026 (US5) need the complete custody model and Transfer history. T027–T031 finish lifecycle compatibility and verification.
- Within each behavior slice, run the test task first and record its expected failure before implementation. Complete one local issue and a stable checkpoint before starting the next. One builder writes; no parallel implementation is planned. Independent read-only review begins only after candidate freeze.
- MVP after T008 is a direct ongoing Assign. The authorized scope is all five stories and cross-cutting gates, so stop only at a real blocker or changed accepted decision, not at MVP.
- After the builder completes T031 and freezes a revision, the native delivery workflow assigns a fresh read-only reviewer. Findings return to the same builder; that reviewer re-reviews the repaired revision. Review is a release gate rather than a builder checkbox.
