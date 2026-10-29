# 02 — Remove Procurement Before Deleting an Asset

**What to build:** Linked Asset deletion explains that Procurement association
must be removed first. Multi-Asset purchase editing detaches with a reason,
returns the chosen Asset to In Storage and preserves the remaining purchase.

**Blocked by:** 01 — Stage Assets Until Procurement Is Added.
**Status:** ready-for-agent
**Traceability:** US2; FR-003/004/008; ALR-001–005; AS-006–009; T008–T011.

- [X] Observe failing linked/archived-linked Asset deletion and detachment API/UI cases first.
- [X] Reject linked deletion without changing Asset/purchase; display actionable guidance.
- [X] Reasoned removal leaves purchase nonempty; only removed Asset becomes unlinked Storage.
- [X] Separate unlinked deletion succeeds only when permissions/history safeguards permit.
- [X] Preserve protected states, custody history, audit/history and applicable notifications.
- [X] Focused checks pass; record red/green terminal evidence and checkpoint.

## Comments

Execute sequentially after issue 01; ordinary archive behavior stays unchanged.

2026-10-29 evidence: API red 2/2 expected failures (linked DELETE 204, reasonless detach 200), exit1, terminal7902. API green11/11 exit0 terminal50379; existing custody-history coverage retained for final full verification. UI red missing Procurement navigation1 fail/1 skipped exit1 terminal87002; UI green2/2 deletion cases plus2/2 creation/edit form cases, exit0 terminal64738. Reasoned history and surviving Asset/purchase asserted through API. Protected detach and denied edit retain association. Coherent US1 checkpoint900e5d2 pushed; issue02 checkpoint follows.
