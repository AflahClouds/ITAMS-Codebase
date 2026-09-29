# 04 — Transfer an ongoing Assignment

**What to build:** Pending leaves A in custody; approval ends A's exact Assignment and begins B's atomically; rejection leaves custody unchanged.

**Blocked by:** 01 — Assign ongoing custody; 03 — Keep temporary Checkout separate.

**Status:** ready-for-agent

**Tasks:** T017–T020. **Requirements:** FR-001/003/008–009/012–013, ALR-001–003; AS-012–015.

- [ ] Pending leaves A in custody; approval ends A's exact Assignment and begins B's atomically; rejection leaves custody unchanged.
- [ ] Stale source, temporary/unclassified, same-holder, service/terminal and permission failures do not mutate custody; PDF means actual handoff.
- [ ] Fail-before API/UI tests, focused green exits and a stable local checkpoint are recorded.

## Comments
