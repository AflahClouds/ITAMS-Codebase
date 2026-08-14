# Feature Specification: AS-BUILT Procurement, Vendor, and Catalog Masters Baseline

**Feature Branch**: `docs/baseline-spec-migration`

**Created**: 2026-08-03

**Status**: Draft

**Evidence Date**: 2026-07-29

**Input**: User description: "Create an AS-BUILT Brownfield Baseline
specification for ROADMAP.md entry B6: Procurement, Vendor, and catalog
masters. Cover completed-purchase recording, Vendor, Category, Brand, Model,
Purchase Mode, protected deletion, invoice/PO information, and Asset linking.
Keep C7, C9, physical-arrival enforcement, date rules, Procurement deletion
and history, and whether Assets may exist without Procurement unresolved.
Exclude employee/team-lead Procurement requests and approval workflows. Do not
modify application code or promote implementation-only behavior to product
intent."

## Clarifications

### Session 2026-08-03

- Q: How must physical arrival be enforced before Procurement is saved? → A:
  Asset arrival record plus required attestation.
- Q: What date rules apply to completed Procurement? → A: Require purchase and
  invoice dates; enforce purchase ≤ invoice ≤ record date and purchase ≤ every
  Asset arrival ≤ record date, without ordering invoice versus arrival.
- Q: How are Procurement deletion and Asset-link changes retained? → A:
  Archive-only Procurement plus reasoned append-only Asset-link history.
- Q: What Asset–Procurement linkage and exception policy applies? → A:
  One-or-more Assets per Procurement; temporary `In Storage` staging and
  reasoned, visibly flagged legacy/import exceptions.
- Q: Which matching frontend/backend B6 permission contract resolves C9? → A:
  Existing action codes with non-Employee `asset_view` reads and no Employee
  B6 pages.

### Session 2026-08-04

- Q: What identity and normalization rules apply to invoice and PO numbers? →
  A: Invoice unique within Vendor; optional PO globally unique; trimmed,
  case-insensitive comparison with preserved display text.
- Q: Where do invoice and PO files belong, and when are they required? →
  A: Store them once on Procurement; require an invoice file and require a PO
  file when a PO number exists; expose them through linked Assets and retain
  replaced versions.
- Q: How are Vendor and catalog-master identities defined and normalized? →
  A: Use globally unique normalized names for Vendor, Category, Brand, and
  Purchase Mode; make Model Brand-scoped; normalize whitespace and case for
  comparison; preserve display text; support reference-safe rename and
  controlled merge; keep Vendor contacts optional and non-identifying.
- Q: How are legacy free-text Vendors and the "Unknown Vendor" backfill handled?
  → A: Preserve original text; automatically match only unambiguous normalized
  identities; flag blank, unknown, ambiguous, or duplicate candidates; keep
  history readable but block flagged Vendors from new use; allow an authorized
  maintainer to map or merge them with retained history.
- Q: Which B6 actions create audit entries or Notifications? → A: Audit every
  successful B6 mutation plus rejected authorization, identity-conflict, and
  protected-deletion attempts; notify IT Managers only for Procurement archive,
  invoice/PO file replacement, Asset detachment, master merge/deletion, and
  legacy Vendor resolution; leave shared infrastructure behavior to B8.

## Specification Lineage *(mandatory)*

**Type**: Brownfield Baseline

**Roadmap Reference**: `ROADMAP.md`, entry B6 — Procurement, Vendor, and
catalog masters.

**Extends**: None.

**Supersedes**: None.

**Reciprocal Links**: `ROADMAP.md` entry B6 links to this Draft. Future changes
after acceptance must be recorded in a new specification and linked here with
`Extends`, `Supersedes`, or `Superseded by` metadata.

### Acceptance Record

*Pending — this baseline is `Draft`. Completing every field below is what moves
it to accepted; until then the fields stay marked pending.*

| Field | Value |
| --- | --- |
| Stakeholder decision | *Pending* |
| Accepting stakeholder | *Pending* |
| Acceptance date | *Pending* |
| Reviewed evidence date | 2026-07-29 |
| Acceptance checklist result | 40 of 40 items closed; executed 2026-08-12 — see `checklists/baseline-acceptance.md` |
| Review basis used for the Success Criteria | **Full population at the reviewed Evidence Date (2026-07-29).** §Success Criteria permits either the whole population or a stratified sample; the whole population is chosen because the deployment's Procurement count is small enough to inspect individually, and a census removes any argument about whether a sample covered the FR-014 and FR-022 exception states — the cases most likely to be rare and most likely to matter. If the population later exceeds practical inspection, the stratified rule in §Success Criteria applies and the basis actually used MUST be re-recorded here rather than inherited from this entry. |
| Unresolved items deliberately carried forward | Concurrent Asset linking — **operator-facing behavior only**: conflict presentation, retry, and stale-edit handling. The atomicity half of that finding is *not* carried forward; it is an implementation conformance gap against ALR-007. See §Unresolved Conflicts, finding 1 disposition. |

**Immutability boundary**: on the acceptance date recorded above, the
requirement and acceptance content of this specification becomes an immutable
flow-forward record. From that point a semantic change MUST use a new feature
directory with reciprocal `Extends`, `Supersedes`, or `Superseded by` links;
this specification may be edited only to add or correct that non-semantic
lineage metadata. *(Constitution §III.)*

## Domain Alignment *(mandatory)*

**Canonical Terms**:

- **Procurement** is a record of a completed Asset purchase, created by IT
  after physical arrival. It is not a purchase request, approval, order-status,
  or delivery-tracking workflow.
- **Vendor** is a first-class managed entity shared by Procurement and Service
  Record. Vendor identity must not be reduced to free text because reliable
  Vendor-grouped reporting depends on consistent references.
- **Asset** is the physical IT item associated with Procurement. This baseline
  covers the Procurement association but not Asset status, condition,
  Custodian, or lifecycle transitions. Each Asset has at most one current
  Procurement; a new Asset may be temporarily unlinked only while `In Storage`.
- **Asset arrival record** is the recorded arrival date and Location for one
  physically received Asset. It is a Procurement precondition, not an Asset
  status or a delivery workflow.
- **Category**, **Brand**, and **Model** are catalog masters used to classify an
  Asset. **Purchase Mode** is the managed master describing how a completed
  purchase was made.
- **invoice information** and **purchase-order (PO) information** identify the
  business documents associated with the completed purchase. Purchase date and
  invoice date are required under the accepted ordering rules. Invoice number
  is required and unique within Vendor; PO number is optional and globally
  unique when present. Document-file expectations are settled by the 2026-08-04
  clarification and specified in FR-018: Procurement owns one current invoice
  file, owns one current PO file whenever a PO number is present, stores each
  file once, exposes it through every linked Asset, and retains superseded
  versions on replacement.
- Use **Procurement**, not "procurement request," for the completed-purchase
  record in this baseline. Use **Checkout**, not "Assignment," at adjacent
  Asset-custody boundaries.

**Relevant Decisions**:

- `docs/adr/0001-service-record-lifecycle.md` confirms that Vendor is a
  first-class entity shared by Procurement and Service Record so Vendor-based
  reporting uses reliable identity rather than free-typed names.
- No current ADR defines Procurement field rules. The 2026-08-03
  clarifications establish physical-arrival enforcement, archive-only
  Procurement, Asset-link history, linkage cardinality, and B6 permission and
  control visibility for this Draft.
- The Draft B2 baseline at
  `specs/001-asset-register-lifecycle-baseline/spec.md` owns Asset register and
  lifecycle behavior and explicitly leaves indefinite absence of Procurement
  unresolved.

**Lifecycle and Actors**:

- IT records Procurement only for a completed purchase. Employee- and
  team-lead-initiated purchase requests and purchase approval are outside the
  current lifecycle.
- Each Asset must have an arrival record containing its arrival date and
  Location before it can be linked to Procurement. Saving Procurement also
  requires the acting User to attest that every linked Asset has physically
  arrived; the attesting actor and time are retained.
- Recording, editing, linking, unlinking, or deleting Procurement must not be
  interpreted as an Asset status, condition, Custodian, Checkout, Transfer, or
  Service Record transition.
- Completed Procurement is never hard-deleted. Archiving retains the record
  and does not itself detach Assets; attachments and detachments are separate,
  reasoned operations retained in append-only history.
- Procurement always has at least one current Asset. A new unlinked Asset must
  remain `In Storage` and cannot become `Available` or enter Checkout,
  Transfer, or Service Record activity until linked. A legacy/import Asset may
  remain unlinked only with a recorded exception reason and visible flag.
- B1 supplies Roles, permission codes, and data-visibility rules. A
  non-Employee User with `asset_view` may read standalone Procurement, Vendor,
  and catalog-master data; Employee receives no B6 pages or standalone B6
  records. Procurement creation uses `asset_create`; editing and Asset-link
  changes use `asset_edit`; archiving uses `asset_delete`; Vendor and catalog
  master writes use `settings_access`. Frontend routes and controls mirror the
  same action checks while backend authorization remains authoritative.
- B8 owns generic AuditLog and Notification storage, access, and retention.
  This Draft keeps the required Procurement and master-data events unresolved.

### Evidence Classification

This Draft uses the following classifications:

- **Stakeholder-confirmed**: stated in `CONTEXT.md`, an ADR, the B6 roadmap
  boundary, or the explicit stakeholder instruction dated 2026-08-03.
- **Governance-backed**: required by `.specify/memory/constitution.md` rather
  than by a product decision. It applies to every capability, carries the same
  requirement force as stakeholder-confirmed content, and is not open to
  amendment or rejection during this baseline's review.
- **Test-backed current behavior**: demonstrated by an automated test and
  eligible for this requested AS-BUILT baseline without implying a broader
  unstated policy.
- **Implementation-only observation**: visible in backend or frontend code
  without dedicated automated behavioral coverage or stakeholder confirmation.
- **Unresolved**: contradictory or incomplete evidence that must not be
  generalized into an accepted requirement.
- **Deferred**: intentionally excluded from the current product scope.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record a Completed Purchase (Priority: P1)

An authorized IT User records a completed Asset purchase using a managed
Vendor and the available invoice and PO information, without opening a request
or approval workflow.

**Why this priority**: Procurement is the business record that connects an
acquired Asset to its supplier and purchase documentation.

**Independent Test**: Attempt to save a completed purchase with a missing
Asset arrival record, then with complete arrival date and Location but no
attestation, and finally with both arrival records and attestation. Only the
final attempt succeeds and it identifies the Vendor and invoice/PO information.

**Acceptance Scenarios**:

1. **AS-001 — Stakeholder-confirmed**: **Given** IT has completed a purchase and
   every linked Asset has an arrival date and Location, **When** the acting User
   attests that all linked Assets physically arrived and saves Procurement,
   **Then** the record retains the attesting actor and time, represents the
   completed purchase, and includes a managed Vendor plus invoice and PO
   information.
2. **AS-002 — Stakeholder-confirmed**: **Given** an Employee or team lead wants
   an Asset purchased, **When** they use current-scope ITAMS, **Then** no
   Procurement request or purchase-approval action is available; B6 begins only
   with IT recording the completed purchase.
3. **AS-010 — Stakeholder-confirmed**: **Given** a proposed purchase date,
   invoice date, linked Asset arrival dates, and Procurement record date,
   **When** Procurement is saved, **Then** both purchase and invoice dates are
   present, purchase date is no later than invoice date or any linked Asset
   arrival date, every date is no later than the record date, and invoice date
   may fall before or after an Asset arrival date.
4. **AS-015 — Stakeholder-confirmed**: **Given** invoice and PO identifiers,
   **When** Procurement is saved, **Then** invoice number is nonblank and unique
   within Vendor, PO number is optional but globally unique when present, both
   identifiers are trimmed and compared case-insensitively, and their entered
   display text is preserved.
5. **AS-016 — Stakeholder-confirmed**: **Given** a completed Procurement with
   one or more linked Assets, **When** its purchase documents are saved or
   replaced, **Then** it has one current invoice file, has one current PO file
   whenever a PO number exists, stores each file once on Procurement, exposes
   the current documents through every linked Asset without duplicating them,
   and retains each replaced version.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-001 — Implementation-only**: The current create surface selects one
   or more Assets that appear unlinked, a Purchase Mode, a Vendor, purchase and
   invoice dates, an invoice number, and a PO number.
2. **OBS-AS-002 — Implementation-only**: The current list shows linked Asset
   identifiers, Purchase Mode, Vendor, purchase date, invoice number, and PO
   number; invoice date is stored but is not displayed in that list.
3. **OBS-AS-003 — Implementation-only partial conformance**: The current data
   contract requires a Purchase Mode, Vendor, purchase date, invoice date, and
   unique invoice number, while PO number is optional. Required dates now align
   in part with AS-010, but invoice uniqueness is currently global rather than
   Vendor-scoped, PO uniqueness and accepted normalization are not enforced, and
   the accepted date-ordering rules are not currently enforced.
4. **OBS-AS-015 — Implementation-only conformance gap**: The current Asset
   document surface recognizes Purchase Invoice and PO Document types, but the
   reviewed Procurement contract does not own, require, expose, or version the
   Procurement-level documents accepted by AS-016.

---

### User Story 2 - Associate Assets with Procurement (Priority: P1)

An authorized User reviews which Assets are associated with a completed
Procurement, attaches or detaches Assets with a reason, and can reconstruct the
complete association history even after Procurement is archived.

**Why this priority**: The association connects the physical Asset register to
the completed purchase, but its cardinality, requiredness, and history policy
materially affect Asset provenance.

**Independent Test**: Attach and detach an Asset with reasons, inspect the
immutable actor/time/before/after history, archive Procurement, and confirm the
record and history remain while archiving causes no implicit detachment.

**Acceptance Scenarios**:

1. **AS-003 — Stakeholder-confirmed boundary**: **Given** an Asset has an
   established status, condition, Custodian, and lifecycle history, **When**
   its Procurement association is recorded or changed, **Then** that
   association change does not itself alter any of those Asset lifecycle
   values or records.
2. **AS-011 — Stakeholder-confirmed**: **Given** an authorized User attaches or
   detaches an Asset, **When** the change completes, **Then** the User supplied
   a reason and an append-only history entry retains the actor, time, and
   before/after associations. **Given** Procurement is archived, **Then** the
   Procurement and its link history remain and current Asset links are not
   changed by the archive action itself.
3. **AS-012 — Stakeholder-confirmed**: **Given** a new Asset has no
   Procurement, **When** it is staged, **Then** it remains `In Storage` and is
   ineligible for `Available`, Checkout, Transfer, or Service Record activity.
   **When** it is linked, **Then** its Procurement has at least one current
   Asset and that Asset has no other current Procurement. A legacy/import Asset
   may remain unlinked only with an exception reason and visible flag.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-004 — Implementation-only**: Creating or updating Procurement can
   associate multiple Assets, and an Asset already associated with a different
   Procurement is rejected by the current write path.
2. **OBS-AS-005 — Implementation-only conformance gap**: Updating Procurement
   can attach previously unlinked Assets and detach Assets omitted from the
   submitted selection without requiring a reason or retaining dedicated link
   history.
3. **OBS-AS-006 — Implementation-only conformance gap**: Deleting Procurement
   currently hard-deletes it and clears the Procurement association on linked
   Assets, contrary to AS-011.
4. **OBS-AS-007 — Implementation-only conformance gap**: The current Asset
   record permits an empty Procurement association, current create/edit
   surfaces do not require Procurement, and the reviewed lifecycle paths do not
   enforce the staging and exception rules in AS-012.

---

### User Story 3 - Use a Shared Vendor Identity (Priority: P1)

An authorized User selects the same managed Vendor identity for Procurement
and Service Record activity so records can be grouped by Vendor reliably.

**Why this priority**: Free-typed supplier names fragment history and make
Vendor-based operational reporting unreliable.

**Independent Test**: Create one Vendor, select it for Procurement and a
Service Record, and verify both records refer to the same Vendor identity
without testing the Service Record lifecycle itself.

**Acceptance Scenarios**:

1. **AS-004 — Stakeholder-confirmed**: **Given** a Vendor is used for both a
   completed purchase and servicing, **When** those records identify the third
   party, **Then** both use the same managed Vendor identity rather than
   separate free-text names.
2. **AS-018 — Stakeholder-confirmed**: **Given** a Vendor originated from legacy
   Procurement free text, **When** the backfill is reviewed, **Then** the
   original text remains visible as provenance, only an unambiguous normalized
   identity is matched automatically, blank, "Unknown Vendor", ambiguous, and
   duplicate candidates remain flagged and unavailable for new records, and a
   `settings_access` maintainer can map or merge them into one canonical Vendor
   without making historical Procurement unreadable.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-008 — Implementation-only**: The current Vendor record uses a
   unique name and optional contact person, phone, and email, and has separate
   list, create, edit, and delete surfaces.
2. **OBS-AS-009 — Implementation-only partial conformance**: A migration converted legacy
   Procurement Vendor text to managed Vendor records, substituting "Unknown
   Vendor" when the legacy name was empty. The reviewed implementation does not
   establish the accepted provenance, review flag, new-use block, unambiguous
   matching, or resolution workflow.

---

### User Story 4 - Maintain Catalog Masters Safely (Priority: P1)

An authorized master-data maintainer manages Vendor, Category, Brand, Model,
and Purchase Mode values while referenced values are protected from deletion.

**Why this priority**: Shared master values keep Asset and Procurement data
consistent, and protected deletion prevents a cleanup action from erasing or
invalidating operational records.

**Independent Test**: For each of the five master types, attempt deletion first
while referenced by the tested Asset or Procurement and then while unused;
confirm protected data remains and the unused record can be removed.

**Acceptance Scenarios**:

1. **AS-005 — Stakeholder-confirmed scope**: **Given** an authorized
   master-data maintainer and a valid unused Vendor, Category, Brand, Model, or
   Purchase Mode value, **When** the maintainer creates, views, updates, or
   deletes that value, **Then** the selected master operation is available,
   subject to the protected-deletion rules below.
2. **AS-006 — Test-backed**: **Given** Category, Brand, or Model is referenced
   by an Asset, or Purchase Mode or Vendor is referenced by Procurement,
   **When** deletion is attempted, **Then** deletion is rejected and the Asset
   and Procurement remain unchanged.
3. **AS-007 — Test-backed**: **Given** a referenced B6 master, **When** deletion
   is attempted through the supported application interface, **Then** the User
   receives a stable explanation that the master cannot be deleted because it
   is in use.
4. **AS-008 — Test-backed**: **Given** a Vendor, Category, Brand, Model, or
   Purchase Mode is unused, **When** it is deleted, **Then** that master record
   is removed without deleting an Asset or Procurement.
5. **AS-017 — Stakeholder-confirmed**: **Given** an authorized maintainer
   creates, renames, or merges B6 master data, **When** normalized identity is
   evaluated, **Then** Vendor, Category, Brand, and Purchase Mode names are
   globally unique, Model is unique within its Brand, display text is preserved
   after whitespace normalization, references survive renames, and a controlled
   merge moves references to one surviving identity without losing provenance.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-010 — Implementation-only partial conformance**: Category, Brand,
   Model, Purchase Mode, and Vendor names are currently globally unique, and a
   seeded set of Category values is created during migration. The current model
   does not provide accepted whitespace/case normalization, Brand-scoped Model
   identity, or controlled merge behavior.
2. **OBS-AS-011 — Implementation-only**: Authenticated Users can currently read
   catalog masters without a B6-specific permission, while writes require the
   current `settings_access` mapping or an administrative bypass.
3. **OBS-AS-012 — Implementation-only conformance gap**: The current shared
   Masters page can list, add, and delete Category, Brand, Model, and Purchase
   Mode, but it does not expose the accepted rename or merge controls even
   though the current backend supports basic update.

---

### User Story 5 - Respect B6 Action Authorization (Priority: P2)

Non-Employee Users see only B6 pages and actions their existing permission
codes authorize; Employees see no standalone B6 pages. Backend authorization
remains authoritative even if a frontend check is bypassed or stale.

**Why this priority**: Procurement and master mutations affect financial
provenance and shared reference data; visual hiding alone cannot protect them.

**Independent Test**: Exercise B6 reads as Employee and non-Employee
`asset_view` Users, then exercise create, edit/link, archive, and master writes
with and without their exact permission codes. Compare every visible route and
control with the authoritative outcome.

**Acceptance Scenarios**:

1. **AS-009 — Governance-backed**: **Given** a User is not authorized for a B6
   mutation, **When** the User attempts it directly despite any visible
   control, **Then** the protected action is denied and no B6 or linked Asset
   data changes.
2. **AS-013 — Stakeholder-confirmed**: **Given** a non-Employee User with
   `asset_view`, **When** the User opens standalone Procurement, Vendor, or
   catalog-master data, **Then** read access is available. **Given** an
   Employee, **Then** those pages and standalone records are unavailable.
3. **AS-014 — Stakeholder-confirmed**: **Given** a B6 route or control for
   create, edit, Asset attachment/detachment, archive, or master write, **When**
   it is rendered or invoked, **Then** both frontend and backend apply the exact
   permission assigned by FR-016, and denial changes no data.
4. **AS-019 — Stakeholder-confirmed**: **Given** a B6 action completes or a
   protected attempt is rejected, **When** its side effects are evaluated,
   **Then** every successful mutation and every rejected authorization,
   identity-conflict, or protected-deletion attempt has an audit entry, while
   only Procurement archive, invoice/PO file replacement, Asset detachment,
   master merge/deletion, and legacy Vendor resolution emit an IT Manager
   Notification trigger.

**Current-System Verification Scenarios — Not Accepted Requirements**:

1. **OBS-AS-013 — Implementation-only partial conformance**: Procurement
   list/retrieve currently uses `asset_view`; create, edit, and delete reuse
   `asset_create`, `asset_edit`, and `asset_delete`. Current reads do not exclude
   Employee, and current delete hard-deletes rather than archives.
2. **OBS-AS-014 — Implementation-only conformance gap for resolved C9**: The
   Procurement list shows edit and delete controls without checking the
   corresponding action permissions, while destination routes and backend
   actions apply narrower checks.

### Edge Cases and Negative Cases

- **NC-001 — Test-backed**: Deleting any tested referenced Vendor, Category,
  Brand, Model, or Purchase Mode is rejected and does not remove its Asset or
  Procurement.
- **NC-002 — Test-backed**: An unused record of each B6 master type can be
  deleted.
- **NC-003 — Governance-backed**: An unauthorized mutation must change no
  Procurement, master, or Asset association even if a stale or incorrectly
  visible frontend control initiates it.
- **NC-008 — Stakeholder-confirmed**: Employee requests for standalone
  Procurement, Vendor, or catalog-master pages and records are denied. A
  missing action permission hides the matching frontend route/control and a
  direct request is also denied without changing data.
- **NC-009 — Stakeholder-confirmed**: Procurement save is rejected without
  change when invoice number is blank, its normalized value duplicates another
  invoice for the same Vendor, or a supplied normalized PO number duplicates
  any existing PO. The same normalized invoice number remains valid for a
  different Vendor.
- **NC-010 — Stakeholder-confirmed**: Procurement save is rejected without
  change when its current invoice file is missing or when a PO number exists
  without a current PO file. Replacing either current file retains the prior
  version and does not create a duplicate copy on any linked Asset.
- **NC-011 — Stakeholder-confirmed**: A master create, rename, or merge is
  rejected without change when its normalized identity is blank or conflicts
  with another identity in the applicable global or Brand scope. A Brand with a
  Model cannot be directly deleted, and a failed merge changes no references.
- **NC-012 — Stakeholder-confirmed**: A flagged legacy Vendor is rejected for a
  new Procurement or Service Record. Ambiguous normalized candidates MUST NOT be
  matched automatically, and a failed review, mapping, or merge preserves the
  historical Vendor link, source text, flag, and every related record.
- **OBS-NC-001 — Implementation-only partial conformance**: A duplicate current
  global master name or globally duplicate invoice number is rejected, but the
  accepted master normalization and Brand-scoped Model rules and the
  Vendor-scoped invoice identity and normalized optional-PO rules in FR-017 are
  not enforced.
- **OBS-NC-002 — Implementation-only**: An Asset already linked to a different
  Procurement is rejected by the current serializer, but concurrent linking,
  transaction boundaries, and partial-failure rollback are untested.
- **OBS-NC-003 — Implementation-only conformance gap**: The current frontend
  requires at least one selected Asset, but the authoritative data path may
  permit a Procurement to end with no Assets and allows unlinked Assets without
  the staging or exception controls required by FR-013 and FR-014.
- **OBS-NC-004 — Implementation-only conformance gap**: Current date fields
  reject missing or malformed values, but the reviewed implementation does not
  enforce the ordering and nonfuture rules in FR-010.
- **NC-004 — Stakeholder-confirmed**: Procurement save is rejected without
  change if any linked Asset lacks an arrival date or Location, or if the acting
  User does not explicitly attest that every linked Asset physically arrived.
- **NC-005 — Stakeholder-confirmed**: Procurement save is rejected without
  change when purchase date or invoice date is missing, purchase date follows
  invoice date or any linked Asset arrival date, or any purchase, invoice, or
  arrival date follows the Procurement record date.
- **OBS-NC-005 — Implementation-only**: Vendor deletion is protected when
  referenced by the tested Procurement. Protection for every Service Record or
  AMC reference follows current relationships but lacks dedicated B6 test
  coverage.
- **OBS-NC-006 — Implementation-only partial conformance**: Procurement create,
  update, and delete currently produce generic audit entries, while other
  successful B6 mutations and the accepted rejected-attempt classes are not
  comprehensively audited, Asset link/unlink changes do not satisfy the accepted
  reasoned history contract, and no accepted B6 Notification trigger set is
  implemented.
- **NC-013 — Stakeholder-confirmed**: A B6 mutation whose required audit entry
  cannot be committed is rejected with no B6 data change. Routine creates,
  edits, Asset attachments, and validation failures emit no Notification;
  rejected attempts are audit-only.
- **NC-006 — Stakeholder-confirmed**: Procurement cannot be hard-deleted.
  Archiving preserves the record and every link-history entry, and it makes no
  implicit Asset attachment or detachment.
- **NC-007 — Stakeholder-confirmed**: A save that would leave Procurement with
  no current Asset, link an Asset already linked elsewhere, move a new unlinked
  Asset out of `In Storage`, or enter custody/service without a link is rejected
  without change. A legacy/import exception is rejected unless both its reason
  and visible flag are retained.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Procurement MUST represent a completed Asset purchase and MUST
  NOT introduce a purchase-request, approval, pending-purchase, or
  awaiting-delivery workflow.
  *(Sources: `CONTEXT.md`, Procurement; explicit stakeholder instruction,
  2026-08-03.)*
- **FR-002**: Procurement MUST be recorded by IT in current scope. Employee and
  team lead Users MUST NOT initiate Procurement requests or purchase approval
  through B6.
  *(Sources: `CONTEXT.md`, Procurement; explicit stakeholder instruction,
  2026-08-03; B1 FR-009.)*
- **FR-003**: Procurement MUST identify its Vendor through a managed Vendor
  entity rather than free text, and that Vendor identity MUST be reusable by
  Service Record without duplicating the third party.
  *(Sources: `CONTEXT.md`, Vendor;
  `docs/adr/0001-service-record-lifecycle.md`.)*
- **FR-004**: A completed Procurement MUST be able to record Vendor, invoice,
  and PO information associated with the purchase. FR-010 governs purchase and
  invoice dates, FR-017 governs invoice/PO identifiers, and FR-018 governs their
  document files.
  *(Source: `CONTEXT.md`, Procurement.)*
- **FR-005**: Authorized master-data maintainers MUST be able to create, view,
  rename, merge, update, and delete Vendor, Category, Brand, Model, and Purchase
  Mode values, subject to the identity and protected-deletion requirements
  below.
  *(Sources: `ROADMAP.md`, entry B6; explicit stakeholder instruction,
  2026-08-03.)*
- **FR-006**: The system MUST reject deletion of Category, Brand, or Model while
  referenced by an Asset and MUST reject deletion of Purchase Mode or Vendor
  while referenced by the tested Procurement relationship.
  *(Source:
  `backend/assets/tests.py::ProtectedMasterDataTests::test_referenced_master_records_cannot_delete_operational_data`.)*
- **FR-007**: A protected-deletion rejection MUST preserve every affected Asset
  and Procurement and MUST explain that the master record cannot be deleted
  because it is in use.
  *(Sources:
  `backend/assets/tests.py::ProtectedMasterDataTests::test_referenced_master_records_cannot_delete_operational_data`;
  `backend/assets/tests.py::ProtectedMasterDataTests::test_delete_api_returns_conflict_for_referenced_master_records`.)*
- **FR-008**: An unused Vendor, Category, Brand, Model, or Purchase Mode MUST
  remain deletable by an otherwise authorized User.
  *(Source:
  `backend/assets/tests.py::ProtectedMasterDataTests::test_unused_master_records_can_still_be_deleted`.)*
- **FR-009**: Before an Asset can be linked to Procurement, the Asset MUST have
  an arrival record containing its arrival date and Location. Saving
  Procurement MUST require explicit attestation that every linked Asset has
  physically arrived and MUST retain the attesting User and time.
  *(Source: stakeholder clarification, 2026-08-03.)*
- **FR-010**: Procurement MUST contain purchase date and invoice date. Purchase
  date MUST be no later than invoice date or any linked Asset arrival date, and
  purchase date, invoice date, and every linked Asset arrival date MUST be no
  later than the Procurement record date. Invoice date and Asset arrival date
  have no required ordering relative to one another.
  *(Source: stakeholder clarification, 2026-08-03.)*
- **FR-011**: Completed Procurement MUST NOT be hard-deleted. An authorized
  removal action MUST archive the Procurement while retaining its purchase
  details and history, and MUST NOT implicitly attach or detach any Asset.
  *(Source: stakeholder clarification, 2026-08-03.)*
- **FR-012**: Every Asset attachment to or detachment from Procurement MUST
  require a reason and MUST append an immutable history entry containing the
  acting User, event time, reason, and before/after associations.
  *(Source: stakeholder clarification, 2026-08-03.)*
- **FR-013**: Each Procurement MUST have at least one current Asset, and each
  Asset MUST have at most one current Procurement.
  *(Source: stakeholder clarification, 2026-08-03.)*
- **FR-014**: A new Asset MAY exist without Procurement only as a temporary
  `In Storage` record. Until linked, it MUST NOT become `Available` or enter
  Checkout, Transfer, or Service Record activity. A legacy/import Asset MAY
  remain without Procurement only when an exception reason is recorded and the
  record remains visibly flagged as missing Procurement. **Visibly flagged**
  means the exception state is carried on the record itself and presented on
  every surface that lists or displays it, without the reader opening a detail
  view or running a separate report; it is not satisfied by the absence of a
  Procurement reference alone.
  *(Source: stakeholder clarification, 2026-08-03.)*
- **FR-015**: Standalone Procurement, Vendor, Category, Brand, Model, and
  Purchase Mode reads MUST require `asset_view` and a non-Employee User.
  Employee MUST receive no standalone B6 page or record access.
  *(Source: stakeholder clarification, 2026-08-03.)*
- **FR-016**: B6 mutations MUST use these existing permission codes:
  - Procurement create, initial Asset links, initial arrival attestation:
    `asset_create`.
  - Procurement edit, later arrival attestation, Asset attachment, and Asset
    detachment: `asset_edit`.
  - Procurement archive: `asset_delete`.
  - Vendor, Category, Brand, Model, and Purchase Mode create, update, and
    delete: `settings_access`.
  *(Source: stakeholder clarification, 2026-08-03.)*
- **FR-017**: Invoice number MUST be nonblank and unique within its Vendor. PO
  number MAY be absent, but when present it MUST be globally unique. Both
  identifiers MUST be trimmed for storage, compared case-insensitively for
  uniqueness, and presented using the entered display text after trimming.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-018**: Procurement MUST own exactly one current invoice file. When a PO
  number is present, Procurement MUST also own exactly one current PO file; an
  absent PO number creates no PO-file requirement. Each file MUST be stored once
  on Procurement and exposed through every linked Asset without duplication.
  Replacing a current invoice or PO file MUST retain the superseded version.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-019**: Vendor, Category, Brand, and Purchase Mode MUST each use a nonblank
  globally unique normalized name. Model MUST use the combination of its Brand
  and a nonblank normalized name as its identity. Names MUST be trimmed, runs of
  whitespace MUST be collapsed, uniqueness MUST be compared case-insensitively,
  and the entered casing and characters MUST be preserved after whitespace
  normalization. Vendor contact person, phone, and email MAY be absent and MUST
  NOT form part of Vendor identity.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-020**: Every Model MUST belong to exactly one Brand and MUST NOT be
  directly related to Category; Category remains a flat Asset-classification
  master. Direct deletion of a Brand MUST be protected while any Model refers
  to it.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-021**: Renaming a master MUST preserve its stable identity and all
  references. A controlled merge MUST select one surviving identity, atomically
  move every reference from the duplicate to the survivor, make the duplicate
  unavailable for new selection, and retain the source identity and merge
  provenance. A failed rename or merge MUST change no master or reference.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-022**: Legacy Procurement Vendor backfill MUST retain the original
  free-text value as provenance and MUST automatically match it only to one
  unambiguous Vendor under FR-019 normalization. Blank values, "Unknown Vendor",
  ambiguous matches, and duplicate candidates MUST remain visibly flagged and
  unavailable for selection by new Procurement or Service Record activity while
  historical records remain readable. A `settings_access` maintainer MUST be
  able to resolve a flag by mapping or merging it into a canonical Vendor with
  the source text, reviewer, review time, decision, and prior links retained.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-023**: Every successful B6 mutation MUST create an audit entry recording
  actor, event time, action, outcome, affected identity, and before/after values,
  plus the required reason when the action requires one. Rejected authorization,
  normalized identity-conflict, and protected-deletion attempts MUST also create
  an audit entry recording the attempted action and rejection outcome without
  changing B6 data. Other validation failures are not required B6 audit events.
  *(Source: stakeholder clarification, 2026-08-04.)*
- **FR-024**: B6 MUST emit an IT Manager Notification trigger after each
  successful Procurement archive, invoice or PO file replacement, Asset
  detachment, master merge or deletion, and legacy Vendor resolution. Routine
  creates, edits, Asset attachments, and validation failures MUST NOT emit a B6
  Notification trigger. B8 owns Notification storage, delivery, read state,
  access, filtering, and retention.
  *(Source: stakeholder clarification, 2026-08-04.)*

### Authorization and Lifecycle Requirements

- **ALR-001**: Backend authorization MUST remain authoritative for every B6
  read and mutation; frontend route or control visibility MUST NOT substitute
  for the authorization decision.
  *(Source: `.specify/memory/constitution.md`, Principle II.)*
- **ALR-002**: A denied B6 mutation MUST NOT create, alter, delete, link, or
  unlink a Procurement, Vendor, catalog master, or Asset association.
  *(Source: `.specify/memory/constitution.md`, Principle II.)*
- **ALR-003**: Protected master deletion MUST be enforced at the authoritative
  data boundary so bypassing a frontend warning cannot remove a referenced
  master or its operational data.
  *(Sources: `.specify/memory/constitution.md`, Principle II; the automated
  tests cited by FR-006 and FR-007.)*
- **ALR-004**: Recording or changing Procurement or its Asset associations MUST
  NOT itself change Asset status, condition, Custodian, or another lifecycle
  record.
  *(Sources: `ROADMAP.md`, B6 scope boundary; Draft B2 baseline ownership.)*
- **ALR-005**: Arrival-record and attestation validation MUST apply atomically
  to every linked Asset. A failed check MUST leave Procurement, arrival data,
  and Asset associations unchanged.
  *(Source: stakeholder clarification, 2026-08-03.)*
- **ALR-006**: Each attach, detach, and archive action MUST commit its current
  state change and required history as one operation. Any validation or history
  failure MUST leave Procurement and Asset associations unchanged.
  *(Sources: stakeholder clarification, 2026-08-03;
  `.specify/memory/constitution.md`, Principles II and III.)*
- **ALR-007**: A detach or reassignment MUST atomically preserve FR-013 and
  FR-014. It MUST NOT leave a Procurement empty or a non-exempt operational
  Asset without Procurement at any observable point.
  *(Sources: stakeholder clarification, 2026-08-03;
  `.specify/memory/constitution.md`, Principle II.)*
- **ALR-008**: Every frontend B6 route and action control MUST use the same
  permission and Employee exclusion as FR-015 and FR-016. Hidden controls MUST
  NOT substitute for backend enforcement, and stale visibility MUST NOT permit
  the action.
  *(Sources: stakeholder clarification, 2026-08-03;
  `.specify/memory/constitution.md`, Principle II.)*
- **ALR-009**: A successful B6 mutation and its FR-023 audit entry MUST commit as
  one operation. Failure to retain the audit entry MUST leave B6 data unchanged.
  Notification delivery is not part of that transaction; B6 owns only the
  trigger selection in FR-024 and B8 owns delivery behavior.
  *(Sources: stakeholder clarification, 2026-08-04;
  `.specify/memory/constitution.md`, Principles II and III.)*

### Key Entities

- **Procurement**: The completed-purchase record. Accepted meaning includes an
  IT-recorded completed purchase, managed Vendor, invoice/PO information, and
  required purchase and invoice dates governed by FR-010. It remains retained
  when archived and exposes current and historical Asset associations. Its
  identity includes the Vendor-scoped invoice number and optional globally
  unique PO number governed by FR-017, and it owns the purchase documents
  governed by FR-018. Current implementation additionally stores Purchase Mode,
  timestamps, and associated Assets; those remaining exact field rules remain
  unaccepted.
- **Procurement Document**: The Procurement-owned invoice or PO file. One
  current invoice document is required; one current PO document is required
  when a PO number exists. Linked Assets expose the document without owning a
  duplicate, and replacement preserves prior versions.
- **Vendor**: The managed third-party identity shared by Procurement and
  Service Record, identified by its globally unique normalized name. Contact
  person, phone, and email are optional attributes and do not define identity.
  A flagged legacy Vendor remains readable for history but unavailable for new
  selection until resolved under FR-022.
- **Category**: A flat managed Asset-classification value identified by its
  globally unique normalized name. Exact vocabulary and seeded defaults are not
  accepted by this Draft.
- **Brand**: A managed Asset-brand value identified by its globally unique
  normalized name and referenced by Model.
- **Model**: A managed Asset-model value belonging to exactly one Brand and
  identified by its normalized name within that Brand, with no direct Category
  relationship.
- **Purchase Mode**: A managed value describing how a completed purchase was
  made and identified by its globally unique normalized name. Exact allowed
  values are not accepted by this Draft.
- **Master Merge Record**: Retained provenance connecting a duplicate master
  identity to its surviving identity after all references move atomically.
- **Legacy Vendor Review**: The visible disposition of a Vendor derived from
  legacy Procurement text, retaining the source text, flag reason, reviewer,
  review time, decision, prior links, and canonical Vendor when resolved.
- **B6 Audit Event**: The B6-owned business event selection and required content
  for a successful mutation or specified rejected attempt; B8 owns the shared
  AuditLog facility, access, and retention.
- **B6 Notification Trigger**: A B6-owned signal for one of the high-impact
  events in FR-024, addressed to IT Managers; B8 owns shared delivery and state.
- **Asset**: The physical IT item. The current association allows multiple
  Assets per Procurement and at most one Procurement per Asset; FR-013 now
  accepts that cardinality and requires at least one Asset per Procurement.
  Each linked Asset has an arrival record containing arrival date and Location,
  and its association changes are retained under FR-012. A permitted unlinked
  Asset is either temporary `In Storage` staging or a visibly flagged,
  reasoned legacy/import exception under FR-014.
- **Asset Arrival Record**: Evidence that one Asset physically arrived,
  containing the arrival date and Location. Procurement additionally retains
  the User and time of the all-Assets-arrived attestation.
- **Procurement Asset Link History**: The append-only record of each Asset
  attachment and detachment, including actor, time, reason, and before/after
  associations.
- **B6 Reader**: A non-Employee User whose Role grants `asset_view`. Permission
  to mutate B6 data is separately determined by FR-016.

## Success Criteria *(mandatory)*

### Measurable Outcomes

The **review set** used by the criteria below is every Procurement record
existing at the reviewed Evidence Date, or — where that population is too large
to inspect individually — a sample that includes at least one record per Vendor,
per Purchase Mode, and per exception state named in FR-014 and FR-022. The basis
chosen MUST be recorded in the acceptance record so a later reader can tell what
was actually inspected. "Visibly flagged" carries the meaning defined in FR-014
wherever it appears below.

- **SC-001**: In a review set of completed purchases, 100% of accepted examples
  identify a managed Vendor and support invoice and PO information, while 0%
  introduce a Procurement request or approval state.
- **SC-002**: For each of the five B6 master types, 100% of tested deletions
  while referenced are rejected, preserve the Asset and Procurement, and give
  an in-use explanation; 100% of tested unused records remain deletable.
- **SC-003**: In a review containing a Vendor used by both Procurement and a
  Service Record, 100% of those records refer to one managed Vendor identity
  rather than separately typed names.
- **SC-004**: For every unauthorized B6 mutation scenario reviewed, 0
  Procurement, master, or Asset-association records change, regardless of
  whether a frontend control was visible.
- **SC-005**: 100% of B6 behavior lacking stakeholder intent or automated-test
  evidence is labeled implementation-only or unresolved and cites at least one
  repository evidence path.
- **SC-006**: Before this Draft can be accepted, stakeholder review explicitly
  resolves or deliberately carries forward the remaining conflicts listed
  below.
- **SC-007**: In 100% of Procurement save attempts, every linked Asset has an
  arrival date and Location and the record retains the arrival attestation's
  User and time; any missing prerequisite causes zero Procurement or Asset-link
  changes.
- **SC-008**: In 100% of Procurement save attempts, purchase and invoice dates
  are present, purchase is no later than invoice or any linked Asset arrival,
  and no purchase, invoice, or arrival date is later than the Procurement
  record date; an invalid date set causes zero record or link changes.
- **SC-009**: In 100% of completed Asset attachment and detachment actions, one
  immutable history entry retains actor, time, reason, and before/after
  associations. Archiving retains 100% of Procurement data and history and
  causes zero implicit Asset-link changes.
- **SC-010**: 100% of Procurement records retain at least one current Asset and
  0% of Assets have more than one current Procurement. Every new unlinked Asset
  remains `In Storage` and blocked from custody/service until linked; 100% of
  retained legacy/import exceptions show a reason and visible flag.
- **SC-011**: In a complete permission-matrix review, 100% of frontend routes
  and controls match FR-015 and FR-016, 100% of direct unauthorized attempts
  are denied with zero data changes, and Employee receives zero standalone B6
  pages or records.
- **SC-012**: In 100% of Procurement save attempts, invoice number is nonblank
  and unique within Vendor and every supplied PO number is globally unique
  after trimming and case-insensitive comparison; duplicates cause zero record
  or link changes, while entered display text is preserved after trimming.
- **SC-013**: In 100% of completed Procurement records, one current invoice file
  is stored on Procurement; every record with a PO number also has one current
  PO file. Every linked Asset exposes those files without duplicate storage, and
  100% of replacements retain the superseded version.
- **SC-014**: In 100% of master create, rename, and merge checks, normalized
  global or Brand-scoped uniqueness is enforced with zero partial reference
  changes. All successful renames preserve references, and all successful
  merges leave one selectable survivor while retaining source provenance.
- **SC-015**: In 100% of legacy Vendor review cases, source text remains
  traceable; only an unambiguous normalized identity is matched automatically;
  every unresolved blank, unknown, ambiguous, or duplicate candidate is visibly
  flagged, remains readable in history, and is rejected for new selection; and
  every successful resolution retains its reviewer, time, decision, and prior
  links.
- **SC-016**: In a complete B6 event-matrix review, 100% of successful mutations
  and specified rejected attempts produce the required audit entry, 0% of
  audited mutations commit without it, 100% of the FR-024 high-impact events
  emit an IT Manager Notification trigger, and 0% of excluded routine actions
  emit one.

## Assumptions

- This is an AS-BUILT documentation baseline based on the repository evidence
  date 2026-07-29 and inspected from 2026-08-03 through 2026-08-04. It requests
  no behavior change and makes no implementation-only behavior authoritative.
- The explicit stakeholder instruction permits the protected-deletion behavior
  demonstrated by automated tests to be recorded as a baseline requirement.
- `CONTEXT.md` is authoritative for Procurement, Vendor, Asset, and deferred
  employee-request terminology, but it does not define the complete B6 data or
  authorization contract.
- `ROADMAP.md` entry B6 and the explicit stakeholder instruction confirm the
  five managed master types and master CRUD as B6 scope. FR-019 through FR-021
  accept their identity and normalization contract; other current field shapes,
  seed values, and interfaces remain evidence rather than accepted intent.
- The B1 stakeholder-confirmed Role matrix and custom-Role rules remain inputs;
  FR-015 and FR-016 define how those existing codes apply to B6.
- The Draft B2 baseline owns Asset identity and lifecycle and is not
  rewritten by this Draft. B6 resolves its previously open Procurement-link
  boundary through FR-013 and FR-014.
- The Asset arrival record is a B6 Procurement precondition and does not add a
  new Asset status or a pending-delivery workflow to B2.
- Procurement archival is not Asset detachment. Any intended detachment is a
  separate authorized action with the history required by FR-012.
- Legacy/import exception means pre-existing or externally imported Asset data
  whose Procurement cannot be established; it is not an alternative path for
  registering a new purchase.
- Legacy Vendor review under FR-022 is distinct from the unlinked-Asset
  exception under FR-014. It governs migrated supplier identity without
  weakening Procurement linkage or arrival rules.
- B6 owns which domain actions require audit entries and Notifications. B8 owns
  generic AuditLog and Notification storage, delivery, read state, access,
  filtering, and retention; B6 does not redefine those shared facilities.
- "Invoice and PO information" includes the business-identifying data governed
  by FR-010 and FR-017 and the Procurement-owned files governed by FR-018.
  Other Asset-owned files remain outside B6.
- Vendor administration is in scope; Service Record operations and AMC Vendor
  behavior are not.
- Existing current-system evidence records a passing 70-test baseline on
  2026-07-29. The targeted protected-deletion tests could not be re-run in this
  documentation session because the local environment lacks the installed
  `corsheaders` dependency; no application behavior is inferred from that
  environment failure.

## Baseline Evidence and Unresolved Conflicts *(Brownfield Baseline only)*

### Accepted Intent

- Procurement is an IT-recorded completed purchase after an Asset physically
  arrives, includes Vendor and invoice/PO information, and is not a request or
  approval workflow: `CONTEXT.md`, Procurement.
- Physical arrival is enforced by an Asset arrival record containing arrival
  date and Location plus a required Procurement attestation retaining actor and
  time: stakeholder clarification dated 2026-08-03.
- Purchase and invoice dates are required; purchase is no later than invoice or
  any linked Asset arrival, all dates are no later than the Procurement record
  date, and invoice and arrival have no relative ordering requirement:
  stakeholder clarification dated 2026-08-03.
- Completed Procurement is archive-only, and every Asset attachment or
  detachment retains reasoned append-only history with actor, time, and
  before/after associations: stakeholder clarification dated 2026-08-03.
- Procurement has one or more current Assets, an Asset has at most one current
  Procurement, new unlinked Assets are restricted to `In Storage`, and
  reasoned legacy/import exceptions remain visibly flagged: stakeholder
  clarification dated 2026-08-03.
- Non-Employee `asset_view` controls standalone B6 reads; Employee has no B6
  pages; existing create/edit/delete/settings codes map to the corresponding
  B6 actions and must match in frontend and backend: stakeholder clarification
  dated 2026-08-03.
- Invoice number is required and unique within Vendor; PO number is optional
  and globally unique when present; both use trimmed, case-insensitive identity
  with preserved display text: stakeholder clarification dated 2026-08-04.
- One current invoice file is required on Procurement; one current PO file is
  also required when a PO number exists. Linked Assets expose the single stored
  documents, and replacements retain prior versions: stakeholder clarification
  dated 2026-08-04.
- Vendor, Category, Brand, and Purchase Mode have globally unique normalized
  names; Model is unique within its Brand; names use trimmed, collapsed,
  case-insensitive identity with preserved display; Vendor contacts are
  optional; renames preserve references and controlled merges retain
  provenance: stakeholder clarification dated 2026-08-04.
- Legacy Vendor source text remains traceable; only unambiguous matches may be
  automatic; blank, unknown, ambiguous, and duplicate candidates are flagged
  and blocked from new use until a `settings_access` maintainer maps or merges
  them with retained history: stakeholder clarification dated 2026-08-04.
- Every successful B6 mutation and specified authorization, identity-conflict,
  or protected-deletion rejection is audited. Only Procurement archive,
  invoice/PO file replacement, Asset detachment, master merge/deletion, and
  legacy Vendor resolution notify IT Managers; B8 owns shared infrastructure:
  stakeholder clarification dated 2026-08-04.
- Vendor is a first-class managed entity shared by Procurement and Service
  Record for reliable Vendor-grouped reporting: `CONTEXT.md`, Vendor;
  `docs/adr/0001-service-record-lifecycle.md`.
- B6 covers completed Procurement, Vendor, Category, Brand, Model, Purchase
  Mode, master CRUD, protected deletion, invoice/PO information, and Asset
  linking while excluding Asset lifecycle and Service Record operations:
  `ROADMAP.md`, entry B6; explicit stakeholder instruction dated 2026-08-03.
- Employee- and team-lead-initiated Procurement requests and purchase approval
  are excluded: `CONTEXT.md`, Procurement; explicit stakeholder instruction
  dated 2026-08-03; B1 FR-009.
- Asset register and lifecycle behavior remains owned by the Draft B2
  baseline: `specs/001-asset-register-lifecycle-baseline/spec.md`.
- Brownfield evidence, authorization, and acceptance rules:
  `.specify/memory/constitution.md`; `docs/agents/domain.md`.

### Verified Behavior Evidence

- **AS-006, NC-001, FR-006, FR-007, ALR-003** — direct deletion of referenced
  Category, Brand, Model, Purchase Mode, and Vendor is rejected and the Asset
  and Procurement remain:
  `backend/assets/tests.py::ProtectedMasterDataTests::test_referenced_master_records_cannot_delete_operational_data`.
- **AS-007, FR-007, ALR-003** — deletion of each referenced master through the
  supported interface returns the current conflict outcome and stable in-use
  explanation without deleting operational records:
  `backend/assets/tests.py::ProtectedMasterDataTests::test_delete_api_returns_conflict_for_referenced_master_records`.
- **AS-008, NC-002, FR-008** — an unused record of every B6 master type remains
  deletable:
  `backend/assets/tests.py::ProtectedMasterDataTests::test_unused_master_records_can_still_be_deleted`.
- Consolidated evidence classification and the recorded successful 70-test
  baseline run: `docs/research/itams-current-system-baseline.md`.

### Implementation-Only Observations

- Current unique names and Vendor contact fields:
  `backend/catalog/models.py`;
  `backend/catalog/serializers.py`;
  `backend/catalog/migrations/0001_initial.py`;
  `backend/catalog/migrations/0003_vendor.py`.
- Seeded Category values and non-reversible unseed behavior:
  `backend/catalog/migrations/0002_seed_categories.py`.
- Current authenticated reads, `settings_access` writes, ordering, and
  protected-deletion response behavior for catalog masters:
  `backend/catalog/views.py`;
  `backend/catalog/urls.py`;
  `backend/core/mixins.py`.
- Absence of substantive catalog behavior tests beyond the cross-app protected
  deletion tests: `backend/catalog/tests.py`; `backend/assets/tests.py`.
- Current Procurement fields, requiredness, uniqueness, timestamps, Vendor and
  Purchase Mode protection, and nullable Asset association:
  `backend/assets/models.py`;
  `backend/assets/migrations/0001_initial.py`.
- Current Asset create/edit surfaces omit Procurement selection even though
  Asset detail can display the linked Procurement invoice:
  `frontend/src/pages/asset/Create.jsx`;
  `frontend/src/pages/asset/Edit.jsx`;
  `frontend/src/pages/asset/Detail.jsx`.
- Migration from Procurement free-text Vendor to a required managed Vendor,
  including the "Unknown Vendor" fallback:
  `backend/assets/migrations/0002_asset_amc_end_asset_amc_end_reason_asset_amc_start_and_more.py`;
  `backend/assets/migrations/0003_backfill_procurement_vendor.py`;
  `backend/assets/migrations/0004_finalize_procurement_vendor.py`.
- Procurement representations, rejection of Assets linked elsewhere, and
  current attach/detach behavior:
  `backend/assets/serializers.py`.
- Procurement permission mappings, global ordering, generic create/update/delete
  audit entries, and current delete behavior:
  `backend/assets/views.py`.
- Current Procurement list, create, edit, delete confirmation, selected fields,
  at-least-one-Asset frontend validation, and action-control mismatch:
  `frontend/src/pages/procurement/Procurement.jsx`;
  `frontend/src/pages/procurement/Create.jsx`;
  `frontend/src/pages/procurement/Edit.jsx`;
  `frontend/src/pages/procurement/Delete.jsx`;
  `frontend/src/App.jsx`.
- Current Vendor list, contact fields, create/edit/delete surfaces, control
  visibility, and protected-delete error display:
  `frontend/src/pages/vendor/Vendors.jsx`;
  `frontend/src/pages/vendor/Create.jsx`;
  `frontend/src/pages/vendor/Edit.jsx`;
  `frontend/src/pages/vendor/Delete.jsx`.
- Current shared Masters page supports listing, adding, and deleting Category,
  Brand, Model, and Purchase Mode but not editing them:
  `frontend/src/pages/admin/Masters.jsx`.
- Current navigation visibility for Procurement, Vendor, and Masters:
  `frontend/src/components/navbar/Menu.jsx`;
  `frontend/src/components/navbar/ShortMenu.jsx`;
  `frontend/src/App.jsx`.
- Current Asset detail shows a Procurement invoice reference, and the Asset
  document surface separately recognizes Purchase Invoice and PO Document
  types: `frontend/src/pages/asset/Detail.jsx`.
- Absence of a frontend behavioral-test script: `frontend/package.json`.

### Unresolved Conflicts

1. **Concurrent Asset linking**: FR-013 and ALR-007 define accepted cardinality
   and atomic outcomes, but conflict presentation, retry behavior, and stale
   concurrent edits remain unspecified for planning. The current write path
   rejects an Asset already linked elsewhere but has no dedicated concurrency
   test.
   Evidence: `backend/assets/serializers.py`;
   `backend/assets/tests.py`.

   **Disposition — 2026-08-12.** Reviewing this finding against ALR-007 showed it
   to be two different things filed as one, and they are dispositioned
   differently.

   *Carried forward as planning detail* — the operator-facing behavior: how a
   lost link conflict is presented, whether the losing request retries or fails,
   and whether a save from a form opened before another operator's change is
   rejected as stale. None of this is decided by B6, and none of it needs to be
   for the baseline to be accurate about current behavior.

   *Reclassified as an implementation conformance gap, not an open decision* —
   the atomicity itself. ALR-007 already requires that a reassignment
   "atomically preserve FR-013 and FR-014" and "MUST NOT leave a Procurement
   empty… at any observable point." That is an accepted requirement, so the
   correctness question is not undecided; the implementation simply does not meet
   it. `ProcurementSerializer.validate_asset_ids` reads `procurement_id` and
   `create`/`update` then write with an unconditional
   `Asset.objects.filter(...).update(procurement=...)`. Two operators linking the
   same Asset both pass validation and both write, the later write silently wins,
   and a Procurement whose only Asset was taken is left empty — the exact state
   ALR-007 forbids. Neither `select_for_update` nor a uniqueness constraint nor a
   concurrency test exists (`backend/assets/serializers.py`;
   `backend/assets/tests.py`). FR-012's append-only history compounds it: the
   losing Procurement's history records no entry for an association it believes
   it still holds.

   Splitting the finding this way keeps a specified-but-unmet correctness
   requirement out of the same bucket as genuinely undecided interaction design.
   Carrying the whole finding forward would have parked an ALR-007 violation as
   though it were a UX question.

### Implementation Conformance Update

**Date**: 2026-08-12. **Commits**: `538c3a8`, `070c8c2`. Records where the
implementation now conforms to requirements this baseline already states. No
requirement changes; the findings above are preserved as the dated review record.

| Finding | Status | Evidence |
| --- | --- | --- |
| OBS-AS-013 — B6 read authorization | **Partly closed** | The Employee exclusion is now enforced: `ProcurementViewSet` and every catalog master viewset deny own-records scope outright (`backend/core/permissions.py::NotOwnRecordsScope`; `backend/assets/views.py`; `backend/catalog/views.py`), answering 403 rather than an empty list, since C9 puts no B6 surface in front of the Employee Role. Master reads additionally now require a permission at all — previously `MASTER_WRITE` declared no read codes, so any authenticated request was admitted. Tests: `MasterDataAccessTests` (4); `BaselineConformanceTests::test_employee_is_denied_procurement_entirely`, `::test_a_global_reader_still_sees_every_record`. Still open: Procurement delete remains a hard delete rather than the accepted archive-only behavior. |
| OBS-AS-014 — hidden action controls | **Open** | Unchanged. The Procurement list still renders edit and delete controls without checking the matching action permission. The B6 menu section is now hidden from the Employee Role (`frontend/src/components/navbar/Menu.jsx`), but that is menu-level only and is not the per-row control check this finding describes. |

The Concurrent Asset linking finding remains open and unchanged.

**Provenance note**: these changes were written implementation-first and covered
by tests afterwards, not through the red-green loop Principle IV requires.

### Conformance Gap Register (added 2026-08-13)

Writing B6's conformance suite (`backend/assets/tests_b6_conformance.py`) established
that this baseline had **no gap register at all**, while ten accepted requirements are
unimplemented. They were not previously recorded as either conformance gaps or open
decisions; the earlier reviews found them because they read the code for *defects*, and
an absent feature is not a defect. Each row below is an executable `expectedFailure`
test, so the runner reports an unexpected success the moment one is closed.

No requirement changes. These are delivery obligations against requirements this
baseline already states, not new intent, and not questions for a stakeholder.

| # | Requirement | Gap | Test |
| --- | --- | --- | --- |
| U-008 | FR-009 | No arrival record and no attestation exist in the data model. Decision C7 was resolved in favour of system enforcement; it is unimplemented, not partly implemented. | `test_saving_a_procurement_requires_an_arrival_record_and_attestation` |
| U-009 | FR-010 | No date ordering is enforced. A purchase date after the invoice date, or in the future, is accepted. | `test_a_purchase_date_after_the_invoice_date_is_rejected`, `test_a_future_purchase_date_is_rejected` |
| U-010 | FR-011 | Procurement removal is a hard delete. The archive that retains purchase details and history does not exist. Previously noted in passing under OBS-AS-013 ("still open"); now registered in its own right. | `test_removing_a_procurement_archives_it_rather_than_deleting_it` |
| U-011 | FR-012 | Attach and detach carry no reason and append no history entry, so link changes leave no trail of actor, time, or prior association. | `test_detaching_an_asset_records_a_reason_and_a_history_entry` |
| U-012 | FR-013 | The upper bound (at most one Procurement per Asset) holds; the lower bound does not. A Procurement can be emptied of every Asset. | `test_a_procurement_cannot_be_left_without_any_asset` |
| U-013 | FR-017 | `invoice_number` is globally unique rather than unique within Vendor, so two suppliers cannot both issue an invoice numbered "1". `po_number` carries no uniqueness constraint at all. | `test_the_same_invoice_number_is_allowed_for_a_different_vendor`, `test_a_purchase_order_number_is_globally_unique_when_present` |
| U-014 | FR-019 | Master names are plain unique CharFields. No trimming, no whitespace collapsing, and no case-insensitive comparison, so "Acme", "acme", and " Acme " are three distinct masters. | `test_master_names_are_compared_case_insensitively_after_trimming` |
| U-015 | FR-020 | `catalog.Model` has no Brand relation. Model identity is a bare global name rather than the Brand-plus-name pair this requirement defines, and no deletion protection can exist without the link. | `test_a_model_belongs_to_exactly_one_brand` |

U-015 is the structural one: FR-021 (rename and merge) and FR-022 (legacy Vendor
backfill) remain `unverified` rather than registered here because neither can be
specified as a test until the Model–Brand relation exists to rename or merge across.

### OBS-AS-014 Closed — Per-Row Action Controls (2026-08-14)

The Implementation Conformance Update above records OBS-AS-014 as **Open**: "The
Procurement list still renders edit and delete controls without checking the matching
action permission. The B6 menu section is now hidden from the Employee Role, but that is
menu-level only and is not the per-row control check this finding describes."

Closed. `frontend/src/pages/procurement/Procurement.jsx` gates each control on its own
code — edit on `asset_edit`, archive on `asset_delete` — so the two are decided
separately rather than by one "may write anything" test.

This was never a security hole: the backend refused the action either way, and it still
makes the decision. ALR-008's point is different — a control offering an action the
reader cannot take is a broken promise, and an operator learns the refusal by clicking.
The data stays visible to `asset_view`; only the controls are hidden.

It stayed open this long because it could not be *demonstrated*. No frontend test runner
existed, so ALR-008 sat in the traceability map as permanently `unverified`. Six tests
now cover it (`frontend/src/pages/procurement/Procurement.test.jsx`), including the
read-only reader who must still see the purchase, and the archive control being named
for what it now does rather than "delete".

### Conformance Gap Closure (2026-08-13)

All eight rows of the register above (U-008 to U-015) are closed. Each has a passing
test in `backend/assets/tests_b6_conformance.py`; none remains an `expectedFailure`.

| Gap | Closed by |
| --- | --- |
| U-008 FR-009 | `ProcurementArrival` records date, Location, attester, and time; a purchase cannot be saved until every linked Asset has one and the operator has attested. Decision C7 is implemented rather than assumed. |
| U-009 FR-010 | Purchase date must not follow the invoice date, and neither may be in the future. |
| U-010 FR-011 | Removal archives (`archived`, `archived_at`, `archive_reason`). Archived purchases leave the working list but stay readable. |
| U-011 FR-012 | `ProcurementAssetLink` appends an entry per attach and detach carrying reason, actor, time, and the prior association. |
| U-012 FR-013 | The lower bound is enforced: a Procurement cannot be emptied of every Asset. |
| U-013 FR-017 | Invoice uniqueness is scoped to the Vendor; PO number is globally unique when present and unconstrained when absent. |
| U-014 FR-019 | Names are trimmed and internally collapsed on save, and compared case-insensitively. Display casing is preserved. |
| U-015 FR-020 | `Model.brand` exists, PROTECTed, with identity as the Brand-plus-name pair. Migration `catalog.0005` backfills each Model's Brand from the Assets that use it. |

**Not closed, and deliberately so**: the backfill leaves `Model.brand` empty where the
Assets using a Model disagree about its Brand, or where no Asset uses it. Inventing a
Brand on no evidence would be worse than leaving the gap visible - it would put a
manufacturer's name against a product because a migration needed a value. Those rows are
a data-cleanup task for review. FR-021 (rename and merge) and FR-022 (legacy Vendor
backfill) remain unimplemented, and are expressible for the first time now that the
relation they operate on exists.

## Out of Scope *(mandatory)*

### Adjacent Baseline Ownership

- Authentication, Role/permission administration, User data visibility,
  Department, and Location masters: B1.
- Asset identity, status, condition, Custodian, direct lifecycle transitions,
  Asset-owned files, barcode, and Asset deletion: Draft B2. B6 owns only the
  Procurement invoice and PO documents governed by FR-018.
- Checkout/check-in: B3.
- Approval-gated Transfer: B4.
- Service Record open/close behavior, service dates/cost/bill/outcome, and
  custody effects: B5. B6 owns only the shared Vendor master boundary.
- Warranty, AMC contracts, AMC Vendor capture, and expiry actions: B7.
- Generic Notification and AuditLog storage, access, delivery, filtering, and
  retention: B8.
- Dashboard, purchase reports, Vendor reports, and exports: B9.

### Explicitly Deferred Product Behavior

- Employee- or team-lead-initiated Procurement requests.
- Purchase-request review, approval, rejection, budgeting, ordering, delivery
  tracking, and pending Procurement states.
- Employee self-service Checkout and scheduled or periodic physical Asset
  audits.

### Unaccepted Adjacent Possibilities

- Supplier onboarding, contracts, quotations, purchase line items, taxes,
  currencies, payments, receiving inspections, returns to Vendor, and external
  finance/procurement integration are not established as current B6 behavior.

### Delivery Boundary

- This baseline does not modify application code or tests, redesign other
  Procurement or master behavior, create an implementation plan, generate
  tasks or tickets, or authorize implementation work.
