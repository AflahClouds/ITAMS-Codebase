# Invoice Attachment Requirements Checklist: Procurement Purchase Invoice Attachment

**Purpose**: Review the completeness, clarity, consistency, and measurability of
requirements for optional invoice capture, multi-Asset mapping, versioning,
authorization, and failure recovery before implementation planning is approved.
**Created**: 2026-09-22
**Feature**: [spec.md](../spec.md)

**Audience / Timing**: Peer reviewer during pre-implementation Spec Kit review.
**Depth**: Standard release-gate review focused on the highest-risk data and
authorization boundaries.

## Requirement Completeness

- [x] CHK001 Are invoice-upload requirements defined for both Procurement
  creation and later Procurement editing? [Completeness, Spec §FR-001–FR-004]
- [x] CHK002 Is optionality explicitly defined for creation, existing records
  without an invoice, and edits that omit a new file? [Completeness, Spec
  §FR-002, §FR-005]
- [x] CHK003 Are requirements present for one-Asset and multi-Asset Procurement
  records without changing behavior by cardinality? [Coverage, Spec §Edge
  Cases; §FR-007]
- [x] CHK004 Are initial upload, later add, replacement, and no-document-change
  outcomes all documented? [Completeness, Spec §AS-001–AS-006]
- [x] CHK005 Is invoice removal without replacement explicitly included or
  excluded so omission cannot be misread as deletion? [Scope, Spec §Edge Cases;
  §Out of Scope]

## Requirement Clarity

- [x] CHK006 Is "mapped to an Asset" defined as authorized shared exposure
  rather than a copied Asset-owned file? [Clarity, Spec §Domain Alignment]
- [x] CHK007 Is the distinction among no invoice, one current invoice, and
  retained superseded versions unambiguous? [Clarity, Spec §FR-006, §FR-010]
- [x] CHK008 Are file validation limits explicit for extension, naming, size,
  and user-facing rejection? [Clarity, Spec §FR-011]
- [x] CHK009 Is edit-time file omission explicitly defined as preserving the
  existing current document or no-document state? [Clarity, Spec §FR-005]
- [x] CHK010 Is current-version behavior defined under concurrent replacements,
  including the prohibition on divergent Asset views? [Clarity, Spec §Edge
  Cases; §FR-010]

## Requirement Consistency

- [x] CHK011 Do create, edit, and Asset-context requirements consistently keep
  document ownership on Procurement? [Consistency, Spec §FR-001–FR-010]
- [x] CHK012 Are Asset attach/detach mapping rules consistent with existing
  Procurement cardinality and link-history boundaries? [Consistency, Spec
  §FR-008–FR-009, §FR-015]
- [x] CHK013 Does the change specification consistently supersede only Draft
  B6's invoice-file requiredness while retaining its ownership, version, audit,
  and Notification rules? [Consistency, Spec §Specification Lineage; §ALR-004]
- [x] CHK014 Are the `asset_create`, `asset_edit`, and read-visibility rules
  consistent between actor descriptions and authorization requirements?
  [Consistency, Spec §Domain Alignment; §ALR-001–ALR-003]

## Acceptance Criteria Quality

- [x] CHK015 Can optional create be objectively assessed for both file-present
  and file-absent paths? [Measurability, Spec §AS-001–AS-003; §SC-001]
- [x] CHK016 Can single storage across multiple Assets be measured without
  relying on implementation-specific UI details? [Measurability, Spec §SC-002]
- [x] CHK017 Can later add/replacement consistency and stale-version absence be
  objectively assessed across all linked Assets? [Measurability, Spec §SC-003]
- [x] CHK018 Can authorization and atomic rollback outcomes be verified for all
  protected mutation and read paths? [Measurability, Spec §SC-004–SC-005]

## Scenario and Edge-Case Coverage

- [x] CHK019 Are invalid extension, oversize file, storage failure, and
  unauthorized mutation requirements covered with unchanged-state outcomes?
  [Exception Coverage, Spec §AS-003; §FR-011–FR-012; §ALR-001–ALR-002]
- [x] CHK020 Are later Asset attachment and detachment both covered without
  duplicate files or loss of retained history? [Alternate Flow, Spec §AS-008–
  AS-009]
- [x] CHK021 Are unauthorized Asset-context, Procurement-context, and direct-file
  reads all covered without content or metadata disclosure? [Security Coverage,
  Spec §AS-010; §ALR-003]
- [x] CHK022 Are concurrent replacement and partial-failure recovery requirements
  defined strongly enough to preserve one current version? [Recovery Coverage,
  Spec §Edge Cases; §FR-010, §FR-012]

## Dependencies and Scope

- [x] CHK023 Are dependencies on existing Procurement metadata, Asset links,
  document policy, AuditLog, and Notification facilities explicit? [Dependency,
  Spec §Assumptions]
- [x] CHK024 Are PO documents, OCR, payment, approval, duplicate Asset copies,
  and unrelated lifecycle changes explicitly outside this feature? [Scope, Spec
  §Out of Scope]

## Notes

- All 24 requirement-quality checks passed on 2026-09-22.
- No additional stakeholder question was required: the request decides
  optionality and timing, while Draft B6 supplies already-recorded ownership,
  shared exposure, and version-retention rules.
- Checklist items evaluate the specification, not implementation behavior.

## Implementation Validation Evidence — 2026-09-23

- [x] VAL001 Optional create succeeds with and without a file and maps one
  Procurement-owned version to multiple Assets.
- [x] VAL002 Edit adds version 1, omission preserves state, and replacement
  retains the old version while selecting exactly one current version.
- [x] VAL003 Five linked Assets expose one shared invoice identity; detaching an
  Asset removes its projection without creating or deleting AssetDocument rows.
- [x] VAL004 Invalid type, oversize input, partial storage failure, audit failure,
  and denied mutation leave no partial new state or orphaned file.
- [x] VAL005 Procurement and Asset downloads require their respective record
  visibility and stream from private storage without a raw media URL.
- [x] VAL006 Migration consistency, focused suites, full backend/frontend suites,
  lint, and production build completed with results recorded in `quickstart.md`.
