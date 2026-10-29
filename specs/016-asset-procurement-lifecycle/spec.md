# Feature Specification: Asset Procurement Lifecycle

**Feature Branch**: `codex/016-asset-procurement-lifecycle`

**Created**: 2026-10-29

**Status**: Accepted scope — implemented and independently reviewed locally on
2026-10-29; native run `bfc1a11c` completed after clean re-review of `e63184b`.
Canonical documentation closeout also received clean independent review.
The reported F002 confirmation-intent correction was independently reviewed
clean at `4295a73`; native run `c27104cb` completed on the same date.
Browser/manual acceptance, deployment, and main promotion have not been performed.

**Input**: New Assets must start `In Storage` and become `Available` after
Procurement is added. An Asset linked to Procurement cannot be deleted until
removed from that Procurement. When it is the Procurement's last Asset, removal
must happen by completely deleting the Procurement.

## Clarifications

### Session 2026-10-29 — Specify preparation

- Q: Does deleting the Procurement of the last Asset mean archive-and-detach or
  permanent deletion of the purchase and invoice/history? → A: Permanently
  delete Procurement and its history.
- Q: If an Available Asset is detached but kept in the register, what status
  should it have? → A: Return it to `In Storage`.

These answers resolve the two product questions raised during preparation;
they are not approval of Specify, Clarify, final scope, or a local sprint.

### Session 2026-10-29

- Specify approval: The stakeholder approved the presented draft and entry
  into Clarify on 2026-10-29. This grants no implementation authority.
- Clarify coverage review: No additional questions were needed; the two prior
  answers remain authoritative. Functional scope, domain/data, interaction,
  quality attributes, dependencies, failure handling, constraints, terminology,
  completion signals, and placeholders were checked. No critical ambiguity
  remains within this update; unchanged operational qualities and lifecycle
  protections continue under the existing repository rules.
- The requirements checklist was revalidated: 16/16 before and 16/16 after,
  with no changed checkbox states, regressions, or unchecked items. No Clarify
  hooks are registered. Business scope and acceptance outcomes are unchanged.
- Clarify approval: The stakeholder approved the clarified design and entry
  into the final scope decision on 2026-10-29. No business requirement or
  acceptance outcome changed between the two design-stage approvals.
- Final decision presented: Accept this clarified scope and authorize its full
  local sprint (Plan, quality work, local implementation issues, test-first
  implementation, independent review/repair, verification, convergence, and
  closeout). At that presentation both design-stage approvals were verified;
  final scope and sprint authority had not yet been granted. The subsequent
  affirmative decision is recorded below.
- Authorization identity: Repository `AflahClouds/ITAMS-Codebase`, local root
  `D:/AFLAH V K/ITAMS - Codebase`, development branch
  `codex/016-asset-procurement-lifecycle`, baseline revision
  `bb89e95dbc258d40c6179492a629439289adf88d`, specification at this feature's
  `spec.md`, and checklist at `checklists/requirements.md`. Their exact current
  digests must be revalidated and bound to any subsequent affirmative decision.
- Final scope and sprint decision: On 2026-10-29, after both design-stage
  approvals and presentation of the final specification and full local-sprint
  request, the stakeholder authorized proceeding. Authority is
  `combined-local-afk` for this update on the stated repository/branch/baseline.
  The presented and revalidated specification SHA-256 was
  `af421fdb9cb4024eb3859265970f41c3432678129aaaa5ef3f69d49498675e42`;
  checklist SHA-256 was
  `4cd3a94315a14d2bf094cd2c35f1f3bfecb7f2ebcdafb089c98ae152723115d6`.
  This entry updates authority metadata only; approved requirements and
  acceptance outcomes are unchanged. The sprint includes routine preparation,
  local tickets, implementation, tests, independent review/repair, convergence,
  and closeout. Ordinary checkpoints publish only to
  `origin refs/heads/codex/016-asset-procurement-lifecycle` under existing policy.
  Main promotion, deployment, force-push, tags, billing, and paid/reset capacity
  are excluded. Preserve unrelated existing work and immutable feature history.
- Delivery evidence: All 21 tasks and five local issue acceptance lists are
  complete. The fresh read-only reviewer identified navigation finding F001;
  the same builder repaired it with regressions and the same reviewer returned
  clean. Full HEAD/index/content snapshots verified read-only behavior. See
  `quickstart.md` and issues 04–05 for terminal check results. Current domain and
  frontend documentation are consolidated only after this verified result.
- Guide closeout: The same read-only reviewer independently checked the current
  domain/README/agent-fact consolidation and returned clean; full before/after
  repository fingerprints matched. Requirements remain unchanged, the quality
  checklist is 16/16, and all implementation work is complete. Retain this feature
  and its evidence under the governing per-feature history convention; active
  feature and supported agent-context pointers resolve here. No installer or
  managed-policy update occurred.
- Follow-up conformance repair: The stakeholder reported that both removal
  controls opened the same page. Under FR-008 and the unchanged accepted scope,
  issue 06 and T022–T024 repaired the action-intent routes and confirmations.
  The retained reviewer returned clean at `4295a73`, with unchanged full review
  snapshots; native correction run `c27104cb` completed. All 24 tasks and six
  issue acceptance lists are complete. No purchase, retention, authorization,
  cardinality or status requirement changed.

## Specification Lineage *(mandatory)*

**Type**: Change; retained authoritative feature record after verified delivery
under constitution 1.1.0's per-feature history convention.

**Roadmap Reference**: Standalone update affecting B2 (Asset register and
lifecycle) and B6 (Procurement) in `ROADMAP.md`.

**Extends**:
- `specs/001-asset-register-lifecycle-baseline/spec.md`
- `specs/002-procurement-vendor-catalog-baseline/spec.md`
- `specs/013-procurement-invoice-attachment-change/spec.md`
- `specs/014-asset-assignments/spec.md`

**Supersedes**: The B2 creation choice of `Available` or `In Storage`, the B6
rule that linking never changes Asset status, and B6's archive-only and
never-empty restrictions only for the explicitly confirmed last-Asset
Procurement deletion. B6's ordinary archive behavior remains outside this
exception. The 2026-10-29 stakeholder answers explicitly authorize the proposed
retention exception as design intent; final scope and local implementation
authority were subsequently granted as recorded above.

**Reciprocal Links**: Predecessors 001, 002, 013 and 014 contain non-semantic
successor links to this feature; their requirement content remains unchanged.

## Domain Alignment *(mandatory)*

**Canonical Terms**:
- **Asset** remains the physical IT item defined in `CONTEXT.md`.
- `In Storage` and `Available` are existing Asset statuses, independent of
  condition. No new status is introduced.
- **Procurement** remains the completed purchase record; adding Procurement
  means successfully linking an Asset to that purchase, not uploading its
  optional invoice file.
- **Custodian**, **Checkout**, **Assignment**, **Transfer**, and **Service
  Record** retain their existing meanings and ownership of custody changes.

**Relevant Decisions**:
- `CONTEXT.md` supplies the vocabulary and custody boundaries.
- ADR-0001 continues to govern Service Record custody clearing and deliberate
  reissue; this change does not override it.
- B6 FR-011 currently requires archive-only retention and no implicit
  detachment. The stakeholder explicitly selected permanent purchase and
  invoice/history deletion for the last-Asset case on 2026-10-29.
- Feature 014's custody-history protection remains applicable after an Asset
  is detached; detachment alone is not sufficient to make every Asset deletable.

**Lifecycle and Actors**:
- Authorized Asset creation starts `In Storage`, with no Custodian or
  department. A successful new Procurement association changes an eligible
  `In Storage` Asset to `Available`.
- Removing a procurement association from an eligible `Available` Asset
  returns it to `In Storage`; an Asset already `In Storage` stays there.
- Linking, detaching, or deleting Procurement must not overwrite `Assigned`,
  `Under Repair`, or terminal state, or bypass their existing lifecycle rules.
- Existing permission checks apply: Asset/Procurement creation uses
  `asset_create`, Procurement editing/detachment uses `asset_edit`, and Asset
  deletion or the last-Asset Procurement deletion requires `asset_delete` and
  the existing actor restrictions. Permission to edit is not deletion authority.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Stage an Asset Until Procurement Is Added (Priority: P1)

IT registers an Asset before recording the completed purchase. Its status
clearly distinguishes staged stock from stock ready for use.

**Why this priority**: An unprocured new Asset must not appear ready to issue.

**Independent Test**: Register Asset A, then record valid Procurement P linked
to A, and inspect A after each successful action.

**Acceptance Scenarios**:
1. **AS-001**: **Given** valid new Asset A, **When** creation succeeds,
   **Then** A is `In Storage`, unlinked, with no Custodian or department.
2. **AS-002**: **Given** staged Asset A, **When** valid Procurement P is
   successfully added and linked to A, **Then** A is `Available` and linked to P.
3. **AS-003**: **Given** staged Assets A and B, **When** valid Procurement P
   links both, **Then** both become `Available` and both link to P.
4. **AS-004**: **Given** staged A, **When** Procurement creation or attachment
   fails validation or authorization, **Then** A remains unlinked and
   `In Storage`, and no partial purchase, link, or status change remains.
5. **AS-005**: **Given** a successful purchase without an uploaded invoice
   file, **When** the Asset is linked, **Then** it becomes `Available`; adding
   an invoice file later does not trigger another status change.

---

### User Story 2 - Remove the Purchase Link Before Asset Deletion (Priority: P1)

An authorized operator attempting to delete a purchased Asset is told to
remove its Procurement association first.

**Why this priority**: Asset deletion must not silently modify purchase contents.

**Independent Test**: Create P linked to A and B, attempt to delete A, detach A
through a valid reasoned Procurement edit, then separately delete eligible A.

**Acceptance Scenarios**:
1. **AS-006**: **Given** A is linked to P, **When** Asset deletion is requested,
   **Then** deletion is rejected, A and P remain unchanged, and the operator is
   told to remove A from Procurement first.
2. **AS-007**: **Given** P contains A and B, **When** authorized IT detaches
   eligible A with a reason, **Then** P retains B, A is unlinked and `In Storage`,
   and the existing reasoned link history records detachment.
3. **AS-008**: **Given** A is detached and has no other deletion restriction,
   **When** authorized IT separately deletes A, **Then** A is deleted and P/B
   remain unchanged.
4. **AS-009**: **Given** a detached Asset with custody history, **When** its
   deletion is attempted, **Then** the existing custody-history protection
   still rejects deletion.

---

### User Story 3 - Delete Procurement to Release Its Last Asset (Priority: P1)

If A is P's only remaining Asset, the operator must completely delete P to
release A instead of saving an empty Procurement.

**Why this priority**: The last-Asset boundary needs an explicit destructive
action with the existing deletion authorization.

**Independent Test**: Create P containing only eligible A, attempt ordinary
detachment, then use the explicit permanent Procurement deletion action and
inspect the retained Asset before separately deleting it.

**Acceptance Scenarios**:
1. **AS-010**: **Given** P contains only A, **When** a normal edit attempts to
   remove A, **Then** the edit fails without mutation and explains that P must
   be completely deleted to release its last Asset.
2. **AS-011**: **Given** P contains only eligible A, **When** an authorized
   operator explicitly permanently deletes P, **Then** P and its owned purchase
   invoice versions and Procurement history are removed, A remains registered
   without P and is `In Storage`, and no empty active Procurement remains.
3. **AS-012**: **Given** A has been released by deleting P, **When** an
   authorized operator separately deletes A, **Then** deletion succeeds only
   if the existing Asset deletion protections also permit it.
4. **AS-013**: **Given** missing deletion permission or a failed last-Asset
   release, **When** deletion is attempted, **Then** P, its history, and A's
   association/status remain unchanged.

### Edge Cases

- A linked Asset is protected even when its Procurement is archived.
- A last-Asset removal must not silently archive Procurement while leaving A
  linked, nor automatically delete A along with Procurement.
- A failed or simultaneous link/detach/delete request must not leave a partial
  status change, a deleted purchase with a dangling Asset link, or an empty
  active Procurement.
- A regular Procurement metadata or invoice-file edit must not reset the
  status of Assets already linked to that Procurement.
- Existing custody, servicing, terminal-state, arrival, reason, and access
  protections apply to affected operations.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every newly created Asset MUST start `In Storage`; the create
  surface MUST not offer `Available` as an alternative initial state (AS-001).
- **FR-002**: A successful new Procurement association of an eligible
  `In Storage` Asset MUST make it `Available`, whether associated during
  Procurement creation or by adding it to an existing Procurement (AS-002–005).
- **FR-003**: Asset deletion MUST be rejected while any current Procurement
  association exists, with an actionable explanation (AS-006).
- **FR-004**: Detaching an eligible Asset while another Asset remains in its
  Procurement MUST remove only the chosen association, return that Asset to
  `In Storage`, and preserve the surviving purchase and Assets (AS-007–008).
- **FR-005**: Normal detachment MUST reject removal of the last Asset and
  explain the required complete Procurement deletion (AS-010).
- **FR-006**: Explicit last-Asset Procurement deletion MUST permanently remove
  that Procurement and its owned invoice versions and Procurement history,
  detach the retained Asset, and return it to `In Storage` (AS-011).
- **FR-007**: Procurement deletion MUST NOT implicitly delete its Asset; Asset
  deletion is a subsequent separately authorized action (AS-011–012).
- **FR-008**: User-facing forms, actions, status displays, and failure messages
  MUST reflect these rules and clearly identify permanent deletion (AS-001–013).

### Authorization and Lifecycle Requirements *(include when applicable)*

- **ALR-001**: Every action MUST enforce existing actor, permission, and
  visibility restrictions. Last-Asset deletion MUST require Procurement
  deletion permission, even when initiated from an edit surface (AS-013).
- **ALR-002**: Each purchase/link/status mutation MUST succeed atomically or
  leave the previous state intact. Conflicting simultaneous operations MUST
  preserve valid purchase cardinality and Asset associations (AS-004, AS-013).
- **ALR-003**: New behavior MUST preserve custody-history Asset deletion
  protection and existing custody, Service Record, and terminal transitions;
  it MUST NOT move protected lifecycle states into `Available` or `In Storage`
  as a side effect of Procurement maintenance (AS-009, AS-013).
- **ALR-004**: Existing operational audit and applicable IT Manager notification
  obligations MUST remain. Permanent deletion removes Procurement-owned
  history under FR-006; it MUST NOT erase the independent operational audit
  evidence recording who performed the destructive action.
- **ALR-005**: Ordinary Asset detachment MUST retain the existing reason and
  append-only association history; the explicitly confirmed last-Asset
  Procurement deletion is the scoped retention exception.

### Key Entities *(include if feature involves data)*

- **Asset**: Physical item with an independent condition, authoritative status,
  at most one current Procurement, and existing custody protections.
- **Procurement**: Completed purchase with one or more current Assets, purchase
  metadata, optional invoice versions, arrival evidence, and association history.
- **Operational audit**: Independently retained evidence of authorized actions;
  distinguish it from Procurement-owned records destroyed under FR-006.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All new-Asset acceptance cases show `In Storage` immediately after
  creation and `Available` only after successful Procurement association.
- **SC-002**: Every tested deletion of a currently linked Asset is rejected
  without changing either the Asset or its Procurement.
- **SC-003**: Both cardinality boundaries pass: removing one of two Assets
  keeps the purchase; releasing the last Asset requires complete Procurement
  deletion and retains the Asset as unlinked `In Storage`.
- **SC-004**: All tested rejected/failed operations preserve previous state,
  and existing custody-history deletion and permission protections still pass.

## Assumptions

- Existing IT Asset and Procurement actors and permissions remain applicable.
- Existing arrival and purchase validation remain prerequisites; adding a
  Procurement does not mean merely uploading the optional invoice document.
- The requested sequence means reject linked-Asset deletion and require the
  operator to remove its association first. It does not authorize automatic
  detachment or automatic purchase deletion from the Asset delete action.
- Historical Asset records are not bulk-reclassified by this update.

## Out of Scope *(mandatory)*

- Changes to ordinary Procurement archiving outside the last-Asset exception.
- Bulk deletion of multi-Asset Procurements or retrospective history cleanup.
- New statuses, permission codes, purchase-request or approval workflows.
- Changes to Checkout, Assignment, Transfer, servicing, Warranty, AMC, exports,
  or their established lifecycle outcomes.
- Deployment, main-branch promotion, and unrelated working-tree changes.
