# Tasks: Standards Remediation

**Input**: spec.md, plan.md, research.md, data-model.md, contracts/standards.md.
**Tests**: Required fail-before regressions at API/UI/delivered-file seams.
**Publication boundary**: Planning input only; execute the separate approved issues/01–07.
**Persistence gate**: Accepted change scope and current-update full local sprint authority recorded in spec.md. Historical predecessors are unchanged except lineage.

## Phase 1: Feature Setup

- [x] T001 Verify accepted spec/checklist/branch identity and preserve unrelated work in specs/015-standards-remediation/issues/01-model-brand.md before writing application code.

## Phase 2: Foundational

No new framework, schema, or shared foundational implementation is needed. Each story owns its regression before its fix; existing permissions and request transactions are reused.

## Phase 3: User Story 1 — Record a Model with its Brand (P1)

Goal: Brand-backed Model creation/read/correction and an operational maintenance form.
Independent test: AS-001–003 API and UI journey.

- [x] T002 [US1] Add and observe failing AS-001–003 API regressions in backend/catalog/tests_standards.py and Brand selection/display tests in frontend/src/pages/admin/Masters.test.jsx; prove missing/invalid/null Brand handling and stable legacy Model IDs/references.
- [x] T003 [US1] Expose/validate Model Brand in backend/catalog/serializers.py and add Brand selection/display in frontend/src/pages/admin/Masters.jsx; new creation requires one valid Brand, explicit clear is rejected, historical nullable rows remain readable and correctable. Covers FR-001, ALR-001–003.
- [x] T004 [US1] Run focused API/UI green checks, remove the superseded unbranded write path from backend/catalog/serializers.py, and record terminal evidence plus a coherent development checkpoint in issues/01-model-brand.md.

## Phase 4: User Story 2 — Normalized identity conflicts (P1)

Goal: Stable catalog identity with useful and audited duplicate rejection.
Independent test: AS-004–007 across all five master types.

- [x] T005 [US2] Add and observe failing case/whitespace, blank, self-update, rename, same-name/different-Brand, and save-time race regressions in backend/catalog/tests_standards.py, including one durable rejection audit and no partial mutation/reference changes.
- [x] T006 [US2] Implement normalized and Brand-scoped identity validation plus known-conflict handling/audit durability in backend/catalog/serializers.py and backend/catalog/views.py (small catalog helper if justified); preserve display casing and reject only recognized conflicts. Covers FR-002–003, ALR-001–003.
- [x] T007 [US2] Run focused green checks, remove the superseded exact-only duplicate path from backend/catalog/serializers.py, and record terminal evidence plus a checkpoint in issues/02-normalized-identity.md.

## Phase 5: User Story 3 — Direct Audit Trail read accountability (P1)

Goal: One private access record per successful list/filter/detail read, failing closed.
Independent test: AS-008–010 including empty results and injected audit failure.

- [x] T008 [US3] Add and observe failing list/filter/empty/retrieve and audit-failure integration tests in backend/core/tests_standards.py; verify existing denial, IP privacy, omission disclosure and no recursive/payload copying.
- [x] T009 [US3] Audit successful direct reads in backend/core/views.py, using an unsliced detail queryset while retaining the list limit/envelope; required audit failure exposes no protected content. Covers FR-004, FR-006, ALR-001–003.
- [x] T010 [US3] Run focused green checks, remove the old unaudited read behavior in backend/core/views.py, and record terminal evidence plus a checkpoint in issues/03-audit-reads.md.

## Phase 6: User Story 4 — Setting mutation accountability (P1)

Goal: Exactly one private audit for every supported Setting mutation, atomic on failure.
Independent test: AS-011–013 through POST/upsert/PUT/PATCH/DELETE.

- [x] T011 [US4] Add and observe failing all-method Setting audit, injected audit-failure rollback and permission/privacy tests in backend/core/tests_standards.py.
- [x] T012 [US4] Add minimized mutation audit hooks in backend/core/views.py, preserve POST/upsert and avoid duplicate logs; no Setting secret values and no unaudited inherited mutation remain. Covers FR-005–006, ALR-001–003.
- [x] T013 [US4] Run focused green checks and record terminal evidence plus a checkpoint in issues/04-setting-audits.md.

## Phase 7: User Story 5 — Literal PDF text (P2)

Goal: Safe literal company/headings/cells/Transfer text with intended layout preserved.
Independent test: AS-014–015 using generated report/Transfer documents.

- [x] T014 [US5] Add and observe failing actual PDF text and no-resource-load regressions in backend/core/tests_exports_standards.py, including public report/Transfer delivery and markup-like values in every user-text position.
- [x] T015 [US5] Escape user text at shared Paragraph boundaries in backend/core/exports.py while preserving application-owned formatting; remove superseded raw user-markup input paths. Covers FR-007, FR-009, ALR-001–003.
- [x] T016 [US5] Run focused green checks, inspect delivered document content using existing tools, and record terminal evidence plus a checkpoint in issues/05-literal-pdf.md.

## Phase 8: User Story 6 — Literal Excel text (P2)

Goal: User strings remain literal and non-string values keep their types.
Independent test: AS-016–018 by reopening exported workbooks.

- [x] T017 [US6] Add and observe failing XLSX regressions in backend/core/tests_exports_standards.py for =1+1, +, -, @ strings, headings/company fields and typed 0/-1/bool/date/null values, including public delivery.
- [x] T018 [US6] Mark string cells explicitly as text in backend/core/exports.py without modifying their visible values or non-string types; remove superseded raw formula-promoting string writes. Covers FR-008–009, ALR-001–003.
- [x] T019 [US6] Run focused green checks and record terminal evidence plus a checkpoint in issues/06-literal-excel.md.

## Final Phase: Verification and Pre-closeout Review

- [ ] T020 Run the complete backend suite and relevant frontend tests/lint/build from quickstart.md, retaining each long-running process handle until terminal exit, and record actual counts/flags/exits in issues/07-verification.md. If model declarations change, verify migration drift with --check --dry-run. Covers SC-001–005.
- [ ] T021 Freeze a committed candidate; obtain a fresh read-only native reviewer assessment with complete before/after HEAD/index/worktree evidence. The same builder repairs findings and the same reviewer re-reviews; no concurrent writer/reviewer. Record evidence in issues/07-verification.md.
- [ ] T022 Complete one repository-wide stale-material/self-description review, bounded successor-path cleanup after proof, current source/operation/resume facts and supported context update; record no remaining implementation task in issues/07-verification.md and a stable final implementation checkpoint. Preserve unrelated work and immutable historical requirements.

## Dependencies & Execution Order

T001 precedes US1. US2 follows US1 because Model validation is shared. US3 and US4 are independently testable but execute sequentially in the shared core view module. US5 and US6 execute sequentially in exports.py. Final verification follows all six stories. Issue 07 is blocked by 01–06. All writing is one native builder; no [P] writer tasks are advertised.

## Parallel Opportunities

Only independent read-only discovery may be parallel when its benefit exceeds coordination cost. API and UI test design for US1, audit-read versus Setting test inspection, or PDF versus Excel fixture inspection can be independent, but no extra agents are required for these known local defects. Tests may use native runner concurrency only where reliable; reviewer never overlaps a writer.

## Implementation Strategy

Use US1 as the first independently green tracer bullet, then complete all six accepted slices (no reduction of scope). In each ticket: write/observe red tests, implement the smallest fix, run green checks, update evidence and tasks, and commit/push only that coherent slice under the verified development destination policy. Review the full frozen candidate after integrated checks; repair/re-review until clean. No deployment or main promotion.

Guide-owned canonical review, safe temporary-artifact cleanup, routing restoration and post-cleanup checks occur after task-tracked convergence and are intentionally outside this ledger. The ratified historical-record preservation rule remains binding.






