# 01 — Stage Assets Until Procurement Is Added

**What to build:** New Assets start In Storage. Valid Procurement association
makes newly attached eligible Assets Available, including batch association and
adding to an existing purchase. Direct edits cannot bypass this rule.

**Blocked by:** None — can start immediately.
**Status:** ready-for-agent
**Traceability:** US1; FR-001/002/008; ALR-001–005; AS-001–005; T001–T007.

- [ ] Observe intended failing API/form regressions before production changes.
- [ ] Register as Storage, associate as Available; optional invoice remains optional.
- [ ] Failed writes/permissions leave purchase/link/status unchanged; metadata-only edits preserve lifecycle state.
- [ ] Direct Asset procurement/status edits cannot bypass purchase validation.
- [ ] Default-only migration preserves historical records; unrelated lifecycle tests keep meaningful explicit fixtures.
- [ ] Focused checks pass; record terminal red/green evidence and ordinary development checkpoint.

## Comments

Published under current-update combined-local-afk authority; granularity is a
routine approved-sprint choice. One bounded native builder; preserve unrelated work.