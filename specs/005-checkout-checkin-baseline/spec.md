# Feature Specification: AS-BUILT Checkout and Check-in Baseline

**Feature Branch**: `docs/baseline-spec-migration`

**Created**: 2026-08-04

**Status**: Draft

**Evidence Date**: 2026-08-04

**Input**: User description: "Create an AS-BUILT Brownfield Baseline
specification for ROADMAP.md entry B3: Checkout and check-in. Cover IT-performed
Checkout from Available to Assigned, check-in to Available,
`asset_custody_manage`, Custodian and department effects, conditions, remarks,
expected return date, notifications, rejected operations, and endpoint round
trips. Keep department semantics after check-in, default return condition,
expected-return obligations, and audit requirements unresolved. Exclude employee
self-service, Transfer, and Service Record except their explicit integration
boundaries. Use Checkout, never Assignment. Do not modify application code."

## Clarifications

### Session 2026-08-04

- Q: What value should the Asset department hold after a check-in? → A: Clear it
  with the Custodian, confirming Draft B2 FR-015; Checkout sets department to
  the Checkout User's department and empties it when that User has none.
- Q: When a check-in supplies no return condition, what happens, and how is the
  resulting Asset condition change recorded? → A: The return condition is
  mandatory and a check-in without one is rejected; every check-in condition
  change creates an Asset condition-inspection history row. The `Good` default
  is removed.
- Q: What rules govern the expected return date, and what should overdue do? →
  A: Optional, and when supplied it must be today or later; an open Checkout
  past its expected return date is Overdue and proactively notifies the
  Custodian and every `asset_custody_manage` holder.
- Q: Which Checkout and check-in events require an AuditLog entry? → A: Every
  successful Checkout and check-in, every rejected or permission-denied attempt,
  and every interrupting closure; each entry identifies the operator, Asset,
  Checkout User, status/Custodian/department effects, and the condition
  recorded.
- Q: Who receives a Notification for Checkout, check-in, and an interrupted
  closure? → A: The new Custodian on Checkout, the returning Checkout User on
  check-in, that Checkout User when an interrupting operation ends their
  custody, and every `asset_custody_manage` holder on each Checkout and
  check-in; every destination must resolve to the Asset detail surface.
- Q: How should intake remarks and return remarks behave? → A: They are distinct
  retained fields that a check-in never overwrites, both optional, except that
  return remarks are mandatory when the return condition is worse than the
  checkout condition.
- Q: What happens to an open Checkout when a Service Record opens on the held
  Asset? → A: It closes atomically, is marked closed-as-interrupted and remains
  distinguishable from a check-in, takes the Asset's current condition as its
  return condition, clears the Custodian, and requires a fresh Checkout after
  service closes.

## Specification Lineage *(mandatory)*

**Type**: Brownfield Baseline

**Roadmap Reference**: `ROADMAP.md`, entry B3 — Checkout and check-in.

**Extends**: None.

**Supersedes**: None.

**Reciprocal Links**: `ROADMAP.md` reserves
`specs/005-checkout-checkin-baseline/` for B3 and already records that path in
its B3 row. The roadmap is not edited by this specification run, matching the
handling of the Draft B8 baseline in the same worktree; converting the reserved
path to a link and moving B3 from `R1` to `R3` are review actions, not
specification actions. Future changes after acceptance must be recorded in a new
specification and linked here with `Extends`, `Supersedes`, or `Superseded by`
metadata.

**Dependencies**: B1 (identity, `asset_custody_manage`, User, Department), B2
(accepted Asset register, status, condition, Custodian, and department
contract), B8 (shared Notification and AuditLog facility, Draft).

## Domain Alignment *(mandatory)*

**Canonical Terms**:

- **Checkout** is the operation that moves an Asset from `Available` to
  `Assigned` for one User, and the record of that usage session. It has no
  approval gate and no `Pending` state.
- **Check-in** is the closing operation of a Checkout: the Asset returns to
  `Available` and the Checkout record becomes `Returned`.
- **Custodian** is the User currently holding the Asset. Checkout sets it;
  check-in clears it.
- **Checkout User** is the User to whom the Asset is checked out and who becomes
  the Custodian. **Custody operator** is the IT actor who performs Checkout or
  check-in on that User's behalf.
- **Intake remarks** are recorded when custody begins; **return remarks** are
  recorded at check-in. They are distinct values and neither replaces the other.
- **Overdue** describes an open Checkout whose expected return date has passed.
  It is a derived state of the Checkout, never an Asset status.
- **Interrupted closure** is the closing of an open Checkout by an operation
  other than a check-in — currently opening a Service Record or an accepted
  terminal transition. A Checkout so closed is **closed-as-interrupted** and
  stays distinguishable from one closed by a check-in.
- **Asset**, **status**, **condition**, **Department**, **Transfer**, **Service
  Record**, and **Notification** follow `CONTEXT.md` and the Draft B2
  baseline.
- `Assignment` is rejected terminology for this lifecycle and MUST NOT appear on
  any user-visible Checkout surface. `Assigned` remains the canonical Asset
  *status* value and is not the rejected term.
- "Self-service" MUST NOT be used for the current Checkout without
  qualification: the state machine has no approval step, but only IT holds the
  permission required to create a Checkout.

**Relevant Decisions**:

- `CONTEXT.md`, **Checkout**: `Available → Assigned` and back to `Available` on
  check-in; no approval gate; distinct from Transfer; IT Manager or IT Staff
  performs every Checkout in person using `asset_custody_manage`; employees
  cannot check an Asset out to themselves. Employee self-service Checkout is
  explicitly deferred (`ROADMAP.md`, F2).
- `CONTEXT.md`, **Custodian**: Checkout or Transfer sets the Custodian;
  check-in or opening a Service Record clears it; Asset `status` remains
  authoritative for availability.
- `CONTEXT.md`, **Service Record** and `docs/adr/0001-service-record-lifecycle.md`:
  opening a Service Record mirrors check-in by clearing the Custodian, and
  closing it never restores the previous Custodian — IT must perform a fresh
  Checkout. This is the B3/B5 integration boundary.
- Draft B2 baseline (`specs/001-asset-register-lifecycle-baseline/spec.md`):
  AS-004, AS-005, FR-006, FR-012, FR-015, ALR-004, ALR-006, ALR-007, the
  Accepted Lifecycle Boundary table, and the Accepted Asset Permission Contract
  are authoritative inputs to B3 and are not reopened here.
- Draft B8 baseline (`specs/004-notifications-audit-baseline/spec.md`): FR-002,
  FR-008, and FR-018 assign the explicit Checkout Notification and audit trigger
  matrix to B3 while B8 owns shared in-app delivery, read state, access, and
  retention. B8 is Draft, so its shared minimums are cited as a dependency, not
  as accepted B3 requirements.
- `ROADMAP.md` decision register, C1 (shared with B4): whether Store-to-User
  issuance is a Checkout or a Transfer is unresolved and blocks B3 acceptance.
- `ROADMAP.md` decision register, C3 (shared with B2): the user-visible term
  `Assignment` is replaced by `Checkout`; any exception requires an explicit
  `CONTEXT.md` amendment.
- Stakeholder clarification dated 2026-08-04 resolves the four roadmap-listed B3
  blockers — department semantics after check-in, the return condition,
  expected-return obligations, and audit events — and additionally settles
  Notification recipients, remarks behavior, and the Service Record interruption
  boundary. C1 remains open.

**Lifecycle and Actors**:

- Admin, IT Manager, and IT Staff hold `asset_custody_manage` and are the only
  actors who may create a Checkout or perform a check-in (Draft B2 permission
  contract; `CONTEXT.md`, **Checkout**).
- Any actor whose Role grants `asset_view` may read Checkout records. Employee
  Asset-read scope is owned by B1 and B2 and is not extended here.
- The Checkout User may be any active User; that User performs no system action
  in the current Checkout lifecycle and receives only a Notification.
- Checkout owns entry into `Assigned`; check-in owns the return to `Available`.
  Neither state may be entered or left by a direct Asset edit (B2 ALR-004).
- Two adjacent operations close an open Checkout without a check-in: opening a
  Service Record (B5) and an accepted terminal transition (B2). Both are
  integration boundaries; B3 owns only the resulting closure of its own record.
- Checkout sets the Asset department from the Checkout User and check-in clears
  it with the Custodian, confirming Draft B2 FR-015.
- `asset_custody_manage` holders are both the accepted actors and, from the
  2026-08-04 clarification, Notification recipients for every Checkout,
  check-in, and Overdue Checkout.

### Evidence Classification

This Draft uses the following classifications:

- **Accepted intent**: confirmed by `CONTEXT.md`, an ADR, or an accepted
  specification, and eligible to be a baseline requirement.
- **Stakeholder-confirmed**: decided in a dated clarification session recorded in
  §Clarifications, and eligible to be a baseline requirement on the same footing
  as accepted intent. It differs only in where the authority is recorded — in
  this specification rather than in `CONTEXT.md`, an ADR, or an accepted
  specification. Most of the 2026-08-04 decisions carry this classification.
- **Governance requirement**: required by `.specify/memory/constitution.md`
  rather than by a product decision. It applies to every capability, carries the
  same requirement force as accepted intent, and is not open to amendment or
  rejection during this baseline's review.
- **Test-verified current behavior**: demonstrated by a passing automated test,
  but still awaiting stakeholder acceptance as product intent.
- **Implementation-only observation**: visible in backend or frontend code
  without dedicated automated behavioral coverage or authoritative intent.
- **Unresolved**: a material choice or contradictory evidence that must not be
  promoted into an accepted requirement and that blocks B3 acceptance.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Check Out an Available Asset to a User (Priority: P1)

A custody operator hands a physical Asset to an employee in person and records
the Checkout so that the register shows who holds the Asset, on behalf of which
department, in what condition, and for what purpose.

**Why this priority**: Checkout is the primary way an Asset acquires a
Custodian. Without it the register cannot answer "who has this Asset".

**Independent Test**: With an `Available` Asset and an active User, perform one
Checkout and confirm the Asset status, Custodian, department, and the new
Checkout record's intake data, then confirm the User is notified.

**Acceptance Scenarios**:

1. **AS-001 — Accepted intent**: **Given** an `Available` Asset, **When** a
   custody operator checks it out to a User, **Then** the Asset status becomes
   `Assigned`, that User becomes the Custodian, and one open Checkout record
   exists for the pair.
2. **AS-002 — Accepted intent**: **Given** a successful Checkout, **When** the
   record is created, **Then** no approval, `Pending` state, or second actor is
   required for the Asset to become `Assigned`.
3. **AS-003 — Stakeholder-confirmed (B2 FR-015)**: **Given** a Checkout User who
   has a department, **When** the Checkout succeeds, **Then** the Asset
   department becomes that User's department; **Given** a Checkout User with no
   department, **When** the Checkout succeeds, **Then** the Asset department is
   emptied rather than left at its previous value.
4. **AS-004 — Accepted intent (B2 ALR-004 and FR-012)**: **Given** an
   `Available` Asset, **When** a User attempts to reach `Assigned` by editing
   the Asset directly instead of performing a Checkout, **Then** the attempt is
   rejected and no Checkout record is created.
5. **AS-005 — Accepted intent (C3)**: **Given** any user-visible surface that
   presents this lifecycle, **When** it names the operation or its history,
   **Then** it uses `Checkout` and never `Assignment`.
6. **AS-006 — Accepted intent**: **Given** a successful Checkout, **When** its
   effects complete, **Then** the Asset status change, Custodian assignment,
   department effect, and Checkout record are one atomic operation, and no
   partial result is user-visible.
7. **AS-026 — Stakeholder-confirmed**: **Given** a successful Checkout, **When**
   it completes, **Then** an in-app Notification addressed to the new Custodian
   and one addressed to every `asset_custody_manage` holder are requested, and
   each destination resolves to that Asset's detail surface.
8. **AS-027 — Stakeholder-confirmed**: **Given** an expected return date earlier
   than the current date, **When** a Checkout is submitted, **Then** it is
   rejected and no Checkout record is created; **Given** no expected return date
   at all, **When** a Checkout is submitted, **Then** it is accepted.
9. **AS-028 — Stakeholder-confirmed**: **Given** a successful Checkout, **When**
   it completes, **Then** exactly one AuditLog entry identifies the custody
   operator, the Asset, the Checkout User, the resulting status, Custodian, and
   department effects, and the recorded checkout condition.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-001 — Test-verified**: **Given** an `Available` Asset and a User
   with a department, **When** Checkout runs, **Then** status becomes
   `Assigned`, Custodian becomes that User, Asset department becomes the User's
   department, and the record's checkout condition defaults to the Asset's
   current condition.
2. **OBS-AS-002 — Test-verified**: **Given** intake remarks supplied at
   Checkout, **When** the record is created, **Then** those remarks are
   persisted on the Checkout record.
3. **OBS-AS-003 — Implementation-only conformance gap (AS-003, FR-006)**:
   **Given** a Checkout User with no
   department, **When** Checkout runs, **Then** the Asset department is left at
   its previous value rather than emptied.
4. **OBS-AS-004 — Implementation-only**: **Given** an explicit checkout
   condition in the request, **When** Checkout runs, **Then** the value is
   stored on the record without validation against the canonical condition set
   and without changing the Asset's own condition.
5. **OBS-AS-005 — Implementation-only conformance gap (AS-027, FR-026)**:
   **Given** an expected return date and a purpose in the request, **When**
   Checkout runs, **Then** both are stored on the record and neither is
   validated, required, or acted upon later.
6. **OBS-AS-006 — Implementation-only**: **Given** a successful Checkout,
   **When** the record is returned, **Then** the operator who performed it is
   recorded in a field presented as `approved_by`, even though the lifecycle has
   no approval step.

---

### User Story 2 - Check In a Held Asset (Priority: P1)

A custody operator receives the Asset back from its holder and records the
check-in, closing the usage session, returning the Asset to circulation, and
capturing the condition it came back in.

**Why this priority**: Without a reliable check-in an Asset stays permanently
`Assigned`, cannot be checked out again, and the register overstates custody.

**Independent Test**: From an open Checkout, perform one check-in with a
canonical condition and remarks, then confirm the record closure, Asset status,
Custodian clearing, and recorded condition.

**Acceptance Scenarios**:

1. **AS-007 — Accepted intent**: **Given** an `Assigned` Asset with an open
   Checkout, **When** check-in succeeds, **Then** the Asset status becomes
   `Available`, the Custodian is cleared, and the Checkout record becomes
   `Returned` with a return date.
2. **AS-008 — Accepted intent (B2 ALR-004 and FR-012)**: **Given** an `Assigned`
   Asset, **When** a User attempts to reach `Available` by editing the Asset
   directly instead of performing a check-in, **Then** the attempt is rejected
   and the open Checkout remains open.
3. **AS-009 — Accepted intent**: **Given** a check-in, **When** its effects
   complete, **Then** the record closure, status change, and Custodian clearing
   are one atomic operation.
4. **AS-010 — Accepted intent**: **Given** a returned Asset, **When** it is next
   handed to a User, **Then** a new Checkout is required; a closed Checkout is
   never reopened and never restores a previous Custodian.
5. **AS-011 — Stakeholder-confirmed**: **Given** a completed check-in, **When**
   the Asset department is evaluated, **Then** it is empty, having been cleared
   with the Custodian as an effect of the same operation.
6. **AS-012 — Stakeholder-confirmed**: **Given** a check-in submitted without an
   explicit return condition, **When** it is processed, **Then** it is rejected
   and no Checkout, Asset status, Custodian, department, or condition changes;
   no default return condition is applied.
7. **AS-029 — Stakeholder-confirmed**: **Given** a check-in whose return
   condition is worse than that session's checkout condition, **When** it is
   submitted without return remarks, **Then** it is rejected; **Given** the same
   check-in with return remarks, **When** it succeeds, **Then** that session's
   intake remarks remain readable alongside the return remarks.
8. **AS-030 — Stakeholder-confirmed**: **Given** a successful check-in, **When**
   it completes, **Then** an in-app Notification addressed to the returning
   Checkout User and one addressed to every `asset_custody_manage` holder are
   requested, and each destination resolves to that Asset's detail surface.
9. **AS-031 — Stakeholder-confirmed**: **Given** a successful check-in, **When**
   it completes, **Then** exactly one AuditLog entry identifies the custody
   operator, the Asset, the Checkout User, the resulting status, the cleared
   Custodian and department, and the recorded return condition.
10. **AS-032 — Stakeholder-confirmed**: **Given** a check-in that changes the
    Asset condition, **When** it completes, **Then** an Asset
    condition-inspection history row records that change.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-007 — Test-verified**: **Given** an open Checkout, **When** check-in
   runs with a canonical condition and remarks, **Then** the record becomes
   `Returned` with a return date and return condition, the Asset becomes
   `Available` with no Custodian, and the Asset condition is set to the
   submitted value.
2. **OBS-AS-008 — Implementation-only conformance gap (AS-032, FR-025)**:
   **Given** a check-in that changes the Asset condition, **When** it completes,
   **Then** no condition-inspection history row is created for that change.
3. **OBS-AS-009 — Implementation-only conformance gap (AS-029, FR-014)**:
   **Given** a Checkout that carries intake remarks, **When** check-in supplies
   return remarks or omits them, **Then** the record's remarks are replaced by
   the return value and the intake remarks are no longer retrievable from that
   record. No rule currently requires return remarks for a worsened condition.
4. **OBS-AS-010 — Implementation-only conformance gap (AS-011, FR-023)**:
   **Given** a completed check-in, **When** the Asset department is inspected,
   **Then** it still holds the previous Custodian's department.
5. **OBS-AS-011 — Implementation-only conformance gap (AS-012, FR-024)**:
   **Given** a check-in request that omits the condition, **When** the endpoint
   processes it, **Then** the condition is defaulted to `Good` and the Asset
   condition is set to `Good`; the check-in surface also preselects `Good`.
6. **OBS-AS-012 — Implementation-only, partially conforming (AS-030, FR-020)**:
   **Given** a successful check-in, **When** it completes, **Then** the Checkout
   User receives an in-app Notification confirming the check-in, but no
   `asset_custody_manage` holder is notified and the destination does not
   resolve.

---

### User Story 3 - Restrict Custody Operations and Reject Invalid Ones (Priority: P1)

Only IT custody operators can create a Checkout or perform a check-in, and an
ineligible or invalid request is rejected without changing the Asset or its
history.

**Why this priority**: Custody is the accountability record. An unauthorized or
partially applied custody change corrupts every downstream report, Transfer, and
Service Record.

**Independent Test**: Attempt Checkout and check-in as a User without
`asset_custody_manage`, then attempt each invalid case as a permitted operator,
and confirm the rejection and the unchanged Asset, Custodian, and Checkout
record in every case.

**Acceptance Scenarios**:

1. **AS-013 — Accepted intent**: **Given** a User whose Role does not grant
   `asset_custody_manage`, **When** that User attempts to create a Checkout or
   perform a check-in, **Then** the action is denied and no Asset, Custodian, or
   Checkout data changes.
2. **AS-014 — Accepted intent**: **Given** an employee, **When** that employee
   attempts to check an Asset out to themselves, **Then** the action is denied;
   employee self-service Checkout is deferred scope, not current behavior.
3. **AS-015 — Accepted intent**: **Given** an Asset whose status is not
   `Available`, **When** a Checkout is attempted, **Then** it is rejected and
   the Asset keeps its current status, Custodian, and department.
4. **AS-016 — Accepted intent**: **Given** an already closed Checkout, **When** a
   check-in is attempted on it, **Then** it is rejected and neither the record
   nor the Asset changes.
5. **AS-017 — Accepted intent (B2 FR-011)**: **Given** a return condition
   outside the canonical condition set, **When** check-in is attempted,
   **Then** it is rejected and the Checkout, Asset status, Custodian, and Asset
   condition remain unchanged.
6. **AS-018 — Governance requirement**: **Given** any Checkout or check-in
   control hidden in a frontend surface, **When** authorization is evaluated,
   **Then** the protected backend action is the authoritative control and
   hiding the control is not sufficient.
7. **AS-033 — Stakeholder-confirmed**: **Given** a Checkout or check-in rejected
   for an ineligible Asset, an already closed Checkout, a missing or
   noncanonical return condition, missing return remarks, or a missing
   permission, **When** the attempt completes, **Then** exactly one AuditLog
   entry identifies the actor, the attempted operation, the Asset, and the
   reason, and no Checkout or Asset data is exposed to a denied actor.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-013 — Test-verified**: **Given** an authenticated User with no
   permissions, **When** a Checkout create is requested, **Then** the request is
   rejected with `403` and no Checkout is created.
2. **OBS-AS-014 — Test-verified**: **Given** a non-`Available` Asset, **When**
   Checkout runs, **Then** it fails with "This asset is not available for
   checkout." and no record is created.
3. **OBS-AS-015 — Test-verified**: **Given** a `Returned` Checkout, **When**
   check-in runs again, **Then** it fails with "This checkout is already
   closed."
4. **OBS-AS-016 — Test-verified**: **Given** a noncanonical condition, **When**
   check-in runs, **Then** it fails and lists the canonical condition set.
5. **OBS-AS-017 — Implementation-only**: **Given** a rejected Checkout or
   check-in, **When** the failure is returned, **Then** it carries a `400`
   status and a single explanatory detail message; an authorization failure
   carries `403`.
6. **OBS-AS-018 — Implementation-only**: **Given** a check-in attempt by a User
   without `asset_custody_manage`, **When** it is submitted, **Then** it is
   rejected by the same permission map entry as create, but this specific path
   has no dedicated automated test.
7. **OBS-AS-019 — Implementation-only**: **Given** a request that omits the
   Asset or the User, **When** Checkout create is submitted, **Then** it is
   rejected by field validation before any lifecycle check runs.
8. **OBS-AS-020 — Implementation-only conformance gap**: **Given** an Admin or
   platform superuser, **When** a Checkout record is updated or deleted
   directly, **Then** the current interface permits it, bypassing the Checkout
   and check-in operations and their Asset side effects.

---

### User Story 4 - Read Checkout Records and Complete Endpoint Round Trips (Priority: P2)

An authorized reader lists current and historical Checkouts, filters open from
returned sessions, and an operator completes a full create-then-check-in round
trip through the same interface.

**Why this priority**: The Checkout list is the operational worklist for
outstanding custody, and the round trip is the smallest complete demonstration
that the capability works end to end.

**Independent Test**: Create a Checkout through the interface, list it as open,
check it in through the interface, and confirm the returned representation and
the filtered lists before and after.

**Acceptance Scenarios**:

1. **AS-019 — Accepted intent**: **Given** an authorized reader with
   `asset_view`, **When** Checkout records are requested, **Then** each record
   identifies its Asset, its Checkout User, its open or returned state, and its
   intake and return data.
2. **AS-020 — Accepted intent**: **Given** a permitted operator, **When** a
   Checkout is created and then checked in through the same interface, **Then**
   the round trip completes and the record's final state is `Returned`.
3. **AS-021 — Accepted intent**: **Given** an Asset, **When** its history is
   reviewed, **Then** every Checkout for that Asset remains visible as
   completed custody history, including sessions closed by an adjacent
   operation.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-021 — Test-verified**: **Given** an operator with
   `asset_custody_manage`, **When** a Checkout is created and then checked in,
   **Then** creation returns `201` and check-in returns `200` with state
   `Returned`.
2. **OBS-AS-022 — Implementation-only**: **Given** Checkout records exist,
   **When** the list is requested, **Then** all records are returned newest
   first, unpaginated, with no scoping to the requesting User.
3. **OBS-AS-023 — Implementation-only**: **Given** an exact state filter,
   **When** the list is requested, **Then** only records in that state are
   returned; no other filter is supported.
4. **OBS-AS-024 — Implementation-only**: **Given** the Checkout creation
   surface, **When** it loads, **Then** it offers only `Available` Assets and
   the full active-User directory, and requires only an Asset and a User.
5. **OBS-AS-025 — Implementation-only**: **Given** the Checkout list surface,
   **When** it renders, **Then** the create control and the check-in control
   appear only for a User with `asset_custody_manage`, and the check-in control
   appears only on open rows.
6. **OBS-AS-026 — Implementation-only**: **Given** an Asset detail surface,
   **When** it renders, **Then** it shows a Checkout History panel and also a
   panel labelled "Assignment & Warranty", which violates the C3 terminology
   decision and AS-005.

---

### User Story 5 - Preserve Closure When Another Operation Interrupts a Checkout (Priority: P1)

When a Service Record opens on a held Asset, or an accepted terminal transition
records it as `Sold`, `Scrapped`, or `Lost`, the open Checkout is closed as part
of that operation so no Asset is left with a dangling usage session.

**Why this priority**: A dangling open Checkout makes an Asset appear held by
someone who no longer has it and blocks any later custody operation.

**Independent Test**: Open a Service Record on a checked-out Asset, and
separately record a checked-out Asset as terminal; in both cases confirm the
Checkout is closed and the Asset ends in the state owned by the interrupting
operation.

**Acceptance Scenarios**:

1. **AS-022 — Accepted intent (ADR-0001; B2 ALR-006)**: **Given** an Asset with
   an open Checkout, **When** a Service Record opens on it, **Then** the
   Checkout is closed as part of that operation and the Custodian is cleared
   before the Asset becomes `Under Repair`.
2. **AS-023 — Accepted intent (B2 ALR-006)**: **Given** an Asset with an open
   Checkout, **When** an accepted terminal transition completes, **Then** the
   Checkout is closed atomically with that transition.
3. **AS-024 — Accepted intent (ADR-0001)**: **Given** a Service Record that
   closes and returns the Asset to `Available`, **When** custody is next
   required, **Then** a fresh Checkout is performed; the interrupted Checkout is
   never reopened and the previous Custodian is never restored automatically.
4. **AS-025 — Accepted intent**: **Given** a Checkout closed by an interrupting
   operation, **When** it is later read, **Then** it is distinguishable from a
   Checkout closed by an ordinary check-in.
5. **AS-034 — Stakeholder-confirmed**: **Given** an interrupting closure,
   **When** it runs, **Then** the Checkout is marked closed-as-interrupted, its
   return condition is taken from the Asset's current condition rather than from
   an operator, and the Checkout User receives an in-app Notification that their
   custody ended, with a destination that resolves to the Asset.
6. **AS-035 — Stakeholder-confirmed**: **Given** an interrupting closure,
   **When** it runs, **Then** exactly one AuditLog entry identifies the
   operation that caused it, the Asset, the Checkout User, and the recorded
   return condition.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-027 — Test-verified**: **Given** an Asset with an open Checkout,
   **When** a Service Record opens, **Then** the Checkout becomes `Returned`
   with a return date before the Asset becomes `Under Repair`.
2. **OBS-AS-028 — Test-verified**: **Given** an Asset with an open Checkout,
   **When** the Asset enters a terminal status, **Then** the Checkout becomes
   `Returned` with a return date.
3. **OBS-AS-029 — Implementation-only, partially conforming (AS-034, FR-028)**:
   **Given** an interrupting closure, **When** it runs, **Then** the return
   condition is copied from the Asset's current condition and an explanatory
   note is appended to the record's remarks, which conforms; but the record
   carries no explicit closed-as-interrupted marker and the Checkout User
   receives no Notification that their custody ended.
4. **OBS-AS-030 — Implementation-only**: **Given** an interrupting closure,
   **When** it runs, **Then** it closes every open Checkout on the Asset, not
   only one, although nothing prevents more than one open Checkout from existing
   for an Asset.

---

### User Story 6 - Track an Overdue Checkout (Priority: P2)

A custody operator records when an Asset is expected back, and both the holder
and IT are told when that date passes without a check-in.

**Why this priority**: An expected return date that nothing acts upon cannot
recover a temporarily loaned Asset. Overdue visibility is the reason to record
the date at all.

**Independent Test**: Create a Checkout with a future expected return date, pass
that date without checking in, and confirm the derived Overdue state and the
Notifications to the Custodian and to custody operators.

**Acceptance Scenarios**:

1. **AS-036 — Stakeholder-confirmed**: **Given** an open Checkout whose expected
   return date has passed, **When** it is read, **Then** it is identifiable as
   Overdue; **Given** the same Checkout after a check-in, **When** it is read,
   **Then** it is no longer Overdue.
2. **AS-037 — Stakeholder-confirmed**: **Given** an open Checkout that becomes
   Overdue, **When** that state is reached, **Then** an in-app Notification is
   requested for the Custodian and for every `asset_custody_manage` holder,
   without waiting for a User to open a surface.
3. **AS-038 — Stakeholder-confirmed**: **Given** an Overdue Checkout, **When**
   another custody operation is attempted, **Then** Overdue does not by itself
   block it, and Overdue never appears as an Asset status.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-031 — Implementation-only conformance gap (AS-036, FR-026)**:
   **Given** an open Checkout past its expected return date, **When** it is
   read, **Then** no Overdue state exists anywhere; only a dashboard panel
   displays the raw date beside open Checkouts.
2. **OBS-AS-032 — Implementation-only conformance gap (AS-037, FR-026)**:
   **Given** any open Checkout, **When** its expected return date passes,
   **Then** no Notification, alert, escalation, or report is produced.

### Edge Cases

- An interrupting closure is the one accepted case where a Checkout closes
  without an operator-supplied return condition (FR-028). Every other closure
  path requires one under FR-024.
- "Worse than" in the return-remarks rule depends on a condition severity
  ordering that `CONTEXT.md` lists but never states as a ranking. The ordering
  this Draft relies on is recorded in Assumptions.
- A Checkout User with no department currently leaves the Asset department at
  its previous value, so an Asset can present a department that belongs to no
  current holder. This is a conformance gap against FR-006.
- The checkout condition is recorded but never validated, so a Checkout record
  can carry a value outside the canonical condition set while check-in rejects
  the same value.
- The checkout condition never changes the Asset's condition, while the return
  condition always does. Only the second effect has stated intent.
- An expected return date can currently be set in the past and produces no
  Overdue state anywhere; both are conformance gaps against FR-026.
- Proactive Overdue delivery depends on production scheduling, which C5 leaves
  unresolved for the existing expiry alerts. B3 accepts the requirement and
  inherits that delivery-guarantee risk; see Assumptions.
- Nothing prevents an expected return date from being changed or cleared after
  the fact through the Admin-only direct record path.
- The Asset eligibility check and the Checkout creation are inside one atomic
  operation, but the row lock relied upon is a no-op on the current database
  engine, so two simultaneous Checkouts of one `Available` Asset are not
  provably prevented.
- Nothing in the data model prevents more than one open Checkout per Asset; the
  interrupting-closure helper is written to close many.
- A Notification currently points at `/asset/{id}` while the corresponding
  frontend route is `/asset/detail/{id}`, so the destination does not resolve —
  a conformance gap against FR-020.
- A Checkout to a User with no linked profile record cannot be notified; the
  shared helper silently does nothing and the Checkout still succeeds. Under
  Draft B8 FR-012 that is a failed delivery, not an accepted outcome.
- Deleting a User removes that User's Checkout history. Deleting an Asset
  removes its Checkout history. Current User deletion is refused only while the
  User still holds Assets, so a User with only closed Checkouts can be deleted
  and that custody history is lost. User and Asset deletion are owned by B1 and
  B2; the Checkout history consequence is recorded here.
- An Admin or platform superuser can edit or delete a Checkout record directly,
  which can desynchronize the record from the Asset's status and Custodian.
- A rejected Checkout, a rejected check-in, and an interrupting closure
  currently produce no audit entry of their own — a conformance gap against
  FR-027.
- Opening a Service Record produces both a B3 interrupted-closure Notification
  and a B5 service Notification addressed to the same User for the same event.
  Whether they are merged into one message is a planning concern for the two
  owning baselines, not a change to either accepted trigger.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 — Accepted intent**: A Checkout MUST move an Asset from `Available`
  to `Assigned` for exactly one Checkout User, and MUST record that usage
  session as a Checkout record.
  *(Source: `CONTEXT.md`, **Checkout**; Draft B2 AS-004.)*
- **FR-002 — Accepted intent**: A check-in MUST move an `Assigned` Asset back to
  `Available` and MUST close its Checkout record as returned.
  *(Source: `CONTEXT.md`, **Checkout**; Draft B2 AS-005.)*
- **FR-003 — Accepted intent**: Checkout MUST NOT have an approval gate, a
  `Pending` state, or a second approving actor. Any requirement for those
  belongs to Transfer.
  *(Source: `CONTEXT.md`, **Checkout** and **Transfer**.)*
- **FR-004 — Accepted intent**: Checkout MUST set the Custodian to the Checkout
  User, and check-in MUST clear the Custodian.
  *(Sources: `CONTEXT.md`, **Custodian**; Draft B2 FR-006.)*
- **FR-005 — Accepted intent**: Asset status MUST remain the authoritative
  availability value; the presence or absence of a Custodian MUST NOT by itself
  determine whether an Asset can be checked out.
  *(Sources: `CONTEXT.md`, **Custodian**; Draft B2 FR-005.)*
- **FR-006 — Stakeholder-confirmed**: Checkout MUST set the Asset department to
  the Checkout User's department, and MUST empty it when that User has no
  department, so the department always describes the current holder.
  *(Sources: Draft B2 FR-015 and the Accepted Lifecycle Boundary table;
  stakeholder clarification, 2026-08-04.)*
- **FR-007 — Accepted intent**: `Assigned` MUST be entered only through Checkout
  and left for a nonterminal status only through check-in. A direct Asset status
  edit MUST NOT substitute for either operation, and a rejected attempt MUST
  leave the Asset and any open Checkout unchanged.
  *(Sources: Draft B2 FR-012 and ALR-004.)*
- **FR-008 — Accepted intent**: A Checkout MUST be rejected when the Asset is
  not `Available`, and the Asset MUST remain unchanged.
  *(Sources: `CONTEXT.md`, **Checkout**; current rejection is test-verified.)*
- **FR-009 — Accepted intent**: A check-in MUST be rejected when its Checkout is
  already closed, and both the record and the Asset MUST remain unchanged.
  *(Source: current rejection is test-verified; consistent with `CONTEXT.md`,
  **Checkout**.)*
- **FR-010 — Accepted intent**: A return condition MUST be one of `New`, `Good`,
  `Average`, `Damaged`, or `Repair Required`. A noncanonical value MUST be
  rejected without changing the Checkout, the Asset status, the Custodian, or
  the Asset condition.
  *(Sources: `CONTEXT.md`, **Asset**; Draft B2 FR-003 and FR-011; current
  rejection is test-verified.)*
- **FR-011 — Accepted intent**: A Checkout and a check-in MUST each apply their
  record change, Asset status change, and Custodian effect as one atomic
  operation, so that no partial custody state is user-visible.
  *(Sources: `.specify/memory/constitution.md`, Principle II; Draft B2
  ALR-003.)*
- **FR-012 — Accepted intent**: A closed Checkout MUST NOT be reopened, and a
  check-in MUST NOT retain or later restore the previous Custodian. Returning an
  Asset to a holder MUST require a new Checkout.
  *(Sources: `CONTEXT.md`, **Checkout** and **Service Record**; ADR-0001.)*
- **FR-013 — Accepted intent**: A Checkout record MUST identify its Asset, its
  Checkout User, the custody operator who performed the Checkout, the checkout
  time, and its open or returned state; a returned record MUST additionally
  identify the return time and the return condition.
  *(Source: `CONTEXT.md`, **Checkout**; observable acceptance cases AS-019 and
  AS-020. Field naming is governed by FR-018.)*
- **FR-014 — Stakeholder-confirmed**: A Checkout record MUST retain intake
  remarks and return remarks as distinct values, and a check-in MUST NOT
  overwrite or discard the intake remarks of the same session. Both are
  optional, except that return remarks MUST be supplied when the return
  condition is worse than that session's checkout condition; a check-in missing
  them MUST be rejected. A purpose MAY be recorded at Checkout.
  *(Sources: `CONTEXT.md`, **Checkout**, custody accountability; intake remark
  persistence is test-verified; stakeholder clarification, 2026-08-04. The
  current overwrite is a conformance gap.)*
- **FR-015 — Accepted intent**: Opening a Service Record on an Asset with an
  open Checkout MUST close that Checkout as part of the same operation and MUST
  clear the Custodian before the Asset becomes `Under Repair`.
  *(Sources: `CONTEXT.md`, **Service Record**; ADR-0001; current behavior is
  test-verified.)*
- **FR-016 — Accepted intent**: An accepted terminal transition on an Asset with
  an open Checkout MUST close that Checkout atomically with the transition.
  *(Source: Draft B2 ALR-006; current behavior is test-verified.)*
- **FR-017 — Accepted intent**: A Checkout closed by an interrupting operation
  MUST remain distinguishable from one closed by an ordinary check-in, and MUST
  remain visible in the Asset's custody history.
  *(Sources: Draft B2 ALR-006 and AS-022; `CONTEXT.md`, **Checkout**.)*
- **FR-018 — Accepted intent (C3)**: Every user-visible Checkout surface, label,
  history panel, message, and record field name MUST use `Checkout` and MUST NOT
  use `Assignment`. A field or label that implies an approval step MUST NOT be
  presented for this lifecycle.
  *(Sources: `CONTEXT.md`, **Checkout**; `ROADMAP.md` decision C3; Draft B2
  FR-004.)*
- **FR-019 — Accepted intent**: The current Checkout MUST NOT be described or
  offered as employee self-service. An employee MUST NOT be able to create a
  Checkout for themselves in this version.
  *(Sources: `CONTEXT.md`, **Checkout**; `ROADMAP.md`, F2.)*
- **FR-020 — Stakeholder-confirmed**: A successful Checkout MUST request an
  in-app Notification for the new Custodian and for every `asset_custody_manage`
  holder. A successful check-in MUST request one for the returning Checkout User
  and for every `asset_custody_manage` holder. An interrupting closure MUST
  request one for the Checkout User whose custody ended. An Overdue Checkout
  MUST request one for the Custodian and for every `asset_custody_manage`
  holder. Every Notification MUST address a specific User and MUST carry a
  destination that resolves to the referenced Asset's detail surface. Shared
  in-app delivery, retry, read state, access, and retention remain owned by B8.
  *(Sources: stakeholder clarification, 2026-08-04; Draft B8 FR-002, FR-008, and
  FR-018 for the shared boundary.)*
- **FR-021 — Evidence integrity**: Every Checkout behavior in this Draft that is
  observed only in implementation MUST remain labelled implementation-only until
  backed by a test or an explicit stakeholder decision, and MUST NOT be promoted
  into an accepted requirement by this specification run.
  *(Source: `.specify/memory/constitution.md`, Principle III.)*
- **FR-022 — Decision gate**: U-001 through U-005 are resolved and MUST NOT be
  reopened by observing current implementation behavior. U-001 through U-004 were
  resolved by the stakeholder clarification dated 2026-08-04; U-005 was resolved
  by the B4 clarification of the same date, which decided C1 in favor of
  Checkout, and was absorbed into this Draft on 2026-08-12. No decision gate now
  blocks B3 acceptance. The conformance gaps in U-006 are delivery obligations
  against accepted requirements and MUST NOT be treated as reopened decisions or
  as grounds to weaken a requirement.
  *(Sources: `ROADMAP.md`, decision register C1;
  `specs/006-transfer-baseline/spec.md`, clarification 2026-08-04;
  `.specify/memory/constitution.md`, Principle III.)*
- **FR-023 — Stakeholder-confirmed**: Check-in MUST clear the Asset department
  together with the Custodian.
  *(Sources: Draft B2 FR-015 and AS-005; stakeholder clarification,
  2026-08-04.)*
- **FR-024 — Stakeholder-confirmed**: A return condition MUST be supplied at
  check-in. A check-in that omits it MUST be rejected without changing the
  Checkout or the Asset, and no default return condition MUST be applied. The
  sole exception is an interrupting closure under FR-028.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-025 — Stakeholder-confirmed**: A check-in that changes the Asset condition
  MUST create an Asset condition-inspection history row recording that change,
  so the Asset's condition history remains complete.
  *(Sources: stakeholder clarification, 2026-08-04; Draft B2 condition-history
  ownership.)*
- **FR-026 — Stakeholder-confirmed**: An expected return date is optional. When
  supplied it MUST be the current date or later, and an earlier date MUST be
  rejected. An open Checkout whose expected return date has passed MUST be
  derived as Overdue, MUST be identifiable on Checkout surfaces, and MUST
  proactively notify the Custodian and every `asset_custody_manage` holder.
  Overdue MUST NOT be an Asset status and MUST NOT by itself block another
  custody operation.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-027 — Stakeholder-confirmed**: An AuditLog entry MUST be created for every
  successful Checkout, every successful check-in, every rejected or
  permission-denied Checkout or check-in attempt, and every interrupting
  closure. Each entry MUST identify the operator or attempting actor, the Asset,
  the Checkout User, the resulting or attempted status, Custodian, and
  department effects, and the condition recorded; a rejected attempt MUST also
  identify the reason. Shared AuditLog storage, access, filtering, and retention
  remain owned by B8.
  *(Sources: stakeholder clarification, 2026-08-04; Draft B8 FR-014 through
  FR-017 for the shared boundary.)*
- **FR-028 — Stakeholder-confirmed**: An interrupting closure MUST close the
  Checkout atomically with the operation that caused it, MUST mark it
  closed-as-interrupted so it remains distinguishable from a check-in, and MUST
  take its return condition from the Asset's current condition because no
  operator supplies one. It MUST NOT be treated as a check-in for the purposes
  of FR-014 or FR-024.
  *(Sources: `CONTEXT.md`, **Service Record**; ADR-0001; Draft B2 ALR-006;
  stakeholder clarification, 2026-08-04.)*
- **FR-029 — Accepted intent (Checkout User eligibility)**: A Checkout User MUST be an active
  User. A Checkout naming a Disabled User MUST be rejected without changing the
  Asset or creating a record. Holding no Role MUST NOT disqualify a User from
  being a Checkout User.
  *(Derived, not newly decided. The active-User limit follows Draft B1 FR-004,
  which excludes a Disabled User from the minimal active-User directory that
  CAND-013 records as the selection source, and from custody accountability:
  a deactivated User cannot be answerable for an Asset. The no-Role clause
  follows ALR-006 — the Checkout User is a subject of the record and holds no
  permission by virtue of that role, so requiring a Role would contradict it.)*

  **Implementation conformance gap**: the Checkout serializer accepts any User
  reference without a status check (`backend/assets/serializers.py`), so a
  Disabled User can be made Custodian through the API even though the frontend
  selector offers only active Users.
- **FR-030 — Accepted intent (Checkout condition treatment)**: The checkout condition records the
  Asset's condition at handover. It MUST be one of the canonical conditions in
  FR-010, MUST default to the Asset's current condition when not supplied, and
  MUST NOT change the Asset's own condition — only the return condition does
  that, under FR-025.
  *(Derived, not newly decided. FR-010 already restricts the *return* condition
  to the canonical set, and Draft B2 FR-003 requires every Asset to carry exactly
  one canonical condition; a Checkout record holding a non-canonical value would
  contradict both. The default and the no-effect-on-Asset-condition rule state
  current behavior recorded in CAND-003.)*

  **Implementation conformance gap**: the checkout condition is stored without
  validation (`backend/assets/checkout.py`), so a Checkout record can carry a
  value outside the canonical set while a check-in rejects that same value —
  the asymmetry recorded in §Edge Cases.

### Current-System Contract Candidates — Not Accepted Requirements

These record current behavior only. Where the 2026-08-04 clarification decided
the matter, the cited functional requirement is authoritative and the candidate
below survives solely as the current-state record; each resulting difference is
registered in U-006.

- **CAND-001**: A Checkout record currently holds an Asset reference, a Checkout
  User, a checkout timestamp set at creation, an optional expected return date,
  an optional return timestamp, the acting operator in a field named
  `approved_by`, an optional purpose of up to 255 characters, a checkout
  condition, a return condition, free-text remarks, and a textual state
  defaulting to `Open` with `Returned` as its only other observed value.
- **CAND-002**: Checkout creation currently accepts only the Asset, the Checkout
  User, the expected return date, the purpose, the checkout condition, and the
  remarks. The checkout timestamp, return timestamp, operator, return condition,
  and state are server-controlled.
- **CAND-003**: The checkout condition currently defaults to the Asset's current
  condition when omitted and is stored without validation when supplied. It
  never changes the Asset's own condition.
- **CAND-004**: The expected return date is currently optional, unvalidated,
  never compared against the current date, and produces no overdue state,
  Notification, report, or restriction. One dashboard panel displays it beside
  open Checkouts.
- **CAND-005**: Check-in currently requires no request body: an omitted
  condition is defaulted to `Good` at the interface boundary before the
  canonical-set validation runs, and the check-in surface preselects `Good`.
- **CAND-006**: Check-in currently sets the Asset condition to the return
  condition without creating a condition-inspection history row.
- **CAND-007**: Check-in currently replaces the Checkout record's remarks with
  the submitted return remarks, or with an empty value when none are submitted.
- **CAND-008**: Check-in currently clears the Custodian and leaves the Asset
  department unchanged.
- **CAND-009**: Checkout currently copies the Checkout User's department only
  when that User has one, and otherwise leaves the Asset's previous department
  in place.
- **CAND-010**: Checkout currently notifies the new Custodian with the message
  "Asset {asset id} has been checked out to you." and check-in currently
  notifies the Checkout User with "Asset {asset id} check-in recorded. Thank
  you." Both destinations are `/asset/{id}`, which does not match the frontend
  Asset-detail route.
- **CAND-011**: Checkout list and retrieve currently require `asset_view`;
  create and check-in require `asset_custody_manage`; every other operation on a
  Checkout record, including direct update and delete, falls through to an
  Admin-only rule.
- **CAND-012**: The Checkout list is currently global, unpaginated, ordered
  newest first, and filterable only by exact state.
- **CAND-013**: The Checkout creation surface currently offers only `Available`
  Assets, offers the full active-User directory obtained with `asset_view`,
  requires only an Asset and a User, offers the five canonical conditions, and
  redirects to the Checkout list after a success message.
- **CAND-014**: The Checkout list surface currently gates its create and
  check-in controls on `asset_custody_manage` and shows the check-in control
  only for open records; its route requires `asset_view` and the create route
  requires `asset_custody_manage`.
- **CAND-015**: An interrupting closure currently sets the return condition from
  the Asset's current condition, appends an explanatory note to the record's
  remarks, records no operator, sends no Notification, and closes every open
  Checkout on the Asset.
- **CAND-016**: A successful Checkout currently creates one audit entry in a
  "Checkouts" module recording the Asset and the Checkout User, and a successful
  check-in creates one recording the Asset and the returning User. Both use the
  phrases "usage session started" and "usage session ended".
- **CAND-017**: Rejected Checkouts, rejected check-ins, denied attempts, and
  interrupting closures currently create no audit entry of their own.
- **CAND-018**: Checkout records are currently removed when their Asset is
  deleted and when their Checkout User is deleted.
- **CAND-019**: The eligibility check and record creation currently run inside
  one atomic operation using a row lock that is a no-op on the current database
  engine.
- **CAND-020**: No dedicated automated test covers the check-in permission path,
  the check-in Notification, the `Good` default, department retention, remark
  replacement, the direct-record Admin path, or any frontend Checkout behavior.

### Authorization and Lifecycle Requirements

- **ALR-001 — Accepted intent**: Creating a Checkout and performing a check-in
  MUST require `asset_custody_manage`. Reading Checkout records MUST require
  `asset_view`.
  *(Sources: `CONTEXT.md`, **Checkout**; Draft B2 Accepted Asset Permission
  Contract; the create permission requirement is test-verified.)*
- **ALR-002 — Accepted intent**: Admin, IT Manager, and IT Staff are the accepted
  actors for Checkout and check-in. Every other named Role MUST be denied both
  operations, including HR, Viewer, and Employee.
  *(Sources: `CONTEXT.md`, **Checkout**; Draft B2 Accepted Asset Permission
  Contract.)*
- **ALR-003 — Governance requirement**: Authorization MUST be enforced at the
  protected action boundary. Hiding a Checkout or check-in control in a frontend
  surface MUST NOT be the sole control.
  *(Source: `.specify/memory/constitution.md`, Principle II.)*
- **ALR-004 — Accepted intent**: A denied or rejected Checkout or check-in MUST
  leave the Asset status, Custodian, department, condition, and every Checkout
  record unchanged.
  *(Sources: `.specify/memory/constitution.md`, Principle II; Draft B2
  ALR-002.)*
- **ALR-005 — Accepted intent**: Checkout and check-in MUST be the only
  operations that move an Asset into and out of `Assigned` for a nonterminal
  outcome. Editing a Checkout record directly MUST NOT be a supported way to
  change Asset status, Custodian, or department.
  *(Sources: Draft B2 ALR-004 and ALR-007. The current Admin-only direct
  record path is a conformance gap.)*
- **ALR-006 — Accepted intent**: The Checkout User is a subject of the record,
  not an actor in it. No permission is granted to a User by being the Custodian,
  and being the Custodian MUST NOT allow that User to perform their own check-in
  in this version.
  *(Sources: `CONTEXT.md`, **Checkout**; `ROADMAP.md`, F2.)*
- **ALR-007 — Accepted integration boundary**: An interrupting operation owned by
  B5 or B2 MUST be able to close an open Checkout as part of its own atomic
  operation. B3 MUST NOT require a check-in in those paths and MUST NOT leave
  the Checkout open.
  *(Sources: ADR-0001; Draft B2 ALR-006; current behavior is test-verified.)*
- **ALR-008 — Stakeholder-confirmed**: The AuditLog entries required by FR-027
  MUST be created for successful, rejected, denied, and interrupted Checkout
  operations. A required entry MUST commit with its business action, and a
  denied attempt MUST be audited without exposing Checkout or Asset data to the
  denied actor. Access to the resulting entries is owned by B8.
  *(Sources: stakeholder clarification, 2026-08-04; Draft B8 FR-011 and FR-016
  for the shared boundary.)*

### Accepted Checkout Actor and Permission Contract

| Checkout action | Permission code | Accepted named-Role behavior | Evidence status |
| --- | --- | --- | --- |
| List and retrieve Checkout records | `asset_view` | Admin, IT Manager, IT Staff, HR, and Viewer; Employee scope owned by B1/B2 | Accepted actor intent; current global scope is implementation-only |
| Create a Checkout | `asset_custody_manage` | Admin, IT Manager, and IT Staff | Accepted intent; the permission requirement is test-verified |
| Perform a check-in | `asset_custody_manage` | Admin, IT Manager, and IT Staff | Accepted intent; the permission mapping is implementation-only |
| Be the Checkout User | None | Any active User | Accepted intent; the current directory source is implementation-only |
| Edit or delete a Checkout record directly | Not accepted | None | Implementation-only conformance gap against ALR-005 |

### Accepted Checkout Notification and Audit Trigger Matrix

B8 FR-018 requires B3 to own this matrix. Every row is stakeholder-confirmed by
the 2026-08-04 clarification. B8 owns shared delivery, read state, access, and
retention after these inputs are supplied.

| Business event | Notification recipients | Message meaning | Destination | Required AuditLog entry |
| --- | --- | --- | --- | --- |
| Checkout succeeds | New Custodian; every `asset_custody_manage` holder | The Asset is now in this User's custody | Asset detail surface | Operator, Asset, Checkout User, resulting status/Custodian/department, checkout condition |
| Check-in succeeds | Returning Checkout User; every `asset_custody_manage` holder | The return has been recorded | Asset detail surface | Operator, Asset, Checkout User, resulting status, cleared Custodian/department, return condition |
| Open Checkout becomes Overdue | Custodian; every `asset_custody_manage` holder | The Asset is past its expected return date | Asset detail surface | Not required |
| Checkout rejected — Asset not `Available`, or expected return date in the past | None | — | — | Actor, attempted operation, Asset, reason |
| Check-in rejected — closed Checkout, missing or noncanonical condition, or missing return remarks | None | — | — | Actor, attempted operation, Asset, reason |
| Checkout or check-in denied for missing permission | None | — | — | Actor, attempted operation, Asset, reason; no data exposed to the denied actor |
| Checkout closed by an opening Service Record | The Checkout User whose custody ended | Custody ended because the Asset went for service | Asset detail surface | Causing operation, Asset, Checkout User, return condition |
| Checkout closed by a terminal transition | The Checkout User whose custody ended | Custody ended because the Asset left circulation | Asset detail surface | Causing operation, Asset, Checkout User, return condition; B2 additionally requires the closure in its terminal entry |

Opening a Service Record also notifies the previous Custodian from B5. B3's
interrupted-closure Notification and B5's service Notification address the same
User for the same event; whether they are merged into one message is a planning
concern for the two owning baselines, not a change to either accepted trigger.

### Key Entities

- **Checkout**: One usage session for one Asset and one Checkout User, opened by
  a custody operator and closed by a check-in or by an interrupting operation.
  It carries the checkout time, an optional expected return date, an optional
  purpose, a checkout condition, and remarks; a closed session additionally
  carries a return time and a return condition. Its state is open or returned.
- **Checkout User**: The active User who receives custody and becomes the Asset's
  Custodian for the duration of the session.
- **Custody operator**: The Admin, IT Manager, or IT Staff actor who performs the
  Checkout or check-in on the Checkout User's behalf. Currently recorded in a
  field presented as `approved_by`, which FR-018 rejects as an approval-implying
  label.
- **Expected return date**: An optional date recorded at Checkout that must be
  the current date or later. An open Checkout past this date becomes Overdue
  under FR-026.
- **Overdue**: A derived state of an open Checkout whose expected return date has
  passed. It is not an Asset status, does not block another custody operation,
  and clears when the Checkout closes.
- **Checkout condition**: The condition recorded when custody begins. It
  currently defaults from the Asset and never changes the Asset's condition.
- **Return condition**: The mandatory condition recorded at check-in under
  FR-024. It sets the Asset's condition and produces a condition-inspection
  history row under FR-025. An interrupting closure instead copies the Asset's
  current condition under FR-028.
- **Intake remarks and return remarks**: Distinct retained values on one Checkout
  record. Return remarks are mandatory when the return condition is worse than
  the checkout condition (FR-014).
- **Interrupted closure**: The closing of an open Checkout by an opening Service
  Record or an accepted terminal transition. The record is marked
  closed-as-interrupted and stays distinguishable from a check-in (FR-028).
- **Asset**: Owned by B2. B3 changes only its status, Custodian, department, and
  condition, and only through Checkout and check-in.
- **Department**: Owned by B1 as organizational data and by B2 as an Asset
  attribute. Checkout sets it from the Checkout User and check-in clears it with
  the Custodian (FR-006, FR-023).
- **Notification**: The shared in-app record owned by B8. B3 owns the trigger,
  the recipients, the message meaning, and the destination, as set out in the
  accepted trigger matrix.
- **AuditLog**: The shared operational record owned by B8. B3's required events
  and their content are defined in FR-027.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 11 Checkout-relevant automated tests pass in one verification
  run: seven Checkout lifecycle tests, two Checkout endpoint tests, one
  Service-Record interruption test, and one terminal-transition closure test.
- **SC-002**: 100% of Checkout, check-in, permission, condition, remark,
  expected-return, notification, audit, interface, and interrupting-closure
  observations in this Draft are labelled accepted intent, test-verified,
  implementation-only, or unresolved, and cite a repository path, an accepted
  specification identifier, or `CONTEXT.md`.
- **SC-003**: In a full custody round trip, one `Available` Asset reaches
  `Assigned` with exactly one Custodian and exactly one open Checkout, and after
  check-in returns to `Available` with zero Custodians and zero open Checkouts.
- **SC-004**: In a rejection matrix covering an unavailable Asset, an already
  closed Checkout, a noncanonical return condition, and a missing permission,
  100% of attempts are rejected and produce zero changes to Asset status,
  Custodian, department, condition, and Checkout records.
- **SC-005**: In a permission matrix over Admin, IT Manager, IT Staff, HR,
  Viewer, and Employee, exactly the first three succeed at Checkout and
  check-in, and 100% of the remaining attempts are denied at the protected
  action boundary rather than only in the interface.
- **SC-006**: A terminology review of every user-visible Checkout surface,
  label, message, and record field returns zero occurrences of `Assignment` for
  this lifecycle and zero approval-implying labels; the current review returns
  two known violations (the Asset detail "Assignment & Warranty" panel and the
  `approved_by` field).
- **SC-007**: For every interrupting operation, 100% of open Checkouts on the
  affected Asset are closed within the same atomic operation and zero Assets
  remain in a lifecycle state with a dangling open Checkout.
- **SC-008**: For each B3 Notification trigger, a reviewer can identify exactly
  one recipient rule, one message meaning, and one destination that resolves to
  the referenced Asset; the current review returns two triggers whose
  destination does not resolve.
- **SC-009**: 100% of the four roadmap-listed B3 acceptance blockers — department
  semantics after check-in, default return condition, expected-return
  obligations, and audit requirements — carry an explicit stakeholder decision
  recorded in the Clarifications section, leaving exactly one open blocker (C1).
- **SC-010**: Every Draft B2 requirement that B3 depends upon is either
  satisfied by current behavior or recorded as a named conformance gap; the
  current review returns three gaps (department retention at check-in,
  department retention when the Checkout User has none, and the Admin-only
  direct record path).
- **SC-011**: In overdue verification, 100% of open Checkouts past their expected
  return date are identifiable as Overdue and notify both the Custodian and every
  `asset_custody_manage` holder; 100% of Checkouts submitted with a past
  expected return date are rejected; and Overdue appears as an Asset status in
  0% of cases.
- **SC-012**: In an audit-completeness review, 100% of successful Checkouts,
  successful check-ins, rejected attempts, denied attempts, and interrupting
  closures produce exactly one AuditLog entry carrying the FR-027 content, and
  0% of denied attempts expose Checkout or Asset data to the denied actor.
- **SC-013**: In a recipient review of every B3 trigger, 100% of required
  recipients receive a Notification, 100% of destinations resolve to the
  referenced Asset's detail surface, and 0 unlisted recipients are added.
- **SC-014**: In remarks verification, 100% of check-ins preserve their session's
  intake remarks, and 100% of check-ins recording a condition worse than the
  checkout condition are rejected unless return remarks are supplied.

## Assumptions

- This is a documentation-only AS-BUILT baseline. It records current evidence
  and accepted adjacent intent without changing application code, tests,
  routes, interfaces, or configuration.
- The Draft B2 baseline is the current dependency for Asset status, condition,
  Custodian, department, terminal transitions, and Asset permissions, and
  remains subject to its own acceptance review. B3 consumes those rules without
  independently redefining them; where B3 records a divergence, it does so as a
  conformance gap or unresolved conflict rather than as a new rule.
- B1 owns User identity, Role administration, Department master data, the User
  directory, and User deletion. B3 consumes the resulting User and Department
  values.
- B8 owns shared Notification delivery and AuditLog storage, access, and
  retention. B8 is Draft, so its shared minimums are dependencies rather than
  accepted B3 requirements.
- B4 owns Transfer entirely, and B5 owns Service Record entirely. B3 records
  only the two documented integration boundaries: opening a Service Record
  closes an interrupted Checkout, and closing one requires a fresh Checkout.
- B9 owns dashboard and report presentation of Checkout data, including how an
  expected return date is displayed.
- `User` means the B1 User profile. The separate linked login account is B1
  implementation detail.
- Current frontend Checkout surfaces have no behavioral tests, so their behavior
  is implementation-only even where it matches backend behavior.
- "Custody operator" is a description of the accepted actor set in this Draft,
  not a new Role. Role names remain those seeded and administered under B1.
- FR-014's "worse than" comparison assumes the canonical condition list is a
  severity ranking in the order `New`, `Good`, `Average`, `Damaged`,
  `Repair Required`, so any move toward the end of that list is a worsening.
  `CONTEXT.md` states the list but not the ranking, so this ordering is derived
  rather than sourced and should be confirmed at review; it does not block
  acceptance because the rule is otherwise complete.
- FR-026's proactive Overdue delivery requires production scheduling. C5, owned
  by B7, records that the current in-process scheduler starts only under the
  development server and offers no production guarantee. B3 accepts the Overdue
  requirement and inherits that delivery-guarantee risk; resolving the scheduling
  mechanism remains a C5 engineering decision and is not reopened here.
- Overdue is evaluated against the calendar date in the deployment's configured
  timezone. Exact evaluation frequency and deduplication of repeated Overdue
  Notifications are planning concerns within B8's shared retry and
  deduplication contract.

## Baseline Evidence and Unresolved Conflicts *(Brownfield Baseline only)*

### Accepted Intent

- Checkout moves an Asset `Available → Assigned` for one User and back to
  `Available` on check-in, with no approval gate and no `Pending` state:
  `CONTEXT.md`, **Checkout**.
- Checkout sets the Custodian, check-in clears it, and Asset `status` remains
  authoritative for availability: `CONTEXT.md`, **Custodian**.
- Only IT Manager or IT Staff hold `asset_custody_manage`; IT performs every
  Checkout in person and employees cannot check out Assets to themselves:
  `CONTEXT.md`, **Checkout**.
- `Checkout` is the canonical term and `Assignment` is rejected:
  `CONTEXT.md`, **Checkout**; `ROADMAP.md` decision C3; Draft B2 FR-004.
- Employee self-service Checkout is deferred future scope, not current behavior:
  `CONTEXT.md`, **Checkout**; `ROADMAP.md`, F2.
- Checkout sets Custodian and department, and check-in clears the Custodian;
  `Assigned` is entered and left only through the owning operation; a terminal
  transition atomically closes an open Checkout; and the accepted custody
  permission is `asset_custody_manage` held by Admin, IT Manager, and IT Staff:
  `specs/001-asset-register-lifecycle-baseline/spec.md`, AS-004, AS-005,
  AS-017, FR-006, FR-012, FR-015, ALR-004, ALR-006, ALR-007, and the Accepted
  Asset Permission Contract.
- Opening a Service Record mirrors check-in by clearing the Custodian, and
  closing one never restores the previous Custodian — a fresh Checkout is
  required: `CONTEXT.md`, **Service Record**;
  `docs/adr/0001-service-record-lifecycle.md`.
- B3 owns its explicit Notification and audit trigger matrix while B8 owns
  shared in-app delivery and storage:
  `specs/004-notifications-audit-baseline/spec.md`, FR-002, FR-008, FR-018
  (Draft dependency).
- Brownfield evidence must not be promoted to product intent without explicit
  acceptance: `.specify/memory/constitution.md`, Principle III.

### Verified Behavior Evidence

All 11 tests below passed on 2026-08-04 in the repository-local environment
(`backend/Env/Scripts/python.exe manage.py test`, 11 tests, OK, no system-check
issues).

- **OBS-AS-001**: Checkout sets `Assigned`, Custodian, the User's department,
  and a checkout condition defaulted from the Asset:
  `backend/assets/tests.py::CheckoutLifecycleTests::test_check_out_assigns_asset_to_user_and_their_department`.
- **OBS-AS-002**: Intake remarks are persisted on the Checkout record:
  `backend/assets/tests.py::CheckoutLifecycleTests::test_check_out_persists_intake_remarks`.
- **Checkout Notification trigger**: A successful Checkout notifies the new
  Custodian:
  `backend/assets/tests.py::CheckoutLifecycleTests::test_check_out_notifies_the_new_custodian`.
- **OBS-AS-014**: Checkout of a non-`Available` Asset is rejected:
  `backend/assets/tests.py::CheckoutLifecycleTests::test_check_out_rejects_an_unavailable_asset`.
- **OBS-AS-007**: Check-in closes the record as returned with a return date and
  return condition, sets the Asset to `Available`, clears the Custodian, and
  applies the submitted condition and remarks:
  `backend/assets/tests.py::CheckoutLifecycleTests::test_check_in_returns_asset_to_available_with_new_condition`.
- **OBS-AS-015**: Check-in of an already closed Checkout is rejected:
  `backend/assets/tests.py::CheckoutLifecycleTests::test_check_in_rejects_an_already_closed_checkout`.
- **OBS-AS-016**: Check-in with a noncanonical condition is rejected:
  `backend/assets/tests.py::CheckoutLifecycleTests::test_check_in_rejects_an_invalid_condition`.
- **OBS-AS-013**: Checkout creation without `asset_custody_manage` returns
  `403`:
  `backend/assets/tests.py::CheckoutTransferEndpointTests::test_checkout_create_requires_asset_custody_manage_permission`.
- **OBS-AS-021**: A permitted operator completes a create-then-check-in round
  trip returning `201` then `200` with state `Returned`:
  `backend/assets/tests.py::CheckoutTransferEndpointTests::test_checkout_create_and_checkin_round_trip`.
- **OBS-AS-027**: Opening a Service Record closes the Checkout it interrupts,
  with a return date, before the Asset becomes `Under Repair`:
  `backend/assets/tests.py::ServiceRecordLifecycleTests::test_open_service_closes_the_open_checkout_it_interrupts`.
- **OBS-AS-028**: Entering a terminal status closes the open Checkout:
  `backend/assets/tests.py::AssetStatusTransitionTests::test_entering_terminal_status_closes_the_open_checkout`.

No automated test covers the check-in permission path, the check-in
Notification, the `Good` check-in default, department behavior after check-in,
remark replacement, direct Checkout record editing, audit entries, or any
frontend Checkout surface. No frontend behavioral test harness exists
(`frontend/package.json`).

### Implementation-Only Observations

- Checkout and check-in lifecycle operations, the atomic block, the no-op row
  lock, the department copy condition, the checkout-condition default, the
  remark replacement at check-in, the Asset condition assignment at check-in,
  the retained department at check-in, the two Notification messages and their
  `/asset/{id}` destinations, and the interrupting-closure helper:
  `backend/assets/checkout.py`.
- Checkout record fields, including the operator field named `approved_by`, the
  optional expected return date, purpose, checkout condition, return condition,
  remarks, and the textual state; plus cascade deletion from Asset and from
  Checkout User: `backend/assets/models.py`.
- Checkout permission map (`asset_view` for read, `asset_custody_manage` for
  create and check-in, Admin-only fallback for every other operation), the exact
  state filter, newest-first global ordering, the `Good` check-in default, the
  `400` lifecycle-error responses, and the two audit calls in a "Checkouts"
  module: `backend/assets/views.py`.
- Writable and server-controlled Checkout fields and the absence of any
  validation on the checkout condition or the expected return date:
  `backend/assets/serializers.py`.
- Interrupting closure at Service Record open, and the accompanying previous-
  Custodian Notification owned by B5: `backend/assets/service.py`.
- Interrupting closure on an accepted terminal transition, invoked from the
  Asset serializer: `backend/assets/serializers.py`.
- Route registration for `/checkout/` and `/checkout/{id}/checkin/`:
  `backend/assets/urls.py`.
- Permission resolution, the Admin and superuser bypass, and the active-profile
  requirement: `backend/core/permissions.py`; `backend/accounts/models.py`.
- Shared in-app Notification creation, the silent no-op for a missing profile,
  and audit-entry creation: `backend/core/services.py`.
- The active-User directory used to choose a Checkout User, exposed under
  `asset_view`: `backend/accounts/views.py`;
  `backend/accounts/serializers.py`.
- Checkout creation surface: `Available`-only Asset source, full active-User
  directory, optional expected return date, purpose, canonical condition list,
  Asset-and-User-only validation, and post-success redirect:
  `frontend/src/pages/checkout/Create.jsx`.
- Checkout list surface: permission-gated create and check-in controls,
  open-only check-in control, `Good` preselection, return remarks field, and
  displayed columns: `frontend/src/pages/checkout/Checkouts.jsx`.
- Checkout routes and their route-level permissions: `frontend/src/App.jsx`.
- Asset detail Checkout History panel and the "Assignment & Warranty" panel
  label: `frontend/src/pages/asset/Detail.jsx`.
- Dashboard open-Checkout count, recent open-Checkout panel, and expected-return
  display: `backend/reporting/views.py`; `frontend/src/pages/Dashboard.jsx`.
- The consolidated current-system evidence and its E1/R1 assessment:
  `docs/research/itams-current-system-baseline.md`, sections 1.2, 2.3, 3.4, and
  5.

### Unresolved Conflicts

- **U-001 — Department semantics after check-in — RESOLVED 2026-08-04**: The
  stakeholder confirmed Draft B2 FR-015: check-in clears the department with
  the Custodian, and Checkout sets it from the Checkout User or empties it when
  that User has none. B2 needs no amendment. Recorded in FR-006 and FR-023;
  current retention at both points is now a conformance gap in U-006.
- **U-002 — Default return condition — RESOLVED 2026-08-04**: The stakeholder
  made the return condition mandatory with no default, and required every
  check-in condition change to create a condition-inspection history row.
  Recorded in FR-024 and FR-025; the current `Good` default and the missing
  history row are now conformance gaps in U-006.
- **U-003 — Expected-return obligations — RESOLVED 2026-08-04**: The stakeholder
  made the expected return date optional but required it to be the current date
  or later, introduced Overdue as a derived Checkout state, and required
  proactive notification of the Custodian and every `asset_custody_manage`
  holder. Recorded in FR-026; the absent validation and absent Overdue concept
  are now conformance gaps in U-006. The delivery-guarantee dependency on C5 is
  recorded in Assumptions.
- **U-004 — Audit requirements — RESOLVED 2026-08-04**: The stakeholder required
  audit entries for successful Checkouts and check-ins, rejected and denied
  attempts, and interrupting closures, with defined content. Recorded in FR-027
  and ALR-008; the currently missing entries are conformance gaps in U-006.
- **U-005 — C1, Store-to-User issuance — RESOLVED 2026-08-04, ABSORBED
  2026-08-12** *(shared with B4)*: `CONTEXT.md` says Transfer always moves
  custody between two Users, which implies that handing an unheld `Available`
  Asset to a User is a Checkout. The current Transfer implementation accepts an
  `Available` Asset with no Custodian and labels the empty previous owner
  "IT Store" (`backend/assets/transfer.py`;
  `frontend/src/pages/transfer/Create.jsx`).

  **Resolution.** The B4 clarification dated 2026-08-04 decided C1: Store-to-User
  issuance is a **Checkout**, because issuance has no approval gate.
  `ROADMAP.md`'s decision register records C1 as resolved. This entry previously
  read "Until C1 is decided…", which was stale from the day it was written — the
  decision existed and had simply not been absorbed here.

  **Effect on B3: none.** C1 confirms the boundary this Draft already states
  rather than changing it. FR-001 and FR-008 already require Checkout to move an
  Asset from `Available` and to be rejected otherwise; C1 establishes that the
  only way an `Available` Asset leaves `Available` into a User's custody is a
  Checkout, which is exactly that boundary. No requirement text changes, and the
  eligibility contract that this finding called incomplete is complete.

  **Effect on B4: unchanged and still open.** The no-Custodian `IT Store`
  Transfer path remains reachable, which C1 rejects. That is recorded as an open
  conformance gap in Draft B4 and is not B3's to close.
- **U-006 — Conformance gaps recorded, not accepted**: The current behaviors
  below contradict accepted requirements in this Draft. Each is recorded as a
  gap rather than reconciled by weakening a requirement. Whether a gap is
  corrected, deferred, or formally excepted is a review decision, not a
  specification decision.

| # | Current behavior | Accepted requirement | Current-state record |
| --- | --- | --- | --- |
| 1 | Check-in retains the Asset department | FR-023 | CAND-008 |
| 2 | Checkout retains the previous department when the Checkout User has none | FR-006 | CAND-009 |
| 3 | An omitted return condition defaults to `Good` in both interface and surface | FR-024 | CAND-005 |
| 4 | A check-in condition change creates no condition-inspection history row | FR-025 | CAND-006 |
| 5 | Check-in replaces intake remarks; no rule requires return remarks for a worsened condition | FR-014 | CAND-007 |
| 6 | The expected return date is unvalidated and no Overdue state or notification exists | FR-026 | CAND-004 |
| 7 | Rejected, denied, and interrupting-closure paths create no AuditLog entry | FR-027 | CAND-017 |
| 8 | `asset_custody_manage` holders are not notified on Checkout or check-in, and no interrupted-closure Notification is sent | FR-020 | CAND-010, CAND-015 |
| 9 | Notification destinations do not resolve to the Asset detail route | FR-020 | CAND-010 |
| 10 | An interrupted closure carries no explicit closed-as-interrupted marker | FR-028 | CAND-015 |
| 11 | The operator field is presented as `approved_by` | FR-018 | CAND-001 |
| 12 | The Asset detail panel is labelled "Assignment & Warranty" | FR-018, C3 | OBS-AS-026 |
| 13 | An Admin or superuser may edit or delete a Checkout record directly | ALR-005 | CAND-011 |
| 14 | Two simultaneous Checkouts of one `Available` Asset are not provably prevented, because the row lock relied upon is a no-op on the current database engine | FR-011 | CAND-019 |
| 15 | Nothing in the data model prevents more than one open Checkout per Asset | FR-001, FR-007 | Edge Cases |

Rows 14 and 15 were previously recorded only in §Edge Cases with no owner, which
left them reading as open questions. They are not: FR-011 already requires a
Checkout to apply its record, status, Custodian, and department effects as one
operation with no user-visible partial state, and FR-001 with FR-007 already
confine `Assigned` to a single owning Checkout. The outcomes are specified; the
implementation does not guarantee them. They are therefore conformance gaps owned
by B3 delivery, not decisions awaiting a stakeholder — the same distinction drawn
for concurrent Asset linking in Draft B6's finding 1.

### Implementation Conformance Update

**Date**: 2026-08-12. **Commits**: `538c3a8`, `070c8c2`. Status of each U-006
row against the current implementation. This changes no requirement; the table
above is preserved as the dated review record.

| # | Status | Evidence |
| --- | --- | --- |
| 1 | **Closed** | Check-in clears the department with the Custodian (`backend/assets/checkout.py`). Test: `BaselineConformanceTests::test_check_in_clears_department_and_logs_the_inspection`. |
| 2 | Open | Checkout still retains the previous department when the Checkout User has none. |
| 3 | **Closed** | The `Good` default is removed; a check-in without a return condition is rejected (`backend/assets/checkout.py`, `backend/assets/views.py`). Test: `::test_check_in_requires_a_return_condition`. |
| 4 | **Closed** | Every check-in writes an `AssetConditionLog` row naming the operator as inspector. Test: `::test_check_in_clears_department_and_logs_the_inspection`. Note the implementation records a row on **every** check-in, not only when the condition changes — read as an inspection record, which is a superset of FR-025 and should be confirmed rather than assumed. |
| 5 | **Partly closed** | Intake and return notes are now distinct retained fields; a check-in no longer overwrites intake remarks (`return_remarks`, migration `0009`). The same fix applies to interrupting closures. Tests: `::test_check_in_clears_department_and_logs_the_inspection`, `::test_an_interrupting_closure_also_preserves_intake_remarks`, `CheckoutLifecycleTests::test_check_in_returns_asset_to_available_with_new_condition`. Still open: no rule requires return remarks when the condition has worsened. |
| 6 | Open | The expected return date is still unvalidated and no Overdue state or notification exists. |
| 7 | Open | Rejected, denied, and interrupting-closure paths still write no AuditLog entry. |
| 8 | Open | `asset_custody_manage` holders are still not notified on Checkout or check-in. |
| 9 | Open | Notification destinations still do not resolve to the Asset detail route. |
| 10 | **Partly closed** | An interrupting closure now preserves intake remarks and annotates `return_remarks`, but there is still no explicit closed-as-interrupted marker distinguishing it structurally from a check-in. |
| 11 | Open | The operator field is still presented as `approved_by`. |
| 12 | **Closed** | The Asset detail panel now reads `Custody & Warranty` (`frontend/src/pages/asset/Detail.jsx`). No frontend behavioral test exists, so the evidence is source-level only. |
| 13 | Open | Direct edit or delete of a Checkout record by an Admin or superuser is still possible. |

**U-005 was absorbed on 2026-08-12** during this Draft's acceptance review. The
note previously recorded here — that U-005 read "Until C1 is decided…" while C1
had in fact been decided on 2026-08-04 — is resolved. Absorbing the decision
proved to require no requirement change: C1 confirms the `Available`-only
boundary FR-001 and FR-008 already state. FR-022 no longer gates acceptance on
U-005, and this Draft has no open decision blocker. See §Unresolved Conflicts,
U-005.

Also newly enforced and relevant to this baseline's neighbours: a Checkout list
is now scoped to the Employee it was issued to (`backend/assets/views.py`), per
B1's C6 decision.

**Provenance note**: these changes were written implementation-first and covered
by tests afterwards, not through the red-green loop Principle IV requires.

## Out of Scope *(mandatory)*

### Adjacent Baseline Ownership

- Authentication, Users, Roles, permission-code administration, the User
  directory, Department and Location masters, and User deletion: B1. B3 consumes
  the resulting User, Role, and Department values.
- Asset identity, register, search, status and condition sets, terminal
  transitions, direct administrative edits, files, barcode, condition history,
  and aggregate Asset history: B2. B3 changes Asset status, Custodian,
  department, and condition only through Checkout and check-in.
- Approval-gated Transfer, including requester and approver permissions,
  `Pending`/`Approved`/`Rejected` outcomes, captured previous custody, Transfer
  conditions, Transfer Notifications, and Transfer documents: B4. B3 records
  only that Checkout is distinct from Transfer and that C1 is shared.
- Service Record eligibility, Vendor, dates, cost, outcome, closure, and Service
  Notifications: B5. B3 records only the two accepted integration boundaries in
  FR-015 and FR-012.
- Procurement, Vendor, and catalog masters: B6.
- Warranty, AMC, and expiry alerts: B7.
- Shared Notification storage, read state, unread counts, delivery reliability,
  AuditLog storage, administrative access, filters, and retention: B8. B3 owns
  only its trigger matrix.
- Dashboard KPIs, report catalog, report columns, and PDF/Excel/CSV exports that
  present Checkout data, including the expected-return display: B9.

### Explicitly Unresolved Rather Than Accepted

- Whether Store-to-User issuance is a Checkout or a Transfer (U-005, C1). This
  is the sole remaining acceptance blocker.
- Whether more than one open Checkout per Asset should be prevented explicitly
  rather than only implicitly by the `Available` precondition.
- Retention of Checkout history when its Asset or its Checkout User is deleted.

### Explicitly Deferred or Excluded

- Employee self-service Checkout, including pooled or available-item
  self-checkout (`ROADMAP.md`, F2).
- Any approval, request, or reservation stage for Checkout; the lifecycle has no
  approval gate by accepted intent.
- Scheduled or periodic physical Asset audits (`ROADMAP.md`, F1).
- Application-code, test-code, database, route, interface, or configuration
  changes in this documentation-only specification run.
