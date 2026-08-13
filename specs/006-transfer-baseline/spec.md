# Feature Specification: AS-BUILT Approval-Gated Transfer Baseline

**Feature Branch**: `docs/baseline-spec-migration`

**Created**: 2026-08-04

**Status**: Draft

**Input**: User description: "Create an AS-BUILT Brownfield Baseline
specification for ROADMAP.md entry B4: Approval-gated Transfer. Cover request
and approval actors, transfer_request and asset_custody_manage permissions,
captured previous custody, target User and department,
Pending/Approved/Rejected outcomes, condition effects, terminal/Service
restrictions, notifications, audit effects, and Transfer PDF. Keep C1 and C8,
same-User Transfer, concurrent pending requests, custody changes before
approval, and condition validation unresolved. Do not treat Store-to-User
issuance as accepted Transfer behavior until C1 is resolved. Do not modify
application code."

## Clarifications

### Session 2026-08-04

- Q: Is Store-to-User issuance a Checkout or Transfer? → A: Checkout; Store-to-User issuance has no approval gate.
- Q: Which actors may download a Transfer PDF? → A: Any User with `asset_view`, limited to Transfer records visible under B1.
- Q: What integrity policy applies to same-User targets, concurrent Pending requests, and custody drift before approval? → A: Reject same-User targets, permit only one Pending Transfer per Asset, and reject approval when live Custodian or department differs from the request snapshot.
- Q: When and how must Transfer condition be validated? → A: Approval requires one of `New`, `Good`, `Average`, `Damaged`, or `Repair Required` and applies it to the Asset.
- Q: Which requester/approver Role policy and notification/audit effects apply? → A: B1 permission codes remain authoritative, including Admin and custom Roles; a requester holding both codes may decide their own request; notify approvers on request, both Custodians on approval, and requester on rejection; audit required mutations and security-relevant rejections but not PDF downloads.

## Specification Lineage *(mandatory)*

**Type**: Brownfield Baseline

**Roadmap Reference**: `ROADMAP.md`, entry B4 - Approval-gated Transfer;
durable feature directory `specs/006-transfer-baseline/`.

**Extends**: None. This is the initial B4 baseline.

**Supersedes**: None.

**Reciprocal Links**: `ROADMAP.md` already reserves
`specs/006-transfer-baseline/` for B4. After this Draft is accepted, later
changes must use a new feature directory and record reciprocal `Extends`,
`Supersedes`, or `Superseded by` lineage rather than altering accepted
requirements here.

**Dependencies**: Draft B1 identity and access baseline; Draft B2 Asset
register and lifecycle baseline; Draft B3 Checkout/check-in baseline; Draft B8
Notifications and AuditLog baseline.

## Domain Alignment *(mandatory)*

**Canonical Terms**:

- **Transfer** is an approval-gated handoff of an Asset's custody from a current
  User and department to a different target User and that User's department.
  The previous and target User roles MUST NOT reference the same User.
- **Transfer requester** is the HR or IT Manager actor who requests the handoff
  on an employee's behalf. A User with an Admin bypass or a custom Role holding
  `transfer_request` is also authorized under the accepted B1 permission
  contract. The permission code, not Role name alone, is authoritative.
- **Transfer approver** is the IT Manager or IT Staff actor who approves or
  rejects a Pending Transfer. A User with an Admin bypass or a custom Role
  holding `asset_custody_manage` is also authorized under B1. A requester who
  also holds this code may approve or reject their own request.
- **Previous Custodian** and **previous department** are the custody values
  captured when the request is made. **Target User** is the intended new
  Custodian. Under Draft B2 semantics, the target department is derived from
  the target User rather than selected independently.
- **Pending**, **Approved**, and **Rejected** are Transfer outcomes. They are not
  Asset statuses. A Pending request leaves the Asset unchanged; approval
  reassigns custody; rejection leaves the Asset untouched.
- **Checkout** is the non-approval `Available -> Assigned` operation and MUST
  NOT be called Transfer. **Store-to-User issuance** is Checkout and has no
  approval gate; it is not Transfer behavior.
- **Service Record** owns the `Under Repair` lifecycle. **AuditLog** is an
  operational event record, not a physical Asset audit.

**Relevant Decisions**:

- `CONTEXT.md`, **Transfer**: Transfer always involves two Users, always has an
  approval gate, moves `Pending -> Approved` or `Pending -> Rejected`, and is
  requested by HR or IT Manager and approved by IT Manager or IT Staff.
- Accepted B1 FR-007 and FR-010 through FR-012: Transfer creation uses
  `transfer_request`; approval/rejection uses `asset_custody_manage`; named and
  custom Role grants and global-versus-Employee visibility follow B1.
- Draft B2 FR-006, FR-008, FR-012, FR-015, ALR-003, ALR-004, ALR-006, and
  ALR-007: approved Transfer owns entry to `Assigned`, sets Custodian, derives
  department from that Custodian, respects terminal states, and participates in
  atomic lifecycle processing.
- Draft B2's terminal-transition contract requires every Pending Transfer on
  an Asset to become Rejected atomically when the Asset validly enters a
  terminal state. The current Asset transition implementation does not yet do
  so; this is a B2 conformance gap that B4 must not redefine.
- Draft B8 FR-002, FR-008, FR-012 through FR-015, and FR-018: current-version
  Notifications are in-app only; Transfer owns its business triggers and
  recipients; required audit writes are atomic; notification failure is
  non-blocking and retryable; and successful mutations plus security-relevant
  rejections require minimized AuditLog entries.
- `docs/adr/0001-service-record-lifecycle.md` governs the adjacent Service
  Record boundary. It does not define Transfer behavior beyond making
  `Under Repair` an incompatible custody state.
- Stakeholder clarification dated 2026-08-04 resolves `ROADMAP.md` C1:
  Store-to-User issuance is Checkout with no approval gate. The same session
  resolves C8: PDF download requires `asset_view` and follows B1 Transfer-record
  visibility, and resolves the integrity, condition, actor-policy,
  Notification, and audit questions recorded under Resolution Status and
  Remaining Findings.

**Evidence Classification**:

- **Accepted intent** comes only from `CONTEXT.md`, an accepted dependency, an
  ADR, or an explicit stakeholder decision. A qualifier may name the subject it
  governs — *accepted authorization*, *accepted dependency*, *accepted lifecycle
  boundary*, *accepted visibility dependency*, *accepted atomic approval*,
  *accepted rejection safety*, *accepted terminality*. The qualifier narrows what
  the requirement is about; it never lowers the force.
- **Stakeholder-confirmed** is accepted intent whose authority is a dated
  clarification recorded in §Clarifications rather than `CONTEXT.md`, an ADR, or
  an accepted dependency. It carries the same requirement force.
- **Governance requirement** is required by `.specify/memory/constitution.md`
  rather than by a product decision. It applies to every capability and is not
  open to amendment during this baseline's review; FR-013 and FR-019 carry this
  authority through their cited sources.
- **Test-backed current behavior** is reproducible current-system evidence but
  is not product intent by itself.
- **Implementation-only observation** is visible in code or a frontend surface
  without a dedicated behavioral test and remains unaccepted. The compound
  *implementation-only conformance gap* marks current behavior that contradicts
  an accepted requirement in this Draft.
- **Unresolved** means this Draft deliberately does not choose a rule.

A label may combine a classification with supporting evidence — "Stakeholder-
confirmed and test-backed", "Accepted intent and test-backed core", "Accepted
lifecycle boundary with selected test coverage". The **first** term is the
authority; the second records that a test also demonstrates part of it. A test
never raises or lowers the classification, and "with selected test coverage"
signals partial coverage, not a weaker requirement. A **dependency** label names
the baseline that owns the rule B4 consumes; where that baseline is still
`Draft`, the dependency is not settled and citing it does not make it accepted.

**Lifecycle and Actors**:

| Stage | Actor and permission | Accepted or evidenced effect |
| --- | --- | --- |
| Read Transfer list or detail | `asset_view` | B1 grants global records to authorized non-Employee Roles and only directly involving lifecycle records to Employee; current endpoint listing is global for every caller with `asset_view` |
| Request handoff | HR or IT Manager in canonical intent; `transfer_request` at the authorization boundary | Create a Pending Transfer and capture the request-time custody without changing the Asset |
| Approve Pending request | IT Manager or IT Staff in canonical intent; `asset_custody_manage` at the authorization boundary | Atomically mark Approved and set Asset Custodian, department, `Assigned` status, and any accepted Transfer condition effect |
| Reject Pending request | Same approval authority | Mark Rejected and leave Asset state and custody untouched |
| Enter terminal Asset state while Pending | B2-owned terminal operator | Atomically reject every Pending Transfer; B2 requires no workflow Notification for this automatic rejection |
| Download Transfer PDF | `asset_view` plus B1 Transfer visibility | Every User may download only a Transfer record they are authorized to read; the current Admin-only endpoint is a conformance gap |

An IT Manager holds both request and approval permissions under B1. The current
endpoint test demonstrates one actor requesting and approving the same record;
stakeholder clarification dated 2026-08-04 confirms that no separate
segregation-of-duties rule applies. Any requester who also holds
`asset_custody_manage` may approve or reject their own request.

For each Asset, at most one Transfer may be Pending. Approval is valid only when
the Asset's live Custodian and department still equal the captured previous
Custodian and previous department. A second request, same-User target, or stale
approval attempt is rejected without mutation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Request a User-to-User Custody Handoff (Priority: P1)

An authorized requester records that an Assigned Asset should move from its
current Custodian to a target User. The request preserves the previous custody
as evidence and waits for an IT decision without changing the live Asset.

**Why this priority**: The approval gate has value only if the request is an
accurate, non-mutating proposal. A stale or incomplete proposal cannot support
safe accountability.

**Independent Test**: As a User with `transfer_request`, request a Transfer for
an Assigned Asset and verify the Pending record, captured previous custody,
target User, derived target department, and unchanged Asset.

**Acceptance Scenarios**:

1. **AS-001 - Accepted intent**: **Given** an Assigned Asset held by one User,
   **When** HR or IT Manager requests a handoff to another User, **Then** a
   Pending approval request exists and the Asset remains with its current
   Custodian.
2. **AS-002 - Accepted authorization**: **Given** a User whose Role lacks
   `transfer_request`, **When** that User submits a Transfer request, **Then**
   access is denied and neither Transfer nor Asset data changes.
3. **AS-003 - Test-backed current behavior**: **Given** current Custodian and
   department values, **When** a request is created, **Then** those values are
   copied into `previous_owner` and `previous_department`, the request status
   is Pending, and the supplied target User is recorded.
4. **AS-004 - Accepted dependency**: **Given** a target User with a department,
   **When** the request identifies its target custody, **Then** the target
   department is that User's department; an independently selected department
   is not accepted B4 behavior.
5. **AS-025 - Stakeholder-confirmed**: **Given** the target User equals the
   current Custodian, **When** a Transfer is requested, **Then** the request is
   rejected and no Transfer or Asset data changes.
6. **AS-026 - Stakeholder-confirmed**: **Given** an Asset already has a Pending
   Transfer, **When** another Transfer is requested for that Asset, **Then** the
   second request is rejected and the existing request remains unchanged.

---

### User Story 2 - Approve or Reject a Pending Transfer (Priority: P1)

Authorized IT staff decide a Pending request. Approval performs the custody
handoff as one authoritative lifecycle operation. Rejection closes the request
without touching the Asset.

**Why this priority**: A Transfer is specifically approval-gated. The decision
must not partially update the request, Asset status, Custodian, department, or
condition.

**Independent Test**: Create two equivalent Pending requests in isolated test
fixtures, approve one and reject the other, and verify each Transfer outcome and
all Asset side effects.

**Acceptance Scenarios**:

1. **AS-005 - Accepted intent and test-backed core**: **Given** an eligible
   Pending Transfer, **When** an authorized approver approves it, **Then** the
   Transfer is Approved and the Asset is atomically `Assigned` to the target
   User with that User's department.
2. **AS-006 - Stakeholder-confirmed condition effect**: **Given** an eligible
   Pending Transfer, **When** an authorized approver selects one of `New`,
   `Good`, `Average`, `Damaged`, or `Repair Required` and approves it, **Then**
   that condition is required, recorded on the Transfer, and applied to the
   Asset in the same atomic operation. A missing or noncanonical value rejects
   approval without mutation.
3. **AS-007 - Accepted intent and test-backed core**: **Given** a Pending
   Transfer, **When** an authorized approver rejects it, **Then** the Transfer
   is Rejected and the Asset's status, Custodian, department, and condition are
   unchanged.
4. **AS-008 - Test-backed current behavior**: **Given** an Approved or Rejected
   Transfer, **When** another approve or reject action is attempted, **Then**
   the action is rejected and the existing outcome and Asset remain unchanged.
5. **AS-009 - Accepted authorization**: **Given** a User whose Role lacks
   `asset_custody_manage`, **When** that User attempts approval or rejection,
   **Then** access is denied with no mutation.
6. **AS-027 - Stakeholder-confirmed**: **Given** a Pending Transfer whose live
   Asset Custodian or department no longer equals the captured previous value,
   **When** approval is attempted, **Then** approval is rejected, the Transfer
   remains Pending, and the Asset remains unchanged.

---

### User Story 3 - Reject Lifecycle-Incompatible Transfers (Priority: P1)

The system prevents a Transfer from competing with Service or a terminal Asset
state, both when the request is submitted and when approval is attempted.

**Why this priority**: A late approval must not return a serviced, Sold,
Scrapped, or Lost Asset to ordinary custody.

**Independent Test**: Attempt request and approval against `Under Repair` and
terminal Assets and verify that the Transfer action fails without changing the
Asset or producing an Approved outcome.

**Acceptance Scenarios**:

1. **AS-010 - Accepted lifecycle boundary and test-backed restriction**:
   **Given** an Asset that is `Under Repair`, **When** a Transfer is requested,
   **Then** the request is rejected and no Transfer is created.
2. **AS-011 - Accepted lifecycle boundary with selected test coverage**:
   **Given** an Asset in `Sold`, `Scrapped`, or `Lost`, **When** a Transfer is
   requested, **Then** the request is rejected and no Transfer is created. The
   request-time Sold path is test-backed; the other terminal values follow the
   Draft B2 boundary and shared current restriction.
3. **AS-012 - Test-backed current behavior**: **Given** a Pending Transfer whose
   Asset later becomes `Under Repair` or `Scrapped`, **When** approval is
   attempted, **Then** approval is rejected and custody does not change.
4. **AS-013 - Draft B2 dependency**: **Given** a Pending Transfer when the
   Asset validly enters a terminal state, **When** that terminal operation
   commits, **Then** the Transfer becomes Rejected atomically with the terminal
   transition and no Transfer workflow Notification is emitted by that B2
   operation.

---

### User Story 4 - Receive Transfer Accountability Effects (Priority: P2)

Affected Users receive in-app information about Transfer workflow events, and
operators can trace required mutations and security-relevant rejections through
the shared AuditLog without exposing unnecessary content.

**Why this priority**: Custody handoff affects personal accountability. The
request, decision, and resulting custody must be explainable even though shared
delivery mechanics belong to B8.

**Independent Test**: Exercise each row in the B4 Trigger and Audit Matrix and
verify the selected recipients, resolvable destination, exactly one required
audit event, minimized values, and B8 failure boundary.

**Acceptance Scenarios**:

1. **AS-014 - Stakeholder-confirmed and test-backed**: **Given** a Transfer request is
   submitted, **When** the current trigger executes, **Then** active Users with
   `asset_custody_manage` receive an in-app Pending-approval Notification whose
   destination opens the Pending Transfer list.
2. **AS-015 - Stakeholder-confirmed**: **Given** a Transfer is approved,
   **When** the trigger executes, **Then** the target User and captured previous
   Custodian each receive one in-app Notification whose destination opens the
   Asset detail.
3. **AS-016 - Stakeholder-confirmed**: **Given** a Transfer is rejected,
   **When** the trigger executes, **Then** the requester receives one in-app
   Notification whose destination opens the Transfer list.
4. **AS-017 - Draft B8 dependency**: **Given** a required Transfer AuditLog
   write fails, **When** the owning business action attempts to commit, **Then**
   the business action also fails and no partial Transfer or Asset mutation is
   visible.
5. **AS-018 - Draft B8 dependency**: **Given** a Notification delivery fails
   after valid Transfer work, **When** failure handling runs, **Then** the
   Transfer work remains committed, the failure is operator-visible, and retry
   cannot create a duplicate recipient record.

The three Notification rows are accepted B4 product intent. B8 delivers the
valid matrix but may neither invent nor suppress a Transfer trigger.

---

### User Story 5 - Review Transfers and Produce the Current Transfer PDF (Priority: P2)

An authorized reader can inspect Transfer history and download a printable
custody document for any Transfer record visible to that reader under B1.

**Why this priority**: Operational teams need a legible custody history and a
printable acknowledgement, but document access must not be inferred from a
visible control.

**Independent Test**: List Transfers under each B1 visibility scope, apply the
current status filter, generate a PDF for an in-scope record, verify its fields
and filename, and reject download of an out-of-scope record.

**Acceptance Scenarios**:

1. **AS-019 - Accepted dependency**: **Given** a non-Employee User with
   `asset_view`, **When** Transfer records are requested, **Then** global
   Transfer records are available. **Given** an Employee with `asset_view`,
   **Then** only Transfers directly involving that Employee are available.
2. **OBS-AS-020 - Implementation-only**: **Given** current Transfer records,
   **When** the list is opened, **Then** records are newest first and an exact
   `status` query can select Pending, Approved, or Rejected rows.
3. **OBS-AS-021 - Implementation-only**: **Given** any visible row in the
   current frontend, **When** row actions render, **Then** a PDF button is shown
   regardless of the User's PDF endpoint authority.
4. **AS-022 - Stakeholder-confirmed**: **Given** a User with `asset_view`,
   **When** that User requests a PDF for a Transfer visible under B1, **Then**
   the download succeeds. A request for a Transfer outside that visibility
   scope is denied without returning document data.
5. **OBS-AS-023 - Implementation-only conformance gap**: **Given** a non-Admin
   User with `asset_view`, **When** that User invokes the current PDF endpoint,
   **Then** the endpoint denies access even though the accepted policy and UI
   permit the action.
6. **OBS-AS-024 - Implementation-only**: **Given** a permitted download, **When**
   the document is generated, **Then** it is a portrait custody-transfer PDF
   named from the Transfer code and contains the current fields and three
   signature areas listed under Transfer PDF Baseline.

### Edge Cases

- Store-to-User issuance is Checkout and MUST be rejected as Transfer behavior,
  even though the current backend accepts an Asset with no Custodian and the
  frontend labels that source `IT Store`.
- A target User equal to the captured previous Custodian MUST be rejected. The
  current code accepts this no-op request and is a conformance gap.
- An Asset MUST have at most one Pending Transfer. The current code permits
  concurrent Pending requests and is a conformance gap.
- Approval MUST reject a live Custodian or department that differs from the
  captured previous values, leave the Transfer Pending, and leave the Asset
  unchanged. Current approval checks status but not custody drift and is a
  conformance gap.
- Condition MUST be selected by the approver from the five canonical values.
  The current request form captures it too early, while the backend accepts
  arbitrary text and substitutes the Asset's request-time condition for a blank
  request; both behaviors are conformance gaps.
- The target User may have no department. Draft B2 semantics allow the Asset
  department to be empty in that case; they do not allow an unrelated explicit
  department to replace the derived value.
- Current approval is protected as one operation and reloads the Transfer and
  Asset for update, but row locking has reduced guarantees on the current
  database engine. Planning must still enforce the accepted one-Pending-request
  invariant and must not fall back to last-writer-wins behavior.
- Current rejection changes the Transfer without the same explicit transaction
  boundary used by approval. Rejection must still leave the Asset untouched and
  must satisfy B8 audit atomicity once B8 is accepted.
- The current `transfer_date` is request time while Pending or Rejected and is
  overwritten with approval time when Approved. The field name therefore does
  not establish an accepted business definition of request versus decision
  time.
- Current Transfer Notifications use `/asset/{id}` for approval and
  `/transfer` for rejection, while the frontend Asset detail route is
  `/asset/detail/{id}`. The request destination `/transfer?status=Pending`
  reaches the list, but the current page does not consume that query to filter
  its data. Accepted B4 destinations require the request link to open a
  Pending-filtered list and the approval link to use `/asset/detail/{id}`;
  current links are conformance gaps.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 - Accepted intent**: Transfer MUST be an approval-gated handoff from
  a current User Custodian to a different target User. A Transfer request MUST
  reject an Asset without a current Custodian and MUST reject a target equal to
  that Custodian. Store-to-User issuance MUST use Checkout and MUST NOT have an
  approval gate.
  *(Sources: `CONTEXT.md`, Transfer and Checkout; stakeholder clarification,
  2026-08-04.)*
- **FR-002 - Accepted authorization**: Creating a Transfer request MUST require
  `transfer_request`. The accepted named business requesters are HR and IT
  Manager; Admin holds every code, and an Admin-managed custom Role may hold the
  code under B1. Employee MUST NOT initiate a Transfer.
  *(Source: accepted B1 FR-007 and FR-009 through FR-011.)*
- **FR-003 - Accepted authorization**: Approving or rejecting a Transfer MUST
  require `asset_custody_manage`. Admin, IT Manager, and IT Staff hold that code
  in the accepted named-Role matrix; HR, Employee, and Viewer do not. An Admin
  or custom Role holding the code is authorized, and a requester who holds the
  code MAY approve or reject their own request; no different-actor requirement
  applies.
  *(Sources: `CONTEXT.md`, Transfer; accepted B1 FR-010 and Draft B2
  permission contract.)*
- **FR-004 - Accepted visibility dependency**: Reading Transfer records MUST
  require `asset_view` and follow B1 data visibility: authorized non-Employee
  Roles receive global records, while Employee receives only directly involving
  lifecycle records.
  *(Source: accepted B1 FR-012.)*
- **FR-005 - Stakeholder-confirmed request shape with test-backed core**: A
  successful request MUST create a Pending Transfer that records the Asset,
  captured previous Custodian,
  captured previous department, target User, requester, and remarks without
  changing the Asset. Condition is not required until approval. A request MUST
  be rejected if the Asset already has a Pending Transfer.
  *(Sources: stakeholder clarification, 2026-08-04;
  `backend/assets/tests.py::TransferLifecycleTests::test_request_transfer_captures_the_current_owner_and_department`;
  `backend/assets/transfer.py`; `backend/assets/models.py`.)*
- **FR-006 - Accepted dependency**: The target department MUST be derived from
  the target User under B2. A separately selected target department that differs
  from the target User's department MUST NOT become accepted B4 behavior.
  *(Source: Draft B2 FR-015. Current API and form are a conformance gap.)*
- **FR-007 - Accepted intent**: A Pending Transfer MUST leave the live Asset
  status, Custodian, department, and condition unchanged until a valid decision
  completes.
  *(Source: `CONTEXT.md`, Transfer.)*
- **FR-008 - Accepted intent**: Valid approval MUST atomically mark the Transfer
  Approved and set the Asset to `Assigned`, with the target User as Custodian
  and that User's department as Asset department. Valid rejection MUST mark the
  Transfer Rejected and leave the Asset untouched.
  *(Sources: `CONTEXT.md`, Transfer; Draft B2 FR-006, FR-015, ALR-003, and
  ALR-004; current core is test-backed.)*
- **FR-009 - Accepted lifecycle boundary**: A Transfer request MUST reject
  `Under Repair`, `Sold`, `Scrapped`, and `Lost` Assets without creating a
  request or changing the Asset.
  *(Sources: `CONTEXT.md`; Draft B2 terminal and Service boundaries; current
  Under Repair and Sold request paths are test-backed, while the complete
  shared restriction is implementation evidence.)*
- **FR-010 - Accepted lifecycle boundary**: Approval MUST revalidate that the
  Transfer is Pending, that the Asset is neither `Under Repair` nor terminal,
  and that the live Custodian and department equal the captured previous
  values. A stale-snapshot failure MUST leave the Transfer Pending and the Asset
  unchanged.
  *(Sources: Draft B2 lifecycle contract; stakeholder clarification,
  2026-08-04; current status checks are test-backed.)*
- **FR-011 - Draft B2 dependency**: A valid terminal transition MUST
  atomically mark every Pending Transfer for the Asset Rejected. That automatic
  rejection belongs to the B2 operation and MUST NOT emit a B4 workflow
  Notification.
  *(Source: Draft B2 ALR-006 and Accepted Asset Audit and Notification
  Effects.)*
- **FR-012 - Stakeholder-confirmed condition validation**: Approval MUST require
  the approver to select exactly one of `New`, `Good`, `Average`, `Damaged`, or
  `Repair Required`. The selected value MUST be recorded on the Transfer and
  applied to the Asset atomically with approval. A missing, blank, or
  noncanonical value MUST reject approval and leave the Transfer Pending and
  the Asset unchanged.
  *(Sources: stakeholder clarification, 2026-08-04; Draft B2 canonical
  condition contract; the current approval effect is test-backed.)*
- **FR-013 - Lifecycle integrity**: A Transfer outcome and captured custody MUST
  NOT be changed through direct record update or deletion. State changes MUST
  use request, approve, reject, or a B2-owned terminal transition.
  *(Sources: constitution Principle II; Draft B2 FR-012. Current generic
  update/delete endpoints are Admin-only implementation behavior, not accepted
  lifecycle actions.)*
- **FR-014 - Implementation-only list behavior**: The current Transfer list is
  newest first and accepts an exact status filter. These presentation and query
  details remain current-system evidence until accepted.
  *(Source: `backend/assets/views.py`; `frontend/src/pages/transfer/Transfers.jsx`.)*
- **FR-015 - Stakeholder-confirmed document access**: Downloading a Transfer PDF
  MUST require `asset_view` and MUST use the same B1 visibility scope as reading
  the underlying Transfer. The current fields, signature areas, and timing
  semantics in Transfer PDF Baseline remain implementation-led.
  *(Sources: stakeholder clarification, 2026-08-04;
  `backend/core/exports.py`; `backend/assets/views.py`.)*
- **FR-016 - Draft B8 ownership dependency**: B4 MUST publish and own an
  explicit Transfer trigger matrix covering each business event, recipient,
  message meaning, destination, and audit detail beyond B8's shared minimums.
  The accepted matrix is: request -> all active Users with
  `asset_custody_manage`; approval -> target User and captured previous
  Custodian; rejection -> requester. Request opens the Pending Transfer list,
  approval opens `/asset/detail/{id}`, and rejection opens `/transfer`. B8 MUST
  own only shared in-app delivery, recipient read state, access, retry, and
  retention behavior.
  *(Sources: stakeholder clarification, 2026-08-04; Draft B8 FR-018.)*
- **FR-017 - Draft B8 delivery dependency**: Every accepted B4 Notification
  MUST be in-app only in this version and addressed to a specific User. Email is
  deferred and MUST NOT be inferred from SMTP-labelled Settings.
  *(Source: Draft B8 FR-002 and stakeholder clarification dated 2026-08-04.)*
- **FR-018 - Draft B8 audit dependency**: Every successful Transfer request,
  approval, and rejection and every security-relevant rejected Transfer action
  MUST create exactly one minimized AuditLog entry according to the B4 Trigger
  and Audit Matrix. Routine Transfer reads and Notification read-state actions
  MUST NOT create one. Transfer PDF download is a routine read and MUST NOT
  create an AuditLog entry.
  *(Sources: stakeholder clarification, 2026-08-04; Draft B8 FR-014, FR-015,
  and FR-018.)*
- **FR-019 - Evidence integrity**: Implementation or tests MUST NOT be treated
  as product intent. Every current-only behavior in this Draft MUST remain
  labelled until supported by authoritative intent or an explicit stakeholder
  decision.
  *(Source: `.specify/memory/constitution.md`, Principles I and III.)*
- **FR-020 - Accepted intent (decision accountability)**: A Transfer MUST retain
  its **request time** and, once decided, its **decision time** and the identity
  of the **deciding actor**, as three separately readable values. Request time
  and decision time MUST NOT be represented by a single field, and every surface
  presenting either — including the Transfer PDF — MUST identify which event the
  date denotes. A Pending Transfer has a request time and no decision time.
  *(Derived, not newly decided. The §B4 Trigger and Audit Matrix already requires
  "actor, time" on three distinct events — request, approval, and rejection — so
  three distinct values are already presupposed. FR-003 makes approving and
  rejecting authorized acts, and ALR-004 makes both outcomes terminal; an
  approval-gated workflow whose purpose is accountability must record who decided
  and when. `CONTEXT.md`, Transfer, defines the approval gate this serves.)*

  **Implementation conformance gap**: one `transfer_date` field is reused for
  both events (`backend/assets/models.py`), and the Transfer PDF prints it
  without stating which event it denotes (§Transfer PDF Baseline). The approver
  reference `AssetTransfer.approved_by` is retained by the implementation but was
  required by no requirement before this one, so nothing prevented its removal.
- **FR-021 - Accepted intent (target-User eligibility)**: A Transfer target MUST
  be an active User. A request naming a Disabled target User MUST be rejected
  without creating a Transfer or changing the Asset. Holding no Role MUST NOT
  disqualify a User from being a Transfer target, because the target is a subject
  of the record and gains no permission from it.
  *(Derived, not newly decided. Draft B1 FR-004 excludes a Disabled User from the
  minimal active-User directory that §Assumptions records as the selection
  source, and custody accountability requires a live holder — the same reasoning
  accepted in Draft B3 FR-029 for the Checkout User. This requirement replaces
  the §Assumptions statement, which rested on the selection surface rather than
  on an enforceable rule and therefore did not bind a request submitted
  directly.)*

  **Implementation conformance gap**: the Transfer serializer accepts any User
  reference as `new_owner` without a status check
  (`backend/assets/serializers.py`), so a Disabled User can be made Custodian
  through the API even though the frontend selector offers only active Users.

### Authorization and Lifecycle Requirements

- **ALR-001 - Accepted authorization boundary**: Every Transfer read, request,
  decision, and document action MUST enforce its permission and B1 visibility
  server-side. A hidden or visible frontend control is not authorization.
- **ALR-002 - Accepted atomic approval**: Approval MUST commit the Approved
  outcome, Asset status, Custodian, department, accepted condition effect,
  required AuditLog entry, and no partial intermediate state as one operation.
- **ALR-003 - Accepted rejection safety**: Rejection or any failed permission,
  status, condition, or integrity check MUST leave the Asset unchanged. A failed
  decision MUST leave the Transfer Pending unless the owning valid terminal
  transition changes it under B2.
- **ALR-004 - Accepted terminality**: Approved and Rejected are terminal
  Transfer outcomes. A later approve or reject action MUST be rejected without
  mutation.
- **ALR-005 - Draft B8 failure boundary**: Failure of a required AuditLog write
  MUST reject and roll back the owning Transfer action. Notification failure
  MUST NOT roll back completed Transfer work and MUST be visible and retried
  without duplicate recipient records.
- **ALR-006 - Current permission mapping**: List and retrieve currently use
  `asset_view`; create uses `transfer_request`; approve and reject use
  `asset_custody_manage`; other actions currently fall through to Admin-only.
  List, retrieve, create, and decision mappings are accepted through B1/B2;
  document download MUST instead use `asset_view` and B1 visibility, while
  direct mutation remains prohibited by FR-013.
- **ALR-007 - Stakeholder-confirmed integrity boundary**: Same-User targets MUST
  be rejected, each Asset MUST have no more than one Pending Transfer, and
  approval MUST reject a live Custodian or department that differs from the
  request snapshot. These checks MUST be concurrency-safe and MUST perform zero
  mutation on failure.

### Accepted Transfer Permission Contract

| Transfer action | Permission code | Accepted named-Role behavior | Evidence status |
| --- | --- | --- | --- |
| List/retrieve | `asset_view` plus B1 visibility | Admin, IT Manager, IT Staff, HR, Viewer global; Employee directly involving only | Stakeholder-confirmed in B1; Employee scope is not implemented in the current global queryset |
| Request | `transfer_request` | IT Manager and HR; Admin has all codes | Accepted B1 intent; denial is test-backed |
| Approve/reject | `asset_custody_manage` | Admin, IT Manager, IT Staff | Accepted B1/B2 intent; positive endpoint round trips are test-backed |
| Request/decision through custom Role | Assigned relevant code | Allowed with no implicit bypass and B1 global visibility | Accepted B1 intent |
| Download PDF | `asset_view` plus B1 visibility | Same named/custom Role and Employee-own scope as the underlying Transfer read | Stakeholder-confirmed; current Admin-only endpoint is a conformance gap |
| Directly update/delete a Transfer | Not accepted | None | Current Admin fallback is implementation-only and conflicts with lifecycle ownership |

### B4 Trigger and Audit Matrix

| B4 event | Notification recipient and meaning | Destination | Audit requirement | Acceptance status |
| --- | --- | --- | --- | --- |
| Transfer request succeeds | Every active User with `asset_custody_manage`; a Transfer awaits decision | `/transfer?status=Pending`, which MUST open a Pending-filtered list | Required: actor, time, Transfer/Asset identifiers, absent-to-Pending outcome, captured previous custody, and target custody; no approval condition exists yet | Notification stakeholder-confirmed and test-backed; audit required by Draft B8 |
| Approval succeeds | Target User and captured previous Custodian; custody has changed | `/asset/detail/{id}` | Required: actor, time, Transfer Pending-to-Approved, Asset Custodian/department old and new values, status effect, and required canonical condition old/new values | Notification stakeholder-confirmed; audit required by Draft B8 |
| Rejection succeeds | Requester; request was rejected | `/transfer` | Required: actor, time, Transfer Pending-to-Rejected, Transfer/Asset identifiers; unchanged Asset values need not be duplicated | Notification stakeholder-confirmed; audit required by Draft B8 |
| Permission, terminal/Service, already-processed, or other security-relevant rejection | No current B4 Notification | Not applicable | Required when the rejection is security-relevant: actor, time, attempted action, target identifiers when safe, and reason category; no submitted secrets or full remarks | Draft B8 requirement; current Transfer logging does not cover these failures |
| B2 terminal transition automatically rejects Pending Transfer | None; Draft B2 explicitly emits no workflow Notification | Not applicable | Owned by the B2 terminal-transition entry, including every automatically rejected Transfer | Draft B2 dependency |
| Transfer list/detail read | None | Not applicable | None as a routine business read | Current and Draft B8 minimum |
| Transfer PDF download | None | Download response | None; this is a routine read | Access and no-audit effect stakeholder-confirmed |

Audit values MUST comply with Draft B8 minimization: no password, token,
authentication secret, unnecessary personal data, or full remarks merely because
the source record contains them. Source IP, when captured, is protected B8 data
with its six-month value-retention rule; the AuditLog entry follows B8's
two-year retention rule.

### Transfer PDF Baseline

The following is current implementation evidence, not accepted content or
access policy:

- Portrait A4 document titled `Asset Custody Transfer Document`, branded with a
  configured company name or the current fallback name.
- Filename `transfer_TRF-<five-digit-id>.pdf`.
- Transfer ID, status, current `transfer_date`, Asset ID, Asset name, tag number,
  serial number, category, and condition at Transfer.
- Previous Custodian, previous department, target User, target department,
  requester, approver, and remarks.
- A current null previous Custodian label of `IT Store`; this is a conformance
  gap because Store-to-User issuance is Checkout and a Transfer requires a
  current Custodian.
- Signature areas for Released By (Previous Owner), Received By (New Owner),
  and Authorized By (IT Department).
- The current backend attachment name and frontend download name are consistent
  for the generated Transfer code.
- PDF download requires `asset_view`, follows B1 Transfer-record visibility, and
  must be exposed only for records the current User may read.

### Key Entities

- **Transfer**: The approval record relating one Asset to captured previous
  custody, target custody, requester, approver, Pending/Approved/Rejected
  outcome, approval-time condition, remarks, and a current overloaded date
  field.
- **Asset**: The authoritative lifecycle record. Pending and Rejected Transfer
  leave it untouched; Approved Transfer sets `Assigned`, Custodian, derived
  department, and the accepted condition effect.
- **User**: May act as requester, approver, previous Custodian, target User, or
  Notification recipient. Authorization and visibility are owned by B1.
- **Department**: Organizational data attached to a User. Under Draft B2
  custody semantics the Asset and Transfer target department derive from the
  target User.
- **Notification**: The shared in-app recipient record owned by B8. B4 owns the
  Transfer business event, recipient rule, meaning, and destination.
- **AuditLog Entry**: The shared operational record owned by B8. B4 supplies
  the required Transfer trigger and minimum additional event detail.
- **Transfer PDF**: A generated printable representation of a Transfer. Its
  current fields are evidenced above; access requires `asset_view` and follows
  B1 Transfer visibility.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 13 selected Transfer tests pass in one run: ten lifecycle
  tests and three Transfer endpoint tests covering request authorization,
  approve round trip, and reject round trip.
- **SC-002**: For 100% of valid requests, one Pending Transfer captures the
  request-time previous custody and different target User while producing zero
  changes to the Asset before decision; 100% of second Pending requests for the
  same Asset are rejected.
- **SC-003**: For 100% of valid approvals whose live custody matches the request
  snapshot and whose approver supplies a canonical condition, Transfer outcome,
  Asset status, Custodian, derived department, required condition, and audit
  event commit together; 100% of stale-snapshot, missing-condition, and
  noncanonical-condition approvals are rejected without mutation.
- **SC-004**: For 100% of valid rejections and invalid decision attempts, Asset
  status, Custodian, department, and condition remain unchanged.
- **SC-005**: Request and approval attempts involving `Under Repair`, `Sold`,
  `Scrapped`, or `Lost` Assets produce zero new Approved Transfers and zero
  custody changes.
- **SC-006**: Every protected Transfer action maps to exactly one permission
  and B1 visibility rule; unauthorized attempts return no out-of-scope record
  and perform zero mutation.
- **SC-007**: Every row of the accepted B4 trigger matrix identifies
  one event, recipient rule, message meaning, resolvable destination, and audit
  rule; B8 adds or suppresses zero Transfer business triggers.
- **SC-008**: Every required Transfer audit event contains only the minimum B8
  and B4 fields, and 0% contain authentication secrets or unnecessary full
  remarks. Required audit failure rolls back 100% of owning Transfer actions;
  Notification failure rolls back 0% of otherwise completed actions.
- **SC-009**: In a role-and-record-scope PDF authorization test, 100% of Users
  with `asset_view` can download every Transfer visible to them under B1, 0%
  can download an out-of-scope Transfer, and no denied record exposes a visible
  download control or document data.
- **SC-010**: A scope review finds zero accepted Store-to-User Transfer
  requirements, treats 100% of Store-to-User issuance as Checkout without an
  approval gate, and finds zero confusion between Transfer and Checkout.
- **SC-011**: All six original decisions U-001 through U-006 have explicit
  stakeholder answers, and 0% of their former implementation-only alternatives
  remain presented as accepted behavior.
- **SC-012**: 100% of accepted, test-backed, implementation-only, and unresolved
  claims cite `CONTEXT.md`, an ADR, an accepted dependency identifier, an
  explicit stakeholder decision, or a repository evidence path.

## Assumptions

- The B1 and B2 Draft contracts are current dependencies and remain subject to
  their own acceptance reviews; this Draft does not independently redefine
  them. B3 and B8 likewise remain Draft dependencies until their own acceptance.
- A target User is an active User selected through B1's minimal directory;
  Employees cannot browse that directory or initiate Transfer in current scope.
- The target department follows the Draft B2 Custodian-department invariant.
  The current optional independent department control is a conformance gap.
- Transfer condition is an approval-time accountability value selected by the
  approver from B2's five canonical conditions; request-time free-form capture
  is not accepted.
- `Pending`, `Approved`, and `Rejected` describe Transfer workflow state only;
  they never replace the Asset's canonical status.
- This Draft records current PDF presentation. Its current Admin-only access is
  a conformance gap against the accepted `asset_view` and B1 visibility rule;
  rejected `IT Store` Transfer semantics and the overloaded date field also
  remain implementation findings.
- B8's clarified in-app-only delivery, failure, privacy, access, and retention
  rules apply once B8 is accepted. Email remains deferred.
- No application code is modified as part of specifying this baseline.

## Baseline Evidence and Unresolved Conflicts *(Brownfield Baseline only)*

### Accepted Intent

- Transfer is an approval-gated custody handoff between two Users, requested by
  HR or IT Manager and approved by IT Manager or IT Staff: `CONTEXT.md`,
  **Transfer**.
- Transfer creation uses `transfer_request`; decision uses
  `asset_custody_manage`; named/custom Role and visibility behavior come from
  accepted B1 FR-007 and FR-009 through FR-012.
- A requester who also holds `asset_custody_manage` may approve or reject their
  own request; accepted authorization is permission-code based and includes
  Admin and appropriately granted custom Roles: stakeholder clarification,
  2026-08-04.
- Approved Transfer sets Custodian and derives department from the target User,
  while terminal and Service boundaries come from Draft B2 FR-006, FR-008,
  FR-015, ALR-004, and ALR-006.
- Store-to-User issuance is Checkout without an approval gate under stakeholder
  clarification dated 2026-08-04. The same session resolves C8: Transfer PDF
  download requires `asset_view` and B1 Transfer visibility; the current
  Admin-only endpoint is a conformance gap.
- Shared Notification delivery and AuditLog mechanics remain B8-owned, while
  B4 owns the accepted request/approval/rejection recipient matrix and excludes
  PDF download from audit: stakeholder clarification dated 2026-08-04; Draft B8
  FR-016 through FR-018.

### Verified Behavior Evidence

- **AS-002**: Transfer request without `transfer_request` returns `403`:
  `backend/assets/tests.py::CheckoutTransferEndpointTests::test_transfer_request_requires_transfer_request_permission`.
- **AS-003**: Request captures previous Custodian/department and creates Pending:
  `TransferLifecycleTests::test_request_transfer_captures_the_current_owner_and_department`.
- **AS-005/AS-006**: Approval reassigns Custodian, department, status, and
  condition: `TransferLifecycleTests::test_approve_reassigns_custodian_department_and_condition`.
- **AS-007**: Rejection leaves the Asset untouched:
  `TransferLifecycleTests::test_reject_leaves_the_asset_untouched`.
- **AS-008**: Reprocessing Approved or Rejected records is rejected:
  `TransferLifecycleTests::test_approve_rejects_an_already_processed_transfer`;
  `TransferLifecycleTests::test_reject_rejects_an_already_processed_transfer`.
- **AS-010 through AS-012**: request-time and approval-time Service/terminal
  restrictions are covered by four lifecycle tests in
  `backend/assets/tests.py::TransferLifecycleTests`.
- **AS-014**: request notifies a User with approval permission:
  `TransferLifecycleTests::test_request_transfer_notifies_users_with_approval_permission`.
- Transfer endpoint create/approve and create/reject round trips:
  `CheckoutTransferEndpointTests::test_transfer_request_and_approve_round_trip`;
  `CheckoutTransferEndpointTests::test_transfer_reject_round_trip`.
- The selected 13 tests passed together on 2026-08-04 using the repository-local
  test environment.

### Implementation-Only Observations

- Transfer orchestration, incompatible status list, snapshot creation,
  approval transaction, rejection path, and Notification calls:
  `backend/assets/transfer.py`.
- Transfer persistence fields and `transfer_date` behavior:
  `backend/assets/models.py`.
- Transfer serialization, detail projections, read-only fields, and generated
  `TRF-00001`-style code: `backend/assets/serializers.py`.
- Action permission map, global queryset, status filter, explicit AuditLog
  calls, and Admin-fallback document action: `backend/assets/views.py`.
- PDF fields, branding, signatures, and format: `backend/core/exports.py`.
- Current request form offers `Available` and `Assigned` Assets, all directory
  Users, an optional independent department, five condition choices, and
  remarks: `frontend/src/pages/transfer/Create.jsx`.
- Current list offers request by `transfer_request`, approve/reject by
  `asset_custody_manage`, and PDF for every row; it labels an absent previous
  owner `IT Store`: `frontend/src/pages/transfer/Transfers.jsx`.
- Route and Navbar access use `asset_view`, while the create route uses
  `transfer_request`: `frontend/src/App.jsx`;
  `frontend/src/components/navbar/Menu.jsx`.
- Asset detail exposes Transfer history and repeats the `IT Store` label:
  `frontend/src/pages/asset/Detail.jsx`.
- Current request/approve/reject audit calls exist at the view layer but do not
  satisfy the complete B8 failure, rejected-action, or minimized old/new-value
  contract: `backend/assets/views.py`; `backend/core/services.py`.

### Resolution Status and Remaining Findings

Stakeholder clarification dated 2026-08-04 resolved C1: Store-to-User issuance
is Checkout without an approval gate. B4 therefore requires a current User
Custodian and rejects the current no-Custodian `IT Store` Transfer path.

The same session resolved C8: Transfer PDF download requires `asset_view` and
is limited to the Transfer records visible to that User under B1. The current
Admin-only endpoint is not accepted behavior.

The session also resolves U-003 through U-005: the target must differ from the
current Custodian, only one Pending Transfer may exist per Asset, and approval
must reject a live Custodian or department that differs from the request
snapshot. Current permissive behavior in all three cases is a conformance gap.

The session also resolves U-006: an approver must select one of the five
canonical conditions at approval, and that value is recorded and applied to the
Asset atomically. The current request-time and free-form behavior is a
conformance gap.

The five-question clarification session resolves the requested C1, C8,
integrity, condition, actor-policy, Notification, and audit decisions. Remaining
implementation-led confirmation items are the meaning of request versus
decision timestamps and the exact PDF content; these are presentation/data
semantics outside the five highest-impact decisions and do not reopen U-001
through U-006.

### Implementation Conformance Update

**Date**: 2026-08-12. **Commits**: `538c3a8`, `070c8c2`. Records where the
implementation now conforms to decisions this baseline already states. No
requirement changes; the text above is preserved as the dated review record.

| Decision | Status | Evidence |
| --- | --- | --- |
| C8 — Transfer PDF access | **Closed** | The endpoint is no longer Admin-only: `document` requires `asset_view` and resolves through the scoped queryset, so a reader reaches the PDF only for Transfers visible to them under B1 (`backend/assets/views.py`). Both halves matter — the permission alone would have opened every Transfer document to every reader. Tests: `BaselineConformanceTests::test_asset_view_holder_may_download_the_transfer_document`, `::test_employee_may_download_the_document_for_a_transfer_it_is_party_to`, `::test_employee_cannot_download_someone_elses_transfer_document`, `::test_employee_lists_only_transfers_it_is_party_to`, `::test_a_non_employee_role_still_sees_every_transfer`. |
| U-003 — target differs from Custodian | **Closed** | `request_transfer` rejects a target equal to the current Custodian (`backend/assets/transfer.py`). Test: `::test_transfer_rejects_the_current_custodian_as_target`. |
| U-004 — one Pending Transfer per Asset | **Closed** | A second Pending request on the same Asset is rejected; a new request is permitted once the previous one is decided. Tests: `::test_transfer_rejects_a_second_pending_request`, `::test_a_new_request_is_allowed_once_the_previous_one_is_decided`. |
| U-005 — custody drift before approval | **Open** | `approve` still does not compare the live Custodian and department against the request snapshot. |
| U-006 — condition at approval | **Open** | The condition is still captured at request time and merely applied at approval; there is no approval-time selection from the five canonical values. |
| C1 — no-Custodian `IT Store` path | **Open** | An `Available` Asset with no Custodian can still be transferred, so the path C1 rejects remains reachable. Note this is the mirror of B3's U-005: the same decision is unabsorbed on both sides. |

Both integrity rules surfaced a second defect while being fixed:
`TransferViewSet.create` had no `LifecycleError` handler, so these rejections
would have surfaced as 500s rather than 400s. It now returns 400 like its
sibling actions.

**Provenance note**: these changes were written implementation-first and covered
by tests afterwards, not through the red-green loop Principle IV requires.

## Out of Scope *(mandatory)*

- Store-to-User issuance and all other Checkout/check-in lifecycle behavior
  owned by B3; B4 consumes the decision that Store issuance is Checkout and
  rejects it as Transfer.
- Employee self-service Transfer or any new request actor.
- Service Record opening, closure, Vendor work, cost, or return-to-availability
  behavior owned by B5.
- Asset creation, general maintenance, direct status editing, terminal
  transition implementation, and automatic Pending-Transfer rejection owned by
  B2, except B4's explicit integration boundary.
- Generic Notification storage, unread state, mark-read behavior, retries,
  access, and retention owned by B8.
- Generic AuditLog fields, filters, access, privacy, failure behavior, and
  retention owned by B8.
- Email delivery; the current version is in-app only and SMTP Settings do not
  imply an email implementation.
- Physical Asset audits, periodic inventory verification, or treating AuditLog
  as a physical inspection record.
- Dashboard metrics, Transfer reports, report exports, and general export
  catalog behavior owned by B9. The single current Transfer PDF is included
  only as B4's custody-document boundary.
- Implementation planning or changes to application code.
