# 07 — Verify, independently review and converge Standards remediation

**What to build:** All six fixes have permanent regression evidence, integrated checks, a frozen independently reviewed candidate and a coherent repository state.

**Blocked by:** 01, 02, 03, 04, 05, 06.

**Status:** ready-for-agent

**Traceability:** FR-001–009, ALR-001–003, SC-001–005; T020–T022.

- [x] Complete backend and relevant frontend tests/lint/build have recorded terminal counts, flags and exits; no duplicate healthy long-running test is launched.
- [ ] A fresh native read-only reviewer assesses the frozen candidate; the same builder repairs and same reviewer re-reviews findings.
- [ ] Complete before/after HEAD/index/worktree snapshots prove reviewer read-only behavior and unrelated work preservation.
- [x] One repository-wide stale-material/self-description review and justified successor cleanup are complete; implementation tasks are all checked and final checkpoints recorded.
- [x] Automated evidence is distinguished from any unperformed browser/visual/manual checks; no main merge or deployment occurs.

## Comments

- Published under the user's accepted feature-015 full local-sprint authority. Execute as one bounded native builder; preserve unrelated work.
- Preparation evidence: 22 tasks and seven vertical tickets cover all FR-001–009, ALR-001–003 and AS-001–018; the pre-implementation consistency analysis was clean. No application code changed during preparation.
- Tooling repair authorized separately by the user on 2026-10-27: isolated specify-cli 1.0.13 installed under the ignored .clouds-install-source/runtimes directory. Global CLI remains 1.2.0 and loaded AGENTS.md SHA256 remained 158a13c73ee6d3361ef74bf91ca34bb92de497ac54ed43c15776373801cbdd22 before/after installation. Run 4fd2eeff was created by 1.2.0 and rejected by the strict pinned-state reader before any native child dispatch. Its evidence is retained; a compatible run follows the preparation checkpoint with unchanged accepted requirements and authority.


- Final implementation verification (2026-10-27): backend `Env/Scripts/python.exe manage.py test --noinput` retained exactly one session (4447) from launch through terminal exit 0; 375 tests passed in 771.633 seconds, system check reported no issues, isolated test database destroyed. Initial 8–12 minute estimate was exceeded slightly; no duplicate/elapsed-time abort occurred. Existing injected notification-delivery errors were expected test logs, not failures.
- Frontend full suite used `node 'C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js' test -- --maxWorkers=1 --no-file-parallelism --testTimeout=60000`: 15 files / 73 tests passed, exit 0, 108.04 seconds. The same npm CLI `run lint` exited 0 (0 errors, 13 hook warnings); `run build` exited 0 (2,205 modules, bundle-size warning). Known unrelated test fixture warnings remained non-failing. No production database/media mutation, new dependency or model declaration change; migration drift check inapplicable.
- Red/green evidence is retained in issues 01–06. Focused final counts: catalog 10 API tests; direct audit 3; Setting mutations 3; delivered/shared exports 5; master UI 1. Coherent checkpoints: 300aff4 (Brand), 404f1b3 (identity), 01c5cf6 (audit reads), 52f8338 (Settings), 7e03462 (PDF), e68c10e (Excel), each normally pushed to the verified origin development branch.
- Repository-wide stale-material/self-description check: inspected tracked feature diff, current README/spec/domain/agent documents and research/conformance references; removed the six superseded production paths through proven replacements, with no duplicate old execution path remaining. Preserved historical research/spec requirement snapshots and unrelated findings. Updated frontend README and only factual AGENTS project sections from verified source/terminal/connected-remote evidence; governance and constitution were not amended. No root README or verified deployment/fresh-install operation was invented.
- Supported agent-context evidence: coordinator successfully ran the installed updater after planning; the official block already pointed to feature 015, with initial SHA256 158a13c73ee6d3361ef74bf91ca34bb92de497ac54ed43c15776373801cbdd22. Builder's redundant non-elevated invocation skipped because its YAML parser was unavailable and changed no bytes. Reused the actual successful prior update, preserving the official block during factual maintenance. No before/after-implement extension hook is registered.
- Elevated status/diff verification preserved unrelated `.claude/settings.local.json`; apparent sandbox workflow deletions are ACL artifacts and were not staged. Bound spec, plan, requirements checklist and feature metadata were unchanged. `git diff --check` passed before the final evidence checkpoint. Existing connected repository is AflahClouds/ITAMS-Codebase, authenticated owner/push permission verified by coordinator; development-only normal pushes, no main promotion/force/tags/release/deployment.
- Manual browser walkthrough and visual PDF layout inspection were not performed. Automated tests inspect actual compressed PDF text and reopen actual delivered XLSX files; PDF resource access is prevented/asserted, and no extra PDF inspection dependency was introduced.
- T021 remains deliberately pending: this committed implementation candidate is ready for the fresh read-only native reviewer. The root must capture complete before/after HEAD/index/worktree evidence; the same bounded builder repairs any findings and the same reviewer re-reviews. No independent clean-review claim is made here. All code implementation work and required automated verification are complete; only this review-owned gate remains before guide-owned convergence/closeout.
