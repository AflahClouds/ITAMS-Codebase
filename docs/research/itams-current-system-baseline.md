# ITAMS Current-System Baseline

**Status:** Evidence inventory — not an accepted product specification
**Prepared:** 2026-07-29
**Purpose:** Support brownfield migration into bounded Spec Kit baseline specifications

## Reading rules

This document deliberately separates product intent from observed behavior:

- `CONTEXT.md` is the stakeholder-authoritative source for terminology, shared
  lifecycle rules, and explicitly deferred scope.
- `docs/adr/` records accepted lasting decisions and their rationale.
- Passing automated tests verify current behavior only; they do not create
  product intent by themselves.
- Backend or frontend behavior without a confirming authoritative source or
  automated test is implementation-only evidence and needs stakeholder review
  before it becomes a baseline requirement.
- A contradiction identifies evidence that cannot safely be promoted into a
  specification without a decision.

These rules follow the repository's domain and Spec Kit governance.
(Sources: `AGENTS.md`; `docs/agents/domain.md`;
`.specify/memory/constitution.md`)

## Research scope and validation

The review covered the domain glossary and ADR, Django models, serializers,
lifecycle services, permissions, endpoints, migrations, automated tests,
reporting and export code, React routes, permission gates, pages, API calls,
and existing repository documentation. The only product-focused authoritative
domain sources found were `CONTEXT.md` and ADR-0001; `frontend/README.md` is
unchanged Vite boilerplate, while the existing research notes concern Spec Kit
adoption rather than ITAMS requirements.
(Sources: `CONTEXT.md`; `docs/adr/0001-service-record-lifecycle.md`;
`frontend/README.md`; `docs/research/spec-kit-adoption.md`;
`docs/research/brownfield-spec-baseline-migration.md`)

Validation performed during this research:

- `backend/Env/Scripts/python.exe manage.py test` ran 70 tests successfully in
  252.360 seconds; Django's system check reported no issues. The test sources
  are `backend/accounts/tests.py`, `backend/assets/tests.py`, and
  `backend/reporting/tests.py`.
- No frontend behavioral test files or test script were found. The frontend
  package exposes only `dev`, `build`, `lint`, and `preview`; therefore
  frontend behavior below remains implementation-only unless a backend test
  independently verifies the same effect.
  (Source: `frontend/package.json`)
- `npm run build` completed successfully with Vite 8.1.3 and 2,198 modules.
  The build warned that the main JavaScript chunk was 1,629.01 kB, above
  Vite's 500 kB warning threshold. This proves buildability, not behavior.
  (Sources: `frontend/package.json`; `frontend/vite.config.js`)
- `npm run lint` completed with 26 findings: 12 errors and 14 warnings.
  These are engineering-health findings, not product behavior evidence.
  (Sources: `frontend/package.json`; `frontend/eslint.config.js`)

## Evidence coverage summary

| Capability | Stakeholder intent | Automated-test evidence | Implementation-only evidence | Baseline readiness |
| --- | --- | --- | --- | --- |
| Authentication, users, roles, permissions | Partial | Privacy/API authorization only | Extensive | Needs decisions on role and data-scope policy |
| Asset registry and lifecycle | Strong | Strong for lifecycle transitions | Extensive for CRUD, files, barcode, history | Ready after resolving create-time bypasses |
| Checkout/check-in | Strong | Strong | UI and audit details | Largely ready |
| Transfer | Strong | Strong for assigned-Asset flow | UI, PDFs, unassigned-Asset flow | Needs Transfer-vs-Checkout decision |
| Service Record | Strong plus ADR | Strong | UI/reporting details | Largely ready |
| Procurement and Vendor | Strong at concept level | Protected master deletion only | Extensive CRUD behavior | Needs arrival/workflow validation decisions |
| Warranty and AMC | Strong | Strong for AMC actions and exact-date alerts | Scheduler and reporting details | Needs AMC flag and delivery decisions |
| Notifications and audit logging | Partial side-effect intent | Selected lifecycle notifications only | Extensive | Needs coverage and retention decisions |
| Dashboard, reports, exports | Vendor-report intent only | One AMC report edge case | Extensive | Mostly implementation-only |

## 1. Stakeholder-stated intent

### 1.1 System and Asset model

- ITAMS tracks physical IT Assets across procurement, Checkout, Transfer,
  servicing, and end of life.
  (Source: `CONTEXT.md`, introduction)
- An Asset has an independent `status` and `condition`. Canonical statuses are
  `Available`, `Assigned`, `Under Repair`, `In Storage`, `Sold`, `Scrapped`,
  and `Lost`; canonical conditions are `New`, `Good`, `Average`, `Damaged`,
  and `Repair Required`.
  (Source: `CONTEXT.md`, **Asset**)
- `Sold`, `Scrapped`, and `Lost` are terminal statuses. `Disposed` is rejected
  terminology, and `Scrapped` is not a condition.
  (Source: `CONTEXT.md`, **Asset**, **Sold**, and **Scrapped**)
- `Lost` is recorded reactively, not through a periodic physical-audit process.
  The current Custodian is retained to preserve accountability.
  (Source: `CONTEXT.md`, **Lost** and **Custodian**)

### 1.2 Custodian, Checkout, and check-in

- Custodian means the User currently holding an Asset. Checkout or Transfer
  sets Custodian; check-in or opening a Service Record clears it. Asset
  `status`, rather than Custodian presence, is authoritative for availability.
  `Lost` is the explicit exception that retains the last Custodian.
  (Source: `CONTEXT.md`, **Custodian**)
- Checkout moves an Asset `Available → Assigned` to a User and check-in moves
  it back to `Available`. It has no pending/approval state and is distinct
  from Transfer.
  (Source: `CONTEXT.md`, **Checkout**)
- `Checkout`, not `Assignment`, is the canonical term. In current scope,
  IT Manager or IT Staff performs each Checkout in person using
  `asset_custody_manage`; employees do not check Assets out to themselves.
  (Source: `CONTEXT.md`, **Checkout**)

### 1.3 Transfer

- Transfer is an approval-gated handoff between two Users and departments.
  Approval changes custody; rejection leaves the Asset untouched.
  (Source: `CONTEXT.md`, **Transfer**)
- HR or IT Manager requests Transfer on an employee's behalf. IT Manager or
  IT Staff approves it; it is not employee self-service.
  (Source: `CONTEXT.md`, **Transfer**)

### 1.4 Procurement and Vendor

- Procurement records a completed purchase after the Asset physically arrives.
  It includes Vendor, invoice, and purchase-order information, is created by IT,
  and is not a request/approval workflow.
  (Source: `CONTEXT.md`, **Procurement**)
- Vendor is a first-class managed entity shared by Procurement and Service
  Record so vendor-grouped reporting is reliable.
  (Sources: `CONTEXT.md`, **Vendor**;
  `docs/adr/0001-service-record-lifecycle.md`)

### 1.5 Service Record

- A Service Record represents one repair or maintenance event, including
  Vendor, sent/returned dates, cost/bill information, and outcome.
  (Source: `CONTEXT.md`, **Service Record**)
- Opening a Service Record clears Custodian, moves the Asset to
  `Under Repair`, and follows the same one-Asset/one-state pattern as check-in.
  Closing it moves the Asset to `Available` and never restores the previous
  Custodian automatically; IT must perform a fresh Checkout.
  (Sources: `CONTEXT.md`, **Service Record**;
  `docs/adr/0001-service-record-lifecycle.md`)
- Keeping custody during servicing and auto-restoring the previous Custodian
  were explicitly considered and rejected.
  (Source: `docs/adr/0001-service-record-lifecycle.md`)

### 1.6 Warranty and AMC

- Warranty is manufacturer coverage with start/end dates. AMC is a distinct,
  optional paid maintenance contract with its own dates.
  (Source: `CONTEXT.md`, **Warranty** and **AMC**)
- The intended AMC model distinguishes deliberate no-AMC
  (`has_amc = False`) from an existing but date-incomplete AMC
  (`has_amc = True` with empty dates).
  (Source: `CONTEXT.md`, **AMC**)
- Warranty and AMC alerts are proactively pushed at 30, 15, and 7 days before
  expiry to IT Manager and IT Staff.
  (Source: `CONTEXT.md`, **AMC**)
- IT Staff responds to an AMC alert by either renewing with new dates or ending
  support with a recorded reason. Either action notifies IT Manager. Warranty
  does not have this renew/end workflow.
  (Source: `CONTEXT.md`, **AMC**)

## 2. Behavior verified by automated tests

The statements in this section describe current verified behavior. They are not
automatically accepted requirements unless section 1 confirms them.

### 2.1 Authentication privacy and directory access

- A profile with no relevant permission receives `403` from full User list and
  detail, Role, Permission, and Setting endpoints.
  (Test: `backend/accounts/tests.py::PrivacyAuthorizationTests::test_ordinary_user_cannot_read_privileged_apis`)
- `user_management` permits reading a full User record, including email and
  linked login username.
  (Test: `backend/accounts/tests.py::PrivacyAuthorizationTests::test_user_manager_can_read_full_user_records`)
- `asset_view` permits a minimal active-User directory containing only `id`,
  `user_name`, `emp_id`, and `department_name`; disabled profiles are excluded.
  (Test: `backend/accounts/tests.py::PrivacyAuthorizationTests::test_asset_user_gets_only_minimal_active_user_directory`)
- `settings_access` does not grant access to the administrative Setting API.
  (Test: `backend/accounts/tests.py::PrivacyAuthorizationTests::test_settings_access_does_not_expose_admin_configuration`)

### 2.2 Protected master data

- Category, Brand, Model, PurchaseMode, and Vendor rows referenced by operational
  data cannot be deleted and deletion does not remove the Asset or Procurement.
  Direct model deletion raises `ProtectedError`.
  (Test: `backend/assets/tests.py::ProtectedMasterDataTests::test_referenced_master_records_cannot_delete_operational_data`)
- The same referenced-record deletion through the API returns `409` and a
  stable explanatory message.
  (Test: `backend/assets/tests.py::ProtectedMasterDataTests::test_delete_api_returns_conflict_for_referenced_master_records`)
- Unreferenced master rows remain deletable.
  (Test: `backend/assets/tests.py::ProtectedMasterDataTests::test_unused_master_records_can_still_be_deleted`)

### 2.3 Checkout and check-in

- Checkout assigns an `Available` Asset, sets the User as Custodian, copies the
  User's department when present, and defaults checkout condition from the
  Asset.
  (Test: `backend/assets/tests.py::CheckoutLifecycleTests::test_check_out_assigns_asset_to_user_and_their_department`)
- Checkout persists intake remarks and notifies the new Custodian.
  (Tests: `backend/assets/tests.py::CheckoutLifecycleTests::test_check_out_persists_intake_remarks`;
  `backend/assets/tests.py::CheckoutLifecycleTests::test_check_out_notifies_the_new_custodian`)
- Checkout rejects a non-`Available` Asset.
  (Test: `backend/assets/tests.py::CheckoutLifecycleTests::test_check_out_rejects_an_unavailable_asset`)
- Check-in closes the Checkout as `Returned`, sets return date and remarks,
  changes the Asset to `Available`, clears Custodian, and applies the submitted
  valid condition.
  (Test: `backend/assets/tests.py::CheckoutLifecycleTests::test_check_in_returns_asset_to_available_with_new_condition`)
- Check-in rejects an already closed Checkout and rejects a condition outside
  the canonical condition set.
  (Tests: `backend/assets/tests.py::CheckoutLifecycleTests::test_check_in_rejects_an_already_closed_checkout`;
  `backend/assets/tests.py::CheckoutLifecycleTests::test_check_in_rejects_an_invalid_condition`)
- API creation and check-in require `asset_custody_manage`, and the permitted
  round trip returns an `Open` Checkout as `Returned`.
  (Tests: `backend/assets/tests.py::CheckoutTransferEndpointTests::test_checkout_create_requires_asset_custody_manage_permission`;
  `backend/assets/tests.py::CheckoutTransferEndpointTests::test_checkout_create_and_checkin_round_trip`)

### 2.4 Transfer

- A Transfer request records `Pending`, the current Custodian and department,
  the target department, and notifies Users who have
  `asset_custody_manage`.
  (Tests: `backend/assets/tests.py::TransferLifecycleTests::test_request_transfer_captures_the_current_owner_and_department`;
  `backend/assets/tests.py::TransferLifecycleTests::test_request_transfer_notifies_users_with_approval_permission`)
- Approval changes the Transfer to `Approved`, reassigns Custodian and
  department, sets Asset status to `Assigned`, and applies the Transfer's
  condition.
  (Test: `backend/assets/tests.py::TransferLifecycleTests::test_approve_reassigns_custodian_department_and_condition`)
- Rejection changes only the request outcome and leaves Asset custody and
  department untouched.
  (Test: `backend/assets/tests.py::TransferLifecycleTests::test_reject_leaves_the_asset_untouched`)
- A processed Transfer cannot be approved or rejected again.
  (Tests: `backend/assets/tests.py::TransferLifecycleTests::test_approve_rejects_an_already_processed_transfer`;
  `backend/assets/tests.py::TransferLifecycleTests::test_reject_rejects_an_already_processed_transfer`)
- Request and approval both reject terminal Assets; request and approval also
  reject an Asset that is `Under Repair`, including a status change that occurs
  after the request.
  (Tests: `backend/assets/tests.py::TransferLifecycleTests::test_request_transfer_rejects_a_terminal_asset`;
  `backend/assets/tests.py::TransferLifecycleTests::test_approve_rejects_an_asset_that_turned_terminal_after_the_request`;
  `backend/assets/tests.py::TransferLifecycleTests::test_request_transfer_rejects_an_asset_under_repair`;
  `backend/assets/tests.py::TransferLifecycleTests::test_approve_rejects_an_asset_sent_for_service_after_the_request`)
- API request creation requires `transfer_request`; approval/rejection round
  trips work for a User with the relevant permission codes, and the response
  exposes `TRF-<five digits>`.
  (Tests: `backend/assets/tests.py::CheckoutTransferEndpointTests::test_transfer_request_requires_transfer_request_permission`;
  `backend/assets/tests.py::CheckoutTransferEndpointTests::test_transfer_request_and_approve_round_trip`;
  `backend/assets/tests.py::CheckoutTransferEndpointTests::test_transfer_reject_round_trip`)

### 2.5 Service Record

- Opening Service creates an `Open` record for a Vendor, moves the Asset to
  `Under Repair`, clears Custodian, and notifies the previous Custodian.
  (Tests: `backend/assets/tests.py::ServiceRecordLifecycleTests::test_open_service_clears_custodian_and_marks_under_repair`;
  `backend/assets/tests.py::ServiceRecordLifecycleTests::test_open_service_notifies_the_previous_custodian`)
- Opening Service closes an interrupted open Checkout as `Returned`, with a
  return date, before moving the Asset to `Under Repair`.
  (Test: `backend/assets/tests.py::ServiceRecordLifecycleTests::test_open_service_closes_the_open_checkout_it_interrupts`)
- Opening Service rejects Assets already `Under Repair` or terminal.
  (Tests: `backend/assets/tests.py::ServiceRecordLifecycleTests::test_open_service_rejects_an_asset_already_under_repair`;
  `backend/assets/tests.py::ServiceRecordLifecycleTests::test_open_service_rejects_a_terminal_asset`)
- Closing Service records cost and return date, marks the record `Closed`, and
  returns the Asset to `Available` without restoring Custodian. Closing an
  already closed record is rejected.
  (Tests: `backend/assets/tests.py::ServiceRecordLifecycleTests::test_close_service_returns_asset_to_available_without_reassigning_custodian`;
  `backend/assets/tests.py::ServiceRecordLifecycleTests::test_close_service_rejects_an_already_closed_record`)
- Service creation requires `asset_custody_manage`, and the permitted create
  and close endpoints complete a full round trip.
  (Tests: `backend/assets/tests.py::ServiceRecordEndpointTests::test_service_create_requires_asset_custody_manage_permission`;
  `backend/assets/tests.py::ServiceRecordEndpointTests::test_service_open_and_close_round_trip`)

### 2.6 Asset status transitions

- A terminal status cannot be reversed through Asset update.
  (Test: `backend/assets/tests.py::AssetStatusTransitionTests::test_cannot_reverse_out_of_a_terminal_status`)
- Entering `Sold` clears Custodian even if the request tries to retain it;
  entering `Lost` retains Custodian even if the request tries to clear it.
  (Tests: `backend/assets/tests.py::AssetStatusTransitionTests::test_entering_sold_clears_custodian_even_if_payload_keeps_it`;
  `backend/assets/tests.py::AssetStatusTransitionTests::test_entering_lost_retains_custodian_even_if_payload_clears_it`)
- A direct administrative `Available → In Storage` change succeeds, and an
  unrelated edit to an `Assigned` Asset does not disturb status or Custodian.
  (Tests: `backend/assets/tests.py::AssetStatusTransitionTests::test_administrative_status_edits_are_unaffected`;
  `backend/assets/tests.py::AssetStatusTransitionTests::test_editing_unrelated_fields_without_a_status_change_is_unaffected`)
- Direct update cannot enter `Assigned` or `Under Repair`, leave either
  lifecycle-managed status for a nonterminal status, or move directly between
  the two.
  (Tests: `backend/assets/tests.py::AssetStatusTransitionTests::test_cannot_enter_assigned_by_direct_edit`;
  `backend/assets/tests.py::AssetStatusTransitionTests::test_cannot_enter_under_repair_by_direct_edit`;
  `backend/assets/tests.py::AssetStatusTransitionTests::test_cannot_leave_assigned_by_direct_edit`;
  `backend/assets/tests.py::AssetStatusTransitionTests::test_cannot_leave_under_repair_by_direct_edit`;
  `backend/assets/tests.py::AssetStatusTransitionTests::test_cannot_move_directly_between_assigned_and_under_repair`)
- Direct transition from `Assigned` to `Sold` and from `Under Repair` to
  `Lost` remains permitted.
  (Tests: `backend/assets/tests.py::AssetStatusTransitionTests::test_disposal_is_still_allowed_directly_from_assigned`;
  `backend/assets/tests.py::AssetStatusTransitionTests::test_lost_is_still_allowed_directly_from_under_repair`)
- Entering a terminal status auto-closes any open Checkout or Service Record.
  (Tests: `backend/assets/tests.py::AssetStatusTransitionTests::test_entering_terminal_status_closes_the_open_checkout`;
  `backend/assets/tests.py::AssetStatusTransitionTests::test_entering_terminal_status_closes_the_open_service_record`)

### 2.7 AMC state and actions

- Setting `has_amc = True` without dates creates one `Incomplete` contract;
  later supplying both dates completes that same row as `Active`.
  (Tests: `backend/assets/tests.py::AmcIncompleteStateTests::test_checking_has_amc_without_dates_creates_an_incomplete_contract`;
  `backend/assets/tests.py::AmcIncompleteStateTests::test_supplying_dates_later_completes_the_incomplete_contract`)
- Renewing an incomplete AMC ends it and creates a new active contract; ending
  support can also end an incomplete contract. A newly created incomplete row
  is treated as latest even after an older fully dated ended row.
  (Tests: `backend/assets/tests.py::AmcIncompleteStateTests::test_renew_amc_supersedes_an_incomplete_contract`;
  `backend/assets/tests.py::AmcIncompleteStateTests::test_end_amc_support_can_end_an_incomplete_contract`;
  `backend/assets/tests.py::AmcIncompleteStateTests::test_incomplete_contract_created_after_an_ended_one_is_correctly_latest`)
- Renewal sets new dates/status, ends the previous contract with reason
  `Renewed`, preserves contract history, and notifies an active User whose
  Role is named `IT Manager`.
  (Tests: `backend/assets/tests.py::AmcActionTests::test_renew_amc_sets_dates_and_notifies_it_manager`;
  `backend/assets/tests.py::AmcActionTests::test_renew_amc_ends_previous_contract_and_creates_new_one`)
- Renewal rejects a terminal Asset, unparseable dates, and an end date not
  after the start date.
  (Tests: `backend/assets/tests.py::AmcActionTests::test_renew_amc_rejects_a_terminal_asset`;
  `backend/assets/tests.py::AmcActionTests::test_renew_amc_rejects_an_unparseable_date`;
  `backend/assets/tests.py::AmcActionTests::test_renew_amc_rejects_end_before_start`)
- Ending support requires a nonempty reason and an active/incomplete contract;
  success records `Ended` and the reason and notifies IT Manager.
  (Tests: `backend/assets/tests.py::AmcActionTests::test_end_amc_support_requires_a_reason`;
  `backend/assets/tests.py::AmcActionTests::test_end_amc_support_rejects_when_no_active_amc`;
  `backend/assets/tests.py::AmcActionTests::test_end_amc_support_sets_status_and_notifies_it_manager`)

### 2.8 Expiry alerts and reporting edge case

- Calling the expiry-check function on an exact 30-day Warranty threshold or
  exact 7-day active AMC threshold creates an in-app Notification for a User
  with `asset_custody_manage`.
  (Tests: `backend/assets/tests.py::ExpiryAlertTests::test_warranty_at_a_threshold_notifies_recipients`;
  `backend/assets/tests.py::ExpiryAlertTests::test_active_amc_at_a_threshold_notifies_recipients`)
- The same function is silent for a Warranty at 29 days and an ended AMC at
  the 15-day threshold.
  (Tests: `backend/assets/tests.py::ExpiryAlertTests::test_warranty_not_at_a_threshold_is_silent`;
  `backend/assets/tests.py::ExpiryAlertTests::test_ended_amc_at_a_threshold_is_silent`)
- The AMC expiry report handles an ended contract whose dates were never
  entered and labels it as cancelled before dates were entered.
  (Test: `backend/reporting/tests.py::AmcExpiryReportTests::test_report_does_not_crash_on_a_contract_ended_before_dates_were_entered`)

## 3. Behavior found only in implementation

Unless section 1 or 2 independently confirms a statement, the behavior in this
section is not yet product intent.

### 3.1 Authentication, Users, Roles, and organization

- The backend uses DRF token authentication with login, logout, current-user,
  and change-password endpoints. Login success/failure and logout/password
  change are selectively audit logged; password change enforces a local
  six-character minimum and rotates the token.
  (Sources: `backend/itams/settings.py`; `backend/accounts/urls.py`;
  `backend/accounts/views.py`)
- User profiles optionally link to Django login accounts. User create/update
  can create or rename the account, change its password, and deactivate the
  account when profile status becomes `Disabled`.
  (Sources: `backend/accounts/models.py`;
  `backend/accounts/serializers.py`)
- The Admin Role and Django superusers bypass normal permission-code checks.
  Other active profiles rely on Role-to-Permission membership.
  (Sources: `backend/accounts/models.py`;
  `backend/core/permissions.py`)
- User deletion is Admin-only, cannot delete the current User, and refuses to
  delete a User who still holds Assets.
  (Source: `backend/accounts/views.py`)
- Migrations seed named roles, departments, locations, and a default
  administrative login with a hard-coded initial password. This is deployment
  and security evidence, not confirmed product intent.
  (Source: `backend/accounts/migrations/0002_seed_rbac_and_org.py`)

### 3.2 Master data

- Department and Location are unique-name masters; Category, Brand, Model, and
  PurchaseMode are also unique-name masters. Vendor additionally stores contact
  person, phone, and email.
  (Sources: `backend/accounts/models.py`; `backend/catalog/models.py`)
- Reads of Department, Location, and catalog masters require authentication
  but no specific permission code; writes use `settings_access`. The React
  Masters page manages Department, Location, Category, Brand, Model, and
  PurchaseMode, while Vendor has separate list/create/edit/delete pages.
  (Sources: `backend/accounts/views.py`; `backend/catalog/views.py`;
  `frontend/src/pages/admin/Masters.jsx`; `frontend/src/App.jsx`)
- `backend/catalog/tests.py` and `backend/core/tests.py` contain no substantive
  tests. Protected deletion is the only automated catalog behavior captured in
  section 2.
  (Sources: `backend/catalog/tests.py`; `backend/core/tests.py`;
  `backend/assets/tests.py`)

### 3.3 Asset register, history, files, and barcode

- Asset identity includes unique Asset ID, tag number, and serial number, with
  category, brand, model, optional Procurement, financial fields, status,
  condition, Location, Custodian, department, Warranty dates, notes, and a
  barcode path.
  (Source: `backend/assets/models.py`)
- Asset list supports status/category filters and a text search over Asset ID,
  name, tag number, and serial number. CRUD is mapped respectively to
  `asset_view`, `asset_create`, `asset_edit`, and `asset_delete`.
  (Source: `backend/assets/views.py`)
- Create and update regenerate a Code128 barcode from the tag number and audit
  the operation.
  (Sources: `backend/assets/views.py`; `backend/assets/barcodes.py`)
- Asset detail aggregates Checkout, Transfer, condition-log, Service Record,
  and AMC histories.
  (Sources: `backend/assets/views.py`;
  `frontend/src/pages/asset/Detail.jsx`)
- Users with `asset_edit` can append condition-inspection rows and upload
  images/documents. Document versions increment per Asset and document type;
  upload extension allowlists are configured in Django settings.
  (Sources: `backend/assets/views.py`; `backend/assets/models.py`;
  `backend/itams/settings.py`; `frontend/src/pages/asset/Detail.jsx`)
- The React Asset form exposes all statuses and conditions, Custodian and
  department, Warranty/AMC fields, and financial fields. The edit UI mirrors
  backend update restrictions, but the create UI exposes every status.
  (Sources: `frontend/src/pages/asset/Create.jsx`;
  `frontend/src/pages/asset/Edit.jsx`)

### 3.4 Checkout, Transfer, and Service UI/API details

- Checkout list/retrieve requires `asset_view`; create/check-in requires
  `asset_custody_manage`. The UI fetches only `Available` Assets for creation
  and shows check-in only for open records.
  (Sources: `backend/assets/views.py`;
  `frontend/src/pages/checkout/Create.jsx`;
  `frontend/src/pages/checkout/Checkouts.jsx`)
- The check-in endpoint defaults a missing condition to `Good`; check-in also
  notifies the Checkout User, but those two details have no dedicated tests.
  (Sources: `backend/assets/views.py`; `backend/assets/checkout.py`)
- Check-in clears Custodian but does not clear Asset department.
  (Source: `backend/assets/checkout.py`)
- Transfer list/retrieve requires `asset_view`, request requires
  `transfer_request`, and approval/rejection requires
  `asset_custody_manage`. Approval/rejection emits in-app notifications and
  lifecycle actions are audit logged.
  (Sources: `backend/assets/views.py`; `backend/assets/transfer.py`)
- Transfer creation accepts an optional explicit target department, condition,
  and remarks. No serializer validation constrains Transfer condition to the
  canonical Asset condition set.
  (Sources: `backend/assets/serializers.py`;
  `backend/assets/transfer.py`;
  `frontend/src/pages/transfer/Create.jsx`)
- A transfer-document endpoint builds a branded PDF with Asset, previous/new
  owner and department, request/approval, condition, and signature fields.
  (Sources: `backend/assets/views.py`; `backend/core/exports.py`)
- Service list/retrieve requires `asset_view`; open/close requires
  `asset_custody_manage`. The frontend offers `Available` and `Assigned`
  Assets, while the backend also permits any nonterminal status other than
  `Under Repair`.
  (Sources: `backend/assets/views.py`; `backend/assets/service.py`;
  `frontend/src/pages/service/Create.jsx`)

### 3.5 Procurement

- Procurement requires PurchaseMode, Vendor, purchase date, invoice date, and a
  unique invoice number; PO number is optional. A record can link multiple
  Assets, and an Asset cannot be linked to a different Procurement through the
  serializer.
  (Sources: `backend/assets/models.py`;
  `backend/assets/serializers.py`)
- Updating a Procurement can attach and detach Assets. Deleting a Procurement
  leaves linked Assets in place with `procurement = null`.
  (Sources: `backend/assets/serializers.py`;
  `backend/assets/models.py`;
  `backend/assets/views.py`)
- Procurement list/retrieve uses `asset_view`; create, update, and delete reuse
  Asset CRUD permission codes. The UI selects previously unlinked Assets and
  has no request or approval state.
  (Sources: `backend/assets/views.py`;
  `frontend/src/pages/procurement/Create.jsx`;
  `frontend/src/pages/procurement/Edit.jsx`)

### 3.6 AMC, Warranty, alerts, notifications, and audit

- AMC history is stored as `AmcContract` rows with optional Vendor/dates and
  `Incomplete`, `Active`, or `Ended` status. Asset-level AMC properties are
  derived from the most recently created contract.
  (Source: `backend/assets/models.py`)
- Initial Asset create/update can create or complete an AMC contract, while the
  dedicated renew action ends active/incomplete rows and creates a new row.
  Initial entry does not perform the renew endpoint's date-order validation.
  (Sources: `backend/assets/serializers.py`;
  `backend/assets/views.py`)
- The expiry-check function uses exact-date thresholds of 30, 15, and 7 days
  and notifies active Users with `asset_custody_manage`, which includes Admin
  and any custom Role granting that code.
  (Sources: `backend/assets/alerts.py`;
  `backend/accounts/models.py`)
- An in-process APScheduler job is configured for 07:00 daily, but startup is
  explicitly limited to Django `runserver`; it does not start from normal WSGI
  or ASGI application initialization.
  (Sources: `backend/core/scheduler.py`; `backend/core/apps.py`)
- Notifications are per-User, `Unread`/`Read`, and can be marked individually
  or all at once. The navbar polls unread count every 30 seconds and suppresses
  polling errors.
  (Sources: `backend/core/models.py`; `backend/core/views.py`;
  `frontend/src/components/navbar/Navbar.jsx`;
  `frontend/src/pages/Notifications.jsx`)
- AuditLog stores User/username, action, module, old/new values, time, and IP.
  The API exposes up to 1,000 newest entries to Admin with module and username
  filters; logging is explicit in selected view methods rather than universal
  middleware.
  (Sources: `backend/core/models.py`; `backend/core/services.py`;
  `backend/core/views.py`; `backend/accounts/views.py`;
  `backend/assets/views.py`)

### 3.7 Dashboard, reports, and exports

- Any authenticated API User can read global Dashboard KPIs and charts because
  those function views use the default authentication requirement without a
  role-permission gate. The frontend Dashboard is likewise available to every
  authenticated User.
  (Sources: `backend/reporting/views.py`; `frontend/src/App.jsx`;
  `frontend/src/pages/Dashboard.jsx`)
- Dashboard exposes Asset/status/value, open Checkout, pending Transfer, open
  Service, expired/expiring Warranty and AMC data, recent Transfers, open
  Checkouts, and soon-expiring Warranties. Seven chart endpoints cover category,
  status, department, purchase/Transfer trends, and Warranty/AMC timelines.
  (Sources: `backend/reporting/views.py`;
  `frontend/src/pages/Dashboard.jsx`)
- `report_access` exposes ten server-defined reports: Asset register, movement,
  Warranty, purchase, employee Assets, audit, current service, Vendor service,
  AMC expiry, and Lost Assets.
  (Sources: `backend/reporting/views.py`;
  `frontend/src/pages/Reports.jsx`)
- Server-side PDF and Excel exports use the configured company name; the
  frontend generates CSV locally. Transfer PDFs are generated separately.
  (Sources: `backend/core/exports.py`;
  `backend/reporting/views.py`;
  `frontend/src/pages/Reports.jsx`)

## 4. Contradictions and conflicts requiring a decision

These items must not become baseline requirements until resolved.

### C1. Transfer says “two Users,” but implementation supports IT Store handoff

Authoritative intent says Transfer always involves two Users and is distinct
from Checkout. The backend accepts any Asset except `Under Repair` or terminal,
so an `Available` Asset with no Custodian can create a Transfer whose
`previous_owner` is null. The UI intentionally offers both `Available` and
`Assigned` Assets and labels a null previous owner `IT Store`.
(Sources: `CONTEXT.md`, **Transfer**; `backend/assets/transfer.py`;
`frontend/src/pages/transfer/Create.jsx`;
`frontend/src/pages/transfer/Transfers.jsx`;
`backend/core/exports.py`)

**Decision needed:** Is Store-to-User issuance a Checkout or a Transfer?

### C2. Asset creation can bypass managed lifecycle and Custodian rules

Authoritative intent says Checkout/Transfer sets Custodian and Service/check-in
clears it. Backend update tests prevent direct entry into `Assigned` and
`Under Repair`, but `AssetSerializer.validate()` applies that transition guard
only when updating an existing instance. Create accepts every valid status and
an arbitrary Custodian, and the create UI exposes both.
(Sources: `CONTEXT.md`, **Custodian**, **Checkout**, and **Service Record**;
`backend/assets/serializers.py`; `frontend/src/pages/asset/Create.jsx`;
tests `backend/assets/tests.py::AssetStatusTransitionTests::test_cannot_enter_assigned_by_direct_edit`
and
`backend/assets/tests.py::AssetStatusTransitionTests::test_cannot_enter_under_repair_by_direct_edit`)

**Decision needed:** Which status/Custodian combinations are valid at Asset
creation, and is direct Custodian editing ever allowed?

### C3. Rejected `Assignment` terminology remains user-visible

The glossary says to use Checkout rather than Assignment, but Asset Detail
labels a panel `Assignment & Warranty`.
(Sources: `CONTEXT.md`, **Checkout**;
`frontend/src/pages/asset/Detail.jsx`)

### C4. AMC “flag” semantics differ from the data model

Authoritative intent describes a distinct `has_amc` flag where `False` means
deliberately no AMC. The persisted Asset flag was removed; `has_amc` is now
computed as true whenever any AMC history row exists, including when the latest
contract is `Ended`.
(Sources: `CONTEXT.md`, **AMC**; `backend/assets/models.py`;
`backend/assets/migrations/0007_remove_asset_amc_fields.py`)

**Decision needed:** Should an Asset with only ended AMC history report
`has_amc = True`, and how is deliberate no-AMC represented?

### C5. Proactive alerts are not scheduled in normal deployment entry points

Stakeholder intent requires proactively pushed 30/15/7-day alerts. The alert
function is tested, but the scheduler is started only when the process command
contains `runserver`; WSGI/ASGI startup does not schedule it. The scheduler
module itself says the in-process approach is an accepted temporary limitation.
(Sources: `CONTEXT.md`, **AMC**; `backend/core/apps.py`;
`backend/core/scheduler.py`; tests in
`backend/assets/tests.py::ExpiryAlertTests`)

**Decision needed:** What production scheduler guarantees proactive delivery?

### C6. Seeded Employee description conflicts with permission and deferred scope

The seeded Employee Role description says “View own assets and raise requests,”
but the seeded permission set grants only `asset_view`; the Asset API is not
scoped to the current User. `CONTEXT.md` also says employee Checkout and
Procurement request flows are deferred.
(Sources: `backend/accounts/migrations/0002_seed_rbac_and_org.py`;
`backend/assets/views.py`; `CONTEXT.md`, **Checkout** and **Procurement**)

**Decision needed:** Is Employee access intended to be own-Asset-only, all
Assets read-only, or absent?

### C7. Procurement physical-arrival rule is not represented

Authoritative intent says Procurement is recorded only after physical arrival
at an Asset's Location. Procurement has no arrival field, requires no Location,
and neither serializer nor UI validates arrival.
(Sources: `CONTEXT.md`, **Procurement**; `backend/assets/models.py`;
`backend/assets/serializers.py`;
`frontend/src/pages/procurement/Create.jsx`)

**Decision needed:** Is “physically arrived” a procedural precondition or a
system-enforced state?

### C8. Transfer PDF control and API authorization disagree

The frontend shows PDF download for every visible Transfer row. The backend
`document` action is absent from the explicit permission map and therefore
falls through to the `* = __admin__` rule, so a non-Admin with `asset_view`
sees the control but receives `403`.
(Sources: `frontend/src/pages/transfer/Transfers.jsx`;
`backend/assets/views.py`; `backend/core/permissions.py`)

### C9. Procurement list action visibility disagrees with route permissions

The Procurement list is reachable with `asset_view` and renders edit/delete
controls without checking `asset_edit` or `asset_delete`; the destination
routes require those permissions.
(Sources: `frontend/src/pages/procurement/Procurement.jsx`;
`frontend/src/App.jsx`)

## 5. Unknowns and needs-decision items

- **Named Role policy:** tests verify permission codes, not the complete
  stakeholder-approved Role matrix. Migrations show defaults, Roles are
  editable, and Admin bypasses codes. Confirm the intended grants and whether
  custom Roles are supported policy.
  (Sources: `backend/accounts/migrations/0002_seed_rbac_and_org.py`;
  `backend/accounts/migrations/0003_it_staff_no_transfer_request.py`;
  `backend/accounts/migrations/0004_rename_asset_transfer_permission.py`;
  `backend/accounts/models.py`; `frontend/src/pages/admin/Roles.jsx`)
- **Asset data visibility:** the minimal User directory is tested, but Asset,
  Checkout, Transfer, Service, dashboard, and report querysets are generally
  global. Confirm department/ownership privacy boundaries.
  (Sources: `backend/accounts/tests.py::PrivacyAuthorizationTests`;
  `backend/assets/views.py`; `backend/reporting/views.py`)
- **Asset creation invariants:** valid initial status, Custodian, department,
  Procurement, Warranty, and AMC combinations are unspecified and largely
  untested.
  (Sources: `backend/assets/models.py`;
  `backend/assets/serializers.py`;
  `frontend/src/pages/asset/Create.jsx`)
- **Department after custody ends:** check-in and Service clear Custodian but
  retain department. Confirm whether department means current organizational
  ownership, last holder department, or storage responsibility.
  (Sources: `CONTEXT.md`, **Custodian**;
  `backend/assets/checkout.py`; `backend/assets/service.py`)
- **Transfer integrity:** same-User Transfers, multiple concurrent pending
  requests, changes to Custodian/department between request and approval, and
  free-form Transfer conditions have no explicit rule or test.
  (Sources: `backend/assets/transfer.py`;
  `backend/assets/serializers.py`;
  `backend/assets/tests.py::TransferLifecycleTests`)
- **Service eligibility:** frontend permits `Available`/`Assigned`, but backend
  additionally permits `In Storage`. Confirm the accepted source statuses.
  (Sources: `backend/assets/service.py`;
  `frontend/src/pages/service/Create.jsx`)
- **Procurement lifecycle:** required/optional date rules, ordering between
  purchase and invoice dates, attachment/detachment history, deletion, and
  whether an Asset may exist indefinitely without Procurement are not covered
  by stakeholder intent or tests.
  (Sources: `backend/assets/models.py`;
  `backend/assets/serializers.py`;
  `backend/assets/tests.py`)
- **AMC initial-entry validation:** create/update does not enforce complete date
  pairs or start-before-end as the renew endpoint does, and AMC Vendor is not
  exposed by the Asset form/actions. Confirm desired validation and Vendor
  capture.
  (Sources: `backend/assets/models.py`;
  `backend/assets/serializers.py`; `backend/assets/views.py`;
  `frontend/src/pages/asset/Create.jsx`;
  `frontend/src/pages/asset/Detail.jsx`)
- **Alert operations:** production scheduling, timezone, retry, deduplication,
  downtime recovery, and delivery failure handling are not specified.
  (Sources: `backend/core/apps.py`; `backend/core/scheduler.py`;
  `backend/assets/alerts.py`; `backend/itams/settings.py`)
- **Notification channels:** current code creates in-app rows. SMTP settings
  are editable, but no email-sending implementation was found. Confirm whether
  “pushed” means in-app only or also email.
  (Sources: `backend/core/models.py`; `backend/core/services.py`;
  `frontend/src/pages/Settings.jsx`; `CONTEXT.md`, **AMC**)
- **Audit completeness and retention:** selected endpoints log actions, but
  master CRUD, notification reads, and many reads do not; no retention policy
  is documented. Confirm which events are mandatory.
  (Sources: `backend/core/services.py`; `backend/accounts/views.py`;
  `backend/assets/views.py`; `backend/catalog/views.py`;
  `backend/core/views.py`)
- **Physical audit versus audit trail:** periodic physical verification is
  deferred, while `/audit` and the “Asset Audit Report” expose operational
  AuditLog events. Future specs must keep these meanings distinct.
  (Sources: `CONTEXT.md`, **Lost**;
  `backend/core/views.py`; `backend/reporting/views.py`;
  `frontend/src/pages/Audit.jsx`)
- **Asset deletion and history retention:** deleting an Asset cascades to its
  Checkout, Transfer, Service, image, document, condition, and AMC rows. No
  stakeholder retention rule or automated deletion test was found.
  (Sources: `backend/assets/models.py`; `backend/assets/views.py`;
  `backend/assets/tests.py`)
- **File security and lifecycle:** extension allowlists and a 25 MB request
  limit exist, but content validation, authorization of media URLs, orphan-file
  cleanup, malware scanning, and retention are unspecified and untested.
  (Sources: `backend/itams/settings.py`;
  `backend/assets/views.py`; `backend/assets/models.py`)
- **Reports and Dashboard acceptance:** calculations, column definitions,
  access scope, CSV/PDF/Excel parity, and company branding are almost entirely
  implementation-only. Only one AMC expiry edge case has an automated test.
  (Sources: `backend/reporting/views.py`; `backend/core/exports.py`;
  `backend/reporting/tests.py`; `frontend/src/pages/Dashboard.jsx`;
  `frontend/src/pages/Reports.jsx`)
- **Frontend failure/accessibility behavior:** no frontend behavioral tests
  establish validation, error recovery, responsive behavior, accessibility,
  or authorization-control consistency.
  (Sources: `frontend/package.json`; `frontend/src/App.jsx`;
  `frontend/src/pages/`)

## 6. Explicitly deferred behavior

These are the only deferred product behaviors explicitly recorded in the
authoritative stakeholder context:

1. Scheduled or periodic physical Asset audits by department or Location are
   deferred beyond v1.
   (Source: `CONTEXT.md`, **Lost**)
2. Employee self-service Checkout, such as pooled/available-item Checkout, is a
   possible future scope if IT administration becomes a bottleneck.
   (Source: `CONTEXT.md`, **Checkout**)
3. Employee- or team-lead-initiated Procurement requests are intentionally out
   of current scope.
   (Source: `CONTEXT.md`, **Procurement**)

The scheduler source also proposes moving expiry jobs to an external scheduler
in a future version. That is an implementation-maintenance note, not confirmed
stakeholder product scope, so it is not included in the three deferred product
requirements above.
(Source: `backend/core/scheduler.py`)

## Baseline extraction guidance

The following bounded specifications can be derived from this evidence after
their listed decisions are resolved:

1. Authentication, Users, Roles, permissions, Departments, and Locations.
2. Asset register, status, condition, Custodian, terminal states, files, and
   history.
3. Checkout and check-in.
4. Approval-gated Transfer.
5. Service Record lifecycle.
6. Procurement, Vendor, and catalog masters.
7. Warranty, AMC, alerts, renewal, and End Support.
8. Notifications and AuditLog.
9. Dashboard, reports, and exports.

When drafting them, copy only confirmed user-visible behavior. Link to
`CONTEXT.md` for vocabulary and ADR-0001 for the Service Record decision; keep
every item in sections 3–5 marked as implementation evidence or
`needs-decision` until a stakeholder accepts it.
(Sources: `CONTEXT.md`; `docs/adr/0001-service-record-lifecycle.md`;
`.specify/memory/constitution.md`)
