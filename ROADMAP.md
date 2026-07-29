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
| **B1** | Identity, access, and organization | Baseline authentication, Users, Roles, permission codes, Departments, and Locations used across ITAMS. | **In:** login/logout, password change, User administration, Role-permission assignment, active/minimal User directory, Department and Location masters. **Out:** Asset lifecycle behavior, employee self-service, and department-specific data scoping until explicitly decided. | — | **E2 — mixed:** four passing privacy/authorization tests; Role matrix and most CRUD behavior are implementation evidence. | **R1 — needs decisions:** resolve C6, named Role grants, custom-Role policy, and global versus own/department data visibility. | `specs/002-identity-access-baseline/` |
| **B6** | Procurement, Vendor, and catalog masters | Baseline completed-purchase recording and the managed Vendor, Category, Brand, Model, and Purchase Mode data it relies on. | **In:** master CRUD, protected deletion, Vendor identity, completed Procurement records, invoice/PO data, and linking/unlinking Assets. **Out:** employee procurement requests, purchase approval, Asset lifecycle transitions, and Service Record operations. | B1 | **E2 — mixed:** strong concept intent and protected-deletion tests; Procurement CRUD and arrival behavior are implementation-only. | **R1 — needs decisions:** resolve C7 and C9, physical-arrival enforcement, date rules, deletion/history behavior, and whether Assets may remain without Procurement. | `specs/003-procurement-vendor-catalog-baseline/` |
| **B2** | Asset register and lifecycle | Baseline Asset identity, status, condition, Custodian, terminal-state rules, files, barcode, condition history, and aggregate history. | **In:** Asset CRUD/search/filter, canonical status and condition, terminal states, direct administrative transitions, Custodian invariants, images/documents, barcode, and condition logs. **Out:** Checkout, Transfer, Service Record, Procurement workflow, AMC workflow, and reporting behavior owned by sibling baselines. | B1, B6 | **E2 — mixed with strong lifecycle core:** extensive passing transition tests; register, file, barcode, and deletion behavior are mostly implementation-only. | **R4 — accepted:** baseline accepted 2026-07-29; requirement and acceptance content is immutable. Documented unresolved findings and implementation conformance gaps remain visible in the accepted baseline. | [`specs/001-asset-register-lifecycle-baseline/`](specs/001-asset-register-lifecycle-baseline/) |
| **B8** | Notifications and AuditLog | Baseline the shared in-app notification/read-state and operational AuditLog facilities used by capability-specific triggers. | **In:** Notification recipients and read state, mark-one/all-read, unread counts, AuditLog fields, administrative access, filters, and the boundary between shared delivery and trigger ownership. **Out:** email unless accepted, physical Asset audits, and business trigger rules owned by B3–B7. | B1, B2 | **E2 — mixed:** selected notification side effects have passing tests; generic notification and audit behavior is implementation-only. | **R1 — needs decisions:** define delivery channels, failure behavior, required audit events, access scope, and retention. | `specs/004-notifications-audit-baseline/` |
| **B3** | Checkout and check-in | Baseline IT-performed Checkout from `Available` to `Assigned` and check-in back to `Available`. | **In:** actors and `asset_custody_manage`, eligibility, Custodian/department assignment, conditions, remarks, expected return, notifications, rejection cases, and check-in closure. **Out:** approval-gated Transfer, employee self-service, and Service Record behavior except the documented integration boundary. | B1, B2, B8 | **E1 — strong:** stakeholder intent plus lifecycle and endpoint round-trip tests cover the core behavior. | **R1 — needs decisions:** confirm department semantics after check-in, default return condition, expected-return obligations, and audit requirements. | `specs/005-checkout-checkin-baseline/` |
| **B4** | Approval-gated Transfer | Baseline requested, approved, and rejected custody handoff between Users and departments. | **In:** requester/approver permissions, captured previous custody, target User/department, Pending/Approved/Rejected outcomes, terminal/Service restrictions, notifications, and Transfer document access. **Out:** Store-to-User issuance unless C1 accepts it, Checkout, and employee self-service. | B1, B2, B3, B8 | **E2 — mixed:** strong passing tests for the assigned-Asset lifecycle; IT Store flow, PDF access, and several integrity rules are implementation-only. | **R1 — needs decisions:** resolve C1 and C8 plus same-User Transfer, concurrent requests, changes before approval, and condition validation. | `specs/006-transfer-baseline/` |
| **B5** | Service Record lifecycle | Baseline one repair/maintenance event from opening through closure without automatic Custodian restoration. | **In:** Vendor, eligible Asset states, open/close permissions, Custodian clearing, `Under Repair`, interrupted Checkout closure, dates, cost, remarks/outcome, notifications, and return to `Available`. **Out:** Vendor administration, Procurement, Warranty/AMC, and fresh Checkout after service. | B1, B2, B3, B6, B8 | **E1 — strong:** `CONTEXT.md`, ADR-0001, lifecycle tests, and endpoint tests cover the core behavior. | **R1 — needs decisions:** confirm whether `In Storage` is service-eligible, department semantics while servicing, bill/document expectations, and mandatory audit events. | `specs/007-service-record-baseline/` |
| **B7** | Warranty, AMC, and expiry actions | Baseline manufacturer Warranty, AMC history/state, incomplete contracts, renewal, End Support, and proactive expiry alerts. | **In:** Warranty dates, AMC distinction and Vendor, Incomplete/Active/Ended state, renew/end validation, reasons, history, 30/15/7-day triggers, recipients, and IT Manager notification. **Out:** generic notification storage from B8, Dashboard/report presentation from B9, and unrelated Service Record activity. | B1, B2, B6, B8 | **E2 — mixed with strong action tests:** AMC actions and exact-date alert generation are tested; flag semantics and operational delivery are unresolved. | **R1 — needs decisions:** resolve C4 and C5, deliberate no-AMC representation, initial-entry validation, Vendor capture, delivery channel, and production scheduling guarantees. | `specs/008-warranty-amc-baseline/` |
| **B9** | Dashboard, reports, and exports | Baseline the current read-only operational summaries, report catalog, and PDF/Excel/CSV outputs after their business meaning is accepted. | **In:** Dashboard KPI/chart definitions, report names/columns/filters, access, Lost Asset versus AuditLog reporting, export formats, and branding. **Out:** source lifecycle rules owned by B2–B7 and deferred periodic physical Asset audits. | B1, B2, B3, B4, B5, B6, B7, B8 | **E3 — implementation-led:** one AMC-report edge case is tested; most calculations, access, presentation, and exports exist only in implementation. | **R1 — needs decisions:** approve metric/column definitions, global versus scoped visibility, export parity, branding, performance expectations, and the meaning of “Asset Audit Report.” | `specs/009-dashboard-reports-exports-baseline/` |

## Decision register for baseline acceptance

The decision identifiers below come from
`docs/research/itams-current-system-baseline.md`. Resolving a decision changes
the owning B-row from R1 to R2 only when its other material unknowns are also
closed.

| Decision | Owning baseline | Acceptance question |
| --- | --- | --- |
| **C1** | B3, B4 | Is Store-to-User issuance a Checkout or a Transfer? |
| **C2** | B2 | Which status, Custodian, and department combinations are valid when creating or directly editing an Asset? |
| **C3** | B2, B3 | Replace the user-visible term `Assignment` with `Checkout`; any exception requires an explicit `CONTEXT.md` amendment. |
| **C4** | B7 | How is deliberate no-AMC represented, and should ended AMC history make `has_amc` true? |
| **C5** | B7 | What production scheduling and delivery guarantees satisfy proactive 30/15/7-day alerts? |
| **C6** | B1 | Should Employee access be own-Asset-only, global read-only, or absent, and what does “raise requests” mean in current scope? |
| **C7** | B6 | Is physical arrival a procedural Procurement precondition or a system-enforced state? |
| **C8** | B4 | Which non-Admin actors may download Transfer PDFs? |
| **C9** | B6 | Should Procurement edit/delete controls be hidden unless the matching permission is present? |

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
