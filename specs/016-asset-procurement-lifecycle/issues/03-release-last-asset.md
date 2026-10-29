# 03 — Permanently Delete Procurement to Release Its Last Asset

**What to build:** A normal edit cannot empty a purchase. Explicitly confirmed
permanent deletion of a singleton purchase removes owned history/invoices and
returns its retained Asset to unlinked In Storage for separate deletion.

**Blocked by:** 02 — Remove Procurement Before Deleting an Asset.
**Status:** ready-for-agent
**Traceability:** US3; FR-005–008; ALR-001–005; AS-010–013; T012–T015.

- [ ] Observe intended failing API/form cases before production change.
- [ ] Empty edit explains required complete purchase deletion.
- [ ] Explicit permanent deletion requires existing deletion authority and exactly one eligible Asset.
- [ ] Remove purchase/arrival/link/invoice rows and exact committed private files; retain Asset Storage and independent operational audit.
- [ ] Denied, protected, multi-Asset, stale-link and failed-audit cases preserve records/status/files.
- [ ] Ordinary archive still retains purchase/links; Asset deletion remains separate.
- [ ] UI confirmation clearly names permanent purchase/invoice/history loss; cancellation/error never reports success.
- [ ] Focused regressions pass; record red/green terminal evidence and checkpoint.

## Comments

User explicitly selected permanent deletion/history loss and detached Storage.
Do not broaden to multi-Asset destructive deletion or automatic Asset deletion.