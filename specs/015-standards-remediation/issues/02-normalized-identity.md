# 02 — Reject normalized catalog identity conflicts clearly

**What to build:** A maintainer receives a useful and audited name-conflict response, rather than a server error, without losing master identity or references.

**Blocked by:** 01 — Model Brand contract.

**Status:** ready-for-agent

**Traceability:** FR-002–003, ALR-001–003; AS-004–007; T005–T007.

- [x] Fail-before API tests cover all five masters, creates/renames/self-updates and save-time duplicate races.
- [x] Whitespace/case identity rules and Brand-scoped Model identity are enforced without changing display casing.
- [x] Each identity conflict has one durable rejection audit and no partial business mutation.
- [x] Focused green checks, successor-path cleanup and a development checkpoint are recorded.

## Comments

- Published under the user's accepted feature-015 full local-sprint authority. Execute as one bounded native builder; preserve unrelated work.


- Evidence 2026-10-27: catalog identity red run 7 tests produced 11 expected conflict/server errors across five masters and Brand reassignment; isolated exact duplicate returned 400 but audit count 0 != 1. Production implementation normalizes before lookup, excludes self, scopes Model by Brand, retains ordinary field validators, catches only named/exact unique identity constraints and audits after savepoint rollback. Green catalog.tests_standards: 10/10, exit 0, including all-five race rollback, rejected audit failure and unrelated IntegrityError remaining 500. No model/schema changes. US1 checkpoint 300aff4 pushed normally after one review-timeout retry; no active publication process.

