# 07 — Verify, independently review and converge Standards remediation

**What to build:** All six fixes have permanent regression evidence, integrated checks, a frozen independently reviewed candidate and a coherent repository state.

**Blocked by:** 01, 02, 03, 04, 05, 06.

**Status:** ready-for-agent

**Traceability:** FR-001–009, ALR-001–003, SC-001–005; T020–T022.

- [ ] Complete backend and relevant frontend tests/lint/build have recorded terminal counts, flags and exits; no duplicate healthy long-running test is launched.
- [ ] A fresh native read-only reviewer assesses the frozen candidate; the same builder repairs and same reviewer re-reviews findings.
- [ ] Complete before/after HEAD/index/worktree snapshots prove reviewer read-only behavior and unrelated work preservation.
- [ ] One repository-wide stale-material/self-description review and justified successor cleanup are complete; implementation tasks are all checked and final checkpoints recorded.
- [ ] Automated evidence is distinguished from any unperformed browser/visual/manual checks; no main merge or deployment occurs.

## Comments

- Published under the user's accepted feature-015 full local-sprint authority. Execute as one bounded native builder; preserve unrelated work.
- Preparation evidence: 22 tasks and seven vertical tickets cover all FR-001–009, ALR-001–003 and AS-001–018; the pre-implementation consistency analysis was clean. No application code changed during preparation.
- Tooling repair authorized separately by the user on 2026-10-27: isolated specify-cli 1.0.13 installed under the ignored .clouds-install-source/runtimes directory. Global CLI remains 1.2.0 and loaded AGENTS.md SHA256 remained 158a13c73ee6d3361ef74bf91ca34bb92de497ac54ed43c15776373801cbdd22 before/after installation. Run 4fd2eeff was created by 1.2.0 and rejected by the strict pinned-state reader before any native child dispatch. Its evidence is retained; a compatible run follows the preparation checkpoint with unchanged accepted requirements and authority.

