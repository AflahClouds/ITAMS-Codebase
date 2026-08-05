# Brownfield Baseline Acceptance Checklist: B1 Identity, Access, and Organization

**Purpose**: Formal pre-acceptance review of the B1 requirements for authority,
authorization, privacy, evidence classification, and scope integrity

**Created**: 2026-07-29

**Feature**: [spec.md](../spec.md)

**Audience and timing**: Baseline approvers and security/domain reviewers before
the Draft is marked accepted

**Note**: This checklist evaluates whether the requirements are complete,
clear, consistent, measurable, and traceable. It does not test the application
or assert implementation conformance.

## Requirement Authority and Traceability

- [ ] CHK001 Does every authorization and data-visibility requirement identify either an explicit stakeholder authority or passing-test evidence, without relying on implementation code alone? [Traceability, Spec §FR-001–FR-012, §ALR-001–ALR-005]
- [ ] CHK002 Are all five stakeholder decisions traceable to exactly one dated clarification entry and to every requirement or scenario they authorize? [Traceability, Spec §Clarifications, §AS-011–AS-015, §FR-008–FR-012]
- [ ] CHK003 Do test-backed requirements name the precise automated-test evidence supporting their accepted scope, including negative permission cases and directory privacy? [Traceability, Spec §FR-001–FR-007, §Verified Behavior Evidence]
- [ ] CHK004 Does the evidence classification make clear that passing tests establish accepted AS-BUILT behavior only within their asserted cases and do not establish broader product intent? [Clarity, Spec §Evidence Classification, §Assumptions]
- [ ] CHK005 Are requirements derived from `CONTEXT.md` or the accepted B2 baseline bounded to the actor, lifecycle, and visibility decisions those sources actually establish? [Consistency, Spec §FR-008–FR-009, §Accepted Intent]
- [ ] CHK006 Are stakeholder-confirmed requirements, test-backed requirements, implementation-only observations, resolved decisions with conformance gaps, unresolved decisions, and deferred behavior distinguishable throughout the specification? [Completeness, Spec §Evidence Classification, §Baseline Evidence and Unresolved Conflicts]

## Named Roles and Permission Codes

- [ ] CHK007 Does the specification consistently distinguish a Role as a grouping from a permission code as an action grant, without treating either as a data-scope rule by itself? [Consistency, Spec §Domain Alignment, §FR-010–FR-012]
- [ ] CHK008 Is the accepted named Role matrix complete for Admin, IT Manager, IT Staff, HR, Employee, and Viewer, with every granted code stated explicitly and omissions meaningful? [Completeness, Spec §FR-010, §Permission Code Inventory and Accepted Named Role Matrix]
- [ ] CHK009 Is Admin's phrase “all current permission codes” anchored unambiguously to the evidence-date inventory so later codes cannot silently enter the accepted baseline? [Ambiguity, Spec §FR-010, §Permission Code Inventory and Accepted Named Role Matrix]
- [ ] CHK010 Is it explicit that migration-seeded grants are supporting conformance evidence rather than the authority for the accepted named Role matrix? [Traceability, Spec §Assumptions, §Accepted Intent, §Unresolved Conflict 2]
- [ ] CHK011 Does the custom-Role requirement define what counts as an “existing permission code” and whether later-added codes require a new policy decision? [Ambiguity, Spec §FR-011]
- [ ] CHK012 Is the no-implicit-bypass rule for custom Roles consistent with the accepted Admin authority and the separately unresolved platform-superuser and Admin-Role-protection mechanisms? [Consistency, Spec §FR-010–FR-011, §Unresolved Conflict 5]
- [ ] CHK013 Is it clear that `user_management` and `settings_access` are Admin-only among named Roles but may be deliberately granted to an Admin-managed custom Role? [Clarity, Spec §FR-010–FR-011, §Permission Code Inventory and Accepted Named Role Matrix]
- [ ] CHK014 Are permission-code action meanings kept separate from sibling-baseline lifecycle requirements, reports, Settings, and master-data behavior that B1 does not own? [Scope, Spec §Permission Code Inventory and Accepted Named Role Matrix, §Out of Scope]

## Backend Authorization and Frontend Boundaries

- [ ] CHK015 Is backend authorization identified as authoritative for every protected B1 action, regardless of frontend route, menu, or control visibility? [Completeness, Spec §AS-004, §ALR-001]
- [ ] CHK016 Does the specification avoid citing hidden frontend controls or protected routes as evidence that backend authorization exists? [Consistency, Spec §Evidence Classification, §Implementation-Only Observations]
- [ ] CHK017 Are known frontend/backend authorization mismatches preserved as implementation-only or conformance findings rather than normalized into accepted behavior? [Coverage, Spec §OBS-NC-005–OBS-NC-006, §Unresolved Conflicts 9 and 13]
- [ ] CHK018 Is the denied-action requirement explicit that neither protected data nor a protected mutation may be returned or completed? [Clarity, Spec §ALR-002]
- [ ] CHK019 Are unauthenticated, inactive, unlinked-profile, deleted-User, stale-session, and revoked-session authorization outcomes either specified or explicitly identified as outside the accepted test-backed boundary? [Coverage, Gap, Spec §Assumptions, §Unresolved Conflict 6]
- [ ] CHK020 Are Admin Role authority, custom-Role no-bypass behavior, Role-name implementation bypass, and platform-superuser behavior kept as four distinct concepts? [Consistency, Spec §FR-010–FR-011, §Unresolved Conflict 5]

## Data Visibility and Privacy Boundaries

- [ ] CHK021 Is global visibility stated consistently for every otherwise-authorized Admin, IT Manager, IT Staff, HR, Viewer, and custom Role action? [Completeness, Spec §AS-015, §FR-012, §Data Visibility Boundary]
- [ ] CHK022 Is the Employee visibility boundary complete across own User identity, Custodian-scoped Assets, Checkouts, Transfers, other lifecycle records, and derived summaries? [Completeness, Spec §FR-008, §FR-012]
- [ ] CHK023 Is “directly involving the Employee” replaced everywhere by objective record relationships rather than left as an interpretive phrase? [Clarity, Spec §AS-015, §FR-012, §Data Visibility Boundary]
- [ ] CHK024 Does the specification define the Employee visibility outcome when a Service Record clears Custodian or another lifecycle event removes the relationship that previously made an Asset visible? [Edge Case, Spec §FR-012]
- [ ] CHK025 Are the non-Employee global directory, exact minimal field set, Disabled-User exclusion, and Employee directory denial specified as separate privacy rules? [Completeness, Spec §AS-005–AS-007, §FR-003–FR-004, §Data Visibility Boundary]
- [ ] CHK026 Is the rule that Department is organizational data—not an authorization boundary—consistent across Domain Alignment, FR-012, ALR-005, Key Entities, assumptions, conflicts, and Out of Scope? [Conflict, Spec §Domain Alignment, §FR-012, §ALR-005, §Key Entities]
- [ ] CHK027 Is it explicit that both an action grant and the applicable global-or-Employee visibility rule must succeed before data may be returned? [Clarity, Spec §ALR-004–ALR-005]
- [ ] CHK028 Does “own User identity” identify the accepted fields or representation available to Employee, without silently exposing the full `user_management` record? [Privacy, Gap, Spec §FR-002, §FR-012]
- [ ] CHK029 Are minimal-directory access and full-User access explicitly non-interchangeable, with their different field sets and authorities traceable? [Consistency, Spec §FR-001–FR-004, §ALR-003]
- [ ] CHK030 Is the global visibility consequence of granting a custom Role any data-bearing permission code explicit enough for an Admin to understand the privacy effect? [Clarity, Spec §FR-011–FR-012]

## Negative Authorization and Exception Coverage

- [ ] CHK031 Are negative requirements complete for a User lacking access to full Users, Roles, permission codes, and administrative Settings? [Coverage, Spec §AS-001–AS-003, §FR-001, §NC-001–NC-002]
- [ ] CHK032 Is the distinction between `settings_access` and administrative Settings authority unambiguous for named and custom Roles? [Clarity, Spec §FR-005, §FR-010–FR-011]
- [ ] CHK033 Are missing `asset_custody_manage` and missing `transfer_request` covered as separate rejected-action requirements with precise evidence boundaries? [Coverage, Spec §FR-006–FR-007, §NC-004–NC-005]
- [ ] CHK034 Are Employee attempts to access another User, the cross-User directory, non-Custodian Assets, and unrelated lifecycle records all covered by explicit denial requirements? [Coverage, Spec §AS-007, §FR-008, §ALR-005]
- [ ] CHK035 Is Disabled-User exclusion defined separately from login denial, account deactivation, and other implementation-only status behavior? [Consistency, Spec §FR-004, §NC-003, §Current Validation, Failure, Audit, and Notification Behavior]

## Deferred Requests and Scope Integrity

- [ ] CHK036 Is the absence of Employee-initiated Checkout, Transfer, and Procurement requests stated consistently in scenarios, requirements, C6 resolution, and deferred scope? [Consistency, Spec §AS-012, §FR-009, §Unresolved Conflict 1, §Explicitly Deferred Product Behavior]
- [ ] CHK037 Does the specification distinguish “no Employee request in current scope” from HR or IT Manager initiating Transfer and IT performing Checkout on the Employee's behalf? [Clarity, Spec §FR-009]
- [ ] CHK038 Are deferred request workflows prevented from appearing as currently implemented capabilities through Role descriptions, permission-code names, observations, or success criteria? [Scope, Conflict, Spec §SC-006, §Unresolved Conflict 1, §Out of Scope]

## Evidence Visibility and Acceptance Readiness

- [ ] CHK039 Are all authentication, password, User mutation, organization-master, audit, Notification, frontend, and bypass behaviors lacking authority or tests still visible as implementation-only observations or unresolved findings with repository paths? [Completeness, Spec §SC-005, §Implementation-Only Observations, §Unresolved Conflicts]
- [ ] CHK040 Can an approver objectively determine from SC-001–SC-007 whether every accepted authorization/privacy requirement is traceable, every negative boundary is covered, every implementation-only behavior remains qualified, and every unresolved finding has been reviewed before acceptance? [Measurability, Spec §Success Criteria]

## Notes

- Check items off only after reviewing the written specification and its cited
  authority; do not use application behavior alone to satisfy an item.
- Record acceptance findings inline beneath the relevant item and preserve
  unresolved implementation conformance gaps in the specification.
- A documentation-only brownfield baseline does not require `plan.md` under
  the repository constitution; this checklist is an acceptance gate, not an
  implementation-planning gate.
