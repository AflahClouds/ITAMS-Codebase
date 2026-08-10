# Feature Specification: Report Filtering and Export Parity

**Feature Branch**: `docs/baseline-spec-migration`

**Created**: 2026-08-10

**Status**: Draft

**Input**: User description: "Move the unimplemented report filters, written definitions, server-controlled export parity, typed data, branding, and non-truncating delivery out of the B9 AS-BUILT baseline into a flow-forward Change specification."

## Specification Lineage *(mandatory)*

**Type**: Change

**Roadmap Reference**: `ROADMAP.md`, change CHG-B9-01 under B9 — Dashboard, reports, and exports.

**Extends**: `specs/009-dashboard-reports-exports-baseline/spec.md`.

**Supersedes**: None. B9 remains the current-system evidence baseline; this record owns the prospective report and export behavior.

**Reciprocal Links**: B9 and `ROADMAP.md` link to this Change specification.

## Domain Alignment *(mandatory)*

**Canonical Terms**: Report labels and values use the canonical terms in `CONTEXT.md`, including **Asset**, **Checkout**, **Transfer**, **Service Record**, **Vendor**, **Warranty**, **AMC**, **Custodian**, **Sold**, **Scrapped**, and **Lost**. `Assignment` is rejected terminology. Operational AuditLog reporting is not a physical Asset audit.

**Relevant Decisions**: Stakeholder clarification recorded in Draft B9 on 2026-08-05 establishes standard filters, written metric definitions, server-controlled exports, format parity, typed values, branding, visible limiting, and a report response-time expectation. B1/B2–B8 own source data and visibility; B8 owns AuditLog access and auditing.

**Lifecycle and Actors**: This is read-only presentation behavior. It MUST NOT change Asset, custody, Procurement, Transfer, Service Record, Warranty, AMC, Notification, or AuditLog business state. Report and export access remains governed by source-record visibility and the B9 permission contract.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filter Reports Predictably (Priority: P1)

An authorized reader can narrow a report by date range, status, and department and can see exactly which filters produced the result.

**Why this priority**: Unfilterable reports force readers to export excess data and make it difficult to reproduce operational figures.

**Independent Test**: Apply each filter alone and in combination, compare the rows with source records, and verify the same filter description in every export.

**Acceptance Scenarios**:

1. **AS-001**: **Given** a report for which date range, status, and department are meaningful, **when** filters are applied, **then** only matching authorized rows are returned and every applied filter is displayed.
2. **AS-002**: **Given** a filter that has no meaning for a report, **when** it is requested, **then** the report identifies that filter as unsupported rather than silently ignoring it.
3. **AS-003**: **Given** an exported filtered result, **when** the file is opened, **then** it states the same applied filters as the on-screen result.
4. **AS-004**: **Given** a reader with scoped source-record visibility, **when** filters are applied, **then** filtering narrows only that reader's authorized records and never reveals global totals first.

---

### User Story 2 - Compare Equivalent Export Formats (Priority: P1)

An authorized reader can export PDF, Excel, or CSV and receive the same report data under the same authorization and audit boundary.

**Why this priority**: Different data or protection by format creates contradictory records and an authorization bypass.

**Independent Test**: Export one filtered report in all three formats and compare authorization, audit evidence, row set, column set, ordering, and filter metadata.

**Acceptance Scenarios**:

1. **AS-005**: **Given** one filtered report, **when** PDF, Excel, and CSV exports are produced, **then** all three contain identical rows and columns in the same order and state the same filters.
2. **AS-006**: **Given** an unauthorized requester, **when** any export format is requested, **then** it is refused and no report data is disclosed.
3. **AS-007**: **Given** an authorized export, **when** any format is produced, **then** the same required AuditLog event is created.
4. **AS-008**: **Given** Excel output, **when** a recipient sorts or calculates with date and numeric columns, **then** those cells behave as native dates and numbers.
5. **AS-009**: **Given** CSV output, **when** a recipient parses it, **then** dates use ISO 8601 text and numeric values use locale-independent numeric text without presentation symbols.

---

### User Story 3 - Receive Trustworthy Complete Output (Priority: P2)

A report reader can tell who produced the document, what it contains, and whether a limit affected the result.

**Why this priority**: Reports shared outside the application must be reproducible and must not silently omit data.

**Independent Test**: Generate branded and unbranded formats at below-limit and over-limit volumes and verify identity, completeness indicators, and performance.

**Acceptance Scenarios**:

1. **AS-010**: **Given** a configured organization name, **when** PDF or Excel is produced, **then** it identifies that organization; CSV remains deliberately unbranded.
2. **AS-011**: **Given** no configured organization name, **when** PDF or Excel is requested, **then** the configuration error is surfaced to an administrator rather than silently substituting a built-in name.
3. **AS-012**: **Given** a complete result, **when** it is displayed or exported, **then** it is identifiable as complete.
4. **AS-013**: **Given** an applied result limit, **when** the report is displayed or exported, **then** the limit and instructions for narrowing the filters are visible.
5. **AS-014**: **Given** the organization's supported data volume, **when** a report is run, **then** 95% of ordinary report requests complete within five seconds; a larger result paginates or streams rather than clipping rows.

### Edge Cases

- A zero-row result still displays filters, columns, completeness state, and export metadata.
- Date boundaries explicitly state whether their start and end are inclusive.
- Unknown filters and unsupported report/filter combinations are reported, not ignored.
- Values containing commas, quotes, line breaks, leading zeros, or spreadsheet-like formulas remain data rather than executable content.
- A report that reaches a configured safety limit remains exportable only with an explicit limited-result indicator or after narrower filters are applied.
- PDF may differ visually, but no format may differ in row selection, column meaning, authorization, audit, or filters.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every report MUST define its primary date and subject and MUST support the meaningful subset of date-range, status, and department filters.
- **FR-002**: Every applied filter MUST be displayed with the on-screen result and carried into every export.
- **FR-003**: An unsupported filter MUST be identified explicitly and MUST NOT be silently ignored.
- **FR-004**: Every metric, chart, band, report column, and filter MUST have a written definition covering row selection, terminal-Asset treatment, date basis, and boundary conditions before it is presented.
- **FR-005**: PDF, Excel, and CSV MUST be produced within the same protected server-controlled report operation.
- **FR-006**: All three formats for one report request MUST contain identical row sets and column sets in the same order and MUST state the same applied filters.
- **FR-007**: Excel MUST carry native date and numeric cells. CSV MUST use ISO 8601 date text and locale-independent numeric text. PDF MAY use display-formatted values.
- **FR-008**: PDF and Excel MUST identify the configured organization; CSV MUST remain unbranded.
- **FR-009**: Missing organization identity MUST be surfaced as a configuration error for branded formats rather than replaced silently.
- **FR-010**: A result MUST NOT be silently truncated. It MUST be identifiable as complete or identify the applied limit and how to narrow it.
- **FR-011**: At the supported organizational data volume, at least 95% of ordinary report requests MUST complete within five seconds; larger work MUST paginate or stream rather than clip rows.
- **FR-012**: The same result-definition, completeness, and filter metadata MUST appear on screen and in every export format.

### Authorization and Lifecycle Requirements *(include when applicable)*

- **ALR-001**: Every report and export MUST enforce source-record visibility and the B9 permission contract at the protected operation boundary; menu or button visibility is insufficient.
- **ALR-002**: Every successful export format MUST create the same B8-governed AuditLog event, including actor, report, format, filters, and outcome.
- **ALR-003**: Report generation MUST be read-only and MUST NOT mutate any source lifecycle, custody, financial, Notification, or AuditLog business record except the required export audit event.
- **ALR-004**: Spreadsheet-oriented output MUST prevent untrusted text from becoming an executable formula when opened by a recipient.

### Key Entities *(include if feature involves data)*

- **Report definition**: The stable meaning of one report, including source rows, columns, primary date, supported filters, boundary rules, and authorization.
- **Report request**: One authorized selection of a report and filters.
- **Export artifact**: A PDF, Excel, or CSV representation of the same report request and its metadata.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every supported filter combination, 100% of returned rows satisfy both the filter and the requester's source-record visibility.
- **SC-002**: PDF, Excel, and CSV comparisons show 100% parity in rows, columns, ordering, and filter metadata.
- **SC-003**: 100% of unauthorized export attempts disclose no report data, and 100% of successful exports create the required audit event.
- **SC-004**: 100% of limited results state the limit and narrowing guidance; 0 results are silently truncated.
- **SC-005**: Excel exposes 100% of designated date and numeric columns as native values, while CSV exposes them in the specified parseable text forms.
- **SC-006**: At the supported organizational data volume, at least 95% of ordinary report requests complete within five seconds.

## Assumptions

- Five seconds is the initial stakeholder-review target for ordinary report requests and may be revised during `$speckit-clarify` before planning.
- Each report will declare unsupported filters rather than receiving meaningless default behavior.
- B1 through B9, especially B8 and B9, must complete acceptance review before implementation planning for this Change begins.

## Out of Scope *(mandatory)*

- Changing source lifecycle rules, report-source permissions, or B8 AuditLog retention.
- The B4 Transfer custody PDF, which is not a B9 report export.
- New reports, dashboards, or business metrics beyond the B9 catalog.
- Emailing, externally publishing, or digitally signing exports.
- Physical Asset-audit reporting, which remains deferred.
