# Feature Specification: AS-BUILT Asset Register and Lifecycle Baseline

**Feature Branch**: `docs/baseline-spec-migration`

**Created**: 2026-07-29

**Status**: Baseline — accepted 2026-07-29

**Evidence Date**: 2026-07-29

**Input**: User description: "Create an AS-BUILT baseline specification for the existing ITAMS Asset registry and lifecycle capability under ROADMAP.md entry B2. Document current accepted user-visible behavior, distinguish code-only evidence requiring confirmation, and do not redesign the feature or generate implementation work."

## Clarifications

### Session 2026-07-29

- Q: At Asset creation and during ordinary maintenance, which status and Custodian combinations are accepted? → A: Create only as `Available` or `In Storage`, with no Custodian; Custodian changes only through Checkout or Transfer.
- Q: From which states may terminal transitions occur, and what happens to active lifecycle records? → A: Allow `Sold` and `Scrapped` only from `Available` or `In Storage`; allow `Lost` from any nonterminal status; atomically close open Checkout and Service Records and mark Pending Transfers `Rejected`.
- Q: What does Asset department represent, and how does it change with custody? → A: Department is the current Custodian's department; Checkout and approved Transfer set it, while check-in and Service Record clear it with Custodian.
- Q: Which named Roles may read or maintain the Asset register, and what Asset scope may they see? → A: Admin, IT Manager, IT Staff, HR, and Viewer may read all Assets when granted `asset_view`; Employee may read only Assets where they are Custodian; IT Manager and IT Staff may create/edit; only Admin and IT Manager may delete.
- Q: What AuditLog and Notification effects are required for Asset-register mutations? → A: Audit every successful Asset mutation; terminal audit entries include the operator, old/new status, Custodian/department effects, and every auto-closed or rejected lifecycle record; B2 actions send no Notifications.

## Specification Lineage *(mandatory)*

**Type**: Brownfield Baseline

**Roadmap Reference**: `ROADMAP.md`, entry B2 — Asset register and lifecycle.

**Extends**: None.

**Supersedes**: None.

**Reciprocal Links**: `ROADMAP.md` entry B2 links to this baseline. Future
changes after acceptance must be recorded in a new specification and linked
here with `Extends`, `Supersedes`, or `Superseded by` metadata.

## Domain Alignment *(mandatory)*

**Canonical Terms**:

- **Asset** is a physical IT item tracked from procurement through end of life.
- **status** and **condition** are independent Asset attributes.
- Canonical statuses are `Available`, `Assigned`, `Under Repair`, `In Storage`,
  `Sold`, `Scrapped`, and `Lost`.
- Canonical conditions are `New`, `Good`, `Average`, `Damaged`, and
  `Repair Required`.
- **Custodian** is the User currently holding an Asset, except that a `Lost`
  Asset retains the last Custodian for accountability.
- **Checkout**, **Transfer**, and **Service Record** are the canonical lifecycle
  operations at this baseline's boundaries.
- `Disposed` is rejected terminology; use `Sold`. `Assignment` is rejected for
  the Checkout lifecycle, and `Scrapped` is not a condition.

**Relevant Decisions**:

- `docs/adr/0001-service-record-lifecycle.md` confirms that opening a Service
  Record clears Custodian and moves the Asset to `Under Repair`; closing it
  moves the Asset to `Available` without restoring the previous Custodian.

**Lifecycle and Actors**:

- Admin, IT Manager, IT Staff, HR, and Viewer may read the global Asset
  register when their Role grants `asset_view`. Employee may read only Assets
  where that Employee is the Custodian.
- IT Manager and IT Staff may create and edit Assets. Only Admin and IT Manager
  may delete Assets or Asset files. Admin retains full Asset access.
- IT Manager and IT Staff perform custody operations using
  `asset_custody_manage`; employees do not perform self-service Checkout.
- Checkout and Transfer set Custodian. Check-in and opening a Service Record
  clear Custodian. `Lost` deliberately retains the last Custodian.
- A new Asset starts as `Available` or `In Storage` with no Custodian. Neither
  creation nor ordinary Asset maintenance may set Custodian or department
  directly.
- Department is present only when a Custodian has a department. Checkout and
  approved Transfer copy the Custodian's department; check-in and Service
  Record clear it with Custodian. `Lost` retains both for accountability.
- The Asset register may expose lifecycle state, but it must not bypass the
  Checkout, Transfer, or Service Record operations that own `Assigned`,
  custody handoff, and `Under Repair`.

### Evidence Classification

This Draft uses the following classifications:

- **Accepted intent**: confirmed by `CONTEXT.md` or an ADR and eligible to be a
  baseline requirement.
- **Test-verified current behavior**: demonstrated by passing automated tests,
  but still awaiting stakeholder acceptance as product intent.
- **Implementation-only observation**: visible in backend or frontend code
  without dedicated automated behavioral coverage or authoritative intent.
- **Unresolved**: contradictory or incomplete evidence that blocks baseline
  acceptance.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read a Trustworthy Asset Record (Priority: P1)

An authorized Asset reader opens the register and an Asset detail record to
identify the physical item and understand its current status, condition, and
Custodian without conflating those concepts.

**Why this priority**: The register is the reference point for every downstream
Checkout, Transfer, Service Record, Procurement, and reporting capability.

**Independent Test**: Inspect an Asset that has a canonical status, an
independently chosen canonical condition, and an optional Custodian. Confirm
that each value is presented separately and uses canonical terminology.

**Acceptance Scenarios**:

1. **AS-001 — Accepted intent**: **Given** an Asset with status `Available` and
   condition `Damaged`, **When** an authorized reader views it, **Then** both
   values remain visible and neither value is inferred from or replaces the
   other.
2. **AS-002 — Accepted intent**: **Given** an Asset without a Custodian,
   **When** an authorized reader views it, **Then** the Asset is understood as
   unassigned, its department is empty, and its status remains the
   authoritative availability value.
3. **AS-003 — Accepted intent**: **Given** any user-visible Asset surface,
   **When** lifecycle terminology is presented, **Then** it uses `Checkout`,
   `Sold`, and the canonical condition values, and does not present
   `Assignment`, `Disposed`, or `Scrapped` as a condition.
4. **AS-018 — Stakeholder-confirmed**: **Given** an active Admin, IT Manager,
   IT Staff, HR, or Viewer whose Role grants `asset_view`, **When** that User
   opens the Asset register, **Then** all Assets are visible.
5. **AS-019 — Stakeholder-confirmed**: **Given** an active Employee whose Role
   grants `asset_view`, **When** that Employee opens the Asset register or an
   Asset detail, **Then** only Assets where that Employee is Custodian are
   visible and every other Asset is inaccessible.

---

### User Story 2 - Maintain Asset Register Information (Priority: P2)

An authorized Asset maintainer creates and updates Asset identity and descriptive
information, records condition inspections, and associates images or documents
with the Asset.

**Why this priority**: Accurate identity and supporting evidence make the Asset
usable across its lifecycle, but the exact current register contract is mostly
implementation-led and must be confirmed before acceptance.

**Independent Test**: Exercise each observed register action with an authorized
and unauthorized User and verify the record, validation response, and visible
history. These cases document the current system; they are not accepted product
requirements until the observations in the evidence section are confirmed.

**Acceptance Scenarios**:

1. **AS-014 — Stakeholder-confirmed**: **Given** an authorized maintainer
   creates an Asset, **When** the initial lifecycle data is submitted, **Then**
   status is `Available` or `In Storage` and both Custodian and department are
   empty.
2. **AS-015 — Stakeholder-confirmed**: **Given** an existing Asset, **When** an
   ordinary create or maintenance request attempts to set Custodian or
   department directly, **Then** the request is rejected without changing
   Asset state.
3. **AS-020 — Stakeholder-confirmed**: **Given** the named Asset Roles,
   **When** they attempt register maintenance, **Then** IT Manager and IT Staff
   may create and edit, Admin and IT Manager may delete, and every other
   ungranted write is denied without mutation.
4. **AS-021 — Stakeholder-confirmed**: **Given** an authorized User
   successfully creates, updates, or deletes an Asset, records a condition
   inspection, or uploads or deletes an Asset image or document, **When** the
   mutation completes, **Then** one operational AuditLog record identifies the
   operator, action, affected Asset, and completion time, and no Notification
   is created by B2.

**Current-System Verification Scenarios — Not Yet Accepted Requirements**:

1. **OBS-AS-001 — Implementation-only**: **Given** any User with `asset_view`,
   **When** the User opens the Asset register, filters by status or Category, or
   searches by Asset ID, name, tag number, or serial number, **Then** matching
   current-system Assets are returned from the global register. This conflicts
   with the accepted Employee-only Custodian scope.
2. **OBS-AS-002 — Implementation-only**: **Given** a User with `asset_create`,
   **When** valid current form data is submitted, **Then** one Asset is created
   and a barcode based on its tag number is made available.
3. **OBS-AS-003 — Implementation-only**: **Given** a User with `asset_edit`,
   **When** Asset identity or descriptive data changes, **Then** the Asset and
   barcode are updated.
4. **OBS-AS-004 — Implementation-only**: **Given** a User with `asset_edit`,
   **When** a canonical condition and optional notes are recorded as an
   inspection, **Then** the Asset condition changes and a dated condition-log
   entry identifies the inspector.
5. **OBS-AS-005 — Implementation-only**: **Given** a User with `asset_edit`,
   **When** an allowed image or document is uploaded, **Then** it appears on
   Asset detail; documents increment a per-Asset, per-document-type version.
6. **OBS-AS-006 — Implementation-only**: **Given** a User with `asset_delete`,
   **When** an Asset, image, or document is deleted, **Then** the selected
   record is removed. Asset-history retention and recoverability are unresolved.

---

### User Story 3 - Preserve Lifecycle and Custodian Integrity (Priority: P1)

An authorized Asset maintainer records non-workflow lifecycle facts without
bypassing the operations that own custody and servicing, and without reopening
an Asset that has left circulation.

**Why this priority**: Incorrect status or Custodian combinations make the Asset
register unreliable and can leave Checkout or Service Record history open.

**Independent Test**: Attempt each transition in the accepted boundary table
and the test-verified current-system table. Confirm the allowed or rejected
outcome and all Custodian and lifecycle-record side effects.

**Acceptance Scenarios**:

1. **AS-004 — Accepted intent**: **Given** an `Available` Asset, **When**
   Checkout succeeds, **Then** status becomes `Assigned` and Checkout sets the
   Custodian and that Custodian's department; a direct status edit is not a
   substitute for Checkout.
2. **AS-005 — Accepted intent**: **Given** an `Assigned` Asset, **When**
   check-in succeeds, **Then** status becomes `Available` and Custodian is
   cleared with department; a direct status edit is not a substitute for
   check-in.
3. **AS-006 — Accepted intent**: **Given** an eligible Asset, **When** a
   Service Record opens, **Then** status becomes `Under Repair` and Custodian is
   cleared with department; **When** that Service Record closes, **Then** status
   becomes `Available` and neither the previous Custodian nor department is
   restored.
4. **AS-007 — Stakeholder-confirmed**: **Given** an `Available` or `In Storage`
   Asset moves to `Sold` or `Scrapped`, **When** the transition completes,
   **Then** the Asset has left circulation, Custodian and department are
   cleared, and no later lifecycle transition may return it to circulation.
5. **AS-008 — Stakeholder-confirmed**: **Given** an Asset in any nonterminal
   status, **When** it is recorded as `Lost`, **Then** the Asset leaves
   circulation but retains its last Custodian and that Custodian's department,
   when they exist, for accountability.
6. **AS-009 — Accepted intent**: **Given** a `Sold`, `Scrapped`, or `Lost`
   Asset, **When** a later status change is attempted, **Then** the request is
   rejected and the Asset remains in its terminal status.
7. **AS-016 — Stakeholder-confirmed**: **Given** an `Assigned` or
   `Under Repair` Asset, **When** a User attempts to record it as `Sold` or
   `Scrapped`, **Then** the request is rejected and the existing lifecycle
   state remains unchanged.
8. **AS-017 — Stakeholder-confirmed**: **Given** an accepted terminal
   transition and any open Checkout, open Service Record, or Pending Transfer
   for the Asset, **When** the transition completes, **Then** the Checkout and
   Service Record are closed and every Pending Transfer is marked `Rejected`
   as part of the same operation.
9. **AS-022 — Stakeholder-confirmed**: **Given** an accepted terminal
   transition, **When** it completes, **Then** its AuditLog record identifies
   the operator, old and new status, Custodian and department effects, and every
   Checkout, Service Record, or Transfer automatically closed or rejected, and
   no affected User receives a Notification from B2.

### Accepted Lifecycle Boundary

| From | Operation | To | Custodian and department effect | Acceptance source |
| --- | --- | --- | --- | --- |
| Not yet registered | Create Asset | `Available` or `In Storage` | Both must be empty | Clarification session 2026-07-29 |
| `Available` | Checkout | `Assigned` | Custodian set to Checkout User; department set to that User's department or empty | `CONTEXT.md`; clarification session 2026-07-29 |
| `Assigned` | Check-in | `Available` | Both cleared | `CONTEXT.md`; clarification session 2026-07-29 |
| Eligible nonterminal state | Open Service Record | `Under Repair` | Both cleared | `CONTEXT.md`; ADR-0001; clarification session 2026-07-29 |
| `Under Repair` | Close Service Record | `Available` | Both remain clear; neither previous value is restored | `CONTEXT.md`; ADR-0001; clarification session 2026-07-29 |
| `Available` or `In Storage` | Record `Sold` | `Sold` | Both cleared | `CONTEXT.md`; clarification session 2026-07-29 |
| `Available` or `In Storage` | Record `Scrapped` | `Scrapped` | Both cleared | `CONTEXT.md`; clarification session 2026-07-29 |
| Any nonterminal status | Record `Lost` | `Lost` | Last Custodian and that Custodian's department retained when they exist | `CONTEXT.md`; clarification session 2026-07-29 |
| Any terminal state | Any later lifecycle transition | Rejected | Both unchanged | `CONTEXT.md`, terminal-state definition |

The precise eligible source states for opening a Service Record remain
evidence-qualified; sibling baseline B5 owns that eligibility decision.

### Test-Verified Current Transition Behavior — Awaiting Acceptance

| Attempt | Current outcome | Side effects evidenced | Evidence |
| --- | --- | --- | --- |
| Direct `Available → In Storage` update | Allowed | Status changes; other Asset data remains | `AssetStatusTransitionTests::test_administrative_status_edits_are_unaffected` |
| Direct entry into `Assigned` | Rejected | Existing status and Custodian remain | `AssetStatusTransitionTests::test_cannot_enter_assigned_by_direct_edit` |
| Direct entry into `Under Repair` | Rejected | Existing status remains | `AssetStatusTransitionTests::test_cannot_enter_under_repair_by_direct_edit` |
| Direct exit from `Assigned` to a nonterminal state | Rejected | Status and Custodian remain | `AssetStatusTransitionTests::test_cannot_leave_assigned_by_direct_edit` |
| Direct exit from `Under Repair` to a nonterminal state | Rejected | Status remains | `AssetStatusTransitionTests::test_cannot_leave_under_repair_by_direct_edit` |
| Direct `Assigned ↔ Under Repair` | Rejected | Existing lifecycle state remains | `AssetStatusTransitionTests::test_cannot_move_directly_between_assigned_and_under_repair` |
| Direct `Assigned → Sold` | Allowed, but conflicts with the accepted source-state restriction | Custodian cleared | `AssetStatusTransitionTests::test_disposal_is_still_allowed_directly_from_assigned` |
| Direct `Under Repair → Lost` | Allowed and consistent with reactive `Lost` | Terminal status recorded | `AssetStatusTransitionTests::test_lost_is_still_allowed_directly_from_under_repair` |
| Enter terminal state from an open Checkout | Allowed | Open Checkout becomes returned with return time | `AssetStatusTransitionTests::test_entering_terminal_status_closes_the_open_checkout` |
| Enter terminal state from an open Service Record | Allowed | Open Service Record becomes closed with return time | `AssetStatusTransitionTests::test_entering_terminal_status_closes_the_open_service_record` |
| Change status after terminal state | Rejected | Terminal status remains | `AssetStatusTransitionTests::test_cannot_reverse_out_of_a_terminal_status` |
| Edit an unrelated field without changing `Assigned` | Allowed | Status and Custodian remain | `AssetStatusTransitionTests::test_editing_unrelated_fields_without_a_status_change_is_unaffected` |

---

### User Story 4 - Receive Safe Validation and Failure Outcomes (Priority: P1)

An Asset reader or maintainer receives a clear rejection when an action is not
permitted or would violate a canonical value or lifecycle boundary, and a
failed action leaves current Asset state unchanged.

**Why this priority**: A failed write must not create ambiguous custody or
partial lifecycle history.

**Independent Test**: Submit an invalid value, forbidden action, duplicate
identity, and rejected transition separately; confirm a visible failure and no
unintended mutation.

**Acceptance Scenarios**:

1. **AS-010 — Accepted intent**: **Given** a proposed status or condition
   outside the canonical sets, **When** the change is submitted, **Then** the
   system rejects it and preserves the current Asset.
2. **AS-011 — Governance requirement**: **Given** a User without the permission
   required for a protected Asset action, **When** the action is attempted,
   **Then** access is denied and no Asset, file, or history data is changed.
3. **AS-012 — Accepted intent**: **Given** a request that directly enters or
   leaves a lifecycle-managed status, **When** it bypasses Checkout, check-in,
   Transfer, or Service Record, **Then** it is rejected with guidance to use
   the owning lifecycle operation.
4. **AS-013 — Accepted intent**: **Given** a terminal Asset, **When** a User
   attempts to change its status, **Then** the system reports that the status
   cannot change further and makes no mutation.

### Negative Cases

- **NC-001 — Accepted intent**: Reject a status or condition outside the
  canonical sets and preserve the Asset.
- **NC-002 — Accepted intent**: Reject direct entry into or nonterminal exit
  from `Assigned` and `Under Repair`; direct the User to the owning lifecycle
  operation.
- **NC-003 — Accepted intent**: Reject every attempt to leave `Sold`,
  `Scrapped`, or `Lost`.
- **NC-004 — Governance requirement**: Deny an Asset action when the User lacks
  its accepted permission and make no state change.
- **NC-005 — Implementation-only**: Reject a condition inspection with a
  noncanonical condition.
- **NC-006 — Implementation-only**: Reject an image or document submission when
  no file is supplied or the filename extension is not allowed.
- **NC-007 — Stakeholder-confirmed**: Reject Asset creation with `Assigned`,
  `Under Repair`, `Sold`, `Scrapped`, or `Lost`, and reject any direct
  Custodian or department value during creation or ordinary maintenance.
- **NC-008 — Stakeholder-confirmed**: Reject `Sold` or `Scrapped` when the
  Asset is `Assigned` or `Under Repair`; do not close or change the active
  lifecycle records on a rejected transition.
- **NC-009 — Stakeholder-confirmed**: Deny an Employee access to an Asset where
  another User is Custodian or where Custodian is empty, even though the
  Employee Role grants `asset_view`.

### Edge Cases

- The current create interface and backend accept statuses and Custodian values
  and department values that the clarified creation rule rejects. This remains
  an implementation conformance gap, not product ambiguity.
- A `Lost` Asset cannot be introduced through ordinary Asset creation. `Lost`
  must be recorded as a transition of an existing Asset so the last Custodian,
  when one exists, can be retained for accountability.
- Status and condition remain independent even for terminal Assets. A terminal
  status must not introduce `Scrapped` as a condition or silently rewrite the
  existing canonical condition.
- Current code accepts `Sold` and `Scrapped` from source states that the
  clarified rule rejects. This is an implementation conformance gap.
- An accepted terminal transition must close open Checkout and Service Records
  and reject Pending Transfers atomically. Current code closes the first two
  but leaves a Pending Transfer pending and unapprovable; notification,
  operator attribution, and exact historical wording remain unresolved.
- Current check-in and Service Record behavior clears Custodian but retains
  department; Transfer may accept a target department different from the new
  Custodian's department; and ordinary Asset editing exposes direct department
  maintenance. Each behavior conflicts with the clarified department meaning.
- Current backend Asset queries return the global register to every
  `asset_view` holder, including Employee. The accepted Employee Custodian scope
  therefore remains an authorization conformance gap.
- Asset deletion currently removes related Checkout, Transfer, Service Record,
  condition, AMC, image, and document rows through relationship deletion.
  Retention, archival, and recovery policy are unresolved.
- Uploads with no file or an unsupported extension are currently rejected.
  Content inspection, malware scanning, media access control, orphan cleanup,
  and retention are unresolved.
- Asset ID, tag number, and serial number are currently unique. The frontend
  additionally requires a numeric tag number while the backend identity field
  accepts text; the accepted format is unresolved.
- The Asset detail heading `Assignment & Warranty` conflicts with canonical
  `Checkout` terminology and remains unresolved as C3.

## Requirements *(mandatory)*

### Functional Requirements

The requirements below contain only accepted intent from `CONTEXT.md`, ADR-0001,
or repository governance. Current behavior without that authority remains in
the evidence and unresolved-conflict sections.

- **FR-001**: The system MUST represent each Asset as a physical IT item tracked
  through its lifecycle from procurement to end of life.
  *(Source: `CONTEXT.md`, introduction and Asset.)*
- **FR-002**: Each Asset MUST have exactly one status from `Available`,
  `Assigned`, `Under Repair`, `In Storage`, `Sold`, `Scrapped`, or `Lost`.
  *(Source: `CONTEXT.md`, Asset.)*
- **FR-003**: Each Asset MUST have exactly one condition from `New`, `Good`,
  `Average`, `Damaged`, or `Repair Required`, independent of status.
  *(Source: `CONTEXT.md`, Asset.)*
- **FR-004**: User-visible terminology MUST use `Sold` rather than `Disposed`,
  MUST use `Checkout` rather than `Assignment` for that lifecycle, and MUST NOT
  offer `Scrapped` as a condition.
  *(Source: `CONTEXT.md`, Asset, Scrapped, and Checkout.)*
- **FR-005**: Asset status MUST remain authoritative for availability; absence
  of a Custodian means the Asset is implicitly unassigned and requires an empty
  department, but MUST NOT by itself change or determine status.
  *(Sources: `CONTEXT.md`, Custodian; stakeholder clarification, 2026-07-29.)*
- **FR-006**: Checkout and Transfer MUST set Custodian; check-in and opening a
  Service Record MUST clear Custodian and department.
  *(Sources: `CONTEXT.md`, Custodian; stakeholder clarification, 2026-07-29.)*
- **FR-007**: Opening a Service Record MUST move the Asset to `Under Repair` and
  clear Custodian and department; closing it MUST move the Asset to `Available`
  without restoring the previous Custodian or department.
  *(Sources: `CONTEXT.md`, Service Record;
  `docs/adr/0001-service-record-lifecycle.md`.)*
- **FR-008**: `Sold`, `Scrapped`, and `Lost` MUST be terminal statuses that
  cannot transition back into circulation.
  *(Source: `CONTEXT.md`, Asset, Sold, Scrapped, and Lost.)*
- **FR-009**: Entering `Sold` or `Scrapped` MUST clear Custodian because the
  Asset has left organizational circulation and MUST also clear department;
  entering `Lost` MUST retain the last Custodian and that Custodian's
  department, when they exist, for accountability.
  *(Sources: `CONTEXT.md`, Sold, Scrapped, Lost, and Custodian; stakeholder
  clarification, 2026-07-29.)*
- **FR-010**: A condition change MUST NOT implicitly change Asset status, and a
  status change MUST NOT implicitly derive a different condition.
  *(Source: `CONTEXT.md`, Asset.)*
- **FR-011**: The system MUST reject noncanonical status and condition values
  without changing the Asset.
  *(Source: `CONTEXT.md`, Asset; observable acceptance case AS-010.)*
- **FR-012**: Lifecycle state owned by Checkout, Transfer, check-in, or Service
  Record MUST be entered and left through that owning operation rather than a
  direct Asset edit.
  *(Sources: `CONTEXT.md`, Custodian, Checkout, Transfer, and Service Record;
  ADR-0001.)*
- **FR-013**: A new Asset MUST be created only as `Available` or `In Storage`
  with no Custodian or department. Creation MUST reject every other status and
  any supplied Custodian or department.
  *(Source: stakeholder clarification, 2026-07-29.)*
- **FR-014**: `Sold` and `Scrapped` MUST be accepted only from `Available` or
  `In Storage`; `Lost` MUST be accepted from any nonterminal status so it can be
  recorded reactively without discarding Custodian accountability.
  *(Sources: `CONTEXT.md`, Lost and Custodian; stakeholder clarification,
  2026-07-29.)*
- **FR-015**: Asset department MUST equal the current Custodian's department
  when that User has one and MUST be empty when Custodian is empty. Checkout and
  approved Transfer MUST derive department from the new Custodian; check-in and
  Service Record MUST clear it. `Lost` MUST retain the accountable Custodian's
  department.
  *(Source: stakeholder clarification, 2026-07-29.)*

### Authorization and Lifecycle Requirements

- **ALR-001**: Every protected Asset read or write MUST be authorized at the
  action boundary; hiding a frontend control MUST NOT be the sole authorization
  control.
  *(Source: `.specify/memory/constitution.md`, Principle II.)*
- **ALR-002**: A rejected permission or validation check MUST leave the Asset,
  Custodian, condition history, files, and related lifecycle records unchanged.
  *(Source: `.specify/memory/constitution.md`, Principle II.)*
- **ALR-003**: A transition that changes status, Custodian, and related open
  lifecycle records MUST complete as one authoritative operation so that
  partial state is not user-visible.
  *(Source: `.specify/memory/constitution.md`, Principle II.)*
- **ALR-004**: `Assigned` MUST be entered by Checkout or an approved Transfer;
  direct entry MUST be rejected. Leaving `Assigned` for a nonterminal state
  MUST use check-in or another accepted owning lifecycle operation.
  *(Sources: `CONTEXT.md`, Checkout and Transfer; current rejection is
  test-verified.)*
- **ALR-005**: `Under Repair` MUST be entered by opening a Service Record and
  left for `Available` by closing that Service Record; direct entry or exit
  MUST be rejected.
  *(Sources: `CONTEXT.md`, Service Record; ADR-0001; current rejection is
  test-verified.)*
- **ALR-006**: Terminal-state processing MUST preserve the accountability rules
  in FR-009 and MUST NOT leave an Asset appearing active in an open custody or
  service operation. An accepted terminal transition MUST atomically close open
  Checkout and Service Records and mark every Pending Transfer `Rejected`.
  *(Sources: `CONTEXT.md`, terminal and Custodian rules; stakeholder
  clarification, 2026-07-29.)*
- **ALR-007**: Ordinary Asset maintenance MUST NOT set, replace, or clear
  Custodian or department directly. Checkout and Transfer own Custodian and
  department assignment; check-in and Service Record own the accepted clearing
  behavior; `Lost` owns its accountability exception.
  *(Sources: `CONTEXT.md`, Custodian; stakeholder clarification, 2026-07-29.)*
- **ALR-008**: A rejected `Sold` or `Scrapped` transition from `Assigned` or
  `Under Repair` MUST leave the Asset, Custodian, department, and related active
  lifecycle records unchanged.
  *(Source: stakeholder clarification, 2026-07-29.)*
- **ALR-009**: An active Admin, IT Manager, IT Staff, HR, or Viewer whose Role
  grants `asset_view` MUST be able to read all Assets. An active Employee with
  `asset_view` MUST be limited to Assets where that Employee is Custodian,
  including a `Lost` Asset that retains that Employee as Custodian.
  *(Source: stakeholder clarification, 2026-07-29.)*
- **ALR-010**: IT Manager and IT Staff MUST be permitted to create and edit
  Assets. Asset, image, and document deletion MUST be permitted only to Admin
  and IT Manager. All other named-Role write attempts MUST be denied without
  mutation.
  *(Source: stakeholder clarification, 2026-07-29.)*

- **ALR-011**: Every successful B2 mutation MUST create the AuditLog effect
  defined in AS-021. A terminal transition MUST create the expanded AuditLog
  effect defined in AS-022. No B2 mutation or terminal side effect MUST create
  a Notification.
  *(Source: stakeholder clarification, 2026-07-29.)*

### Accepted Asset Permission Contract and Current Codes

| Asset action | Permission code | Accepted named-Role behavior | Evidence status |
| --- | --- | --- | --- |
| List, retrieve, and aggregate history | `asset_view` | Admin, IT Manager, IT Staff, HR, and Viewer: global; Employee: Custodian-only | Stakeholder-confirmed; Employee scope not implemented |
| Create Asset | `asset_create` | Admin, IT Manager, and IT Staff | Stakeholder-confirmed named Roles; current mapping is implementation evidence |
| Update Asset or append condition inspection | `asset_edit` | Admin, IT Manager, and IT Staff | Stakeholder-confirmed named Roles; current mapping is implementation evidence |
| Upload image or document | `asset_edit` | Admin, IT Manager, and IT Staff | Stakeholder-confirmed named Roles; current mapping is implementation evidence |
| Delete Asset, image, or document | `asset_delete` | Admin and IT Manager | Stakeholder-confirmed named Roles; current mapping is implementation evidence |
| Perform Checkout, Transfer approval/rejection, or Service Record open/close | `asset_custody_manage` | Admin, IT Manager, and IT Staff | Accepted actor intent; endpoint mapping is test-verified or implementation evidence |

The current permission engine also requires an authenticated active profile and
allows superusers and the named `Admin` Role to bypass permission codes. The
named Asset Role behavior above is accepted for B2; B1 still owns Role
administration, custom-Role policy, and non-Asset permissions.

### Accepted Asset Audit and Notification Effects

- Every successful Asset create, update, delete, condition inspection, image
  upload/delete, and document upload/delete MUST create an operational AuditLog
  record identifying the operator, action, affected Asset, and completion time.
- A terminal-transition AuditLog record MUST additionally identify old and new
  status, Custodian and department effects, and every Checkout, Service Record,
  or Transfer automatically closed or rejected by the transition.
- B2 Asset-register actions MUST NOT create Notifications, including when a
  terminal transition closes or rejects related lifecycle records. Explicit
  Checkout, Transfer, and Service Record workflow notifications remain owned by
  B3, B4, and B5.
- Generic AuditLog storage, administrative access, filters, and retention remain
  owned by B8.

### Current Validation and Failure Behavior — Awaiting Acceptance Where Not Sourced

- Noncanonical Asset status and condition values are rejected.
- Direct entry into or nonterminal exit from `Assigned` and `Under Repair` is
  rejected with guidance to use Checkout, check-in, or Service Record.
- A status change from a terminal Asset is rejected.
- Current create validation does not enforce FR-013 or ALR-007. The current
  create interface and backend behavior are a confirmed conformance gap, not an
  accepted exception.
- Current identity requires unique Asset ID, tag number, and serial number, plus
  Category, Brand, and Model. Exact optionality, numeric tag formatting,
  Procurement linkage, department, Location, financial, Warranty, and create
  defaults remain implementation-only.
- Condition-inspection submission rejects a noncanonical condition.
- Image and document submission rejects a missing file or a filename extension
  outside the configured allowlist.
- Current frontend forms show local required/type messages and otherwise expose
  backend failure content. No frontend behavioral tests establish the complete
  wording, accessibility, or recovery behavior.

### Key Entities

- **Asset**: The physical IT item and central lifecycle record. Accepted
  attributes are status, condition, and optional Custodian; the current
  implementation additionally stores identity, catalog, Procurement, financial,
  Location, department, Warranty, notes, barcode, and timestamps.
- **User / Custodian**: The User currently holding an Asset, except that a
  `Lost` Asset retains the last Custodian for accountability.
- **Asset Condition Log**: A current-system inspection entry containing a
  condition, inspection time, inspector, and notes. Its precise retention and
  acceptance are unresolved.
- **Asset Image**: A current-system file associated with an Asset.
- **Asset Document**: A current-system typed, versioned file associated with an
  Asset.
- **Checkout, Transfer, and Service Record**: Related lifecycle records whose
  aggregate histories are currently shown on Asset detail. Their workflows are
  specified by B3, B4, and B5, not by this baseline.
- **AuditLog and Notification**: Shared operational records owned by B8. This
  baseline defines the accepted Asset-specific triggers and no-Notification
  rule.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review set covering all seven canonical statuses and all five
  canonical conditions, 100% of Assets present status and condition as
  independent values using canonical terminology.
- **SC-002**: For every accepted transition scenario AS-004 through AS-017,
  100% of allowed actions complete with the defined status/Custodian effects
  and 100% of rejected actions leave the prior state unchanged.
- **SC-003**: For each protected Asset action in the accepted permission
  contract, 100% of unauthorized attempts change zero Asset, file,
  condition-log, or lifecycle-history records, and Employee reads return zero
  Assets where another User or no User is Custodian.
- **SC-004**: For every reviewed `Sold`, `Scrapped`, and `Lost` transition, the
  Asset is no longer available for circulation; `Sold` and `Scrapped` retain no
  Custodian or department, while `Lost` retains the last Custodian and that
  Custodian's department when they existed.
- **SC-005**: 100% of implementation-led behavior included in this Draft is
  labeled as test-verified, implementation-only, or unresolved and cites at
  least one repository evidence path.
- **SC-006**: Stakeholder review resolves C3, deletion retention, file
  security/lifecycle, custom-Role policy, Asset-specific integration with B8,
  and the C2, terminal, department, Employee-visibility, and detailed
  terminal-audit implementation conformance gaps before the baseline status can
  move from `Draft` to accepted.
- **SC-007**: In a review set containing each successful B2 mutation type, 100%
  produce one operational AuditLog record and zero Notifications; every
  terminal case records 100% of its automatic lifecycle-record effects.

## Assumptions

- This is an AS-BUILT documentation baseline as of 2026-07-29. It does not
  request a behavior change and does not make current code-only behavior
  authoritative.
- B1 (identity, access, and organization) and B6 (Procurement, Vendor, and
  catalog masters) are dependencies whose accepted baselines do not yet exist.
  This Draft freezes only B2's named-Role Asset access; it does not freeze
  authentication, custom-Role policy, non-Asset permissions, or master-data
  requirements.
- Status remains authoritative for availability; Custodian presence is not a
  substitute status.
- The term "terminal" means the Asset cannot return to circulation through a
  later lifecycle transition.
- `Sold` and `Scrapped` are planned terminal transitions from `Available` or
  `In Storage`; `Lost` is a reactive terminal transition allowed from any
  nonterminal status.
- New Assets enter the register only as `Available` or `In Storage` without a
  Custodian or department; historical terminal Assets require a separate,
  explicitly specified migration/import decision if that need arises.
- `Lost` retains the last Custodian only when one already exists; this baseline
  does not invent a Custodian for an unheld Asset.
- Evidence recorded under observations describes current behavior but remains
  open to stakeholder rejection or amendment during clarification.
- The named Role policy in ALR-009 and ALR-010 is authoritative for B2; B1
  remains responsible for whether custom Roles are supported and how their
  Asset scope is expressed.
- B2 owns which Asset actions trigger AuditLog or Notification effects; B8 owns
  the shared records' storage, access, filtering, and retention behavior.

## Baseline Evidence and Unresolved Conflicts *(Brownfield Baseline only)*

### Accepted Intent

- Canonical Asset, status, condition, terminal-state, Custodian, Checkout,
  Transfer, Service Record, Sold, Scrapped, and Lost rules:
  `CONTEXT.md`.
- Service Record custody and return-to-availability decision:
  `docs/adr/0001-service-record-lifecycle.md`.
- B2 capability boundary, dependencies, evidence rating, decisions C2/C3, and
  deferred roadmap:
  `ROADMAP.md`.
- Accepted creation and direct-Custodian rule:
  clarification session 2026-07-29 in this specification.
- Accepted terminal source-state and active-record side effects:
  clarification session 2026-07-29 in this specification.
- Accepted department meaning and lifecycle:
  clarification session 2026-07-29 in this specification.
- Accepted named Role permissions and Asset visibility:
  clarification session 2026-07-29 in this specification.
- Accepted Asset-specific AuditLog and Notification effects:
  clarification session 2026-07-29 in this specification.
- Brownfield evidence and acceptance rules:
  `.specify/memory/constitution.md`;
  `docs/agents/domain.md`;
  `specs/README.md`.

### Verified Behavior Evidence

- **AS-004, AS-005, ALR-004** — Checkout and check-in status, condition, and
  Custodian behavior:
  `backend/assets/tests.py::CheckoutLifecycleTests`;
  `backend/assets/tests.py::CheckoutTransferEndpointTests`.
- **AS-006, ALR-005** — Service Record status/Custodian behavior and rejection
  cases:
  `backend/assets/tests.py::ServiceRecordLifecycleTests`;
  `backend/assets/tests.py::ServiceRecordEndpointTests`.
- **AS-007 through AS-009, ALR-006** — terminal irreversibility, Sold/Lost
  Custodian effects, direct lifecycle guards, and open-record closure:
  `backend/assets/tests.py::AssetStatusTransitionTests`.
- **AS-011** — selected permission enforcement for owning lifecycle endpoints:
  `backend/assets/tests.py::CheckoutTransferEndpointTests`;
  `backend/assets/tests.py::ServiceRecordEndpointTests`.
- Consolidated evidence classification and the recorded successful 70-test
  baseline run:
  `docs/research/itams-current-system-baseline.md`.

### Implementation-Only Observations

- Asset fields, canonical constant lists, file relationships, condition-log
  structure, aggregate-history relationships, and cascading deletion:
  `backend/assets/models.py`.
- Status/condition validation, update-only lifecycle guards, terminal
  Custodian effects, terminal open-record closure, and the create-time bypass:
  `backend/assets/serializers.py`.
- Permission mapping, search/filter behavior, barcode regeneration, aggregate
  history, condition inspection, file validation/versioning, and Asset-specific
  AuditLog calls:
  `backend/assets/views.py`.
- Barcode generation:
  `backend/assets/barcodes.py`.
- Active-profile, permission-code, Admin, and superuser authorization behavior:
  `backend/core/permissions.py`;
  `backend/accounts/models.py`.
- Current seeded Role grants and permission rename:
  `backend/accounts/migrations/0002_seed_rbac_and_org.py`;
  `backend/accounts/migrations/0003_it_staff_no_transfer_request.py`;
  `backend/accounts/migrations/0004_rename_asset_transfer_permission.py`.
- AuditLog and Notification helper effects:
  `backend/core/services.py`;
  `backend/core/models.py`.
- Upload limits and extension allowlists:
  `backend/itams/settings.py`.
- Register presentation and action visibility:
  `frontend/src/pages/asset/Assets.jsx`.
- Create-time exposure of every status and direct Custodian selection:
  `frontend/src/pages/asset/Create.jsx`.
- Edit-time status options, direct Custodian selection, and failure display:
  `frontend/src/pages/asset/Edit.jsx`.
- Asset detail, condition inspection, images/documents, aggregate history,
  barcode, and rejected `Assignment` label:
  `frontend/src/pages/asset/Detail.jsx`.
- Asset deletion confirmation:
  `frontend/src/pages/asset/Delete.jsx`.
- Frontend permission gates:
  `frontend/src/App.jsx`;
  `frontend/src/AuthContext.jsx`;
  `frontend/src/components/ProtectedRoute.jsx`.
- Absence of a frontend behavioral-test script:
  `frontend/package.json`.

### Unresolved Conflicts

1. **C2 — Resolved decision; implementation conformance gap**: stakeholder
   clarification accepts creation only as `Available` or `In Storage` without a
   Custodian and prohibits direct Custodian maintenance.
   `backend/assets/serializers.py` still applies lifecycle guards only to
   updates, while `frontend/src/pages/asset/Create.jsx` offers every status and
   direct Custodian selection. The accepted behavior is now clear, but current
   backend and frontend behavior do not conform.
2. **C3 — Rejected terminology remains visible**: `CONTEXT.md` rejects
   `Assignment` for the Checkout lifecycle, but
   `frontend/src/pages/asset/Detail.jsx` labels a section
   `Assignment & Warranty`. Canonical terminology requires correction or an
   explicit amendment to `CONTEXT.md`.
3. **Terminal matrix resolved; implementation conformance gaps remain**:
   stakeholder clarification accepts `Sold` and `Scrapped` only from
   `Available` or `In Storage`, accepts `Lost` from any nonterminal status, and
   requires atomic closure of open Checkout and Service Records plus rejection
   of Pending Transfers. `backend/assets/serializers.py` still permits
   `Sold`/`Scrapped` from lifecycle-managed statuses, and current terminal
   processing does not reject Pending Transfers.
4. **Department meaning resolved; implementation conformance gaps remain**:
   stakeholder clarification defines department as the current Custodian's
   department, empty whenever Custodian is empty, and retained with Custodian
   only for `Lost`. Current check-in and Service Record behavior retains
   department after clearing Custodian; direct Asset editing exposes department;
   and Transfer can accept an explicit target department.
   Evidence: `backend/assets/models.py`;
   `backend/assets/checkout.py`;
   `backend/assets/transfer.py`;
   `backend/assets/service.py`;
   `frontend/src/pages/asset/Create.jsx`;
   `frontend/src/pages/asset/Edit.jsx`.
5. **Named Role and visibility decision resolved; implementation conformance
   gap remains**: stakeholder clarification accepts global Asset read for
   Admin, IT Manager, IT Staff, HR, and Viewer with `asset_view`, but limits
   Employee to Assets where that Employee is Custodian. Current queries remain
   global for every `asset_view` holder.
   Evidence: `backend/core/permissions.py`;
   `backend/assets/views.py`;
   `backend/accounts/migrations/0002_seed_rbac_and_org.py`;
   `backend/accounts/tests.py::PrivacyAuthorizationTests`.
   B1 still owns Role administration and custom-Role policy.
6. **Asset identity and register contract**: current required/optional fields,
   unique identifiers, create defaults, numeric-versus-text tag format,
   search/filter behavior, barcode rules, and indefinite absence of
   Procurement have no stakeholder-confirmed contract.
   Evidence: `backend/assets/models.py`;
   `backend/assets/serializers.py`;
   `backend/assets/views.py`;
   `frontend/src/pages/asset/Create.jsx`.
7. **Deletion and history retention**: deleting an Asset currently cascades to
   operational and file metadata with no accepted retention, archival,
   recovery, or legal-hold rule.
   Evidence: `backend/assets/models.py`;
   `backend/assets/views.py`;
   `frontend/src/pages/asset/Delete.jsx`.
8. **File security and lifecycle**: extension allowlists and request-size limits
   exist, but content validation, malware scanning, authorization of media
   access, orphan cleanup, retention, and recovery are unspecified.
   Evidence: `backend/itams/settings.py`;
   `backend/assets/views.py`;
   `backend/assets/models.py`;
   `frontend/src/pages/asset/Detail.jsx`.
9. **Audit and notification decision resolved; terminal audit conformance gap
   remains**: stakeholder clarification requires an AuditLog record for every
   successful B2 mutation and an expanded terminal entry covering operator,
   status, Custodian, department, and all automatic lifecycle-record effects.
   B2 actions send no Notifications. Current Asset actions write AuditLog rows
   and send no direct notifications, but terminal updates currently record only
   a generic old/new Asset summary and omit the automatic record effects.
   Evidence: `backend/assets/views.py`;
   `backend/core/services.py`;
   `docs/research/itams-current-system-baseline.md`.
   B8 owns shared AuditLog storage, access, filtering, and retention.
10. **Frontend failure and accessibility behavior**: current forms display
    local and backend errors, but no frontend behavioral tests establish
    wording, recovery, responsiveness, or accessibility.
    Evidence: `frontend/package.json`;
    `frontend/src/pages/asset/Create.jsx`;
    `frontend/src/pages/asset/Edit.jsx`;
    `frontend/src/pages/asset/Detail.jsx`.

## Out of Scope *(mandatory)*

### Adjacent Baseline Ownership

- Authentication, permission administration, custom-Role policy, User
  directory, Departments, Locations, and non-Asset authorization policy: B1.
  This baseline owns the accepted named-Role behavior for Asset actions.
- Procurement workflow, Vendor, Category, Brand, Model, and Purchase Mode
  master behavior: B6.
- Checkout and check-in workflow details beyond the Asset/Custodian boundary:
  B3.
- Approval-gated Transfer workflow details beyond the Asset/Custodian boundary:
  B4.
- Service Record workflow details beyond the Asset/Custodian boundary and
  ADR-0001: B5.
- Warranty and AMC actions, contract history, and expiry alerts: B7.
- Generic Notification and AuditLog storage, delivery, access, and retention:
  B8.
- Dashboard, reports, exports, and the current "Asset Audit Report": B9.

### Explicitly Deferred Product Behavior

- Scheduled or periodic physical Asset audits by department or Location are
  deferred beyond v1. Reactive recording of `Lost` remains in scope.
- Employee self-service Checkout is possible future scope; current Checkout is
  performed by IT on an employee's behalf.
- Employee- or team-lead-initiated Procurement requests are intentionally
  deferred.

### Delivery Boundary

- This baseline does not redesign Asset behavior, resolve the listed
  stakeholder decisions, change code or tests, create a delivery plan, generate
  tasks or tickets, or authorize implementation work.
