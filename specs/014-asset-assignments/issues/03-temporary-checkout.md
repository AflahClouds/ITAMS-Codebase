# 03 — Keep temporary Checkout separate

**What to build:** Checkout visibly represents temporary lending with purpose and optional return date; Check-in physically ends it.

**Blocked by:** 01 — Assign ongoing custody.

**Status:** ready-for-agent

**Tasks:** T013–T016. **Requirements:** FR-001/003/007/009/013–014; AS-009–011/019.

- [x] Checkout visibly represents temporary lending with purpose and optional return date; Check-in physically ends it.
- [x] A confirmed temporary holder blocks Assign and Transfer to another employee with an explanatory error and no Pending request.
- [x] Fail-before API/UI tests, focused green exits and a stable local checkpoint are recorded.

## Comments

### Issue 03 delivery checkpoint (2026-10-07)

Before production edits, API integration tests failed for the missing physical Check-in closure reason, a generic Assign error for a confirmed temporary holder, stale Check-in releasing later custody, and Checkout entering a conflicting active Assignment (`4` expected failures, exit 1). A separate Transfer test showed a Pending request was created on temporary custody (`201` instead of `400`, exit 1); Pending approval after temporary Checkout and notification failure also failed as expected (exit 1). The new Checkout UI suite initially failed all three temporary create/list/detail presentation tests (exit 1). A further list regression failed because an interrupted closure appeared as `Returned` with a physical return date (exit 1); it passed after the outcome and physical Check-in columns were corrected. These failures were observed in this issue pass before their corresponding production changes.

New Checkout explicitly records `Temporary` while existing unclassified history remains unclassified. Checkout and Check-in now use the shared current-custody interpretation, conditional Asset/history writes and postcommit notifications; stale or conflicting records cannot release or replace a later holder. A confirmed temporary holder rejects Assign and Transfer to another employee with the Check-in instruction and no Pending request; an already Pending Transfer cannot be approved while temporary custody is current. The UI distinguishes temporary purpose/optional due date and Check-in from ongoing Take Back, and does not label an interrupted closure as a physical return.

Terminal checks: focused Django custody/B3/API compatibility 52/52 OK, exit 0 (reported wall time 5964.257s after a host suspension; the retained process resumed and exited normally); focused Checkout UI 4/4, exit 0; full Django 303/303 OK, exit 0 (322.569s); full frontend 48/48, exit 0 (46.96s); lint exit 0 with the same 14 warnings; build exit 0. The local commit containing this evidence is the stable issue 03 checkpoint. Only T013–T016 are checked in this pass.
