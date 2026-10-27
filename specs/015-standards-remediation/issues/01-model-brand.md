# 01 — Record a Model with its Brand

**What to build:** A maintainer creates a Model with a selected Brand and sees that Brand retained. Legacy unbranded Models stay readable and can be explicitly corrected without changing their identity or references.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

**Traceability:** FR-001, ALR-001–003; AS-001–003; T001–T004.

- [x] API and maintenance-form fail-before regressions demonstrate the omission before the fix.
- [x] Create/read/update retain the selected Brand; missing/unknown/null Brand is rejected as specified.
- [x] Legacy correction preserves identity and Asset references; existing permissions remain.
- [x] Focused backend/frontend checks pass and red/green terminal evidence plus a development checkpoint are recorded.

## Comments

- Published under the user's accepted feature-015 full local-sprint authority. Execute as one bounded native builder; preserve unrelated work.


- Evidence: branch/HEAD verified as codex/015-standards-remediation at 84f019b; requirements checklist 16/16. API red: catalog.tests_standards 4 tests, missing Brand retention/validation failures; legacy correction independently failed None != Brand after seeded fixture correction. UI red: Masters.test.jsx 1 failed, missing Brand selector. Green: same API 4/4 and UI 1/1, exit 0. Commands use backend Env Python manage.py test catalog.tests_standards --noinput and frontend npm CLI test -- src/pages/admin/Masters.test.jsx --maxWorkers=1 --no-file-parallelism. No schema change; nullable legacy storage retained. Completed 2026-10-27.
