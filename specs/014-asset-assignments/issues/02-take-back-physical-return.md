# 02 — Take Back a physical return

**What to build:** IT records actual condition and inspection, ending the current Assignment and making the Asset Available even when Damaged or Repair Required.

**Blocked by:** 01 — Assign ongoing custody.

**Status:** ready-for-agent

**Tasks:** T009–T012. **Requirements:** FR-004–006, FR-013, ALR-001–004; AS-005–008/018/022.

- [x] IT records actual condition and inspection, ending the current Assignment and making the Asset Available even when Damaged or Repair Required.
- [x] Deterioration remarks follow B3; a Pending Transfer returns “Transfer request is not closed”; stale actions leave state unchanged.
- [x] Fail-before API/UI tests, focused green exits and a stable local checkpoint are recorded.

## Comments

### Recovery checkpoint (2026-10-07; WIP, issue remains open)

The six pre-upgrade Take Back application edits were recovered intact. This is a recovery checkpoint, not acceptance of T009–T012 or completion of this issue. Focused Django custody tests passed (17), the full Django suite passed (294), focused Assignment UI tests passed (5), and the full frontend suite passed (43). Frontend lint exited 0 with 14 warnings; build exited 0. These green results protect the saved draft. The issue runner must still verify the original fail-before evidence, review the accepted criteria, and record its own completion evidence before checking any task or issue box.

### Issue 02 delivery checkpoint (2026-10-07)

The retired run records failing test commands after the recovered test edits, but retains no assertion output. To verify the test intent without claiming historical chronology, a temporary detached checkout of the pre-WIP commit `4416d28` was given only the recovered tests. Its Take Back API test failed `404 != 200` (exit 1), and its Assignment UI test file failed on the missing `Take Back AST-004` button (2 expected failures, exit 1). That temporary checkout was removed. In this delivery pass, a new ongoing-history UI test failed because `Assignment #11` and return details were absent from the list (exit 1); the added Assignment identity, return operator/time and inspection remarks made it pass (exit 0). These are reconstructed and current fail-before observations, respectively, not a claim that the recovered tests' original red output was preserved.

The recovered transactional endpoint and UI were checked against physical receipt, B3 remarks with the New-to-Good exception, disabled former holder, Pending Transfer's exact error, stale/repeated requests, permission denial, audit and inspection rollback, and postcommit notification failure. An added inspection-failure integration test confirms the Asset, Assignment, condition log, audit and notification stay unchanged if inspection recording fails. Current checks reached terminal exit 0: focused Django custody 18/18 (31.937s), full Django 295/295 (254.341s), focused Assignment UI 6/6 (10.51s), full frontend 44/44 (20.09s), frontend lint (14 existing warnings) and build. The local commit containing this evidence is the stable issue 02 checkpoint; T009–T012 are the only tasks checked in this pass.
