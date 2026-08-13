# Feature Specification: AS-BUILT Notifications and AuditLog Baseline

**Feature Branch**: `docs/baseline-spec-migration`

**Created**: 2026-08-04

**Status**: Draft

**Evidence Date**: 2026-08-04

**Input**: User description: "Create an AS-BUILT Brownfield Baseline
specification for ROADMAP.md entry B8: Notifications and AuditLog. Cover
in-app Notification recipients and read state, unread count, mark-one/all-read,
AuditLog fields, filters, access, and the boundary between shared delivery and
capability-specific triggers. Keep delivery channels, failure behavior,
mandatory audit events, audit access, and retention unresolved. Do not infer
email delivery merely because SMTP settings exist. Physical Asset audits are
out of scope. Do not modify application code."

## Clarifications

### Session 2026-08-04

- Q: Which delivery channels are required for B8 Notifications? → A: All B8
  Notifications are in-app only in this version; email delivery is deferred to
  a future version.
- Q: How should required audit writes, Notification delivery failures, and
  unread-count polling failures behave? → A: A required AuditLog entry commits
  atomically with its business action and rejects the action on failure;
  Notification failure does not roll back completed business work, retries
  automatically without duplicates, and is visible to operators; unread
  polling retains the last count, marks it stale, and offers manual retry.
- Q: Which events require AuditLog entries, and what old/new values may they
  contain? → A: Audit successful mutations, authentication events,
  permission/configuration changes, security-relevant rejections, and AuditLog
  views/exports; exclude routine reads and Notification read-state changes;
  record only relevant changed fields and never passwords, tokens, credentials,
  file contents, or unnecessary personal data.
- Q: Who may access AuditLog data, and how long are AuditLog, source IP, and
  Notifications retained? → A: Admin and IT Manager have global
  view/filter/export access; `report_access` alone grants none; retain AuditLog
  and minimized actor identity for 2 years, source IP for 6 months, Read
  Notifications for 90 days, Unread Notifications for 1 year, and delete all
  recipient Notifications when that User is deleted.
- Q: How are audit and Notification trigger rules owned across B3 through B7?
  → A: Each B3–B7 baseline owns an explicit matrix of business events,
  recipients, message meaning, destination, and additional audit detail; B8
  owns shared in-app persistence, retry/deduplication, read state/counts,
  polling, audit minimums, access, privacy, and retention and cannot invent or
  suppress a valid capability trigger.

### Session 2026-08-12

Raised by the B8 acceptance checklist (CHK008, CHK027, CHK028, CHK029, CHK039),
which found presentation, filtering, result limits, and source-address
provenance left as Current-System Contract Candidates rather than accepted or
delegated. The decisions below adopt the current documented behavior as the
AS-BUILT contract, except where the checklist identified a property an audit
surface cannot safely omit.

- Q: Should Notification list presentation be accepted or delegated? → A:
  Accept the current behavior — newest-first ordering, recipient-scoped, no
  filter contract, no recipient-facing delete or edit — and accept the absence
  of pagination on the basis that FR-017 retention bounds the list.
- Q: What is the accepted AuditLog filter contract? → A: Exact module match and
  case-insensitive partial username match, combined conjunctively, ordered
  newest first by event time, with an empty result returned as an empty set
  rather than an error.
- Q: What result limit applies to AuditLog views, and must omission be
  disclosed? → A: Retain the current 1,000-newest-row limit, but require the
  limit and the fact that older matching events were omitted to be disclosed to
  the reader. Silent truncation is not accepted on an audit surface.
- Q: What provenance rules apply to a captured source address? → A: It is
  indicative rather than authoritative; a forwarded header may be trusted only
  when it arrives from a configured trusted proxy; and it MUST NOT be the sole
  basis for any security decision.
- Q: How should SC-005 be restated? → A: Cite the resulting requirements rather
  than describing current behavior.

## Specification Lineage *(mandatory)*

**Type**: Brownfield Baseline

**Roadmap Reference**: `ROADMAP.md`, entry B8 — Notifications and AuditLog.

**Extends**: None.

**Supersedes**: None.

**Reciprocal Links**: `ROADMAP.md` reserves
`specs/004-notifications-audit-baseline/` for B8. The roadmap entry is not
edited by this specification run because it already contains that path and has
pre-existing worktree changes. Future changes after acceptance must be recorded
in a new specification and linked here with `Extends`, `Supersedes`, or
`Superseded by` metadata.


### Acceptance Record

*Pending — this baseline is `Draft`. Completing every field below is what moves
it to accepted; until then the fields stay marked pending.*

| Field | Value |
| --- | --- |
| Stakeholder decision | *Pending* |
| Accepting stakeholder | *Pending* |
| Acceptance date | *Pending* |
| Reviewed evidence date | 2026-08-04 |
| Acceptance checklist result | 40 of 40 items closed; executed 2026-08-12 — see `checklists/baseline-acceptance.md` |
| Unresolved items deliberately carried forward | None within B8's shared-facility scope. The `/asset/{id}` versus `/asset/detail/{id}` destination mismatch is owned by the B3–B7 trigger matrices, not carried here. |
| Delivery gaps recorded against accepted requirements | FR-019 read timestamp, FR-022 omission disclosure, FR-023 forwarded-header trust — delivery tickets, not carried-forward decisions |

**Immutability boundary**: on the acceptance date recorded above, the
requirement and acceptance content of this specification becomes an immutable
flow-forward record. From that point a semantic change MUST use a new feature
directory with reciprocal `Extends`, `Supersedes`, or `Superseded by` links;
this specification may be edited only to add or correct that non-semantic
lineage metadata. *(Constitution §III.)*

## Domain Alignment *(mandatory)*

**Canonical Terms**:

- **Notification** is the shared, recipient-addressed operational message
  currently surfaced inside ITAMS. It is distinct from the business event that
  causes a capability to request delivery.
- **Notification recipient** is a specific ITAMS **User**. A Role, permission
  code, Custodian relationship, requester relationship, or other capability
  rule may be used by the owning capability to choose one or more recipients;
  B8 does not define those business rules.
- **Notification trigger** is a capability-owned decision that a business event
  should notify specified recipients with specified content and an optional
  destination. **Notification delivery and state** are the B8-owned shared
  concerns that begin after a valid trigger has supplied those inputs.
- **AuditLog** is the shared operational event record currently called the
  **Audit Trail** in its administrative frontend surface. It is not a physical
  inspection of Assets.
- **Physical Asset audit** means scheduled or periodic verification of physical
  Assets against system records. It is deferred beyond v1 and must not be
  represented as an AuditLog requirement.
- Adjacent capability language follows `CONTEXT.md`: use **Asset**,
  **Custodian**, **Checkout**, **Transfer**, **Service Record**,
  **Procurement**, **Warranty**, and **AMC**. Do not use “Assignment” as a
  synonym for Checkout.

**Relevant Decisions**:

- `CONTEXT.md` establishes that periodic physical Asset audits are deferred and
  that proactive Warranty/AMC alerts are intended. Stakeholder clarification
  dated 2026-08-04 establishes in-app-only B8 delivery for this version and
  defers email delivery to a future version.
- `docs/adr/0001-service-record-lifecycle.md` governs the adjacent Service
  Record/Custodian transition. It does not define Notification delivery or
  AuditLog policy.
- The Draft B2 baseline owns Asset-register trigger selection: every
  successful B2 mutation has a required operational audit effect, terminal
  transitions require expanded event content, and B2 actions send no
  Notifications.
- The Draft B6 baseline records stakeholder-confirmed Procurement and master
  audit/Notification triggers while assigning shared storage, delivery, access,
  filtering, and retention to B8.
- Each B3–B7 baseline must accept its own explicit audit and Notification
  trigger matrix. B8 owns only the shared behavior defined below and does not
  centralize those capability rules.

**Lifecycle and Actors**:

- B8 does not own an Asset lifecycle transition. It receives Notification and
  AuditLog effects selected by B1–B7 and stores or presents those effects.
- Test-backed Notification recipients include a new Custodian after Checkout,
  a User with `asset_custody_manage` for a Transfer request, a previous
  Custodian when a Service Record opens, an IT Manager after AMC renewal or End
  Support, and a User with `asset_custody_manage` at tested Warranty/AMC expiry
  thresholds. These facts demonstrate selected current triggers; their business
  rules remain owned by B3, B4, B5, and B7.
- Current implementation permits any authenticated active User to reach the
  Notification surface and scopes records to that User. This behavior has no
  dedicated authorization test and is not yet accepted intent.
- Current direct Audit Trail access is limited to Admin or a platform
  superuser, while the separately named “Asset Audit Report” exposes the same
  global AuditLog data to Users with `report_access`. Both are implementation
  conformance gaps against the accepted Admin-and-IT-Manager policy in ALR-003.

### Evidence Classification

This Draft uses the following classifications:

- **Stakeholder-confirmed**: stated in `CONTEXT.md`, an accepted specification,
  or an explicit stakeholder decision.
- **Test-backed current behavior**: demonstrated by an automated test and
  eligible for this requested AS-BUILT baseline without establishing a broader
  delivery or audit policy.
- **Implementation-only observation**: visible in backend or frontend code
  without dedicated automated behavioral coverage or stakeholder confirmation.
- **Scope boundary**: a statement of what this baseline is not, drawn from
  `CONTEXT.md` or the B8 roadmap entry. It constrains interpretation of the
  requirements — most importantly that AuditLog is operational event history and
  never evidence of a physical Asset audit — but introduces no obligation of its
  own and is not a candidate for stakeholder rejection.
- **Deferred**: intentionally excluded from the current product scope and
  recorded in §Out of Scope, not merely unimplemented.
- **Unresolved**: a material choice or inconsistent boundary that must not be
  promoted into an accepted requirement.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receive a Capability-Triggered Notification (Priority: P1)

A User selected by an owning capability receives a recipient-specific in-app
Notification so that a relevant lifecycle or expiry event can be noticed.

**Why this priority**: Selected business workflows already depend on the shared
facility to surface time-sensitive or custody-related events.

**Independent Test**: Execute each covered capability operation, then verify
that a Notification exists for the expected User without generalizing the
capability's recipient rule into B8.

**Acceptance Scenarios**:

1. **AS-001 — Test-backed current behavior**: **Given** a successful Checkout,
   **When** the operation completes, **Then** an in-app Notification exists for
   the new Custodian.
2. **AS-002 — Test-backed current behavior**: **Given** a Transfer request,
   **When** the request is created, **Then** an in-app Notification exists for
   a User whose Role grants `asset_custody_manage`.
3. **AS-003 — Test-backed current behavior**: **Given** an Asset with a
   Custodian, **When** a Service Record opens, **Then** an in-app Notification
   exists for the previous Custodian.
4. **AS-004 — Test-backed current behavior**: **Given** a successful AMC renewal
   or End Support action, **When** the action completes, **Then** an in-app
   Notification exists for an active User in the named IT Manager Role.
5. **AS-005 — Test-backed current behavior**: **Given** a Warranty at the exact
   30-day threshold or an active AMC at the exact 7-day threshold, **When** the
   expiry check runs, **Then** an in-app Notification containing the Asset
   identifier exists for a User with `asset_custody_manage`.
6. **AS-006 — Test-backed current behavior**: **Given** a Warranty that is not
   on a configured threshold or an ended AMC on a threshold date, **When** the
   expiry check runs, **Then** the tested User receives no expiry Notification.

---

### User Story 2 - Review and Clear Personal Notification State (Priority: P1)

An authenticated User reviews their own Notifications, distinguishes Unread
from Read items, marks one item Read, or clears the Unread state of all their
items.

**Why this priority**: Recipient isolation and reliable read state are the core
shared behaviors that make an in-app Notification useful.

**Independent Test**: Create Read and Unread Notifications for two Users,
exercise list, count, mark-one, and mark-all operations as one User, and verify
that only that User's records and state change.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-001 — Implementation-only**: **Given** an authenticated active
   User, **When** the User opens Notifications, **Then** only Notifications
   addressed to that User are returned, newest first.
2. **OBS-AS-002 — Implementation-only**: **Given** the User has Read and Unread
   Notifications, **When** unread count is requested, **Then** the result is the
   number of that User's records whose state is exactly `Unread`.
3. **OBS-AS-003 — Implementation-only**: **Given** one of the User's
   Notifications is Unread, **When** the User marks that item Read, **Then** its
   state becomes `Read` and another User's records do not change.
4. **OBS-AS-004 — Implementation-only**: **Given** the User has multiple Unread
   Notifications, **When** the User marks all Read, **Then** every Unread record
   addressed to that User becomes Read and another User's records do not
   change.
5. **OBS-AS-005 — Implementation-only**: **Given** a Notification contains a
   destination, **When** it is displayed, **Then** its message is a link;
   otherwise the message is displayed without a link.

---

### User Story 3 - See the Current Unread Count (Priority: P2)

An authenticated User sees a badge in the Navbar indicating their current
number of Unread Notifications and can navigate to the Notifications surface.

**Why this priority**: The badge provides awareness without requiring the User
to repeatedly open the Notifications page.

**Independent Test**: Sign in as a User with a known number of Unread
Notifications, observe the Navbar and its refresh behavior, and follow the icon
to the Notifications surface.

**Acceptance Scenarios**:

1. **AS-011 — Stakeholder-confirmed**: **Given** the unread count was loaded
   successfully, **When** a later poll fails, **Then** the Navbar retains the
   last known count, visibly marks it stale, and offers a manual retry without
   changing persisted Notification state.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-006 — Implementation-only**: **Given** an authenticated User,
   **When** the Navbar loads, **Then** it requests the User's unread count and
   displays the returned number on the Notification icon.
2. **OBS-AS-007 — Implementation-only**: **Given** the Navbar remains open,
   **When** 30 seconds elapse, **Then** it requests the unread count again.
3. **OBS-AS-008 — Implementation-only conformance gap**: **Given** an
   unread-count request fails, **When** the failure is handled, **Then** the
   current Navbar suppresses the error and retains its prior displayed state
   but does not mark it stale or offer manual retry as required by AS-011.
4. **OBS-AS-009 — Implementation-only**: **Given** the User marks Notifications
   Read on the Notifications page, **When** that page reloads its list, **Then**
   the Navbar badge is not explicitly refreshed by the action and may remain
   stale until its next poll.

---

### User Story 4 - Review the Operational Audit Trail (Priority: P1)

An authorized reviewer inspects recent operational events by event time, actor
identity, action, module, before/after details, and source address, and narrows
the results by module or username when those filters are available.

**Why this priority**: AuditLog exists to support operational accountability,
but its usefulness and privacy depend on an accepted event schema and access
policy.

**Independent Test**: Seed more than one module and username, request the
direct Audit Trail with and without filters, inspect ordering and fields, and
compare access with the audit report surface.

**Acceptance Scenarios**:

1. **AS-012 — Stakeholder-confirmed**: **Given** a successful mutation,
   authentication event, permission or configuration change,
   security-relevant rejection, or AuditLog view/export, **When** the event
   completes or is rejected, **Then** exactly one required AuditLog entry is
   retained under FR-011.
2. **AS-013 — Stakeholder-confirmed**: **Given** a required AuditLog entry for a
   change, **When** old/new detail is recorded, **Then** it identifies only the
   relevant changed fields and excludes passwords, tokens, credentials, file
   contents, and unnecessary personal data.
3. **AS-014 — Stakeholder-confirmed**: **Given** an ordinary read or a
   Notification mark-one/all-read action, **When** it completes, **Then** it
   creates no AuditLog entry unless the read is itself an AuditLog view or
   export.
4. **AS-015 — Stakeholder-confirmed**: **Given** an Admin or IT Manager, **When**
   that User views, filters, or exports AuditLog data, **Then** global access is
   allowed and the access event is audited; **Given** any other User, including
   one with `report_access`, **When** the same action is attempted, **Then** it
   is rejected and the security-relevant rejection is audited.
5. **AS-016 — Stakeholder-confirmed**: **Given** retained AuditLog and
   Notification records, **When** their respective retention limit is reached,
   **Then** source IP is removed after 6 months, the AuditLog entry and minimized
   actor identity are removed after 2 years, Read Notifications are removed
   after 90 days, and Unread Notifications are removed after 1 year.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-010 — Implementation-only**: **Given** operational AuditLog rows
   exist, **When** the direct Audit Trail is requested, **Then** at most the
   1,000 newest matching rows are returned.
2. **OBS-AS-011 — Implementation-only**: **Given** a module filter, **When** the
   direct Audit Trail is requested, **Then** only exact module matches are
   returned.
3. **OBS-AS-012 — Implementation-only**: **Given** a username fragment, **When**
   the direct Audit Trail is requested, **Then** case-insensitive partial
   username matches are returned.
4. **OBS-AS-013 — Implementation-only**: **Given** a current AuditLog row,
   **When** it is serialized, **Then** it exposes row identity, optional User
   reference, username, action, module, old value, new value, event date/time,
   and IP address.
5. **OBS-AS-014 — Implementation-only and inconsistent**: **Given** a non-Admin
   User with `report_access`, **When** the User opens the report catalog,
   **Then** the User can obtain and export the same global AuditLog dataset as
   the “Asset Audit Report” even though direct Audit Trail access is Admin-only.

---

### User Story 5 - Preserve Shared-Facility Ownership (Priority: P1)

A capability specification decides which of its events require an AuditLog
entry or Notification and who the recipients are, while B8 provides the shared
record, delivery-state, access, filter, and retention contract without
redefining the business trigger.

**Why this priority**: Without a clear boundary, trigger lists drift between
capabilities and shared infrastructure, making omissions and duplicate delivery
likely.

**Independent Test**: Trace one B2 event, one B6 event, and one B3–B7 current
trigger from its owning specification or test into the shared facility and
verify that B8 neither invents nor suppresses the owner-defined trigger.

**Acceptance Scenarios**:

1. **AS-007 — Stakeholder-confirmed boundary**: **Given** a capability owns a
   business action, **When** audit or Notification effects are specified,
   **Then** its B3–B7 baseline owns an explicit matrix of event selection,
   recipient selection, message meaning, business destination, and additional
   audit detail while B8 owns the shared record and its cross-capability
   behavior.
2. **AS-008 — Draft B2 dependency**: **Given** a B2 Asset-register action,
   **When** its side effects are evaluated, **Then** B8 preserves the B2 audit
   event supplied by that capability and creates no B2 Notification.
3. **AS-009 — Stakeholder-confirmed B6 dependency**: **Given** a B6 action,
   **When** its side effects are evaluated, **Then** B8 preserves the B6-owned
   audit event or Notification trigger without expanding its event or recipient
   set.
4. **AS-010 — Scope boundary**: **Given** a record called AuditLog, Audit Trail,
   or “Asset Audit Report,” **When** its meaning is described, **Then** it is
   treated as an operational event trail and never as evidence that a physical
   Asset audit occurred.
5. **AS-017 — Stakeholder-confirmed ownership**: **Given** a valid trigger that
   conforms to an owning B3–B7 matrix and B8's shared minimums, **When** B8
   handles it, **Then** B8 neither invents an additional business trigger nor
   suppresses the supplied trigger and applies the shared delivery, state,
   reliability, access, privacy, and retention contract.

### Edge Cases

- A User with no profile cannot receive a Notification through the current
  shared helper; the helper silently does nothing. Under FR-012 this is a failed
  delivery that must remain operator-visible and retry without duplication
  until delivered or explicitly resolved.
- Marking an already Read Notification Read is currently idempotent in effect,
  but no accepted response or audit requirement exists.
- Mark-all-read with no Unread Notifications currently succeeds without
  changing data; no accepted response contract exists.
- A User cannot select another User's Notification through the recipient-scoped
  current query, but this isolation has no dedicated automated test.
- Notification state is stored as text and current behavior relies on the exact
  `Unread` and `Read` values; handling of legacy or unexpected values is
  unspecified.
- Current Asset destinations use `/asset/{id}`, while the frontend Asset-detail
  route is `/asset/detail/{id}`. The resulting broken or unmatched destination
  is an implementation conformance gap, not an accepted link contract.
- Current Notification and AuditLog records react differently to User deletion:
  Notifications are deleted with the User, while AuditLog retains username and
  may clear the User reference. This aligns only partially with FR-017: all
  recipient Notifications are deleted, while minimized actor identity remains
  available for the AuditLog's 2-year lifetime.
- Current logging may record a User reference, a username snapshot, both, or
  neither. Failed login and selected login paths bypass the shared IP capture
  helper, so field completeness varies by event.
- Forwarded source-address input is currently accepted from the first supplied
  value without a documented trust policy. This is an implementation privacy
  gap; source IP is permitted only as protected AuditLog data and must be
  removed after 6 months under FR-017.
- Audit old/new values are unrestricted text and can contain names, identifiers,
  Roles, statuses, reasons, or other capability data. This is an implementation
  conformance gap where values are not limited and redacted as FR-015 requires.
- Direct Audit Trail and report-based AuditLog access apply different current
  authorization rules and neither has a dedicated access test. Both require
  conformance to ALR-003 and AS-015.
- The current 1,000-row cap has no pagination or indication that older matching
  events were omitted.
- A Notification or AuditLog write can occur before or after its capability
  mutation depending on the caller. Retry, deduplication, rollback, partial
  success, and operator-visible failure behavior are current implementation
  conformance gaps against FR-011 and FR-012.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 — Test-backed current behavior**: For each selected trigger covered
  by AS-001 through AS-005, the shared facility MUST be capable of retaining an
  in-app Notification addressed to the User selected by the owning capability.
  This requirement confirms only the tested side effect and does not establish
  a complete trigger matrix.
- **FR-002 — Stakeholder-confirmed boundary**: Each capability specification
  MUST own an explicit matrix of business trigger selection,
  recipient-selection rule, message meaning, business destination, and any
  additional audit detail. B8 MUST own shared Notification storage, delivery
  behavior, retry/deduplication, recipient visibility, read state, unread
  counts, polling, shared audit minimums, access, privacy, filtering, and
  retention after those inputs are supplied.
- **FR-003 — Draft B2 dependency**: B8 MUST accept and preserve B2's required
  Asset-register audit effects and MUST NOT create Notifications for B2 actions.
  B8 MUST NOT weaken or expand B2's accepted event selection.
- **FR-004 — Stakeholder-confirmed B6 dependency**: B8 MUST accept and preserve
  B6's specified audit events and IT Manager Notification triggers without
  adding Notifications for B6 actions that B6 explicitly excludes.
- **FR-005 — Cross-capability boundary**: B8 MUST NOT convert the selected
  B3–B7 current trigger evidence in AS-001 through AS-006 into a complete or
  mandatory trigger contract. Each owning baseline MUST accept, amend, or
  reject those triggers in its explicit matrix before that capability baseline
  is accepted.
- **FR-006 — Accepted dependency support**: The shared AuditLog facility MUST
  be capable of preserving the event content required by accepted capability
  specifications, including the actor, event time, action, affected identity,
  outcome or state effect, before/after information, and a reason where the
  owning capability requires one. Changed-field content is governed by FR-015.
- **FR-007 — Scope integrity**: B8 MUST describe AuditLog and Audit Trail as
  operational event history and MUST NOT treat either as a physical Asset audit
  or proof of physical verification.
- **FR-008 — Stakeholder-confirmed channel**: Every B8 Notification in this
  version MUST be delivered in-app only. Email delivery MUST NOT be required or
  inferred from editable SMTP Settings and is deferred to a future version.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-009 — Evidence integrity**: Notification list/read-state behavior and
  AuditLog fields, filters, access, limits, and frontend presentation observed
  only in implementation MUST remain labeled implementation-only until backed
  by tests or explicit stakeholder acceptance.
- **FR-010 — Decision gate**: This Draft MUST NOT be accepted or used to infer
  the exact B3–B7 business trigger matrices. Those matrices MUST be resolved in
  the owning capability baselines, not centralized in or inferred by B8. B8 may
  be accepted once this ownership boundary and its shared requirements pass
  review.
- **FR-011 — Stakeholder-confirmed audit failure behavior**: A business action
  that requires an AuditLog entry MUST commit that entry atomically with the
  business change. If the required entry cannot be retained, the action MUST be
  rejected and leave its business data unchanged.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-012 — Stakeholder-confirmed Notification failure behavior**: Failure to
  retain an in-app Notification MUST NOT roll back completed business work. The
  failed delivery MUST retry automatically without creating duplicate
  Notifications and MUST remain visible to an operator until delivered or
  explicitly resolved.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-013 — Stakeholder-confirmed polling failure behavior**: When unread-count
  polling fails, the Navbar MUST retain the last known count, visibly identify
  it as stale, and provide a manual retry. A polling failure MUST NOT change
  Notification records or read state.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-014 — Stakeholder-confirmed mandatory audit events**: AuditLog entries
  MUST be created for every successful business-data mutation; login success,
  login failure, logout, and successful password change; Role, permission, and
  administrative Setting changes; security-relevant authorization,
  identity-conflict, and protected-deletion rejections; and every AuditLog view
  or export. Routine reads and Notification list, count, mark-one-read, and
  mark-all-read actions MUST NOT create AuditLog entries. An owning capability
  MAY require additional risk-based events but MUST NOT omit this shared
  minimum.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-015 — Stakeholder-confirmed audit value privacy**: A mutation AuditLog
  entry MUST identify only the old/new fields whose change is necessary to
  explain the event. AuditLog entries MUST NOT contain passwords, session or
  authentication tokens, credentials, secret configuration values, uploaded
  file contents, or personal data unnecessary for accountability. A reason or
  other capability detail MAY be retained only when the owning capability
  requires it and it complies with this minimization rule.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-016 — Stakeholder-confirmed AuditLog access**: Admin and IT Manager MUST
  have global AuditLog view, filter, and export access. Every other named or
  custom Role MUST be denied, and `report_access` alone MUST NOT grant any
  AuditLog data or export. Direct Audit Trail and report/export surfaces MUST
  enforce the same policy. Every allowed view/export and every rejected access
  attempt MUST create the FR-014 AuditLog entry without exposing AuditLog data
  to a rejected actor.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-017 — Stakeholder-confirmed retention and deletion**: AuditLog entries
  and their minimized actor identity MUST be retained for 2 years. Source IP,
  when captured, MUST be protected as AuditLog data and removed after 6 months
  without deleting the remaining entry. Read Notifications MUST be removed 90
  days after becoming Read; Unread Notifications MUST be removed 1 year after
  creation. All Notifications addressed to a User MUST be removed when that
  User is deleted; AuditLog actor identity MUST remain minimized and readable
  until the entry's 2-year limit.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-018 — Stakeholder-confirmed trigger ownership**: Each B3–B7 baseline MUST
  publish an explicit audit and Notification trigger matrix covering its
  business events, recipients, message meaning, destination, and any audit
  detail beyond FR-014 and FR-015. B8 MUST validate and handle a supplied
  trigger under its shared contract but MUST NOT add, remove, or reinterpret a
  capability business trigger. A capability trigger absent from its accepted
  matrix is not accepted intent even if a current implementation call site or
  test demonstrates it.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-019 — Read state and unread count**: A Notification MUST hold exactly one
  of two states, `Unread` or `Read`, and MUST be created `Unread`. The only
  permitted transition is `Unread` → `Read`; a Notification MUST NOT return to
  `Unread`. Marking an already-`Read` Notification read MUST be idempotent —
  it changes no state and does not restart any retention period. The **unread
  count** is the number of Notifications addressed to the requesting recipient
  whose state is `Unread`, counted over that recipient's own records only. The
  time at which a Notification became `Read` MUST be retained.
  *(Source: entailed by FR-017, stakeholder clarification 2026-08-04. FR-017
  requires Read Notifications to be removed "90 days after becoming Read" and
  Unread Notifications "1 year after creation". Those obligations presuppose the
  two states, the one-way transition, and a retained transition time; this
  requirement states what FR-017 already depends on rather than introducing a new
  decision. The states are recorded as observations in CAND-001 and CAND-005 —
  which remain the record of current behavior, not the authority for this
  requirement.)*

  **Implementation conformance gap**: the current Notification record stores a
  creation time but no read time (`backend/core/models.py::Notification`), and
  the current mark-read operations set the state without recording when
  (`backend/core/views.py::NotificationViewSet`). FR-017's 90-day Read retention
  is therefore not implementable against the present record shape. Whether the
  one-way transition is enforced is likewise unverified; nothing currently
  prevents a write returning a record to `Unread`.
- **FR-020 — Notification list presentation**: A recipient's Notification list
  MUST be ordered newest first by creation time and MUST contain only that
  recipient's records. This version accepts no filter contract beyond that
  recipient scoping, and provides no recipient-facing delete or content-edit
  operation. The list is unpaginated; that is accepted because FR-017 bounds it
  — Unread records are removed one year after creation and Read records 90 days
  after becoming Read, so the list cannot grow without limit. An empty list MUST
  be a normal outcome rather than an error.
  *(Source: stakeholder clarification, 2026-08-12; current behavior recorded as
  observation in CAND-004.)*
- **FR-021 — AuditLog filter contract**: AuditLog views MUST support filtering by
  module using exact match and by username using case-insensitive partial match.
  Supplying both MUST narrow the result to entries satisfying both. Results MUST
  be ordered newest first by event time. A filter matching nothing MUST return an
  empty result rather than an error, and MUST NOT fall back to an unfiltered set.
  *(Source: stakeholder clarification, 2026-08-12; current behavior recorded as
  observation in CAND-009.)*
- **FR-022 — AuditLog result limit and omission disclosure**: An AuditLog view
  MUST return at most the 1,000 newest matching entries. When matching entries
  are omitted by that limit, the response MUST disclose both the limit and the
  fact that older matching events exist beyond it, so a reader can tell the view
  is incomplete and narrow the filter. Silent truncation is NOT accepted: an
  audit surface that appears complete while omitting evidence misrepresents the
  record.
  *(Source: stakeholder clarification, 2026-08-12. The limit itself is current
  behavior recorded in CAND-009; the disclosure obligation follows the same
  decision already taken for the report surface in CHG-B9-01, which replaces the
  fixed cap with filter-driven narrowing and an explicit limit indicator.)*

  **Implementation conformance gap**: the current view truncates with
  `qs[:1000]` and returns no limit, count, or omission indicator
  (`backend/core/views.py::AuditLogViewSet`), so a reader cannot distinguish a
  complete result from a truncated one.
- **FR-023 — Source-address provenance**: A captured source address MUST be
  treated as indicative rather than authoritative. A forwarded-for header MUST be
  trusted only when the request arrives from a configured trusted proxy;
  otherwise the direct peer address MUST be recorded. A source address MUST NOT
  be the sole basis for any authorization, identity, or security decision, and
  its limitations MUST be evident to anyone reading the AuditLog. Capture remains
  subject to FR-015 minimization and the FR-017 six-month window.
  *(Source: stakeholder clarification, 2026-08-12; current derivation recorded as
  observation in CAND-008.)*

  **Implementation conformance gap**: `backend/core/services.py::client_ip`
  trusts `HTTP_X_FORWARDED_FOR` unconditionally and records its first entry. That
  header is client-supplied on any request not passing through a trusted proxy,
  so a recorded address can be chosen by the caller. Entries created outside the
  shared helper omit the field entirely (CAND-008).

### Current-System Contract Candidates — Not Accepted Requirements

- **CAND-001**: A Notification currently contains a recipient, message of up to
  500 characters, optional destination of up to 255 characters, textual state
  defaulting to `Unread`, and creation time.
- **CAND-002**: The current Notification interface exposes record identity,
  message, destination, state, and creation time while omitting the recipient
  identity from the returned representation.
- **CAND-003**: Current Notification list, detail, unread count, mark-one-read,
  and mark-all-read operations are available to any authenticated active User
  without an additional permission code and are scoped to that User's records.
- **CAND-004**: Current Notification records are ordered newest first. The list
  is unpaginated, has no filter contract beyond recipient scoping, and offers no
  recipient-facing delete or content-edit operation.
- **CAND-005**: Current mark-one-read changes the selected record to `Read`;
  mark-all-read changes every `Unread` record in the current User's result set
  to `Read`.
- **CAND-006**: The current Navbar requests unread count immediately and every
  30 seconds, suppresses request failures, and links all authenticated Users to
  the Notifications page. Read-state actions reload that page's list but do not
  immediately refresh the shared Navbar badge.
- **CAND-007**: An AuditLog row currently contains row identity, optional User
  reference, username snapshot, action, module, old value, new value, event
  date/time, and IP address.
- **CAND-008**: The shared current logging helper derives username from the
  authenticated account, User from its linked profile, and source address from
  the first forwarded address or direct remote address. Some authentication
  events create rows directly and therefore omit shared-helper fields.
- **CAND-009**: Current direct Audit Trail access is read-only, returns at most
  1,000 newest matching rows, supports exact module filtering and
  case-insensitive partial username filtering, and is restricted to Admin or a
  platform superuser.
- **CAND-010**: The current Audit frontend displays date, username, action,
  module, old value, new value, and IP address but does not send its own module
  or username filters to the backend.
- **CAND-011**: The current report catalog labels AuditLog data “Asset Audit
  Report,” returns the newest 1,000 global rows, and makes view and export
  operations available through `report_access`; this conflicts with direct
  Audit Trail access and with the deferred physical-audit terminology boundary.
- **CAND-012**: Current AuditLog creation is explicit in selected authentication,
  User, Role, Asset, Procurement, Service Record, Checkout, Transfer, AMC, file,
  condition, and Setting mutation paths rather than universal. Department,
  Location, catalog-master mutations, Notification reads, and many read or
  rejected actions have no visible shared audit call.
- **CAND-013**: Current Notification creation persists an in-app row only. No
  email-sending implementation was found in the reviewed backend or frontend.
- **CAND-014**: Current User deletion cascades to the User's Notifications;
  AuditLog instead permits its User reference to become empty while retaining
  its username snapshot and other event data.
- **CAND-015**: Current shared helpers expose no delivery receipt, retry,
  deduplication key, failure record, or recovery workflow. Caller ordering means
  no single atomicity or partial-success behavior can be inferred.

### Authorization and Lifecycle Requirements

- **ALR-001 — Accepted boundary**: B8 MUST NOT authorize or execute the
  capability action that produces a trigger. The owning capability's backend
  authorization remains authoritative.
- **ALR-002 — Test-backed boundary**: For the selected current Notification
  tests, the owning capability supplies a specific recipient and the shared
  facility retains a record for that recipient. No broader Role or Department
  visibility rule is established by those tests.
- **ALR-003 — Stakeholder-confirmed access**: Admin and IT Manager have global
  AuditLog view, filter, and export access. All other named and custom Roles are
  denied even when granted `report_access`; the same authorization applies to
  direct Audit Trail and report/export surfaces, and backend enforcement is
  authoritative.
- **ALR-004 — Accepted lifecycle boundary**: Notification and AuditLog effects
  MUST NOT independently change Asset status, condition, Custodian, Department,
  Checkout, Transfer, Service Record, Procurement, Warranty, or AMC state.
- **ALR-005 — Stakeholder-confirmed failure boundary**: A required AuditLog entry
  and its business action form one atomic operation. Notification delivery is
  outside that atomic boundary: a delivery failure leaves completed business
  work intact and follows the retry, deduplication, and operator-visibility
  contract in FR-012. Existing stricter trigger requirements in an owning
  accepted specification remain authoritative for that capability.
- **ALR-006 — Governance-backed**: Frontend route or menu visibility MUST NOT be
  treated as authorization evidence; any accepted access contract must be
  enforced at the protected data boundary.

### Key Entities

- **Notification**: A current recipient-addressed in-app message with message
  text, optional destination, `Unread`/`Read` state in observed use, and
  creation time. This version is in-app only and follows FR-012 failure
  guarantees. Read records are retained for 90 days, Unread records for 1 year,
  and all are deleted with their recipient; email delivery is deferred to a
  future version.
- **Notification Recipient**: The User to whom one Notification record belongs.
  Capability-specific recipient eligibility is outside B8.
- **Notification Trigger**: A capability-owned instruction identifying a
  business event, intended recipient or recipients, message meaning, and
  optional destination, recorded in the owning B3–B7 trigger matrix. B8 owns
  shared behavior after this boundary and cannot invent or suppress a valid
  trigger.
- **Read State**: The state used to calculate unread count and control
  mark-one/all-read behavior. The accepted state set, the one-way `Unread` →
  `Read` transition, the idempotence of marking an already-`Read` record, the
  definition of the unread count, and the retained transition time are specified
  in FR-019. CAND-001 and CAND-005 record the corresponding current behavior as
  observation.
- **AuditLog Entry**: A current operational event record containing actor
  references or snapshots, action/module labels, before/after text, event time,
  and source address. The accepted minimum event categories are defined in
  FR-014 and old/new-value privacy in FR-015. Entries and minimized actor
  identity are retained for 2 years; source IP is removed after 6 months.
- **Audit Trail**: The operational presentation of AuditLog entries, available
  globally only to Admin and IT Manager under ALR-003.
- **“Asset Audit Report”**: A B9-owned current report that presents AuditLog
  entries. Its name does not mean a physical Asset audit, and its current
  `report_access` authorization is a conformance gap against ALR-003.
- **Setting**: Administrative key/value configuration. Current SMTP-labeled
  Settings are configuration evidence only and do not establish email delivery.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 13 selected notification and authorization tests pass in one
  verification run, including seven positive recipient-side-effect cases, two
  expiry silence cases, and four privacy/authorization cases.
- **SC-002**: 100% of in-scope Notification list, recipient, state, unread-count,
  mark-one, mark-all, Navbar, AuditLog field, filter, limit, direct-access,
  report-access, and Settings observations are labeled test-backed,
  implementation-only, or unresolved and cite repository evidence.
- **SC-003**: For every selected test-backed Notification trigger, a reviewer
  can identify exactly one owning capability and its matrix entry for the
  business event, recipient category, message meaning, destination, and any
  additional audit detail without B8 defining a new business trigger.
- **SC-004**: A two-User current-system verification of list, unread count,
  mark-one, and mark-all produces zero returned or changed records belonging to
  the other User.
- **SC-005**: In an AuditLog view review, 100% of results satisfy FR-021 —
  ordered newest first, exact on module, case-insensitive partial on username,
  and conjunctive when both are supplied — and 100% of results reaching the
  FR-022 limit disclose both the limit and that older matching events were
  omitted. A filter matching nothing returns an empty result in 100% of cases
  and an unfiltered set in 0%.
- **SC-006**: A scope review finds zero claims that SMTP Settings prove email
  delivery and zero claims that AuditLog or “Asset Audit Report” is a physical
  Asset audit.
- **SC-007**: Stakeholder clarification has resolved 100% of the five original
  B8 acceptance blockers: delivery channels, failure behavior, mandatory audit
  events, AuditLog access, and retention.
- **SC-008**: In failure-path verification, 100% of business actions missing a
  required AuditLog entry leave business data unchanged; 100% of failed
  Notification deliveries leave completed business work intact, are visible to
  operators, and retry without duplicate recipient records.
- **SC-009**: In unread-polling failure verification, 100% of failures retain
  the last known count, visibly mark it stale, offer manual retry, and produce
  zero Notification read-state changes.
- **SC-010**: In a complete event-matrix review, 100% of FR-014 mandatory events
  produce exactly one AuditLog entry, 0% of excluded routine reads or
  Notification read-state actions produce one, and 0% of entries contain an
  FR-015 prohibited value.
- **SC-011**: In an AuditLog authorization matrix, Admin and IT Manager succeed
  for 100% of view, filter, and export cases; every other Role, including a User
  with `report_access`, is denied without receiving AuditLog data; 100% of
  allowed access and rejected attempts create an AuditLog entry.
- **SC-012**: Retention verification removes 100% of source IP values older than
  6 months, AuditLog entries older than 2 years, Read Notifications more than 90
  days past their Read transition, Unread Notifications older than 1 year, and
  Notifications belonging to a deleted User.
- **SC-013**: In a B3–B7 ownership review, 100% of capability audit and
  Notification triggers map to exactly one accepted owning matrix; B8 invents
  or suppresses 0 valid business triggers and applies its shared contract to
  100% of valid supplied triggers.

## Assumptions

- This is a documentation-only AS-BUILT baseline. It records current evidence
  and accepted adjacent intent without changing application code.
- `User` means the B1 User profile when describing current Notification
  recipients; the separate linked login-account representation remains B1
  implementation detail.
- B2's stakeholder-confirmed audit/no-Notification rules and B6's
  stakeholder-confirmed trigger rules are current Draft inputs. B8 does not
  independently redefine them, and B8 acceptance depends on the owning
  baselines completing their own acceptance reviews.
- B3, B4, B5, B6, and B7 each own an explicit audit and Notification trigger
  matrix. Current tests prove shared-facility use but do not establish a matrix
  entry until the owning baseline accepts it.
- B9 owns report naming, presentation, export formats, and report catalog
  behavior. B8 includes the current “Asset Audit Report” only because it exposes
  AuditLog data under a different access rule.
- Current frontend surfaces have no dedicated behavioral tests. Their behavior
  is implementation-only even where it aligns with backend code.
- AuditLog, source-IP, Notification-state, and User-deletion retention follow
  FR-017. Export copies remain subject to the same access and privacy rules;
  downstream file disposal mechanics are a planning concern.
- Required AuditLog writes are atomic with their owning business action;
  Notification failures are non-blocking, automatically retried without
  duplicates, and operator-visible; unread polling failures retain and visibly
  stale the last known count with manual retry. Detailed retry scheduling and
  operator workflow are planning concerns within this accepted behavior.

## Baseline Evidence and Unresolved Conflicts *(Brownfield Baseline only)*

### Accepted Intent

- B8 owns shared in-app Notification/read-state and operational AuditLog
  facilities while business trigger rules remain capability-specific:
  `ROADMAP.md`, B8.
- B8 Notification delivery is in-app only in this version; email delivery is
  deferred to a future version: stakeholder clarification dated 2026-08-04.
- The risk-based mandatory event set and minimized old/new-value contract are
  defined by stakeholder clarification dated 2026-08-04 in FR-014 and FR-015.
- Admin/IT Manager global AuditLog access and the 2-year AuditLog, 6-month source
  IP, 90-day Read Notification, and 1-year Unread Notification retention rules
  are defined by stakeholder clarification dated 2026-08-04 in FR-016 and
  FR-017.
- B3–B7 explicit trigger-matrix ownership and B8's prohibition on inventing or
  suppressing valid capability triggers are defined by stakeholder
  clarification dated 2026-08-04 in FR-018.
- Physical Asset audits are deferred and distinct from operational AuditLog:
  `CONTEXT.md`, **Lost**; `ROADMAP.md`, F1.
- Proactive Warranty/AMC alerts and their intended IT audiences exist as
  adjacent business intent: `CONTEXT.md`, **AMC**. Their current B8 delivery
  channel and shared failure guarantees are resolved by the stakeholder
  clarifications dated 2026-08-04; B7 still owns trigger timing and recipients.
- B2 owns its complete accepted audit and no-Notification trigger contract:
  `specs/001-asset-register-lifecycle-baseline/spec.md`, ALR-011 and Accepted
  Asset Audit and Notification Effects.
- B6 owns its stakeholder-confirmed audit and Notification trigger contract
  while assigning shared delivery and AuditLog behavior to B8:
  `specs/002-procurement-vendor-catalog-baseline/spec.md`, FR-023, FR-024, and
  ALR-009.
- Brownfield evidence must not be promoted to product intent without explicit
  acceptance: `.specify/memory/constitution.md`, Principle III.

### Verified Behavior Evidence

- **AS-001**: Checkout creates a Notification for the new Custodian:
  `backend/assets/tests.py::CheckoutLifecycleTests::test_check_out_notifies_the_new_custodian`.
- **AS-002**: Transfer request creates a Notification for a User with approval
  permission:
  `backend/assets/tests.py::TransferLifecycleTests::test_request_transfer_notifies_users_with_approval_permission`.
- **AS-003**: Opening a Service Record creates a Notification for the previous
  Custodian:
  `backend/assets/tests.py::ServiceRecordLifecycleTests::test_open_service_notifies_the_previous_custodian`.
- **AS-004**: AMC renewal and End Support create Notifications for an IT
  Manager:
  `backend/assets/tests.py::AmcActionTests::test_renew_amc_sets_dates_and_notifies_it_manager`;
  `backend/assets/tests.py::AmcActionTests::test_end_amc_support_sets_status_and_notifies_it_manager`.
- **AS-005 and AS-006**: Exact-threshold Warranty and active-AMC alerts notify,
  while an off-threshold Warranty and ended AMC are silent:
  `backend/assets/tests.py::ExpiryAlertTests`.
- Administrative Settings remain protected from an ordinary User and from a
  User with only `settings_access`:
  `backend/accounts/tests.py::PrivacyAuthorizationTests`.
- The 13 selected tests above passed on 2026-08-04 using the repository-local
  test environment. `backend/core/tests.py` contains no dedicated Notification
  or AuditLog behavioral tests.

### Implementation-Only Observations

- Notification and AuditLog persistence fields and deletion relationships:
  `backend/core/models.py`.
- Shared current User/profile lookup, source-address capture, explicit AuditLog
  creation, and in-app-only Notification creation:
  `backend/core/services.py`.
- Recipient-scoped Notification list, unread count, mark-one/all-read, direct
  AuditLog Admin restriction, module/username filters, newest-first 1,000-row
  cap, and read-only access:
  `backend/core/views.py`;
  `backend/core/serializers.py`;
  `backend/core/urls.py`.
- Selected authentication, User, and Role audit calls, including direct login
  records that do not use shared source-address capture:
  `backend/accounts/views.py`.
- Selected Asset, Procurement, Service Record, Checkout, Transfer, AMC, file,
  and condition audit calls and IT Manager recipient lookup:
  `backend/assets/views.py`.
- Checkout/check-in, Transfer, Service Record, and expiry Notification call
  sites and current destinations:
  `backend/assets/checkout.py`;
  `backend/assets/transfer.py`;
  `backend/assets/service.py`;
  `backend/assets/alerts.py`.
- Notification list/read controls and current linked-message rendering:
  `frontend/src/pages/Notifications.jsx`.
- Navbar unread-count polling, suppressed errors, badge, and route:
  `frontend/src/components/navbar/Navbar.jsx`.
- Direct Audit Trail columns and loading behavior:
  `frontend/src/pages/Audit.jsx`.
- Admin-only Audit and Settings routes and globally authenticated Notifications
  route:
  `frontend/src/App.jsx`;
  `frontend/src/components/ProtectedRoute.jsx`;
  `frontend/src/components/navbar/Menu.jsx`;
  `frontend/src/components/navbar/ShortMenu.jsx`.
- Editable SMTP-labelled Settings with no corresponding email sender found:
  `frontend/src/pages/Settings.jsx`;
  `backend/core/views.py`.
- Global AuditLog report and export access through `report_access`, plus the
  misleading “Asset Audit Report” label:
  `backend/reporting/views.py`;
  `frontend/src/pages/Reports.jsx`.
- The consolidated current-system evidence and its E2/R1 assessment:
  `docs/research/itams-current-system-baseline.md`, sections 2.8, 3.6, and 5.

### Unresolved Conflicts

None within B8's shared-facility scope after the 2026-08-04 clarifications.
Asset-related Notifications currently point to `/asset/{id}` while the frontend
expects `/asset/detail/{id}`; this remains an implementation conformance finding
for the owning B3–B7 matrices to accept or correct, not a B8 trigger decision.

### Implementation Conformance Update

**Date**: 2026-08-12. **Commits**: `538c3a8`, `070c8c2`. Records where the
implementation now conforms to requirements this baseline already states. No
requirement changes; the observations above are preserved as the dated review
record.

| Observation | Status | Evidence |
| --- | --- | --- |
| AuditLog reachable through `report_access` | **Closed** | The audit report served the same rows as the Admin-only `/audit/` endpoint — including actor identity and source IP — to any `report_access` holder, which the B1 matrix grants to IT Staff and Viewer. It is now gated to administrative authority and hidden from the report catalogue for readers who cannot open it, matching FR-016 rather than routing around it (`backend/reporting/views.py::ADMIN_ONLY_REPORTS`; `backend/core/permissions.py::is_admin`). Reading it now also writes its own AuditLog entry, so views are audited and not only exports. Tests: `AuditReportAccessTests` (6), including one asserting the other nine reports stay open to `report_access`. |
| Notification fan-out cost | **Closed (non-functional)** | Group notifications are issued in one insert (`backend/core/services.py::notify_many`), applied to the expiry sweep, Service Record closure, Transfer requests, and AMC decisions. The daily sweep over 20 assets × 10 recipients fell from 227 queries to 27. Message content, recipients, and read-state semantics are unchanged. |
| `/asset/{id}` vs `/asset/detail/{id}` link target | **Open** | Unchanged, and still owned by the B3–B7 trigger matrices. |

FR-016's grant is to **Admin and IT Manager**; the implementation currently
admits Admin only, because `/audit/` itself has always been Admin-only. The fix
made the report match the endpoint rather than widening either. Extending both to
IT Manager remains outstanding conformance work against this baseline, and would
be better served by a dedicated permission code than by a Role-name test.

**Provenance note**: these changes were written implementation-first and covered
by tests afterwards, not through the red-green loop Principle IV requires.

## Out of Scope *(mandatory)*

### Adjacent Baseline Ownership

- Authentication, Users, Roles, permission-code administration, Department,
  Location, and general data-scope rules: B1. B8 consumes the User recipient and
  actor identity boundary.
- Asset-register mutations and their accepted audit/no-Notification rules: B2.
- Checkout/check-in trigger rules: B3.
- Transfer trigger and recipient rules: B4.
- Service Record trigger rules: B5.
- Procurement, Vendor, and catalog trigger rules: B6.
- Warranty, AMC, expiry thresholds, scheduling, renewal, End Support, and their
  trigger/recipient rules: B7.
- Report names, report catalog behavior, report filtering, and PDF/Excel/CSV
  exports: B9. Their current AuditLog exposure is recorded only as B8 access
  evidence.

### Explicitly Unresolved Rather Than Accepted

- Exact B3–B7 audit and Notification trigger declarations remain unresolved in
  their owning capability baselines and are not B8 requirements.
- Capability-owned Notification destination correctness, including the current
  Asset-detail route mismatch, must be resolved in the relevant owning matrix.

### Explicitly Deferred or Excluded

- Scheduled or periodic physical Asset audits by Department or Location.
- Treating operational AuditLog entries or the current “Asset Audit Report” as
  physical inspection records.
- Email Notification delivery, which is deferred for consideration in a future
  version; SMTP-labelled Settings do not enable or imply it in this version.
- Application-code, test-code, database, route, UI, scheduler, or configuration
  changes in this documentation-only specification run.
