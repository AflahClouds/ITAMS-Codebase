# Research: Asset Custody Separation

## Existing behavior and evidence

- `backend/assets/checkout.py` issues from Available and closes a Checkout on Check-in; it does not distinguish temporary from ongoing use. The return operation clears Asset Custodian and department.
- `backend/assets/transfer.py` approves a Transfer by changing Asset Custodian but does not close an old open Checkout. This can leave a historical Checkout naming A while the Asset and approved Transfer name B. Current code also accepts a no-Custodian Transfer despite Draft B4's intended restriction.
- `backend/assets/service.py` closes open Checkouts on service opening, clears Custodian and returns the Asset to Available on service closing. ADR-0001 forbids automatic restoration.
- `backend/assets/models.py` has a unique open-Checkout constraint but no cross-record active-custody constraint. SQLite ignores `select_for_update`; write sequencing must be verified at the API seam as well as within the domain service.
- The checked-in stack is Django REST Framework, SQLite for local development, React/Vite, Vitest, and the Django test runner. No new framework or material dependency is required.

## Decision: represent ongoing Assignment separately

**Decision**: Add an ongoing Assignment record and preserve Checkout as the temporary-loan record. One domain custody boundary coordinates Asset, active Checkout/Assignment, Transfer and lifecycle interruptions.

**Rationale**: The product needs distinct actions, return paths, reporting and history. Existing Checkout data and URLs remain readable. The transition boundary can guard one active custody arrangement and prevent old returns from clearing a later holder.

**Alternatives considered**: A single mode flag on Checkout would overload its return and due-date semantics. A new global Asset status for Temporary would multiply status transitions and contradict the accepted independent status/condition model. A full replacement of Checkout/Transfer with one new event ledger would increase migration and UI cost for this change.

## Decision: classify legacy open Checkouts explicitly

**Decision**: Give existing open Checkouts an Unclassified legacy marker in a data migration. New Checkouts are Temporary. IT classifies each legacy open Checkout as Temporary or Ongoing before its next return or Transfer action. The migration itself never guesses purpose or fabricates a return.

**Rationale**: An old open Checkout could represent either an everyday laptop or a short loan. Explicit per-Asset classification preserves the stakeholder's decision and is safe without a production data inventory.

**Alternatives considered**: Automatically treating all old rows as Temporary or Ongoing was rejected by the stakeholder. Bulk conversion would silently change meaning. Requiring all rows to be classified before deployment would create an unnecessary all-or-nothing cutover.

## Decision: administrative reconciliation is distinct from physical return

**Decision**: If approved Transfer history verifies A-to-B custody and the Asset still names B, IT can reconcile A's stale open Checkout as Superseded by that Transfer. Preserve Checkout issue and expected-return dates, leave physical return date/condition empty, retain B as Custodian and classify B's current custody in the same consistent action. If evidence is incomplete, reject reconciliation without mutation.

**Rationale**: The user explicitly requires an administrative correction rather than a false Check-in. Creating B's classified active arrangement in the same operation maintains the single-custody invariant.

**Alternatives considered**: Direct Checkout edit or Check-in of A would fabricate a return and risk clearing B. Automatically trusting any approved Transfer without operator confirmation was rejected during Clarify. Leaving verified cases permanently blocked would make adoption incomplete.

## Decision: close Pending Transfer before Take Back

**Decision**: A Pending Transfer blocks Take Back with the accepted “Transfer request is not closed” error. IT rejects or decides the request first, then acts on the current Custodian's Assignment.

**Rationale**: This is the user's chosen gate. It prevents a stale request from lingering after a return or blocking a future handoff.

**Alternatives considered**: Automatic rejection on Take Back and leaving the request Pending were offered and not selected.

## Decision: preserve durable feature history

**Decision**: Keep `specs/014-asset-assignments/` as the durable change artifact, update `CONTEXT.md` and ADR-0001's narrow reissue wording, and add reciprocal predecessor lineage without rewriting accepted requirements. Do not migrate to `specs/living` or delete this feature directory.

**Rationale**: Constitution 1.1.0 and the installation research govern ITAMS. The installed Clouds guide contains a repository-specific living-spec approval claim inherited from its source, but no ITAMS owner approval or constitution amendment exists. Native delivery steps appear to operate on the active feature and do not require living-spec deletion; guide-owned closeout follows the higher project authority.

**Alternatives considered**: Silent living-spec conversion conflicts with project governance. Ignoring the guide's independent review and native delivery controls would weaken the installed quality gate. Neither is needed for this feature.

## Validation and operational notes

- High-risk inventory and custody transitions require fail-before integration tests at the backend API seam, with direct domain tests for atomicity and stale actions. Add UI tests for flow clarity and existing full-suite/lint/build verification.
- Audit entries for custody changes must commit with the state change. In-app notification failure must not undo a successful action. Existing recipient permissions and disabled-account behavior stay in force.
- No accepted latency or volume target is available. Keep lists paginated, inspect changed query patterns, and avoid blocking other Assets while an old Checkout awaits IT classification.
- The original checkout has unrelated procurement invoice changes. The managed worktree at checkpoint `877ad2a` isolates this delivery. Local commits remain on `codex/014-asset-assignments-delivery`; no remote publication is authorized.
