# 01 — Assign ongoing custody

**What to build:** IT directly Assigns an Available Asset to an active employee; the Asset and one ongoing Assignment agree.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

**Tasks:** T001–T008. **Requirements:** FR-001–003, FR-013, ALR-001–005; AS-001–004.

- [x] IT directly Assigns an Available Asset to an active employee; the Asset and one ongoing Assignment agree.
- [x] Fail-before API/domain and UI tests prove atomic audit and notification, and rejected invalid/unauthorized/stale actions.
- [x] Focused tests exit green and a stable local checkpoint is recorded.

## Comments

### 2026-09-30 — T001–T008 delivery evidence

- **Fail before:** `manage.py test assets.tests_custody --verbosity 1` exited 1 with 8 new tests failing because `AssetAssignment` and `/assignment/` did not exist (missing model/404). `npm test -- --run src/pages/transfer/Assignments.test.jsx` exited 1 with both UI tests failing because Assign and ongoing history were absent.
- **Model and migration:** `0013_asset_assignment` adds one-open-Assignment uniqueness and Checkout classification/administrative closure fields. A populated pre-migration open Checkout remains Open and becomes Unclassified; a closed historical Checkout becomes Unknown. Issue and return dates are preserved; no physical return is backfilled. New Checkout rows default to Temporary.
- **Custody and API:** `POST /assignment/` re-reads and locks the Asset and target where supported, conditionally claims Available/no-custodian state on SQLite, validates an active target, writes Asset/Assignment/audit atomically, and schedules the active recipient notification after commit. The read-only resolver exposes Ongoing, Temporary, Unclassified, Conflicting or None. Assignment list/retrieve respects Employee record scope, and no generic Assignment edit/delete route exists.
- **UI:** The Transfer area offers Assign through `/transfer/assign` with `asset_custody_manage`, separately from the `transfer_request` route. It uses the active-only User directory and eligible Available Assets, labels ongoing history, and shows custody type and Assignment history on Asset detail.
- **Green exits:** focused Django custody tests 10/10; `manage.py test assets` 180/180; final `manage.py test` 286/286; frontend Vitest 40/40; `npm run lint` exit 0 (14 existing warnings, 0 errors); `npm run build` exit 0; `manage.py check` exit 0; `makemigrations --check --dry-run` exit 0 (`No changes detected`); `git diff --check` exit 0.
- **Checkpoint:** the focused local commit containing this issue, T001–T008, code and tests is the stable checkpoint. No push or remote operation was performed.
