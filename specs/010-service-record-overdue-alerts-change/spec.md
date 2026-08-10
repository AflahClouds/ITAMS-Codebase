# Feature Specification: Service Record Overdue Alerts

**Feature Branch**: `docs/baseline-spec-migration`

**Created**: 2026-08-10

**Status**: Draft

**Input**: User description: "Move the unimplemented Service Record expected-return validation, overdue visibility, and proactive operator notification out of the B5 AS-BUILT baseline into a flow-forward Change specification."

## Specification Lineage *(mandatory)*

**Type**: Change

**Roadmap Reference**: `ROADMAP.md`, change CHG-B5-01 under B5 — Service Record lifecycle.

**Extends**: `specs/007-service-record-baseline/spec.md`.

**Supersedes**: None. B5 remains the current-system evidence baseline; this record owns the prospective behavior.

**Reciprocal Links**: B5 and `ROADMAP.md` link to this Change specification.

## Domain Alignment *(mandatory)*

**Canonical Terms**: Use **Service Record**, **Asset**, **Vendor**, **Open**, **Closed**, and **Overdue**. `Overdue` is a derived alert condition; it is neither an Asset status nor a Service Record state. `Assignment` remains rejected terminology.

**Relevant Decisions**: `CONTEXT.md`, **Service Record**, establishes the repair event and its dates. Stakeholder clarification recorded in Draft B5 on 2026-08-05 establishes optional expected return, validation, derived overdue behavior, and operator notification. B8 owns shared in-app Notification delivery.

**Lifecycle and Actors**: An authorized custody operator records the expected return. Every active User whose Role grants `asset_custody_manage` receives the overdue alert. Becoming overdue does not change Asset status, Service Record state, Custodian, department, or eligibility for closure.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record a Credible Expected Return (Priority: P1)

An operator can record when the Vendor expects to return the Asset without creating an impossible date sequence.

**Why this priority**: Overdue reporting is meaningful only when the expected return is valid relative to the repair's sent date.

**Independent Test**: Open or update a Service Record with valid, absent, and invalid expected-return dates and verify the accepted value or atomic rejection.

**Acceptance Scenarios**:

1. **AS-001**: **Given** an `Open` Service Record, **when** no expected return is supplied, **then** the record remains valid and never becomes overdue solely because time passes.
2. **AS-002**: **Given** a sent date, **when** an expected return on or after that date is supplied, **then** it is retained and readable.
3. **AS-003**: **Given** a sent date, **when** an earlier expected return is supplied, **then** the operation is rejected and neither the Service Record nor Asset changes.

---

### User Story 2 - Identify Overdue Repairs (Priority: P1)

Custody operators can identify an Asset that has not returned by the Vendor's expected date without confusing that signal with lifecycle state.

**Why this priority**: Operators need an actionable late-return queue while the canonical Asset and Service Record lifecycles remain stable.

**Independent Test**: Advance the organizational date past an expected return and verify that only an open record is presented as overdue.

**Acceptance Scenarios**:

1. **AS-004**: **Given** an `Open` Service Record whose expected return has passed, **when** it is listed or read, **then** it is identifiable as overdue.
2. **AS-005**: **Given** that same record after closure, **when** it is read, **then** it is no longer overdue.
3. **AS-006**: **Given** an overdue record, **when** another valid operation including closure is attempted, **then** overdue alone does not block it.
4. **AS-007**: **Given** any overdue record, **when** its Asset and Service Record are read, **then** `Overdue` appears as neither an Asset status nor an `Open`/`Closed` replacement.

---

### User Story 3 - Notify Custody Operators (Priority: P1)

Custody operators receive an in-app warning that the Asset is late back from the Vendor without first opening a report or record.

**Why this priority**: Merely displaying overdue state does not satisfy the stakeholder's proactive follow-up intent.

**Independent Test**: Let one record cross its expected return and verify recipient selection, once-only delivery, destination, and failure isolation.

**Acceptance Scenarios**:

1. **AS-008**: **Given** an open record crossing into overdue, **when** the next daily overdue evaluation completes, **then** every active `asset_custody_manage` holder receives one in-app Notification identifying the Asset and linking to the Service Record surface.
2. **AS-009**: **Given** a record already alerted for its current expected return, **when** evaluation repeats, **then** no duplicate Notification is created.
3. **AS-010**: **Given** Notification delivery fails, **when** overdue evaluation completes, **then** the Service Record remains unchanged and B8 retry and operator-visibility rules apply.

### Edge Cases

- Changing the expected return to a later date ends the current overdue episode; crossing the revised date may create one new alert.
- Closing a record during overdue evaluation leaves it closed and not overdue.
- Deactivated Users and Users without `asset_custody_manage` receive no new alert.
- Multiple open Service Records for one Asset remain an upstream lifecycle-integrity concern; each valid open record is evaluated independently.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Expected return MUST be optional and, when supplied, MUST be on or after the Service Record's sent date.
- **FR-002**: Invalid expected-return input MUST be rejected without mutating the Service Record or Asset.
- **FR-003**: A Service Record MUST be overdue exactly when it is `Open`, has an expected return, and that date has passed in the organizational timezone.
- **FR-004**: Overdue MUST be derived rather than stored as an Asset status or Service Record state and MUST disappear on closure or when the expected return is no longer past.
- **FR-005**: Overdue alone MUST NOT block closure or any otherwise-valid operation.
- **FR-006**: Service Record list and detail surfaces MUST make overdue records identifiable.
- **FR-007**: The next daily evaluation after a record becomes overdue MUST request one in-app Notification for every active `asset_custody_manage` holder.
- **FR-008**: The same record and expected-return episode MUST NOT create duplicate overdue Notifications on repeated evaluation.
- **FR-009**: An overdue Notification MUST identify the Asset, explain that it is late back from the Vendor, and link to the relevant Service Record surface.

### Authorization and Lifecycle Requirements *(include when applicable)*

- **ALR-001**: Recording or correcting expected return MUST require the same protected Service Record operation established by B5; frontend visibility alone is insufficient authorization.
- **ALR-002**: Overdue evaluation and Notification failure MUST NOT change Asset status, Custodian, department, Service Record state, or dates.
- **ALR-003**: B8 MUST own Notification persistence, retry, recipient read state, and failure visibility; this Change owns the overdue trigger and recipient rule.

### Key Entities *(include if feature involves data)*

- **Service Record**: The repair event containing sent date, optional expected return, state, and returned date.
- **Overdue episode**: The derived interval during which one open Service Record is past its current expected return.
- **Notification**: The B8-owned in-app recipient record requested once for each active custody operator per overdue episode.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of expected-return dates earlier than their sent date are rejected without Service Record or Asset mutation.
- **SC-002**: 100% of open records past a supplied expected return are identifiable as overdue; 0% of closed records are overdue.
- **SC-003**: 100% of active `asset_custody_manage` holders receive one overdue Notification by the next successful daily evaluation, with 0 duplicate Notifications for repeated evaluation of the same episode.
- **SC-004**: 0 overdue evaluations alter Asset lifecycle state, custody, department, or Service Record state.

## Assumptions

- The organization uses one configured timezone shared with other scheduled operational checks.
- A daily evaluation is sufficient for the date-granularity expected return recorded by B5.
- B5 and B8 must complete acceptance review before implementation planning for this Change begins.

## Out of Scope *(mandatory)*

- Changing the canonical Asset or Service Record state machines.
- Escalation by email, SMS, or external messaging.
- Vendor-facing reminders or employee self-service.
- Checkout overdue behavior, which remains owned by B3 or a separate B3 Change specification.
- Other B5 gaps involving operator-supplied sent/return dates, bill documents, outcomes, or opening/closing remarks.
