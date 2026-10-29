# 03 — Permanently Delete Procurement to Release Its Last Asset

**What to build:** A normal edit cannot empty a purchase. Explicitly confirmed
permanent deletion of a singleton purchase removes owned history/invoices and
returns its retained Asset to unlinked In Storage for separate deletion.

**Blocked by:** 02 — Remove Procurement Before Deleting an Asset.
**Status:** ready-for-agent
**Traceability:** US3; FR-005–008; ALR-001–005; AS-010–013; T012–T015.

- [X] Observe intended failing API/form cases before production change.
- [X] Empty edit explains required complete purchase deletion.
- [X] Explicit permanent deletion requires existing deletion authority and exactly one eligible Asset.
- [X] Remove purchase/arrival/link/invoice rows and exact committed private files; retain Asset Storage and independent operational audit.
- [X] Denied, protected, multi-Asset, stale-link and failed-audit cases preserve records/status/files.
- [X] Ordinary archive still retains purchase/links; Asset deletion remains separate.
- [X] UI confirmation clearly names permanent purchase/invoice/history loss; cancellation/error never reports success.
- [X] Focused regressions pass; record red/green terminal evidence and checkpoint.

## Comments

User explicitly selected permanent deletion/history loss and detached Storage.
Do not broaden to multi-Asset destructive deletion or automatic Asset deletion.
2026-10-29 implementation evidence:
- API fail-before: empty edit lacked permanent-deletion guidance and the new route returned 404 (first diagnostic assertion was corrected, then the singleton test failed explicitly 404 versus 204). The audit-failure case could not reach its boundary before the route existed. Original three-case run exited 1; corrected singleton red ran 1 test and exited 1.
- UI fail-before: 78341 exited 1 because the explicit permanent-delete button was absent (1 fail/3 skipped). List-action regression 14937 exited 1 because the singleton permanent-delete control was absent (1 fail/6 skipped).
- Initial complete feature API run 5071 passed 32/32, exit 0, including retained Asset, deleted purchase/owned arrivals/link history/invoice rows, exact private files only after commit, independent AuditLog, denied/multi-Asset/protected states, failed-audit rollback and ordinary archive.
- Additional stale form regression exposed a real old-snapshot write restoring a deleted Procurement FK: 1 test failed with the expected missing rejection and FK integrity failure. Asset updates now re-read/lock and reject a changed Asset. Stale purchase selection and detached custody-history regressions also remain permanent.
- Combined API run 81780 completed 82 tests in 105.926s, exit 1: all 35 lifecycle tests and 29 B6 cases passed; one existing invoice/custody fixture assumed Available from the former model default. That fixture now explicitly declares Available, preserving the custody assertions; the final full suite is the authoritative subsequent check.
- Full serial frontend 35709 passed 16 files/80 tests in 119.17s, exit 0. This includes explicit confirmation/cancellation/error/navigation, role/cardinality controls, four preserved ordinary-archive cases, reasoned detachment and invoice create/edit flows. Frontend lint and build both exited 0; existing hook and bundle warnings remain non-failing.
- Ordinary development checkpoints 900e5d2 (US1) and 34257e9 (US2) were pushed successfully to the exact authorized development ref. Singleton-release checkpoint follows final backend verification.

Post-fixture-isolation focused green: 35 feature lifecycle tests plus the preserved Department-rejection case, 36/36 passed in 51.287s, exit 0 (94627). Final full-suite rerun follows the completed first run's single legacy fixture correction; no application defect required a change.
