# 03 — Audit successful direct Audit Trail reads

**What to build:** An authorized reader can inspect the Audit Trail with one private access record for each successful direct read.

**Blocked by:** None — independent behavior, execute after prior writer slice.

**Status:** ready-for-agent

**Traceability:** FR-004, FR-006, ALR-001–003; AS-008–010; T008–T010.

- [x] Fail-before integration tests cover unfiltered/filtered/empty lists and individual events.
- [x] Each successful read produces one access record without copying the returned payload or recursing.
- [x] Required audit failure exposes no protected content; existing authorization, IP privacy and omission disclosure remain.
- [x] Focused green checks and a development checkpoint are recorded.

## Comments

- Published under the user's accepted feature-015 full local-sprint authority. Execute as one bounded native builder; preserve unrelated work.


- Evidence 2026-10-27: core.tests_standards red included missing list/filter/empty access audits (count1 !=2), broken detail404, and audit-failure disclosure200. Green DirectAuditReadTests 3/3, exit0: exactly-one minimized audit, trusted-peer IP, no copied event contents, denial audit and 1000-row cap/omission. Detail now uses unsliced queryset; list alone limits rows. Required log failure propagates before Response. Setting regression class retained separately in tests_settings_standards.py for its next slice.
