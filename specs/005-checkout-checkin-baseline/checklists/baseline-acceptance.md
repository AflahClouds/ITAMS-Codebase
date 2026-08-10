# Brownfield Baseline Acceptance Checklist: AS-BUILT Checkout and Check-in Baseline

**Purpose**: Determine whether the B3 requirements are complete, explicit,
consistent, traceable, evidence-backed, and ready for stakeholder acceptance.
**Created**: 2026-08-04
**Feature**: [spec.md](../spec.md)

**Audience and timing**: Stakeholders and maintainers reviewing the Draft before
baseline acceptance.

**Note**: This checklist evaluates the quality of the written requirements. It
does not test whether the current application conforms to them. Mark an item
complete only when the specification itself supplies clear, authoritative, and
testable text or an explicit scope decision.

## Baseline Scope and Authority

- [ ] CHK001 Is B3's scope boundary explicit that it owns Checkout and check-in while Transfer, Service Record internals, Asset-register rules, and shared Notification/AuditLog infrastructure belong to named sibling baselines? [Completeness, Spec §Specification Lineage, §Dependencies, §Out of Scope]
- [ ] CHK002 Are accepted-intent, stakeholder-confirmed, test-verified, implementation-only, and unresolved classifications applied consistently so that no code or test observation is promoted to product intent? [Consistency, Spec §Evidence Classification, §FR-021, §Baseline Evidence]
- [ ] CHK003 Are the Draft B2 requirements that B3 depends upon cited by identifier rather than referenced in general terms, with an explicit statement that B3 does not reopen them? [Traceability, Spec §Relevant Decisions, §Accepted Intent, §Assumptions]
- [ ] CHK004 Is the dependency on the Draft B8 baseline distinguished from an accepted dependency, so shared delivery and storage rules are not treated as settled? [Clarity, Spec §Relevant Decisions, §FR-020, §FR-027]
- [ ] CHK005 Does the specification state that it is documentation-only and changes no application code, tests, routes, interfaces, or configuration? [Clarity, Spec §Assumptions, §Out of Scope]

## Actors and Backend Permissions

- [ ] CHK006 Is the accepted actor set for Checkout and check-in stated by named Role and by permission code, with every other named Role explicitly denied? [Completeness, Spec §ALR-001, §ALR-002, §Accepted Checkout Actor and Permission Contract]
- [ ] CHK007 Is read access to Checkout records separated from custody-operation access, with the required permission named for each? [Clarity, Spec §ALR-001, §Accepted Checkout Actor and Permission Contract]
- [ ] CHK008 Is it explicit that being the Custodian or the Checkout User grants no permission and does not enable a User to perform their own check-in? [Coverage, Spec §ALR-006, §AS-014]
- [ ] CHK009 Is backend enforcement stated as authoritative, with hidden frontend controls expressly insufficient as an authorization control? [Security, Spec §ALR-003, §AS-018]
- [ ] CHK010 Are eligibility rules for who may be a Checkout User specified, including whether a disabled User or a User with no Role qualifies? [Gap, Spec §Accepted Checkout Actor and Permission Contract, §CAND-013]
- [ ] CHK011 Is direct editing or deletion of a Checkout record excluded from the accepted contract rather than tolerated as an administrative convenience? [Consistency, Spec §ALR-005, §U-006]
- [ ] CHK012 Is the permission model's Admin and superuser bypass acknowledged without being converted into an accepted exception to the custody contract? [Evidence, Spec §Accepted Checkout Actor and Permission Contract, §CAND-011]

## Available-to-Assigned and Check-in Transitions

- [ ] CHK013 Is the accepted source state for Checkout stated unambiguously as `Available`, with every other status rejected? [Clarity, Spec §FR-001, §FR-008, §AS-015]
- [ ] CHK014 Is the accepted outcome of check-in stated as `Available` with the Checkout closed as returned and a return time recorded? [Clarity, Spec §FR-002, §FR-013, §AS-007]
- [ ] CHK015 Is the absence of an approval gate, a `Pending` state, and a second approving actor stated as a positive requirement rather than only as a contrast with Transfer? [Completeness, Spec §FR-003, §AS-002]
- [ ] CHK016 Is it explicit that `Assigned` may be entered and left only through the owning operation, and that a direct Asset edit is rejected in both directions? [Consistency, Spec §FR-007, §ALR-005, §AS-004, §AS-008]
- [ ] CHK017 Is atomicity required across the record change, status change, Custodian effect, and department effect together, with no user-visible partial state? [Completeness, Spec §FR-011, §AS-006, §AS-009]
- [ ] CHK018 Is it explicit that a closed Checkout is never reopened and that resuming custody always requires a fresh Checkout? [Clarity, Spec §FR-012, §AS-010, §AS-024]
- [ ] CHK019 Is the effect of C1 on the eligibility boundary stated, so reviewers know the source-state contract is incomplete until Store-to-User issuance is decided? [Conflict, Spec §U-005, §FR-022]

## Custodian, Department, and Condition Effects

- [ ] CHK020 Is the Custodian effect stated for both directions — set to the Checkout User on Checkout, cleared on check-in? [Completeness, Spec §FR-004, §AS-001, §AS-007]
- [ ] CHK021 Is the department effect at Checkout complete for a Checkout User who has a department and for one who does not? [Coverage, Spec §FR-006, §AS-003]
- [ ] CHK022 Is department clearing at check-in stated as a requirement and reconciled with Draft B2 FR-015 rather than with current behavior? [Consistency, Spec §FR-023, §AS-011, §U-001]
- [ ] CHK023 Is the mandatory status of the return condition unambiguous, with no default value and an explicit rejection outcome when it is omitted? [Clarity, Spec §FR-024, §AS-012]
- [ ] CHK024 Is the canonical condition set enforced for the return condition, with a rejection leaving Asset status, Custodian, department, and condition unchanged? [Completeness, Spec §FR-010, §AS-017]
- [ ] CHK025 Is the condition-history requirement objectively applicable, stating which check-ins produce an Asset condition-inspection row? [Measurability, Spec §FR-025, §AS-032]
- [ ] CHK026 Is the checkout condition's treatment specified — its source, whether it is validated against the canonical set, and whether it affects the Asset's own condition? [Gap, Spec §CAND-003, §Edge Cases]
- [ ] CHK027 Is Asset status stated as authoritative for availability, so the presence or absence of a Custodian never by itself determines Checkout eligibility? [Clarity, Spec §FR-005]

## Remarks, Expected Return, and Overdue

- [ ] CHK028 Are intake remarks and return remarks defined as distinct retained values that a check-in cannot overwrite or discard? [Clarity, Spec §FR-014, §AS-029]
- [ ] CHK029 Is the mandatory-return-remarks rule objectively testable, including the condition severity ordering that "worse than" depends upon? [Measurability, Ambiguity, Spec §FR-014, §Assumptions, §Edge Cases]
- [ ] CHK030 Are the expected-return-date rules complete for optionality, accepted values, and rejection of a date earlier than the current date? [Completeness, Spec §FR-026, §AS-027]
- [ ] CHK031 Is Overdue defined as a derived Checkout state that never appears as an Asset status and never by itself blocks another custody operation? [Clarity, Spec §FR-026, §AS-036, §AS-038, §Key Entities]
- [ ] CHK032 Are Overdue evaluation timing, timezone basis, and deduplication of repeated Overdue Notifications either specified or explicitly delegated to a named owner? [Gap, Spec §Assumptions, §FR-026]
- [ ] CHK033 Is the dependence of proactive Overdue delivery on the unresolved C5 scheduling decision stated as a disclosed, accepted risk rather than left implicit? [Evidence, Spec §Assumptions, §Edge Cases]

## Invalid, Repeated, and Interrupted Operations

- [ ] CHK034 Is every rejection case enumerated — ineligible Asset status, already closed Checkout, missing return condition, noncanonical condition, missing return remarks, past expected return date, and missing permission? [Completeness, Spec §User Story 3, §AS-015, §AS-016, §AS-017, §AS-027, §AS-029, §AS-033]
- [ ] CHK035 Does every rejection state a no-mutation outcome across Asset status, Custodian, department, condition, and Checkout records? [Consistency, Spec §ALR-004, §AS-013, §SC-004]
- [ ] CHK036 Is a repeated check-in against an already closed Checkout explicitly rejected rather than treated as harmlessly idempotent? [Edge Case, Spec §FR-009, §AS-016]
- [ ] CHK037 Are both interrupting operations named, with closure required to occur atomically inside the interrupting operation? [Completeness, Spec §FR-015, §FR-016, §ALR-007, §AS-022, §AS-023]
- [ ] CHK038 Is the interrupted closure's exception from the mandatory-return-condition rule stated in both places, so FR-024 and FR-028 cannot be read as contradictory? [Consistency, Spec §FR-024, §FR-028, §Edge Cases]
- [ ] CHK039 Is a closed-as-interrupted record required to remain distinguishable from a check-in and to remain visible in the Asset's custody history? [Clarity, Spec §FR-017, §FR-028, §AS-025, §AS-034]
- [ ] CHK040 Is behavior for concurrent Checkout attempts and for more than one open Checkout per Asset either specified or explicitly named as an open question with an owner? [Gap, Spec §Edge Cases, §Out of Scope]
- [ ] CHK041 Is retention of Checkout history on Asset or User deletion either specified or explicitly assigned to the owning baseline? [Gap, Spec §Edge Cases, §Out of Scope]

## Notification Requirements

- [ ] CHK042 Is the recipient set stated for each notifying event — Checkout, check-in, interrupted closure, and Overdue — with no unlisted recipient implied? [Completeness, Spec §FR-020, §Accepted Trigger Matrix]
- [ ] CHK043 Is each Notification's message meaning defined by intent rather than by reproducing current message text? [Clarity, Spec §Accepted Trigger Matrix, §CAND-010]
- [ ] CHK044 Is the destination requirement stated as resolving to the referenced Asset's detail surface, with the current non-resolving destination recorded as a gap rather than accepted? [Traceability, Spec §FR-020, §U-006, §Edge Cases]
- [ ] CHK045 Is the ownership boundary explicit that B3 owns trigger, recipients, meaning, and destination while B8 owns delivery, retry, read state, access, and retention? [Consistency, Spec §FR-020, §Domain Alignment]
- [ ] CHK046 Is the overlap between B3's interrupted-closure Notification and B5's service Notification to the same User acknowledged, with a named owner for resolving it? [Edge Case, Spec §Accepted Trigger Matrix, §Edge Cases]
- [ ] CHK047 Is failed delivery to a recipient with no reachable profile treated as a failure under the shared contract rather than as an accepted silent outcome? [Coverage, Spec §Edge Cases]
- [ ] CHK048 Are the events that deliberately send no Notification listed explicitly, so silence is a recorded decision rather than an omission? [Completeness, Spec §Accepted Trigger Matrix]

## Audit Effects

- [ ] CHK049 Is the required audit event set exhaustive across successful, rejected, permission-denied, and interrupted operations? [Completeness, Spec §FR-027, §ALR-008, §Accepted Trigger Matrix]
- [ ] CHK050 Is the required content of each entry specified by concept — operator or attempting actor, Asset, Checkout User, status/Custodian/department effects, condition, and reason on rejection? [Completeness, Spec §FR-027, §AS-028, §AS-031, §AS-033, §AS-035]
- [ ] CHK051 Can "exactly one entry per event" be applied objectively to retried submissions, duplicate requests, and an interrupting operation that closes more than one Checkout? [Measurability, Spec §AS-035, §SC-012, §Edge Cases]
- [ ] CHK052 Is it required that a denied attempt be audited without exposing Checkout or Asset data to the denied actor? [Security, Spec §ALR-008, §AS-033]
- [ ] CHK053 Is the boundary with B2's terminal-transition audit entry explicit, so a closure caused by a terminal transition is neither duplicated nor omitted? [Consistency, Spec §Accepted Trigger Matrix, §FR-016]
- [ ] CHK054 Is shared AuditLog storage, access, filtering, and retention left to B8 without B3 restating or contradicting it? [Traceability, Spec §FR-027, §Out of Scope]
- [ ] CHK055 Is the atomicity relationship between a required audit entry and its business action stated rather than left to the reader? [Clarity, Spec §ALR-008]

## Endpoint and Interface Behavior

- [ ] CHK056 Are the accepted read, create, and check-in operations described by observable behavior rather than by current route shapes or payload names? [Clarity, Spec §User Story 4, §AS-019, §AS-020]
- [ ] CHK057 Is the full create-then-check-in round trip stated as an acceptance outcome with an identifiable final record state? [Measurability, Spec §AS-020, §SC-003]
- [ ] CHK058 Are list scoping, ordering, filtering, and pagination either accepted as requirements or explicitly retained as current-state candidates? [Gap, Spec §CAND-012, §OBS-AS-022, §OBS-AS-023]
- [ ] CHK059 Is the Asset's custody history required to retain every Checkout, including those closed by an interrupting operation? [Coverage, Spec §FR-017, §AS-021]
- [ ] CHK060 Are frontend surface behaviors kept as implementation-only observations rather than treated as accepted requirements, given the absence of any frontend test harness? [Evidence, Spec §FR-021, §Assumptions, §CAND-013, §CAND-014]
- [ ] CHK061 Is the required content of a Checkout record stated by concept, so that field naming remains subject to the terminology requirement? [Consistency, Spec §FR-013, §FR-018]

## Canonical Terminology

- [ ] CHK062 Is `Checkout` used consistently throughout, with `Assignment` appearing only where it is named as rejected or recorded as a conformance gap? [Consistency, Spec §FR-018, §AS-005]
- [ ] CHK063 Does the terminology requirement extend to record field names and labels implying an approval step, not only to page titles and history panels? [Coverage, Spec §FR-018, §Key Entities, §U-006]
- [ ] CHK064 Is the distinction between the rejected term `Assignment` and the canonical status value `Assigned` explicit enough to prevent an over-correction? [Ambiguity, Spec §Canonical Terms]
- [ ] CHK065 Are Overdue, intake remarks, return remarks, interrupted closure, custody operator, and Checkout User each defined before first use? [Clarity, Spec §Canonical Terms, §Key Entities]
- [ ] CHK066 Is "self-service" constrained so the absence of an approval gate is never described as employee self-service? [Clarity, Spec §Canonical Terms, §FR-019]

## Evidence Citations and Traceability

- [ ] CHK067 Does every accepted requirement cite `CONTEXT.md`, an ADR, an accepted specification identifier, or the dated stakeholder clarification? [Traceability, Spec §Requirements, §Accepted Intent]
- [ ] CHK068 Is every test-verified claim tied to a named automated test, with the verification date and result recorded? [Evidence, Spec §Verified Behavior Evidence]
- [ ] CHK069 Is every implementation-only observation tied to a specific repository path? [Evidence, Spec §Implementation-Only Observations]
- [ ] CHK070 Are the areas with no automated coverage listed explicitly rather than left to inference from the tests that do exist? [Gap, Spec §Verified Behavior Evidence]
- [ ] CHK071 Does each of the seven clarification answers trace to at least one requirement and at least one acceptance scenario? [Traceability, Spec §Clarifications, §Requirements, §User Scenarios]
- [ ] CHK072 Is each conformance gap mapped to the requirement it violates and to its current-state record? [Traceability, Spec §U-006]
- [ ] CHK073 Are derived assumptions — notably the condition severity ordering — flagged as derived rather than sourced, with the effect of confirming them stated? [Evidence, Spec §Assumptions]

## Employee Self-Service Exclusion

- [ ] CHK074 Is employee self-service Checkout excluded as deferred future scope with its authoritative source cited? [Clarity, Spec §FR-019, §Out of Scope]
- [ ] CHK075 Is the exclusion consistent across canonical terms, requirements, authorization rules, and out-of-scope text, with no scenario implying an employee-initiated Checkout? [Consistency, Spec §Canonical Terms, §FR-019, §ALR-006, §AS-014]
- [ ] CHK076 Is Transfer excluded except for the stated distinction, and Service Record excluded except for the two named integration boundaries? [Completeness, Spec §Out of Scope, §FR-012, §FR-015]

## Acceptance Criteria and Baseline Readiness

- [ ] CHK077 Do the measurable outcomes collectively cover actors, transitions, custody effects, rejections, remarks, overdue behavior, notifications, audit, terminology, and evidence discipline without substituting implementation observations for acceptance criteria? [Acceptance Criteria, Spec §SC-001–SC-014]
- [ ] CHK078 Is C1 identified as the only remaining acceptance blocker, with U-001 through U-004 shown as resolved and dated? [Readiness, Spec §FR-022, §Unresolved Conflicts]
- [ ] CHK079 Does the Draft avoid weakening any accepted requirement to match current behavior, keeping every divergence in the conformance-gap register instead? [Readiness, Spec §U-006, §Assumptions]
- [ ] CHK080 Is the lineage metadata complete and reciprocal, so a future change to this baseline can be linked back after acceptance? [Traceability, Spec §Specification Lineage]

## Notes

- Check items off as completed: `[x]`.
- Record findings inline with links to the relevant specification section or
  owning baseline.
- A checked item means the written requirements pass that quality gate; it does
  not mean the current implementation conforms. Implementation divergence is
  tracked separately in the specification's conformance-gap register (U-006).
- Any unresolved item in this formal acceptance checklist blocks changing the
  B3 status from `Draft` to accepted.
- C1 remains open independently of this checklist. Even a fully checked list
  does not authorize acceptance while U-005 is unresolved.
