# 02 — Remove Procurement Before Deleting an Asset

**What to build:** Linked Asset deletion explains that Procurement association
must be removed first. Multi-Asset purchase editing detaches with a reason,
returns the chosen Asset to In Storage and preserves the remaining purchase.

**Blocked by:** 01 — Stage Assets Until Procurement Is Added.
**Status:** ready-for-agent
**Traceability:** US2; FR-003/004/008; ALR-001–005; AS-006–009; T008–T011.

- [ ] Observe failing linked/archived-linked Asset deletion and detachment API/UI cases first.
- [ ] Reject linked deletion without changing Asset/purchase; display actionable guidance.
- [ ] Reasoned removal leaves purchase nonempty; only removed Asset becomes unlinked Storage.
- [ ] Separate unlinked deletion succeeds only when permissions/history safeguards permit.
- [ ] Preserve protected states, custody history, audit/history and applicable notifications.
- [ ] Focused checks pass; record red/green terminal evidence and checkpoint.

## Comments

Execute sequentially after issue 01; ordinary archive behavior stays unchanged.