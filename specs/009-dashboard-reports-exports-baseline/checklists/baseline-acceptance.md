# Brownfield Baseline Acceptance Checklist: B9 Dashboard, Reports, and Exports

**Purpose**: Formal stakeholder and reviewer gate for determining whether the B9 requirements are complete, clear, consistent, measurable, and evidence-qualified before the Draft baseline is accepted
**Created**: 2026-08-05
**Feature**: [B9 specification](../spec.md)

**Note**: This checklist validates the requirements as written. It is not an
implementation test plan. Mark an item complete only when the specification
answers it unambiguously and traceably; implementation behavior alone is not
sufficient. Baseline acceptance requires every item to be checked or covered by
an explicit stakeholder-approved waiver recorded in the specification.

B9 is the roadmap's only `E3 — implementation-led` capability, so this gate
weighs classification as heavily as content: every artifact must be either
explicitly accepted or explicitly labelled implementation-only, with nothing
left in between.

Prospective filter, definition, export-parity, branding, and volume-handling
requirements are owned by
[`012-report-filter-export-parity-change`](../../012-report-filter-export-parity-change/spec.md).
Items in this checklist validate only that B9 records current evidence and that
the prospective work is extracted with correct lineage; delivery of that work
does not block acceptance of the B9 AS-BUILT baseline.

## Definition Completeness and Classification

- [ ] CHK001 Is every Dashboard KPI classified as stakeholder-confirmed, test-backed, implementation-only, or unresolved, with prospective written definitions assigned to CHG-B9-01 rather than accepted as current behavior? [Completeness, Spec §CAND-002, §Prospective Change Extracted]
- [ ] CHK002 Is every chart classified the same way, including its grouping, bucket boundaries, and treatment of empty groups? [Completeness, Spec §CAND-005, §OBS-AS-005]
- [ ] CHK003 Is every report in the catalog classified, with its row-selection rule and column set recorded? [Completeness, Spec §Current Report Catalog, §CAND-009]
- [ ] CHK004 Is every current export format classified as evidence, with desired format additions and parity assigned to CHG-B9-01? [Completeness, Spec §CAND-013, §Prospective Change Extracted]
- [ ] CHK005 Is every access rule classified, distinguishing the accepted policy from the current permission mapping? [Consistency, Spec §ALR-006, §FR-007, §FR-008]
- [ ] CHK006 Does B9 avoid accepting prospective per-figure definitions as AS-BUILT behavior and link that obligation to CHG-B9-01? [Classification, Spec §Prospective Change Extracted]
- [ ] CHK007 Is production of future per-figure definitions explicitly excluded as a B9 acceptance precondition and owned by CHG-B9-01? [Scope, Spec §FR-015, §Prospective Change Extracted]
- [ ] CHK008 Is the figure-by-figure residue of U-001 — purchase-trend date basis, transfer-trend date basis, empty-group consistency, and the unused "active" KPI — enumerated so none is silently dropped? [Gap, Spec §U-001]

## Formula and Metric Measurability

- [ ] CHK009 Is each current metric evidence-qualified without claiming that implementation alone supplies an accepted product definition? [Evidence Integrity, Spec §SC-002, §CAND-002]
- [ ] CHK010 Are missing row-selection, terminal-Asset, date-basis, and boundary definitions recorded as current evidence gaps whose normative resolution belongs to CHG-B9-01? [Completeness, Spec §U-001, §Prospective Change Extracted]
- [ ] CHK011 Are the disjoint expiry band boundaries themselves specified — the exact day ranges and what lies beyond the widest band — rather than only the requirement that bands be disjoint? [Gap, Spec §FR-018, §AS-022]
- [ ] CHK012 Is the treatment of an end date falling exactly on a band boundary stated, and is "expired" defined relative to the same reference date? [Ambiguity, Spec §FR-018, §CAND-003]
- [ ] CHK013 Is the set of surfaces whose purpose is terminal — and which therefore include `Sold`, `Scrapped`, and `Lost` — closed and enumerated rather than described by example? [Ambiguity, Spec §FR-017, §AS-021]
- [ ] CHK014 Is the consequence of FR-017 for the Employee Asset report stated, given that excluding terminal Assets removes `Lost` Assets that retain their Custodian for accountability? [Conflict, Spec §FR-017, §OBS-AS-012, §Draft B2 FR-009]
- [ ] CHK015 Is total value's treatment of non-terminal but non-circulating statuses such as `In Storage` stated, not just its exclusion of terminal Assets? [Gap, Spec §FR-017, §CAND-002]
- [ ] CHK016 Is the current reference-date and timezone basis classified as evidence, with any desired cross-surface definition assigned to CHG-B9-01? [Classification, Spec §U-001, §Prospective Change Extracted]

## Empty, Error, and Boundary States

- [ ] CHK017 Is current zero-row behavior recorded for on-screen and available export paths, while prospective cross-format parity is assigned to CHG-B9-01? [Coverage, Spec §OBS-AS-008, §Prospective Change Extracted]
- [ ] CHK018 Are requirements defined for a chart with no data, an empty category, or an empty department? [Coverage, Spec §OBS-AS-005, §CAND-005]
- [ ] CHK019 Is the behavior specified when a Dashboard panel or one of the several independent chart requests fails, so a reader can distinguish "no data" from "failed to load"? [Gap, Spec §User Story 1]
- [ ] CHK020 Are error requirements defined for an unknown report key, unknown chart name, and unsupported export format, or is the current behavior explicitly left implementation-only? [Coverage, Spec §CAND-020, §OBS-AS-030]
- [ ] CHK021 Is the outcome specified when a report is requested by an authorized reader whose visibility scope yields nothing, so an empty result is not mistaken for a denial? [Ambiguity, Spec §FR-007, §FR-016]
- [ ] CHK022 Is the current silent row cap explicitly recorded as an implementation gap, with a future limit indicator and non-silent handling assigned to CHG-B9-01? [Classification, Spec §OBS-AS-029, §Prospective Change Extracted]
- [ ] CHK023 Are requirements defined for a report whose underlying source record was deleted or whose related record is absent, given that current builders substitute a placeholder? [Gap, Spec §Current Report Catalog]

## Report Catalog, Columns, and Filters

- [ ] CHK024 Is the accepted catalog membership stated — which of the ten reports survive, whether any is renamed, and whether the set is closed? [Clarity, Spec §Current Report Catalog, §FR-003]
- [ ] CHK025 Are the corrected column labels specified for the terminology gaps FR-005 requires, including "Owner" and "IT Store"? [Consistency, Spec §FR-005, §U-007 rows 6 and 7]
- [ ] CHK026 Is the current absence of standard report filters recorded as evidence, with per-report primary dates and filter subjects assigned to CHG-B9-01? [Classification, Spec §OBS-AS-009, §Prospective Change Extracted]
- [ ] CHK027 Is behavior for an unsupported future filter excluded from the B9 baseline and assigned to CHG-B9-01? [Scope, Spec §FWD-AS-002, §Prospective Change Extracted]
- [ ] CHK028 Are display and export of applied future filters excluded from the B9 baseline and assigned to CHG-B9-01? [Scope, Spec §FWD-AS-003, §Prospective Change Extracted]
- [ ] CHK029 Is Dashboard filtering explicitly outside the B9 baseline and either bounded or excluded in CHG-B9-01? [Scope, Spec §User Story 1, §Prospective Change Extracted]
- [ ] CHK030 Is the Vendor Service report's business purpose traced to `CONTEXT.md` and distinguished from the other nine reports, which have no stated purpose? [Traceability, Spec §FR-001, §AS-004]
- [ ] CHK031 Is the disclosure requirement stated for the Vendor Service report's total spend, given that historical Service Records may carry no cost even though Draft B5 now requires it? [Gap, Spec §Remaining Evidence-Led Confirmation Items]
- [ ] CHK032 Is the AMC Expiry report's Vendor column addressed, given that it is structurally empty until Draft B7's Vendor capture requirement is implemented? [Gap, Spec §OBS-AS-013, §Remaining Evidence-Led Confirmation Items]

## Access, Scope, and AuditLog Policy

- [ ] CHK033 Is the Dashboard's accepted permission and scope stated completely for every named Role, including what a scoped Employee actually receives? [Completeness, Spec §FR-007, §AS-007]
- [ ] CHK034 Is the requirement that scoped totals be computed over the reader's visible records — rather than filtered from a global result — stated as an outcome that can be verified? [Measurability, Spec §FR-016, §ALR-003]
- [ ] CHK035 Is the tension resolved between scoping the Dashboard for privacy and leaving reports global, given that `report_access` includes Viewer and the Employee Asset report discloses every User's holdings? [Conflict, Spec §FR-007, §OBS-AS-019, §CAND-010]
- [ ] CHK036 Is the AuditLog access rule stated as Admin and IT Manager per Draft B8 FR-016, and applied identically to the view and the export path? [Dependency Consistency, Spec §FR-008, §AS-008]
- [ ] CHK037 Is the requirement that every AuditLog view and export — and every rejected attempt — create an audit entry stated, including for the report path? [Completeness, Spec §FR-009, §OBS-AS-021]
- [ ] CHK038 Is the handling of source IP as protected B8 data specified for report rows and for exported files, including its shorter retention rule? [Privacy/Clarity, Spec §FR-010]
- [ ] CHK039 Is server-side enforcement required for every B9 surface, with frontend route and menu visibility explicitly insufficient? [Security Coverage, Spec §FR-012, §ALR-001]
- [ ] CHK040 Is the read-only property stated so that no B9 action mutates business data, with the required audit entry named as the only permitted write? [Clarity, Spec §FR-013, §ALR-002]
- [ ] CHK041 Is it specified that an export contains exactly what the requester was authorized to read at the moment of export, with no scope widening? [Security Coverage, Spec §ALR-005]

## Export Formats, Parity, and Branding

- [ ] CHK042 Are current server-side and client-side export paths evidence-qualified, with the desired server-controlled three-format policy assigned to CHG-B9-01? [Classification, Spec §U-007 row 13, §Prospective Change Extracted]
- [ ] CHK043 Are current row, column, ordering, and filter differences recorded without treating parity as AS-BUILT behavior, and is future parity assigned to CHG-B9-01? [Classification, Spec §FWD-AS-003, §Prospective Change Extracted]
- [ ] CHK044 Are current format-specific presentation differences classified as evidence, with permitted future differences defined only in CHG-B9-01? [Scope, Spec §U-003, §Prospective Change Extracted]
- [ ] CHK045 Are current Excel and CSV date/number representations recorded as evidence, with prospective native-cell and locale-neutral rules assigned to CHG-B9-01? [Classification, Spec §FWD-AS-005, §Prospective Change Extracted]
- [ ] CHK046 Is the current PDF output recorded as evidence without accepting a future document-of-record policy in the B9 baseline? [Evidence Integrity, Spec §OBS-AS-027, §Prospective Change Extracted]
- [ ] CHK047 Is current branding behavior evidence-qualified, with prospective format-specific branding assigned to CHG-B9-01? [Classification, Spec §FWD-AS-006, §Prospective Change Extracted]
- [ ] CHK048 Is behavior for missing organization branding excluded from B9 baseline acceptance and owned by CHG-B9-01 if required? [Scope, Spec §U-004, §Prospective Change Extracted]
- [ ] CHK049 Are the remaining presentation choices — logo, document reference, banner colour, and the signature block on every report — explicitly left as confirmation items rather than silently accepted? [Clarity, Spec §U-004, §Remaining Evidence-Led Confirmation Items]
- [ ] CHK050 Is the Transfer custody PDF excluded from the B9 catalog in both directions, with B4 named as its owner and its access rule left to B4? [Dependency Consistency, Spec §FR-011, §AS-015]

## Source-Baseline Traceability

- [ ] CHK051 Is the rule that B9 defines no lifecycle rule of its own stated, with every displayed value traced to an owning baseline? [Traceability, Spec §FR-006, §Current Report Catalog]
- [ ] CHK052 Does every report in the catalog table name its owning source baseline, and is that attribution correct for reports drawing on several? [Traceability, Spec §Current Report Catalog]
- [ ] CHK053 Is the requirement stated that B9 follows a source baseline when that baseline changes its definition, rather than freezing a stale one? [Clarity, Spec §FR-006]
- [ ] CHK054 Is canonical terminology required across every label, column, and title, traced to Draft B2 FR-004? [Consistency, Spec §FR-005, §AS-005]
- [ ] CHK055 Is the acceptance gate on every source baseline being accepted first stated as blocking, with its rationale that a metric cannot be validated against an undecided definition? [Clarity, Spec §FR-015]
- [ ] CHK056 Is the accepted-versus-Draft status of each dependency stated accurately wherever it is cited as a source? [Traceability, Spec §Specification Lineage, §Assumptions]
- [ ] CHK057 Is the rule that a Dashboard panel cannot satisfy any alerting obligation stated and reconciled with Draft B7 FR-017 from the owning side? [Dependency Consistency, Spec §FR-004, §AS-001]

## Physical Audit Deferral and Terminology

- [ ] CHK058 Is periodic physical Asset auditing stated as deferred beyond v1 and excluded from this baseline, traced to `CONTEXT.md` and `ROADMAP.md` F1? [Scope, Spec §FR-003, §Out of Scope]
- [ ] CHK059 Is the reservation of the "Asset Audit" name for the deferred F1 capability stated as a requirement, so no current surface may claim it? [Clarity, Spec §FR-003, §AS-020]
- [ ] CHK060 Is the accepted replacement title for the AuditLog projection specified, or is naming it deliberately left to review? [Gap, Spec §FR-003, §U-006]
- [ ] CHK061 Are AuditLog, Audit Trail, physical Asset audit, and Lost Asset reporting defined as four distinct things and used consistently throughout? [Consistency, Spec §Domain Alignment, §FR-002, §FR-003]
- [ ] CHK062 Is Lost Asset reporting characterized as reactive record-keeping with the retained Custodian, rather than as evidence of a physical check? [Clarity, Spec §FR-002, §AS-012]

## Evidence Integrity and Decision Closure

- [ ] CHK063 Is the implementation-led evidence status stated up front, with the single existing test and the total absence of other coverage both explicit? [Traceability, Spec §Evidence Status, §Verified Behavior Evidence]
- [ ] CHK064 Is every accepted requirement traceable to `CONTEXT.md`, a dependency baseline, or the 2026-08-05 clarification, with none resting on implementation evidence alone? [Traceability, Spec §FR-014, §SC-011]
- [ ] CHK065 Are all six resolved decisions U-001 through U-006 recorded with their answers, the requirements they produced, and the conformance gaps they created? [Completeness, Spec §Unresolved Conflicts, §SC-010]
- [ ] CHK066 Is U-001 split cleanly between B9's evidence-qualified current semantics and CHG-B9-01's prospective definitions and filters? [Clarity, Spec §U-001, §Prospective Change Extracted]
- [ ] CHK067 Does FR-015 gate B9 only on accurate baseline classification and accepted source definitions, without making prospective definitions or performance delivery a B9 acceptance precondition? [Clarity, Spec §FR-015, §Prospective Change Extracted]
- [ ] CHK068 Is the prospective data-volume and response-time target owned exclusively by CHG-B9-01 while B9 records current volume and truncation evidence? [Scope, Spec §SC-008, §Prospective Change Extracted]
- [ ] CHK069 Are all 18 conformance gaps in U-007 stated as findings that leave their contradicted requirement intact, rather than as grounds for weakening it? [Consistency, Spec §U-007]
- [ ] CHK070 Is the growth of this baseline's requirement set relative to its evidence base disclosed, so reviewers understand that B9 now describes materially more work than the current system performs? [Traceability, Spec §Evidence Status]
- [ ] CHK071 Are user-defined reports, report scheduling, emailed delivery, and financial reporting excluded explicitly rather than by omission? [Scope, Spec §Out of Scope]

## Notes

- This is a formal baseline-acceptance gate for specification reviewers and
  stakeholders before B9 leaves `Draft`.
- Items marked `[Gap]`, `[Ambiguity]`, or `[Conflict]` intentionally expose
  requirements that may still need a stakeholder decision or an explicit scope
  exclusion. They are not defects in the clarification session; the six mandated
  B9 decisions were closed on 2026-08-05.
- CHK011, CHK014, and CHK035 are the items most likely to change the baseline
  specification. CHK026 and CHK045 now validate extraction to CHG-B9-01 rather
  than requiring prospective behavior in the AS-BUILT baseline.
- B9 cannot be accepted before its source baselines are, so this gate should be
  run last. Several items depend on B5, B7, and B8 content that is still Draft.
- Record supporting requirement identifiers, review findings, or approved
  waivers inline before checking an item.
- The absence of `plan.md` is not evaluated here because this checklist reviews
  the brownfield baseline requirements before implementation planning. For the
  same reason `check-prerequisites.ps1 -Json` reports a missing plan; that is
  expected for a documentation-only baseline.
- The separate `requirements.md` checklist validates specification quality. This
  checklist is the stakeholder acceptance gate and is deliberately stricter.
