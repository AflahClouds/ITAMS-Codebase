# Specification Quality Checklist: AS-BUILT Service Record Lifecycle Baseline

**Purpose**: Validate specification completeness and quality before stakeholder clarification
**Created**: 2026-08-05
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation choices are presented as accepted product intent
- [x] Requirements focus on repair accountability and user-visible outcomes
- [x] The baseline is readable by non-technical stakeholders
- [x] All mandatory template sections are completed
- [x] Canonical Service Record, Vendor, Custodian, `Under Repair`, Checkout, Notification, and AuditLog terms are used consistently

## Requirement Completeness

- [x] No `[NEEDS CLARIFICATION]` markers remain
- [x] Accepted requirements are testable and unambiguous
- [x] Test-backed and implementation-only observations are visibly classified
- [x] Success criteria are measurable and technology-agnostic
- [x] Primary opening, closing, integrity, content, accountability, and read scenarios are defined
- [x] `asset_custody_manage`, named actors, custom Roles, and B1 read visibility are explicit
- [x] Eligible and rejected Asset states, Custodian clearing, and `Under Repair` ownership are explicit
- [x] Interrupted Checkout closure and terminal auto-closure boundaries are explicit
- [x] Dates, cost, remarks, and outcome content is explicit and separated from what is unresolved
- [x] Return to `Available` without Custodian restoration is explicit and traced to ADR-0001
- [x] Notification and AuditLog trigger ownership is explicit and bounded against B8
- [x] Scope and B1/B2/B3/B4/B6/B7/B8/B9 dependencies are clearly bounded

## Brownfield Evidence Integrity

- [x] Code and tests are treated as evidence rather than product intent
- [x] All 9 selected B5 tests and 7 adjacent boundary tests were run on 2026-08-05 and are cited
- [x] Accepted B2 is cited as accepted; B1, B3, B6, and B8 are cited as Draft dependencies
- [x] Current `In Storage` eligibility and closure-status behavior is not accepted while U-001 is open
- [x] Current department retention is recorded as a conformance gap while U-002 is open
- [x] Current absent bill/document/outcome representation is not accepted while U-003 is open
- [x] Current audit coverage is not accepted while U-004 is open
- [x] AuditLog is not confused with physical Asset auditing
- [x] SMTP-labelled Settings are not treated as proof of email delivery
- [x] No application code was modified

## Feature Readiness

- [x] Functional requirements have corresponding scenarios, matrices, or measurable outcomes
- [x] User scenarios cover every primary Service Record journey
- [x] Four mandated unresolved decisions are separately identified as U-001 through U-004
- [x] Conformance gaps are recorded in U-005 rather than reconciled by weakening a requirement
- [x] Automatic Checkout after service is excluded rather than left ambiguous
- [x] The Draft is suitable for targeted stakeholder clarification

## Notes

- Validation iteration 1 (2026-08-05, specification) passed 28 of 33 items. The
  five unchecked items were the four mandated open decisions and their
  identification, not missing content.
- Validation iteration 2 (2026-08-05, after clarification) passes all 33 items.
  The clarification session resolved U-001 through U-004, so the five items that
  were blocked on them now pass. Their wording still describes the decisions as
  open because it records the state each item was validated against; the
  decisions themselves are recorded as RESOLVED in the spec.
- Repository paths appear only where brownfield traceability requires them;
  accepted requirements are expressed as business and lifecycle outcomes.
- U-002 was constrained rather than open-ended: accepted B2 FR-007 and FR-015
  already required the department to be cleared. The stakeholder confirmed that
  rule, so no B2 amendment is required.
- The B5 Notification and Audit Trigger Matrix is now accepted content under
  Draft B8 FR-018. Only the previous-Custodian Notification on opening is
  test-backed; every other row is stakeholder-confirmed with the current gap
  recorded beside it.
- Condition-history evidence for a repair, Employee visibility of a
  subject-less record, and production delivery of the new overdue notification
  remain evidence-led confirmation items. None is an acceptance blocker.
- The selected evidence runs passed 9 B5 tests and 7 adjacent boundary tests on
  2026-08-05.
