# Brownfield Baseline Acceptance Checklist: B1 Identity, Access, and Organization

**Purpose**: Formal pre-acceptance review of the B1 requirements for authority,
authorization, privacy, evidence classification, and scope integrity

**Created**: 2026-07-29

**Executed**: 2026-08-12 — 34 of 40 pass; 5 blockers recorded, all resolved the same day (see §Blocking Findings)

**Feature**: [spec.md](../spec.md)

**Audience and timing**: Baseline approvers and security/domain reviewers before
the Draft is marked accepted

**Note**: This checklist evaluates whether the requirements are complete,
clear, consistent, measurable, and traceable. It does not test the application
or assert implementation conformance.

## Requirement Authority and Traceability

- [x] CHK001 Does every authorization and data-visibility requirement identify either an explicit stakeholder authority or passing-test evidence, without relying on implementation code alone? [Traceability, Spec §FR-001–FR-012, §ALR-001–ALR-005]
- [x] CHK002 Are all five stakeholder decisions traceable to exactly one dated clarification entry and to every requirement or scenario they authorize? [Traceability, Spec §Clarifications, §AS-011–AS-015, §FR-008–FR-012]
- [x] CHK003 Do test-backed requirements name the precise automated-test evidence supporting their accepted scope, including negative permission cases and directory privacy? [Traceability, Spec §FR-001–FR-007, §Verified Behavior Evidence]
- [x] CHK004 Does the evidence classification make clear that passing tests establish accepted AS-BUILT behavior only within their asserted cases and do not establish broader product intent? [Clarity, Spec §Evidence Classification, §Assumptions]
- [x] CHK005 Are requirements derived from `CONTEXT.md` or the Draft B2 baseline bounded to the actor, lifecycle, and visibility decisions those sources actually establish? [Consistency, Spec §FR-008–FR-009, §Accepted Intent]
- [x] CHK006 Are stakeholder-confirmed requirements, test-backed requirements, implementation-only observations, resolved decisions with conformance gaps, unresolved decisions, and deferred behavior distinguishable throughout the specification? [Completeness, Spec §Evidence Classification, §Baseline Evidence and Unresolved Conflicts] — *resolved 2026-08-12, see Blocker 1*

## Named Roles and Permission Codes

- [x] CHK007 Does the specification consistently distinguish a Role as a grouping from a permission code as an action grant, without treating either as a data-scope rule by itself? [Consistency, Spec §Domain Alignment, §FR-010–FR-012]
- [x] CHK008 Is the accepted named Role matrix complete for Admin, IT Manager, IT Staff, HR, Employee, and Viewer, with every granted code stated explicitly and omissions meaningful? [Completeness, Spec §FR-010, §Permission Code Inventory and Accepted Named Role Matrix]
- [x] CHK009 Is Admin's phrase “all current permission codes” anchored unambiguously to the evidence-date inventory so later codes cannot silently enter the accepted baseline? [Ambiguity, Spec §FR-010, §Permission Code Inventory and Accepted Named Role Matrix] — *resolved 2026-08-12, see Blocker 2*
- [x] CHK010 Is it explicit that migration-seeded grants are supporting conformance evidence rather than the authority for the accepted named Role matrix? [Traceability, Spec §Assumptions, §Accepted Intent, §Unresolved Conflict 2]
- [x] CHK011 Does the custom-Role requirement define what counts as an “existing permission code” and whether later-added codes require a new policy decision? [Ambiguity, Spec §FR-011] — *resolved 2026-08-12, see Blocker 2*
- [x] CHK012 Is the no-implicit-bypass rule for custom Roles consistent with the accepted Admin authority and the separately unresolved platform-superuser and Admin-Role-protection mechanisms? [Consistency, Spec §FR-010–FR-011, §Unresolved Conflict 5]
- [x] CHK013 Is it clear that `user_management` and `settings_access` are Admin-only among named Roles but may be deliberately granted to an Admin-managed custom Role? [Clarity, Spec §FR-010–FR-011, §Permission Code Inventory and Accepted Named Role Matrix]
- [x] CHK014 Are permission-code action meanings kept separate from sibling-baseline lifecycle requirements, reports, Settings, and master-data behavior that B1 does not own? [Scope, Spec §Permission Code Inventory and Accepted Named Role Matrix, §Out of Scope]

## Backend Authorization and Frontend Boundaries

- [x] CHK015 Is backend authorization identified as authoritative for every protected B1 action, regardless of frontend route, menu, or control visibility? [Completeness, Spec §AS-004, §ALR-001]
- [x] CHK016 Does the specification avoid citing hidden frontend controls or protected routes as evidence that backend authorization exists? [Consistency, Spec §Evidence Classification, §Implementation-Only Observations]
- [x] CHK017 Are known frontend/backend authorization mismatches preserved as implementation-only or conformance findings rather than normalized into accepted behavior? [Coverage, Spec §OBS-NC-005–OBS-NC-006, §Unresolved Conflicts 9 and 13]
- [x] CHK018 Is the denied-action requirement explicit that neither protected data nor a protected mutation may be returned or completed? [Clarity, Spec §ALR-002]
- [x] CHK019 Are unauthenticated, inactive, unlinked-profile, deleted-User, stale-session, and revoked-session authorization outcomes either specified or explicitly identified as outside the accepted test-backed boundary? [Coverage, Gap, Spec §Assumptions, §Unresolved Conflict 6]
- [x] CHK020 Are Admin Role authority, custom-Role no-bypass behavior, Role-name implementation bypass, and platform-superuser behavior kept as four distinct concepts? [Consistency, Spec §FR-010–FR-011, §Unresolved Conflict 5]

## Data Visibility and Privacy Boundaries

- [x] CHK021 Is global visibility stated consistently for every otherwise-authorized Admin, IT Manager, IT Staff, HR, Viewer, and custom Role action? [Completeness, Spec §AS-015, §FR-012, §Data Visibility Boundary]
- [x] CHK022 Is the Employee visibility boundary complete across own User identity, Custodian-scoped Assets, Checkouts, Transfers, other lifecycle records, and derived summaries? [Completeness, Spec §FR-008, §FR-012]
- [x] CHK023 Is “directly involving the Employee” replaced everywhere by objective record relationships rather than left as an interpretive phrase? [Clarity, Spec §AS-015, §FR-012, §Data Visibility Boundary] — *resolved 2026-08-12, see Blocker 3*
- [x] CHK024 Does the specification define the Employee visibility outcome when a Service Record clears Custodian or another lifecycle event removes the relationship that previously made an Asset visible? [Edge Case, Spec §FR-012]
- [x] CHK025 Are the non-Employee global directory, exact minimal field set, Disabled-User exclusion, and Employee directory denial specified as separate privacy rules? [Completeness, Spec §AS-005–AS-007, §FR-003–FR-004, §Data Visibility Boundary]
- [x] CHK026 Is the rule that Department is organizational data—not an authorization boundary—consistent across Domain Alignment, FR-012, ALR-005, Key Entities, assumptions, conflicts, and Out of Scope? [Conflict, Spec §Domain Alignment, §FR-012, §ALR-005, §Key Entities] — *see Note A*
- [x] CHK027 Is it explicit that both an action grant and the applicable global-or-Employee visibility rule must succeed before data may be returned? [Clarity, Spec §ALR-004–ALR-005]
- [x] CHK028 Does “own User identity” identify the accepted fields or representation available to Employee, without silently exposing the full `user_management` record? [Privacy, Gap, Spec §FR-002, §FR-012] — *resolved 2026-08-12, see Blocker 4*
- [x] CHK029 Are minimal-directory access and full-User access explicitly non-interchangeable, with their different field sets and authorities traceable? [Consistency, Spec §FR-001–FR-004, §ALR-003]
- [x] CHK030 Is the global visibility consequence of granting a custom Role any data-bearing permission code explicit enough for an Admin to understand the privacy effect? [Clarity, Spec §FR-011–FR-012]

## Negative Authorization and Exception Coverage

- [x] CHK031 Are negative requirements complete for a User lacking access to full Users, Roles, permission codes, and administrative Settings? [Coverage, Spec §AS-001–AS-003, §FR-001, §NC-001–NC-002]
- [x] CHK032 Is the distinction between `settings_access` and administrative Settings authority unambiguous for named and custom Roles? [Clarity, Spec §FR-005, §FR-010–FR-011]
- [x] CHK033 Are missing `asset_custody_manage` and missing `transfer_request` covered as separate rejected-action requirements with precise evidence boundaries? [Coverage, Spec §FR-006–FR-007, §NC-004–NC-005]
- [x] CHK034 Are Employee attempts to access another User, the cross-User directory, non-Custodian Assets, and unrelated lifecycle records all covered by explicit denial requirements? [Coverage, Spec §AS-007, §FR-008, §ALR-005]
- [x] CHK035 Is Disabled-User exclusion defined separately from login denial, account deactivation, and other implementation-only status behavior? [Consistency, Spec §FR-004, §NC-003, §Current Validation, Failure, Audit, and Notification Behavior]

## Deferred Requests and Scope Integrity

- [x] CHK036 Is the absence of Employee-initiated Checkout, Transfer, and Procurement requests stated consistently in scenarios, requirements, C6 resolution, and deferred scope? [Consistency, Spec §AS-012, §FR-009, §Unresolved Conflict 1, §Explicitly Deferred Product Behavior] — *resolved 2026-08-12, see Blocker 5*
- [x] CHK037 Does the specification distinguish “no Employee request in current scope” from HR or IT Manager initiating Transfer and IT performing Checkout on the Employee's behalf? [Clarity, Spec §FR-009]
- [x] CHK038 Are deferred request workflows prevented from appearing as currently implemented capabilities through Role descriptions, permission-code names, observations, or success criteria? [Scope, Conflict, Spec §SC-006, §Unresolved Conflict 1, §Out of Scope]

## Evidence Visibility and Acceptance Readiness

- [x] CHK039 Are all authentication, password, User mutation, organization-master, audit, Notification, frontend, and bypass behaviors lacking authority or tests still visible as implementation-only observations or unresolved findings with repository paths? [Completeness, Spec §SC-005, §Implementation-Only Observations, §Unresolved Conflicts]
- [x] CHK040 Can an approver objectively determine from SC-001–SC-007 whether every accepted authorization/privacy requirement is traceable, every negative boundary is covered, every implementation-only behavior remains qualified, and every unresolved finding has been reviewed before acceptance? [Measurability, Spec §Success Criteria] — *see Note B*

## Blocking Findings — All Resolved 2026-08-12

**BLOCKER 1 — CHK006: an evidence label is used but never defined.**
§Evidence Classification defines four categories: Stakeholder-confirmed,
Test-backed current behavior, Implementation-only observation, and Unresolved.
AS-004 is labelled **“Governance-backed”**, which appears nowhere in the scheme.
It is the only scenario asserting that backend authorization outranks frontend
visibility — a security-relevant claim — so a reviewer cannot tell whether it
carries requirement force or is an observation. *Fix*: define
“Governance-backed” in §Evidence Classification as sourced to
`.specify/memory/constitution.md` and not open to per-baseline amendment, or
relabel AS-004 to an existing category. (B2 carried the identical defect and
resolved it the first way.)
**Resolved 2026-08-12**: "Governance-backed" is now defined in §Evidence
Classification as constitution-sourced, carrying the same requirement force as
stakeholder-confirmed content and not open to amendment during this baseline's
review. Every label used on an AS scenario is now defined or is a composite of
defined categories.

**BLOCKER 2 — CHK009 and CHK011: the permission-code set is temporally
unanchored.** FR-010 grants Admin “all current permission codes” and FR-011
allows custom Roles “any combination of existing permission codes”. Neither
fixes *when* “current” or “existing” is evaluated. The §Permission Code
Inventory lists nine codes as of the 2026-07-29 evidence date, but nothing binds
the requirements to that list. As written, a tenth code added later would join
Admin's accepted grant and become available to custom Roles without any
stakeholder decision — and once this baseline is accepted its requirement
content is immutable, so the drift could not be corrected in place. *Fix*: anchor
both requirements to the nine codes enumerated in the dated inventory, and state
explicitly that introducing a new permission code requires a new decision rather
than inheriting these grants.
**Resolved 2026-08-12**: FR-010 now defines "the accepted permission-code set"
as exactly the nine codes enumerated at the 2026-07-29 Evidence Date and states
that a later-added code MUST NOT enter any named Role's grant by operation of
that requirement. FR-011 binds custom Roles to the same set and records that
assigning a post-Evidence-Date code is undecided. The matrix table and Admin's
row now reference the fixed set rather than "all current" codes.

**BLOCKER 3 — CHK023: the Employee scope is objective in FR-012 and
interpretive everywhere else.** FR-012 enumerates precise relationships
(Custodian, Checkout User, Transfer previous or new owner). But §Domain
Alignment still says Employee sees “directly involving lifecycle records”,
AS-015 says records that “directly identify the Employee”, and the §Data
Visibility Boundary table says “directly involving records listed in FR-012”.
Only the third points back to the enumeration. Since B1 is the privacy baseline,
an unqualified “directly involving” invites a broader reading than FR-012
permits. *Fix*: make every occurrence cite FR-012's enumerated relationships, or
delete the interpretive phrasing.
**Resolved 2026-08-12**: §Domain Alignment now says "the lifecycle records
enumerated in FR-012", AS-015 spells out the three relationships inline, and the
§Data Visibility Boundary row points at FR-012. The phrase survives in exactly
one place — the §Clarifications entry of 2026-07-29 — and was deliberately left
verbatim there: that entry is the dated record of what the stakeholder actually
said, and rewriting it would falsify the traceability CHK002 depends on.

**BLOCKER 4 — CHK028: “own User identity” has no defined field set.** FR-012
accepts that an Employee may see “their own User identity” without saying what
that comprises. FR-002 establishes that the full record includes email address
and linked login username, and ALR-003 is careful that minimal-directory access
never implies full-record access — yet nothing bounds the Employee's view of
their *own* record. Read literally, it could return the full `user_management`
representation. This is an accepted requirement, not a recorded gap, so it would
freeze on acceptance. *Fix*: enumerate the accepted self-identity fields, or
demote the clause to an explicit unresolved finding.
**Resolved 2026-08-12** by the second route, since the clarification never
stated a field set and enumerating one here would invent stakeholder intent.
FR-012's clause now records that the field set is NOT accepted, cites new
Unresolved Conflict 14, and forbids reading it as granting the FR-002 full
representation in the interim. SC-007 already gates acceptance on every
unresolved finding being reviewed, so the decision cannot be skipped.

**BLOCKER 5 — CHK036: deferred scope omits Employee-initiated Transfer.**
AS-012, FR-009, and the C6 resolution each state that an Employee initiates no
Checkout, Transfer, **or** Procurement request. §Explicitly Deferred Product
Behavior lists only Employee self-service Checkout and Employee/team-lead
Procurement requests — Transfer is absent from all three of the deferred,
unaccepted, and out-of-scope lists. A reader cannot tell whether
Employee-initiated Transfer is a deferred possibility like the other two or
permanently rejected because HR/IT Manager always initiates. *Fix*: add it to
the deferred list, or state in §Unaccepted Adjacent Possibilities that it is
rejected rather than deferred.
**Resolved 2026-08-12** by the second route, on the evidence: `CONTEXT.md`
carries explicit deferral notes for Employee self-service Checkout and for
Procurement requests, but describes Transfer as requested by HR or IT Manager on
an employee's behalf by design, with no deferred variant. §Explicitly Deferred
Product Behavior now states why Transfer is not listed there, and §Unaccepted
Adjacent Possibilities records that introducing it would need a new decision
rather than the lifting of a deferral.

## Non-Blocking Notes

**Note A — CHK026 (passes).** Every normative statement about Department is
definitive and mutually consistent: §Domain Alignment (“is not an authorization
or data-visibility boundary”), FR-012 (“MUST NOT expand or restrict”), ALR-005
(“MUST NOT be used as a substitute grant”), Assumptions, and Out of Scope. Only
the descriptive §Key Entities gloss softens it to “does not **yet** define an
accepted visibility boundary”, which reads as provisional against an otherwise
settled rule. Worth aligning, but no requirement is ambiguous.

**Note B — CHK040 (passes).** SC-001 through SC-007 collectively cover FR-001
through FR-012, the negative boundaries, the implementation-only labelling
discipline, and the unresolved-findings review gate. ALR-001 (backend
authorization is authoritative) has no corresponding success criterion — it is
governance-derived and arguably not measurable in a review set, but an approver
looking only at the Success Criteria would not see it.

## Notes

- Check items off only after reviewing the written specification and its cited
  authority; do not use application behavior alone to satisfy an item.
- Record acceptance findings inline beneath the relevant item and preserve
  unresolved implementation conformance gaps in the specification.
- A documentation-only brownfield baseline does not require `plan.md` under
  the repository constitution; this checklist is an acceptance gate, not an
  implementation-planning gate.
- **Sequencing note**: B1 has no baseline dependencies, so this result does not
  rest on any unaccepted sibling. The reverse is not true — B2's CHK013, CHK014,
  and CHK018 rest on FR-010 and FR-011 here, so resolving Blocker 2 may require
  re-running those three items in
  `specs/001-asset-register-lifecycle-baseline/checklists/baseline-acceptance.md`.
