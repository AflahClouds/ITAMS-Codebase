# Implementation Plan: Asset Procurement Lifecycle

**Feature Directory**: `specs/016-asset-procurement-lifecycle/`
**Date**: 2026-10-29
**Spec**: [spec.md](spec.md)

**Input**: Accepted specification and current-update local-sprint authority in
spec.md#clarifications.

## Summary

New Assets start In Storage. New Procurement associations make eligible Assets
Available; detachment returns them to In Storage. Asset deletion is blocked while
linked. Explicit singleton Procurement deletion removes its purchase/history and
invoices, retaining the Asset for separate deletion. Ordinary archive remains.

Use the existing Django/React stack and one small authoritative
`assets/procurement_lifecycle.py` module for transactional association/status and
singleton release operations. Reuse serializers for input/arrival validation and
views for authorization/audit/notifications. No new dependency or broad framework.

## Technical Context

**Backend**: Existing Python 3.14.4, Django 6.0.5, DRF 3.17.1.
**Frontend**: Existing React 19, Vite, Material UI, npm/package-lock.
**Storage**: Existing SQLite/Django models, ATOMIC_REQUESTS, private invoice
storage. Default-only Asset status migration; no existing-row rewrite/backfill.
**Testing**: Django TestCase/APIClient and Vitest/Testing Library.
**Target Platform**: Existing browser client and Django web service.
**Performance Goals**: Preserve existing request interaction; no new numerical
latency/scale commitment. Bound work to affected purchase/Assets.
**Constraints**: Atomic link/status changes, exact existing authorization,
reasoned history, independent audit retention, post-commit private-file cleanup,
custody/terminal protection, and no historical mass status correction.
**Scale/Scope**: Asset create/edit/delete and Procurement create/edit/release;
one default migration, focused regression updates, no production data backfill.

## Constitution Check

Pre-research and post-design gates pass:

- **Domain and decisions**: Canonical terms and ADR-0001 retained. User explicitly
  resolves scoped B6 archive-only conflict for last-Asset deletion.
- **Lifecycle and authorization**: Single authoritative operations own atomic
  changes; existing permissions and role checks remain. Fail closed on stale
  links, protected states, missing authority, and audit/history failure.
- **Traceability**: US1: FR-001/002/008, AS-001–005. US2: FR-003/004/008,
  AS-006–009. US3: FR-005–008, AS-010–013. ALR-001–005 and SC-001–004
  receive regression and final verification coverage.
- **Persistence and lineage**: Accepted Change records scoped supersession;
  add predecessor metadata only, preserving historical requirements.
- **Test-first delivery**: API integration and form-flow tests fail for the
  expected reason before each production slice; retain permanent regressions.
- **Local execution**: Publish four vertical issues; execute unblocked issues.
  tasks.md remains planning input.

No constitution exception or technology-envelope change is needed.

## Project Structure

### Documentation (this feature)

spec.md, plan.md, research.md, data-model.md, quickstart.md,
contracts/lifecycle.md, checklists/requirements.md, tasks.md, issues/.

### Source Code (repository root)

- backend/assets/{models,serializers,views}.py, procurement_lifecycle.py,
  a default migration and relevant integration tests.
- frontend/src/pages/asset/{Create,Edit,Delete,Assets}.jsx and existing form/detail
  regressions; frontend/src/pages/procurement/{Procurement,Edit,Delete}.jsx
  and regression tests; reuse confirmation/error components.
- Current README/domain prose and predecessor lineage metadata only.

**Structure Decision**: A focused helper owns lock/revalidation/status invariants;
avoid signals, global save hooks, or a general workflow framework.

## Phase 0: Research

One read-only agent traced callers, direct-write bypasses, invoice storage,
custody lock/conditional-write patterns and tests while the root prepared
artifacts. See research.md for decisions, rationale and alternatives.
No external service, API or technology selection is required.

The existing isolated .clouds-install-source/runtimes/specify-1.0.13/ interpreter
was verified as 1.0.13; use it for native workflow. No install/update. Elevated
inspection confirms apparent sandbox workflow deletions are access artifacts;
preserve installed files and unrelated native run state.

## Phase 1: Design and Contracts

See data-model.md and contracts/lifecycle.md. Keep existing Procurement DELETE
archive-only; add explicit permanent-delete action requiring asset_delete and
exactly one eligible Asset. Reject multi-Asset destructive deletion.

Lock/re-read actual affected rows and revalidate associations/state at save time;
use consistent lock order and conditional writes for SQLite limitations. Do not
trust deserialized snapshots/cached counts. Reject direct Asset procurement
mutation; Procurement owns arrival/reason validation. Prevent direct promotion
of new unprocured Assets from bypassing staging. Preserve metadata-only edits.

Remove owned invoice/history rows atomically with purchase; capture exact private
storage names and delete files after successful commit. Test rollback/no file
loss. Retain independent audit identifying actor, purchase, Asset and state
effects without invoice contents. Existing applicable manager notifications use
surviving Asset/list destinations. Do not silently overwrite or detach protected
Assigned/Under Repair/terminal states. Custody-history deletion remains protected.

## Test Strategy

| Slice | Fail-before observable outcomes |
| --- | --- |
| US1 | API/form create Storage; singleton/batch/new purchase links Available; existing purchase attachment Available; optional invoice; metadata edits preserve state; validation/audit/history failure rolls back; direct status/procurement bypass rejected. |
| US2 | Linked and archived-linked Asset DELETE rejected; reasoned multi-Asset detach only changes removed Assets to Storage; separate deletion if eligible; custody history/protected state/permissions retained. |
| US3 | Empty edit explains complete deletion; explicit singleton release removes purchase/history/invoice rows and committed files, retains Asset Storage; separate Asset DELETE; ordinary archive preserved; denied/multi-Asset/stale/audit-failure cases preserve all data/files. |

Use API/form seams and injected failures at real transaction/commit boundaries.
Update old expectations only where approved scope supersedes them. Fixtures
needing Available stock state it explicitly or link valid Procurement; do not
weaken independent custody assertions.

Required checks: focused Django/frontend cases; full backend suite; full serial
frontend suite; lint; build; makemigrations --check --dry-run. Commands are in
quickstart. Full backend baseline takes roughly 8–12 minutes. Builder retains one
process handle per run, records ETA and next meaningful check, waits to terminal
exit, never duplicates a healthy run, and owns all verification. Root coordinates.

## Delivery Authority and Routing

Trusted source: direct Codex. Three current-update approvals and presented hashes
are in spec.md#clarifications. Scope unchanged. No main promotion, deployment,
new task/handoff, paid API, reset redemption or capacity purchase.

Task class: high-risk-deterministic (inventory integrity and purchase deletion).
Complete business oracle: AS-001–013 and Test Strategy table. Observe intended
failure before production changes and pass after; preserve permanent regressions.

Independently choose native gpt-6.1-sol for builder and reviewer, supported by the
host dispatch schema. Builder must handle cross-layer locks, rollback, storage
commits and custody; reviewer must independently challenge destructive inventory
boundaries. The cheaper fast model does not meet either role's quality bar at
lower expected repair cost. No Astra request. Native inventory/completion tools
are available. Distinct children; same bounded builder repairs and reviewer
re-reviews. Research is independent read-only discovery only.

Root owns preparation/guide closeout; builder alone edits application/tests,
tickets and verification evidence, then freezes candidate. Reviewer is read-only;
compare HEAD, all index entries and complete tracked/nonignored content before
and after. Include unrelated preexisting files; exclude only active-run allowed
state/input/log temporaries. Preserve existing .claude settings and old runs.

Verified origin: https://github.com/AflahClouds/ITAMS-Codebase.git.
Remote main observed ef0f3c231e265f917e4ec191ebd2033bad605d42.
Exact development destination: origin refs/heads/codex/016-asset-procurement-lifecycle,
absent initially. Verify branch/HEAD/ancestry/remote before every checkpoint push.
No force/tags/main mutation. Failed pushes are nonblocking, preserving local work.

Hard stops: material scope/policy conflict, unavailable required host capability,
lost authority/unrelated work, or workflow safety limit. Current sprint authority
covers routine ticket granularity and repairs; no repeated phase approvals or
optional to-tickets interview.

## Predecessor and Closeout Discipline

After successor proof replace old Available create defaults/options, bulk link
writes without state control, missing Procurement Asset-delete check and generic
last-Asset error. Update current comments/docs and only superseded expectations.
Retain custody/ordinary archive coverage. No dependency or flag is obsolete.
Add predecessor lineage metadata only.

Final task combines repository-wide stale-material/reference review,
self-description/resume facts, required verification and checkpoints.
Guide-owned consolidation/review/post-closeout checks stay outside tasks.md.
Preserve the live constitution's immutable history and per-feature convention:
retain this accepted authoritative feature/evidence, never rewrite predecessor
requirements or delete historical records under generic overlay language.
Consolidate current domain/README descriptions and lineage after verified behavior.

## Complexity Tracking

No exception. One focused helper, explicit singleton action, default-only
migration; no framework, material dependency or backfill.