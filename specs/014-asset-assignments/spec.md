# Feature Specification: Ongoing Asset Assignments and Temporary Checkout

**Feature Branch**: `codex/014-asset-assignments` (initial design); local delivery and review occurred on `codex/014-asset-assignments-delivery`.

**Created**: 2026-09-29

**Status**: Accepted scope — implemented and independently reviewed locally on 2026-10-08 (native run `95a02038` completed). Deployment, live operational use and manual acceptance remain unverified.

**Input**: Keep Checkout for temporarily assigning an Asset to an employee. Extend the Transfer module with separate ongoing Assign and Take Back actions. Users with `asset_custody_manage` perform Assign and Take Back immediately; employee-to-employee Transfer retains its request-and-approval process.

## Clarifications

### Session 2026-09-29

- Q: When an old Checkout names employee A but the Asset and an approved Transfer show employee B as current holder, how should IT classify it? → A: Block the action with a clear error until IT resolves the conflicting custody records. When the Asset is confirmed to be on a temporary Checkout held by another employee, explain that temporary custody in the error rather than allowing Assign or Transfer.
- Q: If IT takes back an Asset while an employee-to-employee Transfer request is Pending, what should happen to that request? → A: Take Back must fail with an error explaining that the Transfer request is not closed. IT must close the Pending Transfer before Take Back can proceed.
- Q: After classification is blocked because an old Checkout names A while the Asset and approved Transfer name B, how should IT resolve the records? → A: If verified approved Transfer history correctly moved custody from A to B, record an administrative reconciliation that ends A's stale Checkout as superseded by that Transfer, preserves the Checkout's original dates, and retains B as current Custodian. This is not a physical Check-in.

### Session 2026-10-08

- Q: When an Approved legacy Transfer's recorded date may have been overwritten and its original request time cannot be reliably recovered, what date basis should reconciliation show for a reconstructed current-holder arrangement? → A: Use the recorded historical Transfer date only as an administrative reconstruction marker labeled “Legacy Transfer event date (event type unverified).” Do not claim it is the request, approval, physical issue, handoff or return time. A verified approved holder chain remains sufficient; missing original request-time evidence does not block reconciliation.

## Specification Lineage *(mandatory)*

**Type**: Change

**Roadmap Reference**: Standalone change affecting B2 (Asset lifecycle), B3 (Checkout), B4 (Transfer), and B5 (Service Record) in `ROADMAP.md`.

**Extends**:
- `specs/001-asset-register-lifecycle-baseline/spec.md`
- `specs/005-checkout-checkin-baseline/spec.md`
- `specs/006-transfer-baseline/spec.md`
- `specs/007-service-record-baseline/spec.md`

**Supersedes**: The rule that every store-to-employee issue is a Checkout, the rejection of Assignment as a domain term, and the requirement that every post-service reissue must be a Checkout. Transfer approval, single custody, department derivation, Service Record clearing custody, and terminal accountability remain applicable.

**Extended by**: `specs/016-asset-procurement-lifecycle/spec.md` adds Procurement staging and deletion sequencing while preserving custody-history and protected-state rules.

**Reciprocal Links**: Add lineage metadata to predecessor records during this delivery; their accepted requirements remain unchanged. This specification uses the repository's durable feature convention under constitution 1.1.0. It does not authorize migration to a single living specification or deletion of feature history.

## Domain Alignment *(mandatory)*

**Canonical Terms**:
- **Asset** and **Custodian** retain their physical-item and current-holder meanings, including the Lost accountability exception.
- **Checkout** becomes a temporary loan from available stock, ending through **Check-in**.
- **Assignment** becomes ongoing employee custody, ending through **Take Back**, approved **Transfer**, or an applicable lifecycle interruption. Ongoing means until deliberately returned or reassigned; it does not transfer company ownership to the employee.
- **Assign** issues an available Asset for ongoing employee use.
- **Take Back** records physical receipt of an ongoing Assignment and clears employee custody.
- **Transfer** remains an approval-gated employee-to-employee handoff. The Transfer module also hosts Assign and Take Back; sharing a module does not give these direct actions a Pending approval stage.

**Relevant Decisions**:
- The stakeholder explicitly requested temporary Checkout and separate ongoing Assignment, and on 2026-09-29 confirmed immediate Assign/Take Back by `asset_custody_manage` while retaining Transfer approval.
- The stakeholder confirmed that IT classifies each existing open Checkout, temporary custody is checked in before reissue to another employee, and Take Back always sets `status = Available` while recording the actual return condition, including `Damaged` or `Repair Required`.
- At the initial 2026-09-29 design snapshot, `CONTEXT.md` said to avoid Assignment and defined Checkout as all initial issuance. The accepted narrow change has since been recorded there: Draft B4's 2026-08-04 “Store-to-User issuance ... Checkout” answer now applies only to temporary issuance, while ongoing issuance uses Assignment.
- ADR-0001 retains custody clearing when a Service Record opens and prohibits automatic reassignment on closing. Its original “fresh Checkout” wording was amended to a deliberate fresh Assign or Checkout according to intended use under the accepted narrow scope; the service rationale is retained.
- Status and condition remain independent. No new Asset status is proposed. Assigned Assets must visibly distinguish ongoing Assignment from temporary Checkout.

**Lifecycle and Actors**:

| Action | Actor permission | Starting state | Successful outcome |
| --- | --- | --- | --- |
| Assign | `asset_custody_manage` | Available, no active custody | Assigned; selected employee is Custodian; department follows employee |
| Checkout | `asset_custody_manage` | Available, no active custody | Assigned; temporary Checkout is identified; department follows employee |
| Check-in | `asset_custody_manage` | Current temporary Checkout | Checkout closes; Available; Custodian and department clear under existing B3 rules |
| Request Transfer | `transfer_request` | Eligible ongoing employee custody | Pending request; custody remains unchanged |
| Approve/reject Transfer | `asset_custody_manage` | Eligible Pending request | Approve changes custody and history together; reject leaves custody unchanged |
| Take Back | `asset_custody_manage` | Current ongoing Assignment physically received | Assignment closes; Custodian and department clear; Asset becomes Available with its actual recorded condition |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Assign an everyday work Asset (Priority: P1)

IT issues an employee's everyday laptop using Assign in the expanded Transfer module.

**Why this priority**: Ongoing custody needs a clear path separate from temporary lending.

**Independent Test**: Assign an Available Asset to an active employee and verify current custody and history without creating a temporary Checkout or approval request.

**Acceptance Scenarios**:
1. **AS-001**: Given an Available laptop without custody, when authorized IT assigns it to employee A, then it immediately becomes Assigned to A, its department matches A's department, and an ongoing Assignment identifies the Asset, employee, operator, issue time and issue condition.
2. **AS-002**: Given A has no department, when Assign succeeds, then the Asset department is empty rather than retaining a previous holder's department.
3. **AS-003**: Given an Asset already held by an employee, Under Repair, In Storage, or terminal, when Assign is attempted, then it fails without changing custody or creating a successful Assignment.
4. **AS-004**: Given a user lacks `asset_custody_manage`, when they attempt Assign or Take Back by any supported entry point, then authorization fails and all lifecycle records remain unchanged.

### User Story 2 - Take back an employee's Asset (Priority: P1)

IT receives an assigned Asset when the employee leaves or no longer needs it, records its actual condition, and ends their custody.

**Why this priority**: Offboarding must release accountability only after the actual return.

**Independent Test**: Take back an Asset from its current ongoing Assignment and verify closed history, actual condition and availability.

**Acceptance Scenarios**:
1. **AS-005**: Given A holds an ongoing Assignment and physically returns the Asset in Good condition, when IT records Take Back with that condition, then the Assignment closes, the Asset becomes Available, Custodian and department clear, and the return inspection and operator are retained.
2. **AS-006**: Given a returned Asset is worse than at issue, when remarks are absent, then Take Back fails; selecting the actual canonical condition and providing explanatory remarks permits the return. Preserve B3's New-to-Good exception to deterioration.
3. **AS-007**: Given an employee has left or their account is disabled but their Asset has not returned, when their account status changes, then custody remains recorded. IT can still take back a physically received Asset from a disabled former employee.
4. **AS-008**: Given an Assignment is closed or no longer identifies the current custody, when an old Take Back action is submitted, then it is rejected without clearing a later employee's custody.
5. **AS-018**: Given an Asset is physically taken back in `Damaged` or `Repair Required` condition, when IT records that condition and any required deterioration remarks, then the Asset becomes `Available`, its condition is the value IT selected, and its former Custodian and department clear. The condition must be visible to the next operator.
6. **AS-022**: Given the Asset has a Pending Transfer, when IT attempts Take Back, then the action fails with an error that the Transfer request is not closed. The Transfer, Assignment, Asset Custodian, department, status and condition remain unchanged. IT must reject or otherwise decide the request before retrying Take Back against the then-current Custodian.

### User Story 3 - Keep temporary lending recognizable (Priority: P1)

IT lends a spare Asset through Checkout and uses Check-in for its return.

**Why this priority**: Users must be able to choose the right action and recognize which return workflow applies.

**Independent Test**: Complete a temporary Checkout and Check-in, then compare its presentation and history with an ongoing Assignment.

**Acceptance Scenarios**:
1. **AS-009**: Given an Available spare Asset, when IT performs Checkout, then it shows temporary custody with the existing purpose and optional expected-return-date fields; it does not appear as an ongoing Assignment.
2. **AS-010**: Given a current temporary Checkout, when IT performs Check-in with the actual condition, then existing B3 return rules apply. Take Back cannot silently treat it as an ongoing Assignment.
3. **AS-011**: Given an ongoing Assignment, when a user views custody details, then the display identifies it as ongoing and offers Take Back to authorized IT; it does not describe it as an overdue temporary loan.
4. **AS-019**: Given A holds an open temporary Checkout, when Assign or Transfer to B is attempted, then the action fails without changing A's custody or creating a Pending Transfer. The error explains that the Asset is being temporarily held by another employee; IT must record Check-in before a new Checkout or Assign to B.

### User Story 4 - Transfer an ongoing Assignment safely (Priority: P1)

HR or IT requests a handoff from A to B and authorized IT approves or rejects it through the existing Transfer process.

**Why this priority**: A handoff must update both custody and its history consistently.

**Independent Test**: Request and approve a Transfer of A's ongoing Assignment to B; attempt to return A's prior custody afterward.

**Acceptance Scenarios**:
1. **AS-012**: Given A holds an ongoing Assignment, when a Transfer to B is requested, then A remains Custodian until approval. Approval records A's custody ending and B's ongoing custody beginning together with the Transfer.
2. **AS-013**: Given a Pending Transfer, when it is rejected, then the original Assignment and Asset custody remain unchanged.
3. **AS-014**: Given custody or department has changed since a Transfer request, when approval is attempted, then it is rejected without overwriting the current holder or history. Existing same-employee and single-Pending-request restrictions remain.
4. **AS-015**: Given an Asset has entered service or become Lost, when a stale Checkout, Assignment return, or Transfer action is attempted, then it cannot restore availability or replace the established service/terminal outcome.

### User Story 5 - Preserve existing custody during adoption (Priority: P1)

IT continues managing Assets issued before the distinction existed without losing who holds each Asset or inventing a physical return.

**Why this priority**: Existing Checkout records may represent either temporary or ongoing use.

**Independent Test**: Classify representative existing open Checkouts as temporary or ongoing, including a record whose employee differs from the Asset's current Custodian, and verify accountability and history are retained.

**Acceptance Scenarios**:
1. **AS-016**: Given an existing open Checkout that represents a temporary loan and matches the Asset's current holder, when IT classifies it as temporary, then it remains an open temporary Checkout with its original issue details and the Asset's current custody unchanged.
2. **AS-017**: Given an existing Checkout names A while the Asset names B, when ordinary classification is attempted, then it is blocked with an error identifying the conflicting custody records. No holder is silently overwritten and no physical return is fabricated. IT can use the separate administrative reconciliation in AS-023 if verified approved Transfer history establishes B's custody.
3. **AS-020**: Given an existing open Checkout that represents ongoing use and matches the Asset's current holder, when IT classifies it as ongoing, then an ongoing Assignment becomes the single active custody arrangement, the original Checkout issue facts remain traceable, and its prior open status ends as an administrative reclassification explicitly distinguished from a physical Check-in.
4. **AS-021**: Given an existing open Checkout has not yet been classified, when an action would return or transfer that Asset under the new model, then IT is prompted to classify and resolve it first; the unclassified record is not silently assumed temporary or ongoing.
5. **AS-023**: Given A's old Checkout remains Open, the Asset identifies B as Custodian, and verified approved Transfer history correctly moved custody from A to B, when authorized IT reconciles and classifies that Asset, then A's Checkout ends as superseded by the Transfer, its original issue and expected-return dates remain unchanged, no physical Check-in or actual return date is recorded, B remains Custodian with the same department and Asset status, and B's current custody is recorded as the single active temporary or ongoing arrangement selected by IT. The reconciliation identifies the operator, time, source Checkout and approved Transfer. If B's arrangement must be reconstructed, its copied historical Transfer date is labeled “Legacy Transfer event date (event type unverified),” not a proven request, approval, physical issue, handoff or return time; a missing original request timestamp does not invalidate the verified holder chain.
6. **AS-024**: Given no verified approved Transfer history establishes B as the current holder, when administrative reconciliation is attempted, then it is rejected without changing the Checkout, Asset or custody history; the discrepancy remains for authorized investigation.

### Edge Cases

- Two operators attempt competing Assign/Checkout/Transfer/return actions: at most one incompatible outcome succeeds; failure leaves no partial custody changes.
- A repeat Take Back or Check-in must not release a later Assignment.
- A Pending Transfer must never become approvable against changed or ended custody, including a later new issue to the same employee.
- Take Back is blocked while any Transfer request for that Asset remains Pending; deciding the request first prevents a stale Pending request from outliving the return.
- Disabled employees remain valid previous holders for return history but cannot receive a new issue; preserve existing identity rules.
- Service interrupts ongoing Assignment as well as temporary Checkout without pretending an ordinary return occurred. Closing service does not restore either custody automatically.
- Lost retains the last Custodian for accountability while ending active circulation; Sold/Scrapped eligibility remains unchanged.
- A temporary Checkout cannot be transferred directly to another employee; first Check-in, then a fresh Checkout or Assign according to the new purpose.
- A damaged Take Back makes the Asset Available with its actual condition visible; condition alone does not start a Service Record or make the Asset In Storage.
- Administrative reconciliation is a correction of historical custody records. It neither records a physical return nor changes the verified current Custodian.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The existing Transfer module MUST provide separate Assign, Transfer and Take Back actions with explanatory labels. Checkout MUST remain separately identifiable as temporary lending. “Assignments & Transfers” is the proposed module label.
- **FR-002**: Assign MUST directly issue an Available Asset without active custody to an active employee, recording an ongoing Assignment and its issue condition without a Pending approval stage. It MUST set Assigned, Custodian and the employee's department (or empty).
- **FR-003**: An Asset MUST have at most one active custody arrangement. Its current holder, custody type and current history MUST agree. Historical records MUST NOT release or replace later custody.
- **FR-004**: Take Back MUST require the current ongoing Assignment, physical receipt and no Pending Transfer for the Asset; close that Assignment, record the return operator/time and inspection, and clear Custodian and department. Every successful Take Back MUST make the Asset Available with its actual recorded condition. If a Transfer remains Pending, Take Back MUST fail with a clear “Transfer request is not closed” error without changing custody or either record.
- **FR-005**: Take Back MUST require explicit selection of actual return condition from New, Good, Average, Damaged and Repair Required, without preselecting a return condition. Deterioration MUST require remarks using the established B3 condition-order and New-to-Good exception.
- **FR-006**: Take Back with `Damaged` or `Repair Required` as the actual condition MUST set `status = Available` and retain that selected condition. The system MUST present both values clearly; Take Back MUST NOT silently change the status to In Storage or Under Repair. Starting service or moving an Asset to storage remains a separate deliberate action.
- **FR-007**: Checkout and Check-in MUST retain their existing permissions, condition, purpose, optional expected-return-date, inspection and notification rules while clearly representing temporary use. Ongoing Assignment MUST NOT acquire a temporary-loan due date or overdue classification.
- **FR-008**: Transfer of ongoing custody MUST retain the existing requester and approver permissions and Pending/Approved/Rejected process. Approval MUST end the previous custody and begin the target's ongoing custody atomically with Asset, department, condition and history updates. Rejection MUST leave custody unchanged.
- **FR-009**: An Asset on a temporary Checkout MUST NOT enter the employee-to-employee Transfer workflow or be directly Assigned to another employee. IT MUST Check-in the temporary Checkout before issuing the Asset to another employee through a new Checkout or Assign. A Pending Transfer for an Asset now under temporary custody MUST NOT be approved. A rejected attempt MUST explain that the Asset is temporarily held by another employee when that fact is confirmed.
- **FR-010**: IT MUST classify each existing open Checkout as temporary or ongoing according to its actual purpose. A temporary classification retains the open Checkout. An ongoing classification creates an active Assignment and ends the open Checkout as an administrative reclassification, visibly distinct from physical Check-in. Classification MUST preserve the original issue facts, operator and dates and record who classified it and when.
- **FR-011**: Adoption MUST preserve original issue/return/Transfer facts and links, MUST NOT invent a physical return, and MUST block ordinary classification of inconsistent legacy custody with an actionable error rather than silently choosing a holder. An Asset's legacy record MUST be classified before its first new return or Transfer action. Where the custody type is unconfirmed, the error MUST describe conflicting records rather than assert that the Asset is temporarily held. If verified approved Transfer history establishes that custody moved from the stale Checkout's employee to the Asset's current Custodian, authorized IT MUST be able to record an administrative reconciliation: end the stale Checkout as superseded by the approved Transfer, retain its original issue and expected-return dates, link that Transfer, and keep the Asset's current Custodian, department and status unchanged. The same reconciled action MUST classify the current Custodian's custody as temporary or ongoing according to IT's verified choice, with one active arrangement. If a current-holder arrangement is reconstructed from an Approved legacy Transfer, its copied recorded Transfer date MUST have the visible basis “Legacy Transfer event date (event type unverified)” and MUST NOT be presented as a proven request, approval, physical issue, handoff or return time. Unavailable original request-time evidence MUST NOT by itself reject an otherwise verified holder chain. Reconciliation MUST NOT set an actual physical return date, mark the action as Check-in, or claim a physical inspection. Without a verified Transfer basis, reconciliation MUST fail without mutation.
- **FR-012**: Existing service/terminal operations MUST account for ongoing Assignments and temporary Checkouts together. Service opening clears custody; service closing returns Available without automatic reissue; Lost retains last-custodian accountability; ended custody cannot later change the Asset through a stale return or approval.
- **FR-013**: Authorized readers MUST be able to distinguish current ongoing and temporary custody in the Asset's details and relevant custody lists/history, and see who issued, received, transferred or returned the Asset and when. Existing Transfer history and PDF access MUST continue to represent actual employee-to-employee Transfers correctly.
- **FR-014**: Existing Asset and custody reporting MUST retain accurate current status, holder and department. Assignment history MUST remain separate from temporary-loan reporting; no new report family is required.

### Authorization and Lifecycle Requirements

- **ALR-001**: Assign, Take Back, classification and administrative reconciliation of an existing open Checkout, Checkout and Check-in require `asset_custody_manage`. Transfer requests require `transfer_request`; decisions require `asset_custody_manage`. Preserve permission-based custom roles, Admin policy and existing read visibility; no employee self-service or role-name shortcut is introduced.
- **ALR-002**: Each custody mutation MUST succeed as one consistent operation across Asset, custody history, inspection where applicable and required audit record. Unauthorized, invalid, conflicting or stale actions MUST leave business state unchanged.
- **ALR-003**: Assignment issue, return, Transfer, interruption and administrative reconciliation history MUST identify Asset, affected employee(s), actor, time, reason/remarks where supplied, custody type, and old/new lifecycle values. Reconciliation MUST identify the superseded Checkout and approved Transfer and distinguish it from physical Check-in. Required audit follows B8; no generic edit/delete may bypass the approved lifecycle or erase custody accountability.
- **ALR-004**: On Assign, notify the receiving employee; on Take Back, notify the previous employee when their account is active. Preserve existing Transfer and Checkout notification rules. Notification delivery failure MUST NOT undo committed custody. Apply existing visibility restrictions and retain the return in history even when the former employee is disabled and receives no notification.
- **ALR-005**: Starting an ongoing Assignment from In Storage requires the existing explicit move to Available first. Procurement itself does not assign custody. Same-holder Transfer, unavailable/terminal target Assets and stale custody actions remain rejected.

### Key Entities

- **Asset**: Status, condition, current Custodian and derived department, with identifiable current custody type.
- **Ongoing Assignment**: One employee's continuous custody, including the issue condition and other issue facts, and its ending event (Take Back, Transfer or lifecycle interruption).
- **Temporary Checkout**: Temporary employee custody with issue facts, optional expected return, and Check-in or interruption history.
- **Transfer**: Approval-gated custody handoff, captured source/target, decision and associated custody history.
- **Return inspection**: Actual condition and remarks, inspector and time recorded when physical receipt occurs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 100% of accepted Assign and Take Back scenarios, authorized IT completes the action without a separate approval request and sees the correct holder, status and custody type on completion.
- **SC-002**: In 100% of accepted custody scenarios, the Asset has at most one active arrangement matching its current holder; every stale or unauthorized attempt leaves that arrangement unchanged.
- **SC-003**: An employee's everyday Asset and temporary spare are distinguishable in their custody records, with Take Back for the ongoing Asset and Check-in for the temporary spare.
- **SC-004**: In 100% of adoption acceptance examples, original issue facts remain traceable; reconciliation preserves the current Custodian and original Checkout dates, and no example fabricates a physical return or silently overwrites disputed custody.
- **SC-005**: Every successful ongoing return retains actual condition, operator and time; 100% of applicable deterioration attempts without remarks are rejected.

## Assumptions

- This is a change to the existing ITAMS application and permission model; no technology or authentication change is proposed.
- Existing accepted rules apply except where this change feature explicitly replaces them. Notification recipients are included in the accepted scope.
- The user confirmed direct-action permissions, approved entry into Clarify and the final scope decision separately, accepted the final clarified scope, and authorized this update's local delivery. The initial 2026-09-29 Clarify coverage scan and three material answers, plus the approved 2026-10-08 historical Transfer date-basis clarification, are recorded above. This authority grants no push, merge, deployment or release.
- At the initial design snapshot, the prior active pointer was `specs/013-procurement-invoice-attachment-change`; its files and unrelated working-tree changes were preserved. Initial revision: `5de8099386ea20c67be8612a3f608e1db244a3f6`. The “no native workflow run” observation applied only then; native run `95a02038` completed locally on 2026-10-08.
- At initial drafting, implementation review still needed to reconcile CONTEXT and ADR terminology and predecessor lineage; those changes and reciprocal links are now recorded. Initial code observations were evidence of the pre-implementation state, not intended behavior. Current implementation and verification evidence is in `issues/08-verify-and-converge.md`.

## Out of Scope *(mandatory)*

- Employee self-service, automatic return on account disabling, or automatic reissue after service.
- Procurement request/approval changes, employee ownership of company Assets, bulk issuance, signatures, or new handover-document formats.
- General Checkout editing or deletion as a custody-correction workflow.
- New Asset statuses, a second simultaneous custodian, or ownership retained by an employee while another person temporarily holds the same Asset.
- Unrelated procurement invoice work or other baseline conformance repairs, except gaps necessary for the custody integrity described here.
- Deployment, remote publication, push, release, or changes to the repository's constitution and artifact-persistence convention.
