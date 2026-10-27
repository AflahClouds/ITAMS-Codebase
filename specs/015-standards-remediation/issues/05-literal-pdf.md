# 05 — Preserve literal business text in PDF exports

**What to build:** Authorized report and Transfer PDFs render markup-like names, headings and remarks as literal text while retaining the intended document layout.

**Blocked by:** None — independent behavior, execute after prior writer slice.

**Status:** ready-for-agent

**Traceability:** FR-007, FR-009, ALR-001–003; AS-014–015; T014–T016.

- [x] Permanent fail-before tests generate and inspect actual documents, including the public delivery boundary.
- [x] Company text, headings, cells and Transfer details preserve literal special characters.
- [x] Markup-like user text never loads local/external resources; permissions and data scope remain.
- [x] Focused green content checks and a development checkpoint are recorded.

## Comments

- Published under the user's accepted feature-015 full local-sprint authority. Execute as one bounded native builder; preserve unrelated work.


- Evidence 2026-10-27: PDF red 2 tests failed with3 parse errors and3 resource-fetch/literal failures; isolated every-Transfer-detail test also failed unclosed markup. Green LiteralPdfTests 3/3 exit0. Tests decode actual compressed PDF text streams using stdlib only; public report and Transfer FileResponses contain literal company/name/category/remark text, all Transfer detail positions tested, app signature labels/layout strings retained, ImageReader never invoked, denied exports403. Every shared Paragraph boundary now escapes business text while app-owned bold and line breaks remain. No dependency changes or network/file resource loads; visual/browser walkthrough not performed.
