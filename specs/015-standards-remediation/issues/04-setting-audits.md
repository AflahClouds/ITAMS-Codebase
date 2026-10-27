# 04 — Audit every administrative Setting mutation

**What to build:** An Admin can use any supported Setting mutation path with exactly one private audit record and atomic failure handling.

**Blocked by:** None — independent behavior, execute after prior writer slice.

**Status:** ready-for-agent

**Traceability:** FR-005–006, ALR-001–003; AS-011–013; T011–T013.

- [x] Fail-before tests cover POST/upsert, full update, partial update and deletion.
- [x] Exactly one audit records actor/action/key without secret Setting values.
- [x] Injected required-audit failure preserves the previous Setting state; non-Admin mutations remain denied.
- [x] Focused green checks and a development checkpoint are recorded.

## Comments

- Published under the user's accepted feature-015 full local-sprint authority. Execute as one bounded native builder; preserve unrelated work.


- Evidence 2026-10-27: pre-fix tests demonstrated missing PUT/PATCH/DELETE audits and successful mutations despite injected log failure (200/204 instead of500); existing POST/upsert privacy behavior passed. Green core.tests_settings_standards: 3/3, exit0; every create/upsert/PUT/PATCH/DELETE audited exactly once, no old/new secret values, all methods roll back on injected audit failure, non-Admin methods403. Existing request transaction remains the atomic boundary. No schema/dependency changes.
