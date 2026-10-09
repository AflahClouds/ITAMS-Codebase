# 02 — Attach an optional invoice when creating Procurement

**What to build:** Let an authorized IT User create a completed Procurement for
one or more Assets with one purchase invoice in the same workflow, while keeping
the invoice optional and making the entire save atomic.

**Blocked by:** 01 — Establish versioned private Procurement invoices.

**Status:** ready-for-human

- [x] Procurement creation succeeds both with and without an invoice.
- [x] One supplied invoice is owned once by Procurement for every linked Asset.
- [x] Invalid uploads or persistence failures leave no partial Procurement, links, audit, or file.
- [x] `asset_create` remains the authoritative backend permission.
- [x] The create page submits the optional file with the existing Procurement data.
- [x] Automated API and page tests demonstrate the behavior before implementation.

## Comments

- Published from reviewed user-story tasks T007–T010 on 2026-09-23.
- Verified optional multipart create for multiple Assets, permission denial,
  invalid upload, and audit-failure rollback.
