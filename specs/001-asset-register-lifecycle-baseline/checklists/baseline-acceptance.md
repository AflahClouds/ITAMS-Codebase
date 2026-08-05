# Baseline Evidence and Acceptance Checklist: AS-BUILT Asset Register and Lifecycle Baseline

**Purpose**: Formal reviewer gate for evidence provenance, accepted intent, authorization, lifecycle integrity, side effects, deferred scope, and visible conflicts
**Created**: 2026-07-29
**Feature**: [spec.md](../spec.md)

**Note**: This checklist evaluates the completeness, clarity, consistency, and
traceability of the written baseline requirements. It does not test whether the
current implementation conforms to those requirements.

## Requirement Evidence and Provenance

- [ ] CHK001 Does every FR requirement cite `CONTEXT.md`, ADR-0001, the constitution, or a dated stakeholder clarification as its authority? [Traceability, Spec §Requirements > Functional Requirements]
- [ ] CHK002 Does every ALR requirement cite an authoritative source or dated stakeholder clarification rather than relying only on current code or tests? [Traceability, Spec §Requirements > Authorization and Lifecycle Requirements]
- [ ] CHK003 Are all stakeholder-confirmed requirements traceable to exactly one recorded clarification answer, without unstated additions to that decision? [Consistency, Spec §Clarifications]
- [ ] CHK004 Are accepted-intent acceptance scenarios explicitly distinguishable from stakeholder-confirmed, test-verified, implementation-only, and unresolved scenarios? [Clarity, Spec §User Scenarios & Testing]
- [ ] CHK005 Are test-verified behavior claims linked to specific repository test paths or named test classes so their evidence status is reviewable? [Traceability, Spec §Baseline Evidence and Unresolved Conflicts > Verified Behavior Evidence]
- [ ] CHK006 Are implementation-only observations linked to concrete backend, frontend, configuration, or migration paths without being described as accepted requirements? [Traceability, Spec §Baseline Evidence and Unresolved Conflicts > Implementation-Only Observations]
- [ ] CHK007 Are accepted Asset attributes clearly separated from additional fields and relationships observed only in the implementation? [Clarity, Spec §Requirements > Key Entities]

## Intent Classification and Requirement Consistency

- [ ] CHK008 Does the evidence-classification scheme define accepted intent, test-verified behavior, implementation-only behavior, and unresolved findings with mutually exclusive meanings? [Clarity, Spec §Domain Alignment > Evidence Classification]
- [ ] CHK009 Are code-only register behaviors such as search, filters, barcode generation, file versioning, and cascading deletion kept outside the normative FR/ALR requirement set unless a stakeholder decision accepts them? [Consistency, Spec §User Story 2; Spec §Baseline Evidence and Unresolved Conflicts]
- [ ] CHK010 Are automated tests treated as evidence of current behavior rather than product authority everywhere they are cited? [Consistency, Spec §Domain Alignment > Evidence Classification; Spec §Verified Behavior Evidence]
- [ ] CHK011 Do current-behavior tables clearly identify where observed outcomes conform to or conflict with the accepted requirements? [Clarity, Spec §Test-Verified Current Transition Behavior; Spec §Accepted Asset Permission Contract and Current Codes]
- [ ] CHK012 Are assumptions worded so they bound interpretation without silently converting implementation evidence into stakeholder intent? [Consistency, Spec §Assumptions]

## Permissions and Negative Authorization Coverage

- [ ] CHK013 Are the global-read Roles, Employee Custodian-only scope, and required `asset_view` grant stated unambiguously for register, detail, and aggregate-history access? [Completeness, Spec §ALR-009; Spec §AS-018–AS-019]
- [ ] CHK014 Are create, edit, condition-inspection, file-upload, and deletion permissions assigned consistently between ALR-010 and the accepted permission table? [Consistency, Spec §ALR-010; Spec §Accepted Asset Permission Contract and Current Codes]
- [ ] CHK015 Is the Employee denial case complete for Assets held by another User and Assets with no Custodian, including terminal Assets whose Custodian is cleared? [Coverage, Spec §NC-009; Spec §ALR-009]
- [ ] CHK016 Are negative authorization requirements explicit that denied reads disclose no out-of-scope Asset data and denied writes cause no Asset, file, condition-log, or lifecycle-history mutation? [Completeness, Spec §AS-011; Spec §ALR-002; Spec §SC-003]
- [ ] CHK017 Does the specification state that frontend control visibility is insufficient authorization and that every protected action requires enforcement at the action boundary? [Security, Spec §ALR-001]
- [ ] CHK018 Is the unresolved custom-Role policy visibly assigned to B1 without weakening the accepted named-Role behavior owned by B2? [Dependency, Spec §Assumptions; Spec §Out of Scope > Adjacent Baseline Ownership]

## Lifecycle Transition and Atomic Side-Effect Coverage

- [ ] CHK019 Are all seven canonical statuses, all five canonical conditions, their independence, and the rejected `Scrapped` condition documented consistently? [Completeness, Spec §Domain Alignment; Spec §FR-002–FR-004]
- [ ] CHK020 Is initial Asset state limited unambiguously to `Available` or `In Storage` with empty Custodian and department, with all rejected creation combinations stated? [Clarity, Spec §FR-013; Spec §AS-014; Spec §NC-007]
- [ ] CHK021 Are `Assigned` and `Under Repair` explicitly owned by Checkout/Transfer and Service Record operations, with direct entry and nonterminal exit rejection requirements? [Coverage, Spec §FR-012; Spec §ALR-004–ALR-005; Spec §NC-002]
- [ ] CHK022 Are Service Record status, Custodian, department-clearing, and no-auto-restoration requirements consistent with ADR-0001 and the accepted scenarios? [Consistency, Spec §FR-007; Spec §AS-006; Spec §Accepted Lifecycle Boundary]
- [ ] CHK023 Are `Sold` and `Scrapped` source states distinguished from the broader reactive `Lost` source-state rule without an ambiguous catch-all terminal transition? [Clarity, Spec §FR-014; Spec §AS-007–AS-008]
- [ ] CHK024 Are Custodian and department effects specified for Checkout, Transfer, check-in, Service Record, `Sold`, `Scrapped`, and `Lost`, including the `Lost` accountability exception? [Completeness, Spec §FR-006; Spec §FR-009; Spec §FR-015; Spec §Accepted Lifecycle Boundary]
- [ ] CHK025 Does the terminal-transition requirement define one atomic outcome covering Asset status, Custodian, department, open Checkout, open Service Record, and every Pending Transfer? [Atomicity, Spec §AS-017; Spec §ALR-003; Spec §ALR-006]
- [ ] CHK026 Are rejected `Sold` or `Scrapped` transitions from `Assigned` or `Under Repair` required to leave the Asset and all active lifecycle records unchanged? [Exception Flow, Spec §AS-016; Spec §ALR-008; Spec §NC-008]
- [ ] CHK027 Are terminal irreversibility and reactive `Lost` accountability covered by measurable positive and negative acceptance scenarios? [Acceptance Criteria, Spec §AS-008–AS-009; Spec §SC-002; Spec §SC-004]

## Audit, Notification, and Failure Requirements

- [ ] CHK028 Does the specification enumerate every successful B2 mutation type that requires an AuditLog record, including Asset, condition-inspection, image, and document mutations? [Completeness, Spec §AS-021; Spec §Accepted Asset Audit and Notification Effects]
- [ ] CHK029 Are the additional terminal AuditLog contents explicit for operator, old/new status, Custodian, department, and every automatically closed or rejected lifecycle record? [Clarity, Spec §AS-022; Spec §ALR-011]
- [ ] CHK030 Is the no-Notification rule explicit for every B2 mutation and terminal side effect while preserving sibling ownership of explicit Checkout, Transfer, and Service Record notifications? [Consistency, Spec §ALR-011; Spec §Accepted Asset Audit and Notification Effects]
- [ ] CHK031 Are invalid canonical values, forbidden lifecycle transitions, terminal reversals, unauthorized access, invalid condition inspections, and invalid file submissions classified as accepted, governance, implementation-only, or unresolved failure requirements? [Coverage, Spec §Negative Cases; Spec §Current Validation and Failure Behavior]
- [ ] CHK032 Do all accepted rejection requirements state the required no-mutation outcome for Asset, Custodian, department, files, and related lifecycle records? [Completeness, Spec §AS-010–AS-013; Spec §ALR-002; Spec §ALR-008]
- [ ] CHK033 Is the boundary between B2 trigger requirements and B8 AuditLog storage, access, filtering, and retention requirements explicit and non-overlapping? [Dependency, Spec §Accepted Asset Audit and Notification Effects; Spec §Out of Scope]

## Deferred Scope and Adjacent Baseline Boundaries

- [ ] CHK034 Are periodic physical Asset audits described only as deferred future behavior and kept distinct from reactive `Lost`, operational AuditLog, and the current “Asset Audit Report”? [Scope, Spec §Out of Scope > Explicitly Deferred Product Behavior]
- [ ] CHK035 Are employee self-service Checkout and employee/team-lead Procurement requests described only as deferred possibilities rather than current B2 behavior? [Scope, Spec §Out of Scope > Explicitly Deferred Product Behavior]
- [ ] CHK036 Are B1 and B3–B9 responsibilities excluded precisely enough that this baseline does not claim their workflows, shared facilities, reports, or master-data behavior as implemented B2 requirements? [Dependency, Spec §Out of Scope > Adjacent Baseline Ownership]

## Contradictions, Unresolved Decisions, and Acceptance Readiness

- [ ] CHK037 Does every resolved clarification that conflicts with current behavior remain visible as an implementation conformance gap with repository evidence? [Conflict, Spec §Baseline Evidence and Unresolved Conflicts > Unresolved Conflicts 1, 3, 4, 5, 9]
- [ ] CHK038 Is the canonical `Checkout` versus user-visible `Assignment` contradiction visible without presenting `Assignment` as an accepted synonym? [Conflict, Spec §FR-004; Spec §Unresolved Conflicts 2]
- [ ] CHK039 Are the unresolved Asset identity contract, deletion/history retention, file security/lifecycle, and frontend failure/accessibility decisions visible and excluded from accepted requirements? [Gap, Spec §Unresolved Conflicts 6–8, 10]
- [ ] CHK040 Does the Draft acceptance gate identify all remaining stakeholder decisions and conformance gaps that must be resolved before acceptance, without implying readiness for implementation planning? [Acceptance Readiness, Spec §SC-006; Spec §Delivery Boundary]

## Notes

- Check items off as the written requirements are reviewed: `[x]`.
- Record findings inline or link to the relevant clarification decision.
- A checked item means the specification is complete and unambiguous for that
  requirement-quality concern; it does not mean current code conforms.
