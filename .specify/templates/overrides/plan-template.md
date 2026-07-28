# Implementation Plan: [FEATURE]

**Feature Directory**: `specs/[###-feature-name]/`  
**Date**: [DATE]  
**Spec**: [link]

**Input**: Feature specification from `specs/[###-feature-name]/spec.md`

**Note**: This template is filled by `$speckit-plan`.

## Summary

[Extract the primary requirement and the chosen technical approach.]

## Technical Context

**Backend**: Python, Django, and Django REST Framework versions already pinned in
`backend/requirements.txt`, or a justified change

**Frontend**: React, Vite, Material UI, and existing dependencies pinned in
`frontend/package.json`, or a justified change

**Storage**: [Existing Django models/database, files, or N/A]

**Testing**: Django test runner and the highest practical feature seam; frontend
test harness when applicable

**Target Platform**: Browser client and Django web service

**Performance Goals**: [Measurable user-facing targets or NEEDS CLARIFICATION]

**Constraints**: [Lifecycle, authorization, privacy, audit, notification, or
operational constraints]

**Scale/Scope**: [Expected records, users, screens, endpoints, and migration
impact]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Domain and decisions**: List affected terms from `CONTEXT.md`, relevant ADRs,
  and any conflict requiring an ADR amendment.
- **Lifecycle and authorization**: Identify affected actors, permissions, state
  transitions, transaction boundaries, audit events, and notifications.
- **Traceability**: Map the proposed design to requirement and acceptance
  scenario identifiers in `spec.md`.
- **Test-first delivery**: Name the highest practical test seam for each behavior
  slice and place tests before implementation.
- **Local execution**: Keep `tasks.md` as planning input and publish approved
  implementation slices as separate files under the feature's `issues/`
  directory.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
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

**Structure Decision**: [Identify the existing backend apps and frontend areas
touched by this feature. Justify any new top-level module or architectural seam.]

## Phase 0: Research

[Resolve every NEEDS CLARIFICATION item. Record each decision, its rationale,
and alternatives considered in `research.md`.]

## Phase 1: Design and Contracts

[Describe the data model, state transitions, permissions, API/UI contracts,
transaction boundaries, audit or notification effects, and end-to-end validation
scenario. Produce `data-model.md`, `contracts/`, and `quickstart.md` as needed.]

## Test Strategy

[For each user-story slice, identify the failing test written first, its seam,
the observable behavior it proves, and the validation commands.]

## Complexity Tracking

> Fill only when a Constitution Check violation requires explicit justification.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --- | --- | --- |
| [Violation] | [Specific need] | [Reason the simpler design is insufficient] |
