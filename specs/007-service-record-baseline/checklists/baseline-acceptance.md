# Brownfield Baseline Acceptance Checklist: B5 Service Record Lifecycle

**Purpose**: Formal stakeholder and reviewer gate for determining whether the B5 requirements are complete, clear, consistent, measurable, and evidence-qualified before the Draft baseline is accepted
**Created**: 2026-08-05
**Feature**: [B5 specification](../spec.md)

**Note**: This checklist validates the requirements as written. It is not an
implementation test plan. Mark an item complete only when the specification
answers it unambiguously and traceably; implementation behavior alone is not
sufficient. Baseline acceptance requires every item to be checked or covered by
an explicit stakeholder-approved waiver recorded in the specification.

## ADR-0001 Alignment and Custody Restoration

- [ ] CHK001 Is the ADR-0001 decision — opening clears Custodian and sets `Under Repair`, closing returns `Available` without restoring the previous Custodian — stated identically in the domain vocabulary, the requirements, and the evidence sections, with no weaker variant anywhere? [Consistency, Spec §Domain Alignment, §FR-004, §FR-012, §Accepted Intent]
- [ ] CHK002 Are both alternatives ADR-0001 explicitly rejected — retaining custody through servicing and auto-restoring the previous Custodian on close — recorded as prohibited outcomes rather than merely unimplemented ones? [Completeness, Spec §FR-012, §Out of Scope]
- [ ] CHK003 Is "no automatic Custodian restoration" specified as a requirement about the closing operation itself, so that no future convenience path (bulk close, reopen, correction, or import) may restore custody implicitly? [Clarity, Spec §FR-012, §ALR-005]
- [ ] CHK004 Is the fresh Checkout after service defined as a separate, deliberate, independently authorized operation owned by B3, rather than a step of closing a Service Record? [Clarity, Spec §AS-011, §FR-012, §Lifecycle and Actors]
- [ ] CHK005 Does the specification state that closing creates no Checkout and reopens no Checkout, so an Asset returning from a Vendor is unheld until a new Checkout occurs? [Completeness, Spec §FR-012, §AS-010]
- [ ] CHK006 Is the ADR-0001 "one Asset, one clear state at a time" rationale reflected consistently in the department rule, the interrupted-Checkout rule, and the `Under Repair` ownership rule? [Consistency, Spec §FR-005, §FR-006, §FR-014]

## Actors, Permissions, and Visibility

- [ ] CHK007 Is `asset_custody_manage` identified as the authoritative permission for both opening and closing, with the named-Role expectations for Admin, IT Manager, IT Staff, HR, Employee, and Viewer complete? [Completeness, Spec §ALR-001, §Accepted Service Record Actor and Permission Contract]
- [ ] CHK008 Are custom Roles granted `asset_custody_manage` addressed explicitly, with no implicit bypass beyond the documented Admin and superuser behavior? [Coverage, Spec §ALR-001, §Accepted Service Record Actor and Permission Contract]
- [ ] CHK009 Are Service Record read requirements complete for global non-Employee visibility and for the Employee scope under B1? [Completeness, Spec §ALR-002, §AS-032]
- [ ] CHK010 Is the Employee visibility rule for a Service Record whose subject User was deliberately cleared resolved, or explicitly assigned to B1 with the consequence of leaving it open stated? [Gap, Spec §ALR-002, §Edge Cases, §Remaining Evidence-Led Confirmation Items]
- [ ] CHK011 Does the specification require server-side authorization at every read, open, and close boundary while treating frontend control visibility as a corresponding — not sufficient — control? [Security Coverage, Spec §ALR-003]
- [ ] CHK012 Is direct update or deletion of a Service Record unambiguously prohibited for every actor including Admin and platform superusers, with all valid state changes assigned to named lifecycle operations? [Clarity, Spec §FR-019, §ALR-005, §ALR-009]
- [ ] CHK013 Is the actor who may correct a mistaken cost, outcome, bill reference, or date on an already-closed record specified, given that FR-019 forbids direct record editing? [Gap, Spec §FR-019, §ALR-005]
- [ ] CHK014 Are the permission requirements for attaching, replacing, or reading the bill/service document stated, rather than inherited implicitly from Asset document permissions? [Gap, Spec §FR-028, §Accepted Service Record Actor and Permission Contract]

## Eligible and Rejected Asset States

- [ ] CHK015 Is the eligible source-state set stated as exactly `Available` and `Assigned`, with `In Storage` named as rejected rather than merely unlisted? [Clarity, Spec §FR-008, §AS-035]
- [ ] CHK016 Is the required path for servicing a stored Asset — return it to `Available` through an accepted B2 administrative transition first — stated as a requirement rather than left as operator practice? [Completeness, Spec §FR-008, §Edge Cases]
- [ ] CHK017 Are rejections specified for an Asset already `Under Repair` and for each of `Sold`, `Scrapped`, and `Lost`, with the Asset left unchanged in every case? [Coverage, Spec §FR-007, §AS-004, §AS-005]
- [ ] CHK018 Is the B6 dependency complete and enforceable — no current Procurement and a flagged legacy Vendor both block opening — rather than stated only as an assumption? [Dependency Coverage, Spec §FR-009, §AS-008]
- [ ] CHK019 Is `Under Repair` specified as enterable only by opening and leavable only by closing, with direct status editing rejected in both directions? [Clarity, Spec §FR-006, §AS-007, §AS-015]
- [ ] CHK020 Is the accepted terminal path from `Under Repair` limited to `Lost`, with `Sold` and `Scrapped` from `Under Repair` identified as a B2-owned conformance gap rather than accepted B5 behavior? [Consistency, Spec §FR-016, §AS-020, §U-005]
- [ ] CHK021 Are the incompatibility rules between `Under Repair` and Transfer stated as a boundary B5 depends on, without B5 redefining B4 behavior? [Dependency Consistency, Spec §AS-018, §Out of Scope]
- [ ] CHK022 Is the requirement that closing always returns `Available` — with no pre-service status captured or restored — consistent across the requirements, scenarios, entity definition, and evidence sections? [Consistency, Spec §FR-008, §FR-010, §Key Entities]

## Atomic Custodian, Status, and Checkout Effects

- [ ] CHK023 Are all opening effects required to commit as one operation: record creation, interrupted-Checkout closure, Custodian clearing, department clearing, `Under Repair` status, and the required AuditLog entry? [Atomicity, Spec §ALR-004, §AS-002]
- [ ] CHK024 Are all closing effects required to commit as one operation: closed state, return date, cost, outcome, `Available` status, and the required AuditLog entry? [Atomicity, Spec §ALR-004, §AS-014]
- [ ] CHK025 Is the ordering requirement explicit that the interrupted Checkout closes and the Custodian clears *before* the Asset becomes `Under Repair`, so no intermediate state is observable? [Clarity, Spec §FR-014, §AS-016]
- [ ] CHK026 Is the interrupted Checkout required to remain distinguishable from an ordinary check-in and exempt from B3's return-condition and return-remark rules, with that ownership assigned to B3 rather than restated as B5 behavior? [Dependency Consistency, Spec §FR-015, §ALR-007, §Out of Scope]
- [ ] CHK027 Is the department-follows-custody rule complete for all three points — cleared at opening, absent while at the Vendor, not restored at closing — and reconciled with accepted B2 without requiring a B2 amendment? [Consistency, Spec §FR-005, §U-002]
- [ ] CHK028 Do all rejected openings and closings — permission, eligibility, date, cost, bill, and outcome failures — carry an explicit zero-partial-mutation requirement covering the Asset, its Custodian, its condition, its open Checkout, and every Service Record? [Negative Coverage, Spec §ALR-006, §AS-021, §SC-002]
- [ ] CHK029 Is the terminal auto-closure requirement complete: atomic with the B2 transition, closing every open Service Record, and distinguishable from an operator-confirmed closure that carries a cost and outcome? [Completeness, Spec §FR-016, §AS-019, §Accepted B5 Notification and Audit Trigger Matrix]

## Open and Close Repetition and Concurrency

- [ ] CHK030 Is a second closure of an already-closed record defined as rejected, with both the record and the Asset unchanged? [Exception Coverage, Spec §FR-013, §AS-012]
- [ ] CHK031 Is reopening a closed Service Record prohibited outright, rather than left undefined for a correction or re-repair case? [Clarity, Spec §FR-013, §FR-019]
- [ ] CHK032 Is a repeat repair on the same Asset specified as a new Service Record, so repeated servicing produces distinct events rather than an amended one? [Coverage, Spec §FR-001, §FR-013]
- [ ] CHK033 Is the "at most one `Open` Service Record per Asset" property stated as an enforceable invariant, rather than only as an emergent consequence of the status precondition recorded in Assumptions? [Gap, Spec §Assumptions, §FR-007]
- [ ] CHK034 Does the specification require the single-open and single-close guarantees to hold under simultaneous attempts, rather than permitting last-writer-wins behavior? [Concurrency Coverage, Spec §Edge Cases, §ALR-004, §OBS-AS-007, §OBS-AS-011]

## Vendor Identity and Requirements

- [ ] CHK035 Is a managed Vendor identity required for every Service Record, with free-typed supplier text prohibited rather than merely discouraged? [Clarity, Spec §FR-002, §AS-003]
- [ ] CHK036 Is the shared-Vendor rationale — reliable Vendor-grouped reporting across Procurement and Service Record — stated so that Vendor identity cannot be satisfied by a Service-Record-local value? [Traceability, Spec §Domain Alignment, §Accepted Intent]
- [ ] CHK037 Is Vendor administration clearly excluded and assigned to B6, with only Vendor *selection* owned by B5? [Scope, Spec §Out of Scope, §Key Entities]
- [ ] CHK038 Is the expectation that a Vendor referenced by a Service Record cannot be deleted stated as a requirement or explicitly assigned to B6, given that only the Procurement reference path is test-backed? [Gap, Spec §Edge Cases, §CAND-016]
- [ ] CHK039 Is a Vendor change on an open Service Record — when an Asset is forwarded to a different repairer — either specified or explicitly excluded? [Gap, Spec §FR-018, §FR-019]

## Dates, Cost, Bill, and Outcome

- [ ] CHK040 Are the sent-date and return-date rules complete and objectively verifiable: operator-supplied, defaulted to now, correctable, not future-dated, and correctly ordered? [Acceptance Criteria, Spec §FR-026, §AS-036, §SC-013]
- [ ] CHK041 Is the distinction between the business sent date and the moment the record was created stated clearly enough that the creation moment cannot be substituted for it on any surface? [Clarity, Spec §Edge Cases, §FR-026]
- [ ] CHK042 Are the expected-return rules complete — optional, on or after the sent date, and the sole input to the overdue derivation — with the comparison semantics between a date-only expected return and timestamped sent/return values unambiguous? [Ambiguity, Spec §FR-027, §AS-037]
- [ ] CHK043 Is overdue defined as derived rather than stored, excluded from Asset status and from Service Record state, and specified as non-blocking for closure and every other operation? [Clarity, Spec §FR-027, §AS-038]
- [ ] CHK044 Is the cost rule complete and measurable: mandatory at closure, zero permitted and meaning no-charge, negative and missing both rejected without mutation? [Acceptance Criteria, Spec §FR-011, §AS-039, §SC-014]
- [ ] CHK045 Is the conditional bill requirement unambiguous — bill reference and attached document required when cost is above zero, both optional at zero cost — including the outcome when only one of the two is supplied? [Clarity, Spec §FR-028, §AS-040]
- [ ] CHK046 Is the storage, immutability, and replacement policy for the bill/service document specified, or explicitly deferred as a planning detail with that deferral recorded? [Gap, Spec §FR-028, §U-003]
- [ ] CHK047 Are the four canonical outcome values exhaustive and mutually exclusive for every repair the organization sends to a Vendor, with a missing or noncanonical value rejected? [Completeness, Spec §FR-029, §AS-041, §Assumptions]
- [ ] CHK048 Is the outcome clearly separated from Asset `condition`, Asset status, and the condition history, including the rule that `Not Repairable` triggers no terminal transition by itself? [Consistency, Spec §FR-017, §FR-029, §Edge Cases]
- [ ] CHK049 Is the `Replaced` outcome's boundary stated — it describes the repair, not the creation of a replacement Asset, and no link between the two is recorded? [Clarity, Spec §Edge Cases, §Out of Scope]
- [ ] CHK050 Is the requirement that opening reason, opening remarks, and closing remarks are retained as distinct values stated so that no closure path can overwrite earlier text? [Completeness, Spec §FR-030, §AS-042]
- [ ] CHK051 Is the single-currency assumption for cost recorded as an assumption with its scope boundary, rather than left implicit in a numeric field? [Assumption, Spec §Assumptions]
- [ ] CHK052 Is the relationship between a repair outcome and the Asset's condition history resolved, or recorded as a confirmation item with the consequence of leaving it open stated? [Gap, Spec §CAND-009, §Remaining Evidence-Led Confirmation Items]

## Notifications and AuditLog Effects

- [ ] CHK053 Are Notification triggers and recipient rules complete for opening, opening with no Custodian, closing, overdue, interrupted closure, and terminal auto-closure, with every deliberate no-Notification case stated as deliberate? [Completeness, Spec §FR-021, §Accepted B5 Notification and Audit Trigger Matrix]
- [ ] CHK054 Is every accepted Notification destination specified as a resolvable outcome rather than a literal current path, including the correction of the unresolvable Asset-detail destination? [Clarity, Spec §FR-022, §CAND-010]
- [ ] CHK055 Is the requirement that the B3 interrupted-closure Notification and the B5 opening Notification remain separate messages stated with its rationale, so neither baseline suppresses the other's trigger? [Dependency Consistency, Spec §FR-021, §AS-044, §Edge Cases]
- [ ] CHK056 Is the closing Notification recipient rule precise about whether the closing operator is included among the `asset_custody_manage` holders notified? [Ambiguity, Spec §FR-021, §AS-043]
- [ ] CHK057 Are B8-owned in-app-only delivery, recipient specificity, retry, deduplication, read state, access, and retention clearly separated from B5-owned trigger selection? [Dependency Coverage, Spec §FR-021, §FR-022, §ALR-008, §Out of Scope]
- [ ] CHK058 Are required AuditLog events complete for successful opening, successful closing, terminal auto-closure, and every rejected or permission-denied attempt, with routine reads explicitly excluded? [Completeness, Spec §FR-023, §AS-045]
- [ ] CHK059 Are the minimum B5-specific AuditLog values defined per event — including cost and outcome on closure and the reason on rejection — and consistent with B8 privacy, minimization, source-IP, and retention rules? [Privacy/Clarity, Spec §FR-023, §AS-031, §Accepted B5 Notification and Audit Trigger Matrix]
- [ ] CHK060 Is audit atomicity stated consistently — required-audit failure rolls back the owning opening or closure, Notification failure does not roll back completed work? [Reliability/Consistency, Spec §ALR-008, §AS-029, §AS-030, §SC-010]
- [ ] CHK061 Is the production delivery guarantee for the new overdue Notification addressed, including its dependency on the unresolved `ROADMAP.md` C5 scheduling question? [Assumption/Gap, Spec §FR-027, §Edge Cases, §Remaining Evidence-Led Confirmation Items]
- [ ] CHK062 Is the outcome specified when a Notification recipient has no reachable delivery target, so a silent non-delivery is not treated as a satisfied trigger? [Exception Coverage, Spec §OBS-AS-023, §ALR-008]

## Evidence Integrity, Scope, and Decision Closure

- [ ] CHK063 Is every accepted requirement traceable to `CONTEXT.md`, ADR-0001, an accepted or Draft dependency identifier, or the 2026-08-05 stakeholder clarification, with no requirement resting on implementation evidence alone? [Traceability, Spec §FR-024, §SC-012]
- [ ] CHK064 Are all four resolved decisions U-001 through U-004 recorded with their answers, the requirements they produced, and the conformance gaps they created, without any current-behavior alternative still presented as accepted? [Completeness, Spec §Unresolved Conflicts, §SC-011]
- [ ] CHK065 Are all 17 conformance gaps in U-005 stated as findings that leave their contradicted requirement intact, rather than as grounds for weakening it? [Consistency, Spec §U-005, §FR-025]
- [ ] CHK066 Is the distinction between accepted B2 and the Draft status of B1, B3, B6, and B8 stated accurately everywhere those baselines are cited as sources? [Traceability, Spec §Specification Lineage, §Assumptions]
- [ ] CHK067 Are the retention consequences for service history when an Asset or a User is deleted either specified or explicitly assigned to B2 and B1? [Gap, Spec §Edge Cases]
- [ ] CHK068 Is the boundary against B9 clear — that Dashboard counts, current-service and Vendor-service reports, and exports consume B5 data without defining B5 requirements — including the note that departmental cost attribution cannot be read from the live Asset department? [Scope, Spec §Out of Scope, §Edge Cases]
- [ ] CHK069 Are Vendor administration, Procurement, Warranty/AMC, and automatic Checkout after service each excluded explicitly rather than by omission? [Scope, Spec §Out of Scope]
- [ ] CHK070 Are the canonical terms `Service Record`, `Under Repair`, `Open`, `Closed`, `Vendor`, `Custodian`, and `Checkout` used consistently, with `Assignment` absent and automatic custody restoration never implied by any label or message? [Consistency, Spec §FR-020, §Domain Alignment]

## Notes

- This is a formal baseline-acceptance gate for specification reviewers and
  stakeholders before B5 leaves `Draft`.
- Items marked `[Gap]`, `[Assumption/Gap]`, or `[Ambiguity]` intentionally expose
  requirements that may still need a stakeholder decision or an explicit scope
  exclusion. They are not defects in the clarification session; the four mandated
  B5 decisions were closed on 2026-08-05.
- Record supporting requirement identifiers, review findings, or approved
  waivers inline before checking an item.
- The absence of `plan.md` is not evaluated here because this checklist reviews
  the brownfield baseline requirements before implementation planning. For the
  same reason `check-prerequisites.ps1 -Json` reports a missing plan; that is
  expected for a documentation-only baseline.
- The separate `requirements.md` checklist validates specification quality. This
  checklist is the stakeholder acceptance gate and is deliberately stricter.
