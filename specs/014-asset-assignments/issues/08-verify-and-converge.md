# 08 — Verify and converge local delivery

**What to build:** Full backend/frontend checks have recorded terminal exits, and unverified manual paths are reported accurately.

**Blocked by:** 01–07 — all feature slices.

**Status:** ready-for-agent

**Tasks:** T030–T031. **Requirements:** FR-001–014, ALR-001–005; constitution quality gates.

- [x] Full backend/frontend checks have recorded terminal exits, and unverified manual paths are reported accurately.
- [x] Repository-wide stale-material review is complete while retaining durable feature history; no living-spec migration.
- [ ] Frozen candidate receives independent read-only review; the same builder repairs and the same reviewer re-reviews; commits stay local.

## Comments

- Automated evidence at the frozen issue 07 application checkpoint `ce5bad75025a2a0d09b2a90a8902cea0f3b0253a`: complete Django `manage.py test --noinput` from `backend/` ran 331/331, exit 0 (`itams-014-issue07-full-django-recovered.log`); complete frontend `npm test` ran 57/57 across 9 files, exit 0 (`itams-014-issue07-frontend-test.log`); `npm run lint` exited 0 with 14 warnings and no errors (`itams-014-issue07-frontend-lint.log`); `npm run build` exited 0 (`itams-014-issue07-frontend-build.log`). Issue 07 records focused red/green evidence and the one interrupted unverified test attempt. No application or test source changed after that checkpoint, so the complete suites were not duplicated for this documentation/preset slice. Native issue-delivery regression ran 22/22, exit 0 (`itams-014-issue08-native-regression.log`). Logs are under `C:\Users\aflah.vk\AppData\Local\Temp` and include terminal exit markers.
- Manual paths remain unverified: no live authenticated browser walkthrough, physical device receipt/inspection, production Asset or employee data, or visual review of a downloaded Transfer PDF was performed. API and React integration tests exercise the corresponding modeled flows and access checks, but do not prove those manual observations. No deployment or real-user acceptance was attempted under this local-only authority.
- Repository-wide self-description review: the project-owned preset source and its generated installed guide/implement skills no longer claim issue 02 or the recovered Take Back draft is the next unfinished slice; supported `specify preset update` installed `itams-policy` v1.0.1, and the loaded `AGENTS.md` hash remained unchanged at that install. The generic Vite starter `frontend/README.md` was replaced with verified ITAMS entry points and commands; `AGENTS.md` project facts now report the observed full-suite exits instead of claiming tests were not run. `ROADMAP.md` labels its E/R evidence as a 2026-07-29 brownfield baseline snapshot, so its historical B4/B9 metrics and no-frontend-runner statement are retained rather than rewritten as current feature evidence. Accepted predecessor requirement/acceptance content remains historical; only issue 07's reciprocal lineage was added.
- `.specify/feature.json` still points exactly to `specs/014-asset-assignments`. The supported agent-context updater ran with that feature's plan and preserved the existing managed block. The current feature spec's initial branch/status and domain-decision prose, and the requirements checklist's preplanning notes, are dated initial-stage wording; their bound hashes remain unchanged during native review. Guide-owned post-convergence closeout must correct only currently misleading metadata after independent review, without changing accepted requirements, checklist criteria, or durable history.
- This is the builder's pre-review convergence audit. The independent reviewer has not yet assessed the frozen candidate, may identify further buildable work, and alone can validate the final review-owned criterion. That checkbox remains open until the same builder records actual clean review evidence and the same reviewer re-reviews it.
