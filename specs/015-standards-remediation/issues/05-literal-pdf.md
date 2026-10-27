# 05 — Preserve literal business text in PDF exports

**What to build:** Authorized report and Transfer PDFs render markup-like names, headings and remarks as literal text while retaining the intended document layout.

**Blocked by:** None — independent behavior, execute after prior writer slice.

**Status:** ready-for-agent

**Traceability:** FR-007, FR-009, ALR-001–003; AS-014–015; T014–T016.

- [ ] Permanent fail-before tests generate and inspect actual documents, including the public delivery boundary.
- [ ] Company text, headings, cells and Transfer details preserve literal special characters.
- [ ] Markup-like user text never loads local/external resources; permissions and data scope remain.
- [ ] Focused green content checks and a development checkpoint are recorded.

## Comments

- Published under the user's accepted feature-015 full local-sprint authority. Execute as one bounded native builder; preserve unrelated work.

