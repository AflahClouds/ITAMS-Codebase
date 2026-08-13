# Brownfield Baseline Acceptance Checklist: AS-BUILT Notifications and AuditLog Baseline

**Purpose**: Determine whether the B8 requirements are complete, explicit,
consistent, traceable, privacy-aware, and ready for stakeholder acceptance.
**Created**: 2026-08-04
**Executed**: 2026-08-12 — 33 of 40 pass on first execution; all 7 findings resolved the same day. The five requiring product decisions were closed by a stakeholder clarification session dated 2026-08-12, recorded in the specification.
**Feature**: [spec.md](../spec.md)

**Audience and timing**: Stakeholders and maintainers reviewing the Draft before
baseline acceptance.

**Note**: This checklist evaluates the quality of the written requirements. It
does not test whether the current application conforms to them. Mark an item
complete only when the specification itself supplies clear, authoritative, and
testable text or an explicit scope decision.

## Baseline Scope and Authority

- [x] CHK001 Are B8's shared Notification and AuditLog responsibilities distinguished from the business actions owned by B1–B7? [Completeness, Spec §Domain Alignment, §FR-002, §FR-018]
- [x] CHK002 Are stakeholder-confirmed requirements, test-backed current behavior, implementation-only observations, unresolved findings, and deferred scope consistently classified without promoting code or tests to product intent? [Consistency, Spec §Evidence Classification, §FR-009, §Baseline Evidence] — *resolved 2026-08-12, see Finding 1*
- [x] CHK003 Is AuditLog consistently defined as operational event history and explicitly distinguished from scheduled or periodic physical Asset auditing and proof of physical verification? [Clarity, Spec §Canonical Terms, §FR-007, §Out of Scope]
- [x] CHK004 Is the current-version channel boundary explicit that Notifications are in-app only, email is deferred, and SMTP-labelled Settings neither enable nor imply email delivery? [Clarity, Spec §Clarifications, §FR-008, §Out of Scope]

## Notification Requirement Completeness

- [x] CHK005 Is a Notification recipient unambiguously defined as a specific User, with capability-owned Role, permission, Custodian, requester, or other eligibility rules kept outside B8? [Clarity, Spec §Canonical Terms, §FR-002, §FR-018]
- [x] CHK006 Are recipient-visibility requirements complete enough to require own-recipient isolation for list, detail, unread count, mark-one-read, and mark-all-read without exposing or mutating another User's records? [Completeness, Spec §User Story 2, §ALR-002, §SC-004]
- [x] CHK007 Are the accepted Notification states, their allowed transitions, and the exact definition of the unread count specified without relying solely on implementation-only `Unread`/`Read` observations? [Gap, Spec §Read State, §CAND-001, §CAND-005] — *resolved 2026-08-12, see Finding 2*
- [x] CHK008 Are list ordering, empty state, filtering or absence of filtering, and pagination or absence of pagination explicitly accepted or intentionally delegated rather than left as implementation-only candidates? [Gap, Spec §User Story 2, §CAND-004] — *resolved 2026-08-12, see Finding 3*
- [x] CHK009 Are mark-one-read and mark-all-read requirements clear for already-Read items, zero-Unread state, concurrent state changes, and recipient deletion? [Coverage, Spec §User Story 2, §Edge Cases]
- [x] CHK010 Is Notification destination ownership explicit, including the requirement that each owning matrix resolve route meaning and the current Asset-detail destination mismatch without turning it into a B8 trigger rule? [Traceability, Spec §FR-018, §Unresolved Conflicts, §Out of Scope]

## Failure and Recovery Requirements

- [x] CHK011 Is fail-closed atomicity stated unambiguously for every business action requiring an AuditLog entry, including the no-business-change outcome when the entry cannot be retained? [Clarity, Spec §FR-011, §ALR-005, §SC-008]
- [x] CHK012 Is Notification failure explicitly non-blocking for completed business work and consistent with the owning capability's trigger obligation? [Consistency, Spec §FR-012, §ALR-005]
- [x] CHK013 Are automatic retry, duplicate prevention, operator visibility, and the delivered-or-explicitly-resolved terminal condition all defined as required recovery outcomes? [Completeness, Spec §FR-012, §SC-008]
- [x] CHK014 Does the specification define missing or invalid recipients as failed deliveries subject to the same visibility, retry, deduplication, and resolution contract? [Edge Case, Spec §Edge Cases, §FR-012]
- [x] CHK015 Are unread-polling failure requirements complete and measurable for retaining the last count, visibly marking staleness, offering manual retry, and avoiding read-state mutation? [Recovery, Spec §AS-011, §FR-013, §SC-009]

## Audit Event and Field Requirements

- [x] CHK016 Is the mandatory shared audit-event set exhaustive and unambiguous for successful mutations, authentication events, permission/configuration changes, security-relevant rejections, and AuditLog views/exports? [Completeness, Spec §FR-014, §AS-012]
- [x] CHK017 Are excluded routine reads and Notification list/count/read-state actions clearly distinguished from required AuditLog views/exports, and is the rule for capability-added risk events explicit? [Clarity, Spec §FR-014, §AS-014]
- [x] CHK018 Are required AuditLog concepts defined for actor, event time, action, owning capability or module, affected identity, outcome or state effect, and capability-required reason? [Completeness, Spec §FR-006, §AuditLog Entry]
- [x] CHK019 Are old/new-value requirements limited to the fields necessary to explain the change, with clear criteria for when before/after detail or a reason is required? [Clarity, Spec §FR-006, §FR-015, §AS-013]
- [x] CHK020 Are passwords, tokens, credentials, secret configuration values, file contents, and unnecessary personal data expressly prohibited from every AuditLog field rather than only from old/new values? [Privacy, Spec §FR-015, §SC-010]
- [x] CHK021 Are actor-identity requirements complete for unauthenticated attempts, deleted Users, missing profiles, username snapshots, and minimization over the retention period? [Coverage, Spec §AuditLog Entry, §FR-015, §FR-017, §Edge Cases]
- [x] CHK022 Can the “exactly one required entry” criterion be objectively applied to allowed actions, rejected attempts, retries, and views/exports without ambiguity about duplicate events? [Measurability, Spec §AS-012, §FR-011, §FR-014, §SC-010]

## Audit Access, Filters, and Privacy

- [x] CHK023 Is global AuditLog view, filter, and export access explicitly limited to Admin and IT Manager? [Clarity, Spec §FR-016, §ALR-003, §AS-015]
- [x] CHK024 Is denial for every other named or custom Role explicit, including that `report_access` alone grants no AuditLog data or export? [Completeness, Spec §FR-016, §ALR-003]
- [x] CHK025 Are direct Audit Trail, report, filter, and export requirements consistent under one authoritative backend access policy rather than relying on menu or route visibility? [Consistency, Spec §FR-016, §ALR-003, §ALR-006]
- [x] CHK026 Are allowed AuditLog views/exports and rejected access attempts both required audit events, with a clear rule that rejected actors receive no AuditLog data? [Security, Spec §FR-014, §FR-016, §AS-015]
- [x] CHK027 Are the accepted AuditLog filter dimensions, matching semantics, combinations, ordering, and empty-result behavior explicitly specified instead of remaining implementation-only module/username candidates? [Gap, Spec §User Story 4, §CAND-009, §FR-016] — *resolved 2026-08-12, see Finding 4*
- [x] CHK028 Are accepted result limits, pagination or continuation behavior, and disclosure that older matching events were omitted explicitly defined for views and exports? [Gap, Spec §OBS-AS-010, §Edge Cases, §FR-016] — *resolved 2026-08-12, see Finding 5*
- [x] CHK029 Are source-address requirements explicit about necessity, trusted origin, accuracy limitations, authorized visibility, minimization, and protection during the six-month retention window? [Privacy, Gap, Spec §Edge Cases, §FR-015, §FR-017]

## Retention and Deletion Requirements — *resolved 2026-08-12, see Finding 6*

- [x] CHK030 Is the two-year AuditLog retention period anchored to an unambiguous starting event and does it state what deletion or irreversible anonymization occurs at expiry? [Clarity, Spec §FR-017, §SC-012]
- [x] CHK031 Is the six-month source-IP period anchored to event time and does it require removal without deleting or corrupting the remainder of the AuditLog entry? [Clarity, Spec §FR-017, §AS-016]
- [x] CHK032 Are the 90-day Read Notification period and one-year Unread period anchored respectively to the Read transition and creation time, including repeated mark-read behavior? [Clarity, Spec §FR-017, §SC-012]
- [x] CHK033 Are User-deletion effects explicit and privacy-consistent for deleting recipient Notifications while retaining only minimized AuditLog actor identity until the entry expires? [Consistency, Spec §FR-017, §Edge Cases]
- [x] CHK034 Are exported AuditLog copies subject to explicit access, privacy, retention, and disposal requirements, or is responsibility deliberately assigned to a named adjacent scope? [Gap, Spec §Assumptions, §FR-016, §FR-017]

## Capability Ownership and Traceability — *see Note A*

- [x] CHK035 Must every B3–B7 owning baseline publish a matrix covering business event, recipients, message meaning, destination, and audit detail beyond the B8 minimum before accepting that capability's triggers? [Completeness, Spec §FR-018, §AS-007, §SC-013]
- [x] CHK036 Are B2's accepted audit/no-Notification rules and B6's stakeholder-confirmed audit/Notification rules traceable without B8 weakening, expanding, or duplicating them? [Traceability, Spec §FR-003, §FR-004, §Accepted Intent]
- [x] CHK037 Is it explicit that current call sites and tests demonstrate evidence only and cannot establish a capability matrix entry without acceptance in the owning baseline? [Evidence, Spec §FR-005, §FR-018, §Evidence Classification]
- [x] CHK038 Is B8's obligation to handle valid supplied triggers without inventing, suppressing, or reinterpreting capability business rules consistent across domain definitions, requirements, scenarios, assumptions, and out-of-scope text? [Consistency, Spec §Notification Trigger, §FR-018, §AS-017, §Assumptions]

## Acceptance Criteria and Baseline Readiness

- [x] CHK039 Do measurable outcomes collectively cover channel scope, recipient isolation, read state, failure/recovery, mandatory audit events, field privacy, access, filters, retention, and trigger ownership without substituting implementation observations for acceptance criteria? [Acceptance Criteria, Spec §SC-003–SC-013] — *resolved 2026-08-12, see Finding 7*
- [x] CHK040 Is the Draft free of unresolved B8 shared-facility conflicts while clearly leaving exact B3–B7 matrices, email delivery, physical Asset audits, and capability-owned destination correction in their declared owning or deferred scopes? [Readiness, Spec §Unresolved Conflicts, §Out of Scope, §FR-010]

## Notes

- Check items off as completed: `[x]`.
- Record findings inline with links to the relevant specification section or
  owning baseline.
- A checked item means the written requirements pass that quality gate; it does
  not mean the current implementation conforms.
- Any unresolved item in this formal acceptance checklist blocks changing the
  B8 status from `Draft` to accepted.

## Finding 1 — Resolved 2026-08-12

**CHK002: an evidence label is used but never defined.** §Evidence
Classification defines four categories — Stakeholder-confirmed, Test-backed
current behavior, Implementation-only observation, Unresolved. AS-010 is
labelled **Scope boundary**, which appears nowhere in the scheme, and CHK002
also names *deferred scope* as a kind that must be classified while "Deferred"
is not a defined category here (B6 defines it). Deferred content is consistently
marked in prose and has its own Out of Scope section, so the substantive risk is
limited to the one unplaced label. *Fix applied*: see the amended §Evidence
Classification.

Unlike B1, B2, and B6, this baseline does **not** use the undefined
`Governance-backed` label — the systemic template defect found in the other three
does not appear here.

## Findings That Required Stakeholder Decisions — Resolved 2026-08-12

These five could not be closed by rewording. Each names behavior the specification
deliberately left as a *Current-System Contract Candidate* — explicitly "Not
Accepted Requirements" — while the checklist asks whether it has been accepted or
delegated. Closing them meant deciding, for each, either to accept the current
behavior as a requirement or to record it as an unresolved finding that survives
into acceptance.

**Resolution.** A clarification session dated 2026-08-12 was recorded in the
specification, sourced to the stakeholder instruction of that date, and four new
requirements were written against it — FR-020 through FR-023 — plus a restated
SC-005. The session adopts the current documented behavior as the AS-BUILT
contract in every case except one: FR-022 additionally requires that omission by
the result limit be disclosed, because silent truncation on an audit surface
misrepresents the record. That single departure follows the decision already
taken for the report surface in CHG-B9-01, so it is consistent with an existing
accepted decision rather than novel intent. The CAND entries remain as
observations and are cited as such, never as the authority.

**Finding 2 — CHK007: the Notification state model is never accepted, yet
retention depends on it. — RESOLVED 2026-08-12.** §Key Entities describes Read State as "the current
textual state… Only `Unread` and `Read` are observed" — an observation. CAND-001
and CAND-005 hold the default state and the mark-read transitions as candidates.
No requirement accepts the state set, the allowed transitions, or what the unread
count actually counts. **This is the most consequential of the six**, because
FR-017 is an accepted requirement that reads "Read Notifications MUST be removed
90 days after becoming Read" — it keys a retention obligation to a transition the
baseline never accepts. Accepting FR-017 while leaving CHK007 open leaves a
requirement resting on an undefined term.

**Resolved** by adding **FR-019**, which states what FR-017 already presupposes
rather than deciding anything new: the two-state set, creation as `Unread`, the
one-way `Unread` → `Read` transition, idempotent re-marking that does not restart
a retention clock, the unread count as the recipient's own `Unread` records, and
retention of the transition time. CAND-001 and CAND-005 stay as observations and
are explicitly not the authority. §Key Entities now cites FR-019 instead of
describing the states as merely "observed".

Drafting it surfaced a concrete defect: `Notification` stores a creation time but
**no read time**, and the mark-read operations record no timestamp. FR-017's
90-day Read retention is therefore not implementable against the present record
shape, and nothing enforces the one-way transition. Both are recorded as an
implementation conformance gap under FR-019 — a delivery matter for a ticket, not
a further specification decision.

**Finding 3 — CHK008: Notification list presentation is undelegated.** CAND-004
records newest-first ordering, no pagination, no filter contract, and no
recipient-facing delete. No requirement accepts any of it, and no adjacent
baseline is named as owner. B9 owns report presentation, but the Notification
list is a B8 surface.

**Finding 4 — CHK027: the AuditLog filter contract is undefined.** FR-016 grants
"view, filter, and export access" without stating what may be filtered. CAND-009
holds the current contract — exact module match, case-insensitive partial
username match — as a candidate. Matching semantics, filter combination,
ordering, and empty-result behavior are unspecified.

**Finding 5 — CHK028: result limits and omission disclosure are undefined.**
CAND-009 records a 1,000-newest-row cap as current behavior. No requirement
accepts a limit, defines pagination or continuation, or requires disclosing that
older matching events were omitted. A reader of a truncated Audit Trail currently
cannot tell that anything is missing — a material property for an audit surface.

**Finding 6 — CHK029: source-address provenance is half-specified.** FR-017
covers protection and the 6-month window, FR-015 covers minimization generally,
and FR-016 covers authorized visibility. Three of the six aspects the item names
are absent: when capturing a source address is *necessary* (FR-017 says only
"when captured"), what constitutes a *trusted* origin, and what *accuracy
limitations* apply. CAND-008 records that the value is derived from the first
forwarded address or the direct remote address — a derivation that is
client-influenced and therefore not reliable evidence without a trust rule.

**Finding 7 — CHK039: a measurable outcome encodes unaccepted behavior.**
SC-005 measures that AuditLog verification "returns no more than 1,000 rows,
orders them newest first, and produces 100% exact module matches and 100%
case-insensitive partial username matches." Every one of those properties is
CAND-009 — behavior the specification states is *not accepted*. SC-005 therefore
substitutes an implementation observation for an acceptance criterion, which is
precisely what CHK039 prohibits. It resolves once Findings 4 and 5 are decided:
if the current contract is accepted, SC-005 should cite the resulting
requirements; if not, SC-005 should be removed or restated.


## Conformance Gaps Recorded While Resolving

Writing FR-019 through FR-023 against the current implementation surfaced three
delivery defects. Each is recorded under its requirement in the specification and
belongs in a ticket, not a further specification decision.

| Requirement | Gap | Evidence |
| --- | --- | --- |
| FR-019 | `Notification` stores a creation time but no read time, and mark-read records no timestamp — so FR-017's 90-day Read retention is not implementable, and nothing enforces the one-way transition. | `backend/core/models.py::Notification`; `backend/core/views.py::NotificationViewSet` |
| FR-022 | The view truncates with `qs[:1000]` and returns no limit, count, or omission indicator, so a reader cannot distinguish a complete result from a truncated one. | `backend/core/views.py::AuditLogViewSet` |
| FR-023 | `client_ip` trusts `HTTP_X_FORWARDED_FOR` unconditionally. That header is client-supplied on any request not passing through a trusted proxy, so a recorded source address can be chosen by the caller. | `backend/core/services.py::client_ip` |

The FR-023 gap is the most serious of the three: it means an AuditLog source
address is not reliable evidence of origin, which matters precisely for the
security-relevant rejections FR-014 requires to be logged.

## Note A — CHK034 (passes, with a caveat)

Exported AuditLog copies are addressed: §Assumptions carries the access and
privacy rules forward to exports, FR-016 requires every export to be authorized
and audited, and B9 is named as owner of export formats and the report catalog.
The caveat is disposal — "downstream file disposal mechanics are a planning
concern" is a deliberate disposition but does not name an owning scope, so no
baseline or change specification currently carries it.

## Dependency Impact

B3, B5, B7, and B9 each cite Draft B8 by requirement number, so B8's numbering
must stabilise before those four can be accepted. None of the seven items above
changes an existing FR identifier — Finding 1's fix is confined to §Evidence
Classification, and the six open findings would add requirements rather than
renumber them. The dependents are therefore safe to review now, provided any new
B8 requirement takes the next free number rather than reusing one.
