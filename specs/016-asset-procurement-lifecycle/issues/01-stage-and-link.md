# 01 — Stage Assets Until Procurement Is Added

**What to build:** New Assets start In Storage. Valid Procurement association
makes newly attached eligible Assets Available, including batch association and
adding to an existing purchase. Direct edits cannot bypass this rule.

**Blocked by:** None — can start immediately.
**Status:** ready-for-agent
**Traceability:** US1; FR-001/002/008; ALR-001–005; AS-001–005; T001–T007.

- [X] Observe intended failing API/form regressions before production changes.
- [X] Register as Storage, associate as Available; optional invoice remains optional.
- [X] Failed writes/permissions leave purchase/link/status unchanged; metadata-only edits preserve lifecycle state.
- [X] Direct Asset procurement/status edits cannot bypass purchase validation.
- [X] Default-only migration preserves historical records; unrelated lifecycle tests keep meaningful explicit fixtures.
- [X] Focused checks pass; record terminal red/green evidence and ordinary development checkpoint.

## Comments

Published under current-update combined-local-afk authority; granularity is a
routine approved-sprint choice. One bounded native builder; preserve unrelated work.

Implementation evidence (2026-10-29): starting HEAD 2977da1 on the authorized development branch; unrelated native runs, .claude settings and inaccessible managed-workflow files preserved. Requirements checklist 16/16 PASS; no before/after implement hooks. API red: 8 tests, 6 intended failures, exit 1 (9044). API green: 8/8, exit 0 (26520). UI original create behavior red: expected Storage but received Available, 1 failure/1 skipped, exit 1 (14552); replacement creation flow was already observed 2/2 green (15027). New Storage default is AlterField only, no row rewrite. Focused checkpoint follows this coherent group; subsequent regression suite retains these cases. Seams match the approved plan's API, actual form and commit/storage boundaries.
