# Brownfield Baseline Acceptance Checklist: B7 Warranty, AMC, and Expiry Actions

**Purpose**: Formal stakeholder and reviewer gate for determining whether the B7 requirements are complete, clear, consistent, measurable, and evidence-qualified before the Draft baseline is accepted
**Created**: 2026-08-05
**Feature**: [B7 specification](../spec.md)

**Note**: This checklist validates the requirements as written. It is not an
implementation test plan. Mark an item complete only when the specification
answers it unambiguously and traceably; implementation behavior alone is not
sufficient. Baseline acceptance requires every item to be checked or covered by
an explicit stakeholder-approved waiver recorded in the specification.

## Warranty-versus-AMC Terminology and Distinction

- [ ] CHK001 Are Warranty and AMC defined as separate contracts with independent dates, parties, and rules, with no requirement deriving one from the other? [Clarity, Spec §Domain Alignment, §FR-001, §FR-002]
- [ ] CHK002 Is the absence of any Warranty status, renewal, or discontinuation workflow stated as a requirement rather than left as an unmentioned omission? [Completeness, Spec §FR-003, §AS-002]
- [ ] CHK003 Is the requirement that AMC coverage be queryable data rather than only an uploaded document stated with its consequence for alerts and reporting? [Traceability, Spec §FR-004, §AS-005]
- [ ] CHK004 Are `Incomplete`, `Active`, and `Ended` consistently described as AMC contract states and never as Asset statuses across scenarios, requirements, and entities? [Consistency, Spec §FR-005, §AS-038, §Key Entities]
- [ ] CHK005 Is the rejected `Assignment` terminology on the Warranty panel identified as owned by Draft B2 and `ROADMAP.md` C3, so B7 neither adopts nor silently inherits it? [Scope, Spec §OBS-AS-002]

## No-AMC, Incomplete, and Flag Semantics

- [ ] CHK006 Is the derived AMC flag rule stated unambiguously for all four situations — latest contract `Active`, `Incomplete`, `Ended`, and no contract at all? [Clarity, Spec §FR-006, §AS-006]
- [ ] CHK007 Is the accepted consequence explicit that an Asset which never had an AMC and one whose AMC was deliberately ended are not required to be distinguishable? [Clarity, Spec §FR-006, §AS-009]
- [ ] CHK008 Is the divergence from `CONTEXT.md`'s deliberate-decision definition of the flag surfaced as a required glossary reconciliation with a named owner, rather than absorbed into the requirement? [Conflict, Spec §FR-029, §U-001]
- [ ] CHK009 Does the specification state what AMC data-completeness reporting may and may not claim while FR-006 stands, and define what that reporting covers? [Ambiguity, Spec §FR-029]
- [ ] CHK010 Is the `Incomplete` state defined as exactly one contract with empty dates that is visibly flagged, including the outcome when dates are supplied later? [Completeness, Spec §FR-007, §FR-008, §AS-007, §AS-008]
- [ ] CHK011 Is the rule for selecting an Asset's current contract stated as a requirement, given that a newly created `Incomplete` contract must outrank an older fully dated `Ended` one? [Clarity, Spec §AS-010, §CAND-003]
- [ ] CHK012 Is it specified whether an `Incomplete` AMC should be chased after some period, or is that deferral recorded with its consequence? [Gap, Spec §FR-007, §Remaining Evidence-Led Confirmation Items]
- [ ] CHK013 Is the status of the Asset-form AMC flag control resolved — a derived value cannot be set, so the requirement should say whether the control is removed or redefined? [Gap, Spec §FR-006, §OBS-AS-006, §CAND-008]

## Date and Vendor Validation

- [ ] CHK014 Are the initial AMC entry rules stated identically to renewal's — both dates or neither, parseable dates, end after start — with the rejection outcome specified? [Consistency, Spec §FR-030, §FR-010]
- [ ] CHK015 Is the Warranty ordering rule complete, including that either date may stand alone and that neither is tied to purchase or arrival dates? [Completeness, Spec §FR-031]
- [ ] CHK016 Is the consequence specified when only a Warranty start date is recorded, given that no expiry alert can be derived without an end date? [Gap, Spec §FR-031, §FR-016]
- [ ] CHK017 Is the AMC Vendor requirement unambiguous about when it binds — required on any dated contract, optional while `Incomplete`, required at the moment dates are supplied? [Clarity, Spec §FR-032]
- [ ] CHK018 Is it explicit that the AMC Vendor need not equal the Asset's Procurement Vendor, and is that traced to `CONTEXT.md`'s different-vendor observation? [Traceability, Spec §FR-032, §Domain Alignment]
- [ ] CHK019 Is the treatment of existing dated contracts that carry no Vendor specified, so the new requirement has a defined effect on records created before it? [Gap, Spec §FR-032, §CAND-009]
- [ ] CHK020 Is the Vendor selection constrained to managed B6 identities including the exclusion of flagged legacy Vendors, rather than only described as "managed"? [Dependency Coverage, Spec §FR-032, §Relevant Decisions]
- [ ] CHK021 Is the protected-deletion expectation for a Vendor referenced by an AMC contract stated or assigned to B6, now that dated contracts must reference one? [Gap, Spec §FR-032, §Edge Cases]

## Terminal-Asset and Lifecycle Restrictions

- [ ] CHK022 Is the renewal restriction on terminal Assets stated with its rationale and its zero-mutation outcome? [Clarity, Spec §FR-011, §AS-014]
- [ ] CHK023 Is there an accepted requirement that End Support is also restricted on terminal Assets, or is the asymmetry with renewal deliberately accepted? The conformance table currently cites FR-011, which governs renewal only. [Conflict, Spec §U-006 row 5, §OBS-AS-008, §FR-011]
- [ ] CHK024 Is the exclusion of terminal Assets from expiry alerts stated as a requirement, and is its derivation from Draft B2 rather than `CONTEXT.md` disclosed? [Assumption/Gap, Spec §FR-020, §AS-030, §Remaining Evidence-Led Confirmation Items]
- [ ] CHK025 Is it specified whether renewal is permitted when an Asset has no current contract — the path that would restart AMC coverage after a deliberate End Support? [Gap, Spec §FR-009, §FR-012]
- [ ] CHK026 Is the assumption that an Asset has at most one current AMC contract stated as an enforceable invariant or explicitly recorded as unmodelled? [Assumption, Spec §Assumptions]
- [ ] CHK027 Are concurrent renewal or End Support attempts on the same Asset addressed, or is the absence of a concurrency rule recorded? [Gap, Spec §ALR-002, §FR-014]

## Renewal, End Support, History, and Reasons

- [ ] CHK028 Are all renewal effects required to commit atomically — superseding closure, new contract, Vendor, state, and required audit entry — with no interval in which the Asset has neither contract? [Atomicity, Spec §FR-014, §ALR-002, §AS-016]
- [ ] CHK029 Is history preservation stated as append-only, with each superseded contract retaining its own Vendor, dates, and state unchanged? [Completeness, Spec §FR-034, §ALR-004, §FR-015]
- [ ] CHK030 Is the separation between renewal's supersede marker and the operator's End Support reason specified structurally, so the two are distinguishable without reading their text? [Clarity, Spec §FR-034, §AS-022, §CAND-012]
- [ ] CHK031 Is the mandatory End Support reason requirement complete, including the rejection outcome for a blank reason and for an Asset with no current contract? [Acceptance Criteria, Spec §FR-012, §AS-018, §AS-019]
- [ ] CHK032 Is any constraint on reason content specified — minimum substance or controlled vocabulary — or is free text explicitly accepted? [Ambiguity, Spec §FR-012, §OBS-AS-009]
- [ ] CHK033 Is the rule that a contract never becomes discontinued by its end date passing stated as a requirement, with lapsed-but-unattended defined as a distinct reportable condition? [Clarity, Spec §FR-013, §AS-021]
- [ ] CHK034 Is End Support on an `Incomplete` contract — cancelling a planned AMC before dates were entered — covered as an accepted outcome? [Coverage, Spec §FR-012, §AS-020]
- [ ] CHK035 Is the requirement that no automatic process may set a contract `Ended` stated, so no scheduler, import, or cleanup path can substitute for the human decision? [Security/Clarity, Spec §ALR-005, §ALR-006]

## Expiry Triggers, Recipients, and Channel

- [ ] CHK036 Are the current exact 30/15/7-day threshold behaviors kept separate from prospective catch-up behavior owned by CHG-B7-01? [Consistency, Spec §FR-016, §FWD-B7-001]
- [ ] CHK037 Is the silence requirement complete for off-threshold dates, `Ended` contracts, Assets with no current AMC, and terminal Assets? [Negative Coverage, Spec §FR-019, §FR-020, §AS-026, §AS-028]
- [ ] CHK038 Is the recipient rule stated as a permission grant rather than a Role display name, with the named Roles retained as the business description? [Clarity, Spec §FR-018, §Assumptions]
- [ ] CHK039 Is the "IT Manager grant" used for AMC decision notifications identified as a specific permission code, given that no such code currently exists and only a Role name does? [Gap, Spec §FR-021, §CAND-018]
- [ ] CHK040 Is the accepted breadth of alert recipients explicit, including that Admin and custom Roles holding the code are intended recipients? [Completeness, Spec §FR-018, §CAND-015]
- [ ] CHK041 Is the in-app-only channel decision stated for this version with email explicitly deferred and not inferred from SMTP Settings? [Clarity, Spec §FR-035, §CAND-020]
- [ ] CHK042 Is the residual risk of in-app-only delivery — a recipient who does not open the application inside the alert window — recorded rather than left implicit? [Assumption, Spec §FR-035, §Assumptions]
- [ ] CHK043 Is the requirement that a dashboard or report cannot satisfy proactive push stated, and is it consistent with the B9 boundary? [Consistency, Spec §FR-017, §Out of Scope]
- [ ] CHK044 Is it specified whether an alert must identify which coverage type and which contract it refers to, given that an Asset may have a Warranty and an AMC expiring in the same window? [Gap, Spec §Edge Cases, §Remaining Evidence-Led Confirmation Items]

## Scheduling, Deduplication, and Failure Recovery

- [ ] CHK045 Is development-server-only scheduling classified as current evidence and explicitly not presented as reliable production delivery? [Clarity, Spec §OBS-AS-014, §FWD-B7-001]
- [ ] CHK046 Is exactly-one production execution assigned only to CHG-B7-01 rather than treated as B7 current behavior? [Scope, Spec §FWD-B7-001]
- [ ] CHK047 Is operator-visible run health assigned only to CHG-B7-01? [Scope, Spec §FWD-B7-001]
- [ ] CHK048 Is organizational-timezone delivery assigned only to CHG-B7-01? [Scope, Spec §FWD-B7-001]
- [ ] CHK049 Is once-only delivery assigned only to CHG-B7-01? [Scope, Spec §FWD-B7-001]
- [ ] CHK050 Is coverage-date re-arming excluded from B7 acceptance and left to CHG-B7-01 review? [Boundary, Spec §FWD-B7-001]
- [ ] CHK051 Is downtime catch-up assigned only to CHG-B7-01? [Scope, Spec §FWD-B7-001]
- [ ] CHK052 Is the relationship between catch-up and once-only delivery reviewed in CHG-B7-01 rather than B7? [Boundary, Spec §FWD-B7-001]
- [ ] CHK053 Is production run-health measurability excluded from B7 and retained in CHG-B7-01? [Boundary, Spec §FWD-B7-001]
- [ ] CHK054 Does B7 preserve the stakeholder decision and reciprocal link without prescribing an implementation mechanism? [Traceability, Spec §Extended by, §U-002]

## Notifications and AuditLog

- [ ] CHK055 Is the trigger matrix complete for both expiry thresholds, both AMC decisions, initial entry, rejections, and routine reads, with every deliberate no-notification case stated as deliberate? [Completeness, Spec §FR-024, §B7 Notification and Audit Trigger Matrix]
- [ ] CHK056 Are notification destinations specified as resolvable outcomes, covering both the unresolvable alert destination and the entirely absent AMC decision destination? [Clarity, Spec §AS-033, §CAND-016, §CAND-018]
- [ ] CHK057 Is the required audit content defined per event, including previous and new contract dates and state, the reason where one applies, and the actor? [Completeness, Spec §FR-025, §B7 Notification and Audit Trigger Matrix]
- [ ] CHK058 Is the boundary between B7's own audit entries and the Draft B2 Asset-mutation entry that initial AMC entry already produces stated without double-counting or gaps? [Dependency Consistency, Spec §FR-025, §OBS-AS-021]
- [ ] CHK059 Is audit atomicity stated consistently — required-audit failure rolls back the owning AMC action, notification failure does not roll back completed work? [Reliability/Consistency, Spec §ALR-007, §AS-034, §AS-035, §SC-012]
- [ ] CHK060 Are B8-owned delivery, read state, retry, deduplication of recipient records, access, privacy, and retention clearly separated from B7-owned trigger selection? [Dependency Coverage, Spec §FR-024, §FR-035, §Out of Scope]
- [ ] CHK061 Is the requirement that the expiry check mutate nothing stated, so an alert can never be mistaken for a state change? [Security/Clarity, Spec §ALR-006]

## Dashboard and Report Boundaries

- [ ] CHK062 Is B9 ownership of coverage KPIs, timeline charts, the Warranty-expiring-soon list, and both expiry reports stated so that none of them defines a B7 requirement? [Scope, Spec §Out of Scope]
- [ ] CHK063 Is it explicit that Dashboard and report surfaces consume B7 data and cannot satisfy the proactive push obligation? [Consistency, Spec §FR-017, §Out of Scope]
- [ ] CHK064 Are the current report behaviors that contradict B7 requirements — the always-empty AMC Vendor column and Warranty counts that include terminal Assets — recorded as evidence with their owning baseline identified? [Traceability, Spec §OBS-AS-024, §OBS-AS-025]

## Evidence Integrity, Scope, and Decision Closure

- [ ] CHK065 Is every accepted requirement traceable to `CONTEXT.md`, an accepted or Draft dependency identifier, or the 2026-08-05 stakeholder clarification, with no requirement resting on implementation evidence alone? [Traceability, Spec §FR-027, §SC-014]
- [ ] CHK066 Is the absence of any governing ADR stated, so the unusually heavy reliance on `CONTEXT.md` is visible to reviewers? [Assumption, Spec §Assumptions]
- [ ] CHK067 Are all five resolved decisions U-001 through U-005 recorded with their answers, the requirements they produced, and the conformance gaps they created? [Completeness, Spec §Unresolved Conflicts, §SC-013]
- [ ] CHK068 Are the two remaining acceptance preconditions in FR-028 — the `CONTEXT.md` reconciliation and confirmation of the derived FR-020 — stated as blocking, with owners? [Clarity, Spec §FR-028, §FR-029]
- [ ] CHK069 Are all 18 conformance gaps in U-006 stated as findings that leave their contradicted requirement intact, rather than as grounds for weakening it? [Consistency, Spec §U-006]
- [ ] CHK070 Is the coverage of the 18 cited tests accurately bounded, including the explicit statement of what has no automated coverage? [Traceability, Spec §Verified Behavior Evidence]
- [ ] CHK071 Is the distinction between Draft B2 and the Draft status of B1, B5, B6, and B8 stated accurately everywhere those baselines are cited as sources? [Traceability, Spec §Specification Lineage, §Assumptions]
- [ ] CHK072 Are the retention consequences for AMC history when an Asset is deleted either specified or explicitly assigned to B2? [Gap, Spec §Edge Cases, §Remaining Evidence-Led Confirmation Items]
- [ ] CHK073 Is the exclusion of Warranty renewal, extended-warranty products, AMC cost and payment terms, claim workflows, and automatic contract changes explicit rather than by omission? [Scope, Spec §Out of Scope]
- [ ] CHK074 Is the B5 boundary stated in both directions — a Service Record is not a coverage claim, and B7 infers no coverage from repair activity? [Dependency Consistency, Spec §FR-026, §Out of Scope]

## Notes

- This is a formal baseline-acceptance gate for specification reviewers and
  stakeholders before B7 leaves `Draft`.
- Items marked `[Gap]`, `[Assumption]`, `[Ambiguity]`, or `[Conflict]`
  intentionally expose requirements that may still need a stakeholder decision
  or an explicit scope exclusion. They are not defects in the clarification
  session; the five mandated B7 decisions were closed on 2026-08-05.
- CHK008, CHK009, and CHK068 track the `CONTEXT.md` reconciliation that FR-029
  makes an acceptance precondition. CHK023, CHK039, and CHK050 are the three
  internal inconsistencies this review is most likely to surface.
- Record supporting requirement identifiers, review findings, or approved
  waivers inline before checking an item.
- The absence of `plan.md` is not evaluated here because this checklist reviews
  the brownfield baseline requirements before implementation planning. For the
  same reason `check-prerequisites.ps1 -Json` reports a missing plan; that is
  expected for a documentation-only baseline.
- The separate `requirements.md` checklist validates specification quality. This
  checklist is the stakeholder acceptance gate and is deliberately stricter.
