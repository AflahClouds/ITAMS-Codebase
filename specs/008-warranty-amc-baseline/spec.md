# Feature Specification: AS-BUILT Warranty, AMC, and Expiry Actions Baseline

**Feature Branch**: `docs/baseline-spec-migration`

**Created**: 2026-08-05

**Status**: Draft

**Input**: User description: "Create an AS-BUILT Brownfield Baseline
specification for ROADMAP.md entry B7: Warranty, AMC, and expiry actions. Cover
Warranty/AMC distinction, AMC Vendor and history, deliberate no-AMC,
Incomplete/Active/Ended states, renewal, End Support, reasons, validation,
30/15/7-day alert triggers, recipients, and IT Manager notification. Keep C4 and
C5, deliberate no-AMC representation, initial-entry validation, Vendor capture,
notification channel, and production scheduling guarantees unresolved. Do not
present runserver-only scheduling as reliable production delivery. Do not modify
application code."

## Clarifications

### Session 2026-08-05

- Q: How is deliberate no-AMC represented, and what should the AMC flag report after End Support? → A: The flag stays derived, but from the current contract only: true when the latest contract is `Active` or `Incomplete`, false when it is `Ended` or absent. No deliberate-versus-never-decided distinction is introduced, which diverges from `CONTEXT.md` and requires a glossary reconciliation before acceptance.
- Q: What validation applies to initial AMC entry and to Warranty dates? → A: Initial AMC entry enforces the same rules as renewal — both dates or neither, real dates, end after start — and Warranty requires end after start when both are present while either may be recorded alone; neither is tied to purchase or arrival dates.
- Q: Should an AMC contract record its Vendor, and what rules govern renewal and history? → A: A managed B6 Vendor is required on any dated contract and optional while `Incomplete`; renewal captures the Vendor for the new contract and may change it; history is append-only and renewal's supersede marker is recorded separately from the operator's End Support reason.
- Q: Who receives expiry alerts and AMC decision notifications, and through which channel? → A: Expiry alerts go to every active holder of `asset_custody_manage` and AMC decision notifications to every active holder of the IT Manager grant, both selected by permission rather than Role display name; delivery is in-app only for this version, consistent with Draft B8 FR-008.
- Q: What production scheduling, timezone, deduplication, and recovery guarantees must expiry alerts meet? → A: Keep the scheduler in-process but start it under the real production server as well, with mutual exclusion so exactly one worker runs each execution; evaluate thresholds in one configured organizational timezone; record each Asset/coverage/threshold alert once so reruns are no-ops; and catch up thresholds crossed during downtime on the next run, with failed or overdue runs operator-visible.

## Specification Lineage *(mandatory)*

**Type**: Brownfield Baseline

**Roadmap Reference**: `ROADMAP.md`, entry B7 — Warranty, AMC, and expiry
actions; durable feature directory `specs/008-warranty-amc-baseline/`.

**Extends**: None. This is the initial B7 baseline.

**Supersedes**: None.

**Reciprocal Links**: `ROADMAP.md` already reserves
`specs/008-warranty-amc-baseline/` for B7 and must link the created directory
when the B7 row moves to `R3 — draft review`. After this Draft is accepted, any
later substantive change must use a new feature directory and record reciprocal
`Extends`, `Supersedes`, or `Superseded by` lineage instead of editing accepted
requirement content here.

**Dependencies**:

- Accepted B2 Asset register and lifecycle baseline
  (`specs/001-asset-register-lifecycle-baseline/`, accepted 2026-07-29) for
  Asset identity, terminal statuses, the Asset write permission contract, and
  the rule that B2 register mutations create AuditLog entries and no
  Notifications.
- Draft B1 identity and access baseline
  (`specs/003-identity-access-baseline/`) for Roles, permission codes, named
  Role grants, and data visibility.
- Draft B6 Procurement, Vendor, and catalog masters baseline
  (`specs/002-procurement-vendor-catalog-baseline/`) for the managed Vendor
  identity an AMC would refer to.
- Draft B8 Notifications and AuditLog baseline
  (`specs/004-notifications-audit-baseline/`) for shared delivery, channel,
  failure behavior, audit minimums, and retention.
- Draft B5 Service Record lifecycle baseline
  (`specs/007-service-record-baseline/`) only as a boundary: a Service Record is
  not evidence of a Warranty or AMC claim, and B5 records no relationship to
  either.

## Domain Alignment *(mandatory)*

**Canonical Terms**:

- **Warranty** is the manufacturer's coverage period on an Asset, expressed as a
  warranty start date and a warranty end date. It is fixed by the manufacturer.
- **AMC (Annual Maintenance Contract)** is a separate, optional, paid
  maintenance contract on an Asset with its own start and end dates. It is a
  different contract from Warranty, often with a different third party and a
  different date range, and the two MUST NOT be conflated.
- **AMC contract** is one entry in an Asset's AMC history. An Asset may have
  several over time; only the current one describes today's coverage.
- **`Incomplete`**, **`Active`**, and **`Ended`** are AMC contract states.
  `Incomplete` means the AMC exists but its dates have not been entered yet.
  `Ended` means the contract is deliberately discontinued or superseded. None of
  the three is an Asset status.
- **No current AMC** means the Asset's latest contract is `Ended` or it has no
  contract at all. It excludes the Asset from AMC expiry alerts. Under FR-006 it
  does not distinguish an Asset deliberately excluded from one for which nobody
  has decided; `CONTEXT.md` describes a stronger deliberate-decision meaning that
  FR-029 requires to be reconciled.
- **Renew** is the AMC action that records new contract dates and supersedes the
  previous contract while preserving it in history.
- **End Support** is the AMC action that deliberately discontinues the contract
  with a recorded reason. A contract MUST NOT become discontinued merely because
  its end date passed unattended.
- **Expiry alert** is a proactively pushed message issued 30, 15, and 7 days
  before a Warranty or AMC end date. It is not a dashboard panel someone must
  remember to open.
- **Vendor** is the first-class managed third-party identity owned by B6. Whether
  an AMC records one is unresolved in this Draft.
- **AuditLog** is an operational event record and MUST NOT be described as a
  physical Asset audit.

**Relevant Decisions**:

- `CONTEXT.md`, **Warranty**: manufacturer coverage with start/end dates,
  distinct from AMC, which is a different contract often with a different vendor
  and date range.
- `CONTEXT.md`, **AMC**: a separate optional paid contract with its own dates; a
  `has_amc` flag distinct from the dates, where `False` means the Asset
  deliberately has no AMC (dates stay empty, excluded from alerts and
  data-completeness reports) and `True` with empty dates means the AMC exists
  but has not been entered yet (flagged as incomplete); AMC previously existed
  only as an uploaded document type with no queryable dates.
- `CONTEXT.md`, **AMC**: expiry alerts for both Warranty and AMC are proactively
  pushed, not merely visible on a dashboard, and fire at 30, 15, and 7 days
  before expiry to both IT Manager and IT Staff.
- `CONTEXT.md`, **AMC**: IT Staff is expected to act on an AMC alert before the
  expiry date by explicitly changing the AMC's status — either Renew with new
  dates or End Support with a recorded description/reason — rather than letting
  the dates lapse unattended. Either action notifies the IT Manager with the
  description of what was done.
- `CONTEXT.md`, **AMC**: Warranty dates are manufacturer-fixed and are not
  renewable or endable; the status/renew/end workflow is AMC-specific.
- Accepted B2 FR-001, FR-008, and the Asset permission contract: Warranty dates
  are Asset register data, terminal statuses have left circulation, and Asset
  updates require `asset_edit` held by Admin, IT Manager, and IT Staff.
- Accepted B2 ALR-011 and Accepted Asset Audit and Notification Effects: every
  successful B2 Asset mutation creates an AuditLog entry and B2 register actions
  create no Notifications. B7 owns its own AMC decision Notifications.
- Draft B8 FR-002, FR-008, FR-011, FR-012, FR-014, FR-015, and FR-018: shared
  in-app delivery and its current channel limit, atomic required audit, and the
  rule that each capability owns its trigger matrix.
- Draft B6 FR-003, FR-019, and FR-022: Vendor is a managed identity with a
  normalized unique name; a flagged legacy Vendor is unavailable for new
  selection.
- Draft B5 FR-001 and Out of Scope: a Service Record is one repair event and
  carries no Warranty or AMC claim relationship.
- `ROADMAP.md` decisions C4 and C5 are resolved by the stakeholder
  clarification dated 2026-08-05, together with initial-entry validation, AMC
  Vendor capture, and notification channel,
  resolved by the same session and recorded as U-002 through U-005.

**Evidence Classification**:

- **Accepted intent** comes only from `CONTEXT.md`, an accepted dependency
  baseline, or an explicit recorded stakeholder decision. No ADR governs B7.
- **Test-backed current behavior** is reproducible current-system evidence. It
  demonstrates behavior but is not product intent by itself.
- **Implementation-only observation** is visible in backend code, a migration,
  or a frontend surface without a dedicated behavioral test and remains
  unaccepted.
- **Unresolved** means this Draft deliberately does not choose a rule and
  records the decision for stakeholder clarification.

**Lifecycle and Actors**:

| Stage | Actor and permission | Accepted or evidenced effect |
| --- | --- | --- |
| Read Warranty and AMC state and history | `asset_view` plus B1 visibility | Warranty dates, current AMC state, and AMC history are readable with the Asset |
| Record or correct Warranty dates | Admin, IT Manager, or IT Staff; `asset_edit` | Warranty dates are Asset register data with no status, renew, or end workflow |
| Record an initial AMC, complete or incomplete | Admin, IT Manager, or IT Staff; `asset_edit` | Create the Asset's first AMC contract as `Active` when dates are known, or `Incomplete` when they are not |
| Renew an AMC | IT Staff or IT Manager as the expected actor; `asset_edit` at the authorization boundary | Atomically end the current contract as superseded and create a new `Active` contract with the new dates, preserving history |
| End AMC Support | IT Staff or IT Manager as the expected actor; `asset_edit` at the authorization boundary | Mark the current contract `Ended` with a recorded reason, deliberately and never by date lapse |
| Receive an expiry alert | Every IT Manager and IT Staff | A pushed alert at exactly 30, 15, and 7 days before a Warranty or AMC end date |
| Receive an AMC decision notification | IT Manager | One notification per Renew or End Support carrying the description of what was done |

AMC contract state is the authoritative record of coverage. An expiry alert is a
prompt to act, not a state change: neither the alert nor the passing of an end
date may by itself move a contract to `Ended`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Keep Warranty and AMC Separately Legible (Priority: P1)

An authorized User records the manufacturer's warranty period and, separately,
any paid maintenance contract, and can always tell which coverage is which.

**Why this priority**: Conflating the two produces false confidence that an
Asset is covered. They are different contracts, with different parties, dates,
and renewal rules.

**Independent Test**: Record an Asset with a warranty period and an AMC whose
dates differ, then read the Asset and confirm both are present, distinct, and
independently labelled.

**Acceptance Scenarios**:

1. **AS-001 — Accepted intent**: **Given** an Asset, **When** its coverage is
   read, **Then** Warranty start/end and AMC start/end are separate values that
   may differ, and neither is derived from the other.
2. **AS-002 — Accepted intent**: **Given** an Asset with a Warranty, **When** a
   renew or end-support action is sought for that Warranty, **Then** none is
   offered: Warranty dates are manufacturer-fixed and have no status, renewal,
   or discontinuation workflow.
3. **AS-003 — Accepted intent**: **Given** AMC coverage, **When** it is
   recorded, **Then** it is optional and paid, has its own dates, and may
   involve a different third party from the Warranty.
4. **AS-004 — Accepted intent**: **Given** any user-visible surface, **When**
   Warranty and AMC are presented, **Then** they are labelled distinctly and
   neither is described using the other's terms.
5. **AS-005 — Accepted intent**: **Given** the historical model in which AMC
   existed only as an uploaded document, **When** AMC is recorded now, **Then**
   its dates are queryable data rather than only a file attachment.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-001 — Implementation-only**: **Given** the current Asset record,
   **When** coverage is stored, **Then** Warranty start/end live on the Asset
   while AMC lives in a separate contract history, and the Asset exposes derived
   AMC values taken from the most recently created contract.
2. **OBS-AS-002 — Implementation-only**: **Given** the current Asset detail
   surface, **When** coverage is displayed, **Then** Warranty appears inside a
   panel titled "Assignment & Warranty", which uses the `Assignment`
   terminology `CONTEXT.md` rejects. The label is owned by accepted B2 FR-004
   and `ROADMAP.md` C3.
3. **OBS-AS-003 — Implementation-only conformance gap (FR-031)**: **Given**
   Warranty dates, **When** they are entered, **Then** no validation requires an
   end date after a start date. The absence of a both-together rule and of any
   purchase-date constraint conforms to FR-031.

---

### User Story 2 — Represent Deliberate No-AMC and Not-Yet-Entered AMC Distinctly (Priority: P1)

An authorized User can record that an Asset deliberately has no AMC, and
separately that an AMC exists whose dates are still to be entered, and the two
never look the same.

**Why this priority**: `CONTEXT.md` defines the AMC flag precisely so that "we
decided against an AMC" is not mistaken for "someone has not filled this in
yet". Only the second should appear in completeness reporting and chasing.

**Independent Test**: Record one Asset as deliberately having no AMC and another
as having an AMC with no dates yet, then confirm each is distinguishable and
that only the second is flagged incomplete.

**Acceptance Scenarios**:

1. **AS-006 — Stakeholder-confirmed**: **Given** an Asset whose latest AMC
   contract is `Ended`, or which has no contract at all, **When** its AMC flag
   is read, **Then** it reports false, its AMC dates are empty, and it produces
   no AMC expiry alert.
2. **AS-007 — Accepted intent and test-backed**: **Given** an Asset whose AMC
   exists but whose dates have not been entered, **When** that state is
   recorded, **Then** exactly one `Incomplete` contract exists, its dates are
   empty, and it is visibly flagged as incomplete.
3. **AS-008 — Accepted intent and test-backed**: **Given** an `Incomplete`
   contract, **When** both dates are supplied later, **Then** the same contract
   becomes `Active` with those dates and no duplicate contract is created.
4. **AS-009 — Stakeholder-confirmed**: **Given** an Asset that never had an AMC
   and an Asset whose AMC was deliberately ended, **When** both are read,
   **Then** both report an AMC flag of false and both are excluded from AMC
   alerts; distinguishing the two is explicitly not required, and the `Ended`
   contract's reason remains the only record of the decision.
5. **AS-010 — Test-backed current behavior**: **Given** an Asset whose newest
   contract is `Incomplete` and whose older contract is fully dated and `Ended`,
   **When** the Asset's current AMC state is read, **Then** the `Incomplete`
   contract is treated as current and the stale `Ended` one is not.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-004 — Implementation-only conformance gap (FR-006)**: **Given** an
   Asset whose only AMC history is an `Ended` contract, **When** its AMC flag is
   read, **Then** it reports true, because the flag is computed as "any contract
   row exists" rather than from the current contract.
2. **OBS-AS-005 — Implementation-only, conforming**: **Given** an Asset that
   never had an AMC and an Asset whose AMC was deliberately ended, **When** both
   are read, **Then** they are indistinguishable. Under FR-006 this is accepted
   rather than a gap, though the second still reports true today because of
   OBS-AS-004.
3. **OBS-AS-006 — Implementation-only**: **Given** an Asset with AMC history,
   **When** the AMC flag is cleared on the Asset form, **Then** nothing happens:
   the current write path ignores a false flag. Under FR-006 the flag is derived
   rather than set, so clearing it is meaningless by design; the control that
   offers it is misleading.
4. **OBS-AS-007 — Implementation-only**: **Given** the current Asset detail
   surface, **When** an Asset has no AMC contract, **Then** it reads "This asset
   has no AMC", presenting the absence of data as a decision.

---

### User Story 3 — Renew an AMC Before It Lapses (Priority: P1)

Prompted by an expiry alert, IT records new contract dates. The previous
contract is closed as superseded and preserved, and the Asset's coverage moves
forward without a gap in the record.

**Why this priority**: Renewal is one of the two explicit responses
`CONTEXT.md` requires to an AMC alert, and it must not silently overwrite the
contract history that proves what was covered when.

**Independent Test**: Renew an AMC on an Asset that already has one, then
confirm two contracts exist, the older marked as superseded and the newer
`Active` with the new dates.

**Acceptance Scenarios**:

1. **AS-011 — Accepted intent and test-backed**: **Given** an Asset with an AMC,
   **When** an authorized User renews it with new dates, **Then** a new `Active`
   contract carries those dates and the Asset reports current AMC coverage.
2. **AS-012 — Accepted intent and test-backed**: **Given** the same renewal,
   **When** it completes, **Then** the previous contract is retained as `Ended`
   with a recorded reason identifying it as superseded by renewal, so the
   history remains intact.
3. **AS-013 — Accepted intent and test-backed**: **Given** a renewal, **When**
   its dates are validated, **Then** both dates are required, must be real
   dates, and the end date must be after the start date; any violation is
   rejected and no contract is created or changed.
4. **AS-014 — Accepted intent and test-backed**: **Given** an Asset in a
   terminal status, **When** a renewal is attempted, **Then** it is rejected and
   no AMC contract is created, because the Asset has left circulation.
5. **AS-015 — Accepted intent and test-backed**: **Given** an `Incomplete`
   contract, **When** a renewal is performed, **Then** the incomplete contract
   is superseded and a new `Active` contract exists, so an unfinished record
   does not block renewal.
6. **AS-016 — Accepted intent**: **Given** any renewal, **When** it completes,
   **Then** the contract closure and the new contract commit as one operation,
   leaving no interval in which the Asset has neither.

---

### User Story 4 — End AMC Support Deliberately, With a Reason (Priority: P1)

IT records that a maintenance contract is discontinued on purpose, saying why.
A contract never becomes discontinued merely because nobody acted.

**Why this priority**: `CONTEXT.md` is explicit that discontinuation is a
recorded decision, not an inference from lapsed dates. The reason is the
accountability record for why an Asset is no longer covered.

**Independent Test**: End support on an Asset with an active AMC and confirm the
contract is `Ended` with the supplied reason; then attempt it with no reason and
on an Asset with no current contract, and confirm both are rejected.

**Acceptance Scenarios**:

1. **AS-017 — Accepted intent and test-backed**: **Given** an Asset with a
   current AMC, **When** an authorized User ends support with a reason, **Then**
   the contract becomes `Ended` and the reason is recorded and readable.
2. **AS-018 — Accepted intent and test-backed**: **Given** an End Support
   attempt, **When** the reason is empty, **Then** it is rejected and the
   contract is unchanged.
3. **AS-019 — Accepted intent and test-backed**: **Given** an Asset with no
   `Active` or `Incomplete` contract, **When** End Support is attempted,
   **Then** it is rejected.
4. **AS-020 — Accepted intent and test-backed**: **Given** an `Incomplete`
   contract, **When** End Support is performed, **Then** it becomes `Ended`,
   so a planned AMC can be deliberately cancelled before its dates were ever
   entered.
5. **AS-021 — Accepted intent**: **Given** an AMC whose end date passes with no
   action, **When** its state is read, **Then** it is not `Ended`: the contract
   remains what it was and is reported as expired-but-unattended rather than
   deliberately discontinued.
6. **AS-022 — Accepted intent**: **Given** an `Ended` contract, **When** it is
   read, **Then** its recorded reason distinguishes a deliberate End Support
   from closure by renewal.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-008 — Implementation-only**: **Given** an Asset in a terminal
   status, **When** End Support is attempted, **Then** it succeeds, because the
   terminal-Asset guard applied to renewal is absent from End Support.
2. **OBS-AS-009 — Implementation-only**: **Given** a reason, **When** it is
   recorded, **Then** any non-blank text is accepted with no minimum length,
   controlled vocabulary, or distinction between the operator-supplied reason
   and the automatic supersede marker written by renewal.

---

### User Story 5 — Receive Proactive Expiry Alerts at 30, 15, and 7 Days (Priority: P1)

IT Manager and IT Staff are told, without opening anything, that an Asset's
Warranty or AMC is about to expire, early enough to act.

**Why this priority**: The whole point of recording dates is to act before they
pass. `CONTEXT.md` requires the alerts to be pushed, not merely displayed.

**Independent Test**: Set a Warranty end date and an active AMC end date to
exactly 30, 15, and 7 days ahead, run the expiry check for each, and confirm
recipients receive an alert; repeat off-threshold and with an ended contract and
confirm silence.

**Acceptance Scenarios**:

1. **AS-023 — Accepted intent and test-backed**: **Given** a Warranty end date
   exactly 30, 15, or 7 days away, **When** the expiry check runs, **Then** the
   accepted recipients receive an alert identifying the Asset and the remaining
   days.
2. **AS-024 — Accepted intent and test-backed**: **Given** an `Active` AMC whose
   end date is exactly 30, 15, or 7 days away, **When** the expiry check runs,
   **Then** the accepted recipients receive an equivalent alert.
3. **AS-025 — Accepted intent**: **Given** the accepted recipient rule, **When**
   an alert is issued, **Then** every IT Manager and every IT Staff member
   receives it.
4. **AS-026 — Accepted intent and test-backed**: **Given** a date that is not at
   a threshold, **When** the expiry check runs, **Then** no alert is issued.
5. **AS-027 — Accepted intent and test-backed**: **Given** an `Ended` AMC
   contract at a threshold, **When** the expiry check runs, **Then** no alert is
   issued, because a deliberately discontinued contract needs no action.
6. **AS-028 — Stakeholder-confirmed**: **Given** an Asset with no current AMC
   under FR-006, **When** the expiry check runs, **Then** it produces no AMC
   alert.
7. **AS-029 — Accepted intent**: **Given** the requirement that alerts are
   pushed, **When** delivery is designed, **Then** an alert MUST reach its
   recipients without a User opening a dashboard or report; a dashboard panel
   alone MUST NOT satisfy this requirement.
8. **AS-030 — Accepted intent**: **Given** an Asset in a terminal status,
   **When** the expiry check runs, **Then** no expiry alert is issued for it,
   because the Asset has left circulation and no action is available.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-010 — Implementation-only**: **Given** the current expiry check,
   **When** recipients are selected, **Then** every active User holding
   `asset_custody_manage` is notified, which includes Admin and any custom Role
   granting that code in addition to IT Manager and IT Staff.
2. **OBS-AS-011 — Implementation-only conformance gap (AS-030)**: **Given** a
   `Sold`, `Scrapped`, or `Lost` Asset whose Warranty end date is at a
   threshold, **When** the check runs, **Then** an alert is still issued,
   because Warranty alerts filter on the date alone with no Asset status
   condition.
3. **OBS-AS-012 — Implementation-only conformance gap (FR-039)**: **Given** the
   exact-date threshold design, **When** the check does not run on a given day,
   **Then** that day's thresholds are missed permanently, because no catch-up,
   range, or already-alerted record exists.
4. **OBS-AS-013 — Implementation-only conformance gap (FR-038)**: **Given** the
   check runs more than once in a day, **When** it repeats, **Then** duplicate
   alerts are produced, because no deduplication or already-sent marker
   exists.
5. **OBS-AS-014 — Implementation-only conformance gap (FR-036), not reliable
   production delivery**: **Given** the current in-process daily job configured
   for 07:00, **When** the application runs under a normal WSGI or ASGI
   deployment, **Then** the job is never scheduled at all, because startup is
   deliberately restricted to the development server command. Under a
   multi-worker deployment it would additionally fire once per worker. The
   current arrangement MUST NOT be presented as proactive production
   delivery.
6. **OBS-AS-015 — Implementation-only**: **Given** an alert, **When** its
   destination is followed, **Then** it points at `/asset/{id}` while the
   frontend Asset detail route is `/asset/detail/{id}`, so the destination does
   not resolve.
7. **OBS-AS-016 — Implementation-only conformance gap (FR-037)**: **Given** the
   threshold comparison, **When** it runs, **Then** it uses the server's local
   calendar date with no stated timezone rule, so the day an alert fires depends
   on server configuration.

---

### User Story 6 — Tell the IT Manager What Was Decided (Priority: P2)

Every AMC renewal and every End Support informs the IT Manager, with a
description of what was done.

**Why this priority**: `CONTEXT.md` makes IT Staff the actor and the IT Manager
the accountable reader. Without the notification the manager cannot tell whether
an alert was acted on or ignored.

**Independent Test**: Renew an AMC and end support on another Asset as IT Staff,
then confirm the IT Manager received one informative notification for each.

**Acceptance Scenarios**:

1. **AS-031 — Accepted intent and test-backed**: **Given** an AMC renewal,
   **When** it succeeds, **Then** the IT Manager receives a notification
   describing what was done, including the Asset and the new coverage period.
2. **AS-032 — Accepted intent and test-backed**: **Given** an End Support
   action, **When** it succeeds, **Then** the IT Manager receives a notification
   describing what was done, including the Asset and the recorded reason.
3. **AS-033 — Accepted intent**: **Given** either notification, **When** it is
   read, **Then** it identifies the Asset unambiguously and offers a destination
   that resolves to that Asset.
4. **AS-034 — Draft B8 dependency**: **Given** a required B7 AuditLog write
   fails, **When** the owning AMC action attempts to commit, **Then** the action
   also fails and no partial contract change is visible.
5. **AS-035 — Draft B8 dependency**: **Given** a notification delivery fails
   after a valid AMC action, **When** failure handling runs, **Then** the AMC
   work remains committed, the failure is operator-visible, and retry cannot
   create a duplicate recipient record.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-017 — Implementation-only**: **Given** the current IT Manager
   notification, **When** recipients are selected, **Then** they are active
   Users whose Role is literally named "IT Manager", so renaming that Role
   silently stops the notification, and a custom Role with equivalent authority
   never receives it.
2. **OBS-AS-018 — Implementation-only conformance gap (AS-033)**: **Given** the
   current renewal and End Support notifications, **When** they are delivered,
   **Then** they carry no destination at all, so the reader cannot navigate to
   the Asset from the message.
3. **OBS-AS-019 — Implementation-only**: **Given** a successful renewal or End
   Support, **When** it completes, **Then** one AuditLog entry is written
   carrying the same summary sentence as the notification, with no old value and
   no separate record of the previous contract's dates or state.
4. **OBS-AS-020 — Implementation-only**: **Given** a rejected or
   permission-denied AMC action, **When** it occurs, **Then** no AuditLog entry
   is written for it.
5. **OBS-AS-021 — Implementation-only**: **Given** initial AMC entry through the
   Asset write path, **When** a contract is created or completed that way,
   **Then** no AMC-specific AuditLog entry and no IT Manager notification are
   produced; only the accepted B2 Asset-mutation audit entry exists.

---

### User Story 7 — Read Coverage State and AMC History (Priority: P3)

An authorized reader can see current Warranty and AMC coverage, the contract
state, the reason a contract ended, and the sequence of contracts over time.

**Why this priority**: Reading is how recorded coverage becomes useful, but it
delivers no lifecycle guarantee of its own and depends on B1 visibility.

**Independent Test**: Read an Asset with several AMC contracts and confirm the
current state, the end reason, and the full history are available to an
authorized reader.

**Acceptance Scenarios**:

1. **AS-036 — Accepted intent**: **Given** an Asset with AMC history, **When**
   it is read, **Then** the current contract state, its dates, and the reason
   any contract ended are available, and superseded contracts remain readable.
2. **AS-037 — Draft B1 dependency**: **Given** a User with `asset_view`,
   **When** coverage data is requested, **Then** it follows B1 data visibility
   for the underlying Asset.
3. **AS-038 — Accepted intent**: **Given** any coverage surface, **When** it is
   presented, **Then** `Incomplete`, `Active`, and `Ended` are shown as AMC
   contract states and never as Asset statuses.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-022 — Implementation-only**: **Given** the current Asset detail
   surface, **When** AMC is displayed, **Then** the AMC History block appears
   only when more than one contract exists, so a single superseded-then-recreated
   history can be present without being shown as history.
2. **OBS-AS-023 — Implementation-only**: **Given** the current derived AMC
   values, **When** the Asset's current contract is selected, **Then** it is the
   most recently created contract rather than the one with the latest dates.
3. **OBS-AS-024 — Implementation-only**: **Given** the current AMC expiry
   report, **When** it lists contracts, **Then** it includes a Vendor column
   that is always empty because no code path records an AMC Vendor, and it
   labels a dateless contract as either incomplete or cancelled before dates
   were entered. Report content is owned by B9.
4. **OBS-AS-025 — Implementation-only**: **Given** the current Warranty report
   and Dashboard expiry panels, **When** they are produced, **Then** they count
   every Asset with a warranty end date regardless of Asset status, and the AMC
   panels count only `Active` contracts. Presentation is owned by B9.

### Edge Cases

- An AMC whose end date passes with nobody acting is the case the whole alert
  workflow exists to prevent. It MUST remain distinguishable from a deliberately
  ended contract, and reporting MUST NOT describe it as discontinued.
- An Asset can hold an `Incomplete` AMC indefinitely. Nothing currently chases
  it, and `CONTEXT.md` says exactly this state should be flagged in
  data-completeness reporting.
- Renewal writes an automatic reason onto the superseded contract, which shares
  one field with the operator-supplied End Support reason. A reader cannot tell
  the two apart except by reading the text.
- An `Incomplete` AMC contract may have no Vendor under FR-032, so an Asset can
  be known to need maintenance coverage before its provider is settled. Once
  dates exist a Vendor is required, so no dated contract lacks a provider.
- The migration that introduced AMC history deliberately dropped any legacy
  Asset whose AMC flag was set but whose dates were never completed. That is
  precisely the `Incomplete` case `CONTEXT.md` cares about, so pre-migration
  incomplete AMCs were not carried forward.
- Threshold evaluation uses one configured organizational timezone under
  FR-037, so an alert's firing day is deterministic. The current reliance on the
  server's local calendar date is a conformance gap.
- Catch-up under FR-039 and once-only recording under FR-038 are interdependent:
  re-evaluating a window after downtime is only safe because an already-issued
  alert can never be issued twice.
- An Asset with no AMC contract and an Asset whose AMC was deliberately ended
  are treated identically under FR-006. Neither is chased, and neither is
  identifiable as a deliberate decision — an accepted narrowing that FR-029
  requires be reconciled in `CONTEXT.md` before acceptance.
- An expiry alert names the Asset but not which contract or which coverage
  period it refers to, so an Asset with both a Warranty and an AMC expiring in
  the same window produces two similar messages.
- Deleting an Asset deletes its entire AMC history. Asset deletion is owned by
  B2; the coverage-history consequence is recorded here.
- A Vendor referenced by an AMC contract cannot be deleted, but because no code
  path sets an AMC Vendor, that protection is currently unreachable.
- A Service Record for a repair performed under warranty or AMC carries no link
  to the contract that covered it. B5 records no such relationship, so coverage
  cannot be reconciled against repair spend.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 — Accepted intent**: An Asset MUST be able to record the
  manufacturer's Warranty as a start date and an end date.
  *(Source: `CONTEXT.md`, **Warranty**.)*
- **FR-002 — Accepted intent**: AMC MUST be represented as a separate, optional,
  paid maintenance contract with its own start and end dates. Warranty and AMC
  MUST NOT be conflated, derived from each other, or presented as one coverage
  value.
  *(Source: `CONTEXT.md`, **Warranty** and **AMC**.)*
- **FR-003 — Accepted intent**: Warranty MUST NOT have a status, renewal, or
  discontinuation workflow. The state, renew, and End Support workflow is
  AMC-specific.
  *(Source: `CONTEXT.md`, **AMC**.)*
- **FR-004 — Accepted intent**: AMC coverage MUST be queryable data rather than
  only an uploaded document, so dates can drive alerts and reporting.
  *(Source: `CONTEXT.md`, **AMC**.)*
- **FR-005 — Accepted intent**: An AMC contract MUST be in exactly one of
  `Incomplete`, `Active`, or `Ended`. None of these MUST be presented as an
  Asset status.
  *(Sources: `CONTEXT.md`, **AMC**; current states are test-backed.)*
- **FR-006 — Stakeholder-confirmed**: An Asset's AMC flag MUST be derived from
  its current contract only: true when the latest contract is `Active` or
  `Incomplete`, and false when the latest contract is `Ended` or no contract
  exists. An Asset whose flag is false MUST keep AMC dates empty and MUST be
  excluded from AMC expiry alerts. No separately recorded deliberate-no-AMC
  decision MUST be introduced, and an Asset that never had an AMC MUST NOT be
  required to be distinguishable from one whose AMC was deliberately ended.
  *(Sources: stakeholder clarification, 2026-08-05. This narrows `CONTEXT.md`,
  **AMC**, which describes the flag as a deliberate decision; see FR-029 and
  U-001. The current derivation from any existing contract row is a conformance
  gap.)*
- **FR-007 — Accepted intent**: An AMC that exists but whose dates have not been
  entered MUST be representable as exactly one `Incomplete` contract and MUST be
  visibly flagged as incomplete rather than silently dropped or treated as
  absent.
  *(Sources: `CONTEXT.md`, **AMC**; current behavior is test-backed.)*
- **FR-008 — Accepted intent**: Supplying both dates for an `Incomplete`
  contract MUST complete that same contract as `Active` without creating a
  duplicate.
  *(Sources: `CONTEXT.md`, **AMC**; current behavior is test-backed.)*
- **FR-009 — Accepted intent**: Renewal MUST record new contract dates, create a
  new `Active` contract, and retain the superseded contract in history as
  `Ended` with a reason identifying it as closed by renewal.
  *(Sources: `CONTEXT.md`, **AMC**; current behavior is test-backed.)*
- **FR-010 — Accepted intent**: Renewal MUST require both dates, MUST reject
  unparseable dates, and MUST require the end date to be after the start date. A
  violation MUST be rejected with no contract created or changed.
  *(Sources: `CONTEXT.md`, **AMC**; current validation is test-backed. FR-030
  applies the same rules to initial entry.)*
- **FR-011 — Accepted intent**: Renewal MUST be rejected for an Asset in a
  terminal status, because a `Sold`, `Scrapped`, or `Lost` Asset has left
  circulation.
  *(Sources: accepted B2 FR-008; current rejection is test-backed.)*
- **FR-012 — Accepted intent**: End Support MUST mark the current contract
  `Ended`, MUST require a nonblank recorded reason, and MUST be rejected when no
  `Active` or `Incomplete` contract exists.
  *(Sources: `CONTEXT.md`, **AMC**; current behavior is test-backed.)*
- **FR-013 — Accepted intent**: An AMC contract MUST NOT become discontinued by
  its end date passing unattended. A lapsed contract MUST remain reportable as
  expired-and-unattended and MUST be distinguishable from a deliberately ended
  one.
  *(Source: `CONTEXT.md`, **AMC**.)*
- **FR-014 — Accepted intent**: Renewal and End Support MUST each apply their
  contract closure, creation, state, and reason effects as one atomic operation,
  so no intermediate coverage state is user-visible.
  *(Sources: `.specify/memory/constitution.md`, Principle II; accepted B2
  ALR-003; current renewal is atomic.)*
- **FR-015 — Accepted intent**: AMC history MUST be preserved. A renewal or End
  Support MUST NOT overwrite, delete, or make unreadable any earlier contract.
  *(Sources: `CONTEXT.md`, **AMC**; current history preservation is
  test-backed.)*
- **FR-016 — Accepted intent**: An expiry alert MUST be issued at exactly 30,
  15, and 7 days before a Warranty end date and before an `Active` AMC end date.
  *(Sources: `CONTEXT.md`, **AMC**; current threshold behavior is test-backed.)*
- **FR-017 — Accepted intent**: Expiry alerts MUST be proactively pushed to
  their recipients. A dashboard panel, report, or any surface a User must choose
  to open MUST NOT satisfy this requirement.
  *(Source: `CONTEXT.md`, **AMC**. FR-035 through FR-039 define what satisfies
  it in this version.)*
- **FR-018 — Stakeholder-confirmed**: Warranty and AMC expiry alerts MUST be
  issued to every active User holding `asset_custody_manage`. Under the B1
  grants that code covers IT Manager and IT Staff as `CONTEXT.md` requires, and
  additionally includes Admin and any custom Role holding it. Recipients MUST be
  selected by permission rather than by a Role's display name.
  *(Sources: stakeholder clarification, 2026-08-05; `CONTEXT.md`, **AMC**, for
  the named business recipients; the current recipient rule is test-backed for
  an `asset_custody_manage` holder and conforms.)*
- **FR-019 — Accepted intent**: An `Ended` AMC contract MUST NOT generate expiry
  alerts.
  *(Sources: `CONTEXT.md`, **AMC**, deliberate discontinuation; current silence
  is test-backed.)*
- **FR-020 — Accepted intent**: An Asset in a terminal status MUST NOT generate
  Warranty or AMC expiry alerts.
  *(Source: accepted B2 FR-008. The current Warranty alert path has no status
  condition and is a conformance gap.)*
- **FR-021 — Accepted intent with stakeholder-confirmed recipient rule**: A
  successful renewal and a successful End Support MUST each notify every active
  User holding the IT Manager grant with a description of what was done,
  identifying the Asset and, respectively, the new coverage period or the
  recorded reason. Recipients MUST be selected by permission rather than by a
  Role's display name, so renaming a Role MUST NOT silently stop delivery.
  *(Sources: `CONTEXT.md`, **AMC**; stakeholder clarification, 2026-08-05;
  current notifications are test-backed but the current name-based selection is
  a conformance gap.)*
- **FR-022 — Accepted authorization**: Recording Warranty dates, recording an
  initial AMC, renewing an AMC, and ending AMC support MUST require the Asset
  write authority `asset_edit`, held by Admin, IT Manager, and IT Staff. IT
  Staff MUST be able to perform renewal and End Support, because
  `CONTEXT.md` makes IT Staff the expected actor on an AMC alert.
  *(Sources: `CONTEXT.md`, **AMC**; accepted B2 Asset permission contract.)*
- **FR-023 — Accepted visibility dependency**: Reading Warranty dates, AMC
  state, and AMC history MUST require `asset_view` and MUST follow the B1
  visibility rules that apply to the underlying Asset.
  *(Source: accepted B2 ALR-009 and Draft B1.)*
- **FR-024 — Draft B8 ownership dependency**: B7 MUST publish and own an
  explicit trigger matrix covering each Warranty and AMC business event, its
  recipient-selection rule, message meaning, destination, and any audit detail
  beyond B8's shared minimum. B8 MUST own only shared delivery, read state,
  retry, access, and retention, and MUST NOT add, remove, or reinterpret a B7
  trigger. The matrix below is published for review; its recipient and
  destination rules depend on U-003 and U-005.
  *(Source: Draft B8 FR-002, FR-005, and FR-018.)*
- **FR-025 — Draft B8 audit dependency**: Every successful renewal, End Support,
  and initial AMC entry MUST create a minimized AuditLog entry committed
  atomically with the change, identifying the actor, the Asset, the contract
  state before and after, the dates involved, and the reason where one applies.
  Whether rejected and permission-denied AMC attempts also require an entry
  follows Draft B8 FR-014 once B8 is accepted.
  *(Sources: Draft B8 FR-011, FR-014, FR-015, and FR-018; accepted B2 ALR-011
  for the Asset-mutation entry that initial AMC entry already produces.)*
- **FR-026 — Accepted boundary**: A Service Record MUST NOT be treated as
  evidence of a Warranty or AMC claim, and B7 MUST NOT infer coverage from
  repair activity.
  *(Source: Draft B5 FR-001 and Out of Scope.)*
- **FR-027 — Evidence integrity**: Every Warranty or AMC behavior in this Draft
  that is observed only in implementation MUST remain labelled
  implementation-only until backed by a test or an explicit stakeholder
  decision, and MUST NOT be promoted into an accepted requirement by this
  specification run.
  *(Source: `.specify/memory/constitution.md`, Principle III.)*
- **FR-028 — Decision gate**: U-001 through U-005 were resolved by the
  stakeholder clarification dated 2026-08-05 and MUST NOT be reopened by
  observing current implementation behavior. Two acceptance preconditions
  remain: the `CONTEXT.md` reconciliation required by FR-029, and confirmation
  that the current development-server-only scheduling is treated as a
  conformance gap against FR-036 rather than as satisfying FR-017. The
  conformance gaps in U-006 are review findings, not grounds for weakening the
  requirement each one contradicts.
  *(Sources: `ROADMAP.md` decisions C4 and C5;
  `.specify/memory/constitution.md`, Principles I and III.)*
- **FR-029 — Stakeholder-confirmed reconciliation obligation**: Because FR-006
  does not represent deliberate no-AMC as a recorded decision, the
  `CONTEXT.md` **AMC** wording — "`has_amc = False` means the asset deliberately
  has no AMC" and the associated exclusion from data-completeness reports — MUST
  be reconciled with FR-006 in `CONTEXT.md` before this baseline is accepted.
  This specification MUST NOT be read as silently overriding that glossary
  entry, and AMC data-completeness reporting MUST NOT claim to identify Assets
  that still need an AMC decision while FR-006 stands.
  *(Sources: stakeholder clarification, 2026-08-05;
  `.specify/memory/constitution.md`, Principle I.)*
- **FR-030 — Stakeholder-confirmed**: Initial AMC entry MUST enforce the same
  date rules as renewal. Both dates MUST be supplied together or neither MUST be
  supplied; supplying neither MUST produce an `Incomplete` contract. Dates MUST
  be real parseable dates and the end date MUST be after the start date. A
  violation MUST be rejected without creating or changing any contract, so the
  Asset write path and the renew action MUST NOT apply different standards to
  the same values.
  *(Sources: stakeholder clarification, 2026-08-05; FR-010 for the renewal rules
  this aligns with. The current unvalidated initial-entry path is a conformance
  gap.)*
- **FR-031 — Stakeholder-confirmed**: A Warranty end date MUST be after its
  start date when both are present. Either date MAY be recorded alone, so
  partially known manufacturer coverage remains enterable. Warranty dates MUST
  NOT be constrained relative to the Asset's purchase or arrival dates.
  *(Sources: stakeholder clarification, 2026-08-05; `CONTEXT.md`, **Warranty**.
  The current absence of any Warranty validation is a conformance gap.)*
- **FR-032 — Stakeholder-confirmed**: An AMC contract MUST reference exactly one
  managed Vendor whenever it has dates. A contract in `Incomplete` MAY omit the
  Vendor, and supplying dates MUST require one. The Vendor MUST be a managed B6
  identity rather than free text, and MUST NOT be required to equal the Asset's
  Procurement Vendor, because an AMC is often held with a different third party.
  *(Sources: stakeholder clarification, 2026-08-05; `CONTEXT.md`, **Warranty**
  and **Vendor**; Draft B6 FR-003 and FR-019. No current code path records an
  AMC Vendor, which is a conformance gap.)*
- **FR-033 — Stakeholder-confirmed**: Renewal MUST capture the Vendor for the
  new contract and MAY record a different Vendor from the superseded one, so a
  change of maintainer is visible in history.
  *(Sources: stakeholder clarification, 2026-08-05; FR-032.)*
- **FR-034 — Stakeholder-confirmed**: AMC history MUST be append-only. Each
  superseded or ended contract MUST retain its own Vendor, dates, and state
  unchanged. The marker recording that a contract was superseded by renewal MUST
  be held separately from the operator-supplied End Support reason, so the two
  are distinguishable without reading their text.
  *(Sources: stakeholder clarification, 2026-08-05; `CONTEXT.md`, **AMC**;
  ALR-004. The current shared end-reason field is a conformance gap.)*
- **FR-035 — Stakeholder-confirmed**: Every B7 Notification and expiry alert
  MUST be delivered in-app only in this version and MUST address a specific
  User. Email MUST NOT be required and MUST NOT be inferred from the editable
  SMTP Settings; it remains deferred. An in-app alert that reaches a recipient's
  notification list without any dashboard or report being opened satisfies
  FR-017 for this version.
  *(Sources: stakeholder clarification, 2026-08-05; Draft B8 FR-008. The
  residual risk that a recipient does not open the application within the alert
  window is recorded under Assumptions.)*
- **FR-036 — Stakeholder-confirmed**: The expiry check MUST run on a daily
  schedule under the deployment the organization actually operates, including
  normal WSGI or ASGI server startup, and MUST NOT depend on the development
  server command. Exactly one execution MUST occur per scheduled run regardless
  of how many worker processes or hosts are running, enforced by mutual
  exclusion across them. Because scheduling remains inside the application
  process, alert production depends on that process being alive; the deployment
  MUST make a stalled or non-running scheduler operator-visible.
  *(Sources: stakeholder clarification, 2026-08-05; `CONTEXT.md`, **AMC**,
  proactive push. The current startup restriction to the development server and
  the absence of any cross-worker exclusion are conformance gaps. This decision
  supersedes the engineering note in `backend/core/scheduler.py` proposing an
  external scheduler, which `ROADMAP.md` records as a resolution candidate
  rather than accepted product scope.)*
- **FR-037 — Stakeholder-confirmed**: Threshold evaluation MUST use one
  configured organizational timezone so that the day an alert fires is
  deterministic and independent of server locale.
  *(Sources: stakeholder clarification, 2026-08-05. The current use of the
  server's local calendar date with no configured rule is a conformance gap.)*
- **FR-038 — Stakeholder-confirmed**: Each combination of Asset, coverage type,
  and threshold MUST produce at most one alert, recorded so that it is never
  repeated. A repeated or overlapping execution MUST therefore be a no-op rather
  than a source of duplicate alerts.
  *(Sources: stakeholder clarification, 2026-08-05. The current absence of any
  already-alerted record is a conformance gap.)*
- **FR-039 — Stakeholder-confirmed**: After downtime or a missed run, the next
  execution MUST evaluate every threshold crossed since the last successful run
  and issue the alerts that were missed, relying on FR-038 to prevent repeats. A
  failed or overdue run MUST be operator-visible rather than silent.
  *(Sources: stakeholder clarification, 2026-08-05. The current exact-date
  design permanently skips a missed day and reports nothing, which is a
  conformance gap.)*

### Current-System Contract Candidates — Not Accepted Requirements

These record current behavior only. They are evidence for stakeholder review and
MUST NOT be read as accepted requirements.

- **CAND-001**: Warranty start and end are Asset fields with no validation of
  presence, order, or relationship to purchase or arrival dates. FR-031 is
  authoritative for ordering; the absence of a purchase-date constraint
  conforms.
- **CAND-002**: AMC history is a list of contracts per Asset, each with an
  optional Vendor, optional start and end dates, one of the three states, an end
  reason, and a creation time.
- **CAND-003**: The Asset's current AMC values are derived from the most
  recently created contract rather than the one with the latest dates.
- **CAND-004**: The Asset's AMC flag is computed as "at least one contract row
  exists", so it is true for an Asset whose only contract is `Ended` and false
  for an Asset that never had one. FR-006 is authoritative.
- **CAND-005**: The persisted Asset-level AMC flag, dates, status, and end reason
  were removed by migration once contract history was introduced.
- **CAND-006**: The migration that backfilled contract history deliberately
  skipped any Asset whose legacy AMC flag was set but whose dates were never
  completed.
- **CAND-007**: Initial AMC entry through the Asset write path creates an
  `Active` contract when both dates are present and an `Incomplete` contract
  when they are not; it applies none of the date-order validation the renewal
  action applies. FR-030 is authoritative.
- **CAND-008**: Clearing the AMC flag through the Asset write path has no
  effect. Under FR-006 the flag is derived rather than set, so the control that
  offers it does not correspond to any accepted operation.
- **CAND-009**: No code path sets an AMC Vendor, and no create, edit, renew, or
  end surface exposes one, so the stored Vendor reference is always empty.
  FR-032 and FR-033 are authoritative.
- **CAND-010**: Renewal ends every `Active` and `Incomplete` contract for the
  Asset with the automatic reason `Renewed` and creates one new `Active`
  contract, inside one transaction.
- **CAND-011**: End Support selects the most recently created `Active` or
  `Incomplete` contract, sets it `Ended` with the supplied reason, and applies no
  terminal-Asset guard.
- **CAND-012**: The end-reason field holds both the operator's End Support reason
  and renewal's automatic supersede marker, with no structural distinction.
  FR-034 is authoritative.
- **CAND-013**: The expiry check compares Warranty end dates and `Active` AMC end
  dates against exactly `today + 30`, `today + 15`, and `today + 7` using the
  server's local calendar date, with no range, catch-up, deduplication, or
  already-alerted record. FR-037, FR-038, and FR-039 are authoritative; the
  exact-day threshold semantics themselves are retained by FR-016.
- **CAND-014**: Warranty alerts apply no Asset status condition, so terminal
  Assets are included; AMC alerts apply the `Active` contract condition only.
- **CAND-015**: Alert recipients are every active User holding
  `asset_custody_manage`, which includes Admin and any custom Role granting it.
  This conforms to FR-018.
- **CAND-016**: Alert messages name the Asset and remaining days and carry a
  destination of `/asset/{id}`; the frontend Asset detail route is
  `/asset/detail/{id}`.
- **CAND-017**: The daily job is configured in-process for 07:00 and is started
  only when the process is the development server; it does not start under
  normal WSGI or ASGI initialization, and its own source records this as an
  accepted temporary limitation to be replaced by an externally triggered
  command. FR-036 is authoritative.
- **CAND-018**: The IT Manager notification for renewal and End Support selects
  active Users whose Role is literally named "IT Manager" and carries no
  destination.
- **CAND-019**: Renewal and End Support each write one AuditLog entry containing
  the same summary sentence as the notification, with no old value; rejected and
  denied attempts write none.
- **CAND-020**: The Settings surface exposes SMTP server, port, username, and
  sender values, and no email-sending implementation exists anywhere in the
  backend. FR-035 keeps email deferred, so the absence conforms.

### Authorization and Lifecycle Requirements

- **ALR-001 — Accepted authorization**: Every Warranty and AMC write MUST be
  authorized at the backend action boundary using `asset_edit`; hiding or
  showing a frontend control MUST NOT be the authorization decision.
  *(Sources: `.specify/memory/constitution.md`, Principle II; accepted B2
  ALR-001 and ALR-010.)*
- **ALR-002 — Accepted atomicity**: A renewal MUST commit the superseding
  closure, the new contract, and its required audit entry as one operation. An
  End Support MUST commit the state change, the reason, and its required audit
  entry as one operation.
  *(Sources: accepted B2 ALR-003; Draft B8 FR-011.)*
- **ALR-003 — Accepted rejection safety**: A denied or rejected AMC action MUST
  leave every contract, the Asset, and its Warranty dates unchanged.
  *(Source: accepted B2 ALR-002.)*
- **ALR-004 — Accepted history integrity**: AMC contract history MUST be
  append-only in effect. A superseded or ended contract MUST remain readable
  with its dates, state, and reason intact.
  *(Source: `CONTEXT.md`, **AMC**, contract history.)*
- **ALR-005 — Accepted state ownership**: An AMC contract's state MUST change
  only through initial entry, completion of an `Incomplete` contract, renewal,
  or End Support. Direct editing of a contract row MUST NOT be an accepted path,
  and no automatic process MUST set a contract `Ended`.
  *(Sources: `CONTEXT.md`, **AMC**; accepted B2 FR-012 by analogy for
  lifecycle-owned state.)*
- **ALR-006 — Accepted alert integrity**: The expiry check MUST NOT change any
  Asset, Warranty date, or AMC contract. It MUST be a read-and-notify operation
  only.
  *(Source: `CONTEXT.md`, **AMC**, where acting on an alert is an explicit human
  decision.)*
- **ALR-007 — Draft B8 failure boundary**: Failure of a required AuditLog write
  MUST reject and roll back the owning AMC action. Notification failure MUST NOT
  roll back completed AMC work and MUST remain visible and retryable without
  duplicate recipient records.
  *(Source: Draft B8 FR-011 and FR-012.)*
- **ALR-008 — Current permission mapping**: Asset update, renewal, and End
  Support currently all map to `asset_edit`, and reads map to `asset_view`.
  These mappings are accepted through B1 and B2. No separate AMC permission code
  exists, so any actor who may edit an Asset may also renew or end AMC support.

### Accepted Warranty and AMC Actor and Permission Contract

| Action | Permission code | Accepted named-Role behavior | Evidence status |
| --- | --- | --- | --- |
| Read Warranty dates, AMC state, and AMC history | `asset_view` plus B1 visibility | Admin, IT Manager, IT Staff, HR, and Viewer global; Employee scope owned by B1 | Accepted B2 read contract; Employee scope is not implemented in the current global queryset |
| Record or correct Warranty dates | `asset_edit` | Admin, IT Manager, and IT Staff | Accepted B2 Asset permission contract |
| Record an initial AMC, complete or incomplete | `asset_edit` | Admin, IT Manager, and IT Staff | Accepted B2 permission contract; the `Incomplete` and completion paths are test-backed |
| Renew an AMC | `asset_edit` | Admin, IT Manager, and IT Staff; IT Staff is the expected actor on an alert | Accepted intent for the actor; the permitted action is test-backed |
| End AMC Support | `asset_edit` | Admin, IT Manager, and IT Staff; IT Staff is the expected actor on an alert | Accepted intent for the actor; the permitted action is test-backed |
| Receive expiry alerts | Not an action | Every IT Manager and IT Staff | Accepted intent; the current rule selects `asset_custody_manage` holders |
| Receive AMC decision notifications | Not an action | IT Manager | Accepted intent; the current rule selects a Role named "IT Manager" |
| Directly edit or delete an AMC contract row | Not accepted | None | Contrary to ALR-004 and ALR-005 |

### B7 Notification and Audit Trigger Matrix

This matrix is the input B7 owes B8 under Draft B8 FR-018. Recipient and
destination rules marked open depend on U-003 and U-005 and are not accepted
content yet.

| B7 event | Notification recipient and meaning | Destination | Required audit entry | Current evidence |
| --- | --- | --- | --- | --- |
| Warranty expiry threshold reached (30/15/7 days) | Every IT Manager and IT Staff; the Warranty is about to lapse | Asset detail surface | None; the check is read-only | Threshold behavior test-backed; recipient breadth, destination, and terminal-Asset exclusion are conformance gaps |
| AMC expiry threshold reached (30/15/7 days) on an `Active` contract | Every IT Manager and IT Staff; act before the contract lapses | Asset detail surface | None; the check is read-only | Threshold behavior test-backed; recipient breadth and destination are conformance gaps |
| AMC renewed | IT Manager; describes the Asset and the new coverage period | Asset detail surface | Actor, time, Asset, previous contract dates and state, new dates, and `Active` outcome | Notification test-backed; missing destination, name-based recipient selection, and thin audit content are conformance gaps |
| AMC support ended | IT Manager; describes the Asset and the recorded reason | Asset detail surface | Actor, time, Asset, previous contract state and dates, `Ended` outcome, and the reason | Notification test-backed; same three conformance gaps |
| Initial AMC entry or completion of an `Incomplete` contract | None accepted | Not applicable | Actor, time, Asset, resulting contract state, and any dates supplied | Only the accepted B2 Asset-mutation entry exists; no AMC-specific entry |
| AMC flag becomes false because a contract ended | None beyond the End Support notification | Not applicable | Covered by the End Support entry; no separate decision record exists under FR-006 | Conforms |
| Rejected or permission-denied AMC action | None | Not applicable | Follows Draft B8 FR-014 for security-relevant rejections | No current entry exists |
| Coverage read, Dashboard panel, or report view | None | Not applicable | None as a routine business read | Current behavior conforms |

Audit values MUST comply with Draft B8 FR-015 minimization. Source IP, when
captured, follows B8's six-month value-retention rule and the entry follows B8's
two-year retention rule.

### Key Entities

- **Warranty**: The manufacturer's coverage period on an Asset, expressed as two
  dates on the Asset record. It has no state and no workflow.
- **AMC contract**: One paid maintenance agreement for one Asset, with a state,
  optional dates, a managed Vendor once dated, an end reason, a supersede marker
  held separately from that reason, and a creation time. An Asset's contracts
  form its append-only coverage history.
- **Asset**: The subject of both coverage types. Its identity, register data,
  terminal statuses, and write permissions are owned by accepted B2.
- **Vendor**: The managed third-party identity owned by B6. A dated AMC contract
  references one under FR-032 and need not match the Procurement Vendor.
- **Expiry alert**: A pushed message derived from a coverage end date. It
  changes nothing and prompts a human decision.
- **Notification**: The shared recipient record owned by B8. B7 owns its own
  business events, recipients, meaning, and destinations.
- **AuditLog Entry**: The shared operational record owned by B8. B7 supplies the
  required Warranty and AMC triggers and any additional minimum content.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 18 selected B7 tests pass in one run — 8 AMC action tests, 5
  AMC incomplete-state tests, 4 expiry alert tests, and 1 AMC expiry report
  test.
- **SC-002**: For 100% of Assets, Warranty and AMC coverage are readable as two
  independent records, and 0% of surfaces present one as the other.
- **SC-003**: 100% of Assets fall into exactly one of four distinguishable AMC
  situations — no decision recorded, deliberately no AMC, an incomplete
  contract, or a current contract — and 0% are ambiguous between them.
- **SC-004**: For 100% of renewals, a new `Active` contract and a retained
  superseded contract both exist after the operation, and 0% of earlier
  contracts are lost or overwritten.
- **SC-005**: 100% of renewals missing a date, carrying an unparseable date,
  carrying an end date not after the start date, or targeting a terminal Asset
  are rejected with zero contract changes.
- **SC-006**: 100% of End Support actions record a nonblank reason, and 0% of
  contracts reach `Ended` without either an operator-supplied reason or an
  automatic supersede marker.
- **SC-007**: 0% of AMC contracts change state as a result of an end date
  passing, and 100% of lapsed-but-unattended contracts remain distinguishable
  from deliberately ended ones.
- **SC-008**: For a Warranty end date and an `Active` AMC end date at exactly 30,
  15, and 7 days out, 100% of the accepted recipients receive an alert; for
  off-threshold dates, `Ended` contracts, Assets with no current AMC, and
  terminal Assets, 0% do.
- **SC-009**: 100% of expiry alerts reach recipients without any User opening a
  dashboard or report, under the deployment the organization actually runs; a
  repeated execution produces 0% duplicate alerts, and 100% of thresholds
  crossed during downtime are issued on the next run.
- **SC-010**: 100% of successful renewals and End Support actions produce
  exactly one IT Manager notification whose destination resolves to the Asset,
  and 0% depend on a Role's display name to find their recipient.
- **SC-011**: Every protected B7 action maps to exactly one permission and one
  B1 visibility rule; unauthorized attempts return no out-of-scope record and
  perform zero mutation.
- **SC-012**: Required audit failure rolls back 100% of owning AMC actions;
  notification failure rolls back 0% of otherwise completed actions.
- **SC-013**: All five mandated decisions U-001 through U-005 have explicit
  stakeholder answers, and 0% of their former implementation-only alternatives
  remain presented as accepted behavior.
- **SC-014**: 100% of accepted, test-backed, implementation-only, and unresolved
  claims in this baseline cite `CONTEXT.md`, an accepted or Draft dependency
  identifier, an explicit stakeholder decision, or a repository evidence path.

## Assumptions

- Accepted B2 is authoritative and is not reopened by this Draft. B1, B5, B6,
  and B8 remain Draft dependencies; where this Draft cites them, acceptance of
  B7 depends on their own acceptance.
- No ADR governs Warranty or AMC. `CONTEXT.md` is the only authoritative product
  source, and it is unusually detailed for this capability, so most accepted
  requirements here derive from it directly.
- "Proactively pushed" is read as a delivery obligation on the system, not a
  description of any particular transport. FR-035 records that an in-app
  notification satisfies it for this version.
- The 30, 15, and 7-day thresholds are read as exact days-before-expiry
  checkpoints, consistent with the current implementation and its tests. FR-039
  keeps those exact semantics and adds catch-up for missed runs rather than
  widening them into ranges.
- IT Manager and IT Staff are the named Roles `CONTEXT.md` uses; the accepted
  recipient rule under FR-018 and FR-021 is the underlying permission grant, so
  the named Roles remain the business description and the code is authoritative.
- In-app-only delivery is accepted for this version under FR-035. It carries a
  known residual risk: a recipient who does not open the application between a
  7-day alert and the expiry date effectively receives nothing in time. The
  stakeholder accepted that risk rather than requiring email; it is the reason
  the U-002 scheduling answer matters more, not less.
- Warranty is assumed non-transferable and non-extendable in current scope,
  consistent with `CONTEXT.md` describing its dates as manufacturer-fixed.
  Extended-warranty products are not modelled.
- An Asset is assumed to have at most one current AMC contract at a time.
  Overlapping concurrent contracts are not modelled.
- Currency, cost, and payment terms of a paid AMC are assumed out of scope for
  this baseline; only the coverage period and its state are recorded.
- No application code, test code, database, migration, route, interface, or
  configuration was modified as part of specifying this baseline.

## Baseline Evidence and Unresolved Conflicts *(Brownfield Baseline only)*

### Accepted Intent

- Warranty is manufacturer coverage with start and end dates, distinct from AMC,
  which is a different contract often with a different vendor and date range:
  `CONTEXT.md`, **Warranty** and **AMC**.
- AMC is a separate, optional, paid maintenance contract with its own dates and
  is queryable rather than merely an uploaded document: `CONTEXT.md`, **AMC**.
- The AMC flag is distinct from the dates: false means the Asset deliberately has
  no AMC and is excluded from alerts and completeness reporting; true with empty
  dates means the AMC exists but is not yet entered and is flagged incomplete:
  `CONTEXT.md`, **AMC**.
- Expiry alerts for both Warranty and AMC are proactively pushed at 30, 15, and
  7 days before expiry to IT Manager and IT Staff, rather than only shown on a
  dashboard someone must open: `CONTEXT.md`, **AMC**.
- IT Staff acts on an AMC alert before expiry by explicitly renewing with new
  dates or ending support with a recorded reason; a contract is never
  discontinued merely by dates lapsing unattended: `CONTEXT.md`, **AMC**.
- Either AMC action notifies the IT Manager with the description of what was
  done: `CONTEXT.md`, **AMC**.
- Warranty has no renew or end workflow; that workflow is AMC-specific:
  `CONTEXT.md`, **AMC**.
- Asset writes require `asset_edit` held by Admin, IT Manager, and IT Staff;
  terminal Assets have left circulation; every successful Asset mutation creates
  an AuditLog entry and B2 register actions create no Notifications: accepted B2
  FR-008, ALR-010, ALR-011, and the Asset permission contract.
- B7 owns its Notification and audit trigger matrix while B8 owns shared
  delivery, failure behavior, privacy, access, and retention: Draft B8 FR-002,
  FR-011, FR-012, FR-015, and FR-018.
- A Service Record is not evidence of a Warranty or AMC claim: Draft B5 FR-001
  and Out of Scope.

### Verified Behavior Evidence

The 18 tests below were run together on 2026-08-05 in the repository-local
backend environment and all passed.

- **AS-011, AS-031**: renewal sets new dates, reports `Active`, and notifies the
  IT Manager:
  `backend/assets/tests.py::AmcActionTests::test_renew_amc_sets_dates_and_notifies_it_manager`.
- **AS-012**: renewal ends the previous contract with reason `Renewed` and
  creates a new one, preserving both:
  `AmcActionTests::test_renew_amc_ends_previous_contract_and_creates_new_one`.
- **AS-013**: renewal rejects an unparseable date and an end date not after the
  start date:
  `AmcActionTests::test_renew_amc_rejects_an_unparseable_date`;
  `AmcActionTests::test_renew_amc_rejects_end_before_start`.
- **AS-014**: renewal rejects a terminal Asset:
  `AmcActionTests::test_renew_amc_rejects_a_terminal_asset`.
- **AS-017, AS-032**: End Support records `Ended` with the reason and notifies
  the IT Manager:
  `AmcActionTests::test_end_amc_support_sets_status_and_notifies_it_manager`.
- **AS-018**: End Support requires a nonblank reason:
  `AmcActionTests::test_end_amc_support_requires_a_reason`.
- **AS-019**: End Support is rejected when no current contract exists:
  `AmcActionTests::test_end_amc_support_rejects_when_no_active_amc`.
- **AS-007**: setting the AMC flag with no dates creates exactly one
  `Incomplete` contract with empty dates:
  `AmcIncompleteStateTests::test_checking_has_amc_without_dates_creates_an_incomplete_contract`.
- **AS-008**: supplying both dates later completes that same contract as
  `Active` with no duplicate:
  `AmcIncompleteStateTests::test_supplying_dates_later_completes_the_incomplete_contract`.
- **AS-015**: renewal supersedes an `Incomplete` contract:
  `AmcIncompleteStateTests::test_renew_amc_supersedes_an_incomplete_contract`.
- **AS-020**: End Support can end an `Incomplete` contract:
  `AmcIncompleteStateTests::test_end_amc_support_can_end_an_incomplete_contract`.
- **AS-010**: an `Incomplete` contract created after an older fully dated
  `Ended` one is treated as current:
  `AmcIncompleteStateTests::test_incomplete_contract_created_after_an_ended_one_is_correctly_latest`.
- **AS-023**: a Warranty at a 30-day threshold notifies a recipient:
  `ExpiryAlertTests::test_warranty_at_a_threshold_notifies_recipients`.
- **AS-024**: an `Active` AMC at a 7-day threshold notifies a recipient:
  `ExpiryAlertTests::test_active_amc_at_a_threshold_notifies_recipients`.
- **AS-026**: a Warranty at 29 days is silent:
  `ExpiryAlertTests::test_warranty_not_at_a_threshold_is_silent`.
- **AS-027**: an `Ended` AMC at a 15-day threshold is silent:
  `ExpiryAlertTests::test_ended_amc_at_a_threshold_is_silent`.
- **OBS-AS-024**: the AMC expiry report does not fail on a contract ended before
  its dates were entered and labels it accordingly:
  `backend/reporting/tests.py::AmcExpiryReportTests::test_report_does_not_crash_on_a_contract_ended_before_dates_were_entered`.

No automated test covers the scheduler, the FR-006 flag derivation, initial AMC
entry validation, AMC Vendor capture, alert deduplication, terminal-Asset
Warranty alerts, or notification destinations.

### Implementation-Only Observations

- AMC contract persistence, nullable dates, the always-empty Vendor reference,
  and cascade deletion with the Asset: `backend/assets/models.py`.
- Derivation of the Asset's current AMC values from the most recently created
  contract, and the computed AMC flag: `backend/assets/models.py`.
- Initial AMC creation and completion through the Asset write path, the absence
  of date-order validation there, and the no-op when the AMC flag is cleared:
  `backend/assets/serializers.py`.
- The renewal action's date parsing, ordering check, terminal-Asset guard,
  transactional supersede-and-create, audit call, and IT Manager notification:
  `backend/assets/views.py`.
- The End Support action's reason requirement, contract selection, absent
  terminal-Asset guard, audit call, and IT Manager notification:
  `backend/assets/views.py`.
- Role-name-based IT Manager notification selection with no destination:
  `backend/assets/views.py`.
- Exact-date 30/15/7 thresholds, recipient selection by permission code, message
  wording, and `/asset/{id}` destinations: `backend/assets/alerts.py`;
  `backend/accounts/models.py`.
- In-process daily 07:00 job, its single-start guard, and its own recorded
  limitation that it should move to an externally triggered command:
  `backend/core/scheduler.py`.
- Startup restricted to the development server command, so no scheduling occurs
  under normal WSGI or ASGI initialization: `backend/core/apps.py`.
- Removal of the persisted Asset-level AMC fields and the backfill that skipped
  legacy Assets with an incomplete AMC:
  `backend/assets/migrations/0006_backfill_amc_contract.py`;
  `backend/assets/migrations/0007_remove_asset_amc_fields.py`;
  `backend/assets/migrations/0008_amccontract_incomplete_dates.py`.
- Asset detail AMC panel, renew and End Support forms, the "Cancel Planned AMC"
  label for an `Incomplete` contract, the history block shown only when more
  than one contract exists, and the "This asset has no AMC" message:
  `frontend/src/pages/asset/Detail.jsx`.
- The `Assignment & Warranty` panel title, which uses rejected terminology owned
  by accepted B2 FR-004 and `ROADMAP.md` C3:
  `frontend/src/pages/asset/Detail.jsx`.
- Warranty date pickers, the AMC checkbox, and conditional AMC date fields with
  no Vendor field: `frontend/src/pages/asset/Create.jsx`;
  `frontend/src/pages/asset/Edit.jsx`.
- Dashboard expired and expiring Warranty/AMC counts, the two coverage timeline
  charts, and the Warranty-expiring-soon list, all owned by B9:
  `backend/reporting/views.py`; `frontend/src/pages/Dashboard.jsx`.
- The Warranty Expiry Report over every Asset with a warranty end date and the
  AMC Expiry Report over every contract with an always-empty Vendor column,
  owned by B9: `backend/reporting/views.py`.
- SMTP server, port, username, and sender Settings with no email-sending
  implementation anywhere in the backend: `frontend/src/pages/Settings.jsx`;
  `backend/core/models.py`.

### Unresolved Conflicts

- **U-001 — C4: AMC flag semantics — RESOLVED 2026-08-05 with a recorded
  divergence**: the stakeholder kept the flag derived, but from the current
  contract only — true when the latest contract is `Active` or `Incomplete`,
  false when it is `Ended` or absent. No persisted decision is introduced and no
  migration is required. Recorded in FR-006, AS-006, and AS-009; the current
  "any contract row exists" derivation (`backend/assets/models.py`) is now a
  conformance gap in U-006.

  This answer narrows `CONTEXT.md`, **AMC**, which defines `has_amc = False` as
  a deliberate decision that also excludes the Asset from data-completeness
  reports. Under the accepted rule an Asset that never had an AMC and one whose
  AMC was deliberately ended are indistinguishable, so no report can identify
  Assets that still need an AMC decision. Per constitution Principle I this
  divergence MUST be resolved in `CONTEXT.md` rather than absorbed silently;
  FR-029 makes that reconciliation an acceptance precondition. The decision
  owner for the glossary amendment is the product stakeholder.
- **U-002 — C5: production scheduling guarantees — RESOLVED 2026-08-05**: the
  stakeholder kept scheduling inside the application but required it to start
  under the real production server as well as the development one, with mutual
  exclusion so exactly one execution occurs per scheduled run across every
  worker and host. Threshold evaluation uses one configured organizational
  timezone; each Asset/coverage/threshold alert is recorded once so reruns are
  no-ops; and the next run after downtime issues every threshold crossed since
  the last successful run, with failed or overdue runs operator-visible.
  Recorded in FR-036 through FR-039; the current development-server-only
  startup, absent exclusion, absent timezone rule, absent deduplication, and
  absent catch-up (`backend/core/apps.py`; `backend/core/scheduler.py`;
  `backend/assets/alerts.py`) are now conformance gaps in U-006.

  This answer supersedes the engineering note in `backend/core/scheduler.py`
  proposing a move to an external scheduler. `ROADMAP.md` already records that
  move as a resolution candidate rather than accepted product scope, so no
  authoritative source is overridden. The accepted design keeps alert production
  tied to application process lifetime, which FR-036 requires to be
  operator-visible.
- **U-003 — Initial-entry validation — RESOLVED 2026-08-05**: the stakeholder
  aligned initial AMC entry with renewal — both dates or neither, real dates,
  end after start — and required Warranty to enforce end-after-start when both
  dates are present while permitting either alone. Neither is tied to purchase
  or arrival dates, so legacy and imported records stay enterable. Recorded in
  FR-030 and FR-031; the currently unvalidated initial AMC path and unvalidated
  Warranty ordering (`backend/assets/serializers.py`;
  `backend/assets/models.py`) are now conformance gaps in U-006.
- **U-004 — AMC Vendor capture and history rules — RESOLVED 2026-08-05**: the
  stakeholder required a managed B6 Vendor on any dated contract, optional while
  `Incomplete`, not required to match the Procurement Vendor; required renewal
  to capture the Vendor and permit a change of maintainer; and required
  append-only history with renewal's supersede marker held separately from the
  operator's End Support reason. Recorded in FR-032, FR-033, and FR-034; the
  absent Vendor capture and the shared end-reason field
  (`backend/assets/models.py`; `backend/assets/views.py`;
  `backend/reporting/views.py`) are now conformance gaps in U-006. Whether
  Warranty records a manufacturer identity was not asked and remains out of
  scope for this baseline.
- **U-005 — Recipients and delivery channel — RESOLVED 2026-08-05**: the
  stakeholder made recipients permission-based — `asset_custody_manage` for
  expiry alerts and the IT Manager grant for AMC decision notifications — and
  kept delivery in-app only for this version, consistent with Draft B8 FR-008,
  with email deferred. Recorded in FR-018, FR-021, and FR-035; the current
  Role-display-name selection for AMC decision notifications
  (`backend/assets/views.py`) is now a conformance gap in U-006, while the
  current alert recipient breadth conforms. The residual risk that a recipient
  does not open the application inside a 7-day window is accepted for this
  version and recorded under Assumptions.
- **U-006 — Conformance gaps recorded, not accepted**: the current behaviors
  below contradict accepted requirements in this Draft. Each is recorded as a gap
  rather than reconciled by weakening a requirement. Whether a gap is corrected,
  deferred, or formally excepted is a review decision, not a specification
  decision.

| # | Current behavior | Accepted requirement | Current-state record |
| --- | --- | --- | --- |
| 1 | The AMC flag is computed from any existing contract row, so an ended-only Asset reports as having an AMC | FR-006 | CAND-004 |
| 2 | The Asset form offers an AMC flag control that corresponds to no accepted operation, because the flag is derived | FR-006 | CAND-008 |
| 3 | Warranty alerts include terminal Assets | FR-020 | CAND-014 |
| 4 | Initial AMC entry applies none of renewal's date validation | FR-030 | CAND-007 |
| 4a | Warranty accepts an end date before its start date | FR-031 | CAND-001 |
| 5 | End Support has no terminal-Asset guard while renewal does | FR-011, ALR-003 | CAND-011 |
| 6 | The operator's End Support reason and renewal's automatic supersede marker share one field | FR-034 | CAND-012 |
| 7 | Expiry alert destinations do not resolve to the Asset detail route | FR-024 | CAND-016 |
| 8 | Renewal and End Support notifications carry no destination at all | AS-033, FR-021 | CAND-018 |
| 9 | IT Manager notification recipients are selected by Role display name | FR-021, SC-010 | CAND-018 |
| 11 | A missed run permanently skips that day's thresholds | FR-039 | CAND-013 |
| 11a | A repeated run duplicates alerts, with no already-issued record | FR-038 | CAND-013 |
| 11b | Threshold evaluation uses the server's local date with no configured timezone | FR-037 | CAND-013 |
| 12 | No alert is scheduled at all under a normal production deployment, and nothing prevents one execution per worker | FR-036 | CAND-017 |
| 13 | Renewal and End Support audit entries carry only a summary sentence, and rejected attempts none | FR-025 | CAND-019 |
| 14 | No AMC Vendor is ever recorded, leaving the report column permanently empty | FR-032 | CAND-009 |
| 14a | Renewal captures no Vendor, so a change of maintainer cannot be recorded | FR-033 | CAND-009 |
| 15 | The current AMC contract is chosen by creation order rather than by dates | FR-005, ALR-004 | CAND-003 |

### Remaining Evidence-Led Confirmation Items

These are not among the five mandated blockers and do not reopen U-001 through
U-005. They are review items to confirm alongside them:

- Whether an `Incomplete` AMC should itself be chased after some period, given
  that `CONTEXT.md` requires it to appear in data-completeness reporting
  (FR-007).
- Confirmation of FR-020, which is derived from accepted B2 FR-008 rather than
  stated in `CONTEXT.md`: `CONTEXT.md` never says terminal Assets are excluded
  from expiry alerts, and this Draft infers it from the fact that a `Sold`,
  `Scrapped`, or `Lost` Asset has left circulation and offers no action to take.
- Whether an expiry alert should identify which coverage and which contract it
  refers to, rather than only the Asset (Edge Cases).
- Whether AMC history should be retained when an Asset is deleted, which is
  owned by accepted B2 (Edge Cases).
- Whether a Service Record performed under Warranty or AMC should reference the
  covering contract, which would require a change in both B5 and B7 (FR-026).

## Out of Scope *(mandatory)*

### Adjacent Baseline Ownership

- Authentication, Users, Roles, permission-code administration, named-Role
  grants, and data visibility: B1. B7 consumes the resulting Role and permission
  values.
- Asset identity, register, search, status and condition sets, terminal
  transitions, direct administrative edits, files, barcode, condition history,
  aggregate history, and Asset deletion: B2. B7 adds only coverage semantics to
  the Asset's Warranty dates and AMC history.
- Checkout and check-in: B3. Coverage has no custody effect and no custody
  operation changes coverage.
- Approval-gated Transfer: B4.
- Service Record lifecycle, Vendor selection for repairs, service cost, bill, and
  outcome: B5. A repair is not a coverage claim and B7 records no link to one.
- Procurement, Vendor administration, Vendor naming and normalization, and
  catalog masters: B6. B7 would only select an existing managed Vendor if U-004
  requires it.
- Shared Notification storage, read state, unread counts, polling, delivery
  reliability, channel implementation, AuditLog storage, administrative access,
  filters, privacy, and retention: B8. B7 owns only its trigger matrix.
- Dashboard coverage KPIs, the Warranty and AMC timeline charts, the
  Warranty-expiring-soon list, the Warranty Expiry Report, the AMC Expiry
  Report, report columns, and PDF/Excel/CSV exports: B9. They consume B7 data
  and do not define B7 requirements, and a dashboard panel does not satisfy
  FR-017.

### Explicitly Unresolved Rather Than Accepted

- No requirement-level decision remains open. All five mandated decisions
  U-001 through U-005 were resolved on 2026-08-05.
- Two acceptance preconditions remain, tracked in FR-028: the `CONTEXT.md`
  reconciliation required by FR-029, and reviewer confirmation of the derived
  requirement FR-020 recorded under Remaining Evidence-Led Confirmation Items.

### Explicitly Deferred or Excluded

- Warranty renewal, extension, transfer, or discontinuation workflows;
  `CONTEXT.md` makes Warranty dates manufacturer-fixed.
- Extended-warranty or third-party warranty products distinct from the
  manufacturer's coverage.
- AMC cost, payment terms, invoicing, and contract documents beyond the existing
  AMC document type owned by B2's file handling.
- Overlapping concurrent AMC contracts on one Asset.
- Automatic renewal, auto-extension, or any process that changes contract state
  without an explicit human decision.
- Warranty or AMC claim submission, claim tracking, and reconciliation of repair
  spend against coverage.
- Scheduled or periodic physical Asset audits (`ROADMAP.md`, F1) and any
  treatment of AuditLog as physical verification.
- Application-code, test-code, database, migration, route, interface, or
  configuration changes in this documentation-only specification run.
