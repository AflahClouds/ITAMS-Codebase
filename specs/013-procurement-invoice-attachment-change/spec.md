# Feature Specification: Procurement Purchase Invoice Attachment

**Feature Branch**: `docs/baseline-spec-migration`

**Created**: 2026-09-22

**Status**: Draft

**Input**: User description: "Add the purchase invoice as an optional document
when Procurement is created. A Procurement can contain more than one Asset, and
the uploaded purchase invoice must be mapped to each Asset in that Procurement.
The invoice document is not mandatory at creation and can be added later while
editing Procurement."

## Specification Lineage *(mandatory)*

**Type**: Change

**Roadmap Reference**: `ROADMAP.md`, entry B6 — Procurement, Vendor, and catalog
masters.

**Extends**: `specs/002-procurement-vendor-catalog-baseline/spec.md`.

**Supersedes**: The purchase-invoice-file requiredness in Draft B6's FR-018,
AS-016, NC-010, SC-013, and corresponding accepted-intent text. The B6 rules
for Procurement ownership, single storage, linked-Asset exposure, and retained
replacement versions remain in force.

**Extended by**: `specs/016-asset-procurement-lifecycle/spec.md` removes owned invoice versions/files only under explicit singleton permanent purchase deletion; optional upload and ordinary retained versions remain.

**Reciprocal Links**: Draft B6 records this scoped successor under its
Specification Lineage section.

## Domain Alignment *(mandatory)*

**Canonical Terms**:

- **Procurement** is the completed Asset purchase record defined in
  `CONTEXT.md`; this change does not create a request, approval, ordering, or
  delivery workflow.
- **Asset** is a physical IT item. One Procurement can have one or more linked
  Assets, while each Asset has at most one current Procurement under Draft B6.
- **Purchase invoice** is the Procurement-owned document evidencing the
  completed purchase. It is stored once for the Procurement and exposed through
  each currently linked Asset; the Assets do not own duplicate file copies.
- **Mapped to an Asset** means that an authorized reader can discover and access
  the Procurement's current purchase invoice from that Asset's document
  context while the Asset remains linked to the Procurement.

**Relevant Decisions**:

- No current ADR governs Procurement document storage.
- Draft B6 established Procurement ownership, single storage, linked-Asset
  exposure, and retained replacement versions. The explicit stakeholder
  decision dated 2026-09-22 changes only the invoice file from mandatory to
  optional and requires upload during create or later edit.

**Lifecycle and Actors**:

- An authorized IT User may attach a purchase invoice while creating
  Procurement or later while editing it.
- Omitting the purchase invoice does not block Procurement creation or editing
  and does not change the requiredness of invoice metadata defined by Draft B6.
- Uploading, replacing, or exposing a purchase invoice does not change Asset
  status, condition, Custodian, arrival, Checkout, Transfer, Service Record, or
  Procurement-to-Asset link history.
- Procurement creation and an invoice supplied in the same operation use the
  existing `asset_create` authorization. Adding or replacing the invoice after
  creation uses `asset_edit`. Reading or downloading the invoice follows the
  reader's existing access to the relevant Procurement or linked Asset; a file
  URL alone must not bypass that authorization.
- Successful document mutations are subject to the existing audit and
  replacement-notification rules owned by Draft B6 and the shared B8
  infrastructure.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Optionally Attach Invoice During Creation (Priority: P1)

An authorized IT User creating Procurement can select a purchase invoice file
in the same form, but can also finish creating Procurement without one.

**Why this priority**: It captures the invoice when it is already available
without delaying the completed-purchase record when it is not.

**Independent Test**: Create one Procurement with multiple Assets and an
invoice, then create another without an invoice. Both saves succeed; only the
first Procurement exposes a current invoice through all of its linked Assets.

**Acceptance Scenarios**:

1. **AS-001**: **Given** an authorized IT User is creating Procurement for two
   or more Assets and has a valid purchase invoice file, **When** the User saves
   the completed form with that file, **Then** one current purchase invoice is
   owned by the new Procurement and is mapped to every linked Asset.
2. **AS-002**: **Given** an authorized IT User is creating Procurement and has
   no purchase invoice file, **When** the User saves an otherwise valid form,
   **Then** Procurement is created successfully with no current purchase
   invoice and every selected Asset remains linked.
3. **AS-003**: **Given** an invoice upload in the create operation is invalid or
   cannot be retained, **When** the User submits the form, **Then** neither the
   Procurement, its invoice, nor its Asset links are partially created, and the
   User receives an actionable error.

---

### User Story 2 - Add or Replace Invoice During Editing (Priority: P1)

An authorized IT User can edit an existing Procurement that has no invoice and
add one later, or replace its current invoice when a corrected document is
received.

**Why this priority**: Invoices may arrive after the physical Assets and the
completed-purchase record, so later capture is part of the primary workflow.

**Independent Test**: Edit an existing multi-Asset Procurement with no invoice
to add one, then replace it. The current file changes for the Procurement and
all linked Assets, while the prior version remains retained.

**Acceptance Scenarios**:

1. **AS-004**: **Given** an existing Procurement without an invoice, **When**
   an authorized User uploads a valid purchase invoice while editing it,
   **Then** that invoice becomes the single current invoice and is mapped to all
   currently linked Assets.
2. **AS-005**: **Given** an existing Procurement with a current invoice,
   **When** an authorized User uploads a valid replacement while editing it,
   **Then** the replacement becomes current for the Procurement and all
   currently linked Assets, and the superseded version is retained once.
3. **AS-006**: **Given** an existing Procurement whose other details are being
   edited without selecting a new invoice, **When** the edit is saved, **Then**
   the current invoice remains unchanged, or the Procurement remains without
   an invoice if none existed.

---

### User Story 3 - Access the Invoice Through Linked Assets (Priority: P2)

An authorized reader examining any Asset in a Procurement can discover and
access that Procurement's current purchase invoice without separate duplicate
uploads for each Asset.

**Why this priority**: Asset-level access makes purchase evidence available
where staff investigate an individual physical item while keeping one document
of record.

**Independent Test**: Upload one invoice to a Procurement containing multiple
Assets, access it from each Asset, then attach another Asset and detach one. The
newly attached Asset gains access automatically and the detached Asset no
longer exposes the current invoice through that Procurement.

**Acceptance Scenarios**:

1. **AS-007**: **Given** a Procurement with one current invoice and multiple
   linked Assets, **When** an authorized reader examines each linked Asset,
   **Then** every Asset exposes the same current invoice identity and content,
   backed by one stored Procurement document.
2. **AS-008**: **Given** a Procurement already has a current invoice, **When**
   another Asset is linked to it, **Then** the newly linked Asset exposes that
   invoice without another upload or file copy.
3. **AS-009**: **Given** an Asset is detached from a Procurement, **When** the
   detachment completes, **Then** the Asset no longer exposes the Procurement's
   current invoice through its current document context; retained Procurement,
   document-version, audit, and Asset-link history are unchanged.
4. **AS-010**: **Given** a User cannot view a Procurement or one of its linked
   Assets under the existing visibility rules, **When** the User requests the
   invoice through that record or a direct file address, **Then** access is
   denied without returning document content or metadata.

### Edge Cases

- A Procurement may contain one Asset or many Assets; invoice storage and
  mapping behavior is identical at either cardinality.
- Saving create or edit with no selected invoice is valid and must not be
  interpreted as a request to remove an existing invoice.
- Only one invoice version is current for a Procurement. A later upload is a
  replacement, not an additional current invoice.
- A failed upload or replacement leaves the prior Procurement details, current
  invoice, versions, and Asset mappings unchanged.
- Linking an Asset to a Procurement that has no invoice creates no placeholder
  Asset document.
- Concurrent invoice replacements must not leave multiple versions marked
  current or expose different current files through different linked Assets.
- Invoice document removal without replacement is outside this change; the
  existing retained document remains current unless a valid replacement is
  completed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Procurement create workflow MUST allow an authorized User to
  provide one purchase invoice file in the same submission.
- **FR-002**: A purchase invoice file MUST be optional when Procurement is
  created; omission MUST NOT prevent an otherwise valid Procurement from being
  saved.
- **FR-003**: The Procurement edit workflow MUST allow an authorized User to add
  a purchase invoice to an existing Procurement that has none.
- **FR-004**: The Procurement edit workflow MUST allow an authorized User to
  replace the current purchase invoice with a valid new file.
- **FR-005**: Saving a Procurement edit without selecting a new purchase invoice
  MUST preserve the current invoice unchanged, including the valid state where
  no invoice exists.
- **FR-006**: Procurement MUST own at most one current purchase invoice and MUST
  store each uploaded file version once, irrespective of the number of linked
  Assets.
- **FR-007**: The current purchase invoice MUST be mapped to every Asset
  currently linked to its Procurement without creating per-Asset file copies.
- **FR-008**: When an Asset is later linked to a Procurement, it MUST
  automatically gain the mapping to that Procurement's current invoice, if one
  exists.
- **FR-009**: When an Asset is detached from a Procurement, its current document
  context MUST stop exposing that Procurement's invoice without deleting the
  Procurement document, its versions, or historical link evidence.
- **FR-010**: Replacing the current invoice MUST retain the superseded version
  and MUST make the replacement the same current version for the Procurement
  and all currently linked Assets.
- **FR-011**: Invoice uploads MUST accept only the existing document extension
  allowlist, MUST use safe server-controlled file naming, and MUST reject files
  larger than 25 MB; an invalid file MUST be rejected with an actionable error.
- **FR-012**: Creating Procurement with an invoice and replacing an invoice
  MUST each be atomic with their associated current-version and Asset-mapping
  changes; failure MUST leave no partial Procurement, file version, or mapping.
- **FR-013**: An authorized reader MUST be able to discover and access the
  current purchase invoice from the Procurement and from each currently linked
  Asset, subject to the record's existing visibility rules.
- **FR-014**: The feature MUST NOT create placeholder Asset documents when no
  invoice exists and MUST NOT duplicate an invoice file for each linked Asset.
- **FR-015**: Uploading or replacing an invoice MUST NOT change Asset lifecycle
  state, Procurement-to-Asset cardinality, arrival evidence, or Asset-link
  history except for the explicit link operation that may occur in the same
  authorized Procurement edit.

### Authorization and Lifecycle Requirements

- **ALR-001**: An invoice supplied during Procurement creation MUST require the
  same `asset_create` authorization as the Procurement create operation.
- **ALR-002**: Adding or replacing an invoice on existing Procurement MUST
  require `asset_edit`; a denied request MUST change no Procurement, document,
  version, or mapping state.
- **ALR-003**: Invoice discovery and download MUST enforce the existing
  visibility rule for the Procurement or linked Asset through which it is
  accessed. Direct file access MUST NOT bypass authorization.
- **ALR-004**: Required audit entries and the current invoice replacement
  Notification trigger MUST follow Draft B6 and B8 rules; audit persistence is
  atomic with the successful document mutation, while Notification delivery is
  outside that transaction.

### Key Entities

- **Procurement**: The completed-purchase record that owns zero or one current
  purchase invoice and links one or more Assets.
- **Procurement Invoice Version**: One retained purchase-invoice file version,
  including its stable identity, original file name, version order, uploader,
  and upload time; exactly one retained version is current when any version
  exists.
- **Asset Invoice Mapping**: The derived relationship by which each Asset
  currently linked to Procurement exposes that Procurement's current invoice.
  It is not a duplicate file and ends when the Asset's current Procurement link
  ends.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In acceptance testing, 100% of otherwise valid Procurement create
  attempts succeed both with and without a purchase invoice.
- **SC-002**: For a Procurement containing at least five Assets, one successful
  invoice upload results in all five Assets exposing the same current document
  identity, with exactly one stored file version for that upload.
- **SC-003**: In 100% of tested later-add and replacement cases, all currently
  linked Assets expose the new current invoice immediately after a successful
  save and no Asset exposes a stale current version.
- **SC-004**: In 100% of tested failed create or replacement uploads, there is no
  partial Procurement, file version, current-version switch, or Asset mapping.
- **SC-005**: In 100% of tested authorization cases, unauthorized create,
  edit, discovery, direct-file, and download attempts return no invoice content
  and cause no state change.
- **SC-006**: An authorized IT User can add a missing invoice to an existing
  Procurement in one edit workflow without uploading the file separately for
  each Asset.

## Assumptions

- "Mapped against each Asset" means shared exposure of the single
  Procurement-owned document, not one copied AssetDocument per Asset.
- The latest valid upload becomes the single current invoice and prior versions
  remain retained under the Draft B6 policy.
- Omitting a file during edit means "no document change"; invoice removal
  without replacement is not requested by this feature.
- Existing Procurement identifier, date, arrival, Asset-link, archive, audit,
  and Notification rules remain unchanged except where this specification
  explicitly supersedes invoice-file requiredness.
- Existing configured file validation is reused rather than introducing a new
  invoice-specific file policy.

## Out of Scope *(mandatory)*

- Requiring a purchase invoice before Procurement creation or at a later
  lifecycle milestone.
- Removing the current invoice without a replacement.
- Multiple simultaneously current invoice documents for one Procurement.
- PO document upload behavior, invoice parsing/OCR, line-item extraction,
  payment processing, supplier integration, or approval workflow.
- Duplicating a Procurement invoice into separate physical files owned by each
  linked Asset.
- Changing Procurement-to-Asset cardinality, arrival attestation, Asset status,
  condition, Custodian, Checkout, Transfer, or Service Record rules.
