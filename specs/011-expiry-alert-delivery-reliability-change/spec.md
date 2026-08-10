# Feature Specification: Expiry Alert Delivery Reliability

**Feature Branch**: `docs/baseline-spec-migration`

**Created**: 2026-08-10

**Status**: Draft

**Input**: User description: "Move the unimplemented production scheduling, single-execution, timezone, deduplication, and downtime catch-up guarantees out of the B7 AS-BUILT baseline into a flow-forward Change specification."

## Specification Lineage *(mandatory)*

**Type**: Change

**Roadmap Reference**: `ROADMAP.md`, change CHG-B7-01 under B7 — Warranty, AMC, and expiry actions.

**Extends**: `specs/008-warranty-amc-baseline/spec.md`.

**Supersedes**: None. B7 remains the current-system evidence baseline; this record owns the prospective delivery guarantees.

**Reciprocal Links**: B7 and `ROADMAP.md` link to this Change specification.

## Domain Alignment *(mandatory)*

**Canonical Terms**: Use **Warranty**, **AMC**, **Incomplete**, **Active**, **Ended**, **Renew**, **End Support**, and **Notification**. Warranty and AMC remain distinct from Asset status and Service Record.

**Relevant Decisions**: `CONTEXT.md`, **AMC**, requires proactive 30/15/7-day alerts for Warranty and AMC. Stakeholder clarification recorded in Draft B7 on 2026-08-05 establishes production execution, one organizational timezone, once-only delivery, downtime catch-up, and operator-visible failures. B8 owns shared Notification delivery behavior.

**Lifecycle and Actors**: IT Manager and IT Staff receive expiry alerts. Alert evaluation does not renew or end coverage, change Asset lifecycle state, or mutate Warranty/AMC dates.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receive Alerts in Production (Priority: P1)

IT Manager and IT Staff receive the existing 30/15/7-day Warranty and AMC alerts under the organization's normal production deployment.

**Why this priority**: An alert rule that runs only in a development environment does not protect expiring coverage.

**Independent Test**: Run a production-equivalent deployment with eligible Warranty and AMC dates and verify one logical daily evaluation and the expected recipients.

**Acceptance Scenarios**:

1. **AS-001**: **Given** an eligible Warranty or `Active` AMC at a 30-, 15-, or 7-day threshold, **when** the scheduled evaluation runs under normal production operation, **then** the required in-app alerts are requested for IT Manager and IT Staff.
2. **AS-002**: **Given** several application workers or hosts, **when** one scheduled time arrives, **then** the organization observes one logical evaluation rather than one evaluation per worker.
3. **AS-003**: **Given** the production process responsible for evaluation is stopped or stalled, **when** its expected run is missed, **then** an operator can identify the overdue or failed run without inspecting application source code.

---

### User Story 2 - Evaluate Dates Consistently (Priority: P1)

Every alert date is determined by one organizational calendar rather than the locale of whichever server executes the check.

**Why this priority**: Recipients must not receive an alert a day early, late, or inconsistently across hosts.

**Independent Test**: Execute the same coverage dates from hosts with different local timezone settings and verify identical threshold results.

**Acceptance Scenarios**:

1. **AS-004**: **Given** hosts with different local timezones, **when** they evaluate the same coverage, **then** threshold eligibility is identical because the configured organizational timezone is used.
2. **AS-005**: **Given** a coverage end date exactly 30, 15, or 7 organizational calendar days away, **when** evaluation runs, **then** that threshold is eligible exactly once.

---

### User Story 3 - Recover Without Duplicates (Priority: P1)

The organization can repeat or recover an evaluation without spamming recipients or permanently losing alerts crossed during downtime.

**Why this priority**: Safe retry and catch-up are both necessary for operationally reliable alerts.

**Independent Test**: Repeat one evaluation, then simulate downtime across multiple thresholds and verify once-only catch-up.

**Acceptance Scenarios**:

1. **AS-006**: **Given** an alert already issued for one Asset, coverage type, coverage period, and threshold, **when** evaluation repeats, **then** no duplicate recipient alert is created.
2. **AS-007**: **Given** downtime spanning one or more 30/15/7-day thresholds, **when** the next successful evaluation runs before or after expiry, **then** every missed threshold is evaluated and each required alert is issued at most once.
3. **AS-008**: **Given** catch-up and a concurrent ordinary evaluation, **when** both attempt the same threshold, **then** recipients still receive at most one alert for that threshold.

### Edge Cases

- Changing a coverage end date creates a new coverage period whose thresholds may alert independently of the prior period.
- `Ended` AMC and absent coverage remain ineligible even during catch-up.
- An `Incomplete` AMC with no end date cannot reach an expiry threshold.
- Downtime lasting beyond the coverage end still produces operator-visible catch-up results rather than silently discarding crossed thresholds.
- Partial recipient-delivery failure follows B8 retry behavior without repeating already-retained recipient alerts.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Warranty/AMC expiry evaluation MUST run daily under the organization's normal production operation and MUST NOT depend on a development-only command.
- **FR-002**: Each scheduled time MUST result in exactly one logical evaluation across all active workers and hosts.
- **FR-003**: Threshold eligibility MUST use one configured organizational timezone independent of host locale.
- **FR-004**: The existing 30-, 15-, and 7-day thresholds and B7 eligibility rules MUST remain unchanged.
- **FR-005**: Each Asset, coverage type, coverage period, and threshold combination MUST be retained as issued at most once so repeated or overlapping evaluations are no-ops for that combination.
- **FR-006**: After downtime, the next successful evaluation MUST examine every threshold crossed since the last successful evaluation and request each missed eligible alert at most once.
- **FR-007**: A failed, stalled, or overdue evaluation MUST be visible to an operator with its last successful time and current failure or overdue condition.
- **FR-008**: Evaluation MUST record enough outcome information for an operator to distinguish success, failure, catch-up, and a successful run with no eligible alerts.

### Authorization and Lifecycle Requirements *(include when applicable)*

- **ALR-001**: Expiry evaluation MUST NOT change Asset status, Custodian, department, Warranty dates, AMC dates, or AMC state.
- **ALR-002**: Alert recipients MUST remain the B7-defined active IT Manager and IT Staff Users; shared delivery and retry remain owned by B8.
- **ALR-003**: Operational evaluation status MUST be restricted to authorized administrative operators and MUST NOT expose Notification content beyond the recipient rules.

### Key Entities *(include if feature involves data)*

- **Coverage period**: One Warranty or AMC interval whose end date drives thresholds.
- **Alert issuance**: The once-only record of one Asset, coverage type, coverage period, and threshold being requested for delivery.
- **Evaluation run**: One logical daily or catch-up evaluation with timing, outcome, and operator-visible health.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of scheduled production times create exactly one logical evaluation regardless of worker or host count.
- **SC-002**: Hosts with different local timezone settings produce identical threshold eligibility for 100% of the same coverage examples.
- **SC-003**: Repeated and overlapping evaluations produce 0 duplicate alerts for the same Asset, coverage type, coverage period, threshold, and recipient.
- **SC-004**: 100% of eligible thresholds crossed during simulated downtime are issued on the next successful evaluation, and no crossed threshold is issued more than once.
- **SC-005**: 100% of failed or overdue evaluations are visible to an authorized operator with the last successful evaluation time.

## Assumptions

- One organizational timezone is configured before this Change is enabled.
- A renewed AMC is a new coverage period and may legitimately issue a fresh set of thresholds.
- B7 and B8 must complete acceptance review before implementation planning for this Change begins.

## Out of Scope *(mandatory)*

- Changing 30/15/7-day threshold values or recipient Roles.
- Email, SMS, or other external delivery channels.
- Warranty renewal or End Support behavior.
- Service Record and Checkout overdue evaluation.
- Selecting a particular scheduling or mutual-exclusion technology; that belongs in `plan.md`.
