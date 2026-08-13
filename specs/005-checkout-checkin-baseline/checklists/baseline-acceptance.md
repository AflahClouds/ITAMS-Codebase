# Brownfield Baseline Acceptance Checklist: AS-BUILT Checkout and Check-in Baseline

**Purpose**: Determine whether the B3 requirements are complete, explicit,
consistent, traceable, evidence-backed, and ready for stakeholder acceptance.
**Created**: 2026-08-04
**Executed**: 2026-08-12 — 75 of 80 pass on first execution; all 5 findings resolved the same day. 80 of 80 now closed, and no decision gate remains.
**Feature**: [spec.md](../spec.md)

**Audience and timing**: Stakeholders and maintainers reviewing the Draft before
baseline acceptance.

**Note**: This checklist evaluates the quality of the written requirements. It
does not test whether the current application conforms to them. Mark an item
complete only when the specification itself supplies clear, authoritative, and
testable text or an explicit scope decision.

## Baseline Scope and Authority

- [x] CHK001 Is B3's scope boundary explicit that it owns Checkout and check-in while Transfer, Service Record internals, Asset-register rules, and shared Notification/AuditLog infrastructure belong to named sibling baselines? [Completeness, Spec §Specification Lineage, §Dependencies, §Out of Scope]
- [x] CHK002 Are accepted-intent, stakeholder-confirmed, test-verified, implementation-only, and unresolved classifications applied consistently so that no code or test observation is promoted to product intent? [Consistency, Spec §Evidence Classification, §FR-021, §Baseline Evidence] — *resolved 2026-08-12, see Finding 1*
- [x] CHK003 Are the Draft B2 requirements that B3 depends upon cited by identifier rather than referenced in general terms, with an explicit statement that B3 does not reopen them? [Traceability, Spec §Relevant Decisions, §Accepted Intent, §Assumptions]
- [x] CHK004 Is the dependency on the Draft B8 baseline distinguished from an accepted dependency, so shared delivery and storage rules are not treated as settled? [Clarity, Spec §Relevant Decisions, §FR-020, §FR-027]
- [x] CHK005 Does the specification state that it is documentation-only and changes no application code, tests, routes, interfaces, or configuration? [Clarity, Spec §Assumptions, §Out of Scope]

## Actors and Backend Permissions

- [x] CHK006 Is the accepted actor set for Checkout and check-in stated by named Role and by permission code, with every other named Role explicitly denied? [Completeness, Spec §ALR-001, §ALR-002, §Accepted Checkout Actor and Permission Contract]
- [x] CHK007 Is read access to Checkout records separated from custody-operation access, with the required permission named for each? [Clarity, Spec §ALR-001, §Accepted Checkout Actor and Permission Contract]
- [x] CHK008 Is it explicit that being the Custodian or the Checkout User grants no permission and does not enable a User to perform their own check-in? [Coverage, Spec §ALR-006, §AS-014]
- [x] CHK009 Is backend enforcement stated as authoritative, with hidden frontend controls expressly insufficient as an authorization control? [Security, Spec §ALR-003, §AS-018]
- [x] CHK010 Are eligibility rules for who may be a Checkout User specified, including whether a disabled User or a User with no Role qualifies? [Gap, Spec §Accepted Checkout Actor and Permission Contract, §CAND-013] — *resolved 2026-08-12, see Finding 2*
- [x] CHK011 Is direct editing or deletion of a Checkout record excluded from the accepted contract rather than tolerated as an administrative convenience? [Consistency, Spec §ALR-005, §U-006]
- [x] CHK012 Is the permission model's Admin and superuser bypass acknowledged without being converted into an accepted exception to the custody contract? [Evidence, Spec §Accepted Checkout Actor and Permission Contract, §CAND-011]

## Available-to-Assigned and Check-in Transitions

- [x] CHK013 Is the accepted source state for Checkout stated unambiguously as `Available`, with every other status rejected? [Clarity, Spec §FR-001, §FR-008, §AS-015]
- [x] CHK014 Is the accepted outcome of check-in stated as `Available` with the Checkout closed as returned and a return time recorded? [Clarity, Spec §FR-002, §FR-013, §AS-007]
- [x] CHK015 Is the absence of an approval gate, a `Pending` state, and a second approving actor stated as a positive requirement rather than only as a contrast with Transfer? [Completeness, Spec §FR-003, §AS-002]
- [x] CHK016 Is it explicit that `Assigned` may be entered and left only through the owning operation, and that a direct Asset edit is rejected in both directions? [Consistency, Spec §FR-007, §ALR-005, §AS-004, §AS-008]
- [x] CHK017 Is atomicity required across the record change, status change, Custodian effect, and department effect together, with no user-visible partial state? [Completeness, Spec §FR-011, §AS-006, §AS-009]
- [x] CHK018 Is it explicit that a closed Checkout is never reopened and that resuming custody always requires a fresh Checkout? [Clarity, Spec §FR-012, §AS-010, §AS-024]
- [x] CHK019 Is the effect of C1 on the eligibility boundary stated, so reviewers know the source-state contract is incomplete until Store-to-User issuance is decided? [Conflict, Spec §U-005, §FR-022]

## Custodian, Department, and Condition Effects — *see Note A*

- [x] CHK020 Is the Custodian effect stated for both directions — set to the Checkout User on Checkout, cleared on check-in? [Completeness, Spec §FR-004, §AS-001, §AS-007]
- [x] CHK021 Is the department effect at Checkout complete for a Checkout User who has a department and for one who does not? [Coverage, Spec §FR-006, §AS-003]
- [x] CHK022 Is department clearing at check-in stated as a requirement and reconciled with Draft B2 FR-015 rather than with current behavior? [Consistency, Spec §FR-023, §AS-011, §U-001]
- [x] CHK023 Is the mandatory status of the return condition unambiguous, with no default value and an explicit rejection outcome when it is omitted? [Clarity, Spec §FR-024, §AS-012]
- [x] CHK024 Is the canonical condition set enforced for the return condition, with a rejection leaving Asset status, Custodian, department, and condition unchanged? [Completeness, Spec §FR-010, §AS-017]
- [x] CHK025 Is the condition-history requirement objectively applicable, stating which check-ins produce an Asset condition-inspection row? [Measurability, Spec §FR-025, §AS-032]
- [x] CHK026 Is the checkout condition's treatment specified — its source, whether it is validated against the canonical set, and whether it affects the Asset's own condition? [Gap, Spec §CAND-003, §Edge Cases] — *resolved 2026-08-12, see Finding 3*
- [x] CHK027 Is Asset status stated as authoritative for availability, so the presence or absence of a Custodian never by itself determines Checkout eligibility? [Clarity, Spec §FR-005]

## Remarks, Expected Return, and Overdue

- [x] CHK028 Are intake remarks and return remarks defined as distinct retained values that a check-in cannot overwrite or discard? [Clarity, Spec §FR-014, §AS-029]
- [x] CHK029 Is the mandatory-return-remarks rule objectively testable, including the condition severity ordering that "worse than" depends upon? [Measurability, Ambiguity, Spec §FR-014, §Assumptions, §Edge Cases]
- [x] CHK030 Are the expected-return-date rules complete for optionality, accepted values, and rejection of a date earlier than the current date? [Completeness, Spec §FR-026, §AS-027]
- [x] CHK031 Is Overdue defined as a derived Checkout state that never appears as an Asset status and never by itself blocks another custody operation? [Clarity, Spec §FR-026, §AS-036, §AS-038, §Key Entities]
- [x] CHK032 Are Overdue evaluation timing, timezone basis, and deduplication of repeated Overdue Notifications either specified or explicitly delegated to a named owner? [Gap, Spec §Assumptions, §FR-026]
- [x] CHK033 Is the dependence of proactive Overdue delivery on the unresolved C5 scheduling decision stated as a disclosed, accepted risk rather than left implicit? [Evidence, Spec §Assumptions, §Edge Cases]

## Invalid, Repeated, and Interrupted Operations

- [x] CHK034 Is every rejection case enumerated — ineligible Asset status, already closed Checkout, missing return condition, noncanonical condition, missing return remarks, past expected return date, and missing permission? [Completeness, Spec §User Story 3, §AS-015, §AS-016, §AS-017, §AS-027, §AS-029, §AS-033]
- [x] CHK035 Does every rejection state a no-mutation outcome across Asset status, Custodian, department, condition, and Checkout records? [Consistency, Spec §ALR-004, §AS-013, §SC-004]
- [x] CHK036 Is a repeated check-in against an already closed Checkout explicitly rejected rather than treated as harmlessly idempotent? [Edge Case, Spec §FR-009, §AS-016]
- [x] CHK037 Are both interrupting operations named, with closure required to occur atomically inside the interrupting operation? [Completeness, Spec §FR-015, §FR-016, §ALR-007, §AS-022, §AS-023]
- [x] CHK038 Is the interrupted closure's exception from the mandatory-return-condition rule stated in both places, so FR-024 and FR-028 cannot be read as contradictory? [Consistency, Spec §FR-024, §FR-028, §Edge Cases]
- [x] CHK039 Is a closed-as-interrupted record required to remain distinguishable from a check-in and to remain visible in the Asset's custody history? [Clarity, Spec §FR-017, §FR-028, §AS-025, §AS-034]
- [x] CHK040 Is behavior for concurrent Checkout attempts and for more than one open Checkout per Asset either specified or explicitly named as an open question with an owner? [Gap, Spec §Edge Cases, §Out of Scope] — *resolved 2026-08-12, see Finding 4*
- [x] CHK041 Is retention of Checkout history on Asset or User deletion either specified or explicitly assigned to the owning baseline? [Gap, Spec §Edge Cases, §Out of Scope]

## Notification Requirements

- [x] CHK042 Is the recipient set stated for each notifying event — Checkout, check-in, interrupted closure, and Overdue — with no unlisted recipient implied? [Completeness, Spec §FR-020, §Accepted Trigger Matrix]
- [x] CHK043 Is each Notification's message meaning defined by intent rather than by reproducing current message text? [Clarity, Spec §Accepted Trigger Matrix, §CAND-010]
- [x] CHK044 Is the destination requirement stated as resolving to the referenced Asset's detail surface, with the current non-resolving destination recorded as a gap rather than accepted? [Traceability, Spec §FR-020, §U-006, §Edge Cases]
- [x] CHK045 Is the ownership boundary explicit that B3 owns trigger, recipients, meaning, and destination while B8 owns delivery, retry, read state, access, and retention? [Consistency, Spec §FR-020, §Domain Alignment]
- [x] CHK046 Is the overlap between B3's interrupted-closure Notification and B5's service Notification to the same User acknowledged, with a named owner for resolving it? [Edge Case, Spec §Accepted Trigger Matrix, §Edge Cases]
- [x] CHK047 Is failed delivery to a recipient with no reachable profile treated as a failure under the shared contract rather than as an accepted silent outcome? [Coverage, Spec §Edge Cases]
- [x] CHK048 Are the events that deliberately send no Notification listed explicitly, so silence is a recorded decision rather than an omission? [Completeness, Spec §Accepted Trigger Matrix]

## Audit Effects

- [x] CHK049 Is the required audit event set exhaustive across successful, rejected, permission-denied, and interrupted operations? [Completeness, Spec §FR-027, §ALR-008, §Accepted Trigger Matrix]
- [x] CHK050 Is the required content of each entry specified by concept — operator or attempting actor, Asset, Checkout User, status/Custodian/department effects, condition, and reason on rejection? [Completeness, Spec §FR-027, §AS-028, §AS-031, §AS-033, §AS-035]
- [x] CHK051 Can "exactly one entry per event" be applied objectively to retried submissions, duplicate requests, and an interrupting operation that closes more than one Checkout? [Measurability, Spec §AS-035, §SC-012, §Edge Cases]
- [x] CHK052 Is it required that a denied attempt be audited without exposing Checkout or Asset data to the denied actor? [Security, Spec §ALR-008, §AS-033]
- [x] CHK053 Is the boundary with B2's terminal-transition audit entry explicit, so a closure caused by a terminal transition is neither duplicated nor omitted? [Consistency, Spec §Accepted Trigger Matrix, §FR-016]
- [x] CHK054 Is shared AuditLog storage, access, filtering, and retention left to B8 without B3 restating or contradicting it? [Traceability, Spec §FR-027, §Out of Scope]
- [x] CHK055 Is the atomicity relationship between a required audit entry and its business action stated rather than left to the reader? [Clarity, Spec §ALR-008]

## Endpoint and Interface Behavior

- [x] CHK056 Are the accepted read, create, and check-in operations described by observable behavior rather than by current route shapes or payload names? [Clarity, Spec §User Story 4, §AS-019, §AS-020]
- [x] CHK057 Is the full create-then-check-in round trip stated as an acceptance outcome with an identifiable final record state? [Measurability, Spec §AS-020, §SC-003]
- [x] CHK058 Are list scoping, ordering, filtering, and pagination either accepted as requirements or explicitly retained as current-state candidates? [Gap, Spec §CAND-012, §OBS-AS-022, §OBS-AS-023] — *see Note B*
- [x] CHK059 Is the Asset's custody history required to retain every Checkout, including those closed by an interrupting operation? [Coverage, Spec §FR-017, §AS-021]
- [x] CHK060 Are frontend surface behaviors kept as implementation-only observations rather than treated as accepted requirements, given the absence of any frontend test harness? [Evidence, Spec §FR-021, §Assumptions, §CAND-013, §CAND-014]
- [x] CHK061 Is the required content of a Checkout record stated by concept, so that field naming remains subject to the terminology requirement? [Consistency, Spec §FR-013, §FR-018]

## Canonical Terminology

- [x] CHK062 Is `Checkout` used consistently throughout, with `Assignment` appearing only where it is named as rejected or recorded as a conformance gap? [Consistency, Spec §FR-018, §AS-005]
- [x] CHK063 Does the terminology requirement extend to record field names and labels implying an approval step, not only to page titles and history panels? [Coverage, Spec §FR-018, §Key Entities, §U-006]
- [x] CHK064 Is the distinction between the rejected term `Assignment` and the canonical status value `Assigned` explicit enough to prevent an over-correction? [Ambiguity, Spec §Canonical Terms]
- [x] CHK065 Are Overdue, intake remarks, return remarks, interrupted closure, custody operator, and Checkout User each defined before first use? [Clarity, Spec §Canonical Terms, §Key Entities]
- [x] CHK066 Is "self-service" constrained so the absence of an approval gate is never described as employee self-service? [Clarity, Spec §Canonical Terms, §FR-019]

## Evidence Citations and Traceability

- [x] CHK067 Does every accepted requirement cite `CONTEXT.md`, an ADR, an accepted specification identifier, or the dated stakeholder clarification? [Traceability, Spec §Requirements, §Accepted Intent]
- [x] CHK068 Is every test-verified claim tied to a named automated test, with the verification date and result recorded? [Evidence, Spec §Verified Behavior Evidence]
- [x] CHK069 Is every implementation-only observation tied to a specific repository path? [Evidence, Spec §Implementation-Only Observations]
- [x] CHK070 Are the areas with no automated coverage listed explicitly rather than left to inference from the tests that do exist? [Gap, Spec §Verified Behavior Evidence]
- [x] CHK071 Does each of the seven clarification answers trace to at least one requirement and at least one acceptance scenario? [Traceability, Spec §Clarifications, §Requirements, §User Scenarios]
- [x] CHK072 Is each conformance gap mapped to the requirement it violates and to its current-state record? [Traceability, Spec §U-006]
- [x] CHK073 Are derived assumptions — notably the condition severity ordering — flagged as derived rather than sourced, with the effect of confirming them stated? [Evidence, Spec §Assumptions]

## Employee Self-Service Exclusion

- [x] CHK074 Is employee self-service Checkout excluded as deferred future scope with its authoritative source cited? [Clarity, Spec §FR-019, §Out of Scope]
- [x] CHK075 Is the exclusion consistent across canonical terms, requirements, authorization rules, and out-of-scope text, with no scenario implying an employee-initiated Checkout? [Consistency, Spec §Canonical Terms, §FR-019, §ALR-006, §AS-014]
- [x] CHK076 Is Transfer excluded except for the stated distinction, and Service Record excluded except for the two named integration boundaries? [Completeness, Spec §Out of Scope, §FR-012, §FR-015]

## Acceptance Criteria and Baseline Readiness

- [x] CHK077 Do the measurable outcomes collectively cover actors, transitions, custody effects, rejections, remarks, overdue behavior, notifications, audit, terminology, and evidence discipline without substituting implementation observations for acceptance criteria? [Acceptance Criteria, Spec §SC-001–SC-014]
- [x] CHK078 Is C1 identified as the only remaining acceptance blocker, with U-001 through U-004 shown as resolved and dated? [Readiness, Spec §FR-022, §Unresolved Conflicts] — *resolved 2026-08-12, see Finding 5*
- [x] CHK079 Does the Draft avoid weakening any accepted requirement to match current behavior, keeping every divergence in the conformance-gap register instead? [Readiness, Spec §U-006, §Assumptions]
- [x] CHK080 Is the lineage metadata complete and reciprocal, so a future change to this baseline can be linked back after acceptance? [Traceability, Spec §Specification Lineage]

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

## Findings — All Resolved 2026-08-12

**Finding 1 — CHK002: two evidence labels are used but never defined.**
§Evidence Classification defines four categories — Accepted intent, Test-verified
current behavior, Implementation-only observation, Unresolved. The body uses two
more that appear nowhere in the scheme: **Stakeholder-confirmed** (FR-006,
FR-014, FR-020, FR-023 through FR-028, ALR-008) and **Governance requirement**
(ALR-003). CHK002 itself names stakeholder-confirmed as one of five that must be
consistently applied. This matters more here than in the sibling baselines
because Stakeholder-confirmed carries the entire 2026-08-04 clarification — the
mandatory return condition, department clearing, remarks separation, Overdue, and
the audit set. A reviewer cannot tell whether that content ranks with accepted
intent or below it. Fourth baseline with this defect (B2 CHK008, B1 CHK006,
B6 CHK003); B8 was the only one clear of it.

**Finding 2 — CHK010: who may *be* a Checkout User is unspecified.**
The §Accepted Checkout Actor and Permission Contract governs who may *perform* a
Checkout, and ALR-006 establishes that being the Checkout User grants no
permission. Neither states who is eligible to receive custody. CAND-013 records
that the creation surface offers "the full active-User directory obtained with
`asset_view`" — current behavior, explicitly not accepted. Whether a Disabled
User or a User with no Role may be a Checkout User is unanswered, and both are
reachable: B1's directory excludes Disabled Users, but nothing in B3 requires the
backend to.

**Finding 3 — CHK026: the checkout condition has no stated treatment.**
CAND-003 records that it defaults to the Asset's condition when omitted, is
stored without validation, and never changes the Asset's own condition. §Edge
Cases acknowledges the consequence — "a Checkout record can carry a value outside
the canonical condition set while check-in rejects the same value" — and states
plainly that "Only the second effect has stated intent." The gap is therefore
visible but not closed: FR-010 governs the *return* condition only, and no
requirement covers the checkout condition's source, validation, or effect.

**Finding 4 — CHK040: concurrency is named but unowned.**
§Edge Cases records both halves accurately — "the row lock relied upon is a no-op
on the current database engine, so two simultaneous Checkouts of one `Available`
Asset are not provably prevented", and "Nothing in the data model prevents more
than one open Checkout per Asset". CHK040 permits either specifying the behavior
*or* naming it an open question **with an owner**. Neither is assigned to a
baseline, a change specification, or a decision. Compare the deletion-retention
edge case, which does name owners ("User and Asset deletion are owned by B1 and
B2"), and the B3/B5 Notification overlap, which names "the two owning baselines".

**Finding 5 — CHK078: C1 is described as undecided when it has been decided.**
FR-022 reads "This Draft MUST NOT be accepted while U-005 remains open", and
U-005 reads "Until C1 is decided, B3's eligibility boundary cannot be stated
completely." Both are stale. C1 **was** decided by the B4 clarification dated
2026-08-04 — Store-to-User issuance is a Checkout, not a Transfer — and
`ROADMAP.md`'s decision register records it as *Resolved*.

The blocker is therefore real but mischaracterised. B3 is not waiting for a
decision; it is carrying a decision it has not absorbed. That distinction changes
what closing it takes: not a stakeholder question, but applying an existing,
recorded answer to FR-001, FR-008, and the eligibility boundary — and B4 carries
the mirror image of the same gap, where the no-Custodian `IT Store` path remains
reachable.

## Notes

**Note A — CHK019 (passes).** The effect of C1 on the eligibility boundary *is*
stated, which is what the item asks. The statement's premise is stale for the
reason given in Finding 5; correcting FR-022 and U-005 will carry this text with
it.

**Note B — CHK058 (passes).** List scoping, ordering, filtering, and pagination
remain in CAND-012 as current-state candidates. This item explicitly permits
"explicitly retained as current-state candidates" as a passing outcome, so B3
passes where B8's CHK008 failed — that item required acceptance or delegation and
allowed no third option. The difference is in the checklists, not in the two
baselines' rigour.

## Observations Worth Carrying Into Review

B3 is the most thorough baseline reviewed so far. Its §Edge Cases and §Assumptions
close, with named owners, several things sibling baselines left implicit: the
derived condition-severity ordering is flagged as derived rather than sourced and
marked for confirmation; the C5 scheduling dependency is disclosed as an accepted
inherited risk rather than hidden; Overdue timezone basis is stated and its
evaluation frequency delegated to B8's deduplication contract; and the
B3/B5 duplicate-Notification overlap is assigned to its two owning baselines.


## Resolutions — 2026-08-12

| Finding | Resolution |
| --- | --- |
| 1 — CHK002 | `Stakeholder-confirmed` and `Governance requirement` added to §Evidence Classification. Stakeholder-confirmed is stated as requirement-eligible on the same footing as accepted intent, which matters because it carries the whole 2026-08-04 clarification. Every evidence label used in the body is now defined. |
| 2 — CHK010 | **FR-029** added: a Checkout User MUST be active; a Disabled User is rejected; holding no Role does not disqualify. Derived rather than decided — the active limit follows Draft B1 FR-004 (Disabled Users are excluded from the directory CAND-013 records as the selection source) and from custody accountability; the no-Role clause follows ALR-006, since requiring a Role would contradict the Checkout User being a subject who holds no permission. Conformance gap recorded: the serializer accepts any User reference without a status check. |
| 3 — CHK026 | **FR-030** added: the checkout condition must be canonical, defaults to the Asset's current condition, and never changes the Asset's condition. Derived — FR-010 already restricts the return condition and Draft B2 FR-003 requires every Asset to carry exactly one canonical condition, so a Checkout holding a non-canonical value contradicts both. Conformance gap recorded: it is stored unvalidated. |
| 4 — CHK040 | Both concurrency items moved from §Edge Cases into the U-006 conformance register as rows 14 and 15, with the requirements they violate named (FR-011; FR-001 with FR-007) and an owner assigned — B3 delivery. They were never open questions: the requirements already forbid the outcomes, and only the implementation fails to guarantee them. Same distinction drawn for concurrent Asset linking in Draft B6. |
| 5 — CHK078 | U-005 restated as **RESOLVED 2026-08-04, ABSORBED 2026-08-12**, and FR-022 rewritten so no decision gate remains. Absorbing C1 required **no requirement change**: it confirms the `Available`-only boundary FR-001 and FR-008 already state. The consequence lands on B4, where the no-Custodian `IT Store` path remains reachable — recorded there, not here. |

**Acceptance status.** This Draft's own note said "Even a fully checked list does
not authorize acceptance while U-005 is unresolved." U-005 is now resolved and
absorbed, so that condition is satisfied. What remains are the fifteen U-006
conformance gaps, which are delivery obligations against accepted requirements
rather than open decisions, and which FR-022 explicitly forbids treating as
grounds to weaken a requirement.
