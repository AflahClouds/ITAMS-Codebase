# 06 — Preserve literal text and typed values in Excel exports

**What to build:** An authorized reader opens a workbook whose business text stays text and whose numeric and other typed values retain their meaning.

**Blocked by:** None — independent behavior, execute after prior writer slice.

**Status:** ready-for-agent

**Traceability:** FR-008–009, ALR-001–003; AS-016–018; T017–T019.

- [ ] Permanent fail-before regressions reopen actual workbooks, including public delivery.
- [ ] =1+1 and strings beginning with +, - and @ remain exact literal text, including headings/company fields.
- [ ] Zero, negative numbers, booleans, dates and empty values retain appropriate non-text types; ordering and visible scope remain.
- [ ] Focused green checks and a development checkpoint are recorded.

## Comments

- Published under the user's accepted feature-015 full local-sprint authority. Execute as one bounded native builder; preserve unrelated work.

