# Feature Specification: AS-BUILT Dashboard, Reports, and Exports Baseline

**Feature Branch**: `docs/baseline-spec-migration`

**Created**: 2026-08-05

**Status**: Draft

**Input**: User description: "Create an AS-BUILT Brownfield Baseline
specification for ROADMAP.md entry B9: Dashboard, reports, and exports. Cover
current KPI and chart definitions, report catalog, columns, filters, access
scope, Lost Asset reporting, AuditLog report terminology, PDF/Excel/CSV formats,
Transfer-export boundary, and company branding. Most behavior is
implementation-only. Keep calculation definitions, global versus scoped
visibility, export parity, branding, performance expectations, and the meaning
of Asset Audit Report unresolved. Exclude periodic physical Asset auditing and
lifecycle rules owned by B2 through B7. Do not modify application code."

## Clarifications

### Session 2026-08-05

- Q: What access and data scope apply to the Dashboard and to reports? → A: The Dashboard requires `asset_view` and is scoped to the reader's B1 Asset visibility, so an Employee sees only their own held Assets and no cross-User activity lists; reports keep `report_access` and stay global for the Roles holding it; and no aggregate may summarize records the reader could not read individually.
- Q: What should happen to the "Asset Audit Report" — its name, and who may read it? → A: Retitle it to name operational event history rather than Asset verification, govern its access by Draft B8 FR-016 so only Admin and IT Manager reach it, audit every view and export, treat source IP as protected B8 data, and reserve the "Asset Audit" name for the deferred F1 physical-verification capability.
- Q: What default semantics and filtering should Dashboard metrics and reports use? → A: Terminal-Asset and expiry-band semantics remain stakeholder intent for B9 review. The unimplemented standard filter set and filter metadata are retained in `specs/012-report-filter-export-parity-change/`, not as B9 AS-BUILT requirements.
- Q: What parity and branding rules apply across PDF, Excel, and CSV exports? → A: The stakeholder-selected protected export parity, parseable values, and branding corrections are retained in `specs/012-report-filter-export-parity-change/`, not as B9 AS-BUILT requirements.
- Q: What volume, performance, and truncation expectations apply to reports? → A: The stakeholder-selected visible limiting and response-time behavior is retained in `specs/012-report-filter-export-parity-change/`, not as B9 AS-BUILT requirements.

## Specification Lineage *(mandatory)*

**Type**: Brownfield Baseline

**Roadmap Reference**: `ROADMAP.md`, entry B9 — Dashboard, reports, and exports;
durable feature directory `specs/009-dashboard-reports-exports-baseline/`.

**Extends**: None. This is the initial B9 baseline.

**Supersedes**: None.

**Extended by**: `specs/012-report-filter-export-parity-change/spec.md` owns the
prospective standard filters, written definitions, protected export parity,
parseable values, branding correction, and non-truncating delivery behavior.

**Reciprocal Links**: `ROADMAP.md` already reserves
`specs/009-dashboard-reports-exports-baseline/` for B9 and must link the created
directory when the B9 row moves to `R3 — draft review`. After this Draft is
accepted, any later substantive change must use a new feature directory and
record reciprocal `Extends`, `Supersedes`, or `Superseded by` lineage instead of
editing accepted requirement content here.

**Dependencies**: B9 is the terminal consumer in the roadmap and depends on
every source baseline for the meaning of the data it presents.

- Draft B2 Asset register and lifecycle baseline
  (`specs/001-asset-register-lifecycle-baseline/`, Draft; acceptance review pending) for
  Asset identity, canonical statuses and conditions, terminology, terminal
  states, and Employee data visibility.
- Draft B1 identity and access baseline for Roles, permission codes, and the
  data-visibility model every B9 surface must honor.
- Draft B3 Checkout, B4 Transfer, B5 Service Record, B6 Procurement/Vendor, and
  B7 Warranty/AMC baselines for the business meaning of every metric, column,
  and status B9 displays. B9 defines no lifecycle rule of its own.
- Draft B8 Notifications and AuditLog baseline for AuditLog access, audit of
  views and exports, value minimization, and retention — which govern the
  current report that exposes AuditLog content.

**Evidence Status**: `ROADMAP.md` classifies B9 as **E3 —
implementation-led**: one AMC report edge case is test-backed and essentially
every calculation, column, access rule, presentation choice, and export format
exists only in implementation. This Draft therefore carries a large body of
classified evidence. The stakeholder clarification dated 2026-08-05 converted
the six open decisions into governing rules, so the accepted requirement set is
substantially larger than the evidence base that preceded it — every accepted
requirement beyond that clarification still traces to `CONTEXT.md` or a
dependency baseline.

## Domain Alignment *(mandatory)*

**Canonical Terms**:

- **Dashboard** is the read-only operational summary surface: KPI tiles, expiry
  breakdowns, distribution and trend charts, and short recent-activity lists.
- **Report** is one server-defined tabular output identified by a stable key,
  with a fixed title, a fixed column set, and no user-supplied parameters in the
  current system.
- **Report catalog** is the enumerable list of those reports.
- **Export** is a downloadable rendering of a report: server-generated PDF or
  Excel, or a browser-generated CSV.
- **Transfer document** is the per-Transfer custody PDF owned by B4. It is not a
  report and not part of the B9 export catalog.
- **AuditLog** is the operational event record owned by B8. **Audit Trail** is
  the administrative surface that displays it.
- **Physical Asset audit** is periodic physical verification of Assets against
  system records. It is deferred beyond v1 and MUST NOT be conflated with
  AuditLog, the Audit Trail, or any report whose title contains "Audit".
- **Lost Asset reporting** lists Assets in the terminal `Lost` status together
  with the Custodian retained for accountability. It is reactive reporting, not
  physical verification.
- Every Asset status, condition, and lifecycle term B9 displays is owned by its
  source baseline. B9 MUST use `Sold` rather than `Disposed`, `Checkout` rather
  than `Assignment`, and `Custodian` rather than `Owner`.

**Relevant Decisions**:

- `CONTEXT.md`, **Vendor**: Vendor is first-class so that vendor-grouped
  reporting — explicitly "which vendor has pending repairs" — is reliable. This
  is the only report whose business purpose is stated in an authoritative
  source.
- `CONTEXT.md`, **Lost**: `Lost` is recorded reactively, there is no periodic
  physical audit process, and the Custodian is retained to record who was
  accountable. Scheduled or periodic physical Asset audits are deferred beyond
  v1 (`ROADMAP.md`, F1).
- `CONTEXT.md`, **AMC**: expiry alerts are proactively pushed "not just visible
  on a dashboard someone has to check". A Dashboard panel therefore MUST NOT be
  presented as satisfying any alerting obligation; Draft B7 FR-017 states the
  same rule from the owning side.
- Draft B2 FR-004: user-visible terminology MUST use `Sold`, `Checkout`, and
  the canonical status and condition sets.
- Draft B2 FR-008 and FR-009: terminal Assets have left circulation, and
  `Lost` retains its Custodian and department for accountability.
- Draft B2 ALR-009: an active Employee with `asset_view` is limited to Assets
  where that Employee is Custodian. Any B9 surface that shows Asset data to an
  Employee is bound by that scope.
- Draft B8 FR-016: Admin and IT Manager have AuditLog view, filter, and export
  access; every other named or custom Role is denied; `report_access` alone MUST
  NOT grant any AuditLog data or export; and direct Audit Trail **and
  report/export surfaces** MUST enforce the same policy.
- Draft B8 FR-014 and FR-015: every AuditLog view or export MUST create an
  AuditLog entry, and entries MUST NOT expose unnecessary personal data; source
  IP is protected B8 data.
- Draft B4 FR-015: the Transfer PDF requires `asset_view` and B1 Transfer-record
  visibility. It is B4's custody document, not a B9 report export.
- Draft B5, B6, and B7 own the business meaning of service, procurement, and
  coverage data that B9 reports display.
- `ROADMAP.md` B9 review status listed six open decisions — calculation
  definitions, global versus scoped visibility, export parity, branding,
  performance expectations, and the meaning of "Asset Audit Report". The
  stakeholder clarification dated 2026-08-05 resolves all six as U-001 through
  U-006.

**Evidence Classification**:

- **Accepted intent** comes only from `CONTEXT.md`, an accepted dependency
  baseline, or an explicit recorded stakeholder decision. No ADR governs B9.
- **Test-backed current behavior** is reproducible current-system evidence. Only
  one B9 behavior has a dedicated test.
- **Implementation-only observation** is visible in backend code or a frontend
  surface without a dedicated behavioral test and remains unaccepted. This is
  the majority of B9.
- **Unresolved** means this Draft deliberately does not choose a rule and
  records the decision for stakeholder clarification.

**Lifecycle and Actors**:

| Stage | Actor and permission | Accepted or evidenced effect |
| --- | --- | --- |
| Open the Dashboard | Currently any authenticated active User; no permission code is required | Global KPI counts, portfolio value, expiry breakdowns, seven charts, and recent-activity lists covering every Asset and User |
| List the report catalog | `report_access` | The ten server-defined report keys and titles |
| Run a report | `report_access` | The full row set for that report with no parameters and no pagination |
| Export a report as PDF or Excel | `report_access` | A branded server-generated file, recorded in the AuditLog |
| Export a report as CSV | Whoever can already see the rendered report | A browser-generated file with no branding and no audit record |
| View the Audit Trail surface | Admin only | The AuditLog administrative view owned by B8 |
| Run the "Asset Audit Report" | `report_access` | The same AuditLog content, including source IP, through the report catalog |

The last two rows disagree with each other and with Draft B8 FR-016. That
disagreement is the single most significant finding in this baseline and is
recorded as U-006 rather than resolved here.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — See a Trustworthy Operational Summary (Priority: P1)

An authorized User opens the Dashboard and sees counts, values, and trends whose
definitions they can rely on when making decisions.

**Why this priority**: A summary that is wrong or ambiguous is worse than none,
because it is acted on without being questioned. Every tile is currently an
undocumented calculation.

**Independent Test**: For a fixture with Assets in every canonical status, open
the Dashboard and confirm each KPI and chart matches its documented definition.

**Acceptance Scenarios**:

1. **AS-001 — Accepted intent (`CONTEXT.md`, AMC; Draft B7 FR-017)**: **Given**
   coverage expiring within a threshold, **When** the Dashboard displays it,
   **Then** that display MUST NOT be treated as satisfying any alerting
   obligation; proactive delivery remains owned by B7.
2. **AS-002 — Draft B2 dependency**: **Given** any Dashboard label or value,
   **When** it is presented, **Then** it uses canonical terminology and the
   canonical status and condition sets.
3. **AS-003 — Draft B2 dependency**: **Given** a metric that describes Assets
   in circulation, **When** it is calculated, **Then** its treatment of terminal
   Assets is stated explicitly rather than left to the reader.
4. **AS-021 — Stakeholder-confirmed**: **Given** Assets in `Sold`, `Scrapped`,
   or `Lost`, **When** any metric, chart, or report is produced, **Then** they
   are excluded by default, and total value covers only Assets still held.
   **Given** a surface whose purpose is terminal, **Then** it includes them and
   says so on the surface.
5. **AS-022 — Stakeholder-confirmed**: **Given** coverage expiring in three
   days, **When** the expiry bands are produced, **Then** it appears in exactly
   one band, and the boundary rule is stated on the surface.
6. **FWD-AS-001 — Prospective Change scenario, not B9 baseline acceptance**: **Given** any presented figure, **When**
   a reader asks what it counts, **Then** a written definition exists covering
   row selection, terminal-Asset treatment, date basis, and boundaries.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-001 — Implementation-only**: **Given** any authenticated User,
   **When** the Dashboard is requested, **Then** global figures covering every
   Asset, Checkout, Transfer, and Service Record are returned, because the
   Dashboard and chart endpoints require authentication only and carry no
   permission code or data scope.
2. **OBS-AS-002 — Implementation-only conformance gap (FR-017)**: **Given** the
   total-value tile, **When** it is calculated, **Then** it sums the purchase
   cost of every Asset including `Sold`, `Scrapped`, and `Lost` ones, so it does
   not describe the value of Assets the organization still holds.
3. **OBS-AS-003 — Implementation-only conformance gap (FR-018)**: **Given** the
   expiry breakdown tiles, **When** they are calculated, **Then** "expired"
   counts end dates strictly before today while each threshold counts end dates
   from today through today plus 7, 15, or 30 days inclusive, so the threshold
   buckets are cumulative rather than disjoint and each wider bucket contains
   the narrower ones.
4. **OBS-AS-004 — Implementation-only**: **Given** the recent-activity lists,
   **When** they are returned, **Then** they contain the five newest Transfers,
   the five newest open Checkouts, and the five soonest-expiring Warranties,
   each including the names of the Users involved, to any authenticated caller.
5. **OBS-AS-005 — Implementation-only**: **Given** the seven chart endpoints,
   **When** they are calculated, **Then** category distribution omits categories
   with no Assets while department distribution includes departments with none,
   status distribution includes terminal statuses, both timeline charts bucket
   by days remaining, the purchase trend sums Asset purchase cost by the linked
   Procurement's purchase date over twelve months, and the transfer trend counts
   Approved Transfers by a date field that Draft B4 records as being overwritten
   with the approval time.
6. **OBS-AS-006 — Implementation-only**: **Given** an unknown chart name,
   **When** it is requested, **Then** the response reports that the chart is
   unknown.
7. **OBS-AS-007 — Implementation-only**: **Given** the "active" KPI, **When** it
   is calculated, **Then** it counts only `Available` and `Assigned` Assets,
   excluding `In Storage` and `Under Repair`, and no current surface displays
   it.

---

### User Story 2 — Run a Defined Report from the Catalog (Priority: P1)

An authorized User picks a report by name and receives a table whose columns and
row-selection rules mean what the name implies.

**Why this priority**: The catalog is the primary way operational data leaves
the system. Column meaning and row selection determine whether the output can be
relied on for decisions or audits.

**Independent Test**: Run each of the ten reports against a fixture covering
every lifecycle state and confirm the rows selected and columns produced match
their documented definitions.

**Acceptance Scenarios**:

1. **AS-004 — Accepted intent (`CONTEXT.md`, Vendor)**: **Given** Service Record
   activity across several Vendors, **When** Vendor-grouped reporting is
   produced, **Then** records group reliably by managed Vendor identity so that
   questions such as "which vendor has pending repairs" can be answered.
2. **AS-005 — Draft B2 dependency**: **Given** any report column that names a
   lifecycle concept, **When** it is labelled, **Then** it uses the canonical
   term owned by the source baseline rather than a synonym.
3. **AS-006 — Accepted dependency**: **Given** a report that presents data owned
   by B3 through B7, **When** its values are produced, **Then** they reflect
   that baseline's accepted meaning and B9 introduces no competing definition.
4. **FWD-AS-002 — Prospective Change scenario, not B9 baseline acceptance**: **Given** a report, **When** a date
   range, status, or department filter is applied, **Then** the rows narrow
   accordingly, the applied filters are shown with the result, and the same
   filters appear in every export of that result. **Given** a filter that is
   meaningless for that report, **Then** the report says so rather than ignoring
   it silently.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-008 — Implementation-only**: **Given** the catalog, **When** it is
   listed, **Then** it contains exactly ten reports with fixed keys and titles:
   Asset Register, Asset Movement, Warranty Expiry, Purchase, Employee Asset,
   Asset Audit, Assets Currently In Service, Vendor Service, AMC Expiry, and
   Lost Assets.
2. **OBS-AS-009 — Implementation-only gap motivating CHG-B9-01**: **Given** any
   report, **When** it is run, **Then** it accepts no parameters at all — no
   date range, status filter, department, Vendor, or free-text search — and
   returns every qualifying row in a single response with no pagination.
3. **OBS-AS-010 — Implementation-only conformance gap (FR-005, FR-017)**:
   **Given** the Asset Register report, **When** it is produced, **Then** it
   lists every Asset regardless of status and labels the Custodian column
   "Owner" and the purchase-cost column "Value".
4. **OBS-AS-011 — Implementation-only**: **Given** the Asset Movement report,
   **When** a Transfer has no previous owner, **Then** the row reads "IT Store",
   a concept Draft B4 resolved as Checkout rather than Transfer.
5. **OBS-AS-012 — Implementation-only**: **Given** the Employee Asset report,
   **When** it is produced, **Then** it lists active Users and the Assets they
   currently hold, which includes a `Lost` Asset because `Lost` retains its
   Custodian.
6. **OBS-AS-013 — Implementation-only conformance gap (FR-017)**: **Given** the
   Warranty Expiry and AMC Expiry reports, **When** they are produced, **Then**
   they include terminal Assets, and the AMC report's Vendor column is always
   empty because no code path records an AMC Vendor.
7. **OBS-AS-014 — Test-backed current behavior**: **Given** an AMC contract
   ended before its dates were ever entered, **When** the AMC Expiry report is
   produced, **Then** it does not fail and labels that row as cancelled before
   dates were entered.
8. **OBS-AS-015 — Implementation-only**: **Given** the Vendor Service report,
   **When** it is produced, **Then** it omits Vendors with no Service Records,
   counts open and closed repairs, sums closed-record cost as total spend, and
   averages turnaround in whole days from sent to returned date.
9. **OBS-AS-016 — Implementation-only**: **Given** the Assets Currently In
   Service report, **When** it is produced, **Then** it lists open Service
   Records oldest first with Vendor, sent date, expected return, and reason.
10. **OBS-AS-017 — Implementation-only**: **Given** the Purchase report,
    **When** it is produced, **Then** it lists only Assets linked to a
    Procurement, ordered by purchase date descending, showing the Asset's own
    purchase cost rather than any Procurement-level total.

---

### User Story 3 — Restrict Summary and Report Data to Authorized Readers (Priority: P1)

Every Dashboard figure, report row, and export honors the same data-visibility
rules that govern the underlying records.

**Why this priority**: Reporting is the easiest way to bypass record-level
authorization. A global report handed to a broadly granted Role discloses
everything the Role could not read directly.

**Independent Test**: As each named Role, request the Dashboard, the catalog,
each report, and each export, and confirm the data returned matches that Role's
accepted visibility scope.

**Acceptance Scenarios**:

1. **AS-007 — Stakeholder-confirmed**: **Given** an Employee with `asset_view`,
   **When** the Dashboard is requested, **Then** every figure covers only Assets
   where that Employee is Custodian, and no recent-Transfer or open-Checkout
   list naming other Users is returned. **Given** an authorized non-Employee
   Role, **Then** global figures are returned.
2. **AS-018 — Stakeholder-confirmed**: **Given** a User without `asset_view`,
   **When** the Dashboard is requested, **Then** access is denied rather than
   an empty summary being returned.
3. **AS-019 — Stakeholder-confirmed**: **Given** a User with `report_access`,
   **When** any report is run, **Then** global rows are returned; **Given** a
   User without it, **Then** access is denied.
2. **AS-008 — Stakeholder-confirmed**: **Given** a User holding
   `report_access` but who is neither Admin nor IT Manager, **When** any B9
   surface would present AuditLog content, **Then** access is denied and no rows
   are returned. **Given** an IT Manager, **Then** both the view and the export
   succeed.
3. **AS-009 — Draft B8 dependency (FR-014)**: **Given** any allowed AuditLog
   view or export through a B9 surface, **When** it succeeds or is rejected,
   **Then** it creates the AuditLog entry B8 requires.
4. **AS-010 — Draft B8 dependency (FR-015)**: **Given** any B9 output,
   **When** it includes AuditLog-derived values, **Then** it respects B8 value
   minimization, including the treatment of source IP as protected data.
5. **AS-011 — Governance requirement**: **Given** any B9 surface, **When**
   authorization is decided, **Then** it is enforced at the backend action
   boundary; hiding a menu entry or a route MUST NOT be the authorization
   control.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-018 — Implementation-only conformance gap (FR-007, FR-016)**:
   **Given** any authenticated User including an Employee, **When** the
   Dashboard or a chart is requested, **Then** global data is returned, because
   those endpoints require authentication only and the frontend Dashboard route
   carries no permission gate.
2. **OBS-AS-019 — Implementation-only, conforming**: **Given** any User with
   `report_access`, **When** a report is run, **Then** every qualifying row is
   returned with no ownership or department scoping. Under FR-007 global report
   rows for `report_access` holders are accepted.
3. **OBS-AS-020 — Implementation-only conformance gap (FR-008, FR-010)**:
   **Given** a User with `report_access` and no AuditLog authority — which under
   the seeded Role set includes Viewer — **When** the AuditLog-derived report is
   run or exported, **Then** up to 1,000 AuditLog entries are returned including
   username, action, module, old and new values, and source IP address, while
   the direct Audit Trail surface is restricted to Admin.
4. **OBS-AS-021 — Implementation-only conformance gap (FR-009)**: **Given** a
   report is viewed rather than exported, **When** the request succeeds,
   **Then** no AuditLog entry is created, including for the report that exposes
   AuditLog content.
5. **OBS-AS-022 — Implementation-only**: **Given** the seeded Role set,
   **When** `report_access` is granted, **Then** it belongs to IT Manager, IT
   Staff, and Viewer, while HR and Employee do not hold it and Admin bypasses
   permission codes entirely.

---

### User Story 4 — Keep Lost Asset Reporting Distinct from Physical Auditing (Priority: P1)

A reader can tell the difference between a list of Assets reported missing, an
operational event history, and a physical verification exercise that the
organization has deliberately deferred.

**Why this priority**: `CONTEXT.md` is explicit that there is no periodic
physical audit process. A report titled "Asset Audit" invites exactly the
confusion the glossary warns against.

**Independent Test**: Review every B9 title, label, and column against the
glossary definitions of `Lost`, AuditLog, and physical Asset audit, and confirm
no surface implies physical verification.

**Acceptance Scenarios**:

1. **AS-012 — Accepted intent (`CONTEXT.md`, Lost)**: **Given** Assets recorded
   as `Lost`, **When** they are reported, **Then** the report identifies the
   Custodian retained for accountability and presents the data as reactive
   record-keeping, not as the result of a physical check.
2. **AS-013 — Accepted intent (`CONTEXT.md`, Lost; `ROADMAP.md`, F1)**:
   **Given** any B9 surface, **When** it is named or described, **Then** it MUST
   NOT imply that a periodic physical Asset audit has been performed, because
   that capability is deferred beyond v1 and does not exist.
3. **AS-014 — Draft B8 dependency (FR-007)**: **Given** AuditLog content
   surfaced through B9, **When** it is titled and described, **Then** it is
   presented as an operational event history and never as proof of physical
   verification.
4. **AS-020 — Stakeholder-confirmed**: **Given** the report catalog, **When**
   an AuditLog projection is titled, **Then** it does not use the "Asset Audit"
   name, which remains reserved for the deferred F1 physical-verification
   capability.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-023 — Implementation-only**: **Given** the Lost Assets report,
   **When** it is produced, **Then** it lists `Lost` Assets with a column
   labelled "Last Known Custodian" alongside department and condition, which
   matches the accountability intent in `CONTEXT.md`.
2. **OBS-AS-024 — Implementation-only conformance gap (FR-003)**: **Given**
   the report catalog, **When** it is listed, **Then** it contains a report
   titled "Asset Audit Report" whose content is the AuditLog rather than any
   Asset verification, so its title describes something the system does not
   do.

---

### User Story 5 — Export a Report in a Consistent Form (Priority: P2)

An authorized User downloads a report as PDF, Excel, or CSV and gets the same
data in each, with a form suited to the format.

**Why this priority**: Exports are shared outside the system and outlive the
session that produced them. Divergence between formats produces two versions of
the same "official" figures.

**Independent Test**: Export one report in all three formats and compare row
sets, column sets, ordering, headers, branding, and generation metadata.

**Acceptance Scenarios**:

1. **AS-015 — Accepted boundary (Draft B4 FR-015)**: **Given** the per-Transfer
   custody PDF, **When** export behavior is defined, **Then** it remains a B4
   custody document with B4's access rule and is not part of the B9 report or
   export catalog.
2. **AS-016 — Draft B8 dependency**: **Given** any export containing AuditLog
   content, **When** it is produced, **Then** it obeys the same access, audit,
   and minimization rules as viewing that content.
3. **FWD-AS-003 — Prospective Change scenario, not B9 baseline acceptance**: **Given** a report exported as PDF,
   Excel, and CSV, **When** the three files are compared, **Then** their row
   sets, column sets, and ordering are identical and each states the filters
   that produced it.
4. **FWD-AS-004 — Prospective Change scenario, not B9 baseline acceptance**: **Given** any export, **When** it is
   requested, **Then** it is produced server-side, is refused if the requester
   is not authorized for the underlying report, and creates the required audit
   entry.
5. **FWD-AS-005 — Prospective Change scenario, not B9 baseline acceptance**: **Given** an Excel or CSV export,
   **When** a recipient opens it, **Then** date columns behave as dates and
   numeric columns as numbers without re-parsing.
6. **FWD-AS-006 — Prospective Change scenario, not B9 baseline acceptance**: **Given** no configured organization
   name, **When** a PDF or Excel export is requested, **Then** the missing
   configuration is surfaced to an administrator rather than a built-in
   organization name being substituted.
7. **FWD-AS-007 — Prospective Change scenario, not B9 baseline acceptance**: **Given** a report whose result reaches
   an applied limit, **When** it is displayed or exported, **Then** it states
   that the result was limited and how to narrow it; **Given** a result within
   the limit, **Then** it is identifiable as complete.
8. **FWD-AS-008 — Prospective Change scenario, not B9 baseline acceptance**: **Given** the organization's stated data
   volume, **When** any report is run, **Then** it returns within the approved
   time budget, and any report that cannot paginates or streams rather than
   clipping.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-025 — Implementation-only**: **Given** a report, **When** it is
   exported server-side, **Then** only PDF and Excel are offered, the file is
   named from the report key, and the export is recorded in the AuditLog with
   the report key and format.
2. **OBS-AS-026 — Implementation-only gap motivating CHG-B9-01**:
   **Given** a report, **When** CSV is chosen, **Then** the file is generated in
   the browser from the rows already loaded, carries no company name, title, or
   generation timestamp, and creates no AuditLog entry — so the three formats
   are not equivalent and one of them is outside server-side control.
3. **OBS-AS-027 — Implementation-only**: **Given** a PDF export, **When** it is
   built, **Then** it is a landscape A4 document with a coloured banner reading
   "{company} — {title}", a striped table with equal-width columns, a footer
   carrying the generation timestamp and page number, and a "Prepared By" /
   "Approved By" signature block appended to every report regardless of whether
   the report is something anyone approves.
4. **OBS-AS-028 — Implementation-only**: **Given** an Excel export, **When** it
   is built, **Then** the sheet is named from the report title truncated to 31
   characters, row one is a merged branded banner, row two is the header row,
   panes are frozen below it, and column widths are derived from content and
   capped.
5. **OBS-AS-029 — Implementation-only gap motivating CHG-B9-01**: **Given** any
   export, **When** date columns are produced, **Then** they were already
   formatted as display strings by the report, so Excel receives text rather
   than dates and the output cannot be sorted or filtered as dates by the
   recipient.
6. **OBS-AS-030 — Implementation-only**: **Given** an unknown report key or an
   unsupported format, **When** an export is requested, **Then** the request is
   reported as unknown.

---

### User Story 6 — Produce Recognizably Branded Output (Priority: P3)

Exported documents identify the organization that produced them.

**Why this priority**: Branding matters for documents that leave the
organization, but it carries no correctness or authorization weight.

**Independent Test**: Change the configured company name and confirm every
server-generated export reflects it.

**Acceptance Scenarios**:

1. **AS-017 — Accepted dependency**: **Given** a configured company name,
   **When** a server-generated export is produced, **Then** it identifies the
   organization consistently across formats.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-031 — Implementation-only gap motivating CHG-B9-01**: **Given**
   branding, **When** an export is produced, **Then** the company name comes
   from an administrative Setting with a hard-coded fallback organization name,
   the banner colour is a hard-coded brand blue, and no logo, address, or
   document reference is included.
2. **OBS-AS-032 — Implementation-only, conforming**: **Given** the CSV path,
   **When** it is produced, **Then** it carries no branding at all, which
   matches the prospective branding rule in CHG-B9-01.

### Edge Cases

- The Dashboard requires no permission code, so an Employee who under accepted
  B2 ALR-009 may read only their own Assets can nevertheless see organization-
  wide counts, total portfolio value, and the names of Users involved in recent
  Transfers and open Checkouts.
- The report that exposes AuditLog content is reachable with `report_access`,
  which the seeded Role set grants to Viewer, while the equivalent Audit Trail
  surface is Admin-only. Draft B8 FR-016 requires both to enforce the same
  policy.
- Source IP addresses appear in that report's rows and in its PDF and Excel
  exports. Draft B8 treats source IP as protected data with a shorter retention
  rule than the entry itself.
- Viewing a report creates no AuditLog entry while exporting one does, so the
  read that discloses the most sensitive content is the one that leaves no
  trace.
- CSV is produced entirely in the browser, so it is invisible to server-side
  access logging and cannot be prevented by a backend control once the rows have
  been delivered.
- Reports return every qualifying row with no pagination or limit. The Asset
  Register, Movement, Purchase, and AMC reports grow without bound, while the
  AuditLog-derived report is the only one with a cap, at 1,000 rows — a limit
  that silently truncates rather than paginating.
- Two reports build their rows with per-row queries — the Employee Asset report
  iterates Users and then their Assets, and the Vendor Service report issues
  several queries per Vendor — so cost grows with catalog size rather than with
  result size.
- The expiry threshold tiles are cumulative, so an Asset expiring in three days
  is counted in the 7, 15, and 30-day figures simultaneously. Read as disjoint
  buckets they overstate the near-term workload.
- Total portfolio value includes Assets that have been sold, scrapped, or lost,
  so it cannot be reconciled against a balance sheet.
- The purchase trend attributes an Asset's own purchase cost to its linked
  Procurement's purchase date, mixing an Asset-level figure with a
  Procurement-level date; Assets with no Procurement are silently absent.
- The transfer trend counts Approved Transfers by a date field that Draft B4
  records as being overwritten with the approval time, so the trend is by
  decision date even though the field is named as a request date.
- Category distribution hides empty categories while department distribution
  shows empty departments, so two charts on the same screen answer the same
  shape of question differently.
- Every report PDF carries a "Prepared By" / "Approved By" signature block,
  including reports that record no approval and reports whose content is an
  audit log.
- Report columns are laid out at equal width regardless of content, so a report
  with a long free-text column renders it unreadably narrow.
- The Vendor Service report's total spend depends on Service Record cost, which
  Draft B5 now requires at closure but which is optional in current data, so
  historical spend is understated without saying so.
- The AMC Expiry report's Vendor column is structurally always empty because no
  code path records an AMC Vendor; Draft B7 now requires one on dated contracts.
- The Movement report labels an absent previous owner "IT Store", a concept
  Draft B4 resolved as Checkout rather than Transfer.

## Requirements *(mandatory)*

### Functional Requirements

Most B9 behavior is implementation-only. The requirements below are limited to
what an authoritative source supports; everything else is recorded as evidence
or as an unresolved decision.

- **FR-001 — Accepted intent**: Vendor-grouped reporting MUST group Service
  Record activity by managed Vendor identity so that questions such as "which
  vendor has pending repairs" can be answered reliably.
  *(Source: `CONTEXT.md`, **Vendor**.)*
- **FR-002 — Accepted intent**: Lost Asset reporting MUST present Assets in the
  terminal `Lost` status together with the Custodian retained for
  accountability, and MUST present the data as reactive record-keeping.
  *(Sources: `CONTEXT.md`, **Lost** and **Custodian**; Draft B2 FR-009.)*
- **FR-003 — Accepted intent with stakeholder-confirmed naming rule**: No B9
  surface MUST imply that a periodic physical Asset audit has been performed.
  Physical verification is deferred beyond v1, and AuditLog content MUST be
  titled and described as operational event history rather than Asset
  verification. The "Asset Audit" name MUST be reserved for the deferred F1
  physical-verification capability and MUST NOT be used for an AuditLog
  projection.
  *(Sources: `CONTEXT.md`, **Lost**; `ROADMAP.md`, F1; Draft B8 FR-007;
  stakeholder clarification, 2026-08-05. The current report title is a
  conformance gap.)*
- **FR-004 — Accepted intent**: A Dashboard panel, chart, or report MUST NOT be
  presented as satisfying any alerting obligation. Proactive delivery is owned
  by the source capability.
  *(Sources: `CONTEXT.md`, **AMC**; Draft B7 FR-017.)*
- **FR-005 — Draft B2 dependency**: Every B9 label, column heading, and value
  MUST use the canonical terminology and the canonical status and condition sets
  owned by the source baseline, including `Sold` rather than `Disposed`,
  `Checkout` rather than `Assignment`, and `Custodian` rather than `Owner`.
  *(Source: Draft B2 FR-004.)*
- **FR-006 — Accepted dependency**: B9 MUST NOT define, override, or reinterpret
  any lifecycle rule, status meaning, or business definition owned by B2 through
  B7. Where a source baseline changes its definition, the B9 presentation
  follows it.
  *(Sources: Draft B2; Draft B3 through B7; `.specify/memory/constitution.md`,
  Principle I.)*
- **FR-007 — Stakeholder-confirmed**: The Dashboard MUST require `asset_view`
  and MUST return figures scoped to the reader's B1 Asset visibility. An
  authorized non-Employee Role receives global figures; an Employee receives
  only Assets where that Employee is Custodian and MUST NOT receive
  cross-User activity lists. Reports MUST continue to require `report_access`
  and remain global for the Roles that hold it.
  *(Sources: stakeholder clarification, 2026-08-05; Draft B2 ALR-009. The
  current permission-free, unscoped Dashboard is a conformance gap.)*
- **FR-008 — Stakeholder-confirmed, Draft B8 dependency**: Every B9 surface
  that presents AuditLog content MUST be governed by the Draft B8 FR-016 access
  policy, so only Admin and IT Manager may read or export it. Holding
  `report_access` alone MUST NOT grant AuditLog data or exports through the
  report catalog, and the report path MUST remain available to IT Manager so the
  export access B8 grants is reachable.
  *(Sources: stakeholder clarification, 2026-08-05; Draft B8 FR-016. The current
  `report_access` gating is a conformance gap.)*
- **FR-009 — Draft B8 dependency**: Every allowed AuditLog view or export
  through a B9 surface, and every rejected attempt, MUST create the AuditLog
  entry B8 requires, without exposing AuditLog data to a rejected actor.
  *(Source: Draft B8 FR-014 and FR-016. The current unaudited report view is a
  conformance gap.)*
- **FR-010 — Draft B8 dependency**: B9 output containing AuditLog-derived values
  MUST respect B8 value minimization and its treatment of source IP as protected
  data with a shorter retention rule than the entry itself.
  *(Source: Draft B8 FR-015 and FR-017.)*
- **FR-011 — Accepted boundary**: The per-Transfer custody PDF MUST remain owned
  by B4, with B4's access rule, and MUST NOT be presented as a B9 report or
  added to the B9 export catalog.
  *(Source: Draft B4 FR-015 and Transfer PDF Baseline.)*
- **FR-012 — Governance requirement**: Every B9 read and export MUST be
  authorized at the backend action boundary. A hidden menu entry or an
  unprotected frontend route MUST NOT be the authorization control.
  *(Sources: `.specify/memory/constitution.md`, Principle II; Draft B2
  ALR-001.)*
- **FR-013 — Accepted safety property**: A B9 surface MUST be read-only. Running
  or exporting a report MUST NOT create, change, or delete any business record;
  the required audit entry is the only permitted write.
  *(Source: `.specify/memory/constitution.md`, Principle II; current behavior
  conforms.)*
- **FR-014 — Evidence integrity**: Every calculation, column, row-selection
  rule, access scope, format, and presentation choice in this Draft that is
  observed only in implementation MUST remain labelled implementation-only until
  backed by a test or an explicit stakeholder decision. Because B9 is
  implementation-led, this restriction covers the majority of its current
  behavior.
  *(Source: `.specify/memory/constitution.md`, Principle III.)*
- **FR-015 — Decision gate**: U-001 through U-006 were resolved by the
  stakeholder clarification dated 2026-08-05 and MUST NOT be reopened by
  observing current implementation behavior. Two review inputs remain acceptance
  review inputs remain evidence-classification concerns: current per-figure
  meanings and the data volume at which current behavior has been observed.
  This Draft MUST NOT be accepted before every source baseline it presents has
  itself been accepted, because a metric cannot be validated against an
  undecided definition. The conformance gaps in U-007 are review findings, not
  grounds for weakening the requirement each one contradicts.
  *(Sources: stakeholder clarification, 2026-08-05; `ROADMAP.md` B9 review
  status and drafting order; `.specify/memory/constitution.md`, Principle
  III.)*
- **FR-016 — Stakeholder-confirmed**: No aggregate, count, chart, trend, or
  recent-activity list MUST disclose information about records the reader is not
  authorized to read individually. A scoped reader's totals MUST be computed
  over that reader's visible records rather than filtered from a global result
  after the fact.
  *(Sources: stakeholder clarification, 2026-08-05; Draft B2 ALR-009.)*
- **FR-017 — Stakeholder-confirmed**: Every Dashboard metric, chart, and report
  MUST exclude Assets in `Sold`, `Scrapped`, and `Lost` by default, because a
  terminal Asset has left circulation. A surface whose stated purpose is
  terminal — the Lost Assets report, and any status distribution that exists to
  show the whole register — MUST state that inclusion explicitly on the surface
  itself. Total value MUST therefore describe only Assets the organization still
  holds.
  *(Sources: stakeholder clarification, 2026-08-05; Draft B2 FR-008. The
  current inclusive counting is a conformance gap.)*
- **FR-018 — Stakeholder-confirmed**: Expiry threshold figures MUST be disjoint
  bands rather than cumulative counts, so each Asset or contract appears in
  exactly one band and the bands can be read as a workload breakdown. The band
  boundaries and the treatment of an end date falling exactly on a boundary MUST
  be stated on the surface.
  *(Sources: stakeholder clarification, 2026-08-05. The current cumulative tiles
  are a conformance gap.)*
### Prospective Change Extracted — Not B9 Baseline Requirements

- **FWD-B9-001**: Standard filters and written definitions, protected
  server-controlled export parity, parseable date and numeric values, branding
  corrections, visible limiting, and response-time behavior are desired changes
  absent from the current system. Their normative authority is
  `specs/012-report-filter-export-parity-change/spec.md`; they MUST NOT be used
  as evidence that B9 currently implements or accepts those delivery outcomes.

### Current-System Contract Candidates — Not Accepted Requirements

These record current behavior only. They are evidence for stakeholder review and
MUST NOT be read as accepted requirements.

- **CAND-001**: The Dashboard and chart endpoints require an authenticated
  session and no permission code, and the frontend Dashboard route carries no
  permission gate.
- **CAND-002**: Dashboard KPIs are total Assets; a count of `Available` plus
  `Assigned`; separate `Available`, `Assigned`, and `Under Repair` counts; the
  summed purchase cost of every Asset; open Checkouts; Pending Transfers; open
  Service Records; expired Warranty and expired active AMC counts; and
  cumulative 7, 15, and 30-day expiry counts for both coverage types.
- **CAND-003**: Expired is calculated as an end date strictly before today, and
  each threshold counts end dates from today through today plus the threshold
  inclusive. FR-018 is authoritative.
- **CAND-004**: The Dashboard also returns the five newest Transfers, the five
  newest open Checkouts, and the five Assets whose Warranty expires within 30
  days, each serialized with the related Users' details.
- **CAND-005**: Seven charts exist: category distribution excluding empty
  categories, status distribution including terminal statuses, department
  distribution including empty departments, a twelve-month purchase-cost trend
  keyed on Procurement purchase date, a twelve-month Approved-Transfer count
  trend, and Warranty and active-AMC timelines bucketed as Expired, 0-30, 31-60,
  61-90, and 90+ days.
- **CAND-006**: The report catalog contains ten fixed reports whose keys and
  titles are defined in the backend and returned to the frontend as chips.
- **CAND-007**: No report accepts any parameter; there is no date range, status,
  department, Vendor, or search filter anywhere in the report API or surface.
  CHG-B9-01 owns the desired filtering behavior.
- **CAND-008**: Every report returns all qualifying rows in one response with no
  pagination; only the AuditLog-derived report is capped, at the 1,000 newest
  entries, and that cap is applied silently. CHG-B9-01 owns desired visible
  limiting and response-time behavior.
- **CAND-009**: Report row selection and columns are fixed per report as
  recorded in the Current Report Catalog table below.
- **CAND-010**: Running a report requires `report_access`; the seeded Role set
  grants that code to IT Manager, IT Staff, and Viewer, and Admin bypasses
  permission codes.
- **CAND-011**: The "Asset Audit Report" returns AuditLog date, username,
  action, module, old value, new value, and source IP address to any
  `report_access` holder, while the Audit Trail surface is Admin-only. FR-003
  and FR-008 are authoritative for its title and access.
- **CAND-012**: Exporting a report writes an AuditLog entry recording the report
  key and format; viewing a report writes none.
- **CAND-013**: Server-side exports support PDF and Excel only and are named
  `{key}_report.pdf` and `{key}_report.xlsx`. CHG-B9-01 owns protected CSV
  delivery and format parity.
- **CAND-014**: CSV is generated in the browser from the already-rendered rows,
  named `{key}_report.csv`, quoted with doubled inner quotes, and carries no
  banner, title, timestamp, or audit record.
- **CAND-015**: The report PDF is landscape A4 with a branded banner, a striped
  table with equal-width columns repeating its header row, a footer carrying
  generation time and page number, and a two-signature "Prepared By" / "Approved
  By" block.
- **CAND-016**: The Excel workbook names its sheet from the title truncated to
  31 characters, merges a branded banner across row one, styles row two as
  headers, freezes panes below the header, and sets column widths from content
  up to a cap.
- **CAND-017**: Report values are formatted as display strings before export, so
  dates reach Excel as text and numeric costs reach it as numbers. CHG-B9-01
  owns parseable and typed export values.
- **CAND-018**: The company name is read from an administrative Setting with the
  hard-coded fallback "Cloud Shoe Factory"; the banner colour is a hard-coded
  brand blue; no logo or document reference is included. CHG-B9-01 owns the
  desired missing-configuration behavior; remaining visual choices are
  unresolved presentation detail.
- **CAND-019**: The Employee Asset report iterates active Users and queries each
  User's held Assets; the Vendor Service report iterates every Vendor and issues
  several queries per Vendor, skipping those with no Service Records.
- **CAND-020**: Unknown chart names, report keys, and export formats are
  reported as unknown rather than failing.

### Authorization and Lifecycle Requirements

- **ALR-001 — Accepted authorization boundary**: Every Dashboard, chart, report,
  and export action MUST enforce its access decision server-side, including the
  data scope applied to the rows returned.
  *(Sources: `.specify/memory/constitution.md`, Principle II; Draft B2
  ALR-001. The current permission-free Dashboard is a conformance gap.)*
- **ALR-002 — Accepted read-only property**: No B9 action MUST mutate business
  data. The AuditLog entries required by FR-009 are the only permitted writes.
- **ALR-003 — Stakeholder-confirmed aggregate-disclosure rule**: An aggregate,
  count, chart, trend, or activity list MUST NOT disclose information about
  records the reader is not authorized to read individually, and MUST be
  computed over the reader's visible record set.
  *(Sources: stakeholder clarification, 2026-08-05; Draft B2 ALR-009;
  FR-007 and FR-016.)*
- **ALR-004 — Draft B8 dependency**: AuditLog content reached through a report
  or export MUST be governed by B8's access, audit, minimization, and retention
  rules rather than by `report_access`.
  *(Source: Draft B8 FR-014 through FR-017.)*
- **ALR-005 — Accepted export boundary**: An export MUST contain exactly the
  data the requesting User is authorized to read at the moment of export, and
  MUST NOT widen scope relative to the on-screen report.
- **ALR-006 — Current permission mapping**: The Dashboard and chart endpoints
  currently require authentication only; the report catalog, report retrieval,
  and server-side export require `report_access`; CSV export requires nothing
  beyond having already loaded the report; and the Audit Trail surface is
  Admin-only. Under FR-007 the Dashboard must instead require `asset_view` with
  a scoped result; the report `report_access` mapping conforms; the CSV path and
  the permission-free Dashboard do not.

### Current Report Catalog — Implementation Evidence

| Key | Title | Rows selected | Columns | Owning source baseline |
| --- | --- | --- | --- | --- |
| `register` | Asset Register Report | Every Asset, oldest first | Asset ID, Tag No, Name, Category, Serial No, Owner, Department, Location, Status, Value | B2 |
| `movement` | Asset Movement Report | Every Transfer, newest first | Transfer ID, Asset ID, Asset, Previous User, New User, Date, Approved By, Status | B4 |
| `warranty` | Warranty Expiry Report | Assets with a Warranty end date, soonest first | Asset ID, Name, Category, Warranty Start, Warranty End, Status | B7 |
| `purchase` | Purchase Report | Assets linked to a Procurement, newest purchase first | Asset ID, Name, Vendor, Purchase Date, Cost, Brand, Model | B6 |
| `employee` | Employee Asset Report | Active Users and the Assets they hold | Employee, Department, Asset ID, Asset, Category, Status, Condition | B1, B2, B3 |
| `audit` | Asset Audit Report *(title and access rejected by FR-003 and FR-008)* | The 1,000 newest AuditLog entries | Date, User, Action, Module, Old Value, New Value, IP Address | B8 |
| `in_service` | Assets Currently In Service Report | Open Service Records, oldest first | Asset ID, Asset, Vendor, Sent Date, Expected Return, Reason | B5 |
| `vendor_service` | Vendor Service Report | Vendors with at least one Service Record | Vendor, Pending Repairs, Completed Repairs, Total Spend, Avg Turnaround (days) | B5, B6 |
| `amc_expiry` | AMC Expiry Report | Every AMC contract, soonest end date first | Asset ID, Name, Category, Vendor, AMC Start, AMC End, AMC Status, Expiry | B7 |
| `lost` | Lost Assets Report | Assets with status `Lost` | Asset ID, Name, Last Known Custodian, Department, Condition | B2 |

Titles, keys, row selection, and columns above are implementation evidence.
CHG-B9-01 owns prospective written definitions and report filtering; accepted
semantics in FR-017 and FR-018 apply to every row. The `audit` row's title
and access were resolved on 2026-08-05: it must be retitled as operational event
history and restricted to Admin and IT Manager under FR-003 and FR-008.

### Key Entities

- **Dashboard summary**: A read-only aggregate view of Assets and lifecycle
  activity. It owns no data and no lifecycle rule.
- **Report**: A server-defined, keyed, parameterless tabular projection over
  data owned by other baselines.
- **Report catalog**: The enumerable set of report keys and titles.
- **Export**: A rendering of a report as PDF, Excel, or CSV.
- **Company branding**: The configured organization name and fixed visual
  styling applied to server-generated exports.
- **AuditLog entry**: The shared operational record owned by B8. B9 both
  presents it through a report and, on export, creates one.
- **Transfer document**: B4's per-Transfer custody PDF, explicitly outside the
  B9 catalog.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The single existing reporting test passes, and every additional
  accepted B9 behavior has a stated verification approach before acceptance.
- **SC-002**: 100% of current Dashboard KPIs, charts, and report columns are
  classified as stakeholder-confirmed, test-backed, implementation-only, or
  unresolved. Written-definition delivery is measured by CHG-B9-01.
- **SC-003**: For every named Role, the data returned by every B9 surface
  matches that Role's accepted visibility scope in 100% of checks, and 0% of
  aggregates disclose records the reader could not read individually.
- **SC-004**: 0% of Users holding only `report_access` can obtain AuditLog
  content through any B9 surface, and 100% of allowed AuditLog views and exports
  and rejected attempts create the required audit entry.
- **SC-005**: 0% of B9 titles, labels, or columns imply that a physical Asset
  audit has been performed, and 100% of lifecycle terminology matches the
  canonical set owned by the source baselines.
- **SC-006**: 100% of current PDF, Excel, and CSV differences are classified as
  current evidence or a CHG-B9-01 delivery gap; none is silently presented as
  implemented parity.
- **SC-007**: 100% of current branding behavior is evidence-qualified; desired
  branding correction is measured by CHG-B9-01.
- **SC-008**: Current volume, query, and truncation behavior remains explicit
  evidence; future response-time and completeness outcomes are measured by
  CHG-B9-01.
- **SC-009**: 100% of B9 actions are read-only apart from required audit
  entries, verified by observing no business-record mutation across a full
  catalog run.
- **SC-010**: All six mandated decisions U-001 through U-006 have explicit
  stakeholder answers before acceptance, and 0% of their current
  implementation-only alternatives are presented as accepted behavior in the
  meantime.
- **SC-011**: 100% of accepted, test-backed, implementation-only, and unresolved
  claims in this baseline cite `CONTEXT.md`, an accepted or Draft dependency
  identifier, an explicit stakeholder decision, or a repository evidence path.

## Assumptions

- B9 is a presentation layer. It is assumed to introduce no business rule of its
  own, so every figure it shows should be derivable from an accepted source
  baseline.
- B1 through B8, including Draft B2, remain Draft dependencies subject to their
  own acceptance reviews. `ROADMAP.md` places B9 last precisely because its
  metric definitions cannot settle before theirs do.
- The organization's data volume is assumed to be modest enough that the current
  unpaginated reports return successfully today. That assumption is exactly what
  U-005 asks the stakeholder to state as a number.
- The Dashboard is assumed to be intended as an operational aid for IT rather
  than a financial reporting surface; the total-value tile is treated as an
  operational indicator, not an accounting figure.
- Report titles are assumed to be user-facing product language subject to the
  same terminology rules as any other surface, which is why the "Asset Audit
  Report" title is treated as a domain question rather than a cosmetic one.
- CSV is assumed to be a convenience format for further analysis rather than a
  document of record; PDF is assumed to be the document-of-record format because
  it is the only one carrying generation metadata.
- No application code, test code, database, route, interface, or configuration
  was modified as part of specifying this baseline.

## Baseline Evidence and Unresolved Conflicts *(Brownfield Baseline only)*

### Accepted Intent

- Vendor is first-class so vendor-grouped reporting, explicitly including "which
  vendor has pending repairs", is reliable: `CONTEXT.md`, **Vendor**.
- `Lost` is recorded reactively with the Custodian retained for accountability,
  and there is no periodic physical audit process; scheduled physical Asset
  audits are deferred beyond v1: `CONTEXT.md`, **Lost** and **Custodian**;
  `ROADMAP.md`, F1.
- Expiry alerts are proactively pushed rather than merely visible on a dashboard
  someone has to check: `CONTEXT.md`, **AMC**; Draft B7 FR-017.
- User-visible terminology uses the canonical status, condition, and lifecycle
  terms: Draft B2 FR-004.
- Terminal Assets have left circulation, and `Lost` retains its Custodian and
  department: Draft B2 FR-008 and FR-009.
- An Employee with `asset_view` is limited to Assets where that Employee is
  Custodian: Draft B2 ALR-009.
- `report_access` alone must not grant AuditLog data or exports, report and
  export surfaces must enforce the same policy as the direct Audit Trail, every
  AuditLog view or export must be audited, values must be minimized, and source
  IP is protected data: Draft B8 FR-007 and FR-014 through FR-017.
- The Transfer PDF is B4's custody document with B4's access rule: Draft B4
  FR-015.
- Authorization is enforced at the action boundary and hiding a control is not
  authorization: `.specify/memory/constitution.md`, Principle II; Draft B2
  ALR-001.

### Verified Behavior Evidence

One test covers B9 behavior. It was run on 2026-08-05 in the repository-local
backend environment and passed.

- **OBS-AS-014**: the AMC Expiry report does not fail on a contract ended before
  its dates were entered and labels that row as cancelled before dates were
  entered:
  `backend/reporting/tests.py::AmcExpiryReportTests::test_report_does_not_crash_on_a_contract_ended_before_dates_were_entered`.

No automated test covers any Dashboard KPI, any chart, any other report's rows
or columns, any access rule, any export format, branding, or performance. No
frontend behavioral test exists for the Dashboard or the Report Center. This is
the weakest evidence base of any baseline in the roadmap and is the reason
`ROADMAP.md` classifies B9 as implementation-led.

### Implementation-Only Observations

- Dashboard KPI set, expiry threshold arithmetic, recent-activity lists, and the
  absence of any permission class on the Dashboard and chart endpoints:
  `backend/reporting/views.py`.
- The seven chart calculations, their bucket boundaries, their inclusion or
  exclusion of empty groups, and the twelve-month window helper:
  `backend/reporting/views.py`.
- The ten report builders, their row selection, ordering, column labels, and
  formatted display values, including the "Owner" and "Value" labels, the "IT
  Store" fallback, and the 1,000-entry AuditLog cap:
  `backend/reporting/views.py`.
- The catalog, retrieval, and export endpoints, their shared `report_access`
  requirement, the export-only audit call, and the unknown-key handling:
  `backend/reporting/views.py`; `backend/reporting/urls.py`.
- Default authentication and permission configuration that leaves function-based
  views authenticated-only: `backend/itams/settings.py`.
- Seeded Role grants for `report_access` covering IT Manager, IT Staff, and
  Viewer: `backend/accounts/migrations/0002_seed_rbac_and_org.py`.
- PDF layout, banner, striped table, equal column widths, footer, and signature
  block; Excel banner, header styling, frozen panes, and width capping; the
  hard-coded brand colour and fallback company name: `backend/core/exports.py`.
- The Transfer custody PDF built by the same module but owned by B4:
  `backend/core/exports.py`.
- Report Center chip catalog, on-screen table, row count, server export calls,
  and browser-side CSV generation: `frontend/src/pages/Reports.jsx`.
- Dashboard tile set, expiry breakdown cards, seven chart cards, and three
  recent-activity panels: `frontend/src/pages/Dashboard.jsx`.
- The unprotected Dashboard route, the `report_access` Report Center route, and
  the Admin-only Audit Trail route: `frontend/src/App.jsx`;
  `frontend/src/components/navbar/Menu.jsx`.
- The Audit Trail surface presenting AuditLog columns including IP address:
  `frontend/src/pages/Audit.jsx`.
- The empty reporting models module, confirming B9 owns no persisted data:
  `backend/reporting/models.py`.

### Unresolved Conflicts

- **U-001 — Metric, column, and chart definitions — RESOLVED IN PRINCIPLE
  2026-08-05**: the stakeholder set three governing rules rather than approving
  each figure individually. Terminal Assets are excluded by default except on
  surfaces whose purpose is terminal (FR-017); expiry figures are disjoint bands
  rather than cumulative counts (FR-018); and desired written definitions and
  standard date-range, status, and department filters are retained in
  CHG-B9-01. Column labels are corrected to canonical terms under FR-005.

  These rules resolve the recurring semantic questions. The remaining
  figure-by-figure definitions — what the purchase trend attributes to which
  date, whether the transfer trend is by request or decision date, whether empty
  categories and departments are shown consistently, and whether the unused
  "active" KPI is retained — remain B9 evidence-review questions. Prospective
  written-definition delivery is recorded in CHG-B9-01 rather than promoted to
  B9 AS-BUILT behavior.
- **U-002 — Global versus scoped visibility — RESOLVED 2026-08-05**: the
  stakeholder required the Dashboard to use `asset_view` with results scoped to
  the reader's B1 Asset visibility — global for authorized non-Employee Roles,
  own-Custodian only for Employee, with no cross-User activity lists for a
  scoped reader — while reports keep `report_access` and stay global for the
  Roles holding it. No aggregate may summarize records the reader could not read
  individually. Recorded in FR-007, FR-016, AS-007, AS-018, AS-019, and ALR-003;
  the current permission-free, unscoped Dashboard
  (`backend/reporting/views.py`; `frontend/src/App.jsx`) is now a conformance
  gap in U-007. Department-based scoping was considered and rejected, consistent
  with B1 treating Department as organizational data rather than an
  authorization boundary.
- **U-003 — Export parity — RESOLVED 2026-08-05**: the stakeholder required
  all three formats to be generated server-side under the same authorization
  check and audit entry, to carry identical row and column sets in the same
  order with the applied filters stated, and to use typed dates and numbers in
  Excel and CSV; PDF remains the document of record. The desired behavior is
  recorded normatively in CHG-B9-01; the browser-generated CSV path and the
  pre-formatted values (`frontend/src/pages/Reports.jsx`;
  `backend/core/exports.py`) are evidence motivating that Change.
- **U-004 — Branding — RESOLVED 2026-08-05**: the stakeholder required PDF
  and Excel to identify the organization from the configured organization name,
  CSV to stay unbranded as a data-interchange format, and an unconfigured name
  to be surfaced as a configuration error rather than silently replaced by a
  built-in fallback. Recorded normatively in CHG-B9-01; the hard-coded fallback
  organization name (`backend/core/exports.py`;
  `backend/reporting/views.py`) is now a conformance gap in U-007. Logo,
  document reference, banner colour, and the signature block remain presentation
  detail recorded under Remaining Evidence-Led Confirmation Items.
- **U-005 — Volume and performance expectations — RESOLVED 2026-08-05**: the
  stakeholder prohibited silent truncation outright — a result is complete or
  states that it was limited and how to narrow it — required an approved
  response-time budget at a stated data volume, and required a report that
  cannot meet the budget to paginate or stream rather than clip. The AuditLog
  report's fixed 1,000-row cap is replaced by filter-driven narrowing with an
  explicit limit indicator. Recorded normatively in CHG-B9-01; the current
  silent cap and per-row query patterns (`backend/reporting/views.py`) are
  evidence motivating that Change.
- **U-006 — Meaning and access of the "Asset Audit Report" — RESOLVED
  2026-08-05**: the stakeholder required the report to be retitled so it names
  operational event history rather than Asset verification, with the "Asset
  Audit" name reserved for the deferred F1 physical-verification capability; its
  access governed by Draft B8 FR-016 so only Admin and IT Manager may read or
  export it; every view and export audited; and source IP handled as protected
  B8 data. The report path stays in the catalog so the export access B8 grants
  IT Manager remains reachable, since the Admin-only Audit Trail surface offers
  no export. Recorded in FR-003, FR-008, FR-009, FR-010, AS-008, and AS-020; the
  current title and `report_access` gating (`backend/reporting/views.py`;
  `backend/accounts/migrations/0002_seed_rbac_and_org.py`) are now conformance
  gaps in U-007.
- **U-007 — Conformance gaps recorded, not accepted**: the current behaviors
  below contradict accepted requirements in this Draft. Each is recorded as a
  gap rather than reconciled by weakening a requirement. Whether a gap is
  corrected, deferred, or formally excepted is a review decision, not a
  specification decision.

| # | Current behavior | Accepted requirement | Current-state record |
| --- | --- | --- | --- |
| 1 | The Dashboard and chart endpoints require no permission code and return global data to any authenticated User | FR-007, ALR-001 | CAND-001 |
| 2 | Aggregates and recent-activity lists disclose Users and Assets an Employee could not read individually | ALR-003 | CAND-004 |
| 3 | `report_access` alone yields AuditLog content including source IP, reaching Viewer | FR-008, FR-010 | CAND-011 |
| 4 | Viewing a report, including the AuditLog-derived one, creates no audit entry | FR-009 | CAND-012 |
| 5 | A report title implies physical Asset verification and claims the reserved "Asset Audit" name | FR-003 | CAND-011 |
| 6 | The Asset Register report labels the Custodian column "Owner" | FR-005 | CAND-009 |
| 7 | The Movement report labels an absent previous owner "IT Store" | FR-005, Draft B4 FR-001 | CAND-009 |
| 8 | CSV export bypasses server-side access control and audit entirely | ALR-001, ALR-005 | CAND-014 |
| 9 | Metrics, charts, and reports count terminal Assets, including total portfolio value | FR-017 | CAND-002 |
| 10 | Expiry threshold figures are cumulative, so one Asset is counted in several bands | FR-018 | CAND-003 |
| 11 | No report accepts a date, status, or department filter | CHG-B9-01 delivery gap | CAND-007 |
| 12 | No figure carries a written definition | CHG-B9-01 delivery gap | CAND-002, CAND-005 |
| 13 | CSV is generated in the browser rather than server-side | CHG-B9-01 delivery gap | CAND-014 |
| 14 | The three export formats differ in branding, metadata, and audit | CHG-B9-01 delivery gap | CAND-014, CAND-015 |
| 15 | Dates reach Excel and CSV as text because values are pre-formatted | CHG-B9-01 delivery gap | CAND-017 |
| 16 | An unconfigured organization name is silently replaced by a built-in name | CHG-B9-01 delivery gap | CAND-018 |
| 17 | The AuditLog report truncates at 1,000 rows with no indication to the reader | CHG-B9-01 delivery gap | CAND-008 |
| 18 | Two reports issue per-row queries, so cost grows with catalog size rather than result size | CHG-B9-01 delivery gap | CAND-019 |

### Remaining Evidence-Led Confirmation Items

These are not among the six mandated blockers. They are review items to confirm
alongside them:

- Whether the Dashboard's coverage panels should be removed or relabelled now
  that Draft B7 FR-017 states a dashboard cannot satisfy proactive alerting
  (FR-004).
- Whether the Vendor Service report's total spend should disclose that
  historical Service Records may carry no cost, now that Draft B5 requires cost
  at closure.
- Whether the AMC Expiry report's Vendor column should remain before Draft B7's
  Vendor capture requirement is implemented, given that it is currently always
  empty.
- Whether the "Prepared By" / "Approved By" signature block belongs on reports
  that record no approval.
- Whether report titles and column labels should be reviewed as a set against
  every source baseline's canonical terminology once B1 and B3 through B8 are
  accepted.

## Out of Scope *(mandatory)*

### Adjacent Baseline Ownership

- Authentication, Users, Roles, permission-code administration, and the data
  visibility model: B1. B9 consumes the resulting scope rules.
- Asset identity, register data, statuses, conditions, terminology, terminal
  transitions, condition history, files, and Asset deletion: B2.
- Checkout and check-in behavior, including the expected-return and Overdue
  semantics a Dashboard panel displays: B3.
- Transfer request, approval, rejection, and the per-Transfer custody PDF: B4.
  The custody PDF is not a B9 export.
- Service Record lifecycle, cost, bill, outcome, and Vendor selection: B5.
- Procurement, Vendor administration, and catalog masters: B6.
- Warranty and AMC coverage, contract states, renewal, End Support, and the
  proactive expiry alerts that a Dashboard panel MUST NOT substitute for: B7.
- Notification storage and delivery, AuditLog storage, administrative access,
  filters, privacy, and retention: B8. B9 presents AuditLog content and must
  obey B8's policy; it does not define it.

### Explicitly Unresolved Rather Than Accepted

- No requirement-level decision remains open. All six mandated decisions U-001
  through U-006 were resolved on 2026-08-05.
- Current per-figure meanings and observed data-volume behavior remain evidence
  review inputs. Prospective written definitions and performance targets belong
  to CHG-B9-01 and do not block acceptance of an accurately classified B9
  baseline.
- The items under Remaining Evidence-Led Confirmation Items.


### Explicitly Deferred or Excluded

- Scheduled or periodic physical Asset audits and any report that would claim to
  evidence one (`ROADMAP.md`, F1). A future physical-audit report belongs to
  that deferred capability, not to this baseline.
- User-defined, ad-hoc, or saved reports; report scheduling; and emailed report
  delivery.
- Charts, KPIs, or reports covering capabilities that do not exist, including
  procurement requests and employee self-service.
- Financial or accounting reporting, depreciation schedules, and reconciliation
  against a general ledger.
- Any change to the lifecycle rules, definitions, or permissions owned by B2
  through B8 made in order to simplify a report.
- Application-code, test-code, database, route, interface, or configuration
  changes in this documentation-only specification run.
