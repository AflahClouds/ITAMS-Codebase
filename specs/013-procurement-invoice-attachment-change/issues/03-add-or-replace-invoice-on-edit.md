# 03 — Add or replace a Procurement invoice during edit

**What to build:** Let an authorized IT User add a missing purchase invoice or
replace the current invoice while editing Procurement. Omitting a file preserves
the current state, replacements retain prior versions, audit is atomic, and the
replacement Notification is sent only after commit.

**Blocked by:** 01 — Establish versioned private Procurement invoices.

**Status:** ready-for-human

- [x] Editing can add version 1 to a Procurement that has no invoice.
- [x] Editing can replace the current invoice and retain the superseded version.
- [x] Editing without selecting a file preserves the existing invoice or no-invoice state.
- [x] `asset_edit` remains the authoritative backend permission.
- [x] Audit and post-commit Notification behavior follows the B6/B8 boundary.
- [x] Automated API and page tests demonstrate the behavior before implementation.

## Comments

- Published from reviewed user-story tasks T011–T014 on 2026-09-23.
- Verified later add, omission no-op, retained replacement history, audit
  rollback, and post-commit IT-manager-equivalent Notification.
