# 05 — Validate Procurement invoice delivery

**What to build:** Reconcile the delivered contract and data model, run the
focused and full backend/frontend quality gates, and record end-to-end evidence
for optional creation, later replacement, Asset mapping, authorization, and
failure recovery.

**Blocked by:** 02 — Attach an optional invoice when creating Procurement; 03 —
Add or replace a Procurement invoice during edit; 04 — Expose the Procurement
invoice through linked Assets.

**Status:** ready-for-human

- [x] Migration and API contracts match the implemented behavior.
- [x] Focused and complete Django tests pass.
- [x] Focused and complete frontend tests, lint, and production build pass.
- [x] Quickstart scenarios and the requirements checklist record final evidence.

## Comments

- Published from reviewed validation tasks T019–T022 on 2026-09-23.
- Migration drift: clean. Django: 290/290 full regression tests passed; focused
  invoice suite: 17/17. Frontend: 51/51 serial full-suite tests passed; lint
  has 0 errors and pre-existing warnings; production build passed.
