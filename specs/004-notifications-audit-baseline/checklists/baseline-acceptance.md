# Brownfield Baseline Acceptance Checklist: AS-BUILT Notifications and AuditLog Baseline

**Purpose**: Determine whether the B8 requirements are complete, explicit,
consistent, traceable, privacy-aware, and ready for stakeholder acceptance.
**Created**: 2026-08-04
**Feature**: [spec.md](../spec.md)

**Audience and timing**: Stakeholders and maintainers reviewing the Draft before
baseline acceptance.

**Note**: This checklist evaluates the quality of the written requirements. It
does not test whether the current application conforms to them. Mark an item
complete only when the specification itself supplies clear, authoritative, and
testable text or an explicit scope decision.

## Baseline Scope and Authority

- [ ] CHK001 Are B8's shared Notification and AuditLog responsibilities distinguished from the business actions owned by B1–B7? [Completeness, Spec §Domain Alignment, §FR-002, §FR-018]
- [ ] CHK002 Are stakeholder-confirmed requirements, test-backed current behavior, implementation-only observations, unresolved findings, and deferred scope consistently classified without promoting code or tests to product intent? [Consistency, Spec §Evidence Classification, §FR-009, §Baseline Evidence]
- [ ] CHK003 Is AuditLog consistently defined as operational event history and explicitly distinguished from scheduled or periodic physical Asset auditing and proof of physical verification? [Clarity, Spec §Canonical Terms, §FR-007, §Out of Scope]
- [ ] CHK004 Is the current-version channel boundary explicit that Notifications are in-app only, email is deferred, and SMTP-labelled Settings neither enable nor imply email delivery? [Clarity, Spec §Clarifications, §FR-008, §Out of Scope]

## Notification Requirement Completeness

- [ ] CHK005 Is a Notification recipient unambiguously defined as a specific User, with capability-owned Role, permission, Custodian, requester, or other eligibility rules kept outside B8? [Clarity, Spec §Canonical Terms, §FR-002, §FR-018]
- [ ] CHK006 Are recipient-visibility requirements complete enough to require own-recipient isolation for list, detail, unread count, mark-one-read, and mark-all-read without exposing or mutating another User's records? [Completeness, Spec §User Story 2, §ALR-002, §SC-004]
- [ ] CHK007 Are the accepted Notification states, their allowed transitions, and the exact definition of the unread count specified without relying solely on implementation-only `Unread`/`Read` observations? [Gap, Spec §Read State, §CAND-001, §CAND-005]
- [ ] CHK008 Are list ordering, empty state, filtering or absence of filtering, and pagination or absence of pagination explicitly accepted or intentionally delegated rather than left as implementation-only candidates? [Gap, Spec §User Story 2, §CAND-004]
- [ ] CHK009 Are mark-one-read and mark-all-read requirements clear for already-Read items, zero-Unread state, concurrent state changes, and recipient deletion? [Coverage, Spec §User Story 2, §Edge Cases]
- [ ] CHK010 Is Notification destination ownership explicit, including the requirement that each owning matrix resolve route meaning and the current Asset-detail destination mismatch without turning it into a B8 trigger rule? [Traceability, Spec §FR-018, §Unresolved Conflicts, §Out of Scope]

## Failure and Recovery Requirements

- [ ] CHK011 Is fail-closed atomicity stated unambiguously for every business action requiring an AuditLog entry, including the no-business-change outcome when the entry cannot be retained? [Clarity, Spec §FR-011, §ALR-005, §SC-008]
- [ ] CHK012 Is Notification failure explicitly non-blocking for completed business work and consistent with the owning capability's trigger obligation? [Consistency, Spec §FR-012, §ALR-005]
- [ ] CHK013 Are automatic retry, duplicate prevention, operator visibility, and the delivered-or-explicitly-resolved terminal condition all defined as required recovery outcomes? [Completeness, Spec §FR-012, §SC-008]
- [ ] CHK014 Does the specification define missing or invalid recipients as failed deliveries subject to the same visibility, retry, deduplication, and resolution contract? [Edge Case, Spec §Edge Cases, §FR-012]
- [ ] CHK015 Are unread-polling failure requirements complete and measurable for retaining the last count, visibly marking staleness, offering manual retry, and avoiding read-state mutation? [Recovery, Spec §AS-011, §FR-013, §SC-009]

## Audit Event and Field Requirements

- [ ] CHK016 Is the mandatory shared audit-event set exhaustive and unambiguous for successful mutations, authentication events, permission/configuration changes, security-relevant rejections, and AuditLog views/exports? [Completeness, Spec §FR-014, §AS-012]
- [ ] CHK017 Are excluded routine reads and Notification list/count/read-state actions clearly distinguished from required AuditLog views/exports, and is the rule for capability-added risk events explicit? [Clarity, Spec §FR-014, §AS-014]
- [ ] CHK018 Are required AuditLog concepts defined for actor, event time, action, owning capability or module, affected identity, outcome or state effect, and capability-required reason? [Completeness, Spec §FR-006, §AuditLog Entry]
- [ ] CHK019 Are old/new-value requirements limited to the fields necessary to explain the change, with clear criteria for when before/after detail or a reason is required? [Clarity, Spec §FR-006, §FR-015, §AS-013]
- [ ] CHK020 Are passwords, tokens, credentials, secret configuration values, file contents, and unnecessary personal data expressly prohibited from every AuditLog field rather than only from old/new values? [Privacy, Spec §FR-015, §SC-010]
- [ ] CHK021 Are actor-identity requirements complete for unauthenticated attempts, deleted Users, missing profiles, username snapshots, and minimization over the retention period? [Coverage, Spec §AuditLog Entry, §FR-015, §FR-017, §Edge Cases]
- [ ] CHK022 Can the “exactly one required entry” criterion be objectively applied to allowed actions, rejected attempts, retries, and views/exports without ambiguity about duplicate events? [Measurability, Spec §AS-012, §FR-011, §FR-014, §SC-010]

## Audit Access, Filters, and Privacy

- [ ] CHK023 Is global AuditLog view, filter, and export access explicitly limited to Admin and IT Manager? [Clarity, Spec §FR-016, §ALR-003, §AS-015]
- [ ] CHK024 Is denial for every other named or custom Role explicit, including that `report_access` alone grants no AuditLog data or export? [Completeness, Spec §FR-016, §ALR-003]
- [ ] CHK025 Are direct Audit Trail, report, filter, and export requirements consistent under one authoritative backend access policy rather than relying on menu or route visibility? [Consistency, Spec §FR-016, §ALR-003, §ALR-006]
- [ ] CHK026 Are allowed AuditLog views/exports and rejected access attempts both required audit events, with a clear rule that rejected actors receive no AuditLog data? [Security, Spec §FR-014, §FR-016, §AS-015]
- [ ] CHK027 Are the accepted AuditLog filter dimensions, matching semantics, combinations, ordering, and empty-result behavior explicitly specified instead of remaining implementation-only module/username candidates? [Gap, Spec §User Story 4, §CAND-009, §FR-016]
- [ ] CHK028 Are accepted result limits, pagination or continuation behavior, and disclosure that older matching events were omitted explicitly defined for views and exports? [Gap, Spec §OBS-AS-010, §Edge Cases, §FR-016]
- [ ] CHK029 Are source-address requirements explicit about necessity, trusted origin, accuracy limitations, authorized visibility, minimization, and protection during the six-month retention window? [Privacy, Gap, Spec §Edge Cases, §FR-015, §FR-017]

## Retention and Deletion Requirements

- [ ] CHK030 Is the two-year AuditLog retention period anchored to an unambiguous starting event and does it state what deletion or irreversible anonymization occurs at expiry? [Clarity, Spec §FR-017, §SC-012]
- [ ] CHK031 Is the six-month source-IP period anchored to event time and does it require removal without deleting or corrupting the remainder of the AuditLog entry? [Clarity, Spec §FR-017, §AS-016]
- [ ] CHK032 Are the 90-day Read Notification period and one-year Unread period anchored respectively to the Read transition and creation time, including repeated mark-read behavior? [Clarity, Spec §FR-017, §SC-012]
- [ ] CHK033 Are User-deletion effects explicit and privacy-consistent for deleting recipient Notifications while retaining only minimized AuditLog actor identity until the entry expires? [Consistency, Spec §FR-017, §Edge Cases]
- [ ] CHK034 Are exported AuditLog copies subject to explicit access, privacy, retention, and disposal requirements, or is responsibility deliberately assigned to a named adjacent scope? [Gap, Spec §Assumptions, §FR-016, §FR-017]

## Capability Ownership and Traceability

- [ ] CHK035 Must every B3–B7 owning baseline publish a matrix covering business event, recipients, message meaning, destination, and audit detail beyond the B8 minimum before accepting that capability's triggers? [Completeness, Spec §FR-018, §AS-007, §SC-013]
- [ ] CHK036 Are B2's accepted audit/no-Notification rules and B6's stakeholder-confirmed audit/Notification rules traceable without B8 weakening, expanding, or duplicating them? [Traceability, Spec §FR-003, §FR-004, §Accepted Intent]
- [ ] CHK037 Is it explicit that current call sites and tests demonstrate evidence only and cannot establish a capability matrix entry without acceptance in the owning baseline? [Evidence, Spec §FR-005, §FR-018, §Evidence Classification]
- [ ] CHK038 Is B8's obligation to handle valid supplied triggers without inventing, suppressing, or reinterpreting capability business rules consistent across domain definitions, requirements, scenarios, assumptions, and out-of-scope text? [Consistency, Spec §Notification Trigger, §FR-018, §AS-017, §Assumptions]

## Acceptance Criteria and Baseline Readiness

- [ ] CHK039 Do measurable outcomes collectively cover channel scope, recipient isolation, read state, failure/recovery, mandatory audit events, field privacy, access, filters, retention, and trigger ownership without substituting implementation observations for acceptance criteria? [Acceptance Criteria, Spec §SC-003–SC-013]
- [ ] CHK040 Is the Draft free of unresolved B8 shared-facility conflicts while clearly leaving exact B3–B7 matrices, email delivery, physical Asset audits, and capability-owned destination correction in their declared owning or deferred scopes? [Readiness, Spec §Unresolved Conflicts, §Out of Scope, §FR-010]

## Notes

- Check items off as completed: `[x]`.
- Record findings inline with links to the relevant specification section or
  owning baseline.
- A checked item means the written requirements pass that quality gate; it does
  not mean the current implementation conforms.
- Any unresolved item in this formal acceptance checklist blocks changing the
  B8 status from `Draft` to accepted.
