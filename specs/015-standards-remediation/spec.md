# Feature Specification: Standards Remediation

**Feature Branch**: `codex/015-standards-remediation`

**Created**: 2026-10-27

**Status**: Accepted scope — full local sprint authorized on 2026-10-27; planning and delivery in progress.

**Input**: User description: "solve all the standards issues" from the whole-codebase review: Model/Brand handling, normalized master-name conflicts, direct Audit Trail read auditing, administrative Setting mutation auditing, literal PDF text, and literal Excel text.

## Specification Lineage *(mandatory)*

**Type**: Change

**Roadmap Reference**: Standalone remediation of the six Standards findings in the 2026-10-27 review; related capabilities are ROADMAP B6, B8, and B9.

**Extends**:
- `specs/002-procurement-vendor-catalog-baseline/spec.md`, FR-019, FR-020, FR-023: master identity, Brand membership, and conflict accountability.
- `specs/004-notifications-audit-baseline/spec.md`, FR-011, FR-014, FR-015, FR-016: atomic required auditing, access accountability, and privacy.
- `specs/009-dashboard-reports-exports-baseline/spec.md`: report delivery and data preservation, adding explicit literal-text safety for PDF and Excel output.

**Supersedes**: None. Existing master identity, authorization, audit privacy, and business-record visibility remain authoritative.

**Reciprocal Links**: The three predecessor specifications link to this Draft through lineage metadata only. Their requirements and acceptance content are preserved. This is a separate feature from completed feature 014.

## Domain Alignment *(mandatory)*

**Canonical Terms**: Asset, Brand, Model, Vendor, Category, Purchase Mode, Transfer, AuditLog, Audit Trail, Role, permission, and Setting. Custodian and the distinct temporary Checkout and ongoing Assignment retain their CONTEXT.md meanings.

**Relevant Decisions**: CONTEXT.md governs domain language. ADR-0001 governs Service Record lifecycle and Vendor identity; this change introduces no lifecycle or architectural decision. B6's stakeholder-confirmed normalization/Brand rules and B8's stakeholder-confirmed audit rules supply existing intended outcomes. The user's remediation request supplies the bounded requirement to repair the observed PDF and Excel text handling defects.

**Lifecycle and Actors**: A maintainer with `settings_access` manages catalog masters. Existing authorized Audit Trail readers retain their current backend access. Only the current Admin policy admits administrative Setting changes. Existing authorized report readers and Transfer-document readers may export their visible records. No Asset lifecycle transition or Custodian change is introduced.

## Clarifications

### Session 2026-10-27

- The user's “Proceed” after the Specify report approves entry into Clarify for this six-fix scope. It does not supply the separately required final scope acceptance or current-update sprint authority.
- The user's subsequent “Proceed” after the Clarify report approves the clarified design and entry into the final scope decision. Both separate design-stage approvals are now recorded. The six-fix requirements and AS-001–AS-018 are unchanged; final scope acceptance and full local-sprint authority are still pending.
- The user's third “Proceed”, responding to the final six-fix scope and full-local-sprint question, accepts that scope and authorizes Plan through verified local closeout. Authority binds repository `AflahClouds/ITAMS-Codebase`, branch `codex/015-standards-remediation`, baseline revision `067f141c8fb3b07f270d347d8011bcf88ef087bf`, the presented specification SHA256 `610b195f3fb8f8fa8a4c92aab3eab0432f2fb03f8e18ad6559f619c7cbcfda74`, and requirements-checklist SHA256 `ace8fa26bf578ef0fd43ce1fb8fc4ffffbd2377f0cef56aa6f5d025fbbf0b13d`. This entry changes authority/stage metadata only; FR-001–FR-009, ALR-001–ALR-003, AS-001–AS-018, and scope are unchanged. Ordinary development checkpoints and verified development pushes follow repository policy; main promotion, deployment, and release are excluded.
- One structured coverage scan completed with zero questions: no critical ambiguities detected worth formal clarification. Existing predecessor decisions and AS-001–AS-018 already cover the material business outcomes, permissions, privacy, failure handling, preservation, and export examples. No requirement or acceptance scenario changed.
- Requirements-quality checklist revalidation: 16/16 before and 16/16 after; zero newly passing items, regressions, or unchecked items. Its original Notes record the Specify-stage snapshot; this specification records the current stage.
- No before/after-Clarify extension hooks are registered. No plan, tasks, local implementation tickets, application changes, or delivery run was started.

| Coverage category | Result |
| --- | --- |
| Functional scope and behavior | Clear — six defects, actors, outcomes, and exclusions are explicit. |
| Domain and data model | Clear — existing identity and Brand rules apply; legacy rows and references are preserved. No data-volume change is introduced. |
| Interaction and user experience | Clear — Brand selection/display, validation conflicts, protected reads, and export outcomes have observable acceptance examples. |
| Non-functional quality | Clear — required-audit atomicity, value privacy, permission preservation, text safety, and regression evidence are defined. Existing performance/operating limits remain unchanged. |
| Integration and external dependencies | Clear — existing PDF/Excel delivery and application paths are retained; no new external service or dependency is requested. |
| Edge cases and failure handling | Clear — duplicates, self-updates, concurrent identity conflicts, legacy Models, empty audit results, audit failures, and typed export values are covered. |
| Constraints and tradeoffs | Clear — existing stack and repository governance apply; unrelated Spec defects and historical data cleanup are excluded. |
| Terminology and consistency | Clear — CONTEXT.md terms and predecessor requirement meanings are preserved. |
| Completion signals | Clear — permanent fail-before regressions, required checks, and independent clean review are required. |
| Placeholders and unresolved decisions | Clear — no unresolved material decision or placeholder in this bounded scope. |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record a Model with its Brand (Priority: P1)

A catalog maintainer creates a Model under the correct Brand, can see the stored Brand, and can explicitly correct a missing Brand without losing the Model's identity or Asset references.

**Why this priority**: A Model without its Brand cannot meet the existing identity rule.

**Independent Test**: Create, read, and update a Model through the supported maintenance paths, including the master-data form.

**Acceptance Scenarios**:
1. **AS-001**: Given an existing Brand, when an authorized maintainer creates a Model naming that Brand, then the saved and subsequently displayed Model retains that exact Brand.
2. **AS-002**: Given a new Model submission omitting a Brand, clearing its Brand, or naming an unknown Brand, when the save is attempted, then it is rejected clearly without creating or changing a Model.
3. **AS-003**: Given an existing legacy Model with no Brand, when its details are read, then it remains readable; when a maintainer explicitly supplies a valid Brand, then that Brand is retained with the same Model identity and references. No Brand is guessed or historical Model deleted.

---

### User Story 2 - Resolve normalized identity conflicts clearly (Priority: P1)

A maintainer receives a useful validation response when attempting to create or rename a catalog master to an identity that already exists.

**Why this priority**: Normal user input must not trigger a server failure or an unrecorded identity conflict.

**Independent Test**: Attempt normalized duplicate creates and renames for Vendor, Category, Brand, Purchase Mode, and Brand-scoped Model.

**Acceptance Scenarios**:
1. **AS-004**: Given Vendor `Probe Vendor`, when a maintainer submits `probe vendor` or ` Probe   Vendor `, then the submission is rejected as a name conflict, the original remains unchanged, no duplicate appears, and the identity-conflict rejection is audited.
2. **AS-005**: Given a Model named `Latitude` under Brand A, when an equivalent normalized Model name is submitted under Brand A, then it is rejected; the same name under Brand B is permitted.
3. **AS-006**: Given an existing master, when it is saved without changing its normalized identity, then it does not conflict with itself. A successful rename preserves its stable identity and references, while a conflicting rename changes neither.
4. **AS-007**: Given a nonblank unique name with leading, trailing, or repeated internal whitespace, when it is saved, then whitespace is normalized and entered display casing is preserved. Blank normalized names are rejected.

---

### User Story 3 - Account for direct Audit Trail access (Priority: P1)

An authorized reader can view the Audit Trail, and each successful direct read leaves an attributable access record.

**Why this priority**: Reading protected accountability records must itself be accountable.

**Independent Test**: Perform authorized unfiltered, filtered, and individual-event reads, then verify their access records and privacy.

**Acceptance Scenarios**:
1. **AS-008**: Given an authorized reader, when a direct Audit Trail list or filtered list is read successfully, then exactly one attributable access audit entry is retained for that request without copying the returned event contents into the new entry.
2. **AS-009**: Given a readable AuditLog event, when an authorized reader opens that event directly, then the event is returned and exactly one access audit entry is retained. Logging does not recurse or bypass existing access and source-IP protections.
3. **AS-010**: Given required access-audit persistence fails, when protected Audit Trail content is requested, then the request fails without disclosing that content. Existing denied-access auditing remains effective.

---

### User Story 4 - Account for every administrative Setting change (Priority: P1)

An Admin's successful Setting create, upsert, full update, partial update, or deletion leaves an audit record regardless of the supported path used.

**Why this priority**: Configuration changes must not have an unaudited alternate path.

**Independent Test**: Exercise each supported Setting mutation and inject a required audit failure.

**Acceptance Scenarios**:
1. **AS-011**: Given an authorized Admin, when a Setting mutation succeeds through any supported path, then exactly one audit entry identifies the actor, action, time, and affected Setting key without storing a secret Setting value.
2. **AS-012**: Given required audit persistence fails during a Setting change, when the operation completes, then it fails and the prior Setting state is preserved, including for deletion.
3. **AS-013**: Given a caller without administrative authority, when any Setting mutation is attempted, then it remains denied without changing the Setting.

---

### User Story 5 - Export literal business text to PDF (Priority: P2)

A report or Transfer-document reader can export ordinary business text even when it contains characters resembling document formatting instructions.

**Why this priority**: A stored name or remark must neither prevent a document download nor change its interpretation.

**Independent Test**: Export reports and Transfer documents containing representative markup-like values and inspect the resulting document text.

**Acceptance Scenarios**:
1. **AS-014**: Given a name or remark such as `<b>broken`, `A & B`, or `<img src="review-probe.png"/>`, when an authorized PDF is exported, then generation succeeds and the text is displayed literally rather than interpreted as formatting or an image instruction.
2. **AS-015**: Given special characters in company text, report headings, row values, or Transfer details, when a PDF is exported, then user-supplied text remains literal while the established document layout and deliberate formatting remain intact. Such text causes no local-file or external-resource retrieval.

---

### User Story 6 - Export literal business text to Excel (Priority: P2)

A report reader receives the text entered in business records as text rather than spreadsheet instructions.

**Why this priority**: An export must preserve the meaning of its data when opened in a spreadsheet application.

**Independent Test**: Export formula-like text and ordinary typed values, then reopen the delivered workbook and inspect their stored types and values.

**Acceptance Scenarios**:
1. **AS-016**: Given a textual Asset name `=1+1`, when the Excel report is exported and opened, then that cell is literal text `=1+1`, never a formula or calculated result.
2. **AS-017**: Given textual values beginning with `=`, `+`, `-`, or `@`, when exported, then they remain text with their original visible value. User-controlled headings and company text receive the same protection.
3. **AS-018**: Given numeric values, including zero and a negative number, and other already-typed non-text values, when exported, then the protection does not convert those values to strings or change their meaning, row ordering, or authorized record scope.

### Edge Cases

- Normalized conflicts on updates must exclude the current record and leave all references unchanged on rejection.
- A save-time identity conflict caused by another writer must not escape as an unhandled server failure or partially save a master.
- Legacy Models with missing Brands remain readable and can be explicitly corrected; this feature does not invent historical Brand assignments.
- Empty filtered Audit Trail results are still successful protected reads and require one access entry; omission disclosures and IP minimization remain intact.
- An access record must not contain the protected event payload or generate further access records by being written.
- Setting audit entries must not capture credential-like or arbitrary secret values.
- PDF special-character handling applies at every user-text position and must preserve literal text without introducing resource loading.
- Formula-like strings and legitimate negative numeric values must remain distinguishable in Excel.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Supported Model maintenance MUST expose and retain its Brand, require a valid Brand for new Models, reject attempts to clear it, and support explicit Brand correction on an existing Model while preserving identity and references. The master-data form MUST allow Brand selection and show the saved Brand.
- **FR-002**: Vendor, Category, Brand, Purchase Mode, and Model maintenance MUST enforce B6's existing normalization and identity rules on create and update, reject conflicts with a useful validation response instead of an unhandled server failure, and permit self-updates that do not conflict with another identity.
- **FR-003**: Every rejected normalized master-identity conflict MUST retain the required actor, attempted action, affected identity, and rejection outcome in AuditLog without changing business data.
- **FR-004**: Every successful direct Audit Trail list, filtered list, or individual-event read MUST create exactly one attributable access audit entry and MUST fail without exposing protected content if that required entry cannot be retained.
- **FR-005**: Every successful administrative Setting create/upsert, full or partial update, and deletion MUST create exactly one attributable audit entry. The business mutation and its required entry MUST succeed or fail together.
- **FR-006**: Audit entries added by this feature MUST obey existing value minimization, source-IP handling, and retention rules; Setting secrets and returned AuditLog contents MUST NOT be copied into them.
- **FR-007**: PDF report and Transfer-document exports MUST treat every user-controlled text value as literal text, including company text, headings, cells, and Transfer details; markup-like text MUST NOT cause formatting interpretation, resource retrieval, or export failure.
- **FR-008**: Excel report exports MUST store every user-controlled textual value as literal text, including formula-like text, without changing its visible value. Existing numeric and other non-text values MUST retain their types and meaning.
- **FR-009**: Export protections MUST preserve existing authorized record scope, field meaning, ordering, and intended document formatting; this feature introduces no new report calculation or filter behavior.

### Authorization and Lifecycle Requirements

- **ALR-001**: Existing backend permission checks remain authoritative: `settings_access` for catalog master mutations, current audit-read authority for direct Audit Trail reads, Admin policy for Setting mutations, and the existing report/Transfer-document export permissions. This feature MUST introduce no role-name shortcut, privilege grant, or employee self-service.
- **ALR-002**: Invalid, unauthorized, conflicting, or failed operations MUST leave business records and links unchanged. A required mutation-audit failure MUST roll back its business mutation. These changes MUST NOT alter Asset status, condition, Custodian, or custody history.
- **ALR-003**: New audit entries MUST follow B8's mandatory event and privacy contract. This remediation introduces no new Notification trigger and MUST NOT alter existing capability-owned triggers.

### Key Entities

- **Catalog master**: A Vendor, Category, Brand, Purchase Mode, or Brand-scoped Model with a stable identity and normalized display name.
- **AuditLog**: The attributable record of a required mutation, identity-conflict rejection, or protected Audit Trail access.
- **Setting**: An administrative configuration key and value whose changes require accountability and value privacy.
- **Export**: An authorized PDF or Excel representation of existing report or Transfer data; business text remains data.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All six reviewed Standards defects have a permanent regression check showing the previous failure and the corrected observable outcome.
- **SC-002**: In 100% of the Model and normalized-identity acceptance examples, Brand membership, stable references, display casing, conflict outcomes, and required rejection accountability match AS-001 through AS-007.
- **SC-003**: In 100% of successful protected-read and Setting-mutation examples, exactly one required audit entry exists; every tested required-audit failure exposes no protected read or partial business mutation.
- **SC-004**: All representative PDF and Excel text examples in AS-014 through AS-018 retain their literal meaning, while ordinary typed values and authorized data scope remain intact.
- **SC-005**: Independent review finds no unresolved Standards-remediation finding, and the project's required relevant checks have recorded terminal results before delivery is declared complete.

## Assumptions

- This is a bounded repair request for the six Standards findings, using the existing application, permission model, and technology envelope.
- Existing stakeholder-confirmed B6 and B8 rules remain authoritative even where baseline metadata still says Draft; no baseline requirement or acceptance content is rewritten here.
- Existing legacy Model rows are preserved. Any broader historical data reconciliation remains a separate authorized activity.
- The reference behavior and examples above come from the review and its verified reproductions; they do not authorize applying changes to a live database or uploaded media.
- Baseline revision is `067f141c8fb3b07f270d347d8011bcf88ef087bf`. Initial branch was `codex/014-d-local-integration`; feature 015 uses its own development branch. Existing unrelated working-tree changes are preserved.
- Specify and Clarify are complete, both separate design approvals and final scope/local-sprint authority are recorded above. Execution is bounded to the six accepted fixes and existing technology envelope; unrelated work and baseline requirement content remain preserved.
- No active native workflow run was found during preparation. The supported resolver selected the project override specification template. The optional agent-context post-Specify hook is deferred until the required planned-context stage; no applicable AGENTS.md changes are made during this preparation.

## Out of Scope *(mandatory)*

- The nine separate Spec findings, including terminal custody, Procurement association bypasses, recipient eligibility, invalid lifecycle conditions, date shifting, notification destinations, browser CSV auditing, Audit Trail navigation, and terminal-Asset report exclusion.
- The unresolved policy for custom user managers assigning Admin authority or resetting Admin credentials.
- Master merging, broad legacy data cleanup, new report families, report-filter/export parity delivery, CSV workflow changes, or new production dependencies.
- Production data mutation, deployment, release, main-branch promotion, remote-history rewriting, and live constitution or persistence-convention changes.
