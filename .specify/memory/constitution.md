<!--
Sync Impact Report
- Version change: unversioned template -> 1.0.0
- Modified principles:
  - Placeholder Principle 1 -> I. Domain Language and Recorded Decisions
  - Placeholder Principle 2 -> II. Lifecycle and Authorization Integrity
  - Placeholder Principle 3 -> III. Specification and Traceability
  - Placeholder Principle 4 -> IV. Test-First External Behavior
  - Placeholder Principle 5 -> V. Incremental Local Delivery
- Added sections:
  - Technical and Documentation Constraints
  - Development Workflow and Quality Gates
- Removed sections: none; placeholder sections were concretized
- Templates:
  - updated: .specify/templates/overrides/plan-template.md
  - updated: .specify/templates/overrides/spec-template.md
  - updated: .specify/templates/overrides/tasks-template.md
- Follow-up TODOs: none
-->
# ITAMS Constitution

## Core Principles

### I. Domain Language and Recorded Decisions

All specifications, plans, tickets, tests, interfaces, and code MUST use the
canonical language in `CONTEXT.md`, including its rejected synonyms and deferred
scope. Work MUST read the ADRs relevant to the affected area before planning or
implementation. Any proposed behavior that conflicts with an ADR MUST identify
the conflict explicitly and obtain an ADR amendment; it MUST NOT silently
override the recorded decision. This keeps product language and engineering
decisions stable across long-running asset-lifecycle work.

### II. Lifecycle and Authorization Integrity

Changes to Asset status, condition, Custodian, Checkout, Transfer, Service
Record, Procurement, Warranty, AMC, or terminal-state behavior MUST preserve the
documented lifecycle invariants. State transitions MUST be expressed through a
single authoritative domain operation and covered atomically where multiple
records change. Every protected backend action and corresponding frontend
surface MUST enforce the existing role-permission model; hiding a UI control is
not authorization. Plans and reviews MUST identify affected actors, permissions,
transitions, failure behavior, and audit or notification effects.

### III. Specification and Traceability

Every non-trivial feature MUST have one durable feature directory under
`specs/<feature-id>-<feature-slug>/`. Its `spec.md` is the requirements source of
truth, while `plan.md`, research, data model, contracts, checklists, and
`tasks.md` refine how the requirement will be delivered. Requirements MUST use
stable identifiers and measurable acceptance scenarios. Plans, tickets, tests,
and implementation evidence MUST remain traceable back to those identifiers.
Lower-level artifacts MUST NOT contradict higher-level intent.

### IV. Test-First External Behavior

Every behavior change MUST begin with an automated test at the highest practical
seam that demonstrates the missing behavior and fails for the expected reason.
Implementation follows the red-green-refactor loop and MUST test observable
outcomes rather than private structure. Changes involving permissions, lifecycle
transitions, persistence, API contracts, or cross-layer user journeys REQUIRE
integration-level coverage. If no suitable harness exists, the plan MUST add one
or record an explicit, user-approved exception before implementation.

### V. Incremental Local Delivery

Work MUST be decomposed into independently verifiable tracer-bullet slices that
fit one focused implementation session and keep the repository in a valid state.
Spec Kit's `tasks.md` is a planning and consistency-analysis artifact; approved
implementation work MUST be published as one Markdown issue per ticket under the
feature's `issues/` directory. Each issue MUST declare blockers, acceptance
criteria, and a canonical status from `docs/agents/triage-labels.md`.
`speckit-taskstoissues` MUST NOT be used because the authoritative tracker is
local. Implementation proceeds from unblocked local tickets, not directly from
an unreviewed generated task list.

## Technical and Documentation Constraints

- The current architecture is a Django REST backend under `backend/` and a
  React/Vite frontend under `frontend/`. A feature may change this baseline only
  when its plan justifies the change and an ADR records a lasting architectural
  decision.
- `.specify/` is managed Spec Kit infrastructure. Durable feature artifacts and
  local implementation tickets belong under `specs/`.
- Project-local Spec Kit customizations MUST use supported template overrides or
  explicit constitution propagation. Managed command skills MUST NOT be edited
  casually because integration upgrades track them.
- Secrets, credentials, local databases, uploaded media, virtual environments,
  dependency directories, and build output MUST remain untracked.
- Requirements and plans MUST identify relevant privacy, permission, audit,
  notification, export, and data-retention effects when those concerns are in
  scope.

## Development Workflow and Quality Gates

1. Read `CONTEXT.md`, relevant ADRs, the active feature spec, and repository
   agent instructions before making a plan.
2. Run specification, clarification, planning, requirements-checklist, task, and
   analysis phases as appropriate. No implementation starts while a
   constitution violation, unresolved critical clarification, or incomplete
   required checklist remains.
3. Convert the reviewed task graph into local tracer-bullet issues with
   `to-tickets`; review their granularity and blocking edges before execution.
4. Implement one unblocked ticket at a time using test-first development. Update
   the ticket with evidence and status without rewriting unrelated feature
   history.
5. For backend changes, run the relevant Django tests and normally the complete
   `python manage.py test` suite from `backend/`. For frontend changes, run
   `npm run lint` and `npm run build` from `frontend/`, plus feature tests when a
   test harness applies.
6. Review completion against the constitution, `spec.md`, the plan, acceptance
   criteria, permissions, lifecycle invariants, and observable end-to-end
   behavior.

## Governance

This constitution governs the ITAMS specification and delivery process.
`CONTEXT.md` remains authoritative for domain terminology, ADRs remain
authoritative for accepted architecture and lifecycle decisions, and the active
feature `spec.md` remains authoritative for feature intent. When these sources
conflict, work MUST stop and the conflict MUST be resolved in the appropriate
source before implementation continues.

Amendments require an explicit rationale, review of affected templates and
runtime guidance, and a migration note for active features. Constitution
versions follow semantic versioning: MAJOR for incompatible governance changes,
MINOR for added or materially expanded principles, and PATCH for
non-semantic clarification. Every plan and final review MUST include a
constitution-compliance check. Unjustified complexity or an unapproved exception
blocks implementation.

**Version**: 1.0.0 | **Ratified**: 2026-07-28 | **Last Amended**: 2026-07-28
