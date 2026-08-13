# Baseline Evidence and Acceptance Checklist: AS-BUILT Asset Register and Lifecycle Baseline

**Purpose**: Formal reviewer gate for evidence provenance, accepted intent, authorization, lifecycle integrity, side effects, deferred scope, and visible conflicts
**Created**: 2026-07-29
**Executed**: 2026-08-12 — 37 of 40 pass; 3 blockers recorded, all resolved the same day (see §Blocking Findings)
**Re-run**: 2026-08-12 — CHK013, CHK014, CHK018 re-executed against B1's amended FR-010/FR-011; all three still pass (see §Dependency Re-run)
**Feature**: [spec.md](../spec.md)

**Note**: This checklist evaluates the completeness, clarity, consistency, and
traceability of the written baseline requirements. It does not test whether the
current implementation conforms to those requirements.

## Requirement Evidence and Provenance

- [x] CHK001 Does every FR requirement cite `CONTEXT.md`, ADR-0001, the constitution, or a dated stakeholder clarification as its authority? [Traceability, Spec §Requirements > Functional Requirements]
- [x] CHK002 Does every ALR requirement cite an authoritative source or dated stakeholder clarification rather than relying only on current code or tests? [Traceability, Spec §Requirements > Authorization and Lifecycle Requirements]
- [x] CHK003 Are all stakeholder-confirmed requirements traceable to exactly one recorded clarification answer, without unstated additions to that decision? [Consistency, Spec §Clarifications] — *see Note A*
- [x] CHK004 Are accepted-intent acceptance scenarios explicitly distinguishable from stakeholder-confirmed, test-verified, implementation-only, and unresolved scenarios? [Clarity, Spec §User Scenarios & Testing]
- [x] CHK005 Are test-verified behavior claims linked to specific repository test paths or named test classes so their evidence status is reviewable? [Traceability, Spec §Baseline Evidence and Unresolved Conflicts > Verified Behavior Evidence]
- [x] CHK006 Are implementation-only observations linked to concrete backend, frontend, configuration, or migration paths without being described as accepted requirements? [Traceability, Spec §Baseline Evidence and Unresolved Conflicts > Implementation-Only Observations]
- [x] CHK007 Are accepted Asset attributes clearly separated from additional fields and relationships observed only in the implementation? [Clarity, Spec §Requirements > Key Entities]

## Intent Classification and Requirement Consistency

- [x] CHK008 Does the evidence-classification scheme define accepted intent, test-verified behavior, implementation-only behavior, and unresolved findings with mutually exclusive meanings? [Clarity, Spec §Domain Alignment > Evidence Classification] — *resolved 2026-08-12, see Blocker 1*
- [x] CHK009 Are code-only register behaviors such as search, filters, barcode generation, file versioning, and cascading deletion kept outside the normative FR/ALR requirement set unless a stakeholder decision accepts them? [Consistency, Spec §User Story 2; Spec §Baseline Evidence and Unresolved Conflicts]
- [x] CHK010 Are automated tests treated as evidence of current behavior rather than product authority everywhere they are cited? [Consistency, Spec §Domain Alignment > Evidence Classification; Spec §Verified Behavior Evidence]
- [x] CHK011 Do current-behavior tables clearly identify where observed outcomes conform to or conflict with the accepted requirements? [Clarity, Spec §Test-Verified Current Transition Behavior; Spec §Accepted Asset Permission Contract and Current Codes]
- [x] CHK012 Are assumptions worded so they bound interpretation without silently converting implementation evidence into stakeholder intent? [Consistency, Spec §Assumptions]

## Permissions and Negative Authorization Coverage

- [x] CHK013 Are the global-read Roles, Employee Custodian-only scope, and required `asset_view` grant stated unambiguously for register, detail, and aggregate-history access? [Completeness, Spec §ALR-009; Spec §AS-018–AS-019]
- [x] CHK014 Are create, edit, condition-inspection, file-upload, and deletion permissions assigned consistently between ALR-010 and the accepted permission table? [Consistency, Spec §ALR-010; Spec §Accepted Asset Permission Contract and Current Codes] — *resolved 2026-08-12, see Blocker 2*
- [x] CHK015 Is the Employee denial case complete for Assets held by another User and Assets with no Custodian, including terminal Assets whose Custodian is cleared? [Coverage, Spec §NC-009; Spec §ALR-009]
- [x] CHK016 Are negative authorization requirements explicit that denied reads disclose no out-of-scope Asset data and denied writes cause no Asset, file, condition-log, or lifecycle-history mutation? [Completeness, Spec §AS-011; Spec §ALR-002; Spec §SC-003]
- [x] CHK017 Does the specification state that frontend control visibility is insufficient authorization and that every protected action requires enforcement at the action boundary? [Security, Spec §ALR-001]
- [x] CHK018 Is the unresolved custom-Role policy visibly assigned to B1 without weakening the accepted named-Role behavior owned by B2? [Dependency, Spec §Assumptions; Spec §Out of Scope > Adjacent Baseline Ownership]

## Lifecycle Transition and Atomic Side-Effect Coverage

- [x] CHK019 Are all seven canonical statuses, all five canonical conditions, their independence, and the rejected `Scrapped` condition documented consistently? [Completeness, Spec §Domain Alignment; Spec §FR-002–FR-004]
- [x] CHK020 Is initial Asset state limited unambiguously to `Available` or `In Storage` with empty Custodian and department, with all rejected creation combinations stated? [Clarity, Spec §FR-013; Spec §AS-014; Spec §NC-007]
- [x] CHK021 Are `Assigned` and `Under Repair` explicitly owned by Checkout/Transfer and Service Record operations, with direct entry and nonterminal exit rejection requirements? [Coverage, Spec §FR-012; Spec §ALR-004–ALR-005; Spec §NC-002]
- [x] CHK022 Are Service Record status, Custodian, department-clearing, and no-auto-restoration requirements consistent with ADR-0001 and the accepted scenarios? [Consistency, Spec §FR-007; Spec §AS-006; Spec §Accepted Lifecycle Boundary]
- [x] CHK023 Are `Sold` and `Scrapped` source states distinguished from the broader reactive `Lost` source-state rule without an ambiguous catch-all terminal transition? [Clarity, Spec §FR-014; Spec §AS-007–AS-008]
- [x] CHK024 Are Custodian and department effects specified for Checkout, Transfer, check-in, Service Record, `Sold`, `Scrapped`, and `Lost`, including the `Lost` accountability exception? [Completeness, Spec §FR-006; Spec §FR-009; Spec §FR-015; Spec §Accepted Lifecycle Boundary] — *see Note B*
- [x] CHK025 Does the terminal-transition requirement define one atomic outcome covering Asset status, Custodian, department, open Checkout, open Service Record, and every Pending Transfer? [Atomicity, Spec §AS-017; Spec §ALR-003; Spec §ALR-006]
- [x] CHK026 Are rejected `Sold` or `Scrapped` transitions from `Assigned` or `Under Repair` required to leave the Asset and all active lifecycle records unchanged? [Exception Flow, Spec §AS-016; Spec §ALR-008; Spec §NC-008]
- [x] CHK027 Are terminal irreversibility and reactive `Lost` accountability covered by measurable positive and negative acceptance scenarios? [Acceptance Criteria, Spec §AS-008–AS-009; Spec §SC-002; Spec §SC-004]

## Audit, Notification, and Failure Requirements

- [x] CHK028 Does the specification enumerate every successful B2 mutation type that requires an AuditLog record, including Asset, condition-inspection, image, and document mutations? [Completeness, Spec §AS-021; Spec §Accepted Asset Audit and Notification Effects]
- [x] CHK029 Are the additional terminal AuditLog contents explicit for operator, old/new status, Custodian, department, and every automatically closed or rejected lifecycle record? [Clarity, Spec §AS-022; Spec §ALR-011]
- [x] CHK030 Is the no-Notification rule explicit for every B2 mutation and terminal side effect while preserving sibling ownership of explicit Checkout, Transfer, and Service Record notifications? [Consistency, Spec §ALR-011; Spec §Accepted Asset Audit and Notification Effects] — *see Note C*
- [x] CHK031 Are invalid canonical values, forbidden lifecycle transitions, terminal reversals, unauthorized access, invalid condition inspections, and invalid file submissions classified as accepted, governance, implementation-only, or unresolved failure requirements? [Coverage, Spec §Negative Cases; Spec §Current Validation and Failure Behavior]
- [x] CHK032 Do all accepted rejection requirements state the required no-mutation outcome for Asset, Custodian, department, files, and related lifecycle records? [Completeness, Spec §AS-010–AS-013; Spec §ALR-002; Spec §ALR-008]
- [x] CHK033 Is the boundary between B2 trigger requirements and B8 AuditLog storage, access, filtering, and retention requirements explicit and non-overlapping? [Dependency, Spec §Accepted Asset Audit and Notification Effects; Spec §Out of Scope]

## Deferred Scope and Adjacent Baseline Boundaries

- [x] CHK034 Are periodic physical Asset audits described only as deferred future behavior and kept distinct from reactive `Lost`, operational AuditLog, and the current “Asset Audit Report”? [Scope, Spec §Out of Scope > Explicitly Deferred Product Behavior]
- [x] CHK035 Are employee self-service Checkout and employee/team-lead Procurement requests described only as deferred possibilities rather than current B2 behavior? [Scope, Spec §Out of Scope > Explicitly Deferred Product Behavior]
- [x] CHK036 Are B1 and B3–B9 responsibilities excluded precisely enough that this baseline does not claim their workflows, shared facilities, reports, or master-data behavior as implemented B2 requirements? [Dependency, Spec §Out of Scope > Adjacent Baseline Ownership]

## Contradictions, Unresolved Decisions, and Acceptance Readiness

- [x] CHK037 Does every resolved clarification that conflicts with current behavior remain visible as an implementation conformance gap with repository evidence? [Conflict, Spec §Baseline Evidence and Unresolved Conflicts > Unresolved Conflicts 1, 3, 4, 5, 9]
- [x] CHK038 Is the canonical `Checkout` versus user-visible `Assignment` contradiction visible without presenting `Assignment` as an accepted synonym? [Conflict, Spec §FR-004; Spec §Unresolved Conflicts 2]
- [x] CHK039 Are the unresolved Asset identity contract, deletion/history retention, file security/lifecycle, and frontend failure/accessibility decisions visible and excluded from accepted requirements? [Gap, Spec §Unresolved Conflicts 6–8, 10]
- [x] CHK040 Does the Draft acceptance gate identify all remaining stakeholder decisions and conformance gaps that must be resolved before acceptance, without implying readiness for implementation planning? [Acceptance Readiness, Spec §SC-006; Spec §Delivery Boundary] — *resolved 2026-08-12, see Blocker 3*

## Blocking Findings — All Resolved 2026-08-12

**BLOCKER 1 — CHK008: the classification scheme does not cover the labels the
specification actually uses.** §Evidence Classification defines exactly four
classifications: accepted intent, test-verified current behavior,
implementation-only observation, and unresolved. The body then labels scenarios
with two further categories that are never defined: **Stakeholder-confirmed**
(AS-007, AS-008, AS-014–AS-022, NC-007–NC-009, and most of the permission table)
and **Governance requirement** (AS-011, NC-004). "Stakeholder-confirmed" carries
the bulk of this baseline's accepted content, so its absence from the scheme is
not cosmetic — a reviewer cannot tell whether it ranks with accepted intent or
below it. *Fix*: add both to §Evidence Classification with mutually exclusive
definitions, stating whether stakeholder-confirmed content is eligible to be a
baseline requirement on the same footing as accepted intent.
**Resolved 2026-08-12**: both are now defined. Stakeholder-confirmed is stated
as requirement-eligible on the same footing as accepted intent, differing only
in where the authority is recorded; Governance requirement is sourced to the
constitution and marked not open to per-baseline amendment. A precedence rule
now makes the six classifications mutually exclusive.

**BLOCKER 2 — CHK014: ALR-010 and the permission table disagree about Admin.**
ALR-010 grants create and edit to "IT Manager and IT Staff" and closes with "All
other named-Role write attempts MUST be denied without mutation." Read literally
that denies Admin, contradicting the permission table (which lists Admin for
create, edit, and upload), §Domain Alignment ("Admin retains full Asset access"),
and the table's own note about the Admin bypass. *Fix*: name Admin explicitly in
ALR-010's grants, or qualify the closing sentence to exclude Admin.
**Resolved 2026-08-12**: ALR-010 now grants create and edit to "Admin, IT
Manager, and IT Staff", matching the permission table, and its closing sentence
is scoped per action — "a write attempt by any named Role not listed for that
action" — so it can no longer be read as denying a Role the same requirement
grants.

**BLOCKER 3 — CHK040: the acceptance gate is missing two of its own unresolved
findings.** SC-006 enumerates C3, deletion retention, file security/lifecycle,
custom-Role policy, B8 integration, and the C2/terminal/department/Employee-
visibility/terminal-audit conformance gaps. It omits Unresolved Conflict 6 (the
Asset identity and register contract — required/optional fields, unique
identifiers, numeric-versus-text tag format, Procurement optionality) and
Unresolved Conflict 10 (frontend failure and accessibility behavior). Both are
listed as unresolved in the evidence section but are absent from the gate that
governs acceptance, so the Draft could be accepted with them unaddressed.
*Fix*: extend SC-006 to name both, or record an explicit decision that neither
blocks acceptance.
**Resolved 2026-08-12**: SC-006 now enumerates all ten findings by number,
including 6 and 10, and defines what resolution means — the stakeholder accepts
the behavior, directs a correction, or records an explicit exception; a finding
is not resolved by ceasing to be mentioned.

## Non-Blocking Notes

**Note A — CHK003 (passes).** FR-013's rejection of a supplied *department* at
creation is not stated in the Q1 answer it cites; it follows from the Q3
department answer in the same session. The requirement is sound and traceable,
but the citation would be clearer as Q1 + Q3. Same for AS-014.

**Note B — CHK024 (passes).** Custodian and department effects for Transfer are
specified in FR-006 and FR-015, but the §Accepted Lifecycle Boundary table has no
Transfer row while it does have rows for Checkout, check-in, Service Record, and
each terminal transition. Adding one would make the table self-contained.

**Note C — CHK030 (passes).** ALR-011's final sentence reads "No B2 mutation or
terminal side effect MUST create a Notification." The intent is unambiguous from
the surrounding text, but the construction is literally ambiguous; "MUST NOT
create a Notification" would be exact.

## Notes

- Check items off as the written requirements are reviewed: `[x]`.
- Record findings inline or link to the relevant clarification decision.
- A checked item means the specification is complete and unambiguous for that
  requirement-quality concern; it does not mean current code conforms.
- **Dependency caveat**: B1 and B6 are not yet accepted. Items CHK013, CHK014,
  and CHK018 rest on B1's permission matrix and custom-Role policy; if B1's
  acceptance alters either, re-execute them before relying on this result.
  B1's Draft was amended on 2026-08-12 and those three items were re-executed —
  see §Dependency Re-run below. B6 remains unexecuted.

## Dependency Re-run — 2026-08-12

B1's acceptance review amended FR-010 (anchoring "the accepted permission-code
set" to the nine codes enumerated at the 2026-07-29 Evidence Date) and FR-011
(binding custom Roles to that same set). The three B2 items resting on those
requirements were re-executed against the amended text.

| Item | Result | Basis |
| --- | --- | --- |
| CHK013 | **Still passes** | B1's per-Role grants are unchanged by the amendment — only Admin's row and the set definition moved. `asset_view` is still granted to all six named Roles, so B2's ALR-009 (Admin, IT Manager, IT Staff, HR, Viewer global; Employee Custodian-only) remains aligned with B1 FR-010 and FR-012. |
| CHK014 | **Still passes, and is now better grounded** | B2's ALR-010 grants are exactly the Asset-related subset of B1's FR-010 matrix: IT Staff holds `asset_create` and `asset_edit` but not `asset_delete`, matching "deletion only to Admin and IT Manager"; IT Manager holds all three; Admin holds the full nine-code set. Admin's Asset authority now rests on an enumerated grant in B1 rather than on the implementation bypass recorded as unresolved in B1's Conflict 5. |
| CHK018 | **Still passes** | B2 assigns custom-Role policy to B1 without asserting it is unanswered — §Assumptions says B1 "remains responsible", and SC-006 says it "depend[s] on baselines that are not yet accepted". Both are statements of ownership and sequencing, and both stay accurate now that B1's Draft resolves the policy in FR-011 and FR-012. B2's accepted named-Role behavior is unweakened. |

No B2 requirement text required amendment as a result. The remaining coupling is
procedural rather than textual: B2's named-Role grants are a subset of B1's
matrix, so the two should be signed off together, or B1 first. Accepting B2
alone would freeze a requirement whose authority still sits in an unaccepted
Draft.
