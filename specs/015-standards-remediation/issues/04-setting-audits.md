# 04 — Audit every administrative Setting mutation

**What to build:** An Admin can use any supported Setting mutation path with exactly one private audit record and atomic failure handling.

**Blocked by:** None — independent behavior, execute after prior writer slice.

**Status:** ready-for-agent

**Traceability:** FR-005–006, ALR-001–003; AS-011–013; T011–T013.

- [ ] Fail-before tests cover POST/upsert, full update, partial update and deletion.
- [ ] Exactly one audit records actor/action/key without secret Setting values.
- [ ] Injected required-audit failure preserves the previous Setting state; non-Admin mutations remain denied.
- [ ] Focused green checks and a development checkpoint are recorded.

## Comments

- Published under the user's accepted feature-015 full local-sprint authority. Execute as one bounded native builder; preserve unrelated work.

