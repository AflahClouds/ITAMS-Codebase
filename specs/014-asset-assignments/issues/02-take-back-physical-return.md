# 02 — Take Back a physical return

**What to build:** IT records actual condition and inspection, ending the current Assignment and making the Asset Available even when Damaged or Repair Required.

**Blocked by:** 01 — Assign ongoing custody.

**Status:** ready-for-agent

**Tasks:** T009–T012. **Requirements:** FR-004–006, FR-013, ALR-001–004; AS-005–008/018/022.

- [ ] IT records actual condition and inspection, ending the current Assignment and making the Asset Available even when Damaged or Repair Required.
- [ ] Deterioration remarks follow B3; a Pending Transfer returns “Transfer request is not closed”; stale actions leave state unchanged.
- [ ] Fail-before API/UI tests, focused green exits and a stable local checkpoint are recorded.

## Comments

### Recovery checkpoint (2026-10-07; WIP, issue remains open)

The six pre-upgrade Take Back application edits were recovered intact. This is a recovery checkpoint, not acceptance of T009–T012 or completion of this issue. Focused Django custody tests passed (17), the full Django suite passed (294), focused Assignment UI tests passed (5), and the full frontend suite passed (43). Frontend lint exited 0 with 14 warnings; build exited 0. These green results protect the saved draft. The issue runner must still verify the original fail-before evidence, review the accepted criteria, and record its own completion evidence before checking any task or issue box.
