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

2026-10-29 evidence: API red 2/2 expected failures (linked DELETE 204, reasonless detach 200), exit 1, terminal 7902. API green 11/11 exit 0 terminal 50379; existing custody-history coverage retained for final full verification. UI red missing Procurement navigation1 fail/1 skipped exit 1 terminal 87002; UI green2/2 deletion cases plus2/2 creation/edit form cases, exit 0 terminal 64738. Reasoned history and surviving Asset/purchase asserted through API. Protected detach and denied edit retain association. Coherent US1 checkpoint 900e5d2 pushed; issue 02 checkpoint follows.

Checkpoint 34257e9 was committed/pushed successfully to the authorized development branch. Existing custody-history protections also receive the explicit detach-after-Take-Back regression in the final feature API module.
