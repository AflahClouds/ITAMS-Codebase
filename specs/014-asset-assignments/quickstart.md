# Quickstart: Validate Asset Custody

Use the isolated delivery worktree on `codex/014-asset-assignments-delivery`. This is a validation guide for the accepted [specification](spec.md), not an implementation script. Do not use real employee or production Asset data.

## Prerequisites

- Python runtime with the pinned `backend/requirements.txt` installed and a local test database.
- Node runtime with the checked-in `frontend/package-lock.json` dependencies installed.
- Test users with `asset_custody_manage`, `transfer_request`, read-only Asset access, and no custody permission.
- Sample Assets in Available, Assigned, Under Repair and In Storage states; one active and one disabled employee; a verified historical approved Transfer for an old Checkout.

## Automated checks

From `backend/`:

```powershell
python manage.py test assets
python manage.py test
```

From `frontend/`:

```powershell
npm test -- --run
npm run lint
npm run build
```

These commands are derived from the checked-in project. Their success must be recorded from actual terminal exits during delivery; do not infer it from truncated output.

## Observable walkthrough

1. **Ongoing issue**: Assign an Available Asset to an active employee from the expanded Transfer area. Confirm it becomes Assigned, the employee and department appear in Asset details, the issue condition is saved, and no Pending Transfer or temporary Checkout appears.
2. **Temporary loan**: Checkout a different Available Asset temporarily. Confirm it is labeled Temporary with its optional expected return date. Attempt Assign or Transfer to another employee while open; confirm the temporary-custody error and unchanged holder. Check it in and confirm Available/no Custodian.
3. **Approved handoff**: Request Transfer of the ongoing Asset from employee A to B. Confirm A remains Custodian while Pending. Approve as authorized IT; confirm B becomes Custodian, A's Assignment closes and B's opens. A stale Take Back on A's old record must fail.
4. **Pending gate**: Request another Transfer while B holds the Asset. Attempt Take Back; confirm “Transfer request is not closed” and no mutation. Reject the request, then Take Back against B's current Assignment.
5. **Damaged return**: Take Back with the actual condition Damaged and explanatory remarks. Confirm Available with Damaged condition, no Custodian/department, a return inspection, and a closed Assignment. Repeat without remarks after a worse condition and confirm rejection.
6. **Legacy classification**: Classify an old matching open Checkout as Temporary, then another as Ongoing. Confirm no physical return is recorded. For a stale A Checkout and verified A-to-B approved Transfer, first observe the conflict error; then administratively reconcile. Confirm A's Checkout is Superseded, its original dates are intact, return date remains empty, B remains Custodian, and one classified arrangement exists for B. A non-matching or unapproved Transfer must not reconcile.
7. **Service and offboarding**: Open service for an ongoing Assignment; confirm no active custody and no automatic reassignment on service close. Disable a User holding an Asset; confirm this alone does not return it, while IT can Take Back after physical receipt.
8. **Authorization and history**: Attempt protected actions with read-only credentials. Confirm backend denial, no partial state change, and no unavailable action in the UI. Review audit history, notifications to active recipients, Transfer PDF, Asset details and custody lists for accurate holder/type and no fabricated Check-in.

## Completion evidence

Record the exact commands, terminal exit codes, feature test names, any skipped browser paths and the reasons, and the frozen candidate revision reviewed independently. Complete the repository-wide stale-material/self-description check before local closeout. Keep local commits and the durable feature directory; do not push or publish under this authorization.
