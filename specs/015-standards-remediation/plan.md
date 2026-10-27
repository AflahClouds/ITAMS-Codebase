# Implementation Plan: Standards Remediation

**Feature Directory**: `specs/015-standards-remediation/`
**Date**: 2026-10-27
**Spec**: [spec.md](spec.md)
**Input**: Accepted six-fix specification, FR-001–FR-009, ALR-001–ALR-003, AS-001–AS-018.

## Summary

Repair the six Standards defects using the current Django/DRF and React application. Add Brand-aware Model maintenance, normalized identity validation with durable conflict auditing, complete direct Audit Trail and Setting mutation audit coverage, and literal-text protections at the shared PDF/Excel export boundary. Preserve existing permissions, business-record scope, database contents, and unrelated work. Deliver six independently verifiable local tickets followed by integrated verification and independent review.

## Technical Context

**Backend**: Existing Python environment (3.14.4 recorded by pyvenv.cfg), Django 6.0.5 and DRF 3.17.1 from backend/requirements.txt. Preserve installed versions and the dependency lock policy; no dependency changes.
**Frontend**: Existing React 19, Vite, Material UI, npm package-lock, Vitest/jsdom/Testing Library.
**Storage**: Existing SQLite models and request transactions (ATOMIC_REQUESTS). Model.brand stays schema-nullable for legacy readability; supported new writes require a valid Brand. No production migration or backfill.
**Testing**: Django APIClient integration tests; focused React integration tests; in-memory generated PDF/Excel inspection using existing libraries. Export resource access must be mocked/asserted rather than attempted.
**Target Platform**: Existing browser client and Django web service.
**Performance Goals**: Preserve existing limits, ordering, and data scope; no new throughput target. Use bounded lookups and existing export generation, with no per-cell external I/O.
**Constraints**: Required audits fail closed and commit with mutations; normalized conflict rejection audit must survive DRF rollback behavior. No secrets or returned audit payload in logs. No Asset lifecycle changes.
**Scale/Scope**: Five catalog master types, one master-data page, direct audit reads, Setting mutations, shared report/Transfer PDF and report Excel builders. No schema migration or broad data cleanup.

## Constitution Check

- **Domain and decisions — PASS**: CONTEXT.md vocabulary and ADR-0001 preserved; no new architecture decision.
- **Lifecycle and authorization — PASS**: Existing settings_access, audit_access, Admin policy, report_access, and Transfer-document visibility remain authoritative. No lifecycle mutation. API request transaction covers required audit; rejected duplicate writes use a rolled-back savepoint or pre-save rejection and a durable audit entry.
- **Traceability — PASS**: Six stories map directly to six issues and the task/test table below; acceptance values are the user's accepted examples.
- **Persistence and lineage — PASS**: Accepted change scope is separately recorded; predecessor edits are reciprocal lineage metadata only. Existing durable historical feature requirements are preserved. Any guide-owned canonical living-spec consolidation must retain their meaning and recoverable history; it occurs only after reviewed delivery, never during implementation.
- **Test-first delivery — PASS**: Every fix begins with permanent fail-before API/export/UI tests. Permission, persistence, and audit failure cases use integration-level coverage. No exception requested.
- **Local execution — PASS**: tasks.md is planning input; issues/ contains the executable vertical slices. One native builder writes, a fresh native reviewer reads only, then the same builder/reviewer repair and re-review.
- **Post-design recheck — PASS**: No new dependency, privilege, lifecycle transition, unmanaged policy edit, or premature canonical mutation is required.

## Project Structure

### Documentation (this feature)

spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/standards.md,
checklists/requirements.md, tasks.md, and issues/01–07.

### Source Code (repository root)

- backend/catalog/{serializers,views}.py and catalog integration tests.
- backend/core/{views,exports}.py, a narrowly scoped conflict helper only if needed, and core integration/export tests.
- frontend/src/pages/admin/Masters.jsx and Masters.test.jsx.
- Existing reporting/Transfer routes and tests for export integration.

**Structure Decision**: Extend existing modules. A small catalog-only identity validator/view mixin is sufficient for shared five-master behavior; do not create a general workflow framework. Shared PDF/Excel builders are the text-safety boundary.

## Phase 0: Research

Local source and verified probes settle the implementation choices; there is no unresolved technology question requiring external research or a research agent. See research.md for decisions, rationale, and alternatives. The global CLI was verified as 1.2.0, incompatible with the installed workflow's strict 1.0.13 dispatch reader. The user separately authorized an isolated 1.0.13 runtime at `.clouds-install-source/runtimes/specify-1.0.13/`; installation preserved the global CLI and loaded AGENTS.md hash. Use that isolated interpreter and CLI for this delivery. The pre-dispatch 1.2.0-created run `4fd2eeff` is retained as rejected schema evidence and superseded after a preparation checkpoint; no child was started under it. This is a runtime repair, not a change to requirements or the production stack.

## Phase 1: Design and Contracts

See data-model.md and contracts/standards.md. Normalize before uniqueness lookup; Model uniqueness is Brand plus normalized name. Exclude the current row on updates. Reject blank names and invalid Brand references. Translate only known identity conflicts (including a save-time race) into a useful 400 response and record one rejection audit outside any rolled-back savepoint; unrelated persistence failures must still fail closed.

Audit Trail list/retrieve records one access audit per successful request without recursively reading/logging the returned contents. Preserve the list's filtered 1,000-row disclosure and source-IP projection. Individual retrieval must not attempt filtering a sliced queryset. Audit persistence failure returns no protected payload.

Add standard mutation hooks for Setting PUT/PATCH/DELETE while preserving existing POST/upsert and exactly-one logging. Record key/action/actor, never secret values; failure rolls back the mutation.

Escape literal user text for every ReportLab Paragraph position, preserving intentional application markup only around escaped values. Force user strings to spreadsheet string cells, preserving exact text and numeric/bool/date/None types. No CSV workflow changes.

## Test Strategy

| Slice | Requirements / scenarios | Fail-before and observable verification |
| --- | --- | --- |
| US1 | FR-001; AS-001–003 | API create/read/update retains Brand, missing/unknown/null rejected, legacy read/correction preserves IDs/references; React master form sends/selects/displays Brand. |
| US2 | FR-002–003; AS-004–007 | API case/whitespace duplicates across all five types, rename/self-update, same model name across Brands, blank names, simulated save race, durable rejection audit and unchanged records. |
| US3 | FR-004,006; AS-008–010 | API list/filter/empty/retrieve adds one access entry; denied reader stays denied; audit write failure returns no content; no payload/secret duplication. |
| US4 | FR-005–006; AS-011–013 | API POST/upsert/PUT/PATCH/DELETE exactly-one audit, permissions and injected audit failure rollback, key-only privacy. |
| US5 | FR-007,009; AS-014–015 | Actual shared and public report/Transfer PDFs contain literal markup-like strings; no resource retrieval; ordinary formatting preserved. |
| US6 | FR-008–009; AS-016–018 | Reopen actual XLSX exports; strings =1+1/+/-/@ stay literal strings; numbers 0/-1, bools, date-like typed values/None keep types. |

Run focused tests after each slice and checkpoint only a green coherent slice. Final backend suite normally takes about 8–12 minutes (review baseline 354 tests in 499s). Retain one process handle through terminal exit; do not duplicate a healthy run. Frontend full suite uses serial workers where necessary to avoid the observed parallel timeouts, reporting actual flags; lint/build remain required. Capture commands, terminal exits and counts in issue evidence. Inspect migrations with check --dry-run if model declarations change. Do not claim manual browser/PDF visual checks not performed.

## Delivery Authority and Routing

Trusted source: direct Codex in this repository. Separate Specify/Clarify and final scope/sprint approvals are recorded in spec.md#clarifications. The accepted requirements/checklist are bound to baseline 067f141 and the presented hashes; authority/stage metadata updates preserve requirement bytes. No portable handoff, Sites destination, Work routing, or paid capacity is involved.

Task class: high-risk-deterministic because catalog identity, audit accountability and operational exports can affect inventory/security decisions. Complete expected-outcome oracle: AS-001–018 and the table above, requiring fail-before then pass-after tests before each production change. Native workflow oracle_evidence references this complete oracle, not a claim that tests have already run.

Builder and reviewer: independently select gpt-6.1-sol using the host-advertised native model. The builder must safely handle transactional audit rejection and typed export edge cases; the reviewer must independently challenge those boundaries across six slices. The cheaper fast-model option does not meet these cross-layer security/accountability and oracle-review bars with lower expected repair cost. No Astra request or paid/reset fallback. Distinct native child identities; no reuse of the earlier whole-codebase review assignments. Inventory-check each exact new assignment before spawn.

One builder owns application/test/ticket edits, verification and development checkpoints. Reviewer is fresh and read-only; compare HEAD, all index entries and complete tracked/nonignored worktree content before/after, including pre-existing dirty files. A frozen result only is reviewed. Same bounded children repair/re-review. Root coordinates and performs guide-owned preparation/closeout, not builder implementation or tests.

Verified remote: https://github.com/AflahClouds/ITAMS-Codebase.git. origin/main observed ef0f3c231e265f917e4ec191ebd2033bad605d42 is an ancestor of baseline HEAD. Development destination is exactly origin refs/heads/codex/015-standards-remediation (not present at initial ls-remote). Before each checkpoint push verify branch, HEAD, remote destination, ancestry and remote state; no force, tags, main writes, merge or deployment. Preserve pre-existing .claude/settings.local.json and any other unrelated state. Sandbox-only apparent workflow deletions are not user deletions: elevated inspection proves the installed files exist; do not stage their removal. Failed ordinary development pushes are nonblocking.

Hard stops: material scope/technology/policy conflict, lost user work or authority identity, required model/capability unavailable, unsafe external mutation, or native safety limit. Routine plan/ticket corrections and technical choices within this authority need no new approval. Preserve exact children/process handles if waiting is required.

## Predecessor and Closeout Discipline

Successor proof replaces only the old catalog serializer/validation paths, direct-read and inherited Setting audit gaps, raw PDF Paragraph inputs and raw XLSX string writes. Remove obsolete duplicate code paths only after regression proof, retaining historical specs. Update only current relevant documentation and official context via supported tools. One final task checks repository-wide stale material plus self-description/resume facts; unrelated defects remain documented out of scope.

Guide-owned post-convergence work stays outside the task ledger: independently reviewed canonical consolidation where applicable under governing preservation rules, requirements checklist validation, temporary-artifact cleanup only with proven successor/recovery/ownership, supported pointer/context restoration, post-cleanup checks and final checkpoint. Preserve the ratified durable-feature convention and immutable predecessor requirements; no policy migration is inferred from generic overlay wording. Surface any actual convention conflict before destructive cleanup.

## Complexity Tracking

No constitution exception or new production dependency is needed. Keep the smallest shared catalog helper and existing export builders; no new framework or migration/backfill.
