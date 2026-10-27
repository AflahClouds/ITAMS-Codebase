# 06 — Preserve literal text and typed values in Excel exports

**What to build:** An authorized reader opens a workbook whose business text stays text and whose numeric and other typed values retain their meaning.

**Blocked by:** None — independent behavior, execute after prior writer slice.

**Status:** ready-for-agent

**Traceability:** FR-008–009, ALR-001–003; AS-016–018; T017–T019.

- [x] Permanent fail-before regressions reopen actual workbooks, including public delivery.
- [x] =1+1 and strings beginning with +, - and @ remain exact literal text, including headings/company fields.
- [x] Zero, negative numbers, booleans, dates and empty values retain appropriate non-text types; ordering and visible scope remain.
- [x] Focused green checks and a development checkpoint are recorded.

## Comments

- Published under the user's accepted feature-015 full local-sprint authority. Execute as one bounded native builder; preserve unrelated work.


- Evidence 2026-10-27: shared workbook red stored company formula-like text as type f instead of s; public export independently failed same type assertion after correcting the fixture's existing Report title. Green core.tests_exports_standards 5/5 exit0. Explicit text type applies only to string-valued banner/header/data cells; exact =1+1/+x/-x/@x retained without apostrophes. Reopened workbooks preserve zero/-1 numeric, bool, date/datetime and null cells; public row order and permission denial verified. Existing dependencies only; no CSV changes.
