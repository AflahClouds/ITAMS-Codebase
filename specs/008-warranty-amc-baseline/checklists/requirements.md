# Specification Quality Checklist: AS-BUILT Warranty, AMC, and Expiry Actions Baseline

**Purpose**: Validate specification completeness and quality before stakeholder clarification
**Created**: 2026-08-05
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation choices are presented as accepted product intent
- [x] Requirements focus on coverage accountability and user-visible outcomes
- [x] The baseline is readable by non-technical stakeholders
- [x] All mandatory template sections are completed
- [x] Canonical Warranty, AMC, Incomplete/Active/Ended, Vendor, Notification, and AuditLog terms are used consistently

## Requirement Completeness

- [x] No `[NEEDS CLARIFICATION]` markers remain
- [x] Accepted requirements are testable and unambiguous
- [x] Test-backed and implementation-only observations are visibly classified
- [x] Success criteria are measurable and technology-agnostic
- [x] Warranty/AMC distinction, contract states, renewal, End Support, and alert scenarios are defined
- [x] `asset_edit`, `asset_view`, named actors, and B1 visibility are explicit
- [x] Reasons, date validation, and history preservation are explicit
- [x] 30/15/7-day triggers, recipients, and IT Manager notification are explicit
- [x] Notification and AuditLog trigger ownership is explicit and bounded against B8
- [x] Scope and B1/B2/B5/B6/B8/B9 dependencies are clearly bounded

## Brownfield Evidence Integrity

- [x] Code, migrations, and tests are treated as evidence rather than product intent
- [x] All 18 selected B7 tests were run on 2026-08-05 and are cited
- [x] Accepted B2 is cited as accepted; B1, B5, B6, and B8 are cited as Draft dependencies
- [x] Runserver-only scheduling is explicitly not presented as reliable production delivery
- [x] Current computed AMC flag semantics are not accepted while U-001 (C4) is open
- [x] Current scheduling and delivery behavior is not accepted while U-002 (C5) is open
- [x] Current absence of initial-entry validation is not accepted while U-003 is open
- [x] Current absence of AMC Vendor capture is not accepted while U-004 is open
- [x] Current in-app-only delivery is not accepted as satisfying "proactively pushed" while U-005 is open
- [x] AuditLog is not confused with physical Asset auditing
- [x] SMTP-labelled Settings are not treated as proof of email delivery
- [x] No application code was modified

## Feature Readiness

- [x] Functional requirements have corresponding scenarios, matrices, or measurable outcomes
- [x] User scenarios cover every primary Warranty and AMC journey
- [x] Five mandated unresolved decisions are separately identified as U-001 through U-005
- [x] Conformance gaps are recorded in U-006 rather than reconciled by weakening a requirement
- [x] Warranty renewal, claims, and automatic contract changes are excluded rather than left ambiguous
- [x] The Draft is suitable for targeted stakeholder clarification

## Notes

- Validation iteration 1 (2026-08-05, specification) passed 27 of 33 items. The
  six unchecked items were the five mandated open decisions and their
  identification, not missing content.
- Validation iteration 2 (2026-08-05, after clarification) passes all 33 items.
  The clarification session resolved U-001 through U-005, so the six items that
  were blocked on them now pass. Their wording still describes the decisions as
  open because it records the state each item was validated against; the
  decisions themselves are recorded as RESOLVED in the spec.
- Two acceptance preconditions remain and are tracked in FR-028, not as
  unchecked checklist items: the `CONTEXT.md` reconciliation required by FR-029,
  and reviewer confirmation of the derived requirement FR-020.
- Repository paths appear only where brownfield traceability requires them;
  accepted requirements are expressed as business and coverage outcomes.
- `CONTEXT.md` is unusually detailed for this capability and is the only
  authoritative product source; no ADR governs B7. Most accepted requirements
  derive from the **Warranty** and **AMC** glossary entries directly.
- U-001 was resolved in a way that narrows `CONTEXT.md`: the AMC flag is derived
  from the current contract and no deliberate-no-AMC decision is recorded. Per
  constitution Principle I that divergence is surfaced in FR-029 as an
  acceptance precondition rather than absorbed silently.
- U-002 was resolved by keeping scheduling in-process but requiring it to run
  under the real production server with cross-worker mutual exclusion, a
  configured timezone, once-only alert recording, and catch-up after downtime.
  Nothing in this Draft treats the current development-server-only arrangement
  as satisfying FR-017.
- The B7 Notification and Audit Trigger Matrix is accepted content under Draft
  B8 FR-018. Threshold rows and both AMC decision notifications are test-backed;
  recipient selection by Role display name, destinations, and audit content are
  recorded as conformance gaps.
- Chasing an `Incomplete` AMC, alert message specificity, AMC history retention
  on Asset deletion, a Service Record-to-contract link, and confirmation of the
  derived FR-020 remain evidence-led confirmation items.
- The selected evidence run passed 18 B7 tests on 2026-08-05.
