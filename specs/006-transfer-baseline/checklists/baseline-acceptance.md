# Brownfield Baseline Acceptance Checklist: B4 Approval-Gated Transfer

**Purpose**: Formal stakeholder and reviewer gate for determining whether the B4 requirements are complete, clear, consistent, measurable, and evidence-qualified before the Draft baseline is accepted
**Created**: 2026-08-04
**Executed**: 2026-08-12 — 37 of 40 pass on first execution; all findings resolved the same day, 40 of 40 now closed. Two corrections were made during the pass: CHK015 was initially marked passing (ALR-002 omits two effects it enumerates), and an Evidence Classification defect was initially overstated — see §Correction.
**Feature**: [B4 specification](../spec.md)

**Note**: This checklist validates the requirements as written. It is not an
implementation test plan. Mark an item complete only when the specification
answers it unambiguously and traceably; implementation behavior alone is not
sufficient. Baseline acceptance requires every item to be checked or covered by
an explicit stakeholder-approved waiver recorded in the specification.

## Checkout-versus-Transfer Boundary

- [x] CHK001 Is Store-to-User issuance unambiguously assigned to Checkout without an approval gate and excluded from accepted Transfer behavior everywhere in the specification? [Consistency, Spec §Clarifications, §FR-001, §Out of Scope]
- [x] CHK002 Is Transfer consistently defined as a custody handoff from a current User Custodian to a different target User, with no null-Custodian or `IT Store` exception? [Clarity, Spec §Domain Alignment, §FR-001]
- [x] CHK003 Are the different lifecycle purposes of Checkout (`Available` to `Assigned`) and Transfer (approval-gated User-to-User custody handoff) stated without overlapping eligibility rules? [Completeness, Spec §Domain Alignment, §FR-001]
- [x] CHK004 Is the requirement that target department derives from the target User, rather than independent selection, consistent across scenarios, requirements, entities, and conformance findings? [Consistency, Spec §AS-004, §FR-006, §Key Entities]
- [x] CHK005 Are employee self-service, Checkout/check-in behavior, Service Record behavior, generic B8 mechanics, and B9 reporting clearly separated from B4 ownership? [Scope, Spec §Out of Scope]

## Actors, Permissions, and Visibility

- [x] CHK006 Is the request authorization policy complete for HR, IT Manager, Admin, Employee, IT Staff, Viewer, and custom Roles, with `transfer_request` identified as authoritative? [Completeness, Spec §FR-002, §Accepted Transfer Permission Contract]
- [x] CHK007 Is the approve/reject authorization policy complete for every named and custom Role, with `asset_custody_manage` identified as authoritative? [Completeness, Spec §FR-003, §Accepted Transfer Permission Contract]
- [x] CHK008 Is the policy allowing a requester who holds `asset_custody_manage` to approve or reject their own request explicit and consistent with the actor descriptions and permission matrix? [Consistency, Spec §Clarifications, §Lifecycle and Actors, §FR-003]
- [x] CHK009 Are Transfer read requirements complete for global non-Employee visibility and directly-involving Employee visibility under B1? [Completeness, Spec §FR-004, §Accepted Transfer Permission Contract]
- [x] CHK010 Is PDF authorization defined as exactly the same `asset_view` and B1 record scope used to read the underlying Transfer, without an Admin-only or broader UI exception? [Clarity, Spec §FR-015, §ALR-006, §Accepted Transfer Permission Contract]
- [x] CHK011 Does the specification require server-side authorization for every read, request, decision, and document action while treating frontend control visibility as a corresponding—not sufficient—boundary? [Security Coverage, Spec §ALR-001]
- [x] CHK012 Is direct Transfer update/deletion unambiguously prohibited for every actor, including Admin, with all valid state changes assigned to named lifecycle operations? [Clarity, Spec §FR-013, §Accepted Transfer Permission Contract]

## Transfer State and Atomic Effects

- [x] CHK013 Are the required contents of a successful Pending request complete, including Asset, captured previous Custodian and department, target User, derived target department, requester, remarks, and the absence of an approval-time condition? [Completeness, Spec §FR-005, §FR-006, §B4 Trigger and Audit Matrix]
- [x] CHK014 Are `Pending -> Approved` and `Pending -> Rejected` the only accepted decision transitions, with Approved and Rejected defined as terminal Transfer outcomes? [Clarity, Spec §Domain Alignment, §FR-008, §ALR-004]
- [x] CHK015 Are all approval effects required to commit atomically: Transfer outcome, Asset `Assigned` status, target Custodian, derived department, canonical condition, approver identity, decision time, and required AuditLog entry? [Atomicity, Spec §FR-008, §FR-012, §ALR-002] — *resolved 2026-08-12, see Finding 1*
- [x] CHK016 Is rejection specified to change only the Transfer outcome and decision accountability while leaving Asset status, Custodian, department, and condition unchanged? [Clarity, Spec §AS-007, §FR-008, §ALR-003]
- [x] CHK017 Are repeat approve/reject attempts against Approved or Rejected records defined as rejected operations with no Transfer or Asset mutation? [Exception Coverage, Spec §AS-008, §ALR-004]
- [x] CHK018 Is the approval-time condition requirement complete, including the five allowed values, required timing, Transfer persistence, Asset effect, and missing/blank/noncanonical rejection outcome? [Completeness, Spec §AS-006, §FR-012]
- [x] CHK019 Are request time and decision time defined as distinct business timestamps for every Pending, Approved, and Rejected record and for the Transfer PDF, without relying on the overloaded current `transfer_date` field? [Gap, Spec §Edge Cases, §Transfer PDF Baseline, §Resolution Status and Remaining Findings]

## Same-User, Concurrent, and Stale Requests — *resolved 2026-08-12, see Finding 1*

- [x] CHK020 Is same-User Transfer rejection stated at request time with an objectively verifiable no-record/no-Asset-mutation outcome? [Acceptance Criteria, Spec §AS-025, §FR-001, §ALR-007]
- [x] CHK021 Is the one-Pending-Transfer-per-Asset invariant explicit, including the outcome for a second request and preservation of the existing Pending request? [Clarity, Spec §AS-026, §FR-005, §ALR-007]
- [x] CHK022 Does the specification require the one-Pending invariant and approval decision to remain authoritative under simultaneous request or decision attempts, rather than permitting last-writer-wins behavior? [Concurrency Coverage, Spec §Edge Cases, §ALR-007]
- [x] CHK023 Are both Custodian drift and department drift between request and approval named as stale-snapshot conditions that reject approval? [Completeness, Spec §AS-027, §FR-010]
- [x] CHK024 Is the stale-approval outcome complete—Transfer remains Pending, Asset remains unchanged, required rejection audit applies when security-relevant—and is the subsequent approve/reject path still unambiguous? [Recovery/Exception Coverage, Spec §AS-027, §ALR-003, §B4 Trigger and Audit Matrix]

## Terminal, Service, and Other Negative Cases

- [x] CHK025 Is a null current Custodian expressly rejected at Transfer request time, preventing the current Store/Available path from satisfying B4? [Negative Coverage, Spec §FR-001, §Edge Cases]
- [x] CHK026 Are `Under Repair` restrictions specified both when requesting and when approving after an intervening Service transition? [Coverage, Spec §AS-010, §AS-012, §FR-009, §FR-010]
- [x] CHK027 Are `Sold`, `Scrapped`, and `Lost` restrictions specified both at request time and at approval-time revalidation? [Coverage, Spec §AS-011, §FR-009, §FR-010]
- [x] CHK028 Is B2-owned terminal processing consistently required to reject every Pending Transfer atomically, emit no Transfer workflow Notification, and include the rejection in the B2 audit event? [Dependency Consistency, Spec §AS-013, §FR-011, §B4 Trigger and Audit Matrix]
- [x] CHK029 Do all permission, invalid-state, stale-snapshot, same-User, duplicate-Pending, missing-condition, and noncanonical-condition failures have explicit zero-partial-mutation requirements? [Negative Coverage, Spec §ALR-003, §ALR-007, §SC-004]
- [x] CHK030 Is active target-User eligibility an enforceable requirement rather than only an assumption based on the minimal directory, including the expected outcome for a Disabled target User? [Assumption/Gap, Spec §Assumptions, §FR-005]

## Transfer PDF Requirements — *resolved 2026-08-12, see Finding 2*

- [x] CHK031 Is the PDF access matrix complete for every named Role, custom Role, Employee-own scope, and absent-`asset_view` case? [Completeness, Spec §FR-015, §SC-009]
- [x] CHK032 Are denied PDF requirements complete for both document-data non-disclosure and suppression of the download control for out-of-scope Transfers? [Security Coverage, Spec §AS-022, §SC-009]
- [x] CHK033 Are the exact accepted PDF title, branding source, filename, fields, timestamp meanings, null-value presentation, and signature areas distinguished from implementation-only observations? [Gap, Spec §Transfer PDF Baseline, §FR-015, §Resolution Status and Remaining Findings] — *see Note A*
- [x] CHK034 Is the no-AuditLog rule for PDF download consistent across functional requirements, the trigger/audit matrix, and measurable outcomes? [Consistency, Spec §FR-018, §B4 Trigger and Audit Matrix, §SC-008]

## Notifications and AuditLog

- [x] CHK035 Are Notification triggers and recipient rules complete for request, approval, rejection, automatic terminal rejection, negative operations, and PDF download, with deliberate no-Notification cases stated? [Completeness, Spec §FR-016, §B4 Trigger and Audit Matrix]
- [x] CHK036 Are all accepted Notification destinations specified as resolvable outcomes, including a genuinely Pending-filtered Transfer list, the canonical Asset-detail route, and the Transfer list? [Clarity, Spec §AS-014–AS-016, §FR-016]
- [x] CHK037 Are B8-owned in-app-only delivery, recipient specificity, non-blocking failure, operator visibility, retry, deduplication, read state, and retention clearly separated from B4-owned triggers? [Dependency Coverage, Spec §FR-016, §FR-017, §ALR-005]
- [x] CHK038 Are required AuditLog events complete for successful request, approval, rejection, and each security-relevant rejected action, while routine reads and PDF downloads are explicitly excluded? [Completeness, Spec §FR-018, §B4 Trigger and Audit Matrix]
- [x] CHK039 Are the minimum Transfer-specific AuditLog values defined per event and consistent with B8 privacy, source-IP, retention, and prohibited-value requirements? [Privacy/Clarity, Spec §B4 Trigger and Audit Matrix]
- [x] CHK040 Is required-audit atomicity stated consistently for request, approval, and rejection, including rollback on audit failure and non-rollback on Notification failure? [Reliability/Consistency, Spec §AS-017, §AS-018, §ALR-005, §SC-008]

## Notes

- This is a formal baseline-acceptance gate for specification reviewers and
  stakeholders before B4 leaves `Draft`.
- Items marked `[Gap]`, `[Assumption/Gap]`, or `[Ambiguity]` intentionally expose
  requirements that may still need a stakeholder decision or explicit scope
  exclusion.
- Record supporting requirement identifiers, review findings, or approved
  waivers inline before checking an item.
- The absence of `plan.md` is not evaluated here because this checklist reviews
  the brownfield baseline requirements before implementation planning.

## Findings — Resolved 2026-08-12

**Finding 1 — CHK015 and CHK019: the decision leaves no accountability record.**
§Resolution Status lists "the meaning of request versus decision timestamps" as a
remaining implementation-led confirmation item, and §Transfer PDF Baseline shows
the document printing "current `transfer_date`" — a single field the
implementation reuses for both the request and the decision. No requirement
defines two distinct business timestamps. The consequence is concrete: an
Approved Transfer's record cannot say when it was requested, and the PDF — the
custody document a person signs — prints one date without stating which event it
denotes. The B4 Trigger and Audit Matrix requires "actor, time" for request,
approval, and rejection entries, so the audit trail needs the distinction the
record does not carry.

The same gap reaches further than CHK019 alone. ALR-002 enumerates what approval
must commit atomically — "the Approved outcome, Asset status, Custodian,
department, accepted condition effect, required AuditLog entry" — and omits
**approver identity** and **decision time**, two of the eight effects CHK015
lists. Neither appears in FR-008 nor anywhere else as a requirement. The
implementation does retain an approver reference (`AssetTransfer.approved_by`),
so this is the inverse of the usual conformance gap: the code records the field
and no requirement obliges it, meaning nothing in the baseline would be violated
by removing it. For an approval-gated workflow whose entire purpose is
accountability, who decided and when must be required, not incidental.

**Finding 2 — CHK030: active target-User eligibility is an assumption, not a
requirement.** §Assumptions states "A target User is an active User selected
through B1's minimal directory" — which is precisely the formulation CHK030 rules
out, since it rests on the selection surface rather than on an enforceable rule.
FR-005 defines the request shape without constraining target-User status, and no
requirement states the outcome for a Disabled target User. B1's directory
excludes Disabled Users (FR-004, test-backed), but a request submitted directly
does not pass through that directory. This is the same defect found in Draft B3
as CHK010 and closed there by FR-029.

## Note A — CHK033 (passes, with a caveat)

The PDF title, branding, filename, fields, null-value presentation, and signature
areas are all distinguished from accepted content: §Transfer PDF Baseline opens
"The following is current implementation evidence, not accepted content or access
policy." The caveat is that the section's final bullet — "PDF download requires
`asset_view`, follows B1 Transfer-record visibility, and must be exposed only for
records the current User may read" — *is* accepted access policy, stated in
FR-015 and ALR-006. The section header therefore contradicts its own last entry.
No requirement is ambiguous, but the boundary would read more cleanly if that
bullet moved out of the evidence list.

## Correction — Evidence Classification

An earlier pass on this checklist recorded that B4 had **no** Evidence
Classification. That was wrong. B4 defines one as a bold sub-block inside
§Domain Alignment rather than as its own `###` heading, which is why a
section-level search missed it. The four categories it defined — accepted intent,
test-backed current behavior, implementation-only observation, unresolved — were
present from the start.

The narrower, accurate finding: two labels used on requirements were absent from
that block. **Stakeholder-confirmed** appears on FR-005, FR-012, FR-015, and
ALR-007 — carrying the whole 2026-08-04 clarification — and **Governance
requirement** underlies FR-013 and FR-019 through their constitution citations.
The block's "accepted intent … or an explicit stakeholder decision" arguably
folded the first in, but not by name, so a reviewer could not confirm the two
carried equal force.

*Resolved 2026-08-12* by extending the existing block rather than adding a second
one: both labels are now named, the qualifier convention is stated
("accepted authorization", "accepted lifecycle boundary", and so on narrow the
subject without lowering force), the compound convention is stated (the first
term is the authority; a trailing "and test-backed" or "with selected test
coverage" records evidence, never a weaker requirement), and dependency labels
are noted as unsettled while the owning baseline remains `Draft`.


## Resolutions — 2026-08-12

| Finding | Resolution |
| --- | --- |
| 1 — CHK015, CHK019 | **FR-020** added: request time, decision time, and deciding-actor identity retained as three separately readable values, with no single field representing both times and every surface — including the PDF — identifying which event a date denotes. Derived rather than decided: the Trigger and Audit Matrix already requires "actor, time" on three distinct events, so three values were already presupposed. Conformance gap recorded — one `transfer_date` is reused, and `approved_by` was retained by the implementation while required by nothing. |
| 2 — CHK030 | **FR-021** added: a Transfer target MUST be an active User; a Disabled target is rejected; no Role does not disqualify. Derived from Draft B1 FR-004 and custody accountability, mirroring Draft B3 FR-029 for the Checkout User. It replaces the §Assumptions statement, which rested on the selection surface and so did not bind a directly submitted request. Conformance gap recorded — the serializer accepts any `new_owner` without a status check. |
| Evidence Classification | Existing block in §Domain Alignment extended with `Stakeholder-confirmed` and `Governance requirement`, plus the qualifier, compound, and dependency conventions. See §Correction for what the original finding got wrong. |
