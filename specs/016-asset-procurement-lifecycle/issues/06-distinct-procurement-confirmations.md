# 06 — Open the Confirmation Matching the Procurement Action

**What to build:** Archive opens only its archive confirmation. The singleton
permanent-delete control, including the last-Asset link in Procurement editing,
opens its own clearly named permanent-deletion confirmation. Neither control
lands on the same generic archive page offering both destructive intents.

**Blocked by:** 05 — Open the Retained Asset After Permanent Procurement Release.
**Status:** ready-for-agent
**Traceability:** F002; FR-008; ALR-001; US3; T022–T024.

- [X] Observe failing regressions through the actual table links and App routes,
  including the edit-form singleton link, before production changes.
- [X] Archive and permanent-deletion entry points have distinct destinations and
  confirmation text/actions matching the clicked intent.
- [X] Archive uses only the existing archive request and retains records/links;
  permanent deletion still requires deliberate confirmation and uses only its
  existing singleton permanent-delete request.
- [X] Preserve permission/cardinality restrictions, retained-Asset navigation,
  cancellation and meaningful server errors; no request occurs merely on entry.
- [X] Full frontend suite, lint/build pass, relevant current references agree,
  evidence is recorded and a stable candidate is committed/pushed for review.

## Comments

The stakeholder reported that the two buttons link to one page after delivery.
Read-only inspection at c2026c0 confirms both table controls and the singleton
edit link point to /procurement/delete/:id. The component presents an archive
heading plus an optional permanent-delete section. This is a presentation defect
inside the same approved feature's explicit-action requirement, not a change to
the accepted business scope. Original feature-016 design/scope/sprint authority
and this direct correction request authorize its bounded repair; no new product
rule, technology, dependency, deployment or main-promotion authority is inferred.

Use the same bounded native builder and reviewer identities recovered from host
inventory. The prior completed run remains historical; a new native correction
run captures the current exact artifacts/revision rather than resuming a completed
run with stale hashes. Preserve spec/plan/checklist requirements, all historical
evidence and unrelated working-tree/native state. Only frontend action-intent
routing, confirmations, regressions and local evidence are in scope. A query
mode or distinct route may share the component internally, provided each user
entry opens only the intended confirmation and invalid eligibility fails closed.

F002 implementation evidence (native correction run c27104cb, 2026-10-29):
- Resume identity verified: HEAD aa71a71159e79c0cd7a9ae2d4355b828ab24d740; tasks SHA-256 bc2b8820906b38960edc25a573cb65d949b53655ad93915e79c0a89bddd43cb7, three unchecked tasks. Accepted spec/plan/checklist remain byte-stable at 197a33203db85a1af07c75eed87e361fd9d7f1512c3e04e0b1a8490914715ba8, 8310e0f7255cee7294edc489f7ec30260bab7db5de885db42cedc37f990e028b and 5e3fe28f291ef9eac028bf5dc63db4726e057888ec8d695aa81d3dab8003f74f. Requirements checklist remains 16/16; no implement hooks are registered. The completed original native run was not resumed or rewritten.
- Fail-before 60633 reached terminal exit 1: three files, five intended failures/ten passes in 153.34s. Actual table/edit permanent links used the archive destination; real App-route permanent entries showed Archive, and the archive entry exposed permanent deletion. No production change preceded the observed failures.
- Archive keeps its existing /procurement/delete/:id destination and displays only the archive confirmation. Table and last-Asset edit permanent entries now use distinct /procurement/permanent-delete/:id and only its explicitly named permanent confirmation. Shared rendering selects an explicit intent; the obsolete two-action/toggle page is removed. Cancel is a button with safe list navigation. No mutation occurs from loading or cancellation.
- Existing asset_delete guards apply to both routes. Direct multi-Asset permanent entry shows the singleton requirement and offers neither destructive action nor an Archive fallback. Confirm handlers also guard permission/loading/cardinality/busy state; backend authority, endpoints, status/cardinality rules, audit and storage behavior are unchanged. Permanent server detail/list errors and the refreshed /asset/detail/:id journey remain covered.
- Focused 33922 reached terminal exit 0: five Procurement files/32 tests passed in 68.70s. The actual App router, guards, table, edit form, confirmations and retained Asset detail are exercised with API/auth/nav-chrome test boundaries. Complete fixture catalog data avoids new test-only warnings.
- Relevant combined current-reference/self-description review inspected all frontend Procurement destinations, App routes, confirmation labels, obsolete confirmPermanent state, existing frontend README, CONTEXT and quickstart references. No current permanent entry points to Archive; the two existing backend methods remain confined to their matching intent. Current canonical prose already describes separate Archive/permanent actions and needs no business amendment. Canonical agent/closeout metadata remains root-owned after clean review; historical evidence is preserved.
- Full frontend 62806, lint 26189 and build 85246 are retained to terminal completion; no healthy run is duplicated. No backend check is rerun for this frontend-only presentation correction. No dependency, schema, backend or domain policy change; no browser/manual acceptance claim.

Final F002 verification and freeze:
- Full frontend 62806 reached terminal exit 0: 17 files/89 tests passed in 161.29s. This includes both actual table-link intents, singleton edit intent, explicit confirmation methods, entry/cancel without mutation, direct multi-Asset and permission guards, server errors, and the preserved refreshed Asset detail route. These are Vitest/jsdom integration checks; no browser/manual acceptance is claimed.
- Lint 26189 reached exit 0 with 0 errors/12 existing warnings. The confirmation's obsolete effect-dependency warning is removed. Build 85246 reached exit 0, 2,206 modules in 14.93s, with the existing chunk-size advisory. No process remains pending and no healthy run was duplicated.
- All T001–T024 and all six issue acceptance lists are checked. No changes were made to backend code, schema, dependency files, accepted spec/plan/checklist, canonical domain requirements, README or AGENTS facts. Required verification is complete for this frontend-only correction; earlier backend evidence remains applicable.
- Reverify exact development branch/HEAD/empty index, origin URL, main ancestry and remote development ref before staging only owned F002 source/test/evidence files. The ordinary checkpoint is pushed only to refs/heads/codex/016-asset-procurement-lifecycle; its actual revision and publication result are included in the bound native builder completion. Main, tags, deployment and force-push are excluded.
- The checkpoint containing this evidence freezes the correction candidate for independent read-only review by the retained reviewer. Builder stops writes/tests. Native run state, .claude settings and inaccessible managed-workflow files remain preserved; root owns subsequent review/convergence and guide-closeout metadata.

Guide completion: checkpoint 4295a73 was pushed to the authorized development
branch. The retained read-only reviewer returned clean; complete pre/post review
fingerprints matched. Native run c27104cb completed. Current completion metadata
records 24 completed tasks and six local issues, without changing accepted
requirements or repeating the completed relevant-reference review. No backend,
dependency, production data, main promotion or deployment change is included.
