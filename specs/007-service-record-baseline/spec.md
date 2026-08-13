# Feature Specification: AS-BUILT Service Record Lifecycle Baseline

**Feature Branch**: `docs/baseline-spec-migration`

**Created**: 2026-08-05

**Status**: Draft

**Input**: User description: "Create an AS-BUILT Brownfield Baseline
specification for ROADMAP.md entry B5: Service Record lifecycle. Cover Vendor,
eligible Asset states, asset_custody_manage, opening and closing, Custodian
clearing, Under Repair, interrupted Checkout closure, dates, cost,
bill/remarks/outcome, notifications, audit effects, and return to Available
without restoring Custodian. Keep In Storage eligibility, department meaning
while servicing, bill/document expectations, and mandatory audit events
unresolved. Exclude Vendor administration, Procurement, Warranty/AMC, and
automatic Checkout after service. Do not modify application code."

## Clarifications

### Session 2026-08-05

- Q: Is `In Storage` service-eligible, and what status does closure restore? → A: Only `Available` and `Assigned` are eligible; closure always returns `Available`.
- Q: What does the Asset department mean while and after servicing? → A: It follows custody; opening clears it with the Custodian and closing restores neither, confirming Draft B2.
- Q: What rules apply to the sent, expected return, and return dates? → A: Sent and return dates are operator-supplied, default to now, and cannot be in the future or out of order. The desired expected-return validation, overdue signal, and custody-operator alert are retained as stakeholder intent but moved to `specs/010-service-record-overdue-alerts-change/`; they are not B5 AS-BUILT requirements.
- Q: What must a Service Record capture for cost, bill evidence, outcome, and remarks? → A: Cost is mandatory at closure with zero meaning no-charge; a bill reference and attached bill/service document are required whenever cost is above zero; outcome is one of `Repaired`, `Replaced`, `Not Repairable`, or `No Fault Found` plus optional remarks; opening and closing remarks are retained separately.
- Q: Which Notifications and AuditLog entries must Service Record events produce? → A: Opening notifies the previous Custodian and closing notifies every active `asset_custody_manage` holder, with the B3 interrupted-Checkout message kept separate; audit covers successful opening, successful closing, terminal auto-closure, and every rejected or denied attempt with its reason, under B8's failure boundary.

## Specification Lineage *(mandatory)*

**Type**: Brownfield Baseline

**Roadmap Reference**: `ROADMAP.md`, entry B5 — Service Record lifecycle;
durable feature directory `specs/007-service-record-baseline/`.

**Extends**: None. This is the initial B5 baseline.

**Supersedes**: None.

**Extended by**: `specs/010-service-record-overdue-alerts-change/spec.md` owns
the prospective expected-return validation, derived overdue visibility, and
overdue Notification behavior that the current system does not implement.

**Reciprocal Links**: `ROADMAP.md` already reserves
`specs/007-service-record-baseline/` for B5 and must link the created directory
when the B5 row moves to `R3 — draft review`. After this Draft is accepted, any
later substantive change must use a new feature directory and record reciprocal
`Extends`, `Supersedes`, or `Superseded by` lineage instead of editing accepted
requirement content here.

**Dependencies**:

- Draft B2 Asset register and lifecycle baseline
  (`specs/001-asset-register-lifecycle-baseline/`, Draft; acceptance review pending).
- Draft B1 identity and access baseline
  (`specs/003-identity-access-baseline/`) for Roles, permission codes, and data
  visibility.
- Draft B3 Checkout and check-in baseline
  (`specs/005-checkout-checkin-baseline/`) for the interrupted-Checkout
  boundary.
- Draft B6 Procurement, Vendor, and catalog masters baseline
  (`specs/002-procurement-vendor-catalog-baseline/`) for the managed Vendor
  identity B5 consumes.
- Draft B8 Notifications and AuditLog baseline
  (`specs/004-notifications-audit-baseline/`) for shared delivery, audit
  minimums, privacy, and retention.


### Acceptance Record

*Pending — this baseline is `Draft`. Completing every field below is what moves
it to accepted; until then the fields stay marked pending.*

| Field | Value |
| --- | --- |
| Stakeholder decision | *Pending* |
| Accepting stakeholder | *Pending* |
| Acceptance date | *Pending* |
| Reviewed evidence date | 2026-08-05 (specification Created date; this baseline declares no separate Evidence Date) |
| Acceptance checklist result | 70 of 70 items closed; executed 2026-08-12 — see `checklists/baseline-acceptance.md` |
| Unresolved items deliberately carried forward | *Pending* — the 17 rows in §U-005 are conformance gaps against accepted requirements. Separately, the three §Remaining Evidence-Led Confirmation Items are review items that this record must confirm rather than leave open. |
| Evidence-led confirmation items | *Pending — confirm the condition-history question (CAND-009), the Employee visibility question owned by B1, and the CHG-B5-01 delivery dependency on C5* |

**Immutability boundary**: on the acceptance date recorded above, the
requirement and acceptance content of this specification becomes an immutable
flow-forward record. From that point a semantic change MUST use a new feature
directory with reciprocal `Extends`, `Supersedes`, or `Superseded by` links;
this specification may be edited only to add or correct that non-semantic
lineage metadata. *(Constitution §III.)*

## Domain Alignment *(mandatory)*

**Canonical Terms**:

- **Service Record** is one repair or maintenance event for one Asset,
  identifying its Vendor, the dates the Asset was sent and returned, the
  cost/bill of the work, and the outcome. It is not a condition label and not a
  condition-history row.
- **Opening a Service Record** is the operation that starts that event: it
  clears the Asset's Custodian and moves the Asset to `Under Repair`.
- **Closing a Service Record** is the operation that ends that event: it returns
  the Asset to `Available` and never restores the previous Custodian.
- **Vendor** is the first-class managed third-party identity shared with
  Procurement. A Service Record MUST refer to a managed Vendor, never to
  free-typed supplier text.
- **`Under Repair`** is a canonical Asset status owned exclusively by this
  lifecycle. It is neither a condition nor a Service Record state.
- **`Open`** and **`Closed`** are Service Record states. They are not Asset
  statuses and MUST NOT be presented as such.
- **Custodian** is the User currently holding an Asset. An Asset at a Vendor has
  no Custodian.
- **Interrupted Checkout closure** is the closure of an Asset's open Checkout
  performed as part of opening a Service Record. It is owned by B3 and is not a
  check-in.
- **`condition`** and the Asset condition history remain distinct from the
  Service Record. A Service Record is the fuller event that a condition change
  is often evidence of.
- **AuditLog** is an operational event record and MUST NOT be described as a
  physical Asset audit.
- **Assignment** is rejected terminology. Restoring custody after service is a
  **Checkout**, never an assignment and never an automatic restoration.

**Relevant Decisions**:

- `CONTEXT.md`, **Service Record**: one repair/maintenance event with Vendor,
  dates sent/returned, cost/bill, and outcome; opening clears Custodian and
  moves `status → Under Repair`, mirroring check-in; closing returns
  `status → Available` and the Asset is not auto-restored to its previous
  Custodian, so IT must perform a fresh Checkout.
- `CONTEXT.md`, **Vendor**: Vendor is a first-class managed entity shared by
  Procurement and Service Record so Vendor-grouped reporting is reliable.
- `docs/adr/0001-service-record-lifecycle.md`: retaining the Custodian through
  servicing and auto-restoring the previous Custodian on close were both
  explicitly considered and rejected; reusing the Checkout/check-in pattern
  keeps one Asset in one clear state at a time; Vendor was made first-class
  rather than free text.
- Draft B2 FR-006, FR-007, FR-012, ALR-003, ALR-005, ALR-006, ALR-007, and
  FR-015: opening a Service Record clears Custodian **and department** and moves
  the Asset to `Under Repair`; closing returns it to `Available` without
  restoring Custodian or department; `Under Repair` may be entered and left only
  through this lifecycle; lifecycle transitions are atomic; a terminal
  transition atomically closes open Service Records.
- Draft B2's permission contract: Service Record open and close use
  `asset_custody_manage`, held by Admin, IT Manager, and IT Staff.
- Draft B2 FR-014 and the terminal boundary: `Lost` may be recorded from any
  nonterminal status including `Under Repair`, while `Sold` and `Scrapped` are
  accepted only from `Available` or `In Storage`.
- Draft B2's audit and notification effects: B2 register actions create
  AuditLog entries and no Notifications; Service Record workflow notifications
  remain owned by B5.
- Draft B3 FR-015, FR-017, FR-020, and FR-028: opening a Service Record on an
  Asset with an open Checkout closes that Checkout in the same operation, marks
  it closed-as-interrupted, takes its return condition from the Asset's current
  condition, keeps it distinguishable from a check-in, and requests a B3
  Notification for the Checkout User whose custody ended.
- Draft B6 FR-014 and FR-022: an Asset with no current Procurement MUST NOT
  enter Service Record activity, and a flagged legacy Vendor MUST NOT be
  selectable for new Service Record activity.
- Draft B8 FR-002, FR-008, FR-011, FR-012, FR-014, FR-015, and FR-018:
  Notifications are in-app only in this version; a required audit entry commits
  atomically with its business change; Notification failure does not roll back
  business work; and B5 must publish its own trigger matrix, which B8 may
  neither invent nor suppress.
- `ROADMAP.md` B5 review status listed four open decisions — `In Storage`
  service eligibility, department semantics while servicing, bill/document
  expectations, and mandatory audit events. The stakeholder clarification dated
  2026-08-05 resolves all four as U-001 through U-004.

**Evidence Classification**:

- **Accepted intent** comes only from `CONTEXT.md`, ADR-0001, an accepted
  dependency baseline, or an explicit recorded stakeholder decision.
- **Test-backed current behavior** is reproducible current-system evidence. It
  demonstrates behavior but is not product intent by itself.
- **Implementation-only observation** is visible in backend code or a frontend
  surface without a dedicated behavioral test and remains unaccepted.
- **Stakeholder-confirmed** is accepted intent whose authority is the dated
  clarification recorded in §Clarifications rather than `CONTEXT.md`, an ADR, or
  a dependency baseline. It carries the same requirement force.
- **Governance requirement** is required by `.specify/memory/constitution.md`
  rather than by a product decision. It applies to every capability and is not
  open to amendment during this baseline's review.

A qualifier may name the subject an accepted requirement governs — *accepted
authorization*, *accepted atomicity*, *accepted lifecycle ownership*, *accepted
rejection safety*, *accepted integration boundary*, *accepted visibility
dependency*. The qualifier narrows the subject; it never lowers the force. A
compound such as "Stakeholder-confirmed and test-backed" names the authority
first and the supporting evidence second; a test never raises or lowers a
classification.

- **Unresolved** means this Draft deliberately does not choose a rule and
  records the decision for stakeholder clarification.

**Lifecycle and Actors**:

| Stage | Actor and permission | Accepted or evidenced effect |
| --- | --- | --- |
| Read Service Records and Asset service history | `asset_view` plus B1 visibility | Draft B1 grants global records to authorized non-Employee Roles; the current queryset is global for every caller with `asset_view` |
| Open a Service Record | IT Manager or IT Staff; `asset_custody_manage` | Atomically create an `Open` record for a managed Vendor, close any interrupted Checkout, clear Custodian, and set the Asset to `Under Repair` |
| Close a Service Record | IT Manager or IT Staff; `asset_custody_manage` | Atomically mark the record `Closed`, record the return date, cost, and outcome, and return the Asset to `Available` with no Custodian |
| Restore custody after service | IT Manager or IT Staff; `asset_custody_manage` | A fresh Checkout owned by B3; never automatic and never part of closing |
| Record a terminal Asset state while servicing | B2-owned terminal operator | Atomically close every open Service Record for that Asset; the accepted terminal path from `Under Repair` is `Lost` |
| Directly edit or delete a Service Record | Not accepted | The current Admin-only fallback conflicts with lifecycle ownership and is not accepted B5 behavior |

An Asset at a Vendor has exactly one authoritative state: `Under Repair` with no
Custodian. Because opening a Service Record is the only way in and closing it is
the only way out, a Service Record is `Open` for exactly as long as its Asset is
`Under Repair`, except when an accepted terminal transition ends both together.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Send an Eligible Asset to a Vendor for Repair (Priority: P1)

A custody operator records that a specific Asset has gone to a specific managed
Vendor for repair. The Asset immediately stops appearing as held by anyone and
becomes visibly `Under Repair`.

**Why this priority**: Servicing was previously untracked. Without a reliable
opening operation there is no vendor, date, or accountability history at all,
and an Asset physically at a vendor still appears to be in someone's hands.

**Independent Test**: As a User with `asset_custody_manage`, open a Service
Record for an eligible Asset and a managed Vendor, then verify the `Open`
record, the cleared Custodian, and the `Under Repair` status.

**Acceptance Scenarios**:

1. **AS-001 — Accepted intent, test-backed**: **Given** an eligible Asset and a
   managed Vendor, **When** an authorized custody operator opens a Service
   Record, **Then** an `Open` Service Record exists for that Asset and Vendor,
   the Asset's Custodian is cleared, and the Asset status is `Under Repair`.
2. **AS-002 — Accepted intent (ADR-0001; Draft B2 ALR-003)**: **Given** the
   same opening, **When** it completes, **Then** the record creation, Custodian
   clearing, and status change commit as one operation with no user-visible
   partial state.
3. **AS-003 — Accepted intent (`CONTEXT.md`, Vendor; ADR-0001)**: **Given** a
   Service Record is opened, **When** its Vendor is recorded, **Then** it refers
   to one managed Vendor identity shared with Procurement, and free-typed
   supplier text is rejected.
4. **AS-004 — Accepted intent, test-backed**: **Given** an Asset that is already
   `Under Repair`, **When** an opening is attempted, **Then** it is rejected and
   neither the Asset nor any Service Record changes.
5. **AS-005 — Accepted intent, test-backed**: **Given** an Asset that is `Sold`,
   `Scrapped`, or `Lost`, **When** an opening is attempted, **Then** it is
   rejected and no Service Record is created.
6. **AS-006 — Accepted authorization, test-backed**: **Given** a User whose Role
   does not grant `asset_custody_manage`, **When** that User attempts to open a
   Service Record, **Then** access is denied and no Asset or Service Record data
   changes.
7. **AS-007 — Draft B2 dependency**: **Given** an Asset that is `Available`
   or `Assigned`, **When** a Service Record is opened, **Then** the operation is
   permitted; entry to `Under Repair` by a direct Asset status edit is rejected.
8. **AS-008 — Draft B6 dependency**: **Given** an Asset with no current
   Procurement, or a Vendor flagged as an unresolved legacy value, **When** an
   opening is attempted, **Then** it is rejected and no Service Record is
   created.
9. **AS-035 — Stakeholder-confirmed**: **Given** an Asset that is `In Storage`,
   **When** an opening is attempted, **Then** it is rejected and the Asset
   remains `In Storage`; the Asset must first be returned to `Available` through
   an Draft B2 administrative transition.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-001 — Implementation-only conformance gap (FR-008)**: **Given** the
   current opening operation, **When** eligibility is evaluated, **Then** every
   status except `Under Repair`, `Sold`, `Scrapped`, and `Lost` is accepted,
   which includes `In Storage`. The current create surface's
   `Available`/`Assigned` filter conforms; the backend does not.
2. **OBS-AS-002 — Implementation-only conformance gap (FR-005)**: **Given** an
   Asset with a department, **When** a Service Record is opened, **Then** the
   Custodian is cleared but the department is retained.
3. **OBS-AS-003 — Implementation-only**: **Given** the current create surface,
   **When** an operator chooses an Asset, **Then** only `Available` and
   `Assigned` Assets are offered, and only the Asset, Vendor, expected return
   date, and reason can be submitted; the interface accepts opening remarks that
   the surface never sends.

---

### User Story 2 — Close a Service Record and Return the Asset to Availability (Priority: P1)

A custody operator records that the Asset has come back from the Vendor. The
Service Record closes with its return date, cost, and outcome, and the Asset
becomes `Available` again — deliberately without being handed back to whoever
held it before.

**Why this priority**: Closure is the decision point ADR-0001 exists to protect.
Automatically returning the Asset to its previous holder would skip the check IT
must make, and leaving the record open would strand the Asset in `Under Repair`.

**Independent Test**: Close an `Open` Service Record with a cost and outcome,
then verify the `Closed` record, the recorded return date, the `Available`
Asset, and the absent Custodian.

**Acceptance Scenarios**:

1. **AS-009 — Accepted intent, test-backed**: **Given** an `Open` Service
   Record, **When** an authorized custody operator closes it, **Then** the
   record becomes `Closed` with a return date and the Asset becomes `Available`.
2. **AS-010 — Accepted intent (`CONTEXT.md`; ADR-0001), test-backed**:
   **Given** the same closure, **When** it completes, **Then** the Asset has no
   Custodian, the previous Custodian is not restored, and no Checkout is created
   by the closure.
3. **AS-011 — Accepted intent (ADR-0001)**: **Given** a closed Service Record,
   **When** the Asset is to be handed back to a User, **Then** a fresh Checkout
   is performed as a separate, deliberate operation owned by B3.
4. **AS-012 — Accepted intent, test-backed**: **Given** an already `Closed`
   Service Record, **When** another closure is attempted, **Then** it is
   rejected and neither the record nor the Asset changes.
5. **AS-013 — Accepted authorization**: **Given** a User whose Role does not
   grant `asset_custody_manage`, **When** that User attempts a closure, **Then**
   access is denied and no record or Asset data changes.
6. **AS-014 — Accepted intent (Draft B2 ALR-003)**: **Given** a valid
   closure, **When** it completes, **Then** the record state, return date, cost,
   outcome, and Asset status change commit as one operation.
7. **AS-015 — Accepted intent (Draft B2 ALR-005)**: **Given** an Asset that
   is `Under Repair`, **When** anyone attempts to move it out of that status by
   a direct Asset edit rather than by closing its Service Record, **Then** the
   attempt is rejected and the Asset and record remain unchanged.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-004 — Implementation-only**: **Given** any closure, **When** it
   completes, **Then** the Asset status is set to `Available` without first
   verifying that the Asset is still `Under Repair`. The `Available` result
   itself conforms to FR-008.
2. **OBS-AS-005 — Implementation-only conformance gap (FR-005)**: **Given**
   closure, **When** it completes, **Then** the Asset department is left at
   whatever value it carried through servicing.
3. **OBS-AS-006 — Implementation-only**: **Given** closure, **When** it
   completes, **Then** the Asset `condition` is unchanged and no
   condition-inspection history row is created, so a repair that changed the
   Asset's condition leaves no condition evidence.
4. **OBS-AS-007 — Implementation-only**: **Given** a closure whose
   already-closed check runs before the write transaction begins, **When** two
   closures are attempted simultaneously, **Then** the single-closure guarantee
   is not provably enforced.

---

### User Story 3 — Preserve Custody and Lifecycle Integrity While Servicing (Priority: P1)

When an Asset that someone is holding goes to a Vendor, that person's usage
session ends as part of the same operation, and no competing custody operation
can act on the Asset while it is away.

**Why this priority**: A dangling open Checkout makes an Asset look held by a
User who no longer has it, and a late Transfer approval could hand a
physically-absent Asset to someone new.

**Independent Test**: Open a Service Record on a checked-out Asset and confirm
the Checkout is closed before the Asset becomes `Under Repair`; then attempt a
Transfer request and approval against that Asset and confirm both are rejected.

**Acceptance Scenarios**:

1. **AS-016 — Accepted intent (ADR-0001; Draft B3 FR-015), test-backed**:
   **Given** an Asset with an open Checkout, **When** a Service Record opens,
   **Then** that Checkout is closed with a return date as part of the same
   operation, and the Custodian is cleared before the Asset becomes
   `Under Repair`.
2. **AS-017 — Accepted intent (Draft B3 FR-017 and FR-028)**: **Given** a
   Checkout closed by an opening Service Record, **When** it is later read,
   **Then** it is distinguishable from a Checkout closed by an ordinary
   check-in, remains in the Asset's custody history, and is never reopened by
   closing the Service Record.
3. **AS-018 — Accepted B4 boundary, test-backed**: **Given** an Asset that is
   `Under Repair`, **When** a Transfer is requested or a previously Pending
   Transfer is approved, **Then** the Transfer action is rejected and custody
   does not change.
4. **AS-019 — Draft B2 dependency, test-backed**: **Given** an Asset with an
   open Service Record, **When** an accepted terminal transition completes,
   **Then** every open Service Record for that Asset is closed atomically with
   that transition.
5. **AS-020 — Draft B2 dependency (FR-014), test-backed**: **Given** an Asset
   that is `Under Repair`, **When** it is reactively recorded as `Lost`,
   **Then** the transition is accepted and its open Service Record closes with
   it. `Sold` and `Scrapped` are not accepted directly from `Under Repair`.
6. **AS-021 — Accepted intent (Draft B2 ALR-002)**: **Given** any rejected
   opening, closure, or authorization check, **When** the rejection occurs,
   **Then** the Asset, its Custodian, its condition, its open Checkout, and
   every Service Record remain unchanged.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-008 — Implementation-only conformance gap (Draft B3 FR-028)**:
   **Given** an interrupted Checkout closure, **When** it runs, **Then** the
   record is marked `Returned` with an explanatory remark appended and the
   Asset's current condition copied as its return condition, but it carries no
   explicit closed-as-interrupted marker and the Checkout User receives no
   Checkout-ended Notification of its own.
2. **OBS-AS-009 — Implementation-only**: **Given** an interrupting closure,
   **When** it runs, **Then** it closes every open Checkout on the Asset rather
   than exactly one, although nothing in the data model prevents more than one.
3. **OBS-AS-010 — Implementation-only**: **Given** a terminal transition that
   closes an open Service Record, **When** it runs, **Then** the record receives
   a return date and an appended note but records no closing operator and no
   cost, deliberately distinguishing it from an operator-confirmed closure.
4. **OBS-AS-011 — Implementation-only**: **Given** the eligibility check and the
   record creation inside the opening operation, **When** two openings are
   attempted simultaneously, **Then** the row lock relied upon has no effect on
   the current database engine, so double-opening is not provably prevented.

---

### User Story 4 — Record the Vendor, Dates, Cost, and Outcome of the Repair (Priority: P2)

The Service Record carries enough information to answer what was wrong, who
repaired it, when it left and came back, what it cost, and how it ended.

**Why this priority**: This content is the reason the concept exists —
`CONTEXT.md` defines a Service Record by exactly these attributes, and
Vendor-grouped reporting depends on them.

**Independent Test**: Open a Service Record with a reason and expected return
date, close it with a cost and outcome, and verify every attribute is retained
and readable on the record and in the Asset's service history.

**Acceptance Scenarios**:

1. **AS-022 — Accepted intent (`CONTEXT.md`, Service Record)**: **Given** a
   Service Record, **When** it is read, **Then** it identifies exactly one
   Asset, one managed Vendor, the date the Asset was sent, and — once closed —
   the date it was returned.
2. **AS-023 — Accepted intent (`CONTEXT.md`, Service Record)**: **Given** a
   closed Service Record, **When** it is read, **Then** it records the cost/bill
   of the work and the outcome of the repair.
3. **AS-024 — Accepted intent (`CONTEXT.md`, Service Record)**: **Given** a
   Service Record, **When** it is compared with the Asset's condition and
   condition history, **Then** it remains a distinct event record and MUST NOT
   be presented as a condition label or a condition-history row.
4. **AS-025 — Accepted intent (Draft B2 FR-012)**: **Given** a Service
   Record, **When** any change to its state or lifecycle effect is attempted,
   **Then** it happens only through opening, closing, or an Draft B2 terminal
   transition, never through a direct record edit or deletion.
5. **AS-036 — Stakeholder-confirmed**: **Given** an operator recording a repair
   that happened earlier, **When** the sent or return date is supplied, **Then**
   the entered date is retained; **Given** a date in the future, or a return
   date before the sent date, **When** it is submitted, **Then** it is rejected
   and neither the record nor the Asset changes.
6. **FWD-AS-001 — Prospective Change scenario, not B5 baseline acceptance**: **Given** an expected return date before
   the sent date, **When** it is submitted, **Then** it is rejected. **Given**
   an `Open` Service Record whose expected return date has passed, **When** it
   is read, **Then** it is identifiable as overdue and every active
   `asset_custody_manage` holder has been proactively notified; **Given** the
   same record after closure, **When** it is read, **Then** it is no longer
   overdue.
7. **FWD-AS-002 — Prospective Change scenario, not B5 baseline acceptance**: **Given** an overdue Service Record,
   **When** a closure or any other operation is attempted, **Then** overdue does
   not by itself block it, and overdue never appears as an Asset status or as a
   Service Record state alongside `Open` and `Closed`.
8. **AS-039 — Stakeholder-confirmed**: **Given** a closure, **When** no cost or
   a negative cost is supplied, **Then** the closure is rejected and neither the
   record nor the Asset changes; **Given** a cost of zero, **When** it is
   supplied, **Then** the closure succeeds and the record shows the work carried
   no charge.
9. **AS-040 — Stakeholder-confirmed**: **Given** a closure whose cost is greater
   than zero, **When** a bill reference or the bill/service document is missing,
   **Then** the closure is rejected; **Given** both are supplied, **Then** the
   closure succeeds and the document is readable from the record. **Given** a
   closure whose cost is zero, **When** neither is supplied, **Then** the
   closure still succeeds.
10. **AS-041 — Stakeholder-confirmed**: **Given** a closure, **When** the
    outcome is missing or is not one of `Repaired`, `Replaced`,
    `Not Repairable`, or `No Fault Found`, **Then** the closure is rejected;
    **Given** a canonical outcome, **Then** it is recorded and can be filtered
    on without reading free text.
11. **AS-042 — Stakeholder-confirmed**: **Given** a Service Record opened with a
    reason and remarks, **When** it is closed with closing remarks, **Then** the
    opening reason and opening remarks remain readable alongside the closing
    remarks and neither is overwritten.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-012 — Implementation-only conformance gap (FR-011, FR-028, FR-029,
   FR-030)**: **Given** the current record, **When** its content is inspected,
   **Then** it holds Vendor, sent date, optional expected return date, returned
   date, optional reason, optional cost, one free-text remarks value, opening
   operator, closing operator, and `Open`/`Closed` state — and no bill
   reference, no attached bill or service document, and no outcome value.
2. **OBS-AS-013 — Implementation-only conformance gap (FR-026)**: **Given** the
   sent and returned dates, **When** they are recorded, **Then** both are set
   automatically to the moment the operation runs and neither can be entered or
   corrected, so an Asset that left the building last week cannot be recorded
   with its real send date.
3. **OBS-AS-014 — Implementation-only gap motivating CHG-B5-01**: **Given** an
   expected return date, **When** it is supplied, **Then** it is accepted even
   when it is before the sent date, and produces no overdue state, alert, or
   escalation anywhere.
4. **OBS-AS-015 — Implementation-only conformance gap (FR-011)**: **Given** a
   closure, **When** a cost is supplied, **Then** it is taken directly from the
   submitted request without the validation applied to other record fields, no
   sign rule exists, and omitting it stores an empty cost rather than rejecting
   the closure.
5. **OBS-AS-016 — Implementation-only conformance gap (FR-030)**: **Given**
   remarks recorded when the record was opened, **When** a closure supplies
   remarks, **Then** the opening remarks are replaced rather than retained
   alongside the closing remarks; supplying none preserves the opening text.
6. **OBS-AS-017 — Implementation-only**: **Given** the current surfaces,
   **When** a Service Record is created or closed, **Then** the create surface
   collects Asset, Vendor, expected return date, and reason, and the close
   dialog collects cost and remarks only.

---

### User Story 5 — Receive Service Accountability Effects (Priority: P2)

The User whose custody just ended is told their Asset went to a Vendor, and
operators can later explain who sent which Asset where, when, and at what cost.

**Why this priority**: Opening a Service Record silently strips a User's
custody. That must be visible to the affected person and reconstructable
afterwards.

**Independent Test**: Exercise each row of the B5 Notification and Audit Trigger
Matrix and verify the selected recipients, a destination that resolves to the
Asset, exactly one audit entry per required event, minimized values, and the B8
failure boundary.

**Acceptance Scenarios**:

1. **AS-026 — Stakeholder-confirmed and test-backed**: **Given** an Asset held
   by a Custodian, **When** a Service Record opens, **Then** that previous
   Custodian receives an in-app Notification naming the Asset and the Vendor,
   with a destination that resolves to the Asset detail surface.
2. **AS-043 — Stakeholder-confirmed**: **Given** a Service Record is closed,
   **When** the trigger executes, **Then** every active `asset_custody_manage`
   holder receives one in-app Notification that the Asset is back and can be
   checked out again, with a destination that resolves to the Asset detail
   surface.
3. **AS-044 — Stakeholder-confirmed**: **Given** an Asset with an open Checkout,
   **When** a Service Record opens, **Then** the B3 interrupted-closure
   Notification to the Checkout User and the B5 opening Notification remain
   separate messages, and B5 neither merges nor suppresses the B3 trigger.
4. **AS-045 — Stakeholder-confirmed**: **Given** a successful opening, a
   successful closing, a terminal transition that auto-closes a Service Record,
   or a rejected or permission-denied attempt, **When** the event completes,
   **Then** exactly one minimized AuditLog entry records it with the content
   required by FR-023, including the reason for a rejected attempt.
2. **AS-027 — Draft B8 dependency (B8 FR-008)**: **Given** any accepted B5
   Notification, **When** it is delivered, **Then** it is in-app only in this
   version and addressed to a specific User; email is deferred and MUST NOT be
   inferred from editable SMTP Settings.
3. **AS-028 — Draft B8 dependency (B8 FR-018)**: **Given** the B5 trigger matrix,
   **When** B8 processes it, **Then** B8 delivers exactly the accepted triggers
   and neither adds nor suppresses a Service Record business trigger.
4. **AS-029 — Draft B8 dependency (B8 FR-011)**: **Given** a required B5 AuditLog
   write fails, **When** the owning opening or closure attempts to commit,
   **Then** the business action also fails and no partial Service Record or
   Asset mutation is visible.
5. **AS-030 — Draft B8 dependency (B8 FR-012)**: **Given** a Notification delivery
   fails after a valid opening or closure, **When** failure handling runs,
   **Then** the Service Record work remains committed, the failure is
   operator-visible, and retry cannot create a duplicate recipient record.
6. **AS-031 — Draft B8 dependency (B8 FR-015)**: **Given** any B5 AuditLog entry,
   **When** it is written, **Then** it contains only the values needed to
   explain the event and no authentication secret, credential, or unnecessary
   personal data.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-018 — Implementation-only, conforming**: **Given** an Asset with no
   Custodian, **When** a Service Record opens, **Then** no Notification is
   produced, which matches the accepted matrix because no recipient exists.
2. **OBS-AS-019 — Implementation-only conformance gap (FR-021)**: **Given** any
   closure, **When** it completes, **Then** no Notification is produced for
   anyone, so no custody operator is told the Asset is back and available.
3. **OBS-AS-020 — Implementation-only conformance gap**: **Given** the opening
   Notification, **When** its destination is followed, **Then** it points at
   `/asset/{id}` while the frontend Asset detail route is `/asset/detail/{id}`,
   so the destination does not resolve.
4. **OBS-AS-021 — Implementation-only conformance gap (FR-023)**: **Given** a
   successful opening or closure, **When** it completes, **Then** exactly one
   AuditLog entry is written for module `Service Records` containing only a
   summary line naming the Asset and Vendor, with no old value, no status
   effect, no Custodian effect, and no cost or outcome. The single-entry count
   conforms; the content does not.
5. **OBS-AS-022 — Implementation-only conformance gap (FR-023)**: **Given** a
   rejected opening, a permission-denied attempt, a rejected closure, or a
   terminal transition that auto-closes a Service Record, **When** it occurs,
   **Then** no B5 AuditLog entry is written for it.
6. **OBS-AS-023 — Implementation-only**: **Given** a previous Custodian with no
   linked profile record, **When** the opening Notification is attempted,
   **Then** the shared helper silently does nothing and the opening still
   succeeds; under Draft B8 FR-012 that is a failed delivery, not an accepted
   outcome.

---

### User Story 6 — Read Service Records and Asset Service History (Priority: P3)

An authorized reader can see which Assets are currently at a Vendor and can read
one Asset's complete service history alongside its other lifecycle history.

**Why this priority**: Reading is how the recorded history becomes useful, but
it delivers no lifecycle guarantee of its own and depends on B1's visibility
rules.

**Independent Test**: As Users with different Roles, list Service Records, filter
by state, and open an Asset's service history; verify the records returned match
the reader's B1 visibility scope.

**Acceptance Scenarios**:

1. **AS-032 — Draft B1 dependency**: **Given** a User with `asset_view`,
   **When** Service Records are requested, **Then** the records returned follow
   B1 data visibility: authorized non-Employee Roles receive global records,
   while Employee receives only lifecycle records that directly involve that
   Employee.
2. **AS-033 — Draft B2 dependency**: **Given** an Asset readable by the
   requesting User, **When** its aggregate history is opened, **Then** its
   Service Records appear alongside its Checkout, Transfer, condition, and AMC
   history without any of them being conflated.
3. **AS-034 — Accepted intent**: **Given** any Service Record surface, **When**
   it is presented, **Then** `Open` and `Closed` are shown as Service Record
   states and are never presented as Asset statuses, and `Under Repair` is never
   presented as a condition.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-024 — Implementation-only**: **Given** any authenticated User with
   `asset_view`, **When** the Service Record list is requested, **Then** all
   records are returned globally, newest sent date first, with an exact `status`
   query filter available.
2. **OBS-AS-025 — Implementation-only**: **Given** the current list surface,
   **When** it renders, **Then** it shows Asset, Vendor, sent date, expected
   return, returned-on, reason, cost, and state; the send-for-service and close
   controls appear only for `asset_custody_manage` holders and the close control
   only on `Open` rows.
3. **OBS-AS-026 — Implementation-only conformance gap (ALR-005)**: **Given** an
   Admin or platform superuser, **When** a Service Record is edited or deleted
   directly, **Then** the change is permitted and can desynchronize the record
   from its Asset's status.

### Edge Cases

- An `In Storage` Asset MUST be returned to `Available` before it can be sent
  for service (FR-008), so servicing can never silently change an Asset's
  storage state. The current backend accepts `In Storage` directly and returns
  the Asset as `Available` on closure; that path is a conformance gap.
- Because closure always returns `Available`, an Asset that should go back into
  storage after a repair needs a separate administrative transition owned by
  B2 — the same kind of deliberate second step ADR-0001 requires for restoring
  custody.
- Department follows custody (FR-005), so an Asset at a Vendor has no
  department and a closed Service Record leaves it empty until a fresh Checkout
  sets it. The current opening and closure both retain it, so an Asset
  physically at a Vendor can present a department belonging to a User who no
  longer holds it — a conformance gap at both points.
- Cost attribution for a repair therefore cannot be read from the Asset's live
  department, because that department is empty for exactly as long as the Asset
  is at the Vendor. Any Vendor or departmental cost reporting must derive it
  from the custody history rather than the current record; report definitions
  are owned by B9.
- A zero cost is a meaningful business value, not a missing one: it records
  warranty work, goodwill, or a no-fault return. It MUST NOT be conflated with
  an absent cost, which rejects the closure under FR-011.
- The bill requirement is conditional on cost, so a `No Fault Found` return at
  zero cost closes with no document while a paid repair cannot. An operator who
  has the bill but not yet the file cannot close the record; that is the
  intended trade, since a paid repair with no evidence is what FR-028 exists to
  prevent.
- The canonical outcomes are a repair result, not an Asset condition and not an
  Asset status. `Not Repairable` MUST NOT by itself move the Asset to a terminal
  status; recording the Asset as `Scrapped` or `Sold` afterwards remains a
  separate B2-owned decision.
- `Replaced` describes the repair of the serviced Asset, not the creation of a
  different Asset. A physical swap that produces a new Asset record is Asset
  creation owned by B2, and this baseline records no link between the two.
- A repair that changes an Asset's physical condition produces no condition
  change and no condition-history row, so the Service Record and the condition
  history can disagree about the same event.
- Opening a Service Record on a checked-out Asset deliberately produces two
  Notifications to the same User for the same event: the B3 interrupted-closure
  message that their custody ended and the B5 message that the Asset went to a
  Vendor. FR-021 keeps them separate so neither baseline suppresses the other's
  trigger; a User seeing two related messages is the accepted trade.
- An Asset can be recorded as `Lost` while `Under Repair` — the accepted
  reactive path when a Vendor loses it — which closes the Service Record with no
  closing operator, no cost, and no outcome.
- `Sold` and `Scrapped` are not accepted from `Under Repair` under Draft B2
  FR-014, yet the current direct-edit path accepts them and auto-closes the open
  Service Record. That transition guard is owned by B2.
- The sent and return dates are operator-supplied under FR-026, so a Service
  Record can represent a repair recorded the following day. The current
  automatic-only stamping cannot, and is a conformance gap.
- A correctable sent date means the sent date and the moment the record was
  created can differ. Only the sent date carries business meaning; the creation
  moment is not a substitute for it and MUST NOT be displayed as one.
- The current system has no derived overdue condition or proactive overdue
  delivery. The desired behavior is non-baseline scope owned by
  `specs/010-service-record-overdue-alerts-change/`.
- An expected return date is optional, so a repair with no vendor commitment
  date simply never becomes overdue. Overdue is a signal about dates that were
  promised, not a completeness check on the record.
- Deleting an Asset deletes its entire service history, and deleting a User
  leaves the opening and closing operator identity empty on historical records.
  Asset and User deletion are owned by B2 and B1; the service-history
  consequence is recorded here.
- A Vendor referenced by any Service Record cannot be deleted. Only the
  Procurement reference path for this protection is covered by a test; the
  Service Record path is implementation-only.
- Employee visibility of Service Records is ambiguous under B1's
  "directly involving" rule, because opening a Service Record deliberately
  removes the only User the Asset was attached to. A Service Record identifies
  operators, not a subject User.
- Nothing prevents an authorized operator from opening a Service Record for an
  Asset that is not physically at a Vendor; opening is a record of an operator's
  assertion, not a verified physical fact.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 — Accepted intent**: A Service Record MUST represent exactly one
  repair or maintenance event for exactly one Asset and MUST identify the
  Vendor performing the work.
  *(Source: `CONTEXT.md`, **Service Record**.)*
- **FR-002 — Accepted intent**: A Service Record MUST refer to a managed Vendor
  identity shared with Procurement. Free-typed supplier text MUST NOT be
  accepted in place of it.
  *(Sources: `CONTEXT.md`, **Vendor**; `docs/adr/0001-service-record-lifecycle.md`.)*
- **FR-003 — Accepted intent**: Opening a Service Record MUST move its Asset to
  `Under Repair`.
  *(Sources: `CONTEXT.md`, **Service Record**; ADR-0001; Draft B2 FR-007;
  current behavior is test-backed.)*
- **FR-004 — Accepted intent**: Opening a Service Record MUST clear the Asset's
  Custodian, mirroring check-in, so that one Asset has one clear state at a
  time.
  *(Sources: `CONTEXT.md`, **Custodian** and **Service Record**; ADR-0001;
  Draft B2 FR-006; current behavior is test-backed.)*
- **FR-005 — Stakeholder-confirmed, Draft B2 dependency**: Asset department
  MUST mean the current holder's organizational unit. Opening a Service Record
  MUST therefore clear the department together with the Custodian, an Asset at a
  Vendor MUST have no department, and closing MUST restore neither. Returning an
  Asset to a department MUST happen only through the fresh Checkout that
  restores custody.
  *(Sources: stakeholder clarification, 2026-08-05, confirming Draft B2
  FR-006, FR-007, and FR-015 with no amendment required; Draft B3 FR-023 applies
  the same rule to check-in. The current retention at both points is a
  conformance gap.)*
- **FR-006 — Accepted intent**: `Under Repair` MUST be entered only by opening a
  Service Record and left for `Available` only by closing one. A direct Asset
  status edit MUST NOT substitute for either operation, and a rejected attempt
  MUST leave the Asset and the Service Record unchanged.
  *(Sources: `CONTEXT.md`, **Service Record**; ADR-0001; Draft B2 FR-012 and
  ALR-005; current rejection is test-backed.)*
- **FR-007 — Accepted intent**: Opening a Service Record MUST be rejected when
  the Asset is already `Under Repair` or is `Sold`, `Scrapped`, or `Lost`, and
  the Asset MUST remain unchanged.
  *(Sources: `CONTEXT.md`, terminal statuses; Draft B2 FR-008 and ALR-005;
  current rejection is test-backed.)*
- **FR-008 — Stakeholder-confirmed**: Only an `Available` or `Assigned` Asset
  MUST be eligible to be sent for service. `In Storage` MUST be rejected; an
  Asset held in storage MUST first be returned to `Available` through an
  Draft B2 administrative transition before it can be sent to a Vendor.
  Closing MUST always return the Asset to `Available`, and no pre-service status
  MUST be captured or restored.
  *(Sources: stakeholder clarification, 2026-08-05; `CONTEXT.md`, **Service
  Record**; ADR-0001. The current backend's acceptance of `In Storage` is a
  conformance gap.)*
- **FR-009 — Draft B6 dependency**: An Asset with no current Procurement MUST
  NOT enter Service Record activity, and a Vendor flagged as an unresolved
  legacy value MUST NOT be selectable for a new Service Record.
  *(Source: Draft B6 FR-014 and FR-022.)*
- **FR-010 — Accepted intent**: Closing a Service Record MUST mark it closed,
  record the date the Asset was returned, and move the Asset to `Available`.
  *(Sources: `CONTEXT.md`, **Service Record**; ADR-0001; Draft B2 FR-007;
  current behavior is test-backed.)*
- **FR-011 — Stakeholder-confirmed**: A cost MUST be supplied to close a Service
  Record. Zero MUST be permitted and MUST mean the work carried no charge, such
  as warranty, goodwill, or no fault found. A negative cost and a missing cost
  MUST be rejected without changing the record or the Asset.
  *(Sources: `CONTEXT.md`, **Service Record**; stakeholder clarification,
  2026-08-05. The current optional, unvalidated cost is a conformance gap.)*
- **FR-012 — Accepted intent**: Closing a Service Record MUST NOT restore the
  previous Custodian, MUST NOT create a Checkout, and MUST NOT reopen a Checkout
  that was closed when the record opened. Returning the Asset to a holder MUST
  require a fresh Checkout performed as a separate deliberate operation.
  *(Sources: `CONTEXT.md`, **Service Record**; ADR-0001; Draft B2 FR-007;
  current behavior is test-backed.)*
- **FR-013 — Accepted intent**: A closed Service Record MUST NOT be reopened,
  and a second closure MUST be rejected without changing the record or the
  Asset.
  *(Sources: `CONTEXT.md`, **Service Record**; current rejection is
  test-backed.)*
- **FR-014 — Accepted intent (Draft B3 FR-015)**: Opening a Service Record on an
  Asset with an open Checkout MUST close that Checkout as part of the same
  operation, before the Asset becomes `Under Repair`.
  *(Sources: `CONTEXT.md`, **Service Record**; ADR-0001; Draft B3 FR-015;
  current behavior is test-backed.)*
- **FR-015 — Accepted intent (Draft B3 FR-017 and FR-028)**: A Checkout closed
  by an opening Service Record MUST remain distinguishable from one closed by an
  ordinary check-in, MUST remain visible in the Asset's custody history, and
  MUST NOT be treated as a check-in for the purposes of B3's return-condition
  and return-remark rules.
  *(Sources: ADR-0001; Draft B3 FR-017 and FR-028; Draft B2 ALR-006.)*
- **FR-016 — Draft B2 dependency**: An accepted terminal transition on an
  Asset with an open Service Record MUST close that record atomically with the
  transition. `Lost` is the accepted terminal outcome reachable directly from
  `Under Repair`.
  *(Sources: Draft B2 FR-014 and ALR-006; current closure behavior and the
  `Under Repair → Lost` path are test-backed.)*
- **FR-017 — Accepted intent**: A Service Record MUST remain distinct from the
  Asset's `condition` and from its condition history, and MUST NOT be presented
  or reported as either.
  *(Source: `CONTEXT.md`, **Service Record**.)*
- **FR-018 — Accepted intent**: A Service Record MUST identify its Asset, its
  Vendor, the operator who opened it, the date it was sent, and its `Open` or
  `Closed` state; a closed record MUST additionally identify the operator who
  closed it and the date it was returned.
  *(Sources: `CONTEXT.md`, **Service Record**; observable acceptance cases
  AS-001, AS-009, and AS-022.)*
- **FR-019 — Accepted intent**: A Service Record's state and lifecycle effects
  MUST be changed only by opening, closing, or an Draft B2 terminal
  transition. Direct record update or deletion MUST NOT be an accepted path.
  *(Sources: `.specify/memory/constitution.md`, Principle II; Draft B2
  FR-012. The current Admin-only fallback is implementation-only.)*
- **FR-020 — Accepted intent (C3)**: Every user-visible Service Record surface,
  label, and message MUST use `Service Record`, `Under Repair`, `Vendor`, and
  `Checkout`, and MUST NOT describe restoring custody after service as an
  assignment or as automatic.
  *(Sources: `CONTEXT.md`, **Checkout** and **Service Record**; `ROADMAP.md`
  decision C3; Draft B2 FR-004.)*
- **FR-021 — Stakeholder-confirmed, Draft B8 ownership dependency**: B5 owns the
  accepted trigger matrix below and B8 MUST NOT add, remove, or reinterpret a
  B5 trigger. Opening a Service Record MUST request an in-app Notification for
  the previous Custodian, and closing one MUST request an in-app Notification
  for every active `asset_custody_manage` holder so the returned Asset can be
  checked out again. Prospective overdue alerts are excluded from B5 and owned
  by `specs/010-service-record-overdue-alerts-change/`. An Asset with no Custodian at
  opening produces no opening Notification because no recipient exists. The B3
  interrupted-Checkout Notification MUST remain a separate message addressed to
  the Checkout User; B5 MUST NOT merge or suppress it. B8 MUST own only shared
  in-app delivery, read state, retry, access, and retention.
  *(Sources: stakeholder clarification, 2026-08-05; Draft B8 FR-002, FR-005, and
  FR-018; Draft B3 FR-020 for the separate interrupted-closure trigger. The
  opening Notification is test-backed; the absent closing and overdue
  Notifications are conformance gaps.)*
- **FR-022 — Draft B8 delivery dependency**: Every accepted B5 Notification MUST
  be in-app only in this version, MUST address a specific User, and MUST carry a
  destination that resolves to the referenced Asset's detail surface. Email is
  deferred and MUST NOT be inferred from editable SMTP Settings.
  *(Sources: Draft B8 FR-008 and FR-012. The current unresolvable destination is
  a conformance gap.)*
- **FR-023 — Stakeholder-confirmed, Draft B8 audit dependency**: Exactly one
  minimized AuditLog entry MUST be created for every successful opening, every
  successful closing, every terminal transition that auto-closes a Service
  Record, and every rejected or permission-denied opening or closing attempt.
  Each entry MUST identify the operator or attempting actor, the event time, the
  Asset, the Vendor, the resulting or attempted Service Record state, and the
  Asset status and custody effects; a closing entry MUST additionally identify
  the cost and outcome, and a rejected attempt MUST additionally identify the
  reason. Routine Service Record reads MUST NOT create an entry. Shared AuditLog
  storage, access, filtering, privacy, and retention remain owned by B8.
  *(Sources: stakeholder clarification, 2026-08-05; Draft B8 FR-011, FR-014,
  FR-015, and FR-018. The current summary-only entries and the absent
  rejection and auto-closure entries are conformance gaps.)*
- **FR-024 — Evidence integrity**: Every Service Record behavior in this Draft
  that is observed only in implementation MUST remain labelled
  implementation-only until backed by a test or an explicit stakeholder
  decision, and MUST NOT be promoted into an accepted requirement by this
  specification run.
  *(Source: `.specify/memory/constitution.md`, Principle III.)*
- **FR-025 — Decision gate**: U-001 through U-004 were resolved by the
  stakeholder clarification dated 2026-08-05 and MUST NOT be reopened by
  observing current implementation behavior. The conformance gaps in U-005 are
  review findings, not grounds for weakening the requirement each one
  contradicts. This Draft has no remaining acceptance blocker of its own; it
  MUST NOT be accepted while its Draft B1, B2, B3, B6, and B8 dependencies remain
  unaccepted in the parts this baseline relies on.
  *(Sources: stakeholder clarification, 2026-08-05; `ROADMAP.md` B5 review
  status; `.specify/memory/constitution.md`, Principles I and III.)*
- **FR-026 — Stakeholder-confirmed**: The date an Asset was sent to the Vendor
  and the date it was returned MUST both be supplied by the operator, MUST
  default to the current date and time, and MUST be correctable so a repair
  recorded after the fact carries its real dates. Neither MUST be in the future,
  and the return date MUST NOT precede the sent date. A violation MUST be
  rejected without changing the record or the Asset.
  *(Source: stakeholder clarification, 2026-08-05. The current automatic-only
  stamping is a conformance gap.)*
### Prospective Change Extracted — Not a B5 Baseline Requirement

- **FWD-B5-001**: Expected-return validation, derived overdue visibility, and
  proactive custody-operator alerts are desired behavior absent from the
  current system. Their normative authority is
  `specs/010-service-record-overdue-alerts-change/spec.md`; they MUST NOT be used
  as evidence that B5 currently implements or accepts that delivery behavior.

### Functional Requirements *(continued)*
- **FR-028 — Stakeholder-confirmed**: When the closing cost is greater than
  zero, a bill reference and an attached bill or service document MUST be
  supplied, and a closure missing either MUST be rejected. When the cost is
  zero, both MUST be optional.
  *(Sources: `CONTEXT.md`, **Service Record**, "cost/bill"; stakeholder
  clarification, 2026-08-05. The current record has neither, which is a
  conformance gap.)*
- **FR-029 — Stakeholder-confirmed**: Closing a Service Record MUST record an
  outcome selected from `Repaired`, `Replaced`, `Not Repairable`, and
  `No Fault Found`. A missing or noncanonical outcome MUST be rejected without
  changing the record or the Asset, and the outcome MUST be readable and
  filterable rather than implied by free text.
  *(Sources: `CONTEXT.md`, **Service Record**, "outcome"; stakeholder
  clarification, 2026-08-05. The current absence of any outcome value is a
  conformance gap.)*
- **FR-030 — Stakeholder-confirmed**: A Service Record MUST retain the remarks
  captured when it was opened and the remarks captured when it was closed as
  distinct values. Closing MUST NOT overwrite or discard the opening text. Both
  are optional, and the reason recorded at opening MUST also survive closure.
  *(Sources: `CONTEXT.md`, **Service Record**; stakeholder clarification,
  2026-08-05. The current single remarks value that a closure replaces is a
  conformance gap.)*
- **FR-031 — Accepted intent (correction of a closed record)**: A mistaken cost,
  outcome, bill reference, or date on a closed Service Record MUST be
  correctable only through a named correction operation requiring
  `asset_custody_manage`, never through a direct record edit. A correction MUST
  retain the superseded value, the correcting actor, and the correction time, and
  MUST NOT reopen the record or alter the Asset.
  *(Derived, not newly decided. FR-026 already requires the sent and return dates
  to be "correctable" while FR-019 forbids direct record editing — a tension this
  requirement resolves in the direction FR-019 already sets, by making correction
  a named lifecycle operation rather than an exception to it. The permission
  follows ALR-001, which makes `asset_custody_manage` authoritative for both
  owning operations.)*

  **Implementation conformance gap**: no correction operation exists; the dates
  cannot be entered or corrected at all (U-005 row 11), and the only current path
  that could change a closed record is the Admin-only direct edit FR-019
  prohibits.
- **FR-032 — Accepted intent (bill document authorization)**: Attaching or
  replacing the bill or service document MUST require `asset_custody_manage`, the
  same permission that closes the record it evidences. Reading it MUST follow the
  Service Record read visibility in ALR-002, not the Asset document permissions,
  because the document evidences the repair rather than the Asset. A replaced
  document MUST retain its superseded version.
  *(Derived, not newly decided. FR-028 already requires the document whenever cost
  exceeds zero, and ALR-001 already makes `asset_custody_manage` authoritative for
  closing; this states the authorization that requirement presupposes rather than
  inheriting it implicitly from B2's Asset-document rules.)*
- **FR-033 — Accepted intent (single open record)**: An Asset MUST have at most
  one `Open` Service Record. A second opening attempt MUST be rejected without
  creating a record or changing the Asset, and the invariant MUST hold under
  simultaneous attempts.
  *(Derived, not newly decided. §Assumptions already records this property, but
  only as an emergent consequence of the `Under Repair` status precondition — so
  any future change to that precondition would silently remove it. FR-007 and
  ALR-004 already require the rejection and the atomicity; this states the
  invariant directly so it survives on its own.)*

  **Implementation conformance gap**: the guarantee rests on a row lock the
  current database engine does not enforce, so simultaneous openings are not
  provably prevented (CAND/OBS evidence recorded in §Edge Cases).
- **FR-034 — Accepted intent (Vendor on a Service Record)**: The Vendor is fixed
  when the Service Record opens. Changing it on an `Open` record MUST NOT be an
  accepted operation; forwarding an Asset to a different repairer MUST be
  recorded by closing the current Service Record and opening a new one, so each
  Vendor's involvement remains a distinct event. Protection of a Vendor
  referenced by a Service Record from deletion is owned by B6 as Vendor
  administration; B5 requires only that the reference remain valid for the life
  of the record.
  *(Derived, not newly decided. `CONTEXT.md` defines a Service Record as one
  repair event, FR-001 carries that, and FR-019 forbids direct record editing —
  together these already exclude an in-place Vendor swap. The deletion-protection
  assignment follows the B6 ownership boundary already stated in §Out of Scope;
  §Edge Cases records that only the Procurement reference path is test-backed.)*

### Current-System Contract Candidates — Not Accepted Requirements

These record current behavior only. They are evidence for stakeholder review and
MUST NOT be read as accepted requirements.

- **CAND-001**: Opening accepts any Asset status except `Under Repair`, `Sold`,
  `Scrapped`, and `Lost`, which includes `In Storage`, while the create surface
  offers only `Available` and `Assigned` Assets. FR-008 is authoritative; the
  backend acceptance of `In Storage` is a conformance gap.
- **CAND-002**: Opening retains the Asset department; closing leaves it
  unchanged.
- **CAND-003**: Closing sets the Asset to `Available` unconditionally, without
  re-checking that the Asset is still `Under Repair`. The `Available` result
  conforms to FR-008; the missing precondition check does not.
- **CAND-004**: The sent date and the returned date are both stamped
  automatically at the moment the operation runs and cannot be entered or
  corrected. FR-026 is authoritative.
- **CAND-005**: The expected return date is an optional date, is accepted when
  before the sent date, and drives no overdue state, alert, escalation, or
  report. CHG-B5-01 owns the desired validation and overdue delivery behavior.
- **CAND-006**: The cost is optional, is accepted only at closure, is taken
  directly from the submitted request without the validation applied to other
  record fields, and carries no sign rule. FR-011 is authoritative.
- **CAND-007**: The record holds an optional reason and a single free-text
  remarks value; a closure that supplies remarks replaces the opening text, and
  one that omits them preserves it. FR-030 is authoritative.
- **CAND-008**: The record holds no bill reference, no attached bill or service
  document, and no outcome value. FR-028 and FR-029 are authoritative.
- **CAND-009**: Closing does not change the Asset's `condition` and creates no
  condition-inspection history row.
- **CAND-010**: Opening notifies only the previous Custodian, with a message
  naming the Asset and Vendor and a destination of `/asset/{id}`; an Asset with
  no Custodian produces no Notification, and closing produces none for anyone.
  FR-021 and FR-022 are authoritative.
- **CAND-011**: Successful opening and closing each write one AuditLog entry to
  module `Service Records` containing a single summary line, with no old value,
  status effect, Custodian effect, cost, or outcome. FR-023 is authoritative.
- **CAND-012**: Rejected openings, permission-denied attempts, rejected
  closures, and terminal transitions that auto-close a Service Record write no
  B5 AuditLog entry. FR-023 is authoritative.
- **CAND-013**: A terminal transition closes every open Service Record for the
  Asset with a return date and an appended note, deliberately recording no
  closing operator and no cost.
- **CAND-014**: Reads require `asset_view` and return all records globally,
  newest sent date first, with an exact state filter; open and close require
  `asset_custody_manage`; every other action falls through to Admin-only.
- **CAND-015**: An Admin or platform superuser can update or delete a Service
  Record directly.
- **CAND-016**: A Vendor referenced by a Service Record cannot be deleted;
  deleting an Asset deletes its Service Records.
- **CAND-017**: The eligibility check and the already-closed check rely on
  guards that the current database engine does not enforce, so simultaneous
  openings or closures are not provably prevented.

### Authorization and Lifecycle Requirements

- **ALR-001 — Accepted authorization**: Opening and closing a Service Record
  MUST require `asset_custody_manage`. Admin, IT Manager, and IT Staff hold that
  code in the accepted named-Role matrix; a custom Role granted the code is
  authorized under B1 with no implicit bypass.
  *(Sources: Draft B2 permission contract; `CONTEXT.md`, **Checkout**, for
  the IT-performed custody actor; the denial is test-backed.)*
- **ALR-002 — Accepted visibility dependency**: Reading Service Records MUST
  require `asset_view` and MUST follow B1 data visibility. The Employee scope
  for a record whose subject User has deliberately been cleared MUST be stated
  by B1 rather than inferred from the current global queryset.
- **ALR-003 — Governance requirement**: Every protected B5 action MUST be
  authorized at the backend action boundary. Hiding or showing a frontend
  control MUST NOT be the authorization decision.
  *(Source: `.specify/memory/constitution.md`, Principle II.)*
- **ALR-004 — Accepted atomicity**: An opening MUST commit the Service Record
  creation, the interrupted-Checkout closure, the Custodian and department
  clearing, the `Under Repair` status, and its required audit entry as one
  operation. A closure MUST commit the closed state, return date, cost, outcome,
  `Available` status, and its required audit entry as one operation.
  *(Sources: Draft B2 ALR-003; Draft B8 FR-011.)*
- **ALR-005 — Accepted lifecycle ownership**: Opening and closing MUST be the
  only operations that move an Asset into and out of `Under Repair`, and the
  only operations that change a Service Record's state, except an Draft B2
  terminal transition. Direct record editing or deletion MUST NOT be an accepted
  path.
  *(Sources: Draft B2 FR-012 and ALR-005; ADR-0001.)*
- **ALR-006 — Accepted rejection safety**: A denied or rejected opening or
  closure MUST leave the Asset status, Custodian, department, condition, open
  Checkout, and every Service Record unchanged.
  *(Source: Draft B2 ALR-002.)*
- **ALR-007 — Accepted integration boundary**: Opening a Service Record owns the
  closure of the Checkout it interrupts, and an accepted terminal transition
  owns the closure of the Service Record it interrupts. Neither interrupting
  operation MUST leave a dangling open record, and neither MUST be presented as
  the normal closure of the record it interrupted.
  *(Sources: ADR-0001; Draft B2 ALR-006; Draft B3 FR-015 and FR-028.)*
- **ALR-008 — Draft B8 failure boundary**: Failure of a required AuditLog write
  MUST reject and roll back the owning opening or closure. Notification failure
  MUST NOT roll back completed Service Record work and MUST remain visible and
  retryable without duplicate recipient records.
  *(Source: Draft B8 FR-011 and FR-012.)*
- **ALR-009 — Current permission mapping**: List and retrieve currently use
  `asset_view`; create and close use `asset_custody_manage`; every other action
  currently falls through to Admin-only. The read, open, and close mappings are
  accepted through B1 and B2; the Admin fallback for direct mutation is
  implementation-only and conflicts with ALR-005.

### Accepted Service Record Actor and Permission Contract

| Service Record action | Permission code | Accepted named-Role behavior | Evidence status |
| --- | --- | --- | --- |
| List, retrieve, and read Asset service history | `asset_view` plus B1 visibility | Admin, IT Manager, IT Staff, HR, and Viewer global; Employee scope owned by B1 | Draft B2 read contract; Employee scope is not implemented in the current global queryset |
| Open a Service Record | `asset_custody_manage` | Admin, IT Manager, and IT Staff | Draft B2 permission contract; the denial is test-backed and the permitted round trip is test-backed |
| Close a Service Record | `asset_custody_manage` | Admin, IT Manager, and IT Staff | Draft B2 permission contract; the permitted round trip is test-backed |
| Perform the fresh Checkout after service | `asset_custody_manage` | Admin, IT Manager, and IT Staff | Owned by B3; B5 requires only that it is separate and deliberate |
| Open or close through a custom Role granted the code | Assigned relevant code | Allowed with no implicit bypass | Draft B1 intent |
| Directly update or delete a Service Record | Not accepted | None | Current Admin fallback is implementation-only and conflicts with ALR-005 |
| Administer Vendors | Owned by B6 | Not a B5 action | Out of scope |

### Accepted B5 Notification and Audit Trigger Matrix

This matrix is the input B5 owes B8 under Draft B8 FR-018. Every row is
stakeholder-confirmed as of 2026-08-05; the evidence column records how far
current behavior meets it.

| B5 event | Notification recipient and meaning | Destination | Required audit entry | Current evidence |
| --- | --- | --- | --- | --- |
| Service Record opened | Previous Custodian; custody ended because the Asset went to a Vendor | Asset detail surface | Actor, time, Asset, Vendor, `Open` state, `Under Repair` status effect, and the cleared Custodian and department | Notification test-backed; destination and audit content are conformance gaps |
| Service Record opened for an Asset with no Custodian | None; no recipient exists | Not applicable | Same as the row above with no custody effect to record | Current silence conforms; audit content is a conformance gap |
| Service Record closed | Every active `asset_custody_manage` holder; the Asset is back and can be checked out again | Asset detail surface | Actor, time, Asset, Vendor, `Closed` state, return date, cost, outcome, and the `Available` status effect | No current Notification exists; both are conformance gaps |
| Prospective overdue alert | Owned by CHG-B5-01, not the B5 baseline | Owned by CHG-B5-01 | Owned by CHG-B5-01 and B8 | No current overdue concept exists; evidence motivating the Change specification |
| Interrupted Checkout closed by an opening | Owned by Draft B3 FR-020 and FR-028; addressed to the Checkout User and kept separate from the B5 opening Notification | Asset detail surface | Owned by Draft B3 FR-027 | Draft B3 dependency; B5 MUST NOT merge or suppress it |
| Terminal transition auto-closes an open Service Record | Draft B2 emits no workflow Notification | Not applicable | Actor, time, Asset, Vendor, forced `Closed` state, and the fact that no operator confirmed the repair; may be carried by the Draft B2 terminal-transition entry that already identifies every Service Record it closed | No B5 entry currently exists; conformance gap |
| Permission-denied, ineligible-Asset, or already-closed rejection | None | Not applicable | Actor, time, attempted action, target identifiers when safe, and the rejection reason | No current entry exists; conformance gap |
| Service Record list, detail, or history read | None | Not applicable | None; routine business read | Current behavior conforms |

Audit values MUST comply with Draft B8 FR-015 minimization: no password, token,
authentication secret, or personal data beyond what the event requires. Source
IP, when captured, follows B8's six-month value-retention rule and the entry
follows B8's two-year retention rule.

### Key Entities

- **Service Record**: One repair event relating one Asset to one managed Vendor,
  with an operator-supplied sent date, an optional expected return date, a
  return date, a reason, opening and closing remarks held separately, a
  mandatory closing cost, a conditional bill reference and bill/service
  document, a canonical outcome, opening and closing operators, and an `Open` or
  `Closed` state.
- **Asset**: The authoritative lifecycle record. Opening sets `Under Repair` and
  clears custody; closing sets `Available` and restores nothing. Its status,
  condition, custody, and history rules are owned by Draft B2.
- **Vendor**: The shared managed third-party identity. B5 selects one; B6 owns
  its creation, naming, merging, archiving, and protected deletion.
- **Custodian**: The User holding the Asset before servicing. After opening,
  the Asset has none; after closing, it still has none.
- **Checkout**: The usage session B5 interrupts on opening and the separate
  deliberate operation required to hand the Asset back after closing. Owned by
  B3.
- **Notification**: The shared in-app recipient record owned by B8. B5 owns its
  own business events, recipients, meaning, and destinations.
- **AuditLog Entry**: The shared operational record owned by B8. B5 supplies the
  required Service Record triggers and any additional minimum content.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 9 selected B5 tests pass in one run — 7 Service Record
  lifecycle tests and 2 Service Record endpoint tests — together with the 7
  adjacent boundary tests owned by B2 and B4.
- **SC-002**: For 100% of valid openings, one `Open` Service Record exists, the
  Asset is `Under Repair`, the Custodian is absent, and zero partial states are
  observable at any point.
- **SC-003**: For 100% of valid closures, the record is closed with a return
  date, the Asset is `Available`, and the previous Custodian is restored in 0%
  of cases; 0% of closures create a Checkout.
- **SC-004**: 100% of openings attempted against an Asset that is `Under Repair`
  or terminal are rejected, and 0% of them change the Asset or create a record.
- **SC-005**: 100% of openings on an Asset with an open Checkout close exactly
  that Checkout before the Asset becomes `Under Repair`, and 0% leave a dangling
  open Checkout.
- **SC-006**: 100% of accepted terminal transitions on an Asset with an open
  Service Record close that record atomically, and 0% leave an Asset in a
  terminal status with an open Service Record.
- **SC-007**: Every protected B5 action maps to exactly one permission code and
  one B1 visibility rule; unauthorized attempts return zero out-of-scope records
  and perform zero mutation.
- **SC-008**: 100% of closed Service Records make the Vendor, sent date, return
  date, cost/bill, and outcome readable without consulting application code, and
  0% of Service Records are presented as a condition or a condition-history row.
- **SC-009**: Every row of the accepted B5 trigger matrix identifies one event,
  one recipient rule, one message meaning, one resolvable destination, and one
  audit rule; B8 adds or suppresses 0% of B5 business triggers.
- **SC-010**: Required audit failure rolls back 100% of owning openings and
  closures; Notification failure rolls back 0% of otherwise completed work; and
  0% of B5 audit entries contain authentication secrets or unnecessary personal
  data.
- **SC-011**: All four mandated decisions U-001 through U-004 have explicit
  stakeholder answers, and 0% of their former implementation-only alternatives
  remain presented as accepted behavior.
- **SC-012**: 100% of accepted, test-backed, implementation-only, and unresolved
  claims in this baseline cite `CONTEXT.md`, ADR-0001, an accepted or Draft
  dependency identifier, an explicit stakeholder decision, or a repository
  evidence path.
- **SC-013**: 100% of future-dated sent or return dates and return dates
  preceding their sent date are rejected without mutation. Expected-return
  validation and overdue outcomes are measured by CHG-B5-01, not this baseline.
- **SC-014**: 100% of closures missing a cost, carrying a negative cost, missing
  a canonical outcome, or carrying a cost above zero without a bill reference
  and bill/service document are rejected without mutation; 100% of successful
  closures leave the opening reason and opening remarks readable.

## Assumptions

- Draft B2 is a current dependency and remains subject to its own acceptance
  review; this Draft does not independently redefine it. B1, B2, B3, B6, and B8
  remain Draft dependencies, and B5 acceptance depends on their own acceptance.
- The IT-performed custody actor described for Checkout in `CONTEXT.md` applies
  equally to sending an Asset for service; employees do not send their own
  Assets to a Vendor in current scope.
- "Sent" and "returned" describe the Asset's physical movement to and from the
  Vendor rather than the moment the record was typed. The stakeholder
  clarification dated 2026-08-05 makes both operator-supplied under FR-026.
- "Outcome" in `CONTEXT.md` means how the repair ended. The stakeholder
  clarification dated 2026-08-05 makes it a canonical value under FR-029; the
  four accepted values are assumed sufficient to classify every repair the
  organization currently sends to a Vendor.
- Cost is recorded in the organization's single operating currency. Currency,
  tax breakdown, and multi-line billing are assumed out of scope for a Service
  Record; the bill document carries that detail.
- A Service Record is a record of an operator's assertion that an Asset went to
  a Vendor. No physical verification exists, and periodic physical Asset audits
  remain deferred under `ROADMAP.md` F1.
- One Asset has at most one `Open` Service Record, because opening requires the
  Asset not to be `Under Repair` and opening sets it. This is an emergent
  property of the accepted status rule rather than a separately stated
  constraint.
- Vendor-grouped operational reporting is the reason Vendor is first-class; the
  reports themselves are owned by B9.
- No application code, test code, database, route, interface, or configuration
  was modified as part of specifying this baseline.

## Baseline Evidence and Unresolved Conflicts *(Brownfield Baseline only)*

### Accepted Intent

- A Service Record is one repair/maintenance event for an Asset with Vendor,
  dates sent/returned, cost/bill, and outcome: `CONTEXT.md`, **Service Record**.
- Opening clears the Custodian and moves the Asset to `Under Repair`, mirroring
  check-in and keeping one Asset in one clear state at a time: `CONTEXT.md`,
  **Service Record** and **Custodian**; `docs/adr/0001-service-record-lifecycle.md`.
- Closing returns the Asset to `Available` and never auto-restores the previous
  Custodian; IT must perform a fresh Checkout. Retaining custody through
  servicing and auto-restoring it on close were both explicitly considered and
  rejected: `docs/adr/0001-service-record-lifecycle.md`.
- A Service Record is distinct from `condition` and from the condition history:
  `CONTEXT.md`, **Service Record**.
- Vendor is a first-class managed entity shared with Procurement, chosen over
  free text so Vendor-grouped reporting is reliable: `CONTEXT.md`, **Vendor**;
  `docs/adr/0001-service-record-lifecycle.md`.
- Opening clears the Asset department with the Custodian, closing restores
  neither, `Under Repair` is entered and left only through this lifecycle,
  transitions are atomic, and a terminal transition closes open Service Records:
  Draft B2 FR-006, FR-007, FR-012, FR-015, ALR-003, ALR-005, ALR-006, and
  ALR-007.
- `Lost` may be recorded from `Under Repair`; `Sold` and `Scrapped` are accepted
  only from `Available` or `In Storage`: Draft B2 FR-014.
- Service Record open and close use `asset_custody_manage`, held by Admin, IT
  Manager, and IT Staff: Draft B2 permission contract.
- Opening a Service Record closes the Checkout it interrupts, marks it
  closed-as-interrupted, and keeps it distinguishable from a check-in: Draft B3
  FR-015, FR-017, and FR-028; ADR-0001.
- An Asset without current Procurement cannot enter Service Record activity, and
  a flagged legacy Vendor cannot be selected: Draft B6 FR-014 and FR-022.
- B5 owns its Notification and audit trigger matrix; B8 owns shared in-app
  delivery, failure behavior, privacy, access, and retention: Draft B8 FR-002,
  FR-008, FR-011, FR-012, FR-015, and FR-018.

### Verified Behavior Evidence

The 9 tests below were run together on 2026-08-05 in the repository-local
backend environment and all passed.

- **AS-001**: opening creates an `Open` record for the Vendor, clears the
  Custodian, and sets `Under Repair`:
  `backend/assets/tests.py::ServiceRecordLifecycleTests::test_open_service_clears_custodian_and_marks_under_repair`.
- **AS-026**: opening notifies the previous Custodian:
  `ServiceRecordLifecycleTests::test_open_service_notifies_the_previous_custodian`.
- **AS-016**: opening closes the open Checkout it interrupts, with a return
  date, before the Asset becomes `Under Repair`:
  `ServiceRecordLifecycleTests::test_open_service_closes_the_open_checkout_it_interrupts`.
- **AS-004**: opening is rejected for an Asset already `Under Repair`:
  `ServiceRecordLifecycleTests::test_open_service_rejects_an_asset_already_under_repair`.
- **AS-005**: opening is rejected for a terminal Asset:
  `ServiceRecordLifecycleTests::test_open_service_rejects_a_terminal_asset`.
- **AS-009, AS-010, AS-023**: closing records the cost and return date, marks the
  record `Closed`, and returns the Asset to `Available` without reassigning the
  Custodian:
  `ServiceRecordLifecycleTests::test_close_service_returns_asset_to_available_without_reassigning_custodian`.
- **AS-012**: closing an already closed record is rejected:
  `ServiceRecordLifecycleTests::test_close_service_rejects_an_already_closed_record`.
- **AS-006**: opening without `asset_custody_manage` returns `403`:
  `ServiceRecordEndpointTests::test_service_create_requires_asset_custody_manage_permission`.
- **AS-001, AS-009**: the permitted open-and-close endpoint round trip returns
  the created record and a `Closed` result:
  `ServiceRecordEndpointTests::test_service_open_and_close_round_trip`.

The 7 adjacent boundary tests below are owned by B2 and B4. They were run
together on 2026-08-05 and all passed; they are cited here only as the
current-system evidence for B5's lifecycle boundary.

- **AS-007, AS-015**: `Under Repair` cannot be entered or left by a direct Asset
  edit, and cannot be reached directly from `Assigned`:
  `AssetStatusTransitionTests::test_cannot_enter_under_repair_by_direct_edit`;
  `AssetStatusTransitionTests::test_cannot_leave_under_repair_by_direct_edit`;
  `AssetStatusTransitionTests::test_cannot_move_directly_between_assigned_and_under_repair`.
- **AS-019, AS-020**: entering a terminal status closes the open Service Record,
  and `Lost` remains permitted directly from `Under Repair`:
  `AssetStatusTransitionTests::test_entering_terminal_status_closes_the_open_service_record`;
  `AssetStatusTransitionTests::test_lost_is_still_allowed_directly_from_under_repair`.
- **AS-018**: a Transfer request is rejected for an `Under Repair` Asset, and an
  approval is rejected for an Asset sent for service after the request:
  `TransferLifecycleTests::test_request_transfer_rejects_an_asset_under_repair`;
  `TransferLifecycleTests::test_approve_rejects_an_asset_sent_for_service_after_the_request`.

### Implementation-Only Observations

- Opening and closing orchestration, the ineligible-status list, Custodian
  clearing, interrupted-Checkout closure, the previous-Custodian Notification,
  and the helper that closes open Service Records for an interrupting operation:
  `backend/assets/service.py`.
- The interrupted-Checkout closure helper, its appended note, and its reuse of
  the Asset's current condition as the return condition:
  `backend/assets/checkout.py`.
- Service Record persistence fields, automatic sent/returned date stamping,
  optional expected return date, optional cost and remarks, protected Vendor
  reference, and cascading deletion with the Asset: `backend/assets/models.py`.
- Read-only serializer fields, so cost, state, dates, and operators cannot be
  submitted directly, and the absence of any bill, document, outcome, or
  condition field on the record: `backend/assets/serializers.py`.
- The terminal-transition path that closes open Service Records during a direct
  Asset status edit: `backend/assets/serializers.py`.
- Action permission map with the Admin fallback, global queryset, newest-first
  ordering, exact state filter, raw closure cost handling, and the two
  `Service Records` AuditLog calls: `backend/assets/views.py`.
- Shared notification and audit helpers, including the silent no-op when a
  recipient has no linked profile: `backend/core/services.py`.
- The permission engine's superuser and named-Admin bypass:
  `backend/core/permissions.py`.
- The create surface's `Available`/`Assigned` filter, its Asset, Vendor,
  expected return date, and reason fields, and its confirmation wording:
  `frontend/src/pages/service/Create.jsx`.
- The list surface's columns, `asset_custody_manage`-gated send and close
  controls, close dialog collecting cost and remarks, and its
  check-it-back-out-separately wording: `frontend/src/pages/service/Services.jsx`.
- Route protection using `asset_view` for the list and `asset_custody_manage`
  for creation, and the Service Records menu entry: `frontend/src/App.jsx`;
  `frontend/src/components/navbar/Menu.jsx`.
- The Asset detail Service History panel showing Vendor, state, sent and
  returned dates, and reason: `frontend/src/pages/asset/Detail.jsx`.
- Dashboard open-service counts and the current-service and Vendor-service
  reports, all owned by B9: `backend/reporting/views.py`.

### Unresolved Conflicts

- **U-001 — `In Storage` eligibility and closure status — RESOLVED 2026-08-05**:
  the stakeholder limited eligibility to `Available` and `Assigned`. An
  `In Storage` Asset must first be returned to `Available` through an accepted
  B2 administrative transition, closure always returns `Available`, and no
  pre-service status is captured or restored. `CONTEXT.md` needs no amendment.
  Recorded in FR-008 and AS-035; the current backend's acceptance of
  `In Storage` (`backend/assets/service.py`) is now a conformance gap in U-005.
  The current create surface's `Available`/`Assigned` filter conforms.
- **U-002 — Department meaning while servicing — RESOLVED 2026-08-05**: the
  stakeholder confirmed that department follows custody. It is the current
  holder's organizational unit, so an Asset at a Vendor has none, and only the
  fresh Checkout after service restores one. This confirms Draft B2 FR-006,
  FR-007, and FR-015 and matches the check-in rule in Draft B3 FR-023, so no B2
  amendment is required. Recorded in FR-005; the current retention at both
  opening and closure (`backend/assets/service.py`) remains a conformance gap in
  U-005.
- **U-003 — Bill and document expectations — RESOLVED 2026-08-05**: the
  stakeholder made cost mandatory at closure with zero permitted and meaning
  no-charge, required a bill reference and an attached bill or service document
  whenever the cost is above zero, made outcome a canonical value from
  `Repaired`, `Replaced`, `Not Repairable`, and `No Fault Found`, and required
  opening and closing remarks to be retained separately. Recorded in FR-011,
  FR-028, FR-029, and FR-030; the currently optional cost, absent bill
  reference, absent document, absent outcome, and overwritten opening remarks
  are now conformance gaps in U-005. Where the bill/service document is stored
  relative to the existing Asset document types is a planning detail, not an
  open requirement.
- **U-004 — Mandatory audit events and Notification recipients — RESOLVED
  2026-08-05**: the stakeholder required audit entries for successful openings,
  successful closings, terminal auto-closures, and every rejected or
  permission-denied attempt, with defined content including the rejection
  reason; required closing to notify every active `asset_custody_manage` holder
  while opening continues to notify the previous Custodian; and required the B3
  interrupted-Checkout Notification to stay a separate message. Draft B8's
  failure boundary applies unchanged. Recorded in FR-021, FR-023, ALR-008, and
  the accepted trigger matrix; the currently missing entries and Notifications
  (`backend/assets/views.py`; `backend/core/services.py`) are now conformance
  gaps in U-005.
- **U-005 — Conformance gaps recorded, not accepted**: the current behaviors
  below contradict accepted requirements in this Draft. Each is recorded as a
  gap rather than reconciled by weakening a requirement. Whether a gap is
  corrected, deferred, or formally excepted is a review decision, not a
  specification decision.

| # | Current behavior | Accepted requirement | Current-state record |
| --- | --- | --- | --- |
| 1 | Opening retains the Asset department | FR-005 | CAND-002 |
| 2 | Closing leaves the retained department in place | FR-005 | CAND-002 |
| 3 | A closure that supplies remarks replaces the text captured at opening | FR-030 | CAND-007 |
| 4 | An interrupted Checkout carries no explicit closed-as-interrupted marker | FR-015 | OBS-AS-008 |
| 5 | The opening Notification destination does not resolve to the Asset detail route | FR-022 | CAND-010 |
| 6 | An Admin or superuser may edit or delete a Service Record directly | FR-019, ALR-005 | CAND-015 |
| 7 | `Sold` and `Scrapped` are accepted directly from `Under Repair` by the current direct-edit path | Draft B2 FR-014 (B2-owned gap) | CAND-003 |
| 8 | Required audit entries are absent for rejections, denials, and terminal auto-closures | FR-023 | CAND-012 |
| 9 | The backend accepts an `In Storage` Asset for service | FR-008 | CAND-001 |
| 10 | Closing does not re-check that the Asset is still `Under Repair` | FR-010, ALR-005 | CAND-003 |
| 11 | Sent and return dates cannot be entered or corrected | FR-026 | CAND-004 |
| 12 | The expected return date is unvalidated and no overdue state or notification exists | CHG-B5-01; non-baseline delivery gap | CAND-005 |
| 13 | Cost is optional and unvalidated at closure | FR-011 | CAND-006 |
| 14 | No bill reference and no attached bill or service document exist | FR-028 | CAND-008 |
| 15 | No outcome value exists; outcome is inferable only from free text | FR-029 | CAND-008 |
| 16 | Closing produces no Notification for custody operators | FR-021 | CAND-010 |
| 17 | Successful opening and closing audit entries carry only a summary line | FR-023 | CAND-011 |

### Implementation Conformance Update

**Date**: 2026-08-12. **Commits**: `538c3a8`, `070c8c2`. Status of the U-005
rows against the current implementation. No requirement changes; the table above
is preserved as the dated review record.

| # | Status | Evidence |
| --- | --- | --- |
| 13 — cost at closure | **Closed** | Closing without a cost is rejected, `0` is accepted as an explicit no-charge answer, and non-numeric or negative values are rejected (`backend/assets/service.py`). The close dialog marks the field required and states the zero convention (`frontend/src/pages/service/Services.jsx`). Tests: `ServiceClosureContractTests::test_closing_without_a_cost_is_rejected`, `::test_zero_cost_means_no_charge_and_is_accepted`, `::test_a_negative_cost_is_rejected`. |
| 16 — closing Notification | **Closed** | Closing notifies every active `asset_custody_manage` holder that the Asset has returned and is `Available` (`backend/assets/service.py`, via `core.services.notify_many`). Test: `::test_closing_notifies_every_custody_operator`. |

Rows 1–12, 14, 15, and 17 remain open and unchanged. Worth singling out because
they are easy to assume were carried along with the cost fix: closure remarks
still replace the text captured at opening (row 3), the backend still accepts an
`In Storage` Asset for service (row 9), closing still does not re-check that the
Asset is `Under Repair` (row 10), and no bill reference, attached document, or
outcome value exists (rows 14–15). Row 12 is CHG-B5-01 delivery scope rather
than a baseline conformance gap.

Also newly enforced and relevant to this baseline's neighbours: Service Record
lists are scoped to Assets the reader currently holds under B1's C6 decision
(`backend/assets/views.py`). Because opening a Service Record clears custody, an
Employee does not see a repair while it is in flight — a direct consequence of
FR-005 rather than a separate access rule, and worth confirming at acceptance.

**Provenance note**: these changes were written implementation-first and covered
by tests afterwards, not through the red-green loop Principle IV requires.

### Remaining Evidence-Led Confirmation Items

These are not acceptance blockers and do not reopen U-001 through U-004. They
are review items to confirm at baseline acceptance:

- Whether a repair that changes an Asset's condition should create a condition
  inspection row, given that `CONTEXT.md` calls a condition change evidence of a
  Service Record (CAND-009). A `Repaired` or `Replaced` outcome makes this more
  likely to matter than it was before FR-029.
- How B1's Employee visibility rule applies to a Service Record whose subject
  User has deliberately been cleared (ALR-002).
- Whether the overdue notification in CHG-B5-01 can be delivered reliably in
  production, which depends on the scheduling question `ROADMAP.md` C5 leaves
  open for the existing expiry alerts.

## Out of Scope *(mandatory)*

### Adjacent Baseline Ownership

- Authentication, Users, Roles, permission-code administration, the User
  directory, and Department and Location masters: B1. B5 consumes the resulting
  User, Role, and visibility values.
- Asset identity, register, search, status and condition sets, direct
  administrative edits, terminal-transition implementation, files, barcode,
  condition history, and aggregate Asset history: B2. B5 changes Asset status
  and custody only by opening and closing a Service Record.
- Checkout and check-in, including the fresh Checkout required after service,
  the interrupted-Checkout record's own content and Notification, expected
  return dates, and the Overdue Checkout state: B3. B5 records only the two
  integration boundaries in FR-014 and FR-015.
- Approval-gated Transfer, including requester and approver permissions,
  outcomes, and Transfer documents: B4. B5 records only that an `Under Repair`
  Asset is incompatible with Transfer.
- Vendor administration — creation, naming and normalization, contact details,
  merging, archiving, protected deletion, and legacy backfill — and all
  Procurement recording, linking, invoices, purchase orders, and arrival rules:
  B6. B5 only selects an existing managed Vendor.
- Warranty dates, AMC contracts, AMC renewal and End Support, and 30/15/7-day
  expiry alerts: B7. A Service Record is not evidence of a Warranty or AMC
  claim, and B5 records no relationship to either.
- Shared Notification storage, read state, unread counts, polling, delivery
  reliability, AuditLog storage, administrative access, filters, privacy, and
  retention: B8. B5 owns only its trigger matrix.
- Dashboard open-service counts, the current-service and Vendor-service reports,
  report columns, and PDF/Excel/CSV exports: B9.

### Explicitly Unresolved Rather Than Accepted

- The three items under Remaining Evidence-Led Confirmation Items. All four
  mandated B5 decisions were resolved on 2026-08-05, so no requirement-level
  decision remains open in this baseline.

### Explicitly Deferred or Excluded

- Any automatic Checkout, custody restoration, or reservation after service.
  ADR-0001 rejects it, and this baseline requires a separate deliberate
  Checkout.
- Employee self-service service requests or employee-initiated repair tickets;
  no such request stage exists in current scope.
- Vendor performance, SLA, warranty-claim, or repair-approval workflows.
- Scheduled or periodic physical Asset audits (`ROADMAP.md`, F1) and any
  treatment of AuditLog as physical verification.
- Email delivery of Service Record Notifications; the current version is in-app
  only and SMTP-labelled Settings do not imply an email implementation.
- Application-code, test-code, database, route, interface, or configuration
  changes in this documentation-only specification run.
