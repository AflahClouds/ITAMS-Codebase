# B6 Brownfield Baseline Acceptance Checklist: Procurement, Vendor, and Catalog Masters

**Purpose**: Formal requirements-quality and evidence gate for accepting the B6
AS-BUILT brownfield baseline without treating implementation-only behavior as
product intent.

**Created**: 2026-08-04

**Feature**: [B6 specification](../spec.md)

**Audience / Timing**: Stakeholder and specification-maintainer review while the
baseline remains `Draft`, immediately before an acceptance decision.

**Note**: This checklist evaluates the specification as "unit tests for
English." It does not test the application or assert implementation conformance.

## Baseline Authority and Evidence Discipline

- [ ] CHK001 Is the baseline's `Draft` status, evidence date, B6 roadmap link,
  lineage, and post-acceptance immutability rule complete and mutually
  consistent? [Completeness, Consistency, Spec §Specification Lineage;
  Constitution §III]
- [ ] CHK002 Does the Domain Alignment section consistently use the canonical
  meanings of Procurement, Vendor, Asset, Category, Brand, Model, Purchase Mode,
  and Asset arrival record from the authoritative domain sources? [Consistency,
  Spec §Domain Alignment; `CONTEXT.md`]
- [ ] CHK003 Are stakeholder-confirmed, governance-backed, test-backed,
  implementation-only, unresolved, and deferred statements visibly and
  unambiguously distinguished throughout the baseline? [Clarity, Traceability,
  Spec §Evidence Classification; Constitution §III]
- [ ] CHK004 Are implementation observations and code paths confined to evidence
  sections or explicitly labeled observations, without being expressed as
  accepted `MUST` requirements or success criteria? [Consistency, Spec
  §Implementation-Only Observations; SC-005]
- [ ] CHK005 Is every test-backed requirement limited to the behavior actually
  supported by its cited test evidence, with broader relationships or policies
  left stakeholder-confirmed, implementation-only, or unresolved? [Evidence
  Quality, Spec §Verified Behavior Evidence; FR-006–FR-008]
- [ ] CHK006 Are all dated clarification decisions reflected consistently in
  requirements, scenarios, success criteria, assumptions, and Accepted Intent,
  while the remaining concurrent-linking issue is still explicitly classified?
  [Traceability, Consistency, Spec §Clarifications; §Unresolved Conflicts]

## Procurement Requirement Evidence

- [ ] CHK007 Is the completed-purchase meaning—and the absence of request,
  approval, pending-purchase, and delivery-tracking states—supported by
  authoritative domain intent rather than current implementation shape?
  [Evidence Quality, Spec §FR-001; Accepted Intent; `CONTEXT.md` Procurement]
- [ ] CHK008 Is the IT-only actor boundary and deferral of Employee- and
  team-lead-initiated purchase requests supported by domain intent, the B1
  boundary, and explicit stakeholder direction? [Completeness, Traceability,
  Spec §FR-002; §Explicitly Deferred Product Behavior]
- [ ] CHK009 Are the managed Vendor, invoice, and PO requirements traceable to
  the first-class Vendor decision and completed-Procurement domain definition,
  without importing Service Record lifecycle behavior into B6? [Consistency,
  Spec §FR-003–FR-004; ADR-0001; Accepted Intent]
- [ ] CHK010 Is the physical-arrival precondition fully specified as both an
  Asset arrival record containing date and Location and an attestation retaining
  actor and time? [Completeness, Clarity, Spec §FR-009; AS-001; NC-004; SC-007]
- [ ] CHK011 Are required purchase and invoice dates, all nonfuture constraints,
  purchase-before-or-equal ordering, and the absence of invoice-versus-arrival
  ordering stated without contradiction? [Clarity, Consistency, Spec §FR-010;
  AS-010; NC-005; SC-008]
- [ ] CHK012 Is archive-only Procurement defined clearly enough to exclude hard
  deletion, retain purchase details and history, and avoid implicit Asset
  attachment or detachment? [Completeness, Spec §FR-011; NC-006; SC-009]
- [ ] CHK013 Are reasoned attachment/detachment history, one-or-more Assets per
  Procurement, at-most-one Procurement per Asset, temporary `In Storage`
  staging, and legacy/import exceptions fully specified together? [Coverage,
  Consistency, Spec §FR-012–FR-014; AS-011–AS-012; NC-007; SC-009–SC-010]
- [ ] CHK014 Does the B6 permission contract enumerate every read and mutation
  class, including create, initial and later attestation, edit, attachment,
  detachment, archive, master write, and Employee exclusion? [Completeness,
  Spec §FR-015–FR-016; ALR-001–ALR-002; ALR-008]
- [ ] CHK015 Are invoice and PO identity rules complete for requiredness,
  uniqueness scope, whitespace handling, case-insensitive comparison, and
  preserved display text? [Clarity, Spec §FR-017; AS-015; NC-009; SC-012]
- [ ] CHK016 Are Procurement-owned invoice and PO file rules complete for
  requiredness, optional-PO behavior, single storage, linked-Asset exposure, and
  version retention? [Completeness, Spec §FR-018; AS-016; NC-010; SC-013]
- [ ] CHK017 Are required B6 audit events and excluded validation failures
  enumerated precisely enough to distinguish accepted event selection from B8
  storage and retention behavior? [Clarity, Boundary, Spec §FR-023; ALR-009;
  SC-016]
- [ ] CHK018 Are IT Manager Notification triggers exhaustive for the accepted
  high-impact events and explicit about routine actions that must not trigger a
  B6 Notification? [Completeness, Spec §FR-024; AS-019; NC-013; SC-016]
- [ ] CHK019 Are the Asset-lifecycle non-effects and atomic failure requirements
  complete for arrival validation, attachment, detachment, reassignment,
  archival, history, and cardinality preservation? [Recovery Coverage, Spec
  §ALR-004–ALR-007]
- [ ] CHK020 Is the audit transaction boundary unambiguous that required audit
  retention is atomic with a successful B6 mutation while Notification delivery
  remains a B8 concern? [Clarity, Consistency, Spec §ALR-009; FR-023–FR-024]

## Vendor and Catalog-Master Requirement Evidence

- [ ] CHK021 Is Vendor consistently specified as one first-class managed identity
  shared by Procurement and Service Record for reliable grouping, rather than
  as free text or duplicated per capability? [Consistency, Spec §FR-003; Key
  Entities §Vendor; SC-003; `CONTEXT.md` Vendor; ADR-0001]
- [ ] CHK022 Does master-maintenance scope explicitly cover create, view, rename,
  merge, update, and delete for all five B6 master types under the accepted
  authorization and deletion rules? [Completeness, Spec §FR-005; FR-016]
- [ ] CHK023 Does the referenced-deletion requirement match the exact tested
  Category-, Brand-, Model-, Purchase Mode-, and Vendor-reference relationships
  without generalizing beyond the cited evidence? [Evidence Quality, Spec
  §FR-006; AS-006; NC-001; Verified Behavior Evidence]
- [ ] CHK024 Is the required protected-deletion outcome—preserved operational
  records plus a stable in-use explanation—supported by the cited direct and
  supported-interface evidence? [Traceability, Spec §FR-007; AS-007; ALR-003]
- [ ] CHK025 Is unused-master deletion specified for every B6 master type and
  supported by evidence that is clearly separate from referenced-deletion
  behavior? [Completeness, Evidence Quality, Spec §FR-008; AS-008; NC-002]
- [ ] CHK026 Are global and Brand-scoped master identities, nonblank names,
  whitespace normalization, case comparison, display preservation, and optional
  non-identifying Vendor contacts stated precisely? [Clarity, Spec §FR-019;
  AS-017; NC-011; SC-014]
- [ ] CHK027 Are Model ownership by exactly one Brand, Brand deletion protection,
  and the absence of a direct Model–Category relationship consistent across the
  requirement and entity definitions? [Consistency, Spec §FR-020; Key Entities
  §Category–Model]
- [ ] CHK028 Are rename and controlled-merge requirements complete for stable
  identity, atomic reference movement, survivor selection, source
  non-selectability, retained provenance, and failure rollback? [Recovery
  Coverage, Spec §FR-021; AS-017; NC-011; SC-014]
- [ ] CHK029 Is legacy Vendor backfill complete for original-text provenance,
  unambiguous matching, review flags, historical readability, new-use blocking,
  authorized resolution, and retained review history? [Completeness, Spec
  §FR-022; AS-018; NC-012; SC-015]

## Cross-Section Consistency and Scope Boundaries

- [ ] CHK030 Are physical-arrival requirements identical across Domain Alignment,
  FR-009, the acceptance and negative scenarios, the Asset Arrival Record entity,
  and SC-007? [Consistency, Spec §Domain Alignment; FR-009; AS-001; NC-004;
  SC-007]
- [ ] CHK031 Are date requiredness and ordering identical across the clarification
  record, FR-010, AS-010, NC-005, SC-008, and Accepted Intent? [Consistency,
  Spec §Clarifications 2026-08-03; FR-010; SC-008]
- [ ] CHK032 Are frontend route/control visibility and backend enforcement
  required to use the same `asset_view`, `asset_create`, `asset_edit`,
  `asset_delete`, and `settings_access` mappings for every corresponding B6
  surface? [Consistency, Security Coverage, Spec §FR-015–FR-016; AS-013–AS-014;
  NC-003; ALR-001–ALR-003; ALR-008; SC-011]
- [ ] CHK033 Has the stale statement that document-file expectations "remain
  unresolved" been reconciled with the accepted Procurement-document contract?
  [Conflict, Spec §Domain Alignment; FR-018; Accepted Intent]
- [ ] CHK034 Are direct protected deletion and controlled merge distinguished so
  that merge cannot be misread as bypassing reference protection or erasing
  provenance? [Clarity, Consistency, Spec §FR-006–FR-008; FR-020–FR-021]
- [ ] CHK035 Are Employee/team-lead requests, approval, budgeting, ordering,
  delivery tracking, and pending Procurement states consistently deferred and
  absent from all accepted B6 lifecycle requirements? [Scope, Consistency, Spec
  §FR-001–FR-002; §Explicitly Deferred Product Behavior; SC-001]
- [ ] CHK036 Are the B2 Asset-lifecycle and Asset-file boundary, B5 Service Record
  boundary, B8 audit/Notification infrastructure boundary, and B6 shared-Vendor
  and Procurement-document ownership stated without overlap or contradiction?
  [Dependency, Consistency, Spec §Assumptions; §Adjacent Baseline Ownership]

## Acceptance-Criteria Quality and Readiness

- [ ] CHK037 Can every FR-001–FR-024 and ALR-001–ALR-009 requirement be traced to
  at least one accepted scenario, negative case, measurable outcome, or explicit
  evidence-based acceptance rationale? [Traceability, Coverage, Spec §User
  Scenarios & Testing; §Success Criteria]
- [ ] CHK038 Are the populations and review bases behind phrases such as "review
  set," "complete permission-matrix review," "complete B6 event-matrix review,"
  and "visibly flagged" defined well enough for objective acceptance? [Ambiguity,
  Measurability, Spec §SC-001; SC-010–SC-011; SC-015–SC-016]
- [ ] CHK039 Is concurrent Asset linking explicitly dispositioned for acceptance
  as a carried-forward planning detail, including conflict presentation, retry,
  and stale-edit behavior, as required by SC-006? [Unresolved, Acceptance Gate,
  Spec §Unresolved Conflicts; SC-006]
- [ ] CHK040 Does the final acceptance record identify the stakeholder decision,
  acceptance date, reviewed evidence date, unresolved items deliberately carried
  forward, and the point after which semantic changes require a new linked
  feature directory? [Gap, Governance, Spec §Specification Lineage;
  Constitution §III]

## Notes

- All checklist items are mandatory for formal baseline acceptance unless the
  acceptance record explicitly documents a justified carry-forward disposition.
- Mark completed items with `[x]` and add findings or evidence links inline.
- This feature currently has no `plan.md`; the constitution permits a
  documentation-only baseline to stop after specification, clarification,
  checklist review, and acceptance when no delivery work remains.
