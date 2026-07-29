<!--
Sync Impact Report
- Version change: 1.0.0 -> 1.1.0
- Modified principles:
  - I. Domain Language and Recorded Decisions -> clarified authority of
    CONTEXT.md and ADRs
  - III. Specification and Traceability -> added brownfield baseline
    persistence, lineage, and evidence rules
- Added sections: none; persistence rules were integrated into existing sections
- Removed sections: none
- Templates:
  - updated: .specify/templates/overrides/spec-template.md
  - updated: .specify/templates/overrides/plan-template.md
  - updated: .specify/templates/overrides/tasks-template.md
  - validated: .specify/templates/spec-template.md
  - validated: .specify/templates/plan-template.md
  - validated: .specify/templates/tasks-template.md
- Runtime guidance:
  - updated: AGENTS.md
  - updated: specs/README.md
  - updated: docs/agents/domain.md
  - updated: docs/agents/issue-tracker.md
- Follow-up TODOs: none
-->
# ITAMS Constitution

## Core Principles

### I. Domain Language and Recorded Decisions

`CONTEXT.md` is authoritative for canonical domain terminology, rejected
synonyms, shared lifecycle rules, and explicitly deferred scope. All
specifications, plans, tickets, tests, interfaces, and code MUST use that
language and preserve those rules. ADRs under `docs/adr/` are authoritative for
accepted architecture, lasting design decisions, and their rationale. Work MUST
read the ADRs relevant to the affected area before planning or implementation.
Any conflict between `CONTEXT.md`, an ADR, or proposed behavior MUST be surfaced
and resolved in the appropriate source; work MUST NOT silently override either
record. This keeps product language and engineering decisions stable across
long-running asset-lifecycle work.

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

Brownfield baseline specifications are living documents only while their status
is `Draft`. Each baseline requirement MUST cite stakeholder-confirmed intent or
evidence and MUST distinguish behavior verified by tests from behavior observed
only in implementation. Code and tests are evidence of behavior; neither is
product intent without confirmation from `CONTEXT.md`, an ADR, or an explicit
stakeholder decision. Unconfirmed behavior MUST remain an unresolved finding and
MUST NOT be silently promoted to a requirement.

After a baseline is accepted, its requirement and acceptance content is an
immutable flow-forward record. Later substantive changes MUST use a new feature
directory and MUST record bidirectional `Extends`, `Supersedes`, or `Superseded
by` links. An accepted specification may be edited only to add or correct this
non-semantic lineage metadata; requirement changes always require a new feature
directory.

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
- Accepted baseline and completed feature directories are historical records.
  Their requirement content MUST NOT be rewritten to describe later behavior.
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
2. For a brownfield baseline, classify every candidate requirement as
   stakeholder-confirmed, test-verified, implementation-only, unresolved, or
   deferred. Keep the specification in `Draft` until conflicts are resolved and
   the accepted intent is reviewed.
3. Run specification, clarification, planning, requirements-checklist, task, and
   analysis phases as appropriate. A documentation-only baseline MAY stop after
   specification, clarification, checklist review, and acceptance when no
   delivery work remains. No implementation starts while a constitution
   violation, unresolved critical clarification, or incomplete required
   checklist remains.
4. Before changing an accepted baseline or completed feature, create a new
   feature directory and add reciprocal lineage links to the prior record.
5. Convert the reviewed task graph into local tracer-bullet issues with
   `to-tickets`; review their granularity and blocking edges before execution.
6. Implement one unblocked ticket at a time using test-first development. Update
   the ticket with evidence and status without rewriting unrelated feature
   history.
7. For backend changes, run the relevant Django tests and normally the complete
   `python manage.py test` suite from `backend/`. For frontend changes, run
   `npm run lint` and `npm run build` from `frontend/`, plus feature tests when a
   test harness applies.
8. Review completion against the constitution, `spec.md`, the plan, acceptance
   criteria, permissions, lifecycle invariants, and observable end-to-end
   behavior.

## Governance

This constitution governs the ITAMS specification and delivery process.
`CONTEXT.md` remains authoritative for domain terminology, shared lifecycle
rules, and deferred scope; ADRs remain authoritative for accepted architecture,
lasting design decisions, and rationale; and the active feature `spec.md`
remains authoritative for feature intent. When these sources conflict, work
MUST stop and the conflict MUST be resolved in the appropriate source before
implementation continues.

Amendments require an explicit rationale, review of affected templates and
runtime guidance, and a migration note for active features. Constitution
versions follow semantic versioning: MAJOR for incompatible governance changes,
MINOR for added or materially expanded principles, and PATCH for
non-semantic clarification. Every plan and final review MUST include a
constitution-compliance check. Unjustified complexity or an unapproved exception
blocks implementation.

**Version**: 1.1.0 | **Ratified**: 2026-07-28 | **Last Amended**: 2026-07-29
