# Specification Quality Checklist: AS-BUILT Dashboard, Reports, and Exports Baseline

**Purpose**: Validate specification completeness and quality before stakeholder clarification
**Created**: 2026-08-05
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation choices are presented as accepted product intent
- [x] Requirements focus on reader-facing outcomes rather than presentation mechanics
- [x] The baseline is readable by non-technical stakeholders
- [x] All mandatory template sections are completed
- [x] Canonical Dashboard, report, export, AuditLog, Audit Trail, and physical-audit terms are used consistently

## Requirement Completeness

- [x] No `[NEEDS CLARIFICATION]` markers remain
- [x] Accepted requirements are testable and unambiguous
- [x] Test-backed and implementation-only observations are visibly classified
- [x] Success criteria are measurable and technology-agnostic
- [x] KPI, chart, catalog, column, access, and Lost-reporting baseline scenarios are defined; prospective filtering, export, and branding scenarios are visibly classified and linked to CHG-B9-01
- [x] The current report catalog, its row selection, and its columns are recorded as a reviewable table
- [x] `report_access`, Admin-only Audit Trail, and the permission-free Dashboard are explicit
- [x] The absence of any report filter or parameter is stated rather than implied
- [x] Scope and B1–B8 dependencies are clearly bounded

## Brownfield Evidence Integrity

- [x] Code and the single test are treated as evidence rather than product intent
- [x] The one existing reporting test was run on 2026-08-05 and is cited
- [x] The absence of automated coverage for every other B9 behavior is stated explicitly
- [x] Draft B2 is cited as Draft; B1 and B3–B8 are cited as Draft dependencies
- [x] The implementation-led (E3) evidence status is stated up front rather than implied
- [x] Current metric and column definitions are evidence-qualified; prospective definitions are owned by CHG-B9-01
- [x] Current global visibility is evidence-qualified against the resolved U-002 decision
- [x] Current export divergence is evidence-qualified; prospective parity is owned by CHG-B9-01
- [x] Current branding behavior is evidence-qualified; prospective branding is owned by CHG-B9-01
- [x] Current unpaginated and silently truncated behavior is evidence-qualified; prospective volume handling is owned by CHG-B9-01
- [x] The current "Asset Audit Report" title and access are evidence-qualified against the resolved U-006 decision
- [x] AuditLog and Audit Trail are not confused with physical Asset auditing
- [x] No application code was modified

## Feature Readiness

- [x] Functional requirements have corresponding scenarios, tables, or measurable outcomes
- [x] User scenarios cover Dashboard, catalog, access, Lost reporting, export, and branding
- [x] Six mandated unresolved decisions are separately identified as U-001 through U-006
- [x] Conformance gaps are recorded in U-007 rather than reconciled by weakening a requirement
- [x] Periodic physical Asset auditing and B2–B7 lifecycle rules are excluded rather than left ambiguous
- [x] The dependency on every source baseline being accepted first is stated as a gate
- [x] The Draft is suitable for targeted stakeholder clarification

## Notes

- Validation iteration 1 (2026-08-05, specification) passed 27 of 34 items. The
  seven unchecked items were the six mandated open decisions and their
  identification, not missing content.
- Validation iteration 2 (2026-08-05, after clarification) passes all 34 items.
  The clarification session resolved U-001 through U-006, so the seven items
  that were blocked on them now pass.
- The prospective per-figure definitions, standard filters, export parity,
  branding, and volume target are not B9 acceptance preconditions. They are
  normative only in
  [`012-report-filter-export-parity-change`](../../012-report-filter-export-parity-change/spec.md).
- B9 is the roadmap's only `E3 — implementation-led` capability. Its Draft
  records current-system evidence without converting clarified prospective
  behavior into AS-BUILT requirements.
- The only authoritative product statement about any report remains
  `CONTEXT.md`'s Vendor entry. Every other accepted requirement traces to a
  dependency baseline or to the 2026-08-05 clarification.
- FR-015 also gates acceptance on every source baseline being accepted first,
  matching the drafting order in `ROADMAP.md`.
- U-006 was shared with Draft B8 and is now resolved consistently with B8
  FR-016: the AuditLog projection is retitled and restricted to Admin and IT
  Manager, and the "Asset Audit" name is reserved for the deferred F1
  physical-verification capability.
- U-001 is resolved for baseline classification through FR-017 and FR-018.
  Producing future written definitions and standard filters is delivery scope
  owned by CHG-B9-01.
- The selected evidence run passed 1 reporting test on 2026-08-05.
