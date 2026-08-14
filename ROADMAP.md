# Roadmap: ITAMS Brownfield Baseline Specifications

This roadmap migrates the existing ITAMS capabilities into small, independently
reviewable Spec Kit baseline specifications. It is a decomposition and review
index, not a parent product specification and not an implementation plan.

**Baseline evidence date**: 2026-07-29

**Authoritative inputs**:

- `CONTEXT.md` for canonical terminology, shared lifecycle rules, and deferred
  product scope
- `docs/adr/` for accepted lasting decisions and rationale
- `docs/research/itams-current-system-baseline.md` for test-verified,
  implementation-only, contradictory, and unknown current-system evidence
- `.specify/memory/constitution.md` for persistence and acceptance rules

## Roadmap conventions

- B-numbers are permanent traceability identifiers. Do not renumber them when
  drafting order or dependencies change.
- Rows are ordered by recommended drafting dependency, not B-number.
- Planned sub-spec paths reserve the expected creation order. If another
  feature consumes a sequence number first, update only the path; keep the
  B-number unchanged.
- A Brownfield Baseline remains editable while `Draft`. Once accepted, its
  requirement content becomes an immutable flow-forward record.
- Every generated `spec.md` must reference its B-number and this roadmap. Once
  created, this roadmap must link to the actual feature directory.
- Implementation-only behavior and unresolved conflicts are evidence, not
  baseline requirements, until an explicit stakeholder decision accepts them.

### Evidence status

- **E1 — strong**: stakeholder intent and passing automated tests cover the core
  behavior.
- **E2 — mixed**: some intent or tests exist, but material behavior is known
  only from implementation.
- **E3 — implementation-led**: most behavior lacks stakeholder intent and
  behavioral test coverage.

### Review status

- **R0 — not started**: evidence exists, but review has not begun.
- **R1 — needs decisions**: listed conflicts or unknowns block acceptance.
- **R2 — ready to draft**: dependencies and material decisions are resolved.
- **R3 — draft review**: a linked baseline `spec.md` is under review.
- **R4 — accepted**: the baseline is accepted and its requirement content is
  immutable.

## Implemented baseline capability roadmap

| ID | Capability | Intent | Explicit scope boundary | Depends on | Evidence status | Review status | Planned sub-spec |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **B1** | Identity, access, and organization | Baseline authentication, Users, Roles, permission codes, Departments, and Locations used across ITAMS. | **In:** login/logout, password change, User administration, Role-permission assignment, active/minimal User directory, Department and Location masters. **Out:** Asset lifecycle behavior, employee self-service, and Department-scoped visibility; Department is organizational data, not an authorization boundary. | — | **E1 — strong:** 9 of 12 backend requirements are test-cited across 32 tests covering privacy, Role/permission gating, Employee scope, token revocation on deactivation, password policy, and the seeded administrator credential. Session lifetime, administrative reset, and account-lifecycle atomicity remain implementation-only. | **R3 — draft review:** clarification resolved C6, Employee visibility and request scope, named Role grants, custom-Role policy, and global versus own/Department visibility. Finding 11, the committed bootstrap credential, was the one item explicitly not carried forward; it was resolved by rotation on 2026-08-13 and no longer blocks. Remaining implementation-only findings require baseline review. | [`specs/003-identity-access-baseline/`](specs/003-identity-access-baseline/) |
| **B6** | Procurement, Vendor, and catalog masters | Baseline completed-purchase recording and the managed Vendor, Category, Brand, Model, and Purchase Mode data it relies on. | **In:** master CRUD, protected deletion, Vendor identity, completed Procurement records, invoice/PO data, and linking/unlinking Assets. **Out:** employee procurement requests, purchase approval, Asset lifecycle transitions, and Service Record operations. | B1 | **E2 — mixed, no open gaps:** 13 of 23 backend requirements are test-cited across 38 tests, and every recorded conformance gap (U-008 to U-015) is closed — arrival records and attestation, archive-not-delete, link history, per-Vendor invoice identity, name normalization, and Model–Brand ownership. 10 backend requirements remain undemonstrated rather than known-broken. | **R3 — draft review:** clarification resolved C7, C9, arrival/date enforcement, archive and link history, linkage cardinality, permissions, invoice/PO identity, master normalization, and B6 audit/Notification triggers. All eight recorded conformance gaps were closed on 2026-08-13. Outstanding for review: Models whose Brand could not be inferred from Asset usage, plus rename/merge (FR-021) and legacy Vendor backfill (FR-022), which are now expressible for the first time. | [`specs/002-procurement-vendor-catalog-baseline/`](specs/002-procurement-vendor-catalog-baseline/) |
| **B2** | Asset register and lifecycle | Baseline Asset identity, status, condition, Custodian, terminal-state rules, files, barcode, condition history, and aggregate history. | **In:** Asset CRUD/search/filter, canonical status and condition, terminal states, direct administrative transitions, Custodian invariants, images/documents, barcode, and condition logs. **Out:** Checkout, Transfer, Service Record, Procurement workflow, AMC workflow, and reporting behavior owned by sibling baselines. | B1, B6 | **E2 — mixed with a strong lifecycle core:** 15 of 24 backend requirements are test-cited across 34 tests; transition, custodian-invariant, and terminal-state rules are well covered. Register search, file handling, barcode, and deletion behavior remain untested. | **R3 — draft review:** clarification resolved C2 and recorded the remaining terminology, retention, file-security, integration, and implementation-conformance findings. The formal baseline-acceptance checklist remains unreviewed, so B2 is not yet immutable or accepted. | [`specs/001-asset-register-lifecycle-baseline/`](specs/001-asset-register-lifecycle-baseline/) |
| **B8** | Notifications and AuditLog | Baseline the shared in-app notification/read-state and operational AuditLog facilities used by capability-specific triggers. | **In:** Notification recipients and read state, mark-one/all-read, unread counts, AuditLog fields, administrative access, filters, and the boundary between shared delivery and trigger ownership. **Out:** email unless accepted, physical Asset audits, and business trigger rules owned by B3–B7. | B1, B2 | **E1 — strong:** 14 of 17 backend requirements are test-cited across 52 tests — the widest coverage of any baseline. Recipient isolation, read state and its retained transition time, the in-app channel, the audit filter contract and result-limit disclosure, minimization, access policy, retention, and both failure boundaries are covered. Every recorded gap is closed. | **R3 — draft review:** clarification resolved in-app-only delivery, audit atomicity and Notification retry/failure behavior, the required AuditLog event set and content limits, Admin/IT Manager access scope, retention periods, and B3–B7 trigger ownership. Every recorded gap was closed on 2026-08-13, including the IT Manager access the policy always named. Ready for acceptance review. | [`specs/004-notifications-audit-baseline/`](specs/004-notifications-audit-baseline/) |
| **B3** | Checkout and check-in | Baseline IT-performed Checkout from `Available` to `Assigned` and check-in back to `Available`. | **In:** actors and `asset_custody_manage`, eligibility, Custodian/department assignment, conditions, remarks, expected return, notifications, rejection cases, and check-in closure. **Out:** approval-gated Transfer, employee self-service, and Service Record behavior except the documented integration boundary. | B1, B2, B8 | **E2 — mixed:** 9 of 24 backend requirements are test-cited and 8 more are partly met, across 25 tests. Single-open-Checkout is now enforced by a database constraint, and department handling, worsened-return remarks, and interrupted closure are covered. Overdue state, Notification recipients and destinations, and rejection auditing remain open. | **R3 — draft review:** clarification resolved department semantics after check-in, the mandatory return condition, expected-return and Overdue rules, AuditLog events, Notification recipients, intake/return remarks, and interrupted-Checkout closure. Register rows 2, 5, 10, 14, and 15 were closed on 2026-08-13; rows 6–9 and 11–13 remain open for review. | [`specs/005-checkout-checkin-baseline/`](specs/005-checkout-checkin-baseline/) |
| **B4** | Approval-gated Transfer | Baseline requested, approved, and rejected custody handoff between Users and departments. | **In:** requester/approver permissions, captured previous custody, target User/department, Pending/Approved/Rejected outcomes, terminal/Service restrictions, notifications, and Transfer document access. **Out:** Store-to-User issuance unless C1 accepts it, Checkout, and employee self-service. | B1, B2, B3, B8 | **E2 — mixed:** 13 of 20 backend requirements are test-cited across 22 tests covering the requested/approved/rejected lifecycle, custody capture, and document access. Concurrent Pending requests, custody drift before approval, and IT Store issuance remain untested. | **R3 — draft review:** clarification resolved C1 (Store-to-User issuance is a Checkout), C8, same-User targets, concurrent Pending requests, custody drift before approval, condition validation, and requester/approver, Notification, and audit policy; remaining implementation-only findings require baseline review. | [`specs/006-transfer-baseline/`](specs/006-transfer-baseline/) |
| **B5** | Service Record lifecycle | Baseline one repair/maintenance event from opening through closure without automatic Custodian restoration. | **In:** Vendor, eligible Asset states, open/close permissions, Custodian clearing, `Under Repair`, interrupted Checkout closure, dates, cost, remarks/outcome, notifications, and return to `Available`. **Out:** Vendor administration, Procurement, Warranty/AMC, and fresh Checkout after service. | B1, B2, B3, B6, B8 | **E2 — mixed:** 9 of 21 backend requirements are test-cited and 4 more partly met, across 22 tests. Eligibility, department clearing, cost at closure, stale-status re-checks, and separated opening/closing remarks are covered. Dates, bill references, and a structured outcome value do not exist yet. | **R3 — draft review:** clarification resolved service eligibility, department semantics, dates, cost/bill/outcome/remarks, and Notification/AuditLog effects. Register rows 1, 2, 3, 4, 9, and 10 were closed on 2026-08-13. Expected-return validation and overdue alerts remain non-baseline delivery scope in CHG-B5-01; rows 5, 6, 8, 11, 14, 15, and 17 remain open for review. | [`specs/007-service-record-baseline/`](specs/007-service-record-baseline/) |
| **B7** | Warranty, AMC, and expiry actions | Baseline manufacturer Warranty, AMC history/state, incomplete contracts, renewal, End Support, and proactive expiry alerts. | **In:** Warranty dates, AMC distinction and Vendor, Incomplete/Active/Ended state, renew/end validation, reasons, history, 30/15/7-day triggers, recipients, and IT Manager notification. **Out:** generic notification storage from B8, Dashboard/report presentation from B9, and unrelated Service Record activity. | B1, B2, B6, B8 | **E1 — strong:** 21 of 31 backend requirements are test-cited and 8 more partly met across 48 tests, with **no backend requirement left unverified**. Warranty/AMC separation, contract state and selection, renewal and End Support validation, alert thresholds and exclusions, and audit atomicity are all covered. The residue is CHG-B7-01 scheduler reliability, which is not baseline scope. | **R3 — draft review:** C5's scheduling, timezone, once-only, and catch-up guarantees are non-baseline delivery scope in CHG-B7-01. FR-029's `CONTEXT.md` reconciliation was discharged on 2026-08-12, and U-007 plus seven U-006 rows were closed on 2026-08-13. Remaining review items are UI destinations and audit content detail. | [`specs/008-warranty-amc-baseline/`](specs/008-warranty-amc-baseline/) |
| **B9** | Dashboard, reports, and exports | Baseline the current read-only operational summaries, report catalog, and PDF/Excel/CSV outputs after their business meaning is accepted. | **In:** Dashboard KPI/chart definitions, report names/columns/filters, access, Lost Asset versus AuditLog reporting, export formats, and branding. **Out:** source lifecycle rules owned by B2–B7 and deferred periodic physical Asset audits. | B1, B2, B3, B4, B5, B6, B7, B8 | **E2 — backend strong, presentation unverifiable:** all 9 backend requirements are demonstrated (6 test-cited, 3 partly met) across 40 tests covering read-only safety, authorization, terminal exclusion, disjoint expiry bands, canonical terminology, and audit projection rules. The rating stays E2 because 20 of B9's 29 requirements are presentation-level and no frontend test runner exists to exercise them. | **R3 — draft review:** desired standard filters, written definitions, export parity beyond CSV, branding corrections, and non-truncating delivery are non-baseline scope in CHG-B9-01. Register rows 5–10 were closed on 2026-08-13. The audit report's replacement title is provisional and must be confirmed in the acceptance record under FR-023. | [`specs/009-dashboard-reports-exports-baseline/`](specs/009-dashboard-reports-exports-baseline/) |

## Flow-forward delivery changes discovered during baseline review

These are prospective Change specifications, not implemented baseline behavior.
They remain Draft and MUST NOT be used to mark the corresponding baseline as
implemented or accepted.

| Change ID | Extends | Delivery intent | Status | Specification |
| --- | --- | --- | --- | --- |
| **CHG-B5-01** | B5 | Validate expected return, derive overdue Service Records, and proactively notify custody operators. | Draft — baseline dependencies unaccepted | [`specs/010-service-record-overdue-alerts-change/`](specs/010-service-record-overdue-alerts-change/) |
| **CHG-B7-01** | B7 | Run Warranty/AMC expiry alerts reliably in production with consistent time, once-only delivery, catch-up, and operator-visible health. | Draft — baseline dependencies unaccepted | [`specs/011-expiry-alert-delivery-reliability-change/`](specs/011-expiry-alert-delivery-reliability-change/) |
| **CHG-B9-01** | B9 | Add report filters and definitions, protected equivalent exports, parseable values, branding rules, and visible completeness. | Draft — baseline dependencies unaccepted | [`specs/012-report-filter-export-parity-change/`](specs/012-report-filter-export-parity-change/) |

## Decision register for baseline acceptance

The decision identifiers below come from
`docs/research/itams-current-system-baseline.md`. Resolving a decision changes
the owning B-row from R1 to R2 only when its other material unknowns are also
closed. The Resolution column records the current decision state and the
clarification session or spec finding that carries it; a documented
implementation conformance gap is delivery work, not a reopened decision.

| Decision | Owning baseline | Acceptance question | Resolution |
| --- | --- | --- | --- |
| **C1** | B3, B4 | Is Store-to-User issuance a Checkout or a Transfer? | **Resolved — Checkout** (B4 clarification 2026-08-04): issuance has no approval gate and is outside Transfer scope. Draft B3 still carries C1 as open blocker U-005 and must absorb this decision before acceptance. |
| **C2** | B2 | Which status, Custodian, and department combinations are valid when creating or directly editing an Asset? | **Resolved — stakeholder-confirmed** (B2 clarification, 2026-07-29): create only as `Available` or `In Storage` with no Custodian; Custodian changes only through Checkout or Transfer. Draft B2 documents a backend/frontend conformance gap. |
| **C3** | B2, B3 | Replace the user-visible term `Assignment` with `Checkout`; any exception requires an explicit `CONTEXT.md` amendment. | **Resolved as intent — conformance pending**: `CONTEXT.md` rejects `Assignment`, and Draft B3 FR-018/AS-005 require `Checkout` on every user-visible surface; Draft B2 records the surviving `Assignment & Warranty` label as a finding requiring correction or an explicit `CONTEXT.md` amendment. |
| **C4** | B7 | How is deliberate no-AMC represented, and should ended AMC history make `has_amc` true? | **Resolved — reconciliation complete** (B7 clarification 2026-08-05): `has_amc` derives from the current contract only — true for `Active`/`Incomplete`, false for `Ended` or absent — dropping the deliberate no-AMC distinction. `CONTEXT.md` **AMC** was amended 2026-08-12 to match, recording the lost distinction as accepted and the data-completeness consequence; B7 FR-029 is discharged and no longer blocks acceptance. |
| **C5** | B7 | What production scheduling and delivery guarantees satisfy proactive 30/15/7-day alerts? | **Resolved** (B7 clarification 2026-08-05): the in-process scheduler also runs under the production server with single-worker mutual exclusion, one organizational timezone, once-only alerts per Asset/coverage/threshold, and operator-visible downtime catch-up. |
| **C6** | B1 | Should Employee access be own-Asset-only, global read-only, or absent, and what does “raise requests” mean in current scope? | **Resolved** (B1 clarification 2026-07-29): Employee visibility is own-Custodian Assets only, including retained `Lost` custody; "raise requests" is not accepted Role intent in current scope. |
| **C7** | B6 | Is physical arrival a procedural Procurement precondition or a system-enforced state? | **Resolved — system-enforced** (B6 clarification 2026-08-03): saving a Procurement requires an Asset arrival record plus a required attestation. |
| **C8** | B4 | Which non-Admin actors may download Transfer PDFs? | **Resolved** (B4 clarification 2026-08-04): any User with `asset_view` may download Transfer PDFs, limited to Transfer records visible under B1; downloads are not audited. |
| **C9** | B6 | Should Procurement edit/delete controls be hidden unless the matching permission is present? | **Resolved** (B6 clarification 2026-08-03): existing B6 action codes govern the controls, reads require non-Employee `asset_view`, and Employees receive no B6 pages; B6 records an implementation conformance gap (OBS-AS-014). |

## Recommended drafting order

1. Create the B1 draft with C6 and its unknowns explicit; use clarification and
   stakeholder review to resolve them before acceptance.
2. Draft and accept B6 so shared master and Vendor semantics are stable.
3. Draft and accept B2 as the central Asset contract.
4. Draft and accept B8 for shared notification and audit semantics.
5. Draft B3, then use its accepted boundary to clarify and accept B4.
6. Draft B5 and B7 once their shared dependencies are accepted; resolve every
   listed decision before either baseline is accepted.
7. Draft B9 last, deriving every metric and report term from accepted source
   baselines.

For each row, use `$speckit-specify` once, then `$speckit-clarify` and
`$speckit-checklist`. Do not generate planning, task, ticket, or implementation
artifacts for a documentation-only baseline when the accepted behavior is
already satisfied.

## Deferred product roadmap — excluded from current baselines

These entries are future product possibilities, not implemented current-system
requirements. They must receive new feature specifications if prioritized.

| ID | Deferred capability | Source and boundary | Depends on | Status | Future sub-spec |
| --- | --- | --- | --- | --- | --- |
| **F1** | Periodic physical Asset audits | Department- or Location-based physical verification against system records. This is distinct from the existing AuditLog and “Asset Audit Report.” Source: `CONTEXT.md`, **Lost**. | B1, B2, B8, B9 | Deferred beyond v1 | — |
| **F2** | Employee self-service Checkout | Employee-initiated Checkout for pooled/available Assets. Current IT-performed Checkout remains B3. Source: `CONTEXT.md`, **Checkout**. | B1, B2, B3 | Possible future scope | — |
| **F3** | Procurement request workflow | Employee- or team-lead-initiated request and approval before purchase. Current completed-purchase recording remains B6. Source: `CONTEXT.md`, **Procurement**. | B1, B6 | Intentionally deferred | — |

Moving expiry scheduling to an external production scheduler is an engineering
resolution candidate for C5, not a separately accepted deferred product
capability. Frontend lint findings, missing frontend behavioral tests, and
bundle-size warnings are likewise engineering-quality evidence, not baseline
product requirements.
