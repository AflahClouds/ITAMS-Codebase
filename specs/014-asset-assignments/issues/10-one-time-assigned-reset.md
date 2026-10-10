# 10 — One-time local Assigned asset reset

**What to do:** Apply the current human's 2026-10-10 administrative reset to D's local database only, after independent review of a guarded copy-tested recipe. This is an operational correction, not a new public lifecycle action or change to accepted feature requirements.

**Status:** ready-for-agent

**Delivery state:** Copy-tested candidate frozen for independent read-only review; active database application pending.

**Authorization and binding:** The human requested all Assigned assets be Available, then explicitly approved the concrete administrative reset: clear holders and departments, retain conditions and history, and record no physical returns. Canonical assignment `9a92484f215281af74f813564c1fa41d53687362cc51f3ae90aeb20b20fe4b23`, payload digest `93b8cf1a249543e90123e04534bfd32e7d3ca98aef3e70730facb6320ce4540e`. No push, main promotion, deployment, release, or other database mutation is authorized by this issue.

- [x] Refresh the exact target and dependent custody inventory; preserve a consistent pristine local backup and guard manifest without tracking database or personal data.
- [x] Prepare an atomic, stale-guarded reset and prove success, unchanged condition/history, audit rollback, and stale-data refusal on isolated backup copies.
- [ ] After a clean independent read-only review and full candidate comparison, apply the reviewed recipe once to D's active local database; verify its postconditions and preserve final evidence.

## Preparation evidence

- At preparation/review time, the active local database had exactly five Assigned assets, one Open ongoing Assignment, four Assigned assets without an active arrangement, no Open Checkout, and no Pending Transfer. All five had a holder and department. The binding and ignored guard manifest retain exact IDs, row fingerprints, and original conditions; this tracked issue intentionally contains no holder or other personal data. The active database remained unchanged throughout preparation.
- The consistent SQLite backup and manifest are under ignored `.clouds-install-source/upgrade-backups/2026-10-10/assigned-assets-reset/`, stem `pre-reset-20261010-114027-87a5b69f`. Backup SHA256 `1ed56a8fcd8165581f276abc30ae9ad47031d22cfc01c6095ce4a4a970b9ddbe`; manifest SHA256 `65a67f4f50bed7c92e02c76e60a093852b4ec20263b7e8a75b538e9586629f99`. Snapshot integrity and foreign-key checks passed. The manifest guards every table digest and all five original target rows.
- The ignored recipe `reset_assigned_assets.py` in that directory uses one SQLite immediate transaction. It closes the one Open Assignment with reason `Administrative reset`, preserving its original issue and physical-return fields; makes the five assets Available with no custodian or department while retaining each condition; and appends five audit records attributed to `system-maintenance` with no human user FK and the explicit human-request source. It does not send notifications or create custody/inspection facts for the four orphan records. Its `--allow-active` path requires a clean result from the retained independent reviewer; it refuses altered backup/guard or target data. Recipe SHA256: `b9c0d8da022072d949284ab8560318e5b4ea0169706efe9bbe5eeedb9103c1ad`.
- An isolated pristine copy passed guard validation (exit 0) and reset (exit 0): five Available, zero Assigned, one administrative closure, five new audit entries. An independent read-only query confirmed all five original conditions, the empty physical-return fields, and the expected actor/closure state. The recipe's full-row comparisons confirmed all non-target Asset/Assignment rows, all prior audits, every other table, and original target fields outside the allowed changes were identical to the pristine backup; SQLite integrity and foreign keys passed.
- A separate copy injected failure before the third audit insert: apply exited 1 and the complete-table guard then passed (exit 0), proving rollback. Another copy had a deliberately changed target condition: apply exited 1 on the stale guard and its database-file hash was unchanged. Active apply without independent review proof exited 1, followed by active read-only full-table guard exit 0 (`DATABASE_CHANGED=false`). No broad Django/frontend suite was repeated because application code and schema did not change.

## Comments

- Candidate preparation is complete; active application and post-application verification await an actual clean independent review and coordinator comparison. This statement records the preparation state at this point, not a future assertion about the database after application.
