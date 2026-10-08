# 04 — Transfer an ongoing Assignment

**What to build:** Pending leaves A in custody; approval ends A's exact Assignment and begins B's atomically; rejection leaves custody unchanged.

**Blocked by:** 01 — Assign ongoing custody; 03 — Keep temporary Checkout separate.

**Status:** ready-for-agent

**Tasks:** T017–T020. **Requirements:** FR-001/003/008–009/012–013, ALR-001–003; AS-012–015.

- [x] Pending leaves A in custody; approval ends A's exact Assignment and begins B's atomically; rejection leaves custody unchanged.
- [x] Stale source, temporary/unclassified, same-holder, service/terminal and permission failures do not mutate custody; PDF means actual handoff.
- [x] Fail-before API/UI tests, focused green exits and a stable local checkpoint are recorded.

## Comments

- Local implementation checkpoint: `9871471` (`Implement exact ongoing Assignment transfer handoff`). Transfer requests bind the exact source Assignment; approval changes Asset, closes source, opens target and writes required audit in one transaction. Rejection leaves custody unchanged. Notifications run after commit. The PDF still uses the existing visible Transfer record and labels its Pending/Approved/Rejected status; `asset_view` and party visibility remain intact for all three states.
- Genuine API fail-before: `assets.tests_custody.AssignCustodyTests` exited 1 after 30 tests in 130.701s on 2026-10-07, with 2 failures and 3 errors for missing source identity/target Assignment, stale approval, conflicting custody and audit integration. Five new Transfer API regressions then passed 5/5 in 19.960s. Existing Transfer lifecycle/API compatibility passed 15/15 in 43.370s after old fixtures gained confirmed ongoing source Assignments.
- Genuine UI fail-before: `frontend/src/pages/transfer/Assignments.test.jsx` exited 1 after 8 tests on 2026-10-07 because Available `AST-003` appeared in the new Transfer source list (17:10:24); `Create.jsx` was changed afterward. A later run exited 1 after 9 tests because closed Assignment history lacked `Transferred via TRF-00022` (17:12:07); `Transfers.jsx` was changed afterward. Focused UI passed 9/9 in 18.51s. An earlier proposed Approved-only PDF assertion was discarded before those runs because accepted B4 PDF access includes visible Pending and Rejected records; it is not counted as accepted fail-before evidence.
- Full verification after fixture repair: Django 312/312 passed in 587.964s, terminal exit 0; frontend 51/51 across 9 files passed in 38.14s, exit 0; frontend lint exited 0 with 0 errors and 14 existing warnings; Vite build exited 0. `makemigrations --check --dry-run` and staged `git diff --check` exited 0. The first full Django run exited 1 with seven old baseline fixtures that described Assigned snapshots without Assignment records; exact seven corrected tests passed 7/7 before the final full run. The interrupted earlier full run produced no recoverable terminal exit and is not claimed as verification.
