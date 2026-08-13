# Brownfield Baseline Acceptance Checklist: B5 Service Record Lifecycle

**Purpose**: Formal stakeholder and reviewer gate for determining whether the B5 requirements are complete, clear, consistent, measurable, and evidence-qualified before the Draft baseline is accepted
**Executed**: 2026-08-12 — 65 of 70 pass on first execution; all 5 findings resolved the same day, 70 of 70 now closed.

**Created**: 2026-08-05
**Feature**: [B5 specification](../spec.md)

**Note**: This checklist validates the requirements as written. It is not an
implementation test plan. Mark an item complete only when the specification
answers it unambiguously and traceably; implementation behavior alone is not
sufficient. Baseline acceptance requires every item to be checked or covered by
an explicit stakeholder-approved waiver recorded in the specification.

## ADR-0001 Alignment and Custody Restoration

- [x] CHK001 Is the ADR-0001 decision — opening clears Custodian and sets `Under Repair`, closing returns `Available` without restoring the previous Custodian — stated identically in the domain vocabulary, the requirements, and the evidence sections, with no weaker variant anywhere? [Consistency, Spec §Domain Alignment, §FR-004, §FR-012, §Accepted Intent]
- [x] CHK002 Are both alternatives ADR-0001 explicitly rejected — retaining custody through servicing and auto-restoring the previous Custodian on close — recorded as prohibited outcomes rather than merely unimplemented ones? [Completeness, Spec §FR-012, §Out of Scope]
- [x] CHK003 Is "no automatic Custodian restoration" specified as a requirement about the closing operation itself, so that no future convenience path (bulk close, reopen, correction, or import) may restore custody implicitly? [Clarity, Spec §FR-012, §ALR-005]
- [x] CHK004 Is the fresh Checkout after service defined as a separate, deliberate, independently authorized operation owned by B3, rather than a step of closing a Service Record? [Clarity, Spec §AS-011, §FR-012, §Lifecycle and Actors]
- [x] CHK005 Does the specification state that closing creates no Checkout and reopens no Checkout, so an Asset returning from a Vendor is unheld until a new Checkout occurs? [Completeness, Spec §FR-012, §AS-010]
- [x] CHK006 Is the ADR-0001 "one Asset, one clear state at a time" rationale reflected consistently in the department rule, the interrupted-Checkout rule, and the `Under Repair` ownership rule? [Consistency, Spec §FR-005, §FR-006, §FR-014]

## Actors, Permissions, and Visibility

- [x] CHK007 Is `asset_custody_manage` identified as the authoritative permission for both opening and closing, with the named-Role expectations for Admin, IT Manager, IT Staff, HR, Employee, and Viewer complete? [Completeness, Spec §ALR-001, §Accepted Service Record Actor and Permission Contract]
- [x] CHK008 Are custom Roles granted `asset_custody_manage` addressed explicitly, with no implicit bypass beyond the documented Admin and superuser behavior? [Coverage, Spec §ALR-001, §Accepted Service Record Actor and Permission Contract]
- [x] CHK009 Are Service Record read requirements complete for global non-Employee visibility and for the Employee scope under B1? [Completeness, Spec §ALR-002, §AS-032]
- [x] CHK010 Is the Employee visibility rule for a Service Record whose subject User was deliberately cleared resolved, or explicitly assigned to B1 with the consequence of leaving it open stated? [Gap, Spec §ALR-002, §Edge Cases, §Remaining Evidence-Led Confirmation Items]
- [x] CHK011 Does the specification require server-side authorization at every read, open, and close boundary while treating frontend control visibility as a corresponding — not sufficient — control? [Security Coverage, Spec §ALR-003]
- [x] CHK012 Is direct update or deletion of a Service Record unambiguously prohibited for every actor including Admin and platform superusers, with all valid state changes assigned to named lifecycle operations? [Clarity, Spec §FR-019, §ALR-005, §ALR-009]
- [x] CHK013 Is the actor who may correct a mistaken cost, outcome, bill reference, or date on an already-closed record specified, given that FR-019 forbids direct record editing? [Gap, Spec §FR-019, §ALR-005] — *resolved 2026-08-12, see Finding 1*
- [x] CHK014 Are the permission requirements for attaching, replacing, or reading the bill/service document stated, rather than inherited implicitly from Asset document permissions? [Gap, Spec §FR-028, §Accepted Service Record Actor and Permission Contract]

## Eligible and Rejected Asset States — *resolved 2026-08-12, see Finding 2*

- [x] CHK015 Is the eligible source-state set stated as exactly `Available` and `Assigned`, with `In Storage` named as rejected rather than merely unlisted? [Clarity, Spec §FR-008, §AS-035]
- [x] CHK016 Is the required path for servicing a stored Asset — return it to `Available` through an Draft B2 administrative transition first — stated as a requirement rather than left as operator practice? [Completeness, Spec §FR-008, §Edge Cases]
- [x] CHK017 Are rejections specified for an Asset already `Under Repair` and for each of `Sold`, `Scrapped`, and `Lost`, with the Asset left unchanged in every case? [Coverage, Spec §FR-007, §AS-004, §AS-005]
- [x] CHK018 Is the B6 dependency complete and enforceable — no current Procurement and a flagged legacy Vendor both block opening — rather than stated only as an assumption? [Dependency Coverage, Spec §FR-009, §AS-008]
- [x] CHK019 Is `Under Repair` specified as enterable only by opening and leavable only by closing, with direct status editing rejected in both directions? [Clarity, Spec §FR-006, §AS-007, §AS-015]
- [x] CHK020 Is the accepted terminal path from `Under Repair` limited to `Lost`, with `Sold` and `Scrapped` from `Under Repair` identified as a B2-owned conformance gap rather than accepted B5 behavior? [Consistency, Spec §FR-016, §AS-020, §U-005]
- [x] CHK021 Are the incompatibility rules between `Under Repair` and Transfer stated as a boundary B5 depends on, without B5 redefining B4 behavior? [Dependency Consistency, Spec §AS-018, §Out of Scope]
- [x] CHK022 Is the requirement that closing always returns `Available` — with no pre-service status captured or restored — consistent across the requirements, scenarios, entity definition, and evidence sections? [Consistency, Spec §FR-008, §FR-010, §Key Entities]

## Atomic Custodian, Status, and Checkout Effects

- [x] CHK023 Are all opening effects required to commit as one operation: record creation, interrupted-Checkout closure, Custodian clearing, department clearing, `Under Repair` status, and the required AuditLog entry? [Atomicity, Spec §ALR-004, §AS-002]
- [x] CHK024 Are all closing effects required to commit as one operation: closed state, return date, cost, outcome, `Available` status, and the required AuditLog entry? [Atomicity, Spec §ALR-004, §AS-014]
- [x] CHK025 Is the ordering requirement explicit that the interrupted Checkout closes and the Custodian clears *before* the Asset becomes `Under Repair`, so no intermediate state is observable? [Clarity, Spec §FR-014, §AS-016]
- [x] CHK026 Is the interrupted Checkout required to remain distinguishable from an ordinary check-in and exempt from B3's return-condition and return-remark rules, with that ownership assigned to B3 rather than restated as B5 behavior? [Dependency Consistency, Spec §FR-015, §ALR-007, §Out of Scope]
- [x] CHK027 Is the department-follows-custody rule complete for all three points — cleared at opening, absent while at the Vendor, not restored at closing — and reconciled with Draft B2 without requiring a B2 amendment? [Consistency, Spec §FR-005, §U-002]
- [x] CHK028 Do all rejected openings and closings — permission, eligibility, date, cost, bill, and outcome failures — carry an explicit zero-partial-mutation requirement covering the Asset, its Custodian, its condition, its open Checkout, and every Service Record? [Negative Coverage, Spec §ALR-006, §AS-021, §SC-002]
- [x] CHK029 Is the terminal auto-closure requirement complete: atomic with the B2 transition, closing every open Service Record, and distinguishable from an operator-confirmed closure that carries a cost and outcome? [Completeness, Spec §FR-016, §AS-019, §Accepted B5 Notification and Audit Trigger Matrix]

## Open and Close Repetition and Concurrency

- [x] CHK030 Is a second closure of an already-closed record defined as rejected, with both the record and the Asset unchanged? [Exception Coverage, Spec §FR-013, §AS-012]
- [x] CHK031 Is reopening a closed Service Record prohibited outright, rather than left undefined for a correction or re-repair case? [Clarity, Spec §FR-013, §FR-019]
- [x] CHK032 Is a repeat repair on the same Asset specified as a new Service Record, so repeated servicing produces distinct events rather than an amended one? [Coverage, Spec §FR-001, §FR-013]
- [x] CHK033 Is the "at most one `Open` Service Record per Asset" property stated as an enforceable invariant, rather than only as an emergent consequence of the status precondition recorded in Assumptions? [Gap, Spec §Assumptions, §FR-007] — *resolved 2026-08-12, see Finding 3*
- [x] CHK034 Does the specification require the single-open and single-close guarantees to hold under simultaneous attempts, rather than permitting last-writer-wins behavior? [Concurrency Coverage, Spec §Edge Cases, §ALR-004, §OBS-AS-007, §OBS-AS-011]

## Vendor Identity and Requirements

- [x] CHK035 Is a managed Vendor identity required for every Service Record, with free-typed supplier text prohibited rather than merely discouraged? [Clarity, Spec §FR-002, §AS-003]
- [x] CHK036 Is the shared-Vendor rationale — reliable Vendor-grouped reporting across Procurement and Service Record — stated so that Vendor identity cannot be satisfied by a Service-Record-local value? [Traceability, Spec §Domain Alignment, §Accepted Intent]
- [x] CHK037 Is Vendor administration clearly excluded and assigned to B6, with only Vendor *selection* owned by B5? [Scope, Spec §Out of Scope, §Key Entities]
- [x] CHK038 Is the expectation that a Vendor referenced by a Service Record cannot be deleted stated as a requirement or explicitly assigned to B6, given that only the Procurement reference path is test-backed? [Gap, Spec §Edge Cases, §CAND-016] — *resolved 2026-08-12, see Finding 4*
- [x] CHK039 Is a Vendor change on an open Service Record — when an Asset is forwarded to a different repairer — either specified or explicitly excluded? [Gap, Spec §FR-018, §FR-019]

## Dates, Cost, Bill, and Outcome — *resolved 2026-08-12, see Finding 4*

- [x] CHK040 Are the sent-date and return-date rules complete and objectively verifiable: operator-supplied, defaulted to now, correctable, not future-dated, and correctly ordered? [Acceptance Criteria, Spec §FR-026, §AS-036, §SC-013]
- [x] CHK041 Is the distinction between the business sent date and the moment the record was created stated clearly enough that the creation moment cannot be substituted for it on any surface? [Clarity, Spec §Edge Cases, §FR-026]
- [x] CHK042 Is the current absence of expected-return validation and overdue behavior classified as evidence rather than a B5 requirement, with normative delivery linked to CHG-B5-01? [Scope, Spec §FWD-B5-001, §OBS-AS-014]
- [x] CHK043 Is CHG-B5-01 excluded from the B5 acceptance decision so accepting B5 cannot imply that overdue behavior is implemented? [Lineage, Spec §Extended by, §FWD-B5-001]
- [x] CHK044 Is the cost rule complete and measurable: mandatory at closure, zero permitted and meaning no-charge, negative and missing both rejected without mutation? [Acceptance Criteria, Spec §FR-011, §AS-039, §SC-014]
- [x] CHK045 Is the conditional bill requirement unambiguous — bill reference and attached document required when cost is above zero, both optional at zero cost — including the outcome when only one of the two is supplied? [Clarity, Spec §FR-028, §AS-040]
- [x] CHK046 Is the storage, immutability, and replacement policy for the bill/service document specified, or explicitly deferred as a planning detail with that deferral recorded? [Gap, Spec §FR-028, §U-003]
- [x] CHK047 Are the four canonical outcome values exhaustive and mutually exclusive for every repair the organization sends to a Vendor, with a missing or noncanonical value rejected? [Completeness, Spec §FR-029, §AS-041, §Assumptions]
- [x] CHK048 Is the outcome clearly separated from Asset `condition`, Asset status, and the condition history, including the rule that `Not Repairable` triggers no terminal transition by itself? [Consistency, Spec §FR-017, §FR-029, §Edge Cases]
- [x] CHK049 Is the `Replaced` outcome's boundary stated — it describes the repair, not the creation of a replacement Asset, and no link between the two is recorded? [Clarity, Spec §Edge Cases, §Out of Scope]
- [x] CHK050 Is the requirement that opening reason, opening remarks, and closing remarks are retained as distinct values stated so that no closure path can overwrite earlier text? [Completeness, Spec §FR-030, §AS-042]
- [x] CHK051 Is the single-currency assumption for cost recorded as an assumption with its scope boundary, rather than left implicit in a numeric field? [Assumption, Spec §Assumptions]
- [x] CHK052 Is the relationship between a repair outcome and the Asset's condition history resolved, or recorded as a confirmation item with the consequence of leaving it open stated? [Gap, Spec §CAND-009, §Remaining Evidence-Led Confirmation Items]

## Notifications and AuditLog Effects

- [x] CHK053 Are B5 baseline Notification triggers and recipient rules complete for opening, opening with no Custodian, closing, interrupted closure, and terminal auto-closure, with every deliberate no-Notification case stated as deliberate and prospective overdue delivery excluded to CHG-B5-01? [Completeness/Scope, Spec §FR-021, §FWD-B5-001, §Accepted B5 Notification and Audit Trigger Matrix]
- [x] CHK054 Is every accepted Notification destination specified as a resolvable outcome rather than a literal current path, including the correction of the unresolvable Asset-detail destination? [Clarity, Spec §FR-022, §CAND-010]
- [x] CHK055 Is the requirement that the B3 interrupted-closure Notification and the B5 opening Notification remain separate messages stated with its rationale, so neither baseline suppresses the other's trigger? [Dependency Consistency, Spec §FR-021, §AS-044, §Edge Cases]
- [x] CHK056 Is the closing Notification recipient rule precise about whether the closing operator is included among the `asset_custody_manage` holders notified? [Ambiguity, Spec §FR-021, §AS-043]
- [x] CHK057 Are B8-owned in-app-only delivery, recipient specificity, retry, deduplication, read state, access, and retention clearly separated from B5-owned trigger selection? [Dependency Coverage, Spec §FR-021, §FR-022, §ALR-008, §Out of Scope]
- [x] CHK058 Are required AuditLog events complete for successful opening, successful closing, terminal auto-closure, and every rejected or permission-denied attempt, with routine reads explicitly excluded? [Completeness, Spec §FR-023, §AS-045]
- [x] CHK059 Are the minimum B5-specific AuditLog values defined per event — including cost and outcome on closure and the reason on rejection — and consistent with B8 privacy, minimization, source-IP, and retention rules? [Privacy/Clarity, Spec §FR-023, §AS-031, §Accepted B5 Notification and Audit Trigger Matrix]
- [x] CHK060 Is audit atomicity stated consistently — required-audit failure rolls back the owning opening or closure, Notification failure does not roll back completed work? [Reliability/Consistency, Spec §ALR-008, §AS-029, §AS-030, §SC-010]
- [x] CHK061 Is production delivery of the prospective overdue Notification assigned only to CHG-B5-01 and B8 rather than treated as B5 current behavior? [Scope, Spec §FWD-B5-001]
- [x] CHK062 Is the outcome specified when a Notification recipient has no reachable delivery target, so a silent non-delivery is not treated as a satisfied trigger? [Exception Coverage, Spec §OBS-AS-023, §ALR-008]

## Evidence Integrity, Scope, and Decision Closure

- [x] CHK063 Is every accepted requirement traceable to `CONTEXT.md`, ADR-0001, an accepted or Draft dependency identifier, or the 2026-08-05 stakeholder clarification, with no requirement resting on implementation evidence alone? [Traceability, Spec §FR-024, §SC-012]
- [x] CHK064 Are all four resolved decisions U-001 through U-004 recorded with their answers, the requirements they produced, and the conformance gaps they created, without any current-behavior alternative still presented as accepted? [Completeness, Spec §Unresolved Conflicts, §SC-011]
- [x] CHK065 Are all 17 conformance gaps in U-005 stated as findings that leave their contradicted requirement intact, rather than as grounds for weakening it? [Consistency, Spec §U-005, §FR-025]
- [x] CHK066 Is the distinction between Draft B2 and the Draft status of B1, B3, B6, and B8 stated accurately everywhere those baselines are cited as sources? [Traceability, Spec §Specification Lineage, §Assumptions]
- [x] CHK067 Are the retention consequences for service history when an Asset or a User is deleted either specified or explicitly assigned to B2 and B1? [Gap, Spec §Edge Cases]
- [x] CHK068 Is the boundary against B9 clear — that Dashboard counts, current-service and Vendor-service reports, and exports consume B5 data without defining B5 requirements — including the note that departmental cost attribution cannot be read from the live Asset department? [Scope, Spec §Out of Scope, §Edge Cases]
- [x] CHK069 Are Vendor administration, Procurement, Warranty/AMC, and automatic Checkout after service each excluded explicitly rather than by omission? [Scope, Spec §Out of Scope]
- [x] CHK070 Are the canonical terms `Service Record`, `Under Repair`, `Open`, `Closed`, `Vendor`, `Custodian`, and `Checkout` used consistently, with `Assignment` absent and automatic custody restoration never implied by any label or message? [Consistency, Spec §FR-020, §Domain Alignment]

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


## Findings — All Resolved 2026-08-12

**Finding 1 — CHK013: no actor could correct a closed record.** FR-026 requires
the sent and return dates to be "correctable" while FR-019 forbids changing a
Service Record through a direct record edit. Nothing reconciled the two, so a
mistaken cost, outcome, bill reference, or date on a closed record had no lawful
correction path — the only mechanism that could reach it was the Admin-only
direct edit FR-019 prohibits. **Resolved** by FR-031, which makes correction a
named lifecycle operation requiring `asset_custody_manage`, retains the
superseded value with its actor and time, and forbids reopening the record.

**Finding 2 — CHK014: bill document permissions were inherited implicitly.**
FR-028 requires a bill reference and attached document whenever cost exceeds
zero, but no requirement stated who may attach, replace, or read it — leaving it
to be read across from B2's Asset-document permissions. **Resolved** by FR-032:
attaching or replacing requires `asset_custody_manage`, the same permission that
closes the record the document evidences; reading follows the Service Record
visibility in ALR-002 rather than the Asset's, because the document evidences the
repair rather than the Asset.

**Finding 3 — CHK033: the single-open invariant existed only as a side effect.**
§Assumptions recorded that "One Asset has at most one `Open` Service Record,
because opening requires the" status precondition — an emergent consequence, not
a rule. Any future change to that precondition would have removed the invariant
silently. **Resolved** by FR-033, which states it directly and requires it to
hold under simultaneous attempts, with the row-lock conformance gap recorded.

**Finding 4 — CHK038 and CHK039: two Vendor questions were unanswered.**
Neither the protection of a referenced Vendor from deletion nor a Vendor change
on an open record was specified or assigned. **Resolved** by FR-034: the Vendor is
fixed at opening, forwarding to a different repairer is recorded as a new Service
Record rather than an in-place swap, and deletion protection is assigned to B6 as
Vendor administration. Both follow from rules already present — `CONTEXT.md`
defines a Service Record as one repair event and FR-019 forbids direct editing,
which together already excluded a Vendor swap.

## Structural Note — Evidence Classification

B5 defined four categories but used two more on its requirements —
**Stakeholder-confirmed** (carrying the whole 2026-08-05 clarification) and
**Governance requirement** — plus qualified forms such as "accepted atomicity"
and "accepted lifecycle ownership". No item in this checklist tests for it; the
same coverage gap exists in B4's checklist and is absent from B1's, B2's, B6's,
B8's, and B3's, all of which do test it. Fixed here anyway: both labels are now
defined, along with the qualifier and compound conventions.
