# Feature Specification: AS-BUILT Identity, Access, and Organization Baseline

**Feature Branch**: `docs/baseline-spec-migration`

**Created**: 2026-07-29

**Status**: Draft

**Evidence Date**: 2026-07-29

**Input**: User description: "Create an AS-BUILT Brownfield Baseline
specification for ROADMAP.md entry B1: Identity, access, and organization.
Cover authentication, password changes, Users, Roles, permission codes,
Departments, Locations, administrative bypasses, the minimal active-User
directory, actors, authorization failures, and data visibility. Keep C6, the
named Role matrix, custom-Role policy, and global versus own/department data
visibility explicitly unresolved. Treat only stakeholder-confirmed or
test-backed behavior as requirements and do not modify application code."

## Clarifications

### Session 2026-07-29

- Q: Which Assets may an active Employee with `asset_view` see? → A: Only
  Assets where the Employee is Custodian, including `Lost` Assets that retain
  that Employee as Custodian.
- Q: What does "raise requests" mean for Employee in current scope? → A:
  Employees cannot raise requests in current scope; the phrase is not accepted
  Role intent.
- Q: Which permission-code matrix applies to the named Roles? → A: Admin has
  all permission codes; IT Manager has `asset_create`, `asset_edit`,
  `asset_delete`, `transfer_request`, `asset_custody_manage`, `asset_view`, and
  `report_access`; IT Staff has `asset_create`, `asset_edit`,
  `asset_custody_manage`, `asset_view`, and `report_access`; HR has
  `asset_view` and `transfer_request`; Employee has `asset_view`; Viewer has
  `asset_view` and `report_access`.
- Q: Are custom Roles supported? → A: Yes. Admin may manage custom Roles using
  any combination of existing permission codes; custom Roles receive no
  implicit administrative bypass.
- Q: What global, own-User, or Department data-visibility rule applies? → A:
  Admin, IT Manager, IT Staff, HR, Viewer, and custom Roles receive global data
  for granted permission codes; Employee receives only own identity,
  Custodian-scoped Assets, and directly involving lifecycle records, cannot
  browse the cross-User directory, and is not Department-scoped.

## Specification Lineage *(mandatory)*

**Type**: Brownfield Baseline

**Roadmap Reference**: `ROADMAP.md`, entry B1 — Identity, access, and
organization.

**Extends**: None.

**Supersedes**: None.

**Reciprocal Links**: `ROADMAP.md` entry B1 links to this Draft. Future changes
after acceptance must be recorded in a new specification and linked here with
`Extends`, `Supersedes`, or `Superseded by` metadata.

## Domain Alignment *(mandatory)*

**Canonical Terms**:

- **User** is the canonical term for a person represented in ITAMS. This
  baseline distinguishes a User from the current implementation's linked login
  account without accepting that implementation relationship as lasting
  product policy.
- **Role** is the canonical term for a named grouping used to grant permission
  codes. The named Role matrix and Admin-managed custom-Role policy are
  stakeholder-confirmed below.
- **permission code** is the canonical term for a grant checked for a protected
  action. The accepted Role and visibility rules below determine whether that
  granted action sees global or own-User data.
- **Department** is the canonical organizational grouping used for Users and
  Assets. **Location** is the canonical physical-place master. Department is
  not an authorization or data-visibility boundary.
- The named Roles found in stakeholder context or current-system evidence are
  Admin, IT Manager, IT Staff, HR, Employee, and Viewer.
- At adjacent lifecycle boundaries, use **Asset**, **Custodian**, **Checkout**,
  **Transfer**, **Service Record**, and **Procurement** as defined in
  `CONTEXT.md`. Do not use `Assignment` as a synonym for Checkout.

**Relevant Decisions**:

- No current ADR establishes B1 authentication, User, Role, permission,
  Department, Location, or data-scope policy.
- `docs/adr/0001-service-record-lifecycle.md` concerns the adjacent Service
  Record lifecycle and does not resolve any B1 access-policy question.

**Lifecycle and Actors**:

- B1 does not own an Asset lifecycle transition. It supplies identity and
  authorization inputs used by sibling lifecycle baselines.
- Test-backed actors are: an authenticated User with no relevant permission
  code; a User whose Role grants `user_management`; and a User whose Role
  grants `asset_view`.
- Current implementation also recognizes a User with `settings_access`, a
  Role named Admin, and a platform superuser. Their complete authority and
  bypass behavior are implementation-only except for the tested fact that
  `settings_access` alone does not grant access to administrative Settings.
- `CONTEXT.md` confirms only selected lifecycle actors: IT Manager and IT Staff
  perform Checkout and approve Transfer; HR or IT Manager request Transfer;
  employees do not perform self-service Checkout or Procurement requests.
  Stakeholder clarification confirms that an Employee with `asset_view` sees
  only Assets where that Employee is Custodian, including `Lost` Assets that
  retain them as Custodian, and that Employees raise no requests in current
  scope. Stakeholder clarification also confirms the complete named Role
  permission matrix recorded in FR-010 and Admin-managed custom Roles recorded
  in FR-011. When otherwise authorized, Admin, IT Manager, IT Staff, HR,
  Viewer, and custom Roles see global data; Employee is limited to own identity,
  Custodian-scoped Assets, and directly involving lifecycle records.

### Evidence Classification

This Draft uses the following classifications:

- **Stakeholder-confirmed**: stated in `CONTEXT.md`, an ADR, an accepted
  specification, or an explicit stakeholder instruction.
- **Test-backed current behavior**: demonstrated by an automated test and
  eligible for this requested AS-BUILT baseline without implying a broader
  policy.
- **Implementation-only observation**: visible in backend or frontend code
  without dedicated automated behavioral coverage or stakeholder confirmation.
- **Unresolved**: contradictory or incomplete evidence that must not be
  generalized into an accepted requirement.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Protect Administrative and User Data (Priority: P1)

An authenticated User without the required authority cannot read full User
records, Role assignments, permission-code definitions, or administrative
configuration.

**Why this priority**: These surfaces expose personal information and the
controls that determine access across ITAMS.

**Independent Test**: Authenticate a User whose Role has none of the relevant
permission codes, request each protected surface independently, and verify that
access is denied without returning the protected record.

**Acceptance Scenarios**:

1. **AS-001 — Test-backed**: **Given** an authenticated User whose Role has no
   relevant permission code, **When** the User requests the full User list,
   **Then** access is denied with `403`.
2. **AS-002 — Test-backed**: **Given** that same User, **When** the User
   requests a full User detail, Role list, permission-code list, or
   administrative Setting list, **Then** each request is denied with `403`.
3. **AS-003 — Test-backed**: **Given** an authenticated User whose Role grants
   `settings_access` but no administrative bypass, **When** the User requests
   administrative Settings, **Then** access is denied with `403`.
4. **AS-004 — Governance-backed**: **Given** a protected action, **When** a
   frontend surface hides or shows its control, **Then** the backend
   authorization decision remains authoritative.

---

### User Story 2 - Use the Minimal Active-User Directory (Priority: P1)

A non-Employee Asset workflow authorized by `asset_view` can select an active
User without receiving the email, login username, Role, mobile number,
designation, or other fields from a full User record. Employee cannot browse
this cross-User directory.

**Why this priority**: Checkout, Transfer, and Asset forms need a User selector
without exposing unnecessary identity data.

**Independent Test**: Request the directory with `asset_view` while both active
and Disabled Users exist, then inspect every returned field and the excluded
Disabled User.

**Acceptance Scenarios**:

1. **AS-005 — Test-backed and stakeholder-bounded**: **Given** an authenticated
   non-Employee User whose Role grants `asset_view`, **When** the User requests
   the minimal active-User directory, **Then** each returned row contains only
   `id`, `user_name`, `emp_id`, and `department_name`.
2. **AS-006 — Test-backed**: **Given** a Disabled User exists, **When** the
   directory is requested with `asset_view`, **Then** that Disabled User is not
   returned.
3. **AS-007 — Stakeholder-confirmed**: **Given** an Employee whose Role grants
   `asset_view`, **When** the Employee requests the cross-User directory,
   **Then** access is denied and no directory records are returned.

---

### User Story 3 - Read and Maintain Users (Priority: P2)

A User administrator can inspect the full identity information needed for
administration. Current create, edit, deactivate, login-account maintenance,
password reset, and deletion behavior is documented for review but is not
accepted as product intent without further confirmation or tests.

**Why this priority**: User records connect people, organizational membership,
Roles, and login access, but most mutation and failure semantics are currently
implementation-led.

**Independent Test**: The accepted portion can be tested by reading a full User
detail with `user_management`. The observational portion requires separate
verification of each create, update, disable, credential, and delete path.

**Acceptance Scenarios**:

1. **AS-008 — Test-backed**: **Given** an authenticated User whose Role grants
   `user_management`, **When** that User requests a full User detail, **Then**
   the response includes the User's email address and linked login username.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-001 — Implementation-only**: A User administrator can currently
   list, create, retrieve, and update User records containing name, employee
   ID, email, mobile number, optional Department, designation, optional Role,
   and a free-form status.
2. **OBS-AS-002 — Implementation-only**: Creating or updating a User can
   currently create or rename a linked login account and set or reset its
   password. Supplying only one of username or password when creating the
   account is rejected.
3. **OBS-AS-003 — Implementation-only**: Updating a User to `Disabled`
   currently deactivates an existing linked login account, and login also
   checks the User status.
4. **OBS-AS-004 — Implementation-only**: User deletion is currently restricted
   to an administrative bypass, rejects deleting the current User, and rejects
   deleting a User who remains Custodian of an Asset.
5. **OBS-AS-005 — Implementation-only**: Successful User create, update, and
   delete actions currently create selected AuditLog entries; no complete
   audit, Notification, or retention contract is accepted here.

---

### User Story 4 - Authenticate and Change a Password (Priority: P1)

A person can currently sign in with a username and password, sign out, restore
current-session identity, and change their own password. Every detailed outcome
in this story remains implementation-only because no automated authentication
or password-change behavior test was found and no stakeholder source fixes the
contract.

**Why this priority**: Authentication is the entry point to every protected
capability, but describing untested code as accepted policy would hide material
security decisions.

**Independent Test**: Exercise successful, invalid-credential, Disabled-User,
logout, current-session, incorrect-current-password, short-password, and
successful-password-change cases while observing access, credential state,
session continuity, and audit effects.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-006 — Implementation-only**: Valid credentials currently return an
   authentication token and User summary containing identity, Department,
   Role, permission codes, and an administrative indicator.
2. **OBS-AS-007 — Implementation-only**: Invalid credentials currently return
   `401`; a User whose status is not `Active` receives `403`.
3. **OBS-AS-008 — Implementation-only**: Logout currently deletes the presented
   token. A later unauthorized response causes the frontend to clear locally
   stored identity and redirect to login.
4. **OBS-AS-009 — Implementation-only**: A password change currently requires
   the existing password, rejects a new password shorter than six characters,
   changes the password, and replaces the current token.
5. **OBS-AS-010 — Implementation-only**: The password-change page rejects a
   mismatched confirmation before submission; backend behavior does not receive
   or validate that confirmation field.
6. **OBS-AS-011 — Implementation-only**: Login success, login failure, logout,
   and successful password change currently create selected AuditLog entries.
   Disabled-User denial and password-change failures are not visibly logged by
   the reviewed implementation.

---

### User Story 5 - Administer Roles and Permission Codes (Priority: P1)

An administrator can currently inspect permission codes, create Roles, and
change Role-to-permission assignments. The named Role matrix is accepted;
custom Roles are supported under Admin control without implicit bypass. The
implementation's platform-superuser and Role-name bypass mechanics remain
unresolved.

**Why this priority**: Role configuration changes who can see or change data
throughout ITAMS.

**Independent Test**: For accepted behavior, exercise the test-backed
permission-code denial and allowance cases. For observations, inspect Role and
permission-code administration using an administrator and a non-administrator.

**Acceptance Scenarios**:

1. **AS-009 — Test-backed**: **Given** an authenticated User without
   `asset_custody_manage`, **When** that User attempts to create a Checkout or
   Service Record, **Then** each protected action is denied with `403`.
2. **AS-010 — Test-backed**: **Given** an authenticated User without
   `transfer_request`, **When** that User attempts to create a Transfer,
   **Then** the protected action is denied with `403`.
3. **AS-011 — Stakeholder-confirmed**: **Given** an active Employee whose Role
   grants `asset_view`, **When** the Employee requests the Asset register or an
   Asset detail, **Then** only Assets where that Employee is Custodian are
   visible, including a `Lost` Asset that retains that Employee as Custodian.
4. **AS-012 — Stakeholder-confirmed**: **Given** an Employee using current
   ITAMS scope, **When** that Employee looks for a request action, **Then** no
   Employee-initiated Checkout, Transfer, or Procurement request is available;
   HR or IT Manager initiates Transfer on the employee's behalf.
5. **AS-013 — Stakeholder-confirmed**: **Given** an active User assigned to a
   named Role, **When** a protected action checks a permission code, **Then**
   the Role grants exactly the codes in FR-010, subject to the separately
   accepted Employee Asset visibility rule in FR-008.
6. **AS-014 — Stakeholder-confirmed**: **Given** an Admin manages a custom
   Role, **When** existing permission codes are assigned, **Then** the Role
   grants only those codes and receives no implicit administrative bypass.
7. **AS-015 — Stakeholder-confirmed**: **Given** an active User in Admin, IT
   Manager, IT Staff, HR, Viewer, or a custom Role, **When** a granted
   permission code authorizes a data surface, **Then** its records are global.
   **Given** an Employee, **Then** visible records are limited to that
   Employee's own identity, Custodian-scoped Assets, and lifecycle records that
   directly identify the Employee; Department never expands or restricts
   either scope.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-012 — Implementation-only**: Role and permission-code
   administration is currently restricted to a Role named Admin or a platform
   superuser; permission-code records are read-only through the reviewed
   administration interface.
2. **OBS-AS-013 — Implementation-only**: A Role named Admin and a platform
   superuser currently bypass ordinary permission-code membership. Other active
   Users rely on their Role's assigned codes.
3. **OBS-AS-014 — Implementation-only conformance evidence**: The Role page
   currently supports creating a new Role and changing permission assignments,
   consistent with AS-014; no frontend behavioral test establishes the full
   management or no-bypass contract.
4. **OBS-AS-015 — Implementation-only conformance evidence**: Current
   migrations seed the named Roles and permission assignments listed under
   Permission Code Inventory and Accepted Named Role Matrix below. The
   migrations support but do not independently establish stakeholder intent.

---

### User Story 6 - Use Department and Location Masters (Priority: P2)

Authenticated Users currently consume Department and Location values while a
`settings_access` holder can use the shared master-data page to add or remove
them. The accepted manager, validation, deletion, history, and visibility
policies remain unspecified.

**Why this priority**: User and Asset records depend on consistent
organizational and physical-place values.

**Independent Test**: Independently exercise list, create, update, and delete
for Department and Location with no code, with `settings_access`, and with an
administrative bypass, including referenced and duplicate records.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-016 — Implementation-only**: Department and Location names are
   currently unique; Department also stores an optional description and
   Location an optional address.
2. **OBS-AS-017 — Implementation-only**: Backend reads currently require an
   authenticated active User but no specific permission code; writes currently
   require `settings_access` or an administrative bypass.
3. **OBS-AS-018 — Implementation-only**: The frontend exposes Department and
   Location administration only through a `settings_access`-gated master page,
   so the frontend does not expose the broader authenticated read behavior as a
   standalone route.
4. **OBS-AS-019 — Implementation-only**: Department deletion can currently
   clear Department references that use a set-null relationship. Location and
   Department retention, referenced-record failure behavior, audit effects, and
   historical-report effects have no accepted contract or dedicated tests.

### Edge Cases and Negative Cases

- **NC-001 — Test-backed**: A User with no relevant permission receives `403`
  from full User list/detail, Role, permission-code, and administrative Setting
  reads.
- **NC-002 — Test-backed**: `settings_access` alone still receives `403` from
  administrative Settings.
- **NC-003 — Test-backed**: A Disabled User does not appear in the directory
  returned under `asset_view`.
- **NC-004 — Test-backed**: Absence of `asset_custody_manage` rejects the
  tested Checkout and Service Record create actions.
- **NC-005 — Test-backed**: Absence of `transfer_request` rejects the tested
  Transfer create action.
- **OBS-NC-001 — Implementation-only**: Invalid login credentials produce a
  generic failure; Disabled-User login is separately rejected.
- **OBS-NC-002 — Implementation-only**: Incorrect current password, a new
  password shorter than six characters, and a mismatched frontend confirmation
  are rejected at different layers.
- **OBS-NC-003 — Implementation-only**: Duplicate employee ID, email, login
  username, Role name, Department name, Location name, or permission code is
  constrained, but complete user-visible error wording and recovery are
  untested.
- **OBS-NC-004 — Implementation-only**: User create/update persists profile
  fields before linked-account synchronization in the reviewed implementation.
  Atomic rollback on a later account-validation failure is not established.
- **OBS-NC-005 — Implementation-only**: A `user_management` holder can reach
  User create/edit routes but those pages request the Admin-only Role list.
  Non-Admin completion of the page flow is not established by tests.
- **OBS-NC-006 — Implementation-only**: Frontend route hiding and local
  permission checks can become stale after a Role changes because the cached
  User summary is not visibly refreshed on each navigation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: An authenticated User whose Role has no relevant permission code
  MUST receive `403` when requesting the full User list, a full User detail,
  Roles, permission codes, or administrative Settings.
  *(Source: `backend/accounts/tests.py::PrivacyAuthorizationTests::test_ordinary_user_cannot_read_privileged_apis`.)*
- **FR-002**: A User whose Role grants `user_management` MUST be able to read a
  full User detail that includes the User's email address and linked login
  username.
  *(Source: `backend/accounts/tests.py::PrivacyAuthorizationTests::test_user_manager_can_read_full_user_records`.)*
- **FR-003**: A non-Employee User whose Role grants `asset_view` MUST be able
  to request a minimal active-User directory in which every returned row
  contains only `id`, `user_name`, `emp_id`, and `department_name`.
  *(Sources:
  `backend/accounts/tests.py::PrivacyAuthorizationTests::test_asset_user_gets_only_minimal_active_user_directory`;
  stakeholder clarification, 2026-07-29.)*
- **FR-004**: A Disabled User MUST be excluded from the minimal active-User
  directory.
  *(Source: `backend/accounts/tests.py::PrivacyAuthorizationTests::test_asset_user_gets_only_minimal_active_user_directory`.)*
- **FR-005**: `settings_access` without an administrative bypass MUST NOT grant
  access to administrative Settings.
  *(Source: `backend/accounts/tests.py::PrivacyAuthorizationTests::test_settings_access_does_not_expose_admin_configuration`.)*
- **FR-006**: The absence of `asset_custody_manage` MUST deny the tested
  Checkout and Service Record create actions with `403`.
  *(Sources: `backend/assets/tests.py::CheckoutTransferEndpointTests::test_checkout_create_requires_asset_custody_manage_permission`;
  `backend/assets/tests.py::ServiceRecordEndpointTests::test_service_create_requires_asset_custody_manage_permission`.)*
- **FR-007**: The absence of `transfer_request` MUST deny the tested Transfer
  create action with `403`.
  *(Source: `backend/assets/tests.py::CheckoutTransferEndpointTests::test_transfer_request_requires_transfer_request_permission`.)*
- **FR-008**: An active Employee whose Role grants `asset_view` MUST be limited
  to Assets where that Employee is Custodian, including a `Lost` Asset that
  retains that Employee as Custodian.
  *(Source: stakeholder clarification, 2026-07-29; consistent with
  `specs/001-asset-register-lifecycle-baseline/spec.md`.)*
- **FR-009**: Employees MUST NOT initiate Checkout, Transfer, or Procurement
  requests in current scope. HR or IT Manager MUST initiate Transfer on an
  employee's behalf; IT MUST perform Checkout on an employee's behalf.
  *(Sources: stakeholder clarification, 2026-07-29; `CONTEXT.md`, Checkout,
  Transfer, and Procurement.)*
- **FR-010**: The named Roles MUST grant these permission codes:
  - Admin: all current permission codes.
  - IT Manager: `asset_create`, `asset_edit`, `asset_delete`,
    `transfer_request`, `asset_custody_manage`, `asset_view`, and
    `report_access`.
  - IT Staff: `asset_create`, `asset_edit`, `asset_custody_manage`,
    `asset_view`, and `report_access`.
  - HR: `asset_view` and `transfer_request`.
  - Employee: `asset_view`.
  - Viewer: `asset_view` and `report_access`.
  *(Source: stakeholder clarification, 2026-07-29.)*
- **FR-011**: Admin MUST be able to manage custom Roles using any combination
  of existing permission codes. A custom Role MUST grant only its assigned
  codes, MUST follow the accepted action and data-visibility rules for those
  codes, and MUST NOT receive an implicit administrative bypass.
  *(Source: stakeholder clarification, 2026-07-29.)*
- **FR-012**: When a granted permission code authorizes access, a User in
  Admin, IT Manager, IT Staff, HR, Viewer, or a custom Role MUST receive global
  records for that action. Employee MUST receive only:
  - their own User identity;
  - Assets where they are Custodian, including `Lost` Assets retaining them as
    Custodian;
  - Checkouts where they are the User;
  - Transfers where they are the previous or new owner; and
  - other lifecycle records only while the related Asset remains visible under
    the Custodian rule, plus summaries derived solely from these visible
    records.
  Employee MUST NOT browse the cross-User directory. Department MUST NOT expand
  or restrict visibility for any Role.
  *(Source: stakeholder clarification, 2026-07-29.)*

### Authorization Requirements

- **ALR-001**: Backend authorization MUST remain authoritative for every
  protected B1 action; frontend route or control visibility MUST NOT substitute
  for the backend decision.
  *(Source: `.specify/memory/constitution.md`, Principle II.)*
- **ALR-002**: A denied request covered by FR-001, FR-005, FR-006, or FR-007
  MUST NOT return the protected representation or complete the protected
  action.
  *(Sources: the automated tests cited by those requirements.)*
- **ALR-003**: Access to the minimal directory under FR-003 MUST NOT imply
  access to a full User record; full User detail remains governed by FR-001 and
  FR-002.
  *(Sources: `backend/accounts/tests.py::PrivacyAuthorizationTests`.)*
- **ALR-004**: Permission-code authorization and data visibility MUST both
  succeed before data is returned: FR-010 and FR-011 determine the granted
  actions, while FR-008 and FR-012 determine global or Employee-own scope.
  *(Source: stakeholder clarification, 2026-07-29.)*
- **ALR-005**: An Employee attempt to retrieve another User's identity, browse
  the cross-User directory, or retrieve an Asset or lifecycle record outside
  FR-012 MUST be denied without returning the record. Department membership
  MUST NOT be used as a substitute grant.
  *(Source: stakeholder clarification, 2026-07-29.)*

### Data Visibility Boundary

The accepted, test-backed visibility contract is intentionally narrow:

| Surface | Accepted current access | Accepted visible data | Evidence |
| --- | --- | --- | --- |
| Full User detail | Role grants `user_management` | Includes email and linked login username | `PrivacyAuthorizationTests::test_user_manager_can_read_full_user_records` |
| Minimal active-User directory | Non-Employee Role grants `asset_view` | Global active Users; exactly `id`, `user_name`, `emp_id`, `department_name`; excludes Disabled User | Test-backed fields/exclusion; stakeholder-confirmed global scope and Employee exclusion |
| Cross-User directory for Employee | Employee Role grants `asset_view` | Denied; no directory records | Stakeholder clarification, 2026-07-29 |
| Asset register and Asset detail for Employee | Employee Role grants `asset_view` | Only Assets where that Employee is Custodian, including retained Custodian on `Lost` | Stakeholder clarification, 2026-07-29; accepted B2 baseline |
| Any granted data action for Admin, IT Manager, IT Staff, HR, Viewer, or custom Role | Required permission code or accepted administrative authority | Global records; no Department filter | Stakeholder clarification, 2026-07-29 |
| Employee identity and lifecycle data | Employee access is otherwise granted | Own User identity and directly involving records listed in FR-012; no Department expansion | Stakeholder clarification, 2026-07-29 |
| Full Users, Roles, permission codes, administrative Settings | No relevant permission | Denied with `403` | `PrivacyAuthorizationTests::test_ordinary_user_cannot_read_privileged_apis` |
| Administrative Settings | `settings_access` without administrative bypass | Denied with `403` | `PrivacyAuthorizationTests::test_settings_access_does_not_expose_admin_configuration` |

This table accepts global visibility for authorized non-Employee named and
custom Roles and the Employee-own boundary in FR-012. Department is
organizational data, not a visibility filter.

### Permission Code Inventory and Accepted Named Role Matrix

The current permission-code inventory is implementation evidence:

| Permission code | Current observed use | Evidence status |
| --- | --- | --- |
| `asset_create` | Asset and Procurement create routes | Implementation-only; B2 contains accepted Asset-specific named-Role behavior |
| `asset_edit` | Asset and Procurement update plus Asset sub-actions | Implementation-only; B2 contains accepted Asset-specific named-Role behavior |
| `asset_delete` | Asset and Procurement deletion | Implementation-only; B2 contains accepted Asset-specific named-Role behavior |
| `transfer_request` | Transfer creation | Denial is test-backed; named Role grants are stakeholder-confirmed |
| `asset_custody_manage` | Checkout, Transfer approval/rejection, and Service Record actions | Selected denials are test-backed; named Role grants are stakeholder-confirmed |
| `asset_view` | Asset-family reads and minimal active-User directory | Directory shape/exclusion is test-backed; global non-Employee and Employee-own scopes are stakeholder-confirmed |
| `user_management` | Full User list/detail/create/update | Full-detail read is test-backed; mutation behavior is implementation-only |
| `report_access` | Reports and exports | Implementation-only and owned by B9 |
| `settings_access` | Department, Location, catalog, and Vendor writes | Administrative Setting exclusion is test-backed; other behavior is implementation-only |

Stakeholder clarification accepts the following named Role grants, which match
the grants currently produced by migrations after the
`asset_transfer` to `asset_custody_manage` rename and removal of
`transfer_request` from IT Staff:

| Named Role | Accepted permission codes |
| --- | --- |
| Admin | All current permission codes |
| IT Manager | `asset_create`, `asset_edit`, `asset_delete`, `transfer_request`, `asset_custody_manage`, `asset_view`, `report_access` |
| IT Staff | `asset_create`, `asset_edit`, `asset_custody_manage`, `asset_view`, `report_access` |
| HR | `asset_view`, `transfer_request` |
| Employee | `asset_view` |
| Viewer | `asset_view`, `report_access` |

No non-Admin named Role receives `user_management` or `settings_access`; those
actions are therefore Admin-only among the accepted named Roles. The
persistence migrations are supporting evidence rather than the source of
intent. The editable Role page is consistent with accepted custom-Role
management. A custom Role may receive either code but receives no implicit
bypass.

### Current Validation, Failure, Audit, and Notification Behavior

The following details are observations awaiting confirmation:

- Login trims the submitted username. Invalid credentials return `401`; a
  non-Active linked User returns `403`.
- Successful login returns a token and User summary. Logout deletes the
  presented token. Current-session retrieval can return or create a token.
- Self-service password change checks the current password, applies a
  six-character minimum, changes the password, replaces the token, and records
  an AuditLog entry. It does not visibly invoke the broader configured password
  validators.
- The frontend checks new-password confirmation locally and stores the token
  and User summary in browser local storage. A `401` clears both; a `403` does
  not automatically refresh or clear cached permissions.
- User fields currently enforce unique employee ID and email. A linked login
  username is also unique. Exact required fields differ between the frontend,
  serializer, and underlying record constraints.
- User account creation requires both a login username and password when either
  is supplied. Administrative password reset does not visibly share the
  self-service six-character check.
- User deletion currently rejects self-deletion and a User who remains
  Custodian of an Asset. Effects on other User history, audit retention, and
  recovery remain unspecified.
- Role names, permission codes, Department names, and Location names are
  currently unique. Current User status accepts more backend values than the
  frontend's `Active` and `Disabled` options.
- Login success/failure, logout, password change, User create/update/delete,
  and Role create/update/delete have selected AuditLog calls. Department and
  Location mutations have no visible B1-specific AuditLog call.
- No B1-specific Notification trigger was found. AuditLog storage, access, and
  retention and generic Notification behavior are owned by B8.
- No frontend behavioral tests establish error wording, route-gate
  consistency, local-storage security, accessibility, or recovery behavior.

### Key Entities

- **User**: A person represented in ITAMS. Test-backed visible forms are a full
  detail containing email and linked login username for `user_management`, and
  a minimal directory row for `asset_view`. Other fields and mutation behavior
  are implementation-only.
- **Login account**: The current credential-bearing record optionally linked to
  a User. Its optionality, lifecycle, token behavior, and recovery policy are
  implementation-only.
- **Role**: A named set of permission-code assignments. The named matrix and
  Admin-managed custom-Role policy are accepted in FR-010 and FR-011.
- **Permission code**: A capability grant checked for selected protected
  actions. The current nine-code inventory supplies the codes used by the
  accepted Role matrix; selected action meanings remain test-backed or owned by
  sibling baselines.
- **Department**: An organizational grouping currently associated with Users
  and Assets. It does not yet define an accepted visibility boundary.
- **Location**: A physical-place master currently associated with Assets.
- **AuditLog**: A shared operational record owned by B8. B1 currently creates
  selected authentication, User, and Role entries, but required events,
  failure logging, access, and retention remain unresolved.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review covering ordinary-User denial, full User detail under
  `user_management`, the minimal active-User directory under `asset_view`, and
  administrative Setting denial under `settings_access`, 100% of the four
  access cases produce the outcomes specified by FR-001 through FR-005.
- **SC-002**: For every directory row reviewed under FR-003, 100% contain
  exactly four fields, 0% of Disabled Users appear, and Employee directory
  requests return 0 records.
- **SC-003**: For every protected surface in FR-001 and FR-005, an unauthorized
  request returns no protected record and receives `403`.
- **SC-004**: In the three selected lifecycle authorization cases cited by
  FR-006 and FR-007, 100% of attempts made without the required permission code
  are rejected with `403`.
- **SC-005**: 100% of login, password, User mutation, Role, permission-code,
  administrative-bypass, Department, Location, audit, Notification, and
  frontend behaviors not backed by stakeholder intent or tests are labeled
  implementation-only or unresolved and cite repository evidence.
- **SC-006**: Employee Asset visibility produces zero Assets where another User
  or no User is Custodian, and current Employee surfaces expose zero
  Employee-initiated Checkout, Transfer, or Procurement request actions. The
  named Role matrix grants 100% of the codes in FR-010 and no additional codes.
  Every custom Role grants exactly its configured existing codes and no
  implicit bypass. Authorized non-Employee Roles receive global records,
  Employee receives only the records in FR-012, and Department changes neither
  scope.
- **SC-007**: Before this Draft can be accepted, stakeholder review accounts
  for all unresolved conflicts listed below and confirms that no deferred or
  implementation-only behavior has been described as currently accepted.

## Assumptions

- This is an AS-BUILT documentation baseline as of 2026-07-29. It does not
  request a behavior change and does not make implementation-only behavior
  authoritative.
- The explicit stakeholder instruction permits test-backed current behavior to
  be recorded as a baseline requirement even when `CONTEXT.md` does not state a
  broader product policy.
- `CONTEXT.md` is authoritative for canonical lifecycle terminology and its
  selected actor statements, but it does not define a complete B1 identity or
  authorization model.
- The accepted B2 baseline and this clarification establish Custodian-only
  Asset visibility for Employee. This clarification also establishes that
  Employee raises no requests in current scope. Authorized non-Employee named
  and custom Roles receive global records, Employee receives only the records
  in FR-012, and Department is not a visibility boundary.
- A `403` is an accepted outcome only for the exact tested cases. This Draft
  does not infer response codes for unauthenticated, inactive, unlinked,
  deleted, or stale-session actors.
- The minimal active-User directory is global for authorized non-Employee
  Roles and unavailable to Employee. Its accepted field set and Disabled-User
  exclusion remain unchanged.
- Stakeholder clarification accepts the named Role matrix currently represented
  by the post-migration grants. The migrations remain supporting evidence and
  do not independently establish intent.
- Custom Roles are accepted only when managed by Admin, composed from existing
  permission codes, and given no implicit administrative bypass.
- B8 owns generic AuditLog and Notification storage, visibility, and retention;
  B1 records only observed identity-specific triggers and gaps.

## Baseline Evidence and Unresolved Conflicts *(Brownfield Baseline only)*

### Accepted Intent

- B1 capability boundary and the policy areas selected for clarification:
  `ROADMAP.md`, entry B1; explicit stakeholder instruction dated 2026-07-29.
- Employee Custodian-only Asset visibility:
  stakeholder clarification dated 2026-07-29;
  `specs/001-asset-register-lifecycle-baseline/spec.md`.
- No Employee-initiated request workflow in current scope:
  stakeholder clarification dated 2026-07-29;
  `CONTEXT.md`, Checkout, Transfer, and Procurement.
- Named Role permission-code matrix:
  stakeholder clarification dated 2026-07-29.
- Admin-managed custom Roles without implicit bypass:
  stakeholder clarification dated 2026-07-29.
- Global non-Employee, Employee-own, and no-Department visibility policy:
  stakeholder clarification dated 2026-07-29.
- Canonical Asset-lifecycle terminology, selected IT/HR actor intent, and
  explicitly deferred employee self-service:
  `CONTEXT.md`.
- Asset-specific Role and visibility decisions that must not be generalized by
  B1:
  `specs/001-asset-register-lifecycle-baseline/spec.md`.
- Brownfield evidence and acceptance rules:
  `.specify/memory/constitution.md`;
  `docs/agents/domain.md`;
  `specs/README.md`.
- No ADR under `docs/adr/` currently establishes B1 policy. The reviewed
  `docs/adr/0001-service-record-lifecycle.md` is an adjacent lifecycle
  decision only.

### Verified Behavior Evidence

- **AS-001, AS-002, FR-001, ALR-002** — ordinary User denied privileged User,
  Role, permission-code, and Setting reads:
  `backend/accounts/tests.py::PrivacyAuthorizationTests::test_ordinary_user_cannot_read_privileged_apis`.
- **AS-008, FR-002** — `user_management` reads email and linked login username
  from a full User detail:
  `backend/accounts/tests.py::PrivacyAuthorizationTests::test_user_manager_can_read_full_user_records`.
- **AS-005, AS-006, FR-003, FR-004, ALR-003** — `asset_view` minimal
  active-User directory fields and Disabled-User exclusion:
  `backend/accounts/tests.py::PrivacyAuthorizationTests::test_asset_user_gets_only_minimal_active_user_directory`.
- **AS-003, FR-005** — `settings_access` does not grant administrative Setting
  access:
  `backend/accounts/tests.py::PrivacyAuthorizationTests::test_settings_access_does_not_expose_admin_configuration`.
- **AS-009, FR-006** — selected `asset_custody_manage` denial behavior:
  `backend/assets/tests.py::CheckoutTransferEndpointTests::test_checkout_create_requires_asset_custody_manage_permission`;
  `backend/assets/tests.py::ServiceRecordEndpointTests::test_service_create_requires_asset_custody_manage_permission`.
- **AS-010, FR-007** — selected `transfer_request` denial behavior:
  `backend/assets/tests.py::CheckoutTransferEndpointTests::test_transfer_request_requires_transfer_request_permission`.
- Consolidated evidence classification, absence of frontend behavior tests, and
  recorded successful 70-test baseline run:
  `docs/research/itams-current-system-baseline.md`.

### Implementation-Only Observations

- User, Role, permission-code, Department, Location, administrative bypass, and
  active-User lookup structure:
  `backend/accounts/models.py`.
- Full/minimal representations, Role permission assignment, linked login
  creation/rename/password behavior, status synchronization, and validation
  ordering:
  `backend/accounts/serializers.py`.
- Login, logout, current-session, password change, User/Role/master actions,
  permission maps, deletion guards, and selected AuditLog effects:
  `backend/accounts/views.py`;
  `backend/accounts/urls.py`.
- Permission-map evaluation, active-profile checks, Role-name Admin bypass, and
  platform-superuser bypass:
  `backend/core/permissions.py`.
- Department and Location write permission mapping:
  `backend/core/mixins.py`.
- Token authentication, authenticated-by-default API policy, and configured
  password validators:
  `backend/itams/settings.py`.
- Initial entity schema:
  `backend/accounts/migrations/0001_initial.py`.
- Seeded permission codes, named Roles, Role descriptions, Department and
  Location values, and default administrative credential:
  `backend/accounts/migrations/0002_seed_rbac_and_org.py`.
- Removal of `transfer_request` from IT Staff:
  `backend/accounts/migrations/0003_it_staff_no_transfer_request.py`.
- Rename of `asset_transfer` to `asset_custody_manage`:
  `backend/accounts/migrations/0004_rename_asset_transfer_permission.py`.
- Frontend login state, locally cached User/permission data, logout cleanup,
  and client-side permission calculation:
  `frontend/src/AuthContext.jsx`;
  `frontend/src/api/client.js`.
- Frontend authentication and permission route behavior:
  `frontend/src/components/ProtectedRoute.jsx`;
  `frontend/src/App.jsx`.
- Login and password-change forms and failure presentation:
  `frontend/src/pages/Login.jsx`;
  `frontend/src/pages/ChangePassword.jsx`.
- Full User listing and action visibility:
  `frontend/src/pages/user/User.jsx`.
- User create, edit, credential maintenance, and validation:
  `frontend/src/pages/user/Create.jsx`;
  `frontend/src/pages/user/Edit.jsx`.
- User deletion confirmation and failure display:
  `frontend/src/pages/user/Delete.jsx`.
- Role and permission-code matrix administration and custom Role creation:
  `frontend/src/pages/admin/Roles.jsx`.
- Department and Location administration:
  `frontend/src/pages/admin/Masters.jsx`.
- Cross-capability data-scope evidence:
  `backend/assets/views.py`;
  `backend/reporting/views.py`;
  `frontend/src/components/navbar/Menu.jsx`;
  `frontend/src/components/navbar/ShortMenu.jsx`.
- Absence of a frontend behavioral-test script:
  `frontend/package.json`.

### Unresolved Conflicts

1. **C6 — Resolved decision; seeded-description and implementation gaps**:
   the seeded Employee Role says "View own assets and raise requests," grants
   `asset_view`, and current Asset querysets are generally global.
   `CONTEXT.md` defers employee self-service Checkout and Procurement requests.
   Stakeholder clarification confirms that Employee Asset visibility is
   limited to Assets where the Employee is Custodian, including retained
   Custodian on `Lost`, and that Employee raises no requests in current scope.
   The current global Asset implementation and seeded "raise requests"
   description do not conform to the accepted behavior.
   Evidence: `CONTEXT.md`;
   `backend/accounts/migrations/0002_seed_rbac_and_org.py`;
   `backend/assets/views.py`;
   `specs/001-asset-register-lifecycle-baseline/spec.md`.
2. **Named Role matrix resolved; coverage gap remains**: stakeholder
   clarification accepts the post-migration grants in FR-010. This makes
   `user_management` and `settings_access` Admin-only for named Roles.
   Automated tests still exercise synthetic Roles and selected permission codes
   rather than proving the complete named matrix.
   Evidence: `CONTEXT.md`;
   `backend/accounts/tests.py`;
   `backend/accounts/migrations/0002_seed_rbac_and_org.py`;
   `backend/accounts/migrations/0003_it_staff_no_transfer_request.py`;
   `backend/accounts/migrations/0004_rename_asset_transfer_permission.py`.
3. **Custom-Role policy resolved; enforcement coverage gap remains**:
   stakeholder clarification accepts Admin-managed custom Roles composed from
   any existing permission codes and denies them implicit administrative
   bypass. Current models, synthetic test Roles, backend Role CRUD, and the Role
   page are consistent with custom permission combinations, but no automated
   test covers the complete management and no-bypass contract.
   Evidence: `backend/accounts/models.py`;
   `backend/accounts/tests.py`;
   `backend/accounts/views.py`;
   `frontend/src/pages/admin/Roles.jsx`.
4. **Visibility policy resolved; Employee implementation gaps remain**:
   stakeholder clarification accepts global records for authorized Admin, IT
   Manager, IT Staff, HR, Viewer, and custom Roles; Employee is limited to the
   records in FR-012; Department is not a visibility boundary. Current Asset,
   Checkout, Transfer, Service Record, dashboard, reporting, and minimal
   directory querysets are generally global for every permission holder and do
   not consistently enforce the Employee-own restriction.
   Evidence: `backend/accounts/views.py`;
   `backend/assets/views.py`;
   `backend/reporting/views.py`;
   `backend/accounts/tests.py::PrivacyAuthorizationTests`;
   `specs/001-asset-register-lifecycle-baseline/spec.md`.
5. **Administrative bypass partly resolved**: Admin has all permission codes
   under FR-010, while custom Roles receive no implicit bypass under FR-011.
   Current code implements authority through a Role named exactly Admin and a
   separate platform-superuser bypass. Tests do not confirm those mechanisms,
   protection against renaming or deleting Admin, or whether platform
   superusers without a User profile belong in product behavior.
   Evidence: `backend/accounts/models.py`;
   `backend/core/permissions.py`;
   `backend/accounts/views.py`;
   `frontend/src/pages/admin/Roles.jsx`.
6. **Authentication and session contract**: token issue/reuse, current-session
   token creation, logout invalidation, Disabled-User handling, frontend local
   storage, `401` redirect, concurrent sessions, expiry, revocation, idle
   timeout, and stale permission refresh are implementation-only and untested.
   Evidence: `backend/accounts/views.py`;
   `backend/itams/settings.py`;
   `frontend/src/AuthContext.jsx`;
   `frontend/src/api/client.js`;
   `frontend/src/components/ProtectedRoute.jsx`.
7. **Password policy and administrative reset**: self-service change enforces
   only a local six-character minimum, configured platform validators are not
   visibly invoked, and User-administration reset follows a different path with
   no visible minimum. Rotation, history, complexity, expiry, reuse, reset
   recovery, and audit-failure requirements are unconfirmed.
   Evidence: `backend/accounts/views.py`;
   `backend/accounts/serializers.py`;
   `backend/itams/settings.py`;
   `frontend/src/pages/ChangePassword.jsx`;
   `frontend/src/pages/user/Create.jsx`;
   `frontend/src/pages/user/Edit.jsx`.
8. **User/account lifecycle and atomic failure**: a User may exist without a
   login account; account creation and synchronization occur after profile
   persistence; deletion removes a linked account and profile; and status
   accepts backend values beyond the two frontend options. Required fields,
   atomic rollback, archival, reactivation, historical attribution, and
   recovery are unconfirmed.
   Evidence: `backend/accounts/models.py`;
   `backend/accounts/serializers.py`;
   `backend/accounts/views.py`;
   `frontend/src/pages/user/Create.jsx`;
   `frontend/src/pages/user/Edit.jsx`;
   `frontend/src/pages/user/Delete.jsx`.
9. **Custom-Role User-administration conformance gap**: FR-010 makes
   `user_management` Admin-only among named Roles, while FR-011 permits Admin
   to grant that code to a custom Role. A non-Admin custom User manager can
   pass the User route gate but cannot load the Admin-only Role list required
   by the current create/edit pages.
   Evidence: `backend/accounts/views.py`;
   `backend/accounts/tests.py::PrivacyAuthorizationTests::test_user_manager_can_read_full_user_records`;
   `frontend/src/App.jsx`;
   `frontend/src/pages/user/Create.jsx`;
   `frontend/src/pages/user/Edit.jsx`.
10. **Department and Location administration**: FR-010 makes
    `settings_access` Admin-only among named Roles. Authenticated reads and the
    exact write behavior remain implementation-only; edit support,
    referenced-record deletion behavior, historical effects, archival, and
    whether organization masters should be globally visible are unresolved.
    Evidence: `backend/accounts/models.py`;
    `backend/accounts/views.py`;
    `backend/core/mixins.py`;
    `frontend/src/pages/admin/Masters.jsx`.
11. **Default administrative credential**: the seed migration contains a
    hard-coded initial administrative username and password. This is
    deployment/security evidence, not accepted product behavior; rotation and
    bootstrap policy are unspecified.
    Evidence: `backend/accounts/migrations/0002_seed_rbac_and_org.py`.
12. **Audit and Notification effects**: current authentication, User, and Role
    paths selectively write AuditLog entries, while Department and Location
    changes do not visibly do so. Required success/failure events,
    Notification effects, access, retention, and sensitive-value handling are
    unresolved and owned jointly with B8.
    Evidence: `backend/accounts/views.py`;
    `backend/core/services.py`;
    `backend/core/models.py`.
13. **Frontend authorization and failure behavior**: frontend gates rely on a
    cached User summary, and no frontend behavioral test verifies route
    consistency, stale Role changes, error recovery, accessibility, or
    local-storage security. Frontend gates cannot confirm backend authority.
    Evidence: `frontend/src/AuthContext.jsx`;
    `frontend/src/components/ProtectedRoute.jsx`;
    `frontend/src/App.jsx`;
    `frontend/package.json`.

## Out of Scope *(mandatory)*

### Adjacent Baseline Ownership

- Asset registry, Asset status/condition, Custodian rules, and terminal-state
  behavior: B2. Its accepted Asset-specific Role rules are not generalized
  here.
- Checkout/check-in workflow: B3.
- Approval-gated Transfer workflow: B4.
- Service Record lifecycle: B5 and ADR-0001.
- Procurement, Vendor, and catalog masters: B6.
- Warranty, AMC, alerts, and renewal: B7.
- Generic Notification and AuditLog storage, access, delivery, filtering, and
  retention: B8.
- Dashboard, report, and export calculations and presentation: B9. Any granted
  access remains subject to B1 visibility rule FR-012.
- Administrative Setting values and SMTP configuration except the tested
  access-denial boundary in FR-001 and FR-005.

### Explicitly Deferred Product Behavior

- Employee self-service Checkout is deferred; IT currently performs Checkout
  on an employee's behalf.
- Employee- or team-lead-initiated Procurement requests are deferred.
- Scheduled or periodic physical Asset audits are deferred and do not alter
  B1's rule that Department is not a visibility boundary.

### Unaccepted Adjacent Possibilities

- Self-registration, invitations, password recovery, single sign-on,
  multi-factor authentication, identity-provider integration, and
  Department-based delegated administration are neither evidenced nor accepted
  in this baseline.
- Department-based delegated administration and Department-scoped data
  visibility are not accepted by this Draft.

### Delivery Boundary

- This baseline does not resolve the remaining platform-superuser or
  Admin-Role-protection decisions, redesign identity or authorization behavior,
  change application code or tests, create a delivery plan, generate tasks or
  tickets, or authorize implementation work.
