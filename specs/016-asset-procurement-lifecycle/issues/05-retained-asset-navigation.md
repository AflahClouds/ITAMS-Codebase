# 05 — Open the Retained Asset After Permanent Procurement Release

**What to build:** Repair independent review finding F001: release success and
its manager notification must use the existing `/asset/detail/:id` route and
open the retained Asset with its refreshed unlinked In Storage state.

**Blocked by:** 04 — Verify the Complete Lifecycle Change and Freeze Delivery.
**Status:** ready-for-agent
**Traceability:** F001; FR-008; ALR-004; AS-011; T014; T019–T021.

- [X] Observe intended failing success-navigation and notification-destination regressions.
- [X] Correct both destinations to the existing Asset detail route without changing release behavior.
- [X] Through the actual App routes, confirm successful release opens the retained Asset and freshly loads In Storage with no Procurement/invoice.
- [X] Verify manager notification points to that same retained Asset detail route.
- [X] Focused backend and full frontend checks, lint/build pass; record evidence/checkpoint and freeze for the same reviewer.

## Comments

Published under the existing accepted sprint authority after fresh read-only
review of candidate 802a425. Same bounded builder assignment, pass 02; no new
requirements or scope change. Canonical docs remain guide-owned after clean
review. Preserve the accepted spec/plan/checklist bytes and unrelated state.

F001 repair evidence (2026-10-29):
- Identity verified at resume: expected HEAD 802a425; original tasks SHA-256 1df737ed4f965b01b26119ba1212a71a1f5553a393e3743c8dd7d9bf7be9ca0f; accepted spec/plan/checklist unchanged. No unrelated writes or role expansion.
- Backend red: the existing successful-release API/private-file/audit journey now reads the actual manager notification through /notification/. One test failed exactly because /asset/1 did not equal /asset/detail/1, exit 1.
- UI red: retained 76915 reached terminal exit 1, 2 intended failures and 8 passes in 20.80s. The corrected destination assertion exposed the old URL; the real App-route journey navigated to an empty main surface, so fresh In Storage Asset detail could not render. No production destination changed before these failures were observed.
- Repair changes only the success and notification destinations. The App route definition, permissions, permanent-release transaction, file lifecycle and audit behavior are unchanged. The new route regression keeps real App routing, permission guards, release form and Asset Detail, mocking only the API/auth boundary and unrelated navbar chrome. A successful release must mount the detail route, fetch the retained Asset afresh and show In Storage, no old Procurement number and no mapped invoice.
- Backend green 70425 reached terminal exit 0: 35/35 focused lifecycle tests passed in 29.538s; system check no issues, isolated database destroyed. This includes the real notification destination and retained Asset state. The prior full 410-test green remains adequate broader evidence because this backend repair changes only a notification URL literal; no schema, transaction or lifecycle logic changed.
- Lint 97035 reached exit 0 (0 errors/13 existing hook warnings). Build 68816 reached exit 0 (2,206 modules in 7.78s; existing chunk-size advisory). Full frontend 92889 is retained to terminal completion; no healthy run is duplicated.

Final F001 verification/freeze:
- Full frontend 92889 reached terminal exit 0: 17 files/82 tests passed in 86.26s, including the real App-route/refreshed Asset detail journey. No browser/manual acceptance is claimed; this is the existing Vitest/jsdom integration seam.
- T019–T021 and all issue 05 acceptance criteria are complete. All 21 feature tasks and all five local issue acceptance lists are checked. The accepted spec/plan/checklist remain byte-stable at 6c0e2a40c1258a3725783c622bf8aa64644b8667fa5654468d193283c31ad1b4, 8310e0f7255cee7294edc489f7ec30260bab7db5de885db42cedc37f990e028b and 608d2563c611f51278cc2fee5cda0066ece87b8276d6ab8e1e36618502b30a1e. No requirement, migration, dependency or canonical-domain amendment.
- Before the repair checkpoint, verify exact branch/HEAD/empty index, origin URL, main ancestry and remote development revision. Stage only F001 application/tests and its local task/issue/evidence files. Commit and automatically attempt the normal push only to refs/heads/codex/016-asset-procurement-lifecycle; actual revision/result is included in the bound native builder completion.
- The checkpoint containing this evidence freezes the repaired candidate for the same reviewer. All retained check processes have reached terminal exits; builder stops writes/tests. Preserve native workflow runs, ignored .claude settings and inaccessible managed-workflow files. Guide-owned canonical consolidation remains pending clean independent re-review.
