# Brownfield specification baseline migration for ITAMS

**Researched:** 2026-07-28  
**Scope:** Capture pre-Spec-Kit requirements safely after Spec Kit has already
been configured. No application-code migration is required.

## Recommendation

Do not try to convert the whole existing system into one giant `spec.md`, and
do not move `CONTEXT.md` or ADR content into `.specify/`.

Build an incremental, evidence-backed baseline:

1. Keep `CONTEXT.md` as the canonical domain glossary and lifecycle vocabulary.
2. Keep `docs/adr/` as the record of architectural and lasting design decisions.
3. Create a researched "compressed view" of the current codebase and tests.
4. Create a lightweight migration roadmap that divides the system into
   independently reviewable capabilities.
5. Run `$speckit-specify` once per capability to create one baseline
   `specs/<id>-<slug>/spec.md`.
6. Reconcile contradictions with a human; never turn every existing code path
   into a requirement automatically.
7. Freeze accepted baseline specs. Describe later substantive changes in new
   flow-forward feature directories that link to the earlier baseline.

This separation matches ITAMS's current governance: its constitution already
assigns terminology to `CONTEXT.md`, decisions to ADRs, and feature intent to
`spec.md`.

## Why this is the safe model

Spec Kit has no required or default artifact persistence policy. Its official
documentation defines flow-back, flow-forward, and living-spec models and says
teams should choose and record their convention. Flow-forward keeps completed
feature directories as historical records and is particularly suited to
auditability and traceability, at the cost of needing links or an index across
related specs. A living spec is useful while a baseline is being drafted, but
can lose rationale if derived artifacts are regenerated without preserving
decisions.
[Spec Persistence Models](https://github.github.com/spec-kit/concepts/spec-persistence.html)

For ITAMS, use a small hybrid:

- **During baseline capture:** the draft `spec.md` is living and may be corrected
  as evidence and stakeholder answers arrive.
- **After baseline acceptance:** freeze the directory as a flow-forward
  historical record.
- **For later product changes:** create a new feature directory and link it to
  the baseline it extends or supersedes.

The official guide for existing projects gives this same flow-forward sequence:
new substantial changes receive a new feature directory while the old directory
remains available for audit and explanation. It also distinguishes feature
artifact evolution from upgrades to Spec Kit project files.
[Evolving Specs in Existing Projects](https://github.github.com/spec-kit/guides/evolving-specs.html)

## Classify old knowledge before importing it

| Existing knowledge | Canonical destination | Treatment |
| --- | --- | --- |
| Terms, rejected synonyms, domain invariants | `CONTEXT.md` | Reference from specs; do not duplicate the whole glossary |
| Lasting architecture or design choice | `docs/adr/` | Reference from plans/spec Domain Alignment; do not recast as a user requirement |
| Verified current user-visible behavior | `specs/<id>-<slug>/spec.md` | Capture in an **As-built baseline** spec with evidence |
| Desired but unimplemented behavior | New normal feature spec | Run the full Spec Kit lifecycle when it is prioritized |
| Code behavior with no confirmed product intent | Research/inventory finding | Mark `needs-decision`; do not silently promote a possible bug to a requirement |
| Informal recollection | Clarification candidate | Record provenance and obtain stakeholder confirmation |
| Deferred behavior in `CONTEXT.md` | Roadmap entry, status `deferred` | Do not claim it in a current baseline |

This distinction matters in this repository. For example, `CONTEXT.md` says
periodic physical asset audits are deferred, while the existing `/audit` UI is
an audit-log surface. A baseline must not conflate those two meanings.

## Migration sequence

### 1. Create an evidence-only current-system research note

Use the repository's research skill first:

```text
$research Build an evidence-only current-system baseline for ITAMS.
Read CONTEXT.md, relevant docs/adr files, backend models/services/views/tests,
frontend routes/pages, and existing documentation. Separate:
1) stakeholder-stated intent,
2) behavior verified by automated tests,
3) behavior observed only in implementation,
4) contradictions,
5) unknowns, and
6) explicitly deferred behavior.
For every claim, cite repository file paths and relevant test names.
Do not modify application code and do not treat an implementation quirk as a
product requirement. Save the result as
docs/research/itams-current-system-baseline.md.
```

This follows the approach recommended by a Spec Kit maintainer for brownfield
projects: research the existing codebase into a referenced "compressed view"
rather than stuffing all code context into every feature spec.
[GitHub Spec Kit discussion #331](https://github.com/github/spec-kit/discussions/331)

Suggested first capability boundaries visible in the current ITAMS code and
tests are:

1. Authentication, roles, permissions, departments, and locations
2. Asset registry, status, condition, and terminal-state rules
3. Checkout and check-in
4. Approval-gated Transfer
5. Service Record lifecycle
6. Procurement, Vendor, and catalog master data
7. Warranty, AMC, expiry alerts, and AMC actions
8. Notifications and audit logging
9. Dashboard, reports, and exports

These are starting hypotheses, not automatically accepted specifications.

### 2. Create a shallow baseline roadmap

For a system-wide migration, use a root `ROADMAP.md` with stable IDs such as
`B1`, `B2`, and `B3`. Ask Codex:

```text
Read docs/research/itams-current-system-baseline.md and CONTEXT.md.
Create ROADMAP.md as a specification-migration roadmap only; do not change
application code. Give each independently reviewable current capability a stable
B-number, one-line intent, explicit scope boundary, dependencies, evidence
status, review status, and eventual sub-spec path. Keep future/deferred behavior
separate from the as-built baseline.
```

The official "spec of specs" guidance calls this a lightweight decomposition
pass, not a full parent spec. Each child then runs through its own Spec Kit
cycle, and the roadmap and child specs link in both directions. It recommends a
top-level `ROADMAP.md` for a large cross-cutting effort and warns that this
structure should be used only when the work is too large for one bounded spec.
[Spec of Specs](https://github.github.com/spec-kit/concepts/spec-of-specs.html)

### 3. Create one baseline feature spec at a time

Example for Checkout:

```text
$speckit-specify Create an AS-BUILT baseline specification for the current
ITAMS Checkout and check-in capability.

Parent roadmap: ROADMAP.md entry B3.
Evidence sources: CONTEXT.md; docs/research/itams-current-system-baseline.md;
backend/assets/checkout.py; checkout-related serializers, views, and tests; and
the checkout frontend pages.

Document only stakeholder-confirmed or evidence-backed current observable
behavior. Use canonical CONTEXT.md terminology. Include actors and permissions,
valid and rejected transitions, Custodian effects, notifications, failure
behavior, acceptance scenarios, explicit out-of-scope behavior, and a
"Baseline Evidence and Unresolved Conflicts" section with repository paths.
Do not propose implementation work, infer desired behavior from code alone, or
include deferred employee self-service Checkout.
```

`$speckit-specify` is intentionally one feature per invocation. It creates one
directory under `specs/`, writes `spec.md`, records the active directory in
`.specify/feature.json`, and generates a requirements-quality checklist. Its
source also requires specs to focus on user-visible **what and why**, leaving
technical design to planning.
[Current `speckit.specify` command source](https://github.com/github/spec-kit/blob/main/templates/commands/specify.md)

Then resolve only material uncertainty:

```text
$speckit-clarify Focus on conflicts between stakeholder intent, CONTEXT.md,
automated tests, and implementation. Ask only questions whose answers change
observable behavior, permissions, lifecycle rules, or acceptance tests.
```

And generate a migration-specific requirements review:

```text
$speckit-checklist Check that every baseline requirement has evidence or an
explicit stakeholder decision; conflicts are visible; permissions, state
transitions, side effects, and negative cases are covered; code quirks are not
silently promoted to product intent; and deferred behavior is not presented as
implemented.
```

Spec Kit documents `$speckit-clarify` as encoding targeted answers directly into
the active `spec.md`, while `$speckit-checklist` tests the requirements
themselves for completeness and ambiguity.
[Agentic SDD command reference](https://github.github.com/spec-kit/reference/agentic-sdd.html)

After human review, change the spec status from `Draft` to
`Baseline — accepted YYYY-MM-DD`, update the roadmap row, and commit it.

### 4. Do not generate implementation work for already-satisfied baselines

For a documentation-only as-built baseline, normally stop after:

```text
$speckit-specify ...
$speckit-clarify ...
$speckit-checklist ...
```

Do **not** run `$speckit-plan`, `$speckit-tasks`, `$to-tickets`, or
`$speckit-implement` merely to document behavior that already exists.
`$speckit-analyze` is a consistency check across `spec.md`, `plan.md`, and
`tasks.md`, so it is not the right validator when the latter two intentionally
do not exist. `$speckit-converge` is also not a reverse-engineering command: its
official contract requires a complete plan and tasks, and it may run only after
implementation has processed the current task list.
[Agentic SDD command reference](https://github.github.com/spec-kit/reference/agentic-sdd.html),
[current `speckit.converge` source](https://github.com/github/spec-kit/blob/main/templates/commands/converge.md)

If baseline review reveals a real missing behavior, split that gap into a new
future feature spec and use the normal ITAMS workflow:

```text
$speckit-specify <desired behavior and why; link the baseline spec it extends>
$speckit-clarify
$speckit-plan
$speckit-checklist
$speckit-tasks
$speckit-analyze
$to-tickets
```

The full command order is documented officially, while only `specify` is
strictly required before `plan`; clarify, checklist, and analyze are added when
the risk or ambiguity warrants them.
[Agentic SDD command reference](https://github.github.com/spec-kit/reference/agentic-sdd.html)

## Governance addition

The current constitution should explicitly record the chosen persistence rule.
After review, use:

```text
$speckit-constitution Amend ITAMS governance so draft baseline specs are living
documents until stakeholder acceptance; accepted baseline and completed feature
directories are immutable flow-forward records; substantial later changes use a
new feature directory with bidirectional Extends/Supersedes links; CONTEXT.md
remains authoritative for terminology; ADRs remain authoritative for accepted
design decisions; and code alone is evidence, not product intent.
```

The persistence choice is a team convention rather than a CLI setting, and the
official guidance recommends recording it in the constitution or onboarding
documentation.
[Spec Persistence Models](https://github.github.com/spec-kit/concepts/spec-persistence.html)

## Acceptance gate for each migrated baseline

A baseline is complete only when:

- every functional requirement has an acceptance scenario;
- every requirement has cited evidence or a recorded stakeholder decision;
- conflicts between `CONTEXT.md`, ADRs, tests, UI, and implementation are
  resolved or explicitly marked unresolved;
- deferred behavior is not represented as current;
- the capability boundary is small enough to review independently;
- `ROADMAP.md` links to the spec and the spec links back to its stable roadmap
  entry;
- no `plan.md`, `tasks.md`, or implementation ticket was created unless actual
  approved delivery work remains.
