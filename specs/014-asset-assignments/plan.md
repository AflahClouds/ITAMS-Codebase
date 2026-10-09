# Implementation Plan: Ongoing Asset Assignments and Temporary Checkout

**Feature Directory**: `specs/014-asset-assignments/`
**Date**: 2026-09-29
**Spec**: [spec.md](spec.md)

**Input**: Accepted scope in `spec.md`, the user's three original 2026-09-29 Clarify answers, and the approved 2026-10-08 historical Transfer date-basis clarification already recorded in that specification. Local sprint authority applied to this feature on the isolated `codex/014-asset-assignments-delivery` branch, derived from checkpoint `877ad2a`; it granted no push, merge, deployment, or release.

## Summary

Keep Checkout and Check-in for temporary loans. Add an ongoing Assignment and Take Back path in the existing Transfer area. Existing employee-to-employee Transfer remains approval gated. Every custody action updates the Asset and active custody history together. IT classifies open legacy Checkouts and may reconcile a stale Checkout only when approved Transfer history proves the current Custodian. The repository's durable feature specification convention remains in force; no living-spec migration or deletion is planned.

## Technical Context

**Backend**: Existing Python/Django 6.0.5/Django REST Framework 3.17.1 (`backend/requirements.txt`).

**Frontend**: Existing React 19, Vite 8, Material UI 9, Axios, Formik and Yup (`frontend/package.json`).

**Storage**: Existing Django models and SQLite in local development. Add custody history fields/models through normal migrations; use no new data store.

**Testing**: Django test runner with domain-service and API integration tests; existing Vitest/React Testing Library for custody screens. Write observable failing tests before each behavior change.

**Target Platform**: Existing browser client and Django REST service.

**Performance Goals**: Preserve existing paginated/list behavior. No new volume or latency target was accepted; the implementation must avoid loading full custody history for every row and verify bounded list queries in relevant tests where changed.

**Constraints**: One current holder and one active custody arrangement per circulating Asset; condition independent of status; `asset_custody_manage` for Assign, Take Back, classification and reconciliation; `transfer_request` for requests; audit state changes atomically; notifications follow existing in-app policy after a successful state change; no fabricated physical returns.

**Scale/Scope**: The existing asset population and all open Checkout rows may need one-time classification. No production count is recorded, so the adoption flow must be incremental and resumable. Affected UI surfaces are Checkout, Transfer, Asset details and the corresponding lists; reporting must continue to show the correct holder/status.

## Constitution Check

*GATE: Passed for planning; recheck after Phase 1 and before implementation.*

- **Domain and decisions**: `CONTEXT.md` currently reserves Checkout for all issuance and rejects Assignment; ADR-0001 says fresh Checkout after service. The accepted feature explicitly changes those narrow obligations while retaining service custody clearing and no automatic reissue. Update the authoritative glossary and amend/supersede the ADR's reissue wording as part of the same feature before completion. Preserve other accepted obligations.
- **Lifecycle and authorization**: Assignment, Take Back, Transfer, Checkout, Service Record and terminal transitions must share one authoritative custody check. Protected backend actions and UI affordances use permission codes, including custom roles. Required audit is part of the database transaction; notify active recipients after commit where applicable.
- **Traceability**: Assign maps to FR-001–003, AS-001–004; Take Back to FR-004–006, AS-005–008/018/022; temporary lending to FR-007/009, AS-009–011/019; Transfer to FR-008, AS-012–015; adoption to FR-010/011, AS-016/017/020/021/023/024; service/terminal/reporting to FR-012–014 and ALR-001–005.
- **Persistence and lineage**: `spec.md` records accepted scope for this Change feature. Do not edit accepted requirement content of predecessors. Add reciprocal lineage metadata to relevant predecessors and retain the durable feature directory after closeout. No canonical `specs/living` exists or has been adopted for ITAMS; the installed guide's living-spec closeout instruction conflicts with constitution 1.1.0 and the installation record, so the constitution controls.
- **Test-first delivery**: Every behavior slice starts with a failing domain/API integration test; frontend behavior gets focused UI tests. Include physical return, damaged condition, pending Transfer, legacy reconciliation, service interruption, stale action, permission and concurrency cases.
- **Local execution**: Use `tasks.md` for planning, then publish reviewed vertical slices as local issue files under `issues/`. Only one builder writes implementation; a fresh read-only reviewer inspects a frozen candidate and the same builder repairs findings. Keep commits local.
- **Stop conditions**: Pause if implementation needs to change accepted business behavior, introduce a material dependency, cannot preserve legacy dates/history, cannot isolate unrelated user changes, cannot execute required tests or independent review, or the native workflow conflicts with the constitution's durable-spec rule.

## Project Structure

### Documentation (this feature)

```text
specs/014-asset-assignments/
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
|-- assets/        # custody models, services, serializers, views, routes and tests
|-- core/          # existing audit and notification services
|-- itams/
`-- manage.py

frontend/
|-- src/api/
|-- src/pages/asset/
|-- src/pages/checkout/
|-- src/pages/transfer/
|-- src/pages/service/
`-- package.json
```

**Structure Decision**: Extend `assets` and the existing Transfer UI. A small new custody service/module may centralize state transitions if needed; no new top-level app, framework or runtime is justified. Keep existing Checkout and Transfer URLs for compatibility; add explicit Assignment and reconciliation actions rather than repurposing generic edit endpoints.

## Phase 0: Research

See [research.md](research.md) for checked-in behavior, decisions, alternatives and unresolved risks. The preferred shape is a separate ongoing Assignment record alongside existing Checkout history, with one custody transition service enforcing both. Mark open pre-feature Checkouts as unclassified for IT review; all new Checkouts are temporary. Preserve date fields and record administrative closure separately from physical Check-in. No external library research or new dependency is needed.

## Phase 1: Design and Contracts

See [data-model.md](data-model.md), [custody API contract](contracts/custody-api.md), and [quickstart.md](quickstart.md).

- Add a durable ongoing Assignment record with issue condition, holder, timestamps, closure reason, return condition and source links. Add explicit classification and closure metadata to Checkout without rewriting original issue/expected-return dates.
- Keep `Asset.status`, `condition`, `custodian` and `department` as the current snapshot. Domain operations lock/re-read current state, validate active custody and pending approvals, then persist snapshot, history, condition inspection and required audit together. Notification failure cannot undo committed custody.
- A transfer request is valid only against current ongoing Assignment. Approval verifies the captured source arrangement still matches and atomically closes it and opens the target Assignment. Rejection leaves custody unchanged. Take Back refuses a Pending Transfer with the accepted error.
- Legacy classification is explicit and per Asset. For a verified approved A-to-B Transfer, an audited reconciliation closes A's stale Checkout as superseded, preserves its dates, retains B's snapshot and creates one classified current arrangement in the same operation. Unverified differences remain blocked.
- Service and terminal paths close/interrupt active Assignment and Checkout appropriately. A stale return or approval cannot release or replace a later holder. Read models expose custody type and history without mixing temporary loans with ongoing assignments.

**Post-design constitution recheck**: The model and API contract retain one Asset snapshot, explicit permission checks, atomic history/audit, distinct physical and administrative closure, and no new technology. The test strategy covers every accepted high-risk custody transition before code. This change feature remains durable under constitution 1.1.0. No exception is requested; the scope remains inside the accepted business rules.

## Test Strategy

1. **Issue/return** (AS-001–008, AS-018/022): failing API tests for permission, direct Assign, issue condition, physical Take Back, damaged Available outcome, worse-condition remarks, disabled former holder, Pending Transfer block and stale repeat. Follow with UI tests for the visible action and actual condition selection.
2. **Temporary Checkout** (AS-009–011/019): failing API tests that block Assign/Transfer while Checkout is open and retain Check-in behavior; UI tests show the temporary error and distinguish current custody type.
3. **Transfer** (AS-012–015): failing integration tests for source snapshot, atomic history handoff, rejection, condition and stale approvals. Include service/terminal interruption.
4. **Legacy adoption** (AS-016/017/020/021/023/024): failing migration and action tests for unclassified open rows, temporary/ongoing classification, verified supersession with preserved dates/no physical return, unverified rejection, audit and idempotent retries.
5. **Broader checks**: `python manage.py test` from `backend/`; `npm test -- --run`, `npm run lint`, `npm run build` from `frontend/`, plus a browser path only when available and relevant. These commands are checked-in scripts, but their success remains unverified until run in this worktree.
6. **Closeout**: One repository-wide review checks stale Checkout-only instructions, duplicate entry points, documentation self-description, lineage and feature routing. Run independent read-only review on the frozen candidate and repeat affected tests after repairs. Retain this durable feature directory.

## Complexity Tracking

No constitution exception is requested. The separate Assignment record adds one domain concept because Checkout remains temporary and its historical contract must remain readable. A single custody transition boundary limits the cross-table consistency cost.
