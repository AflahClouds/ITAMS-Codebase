# 04 — Expose the Procurement invoice through linked Assets

**What to build:** Let an authorized reader discover and download the same
current Procurement invoice from the Procurement and every currently linked
Asset. Later Asset links inherit exposure, detachments lose it, and no Asset
receives a copied file or public storage URL.

**Blocked by:** 01 — Establish versioned private Procurement invoices.

**Status:** ready-for-human

- [x] Every linked Asset exposes the same current invoice identity without an AssetDocument copy.
- [x] Later attachment and detachment update exposure automatically.
- [x] Procurement and Asset downloads stream only through record-authorized routes.
- [x] An out-of-scope reader or guessed storage path returns no content or metadata.
- [x] Procurement list and Asset detail present protected download actions.
- [x] Automated API and page tests demonstrate the behavior before implementation.

## Comments

- Published from reviewed user-story tasks T015–T018 on 2026-09-23.
- Verified one invoice identity across five linked Assets, detach behavior,
  own-record scoping, no AssetDocument copies, and streamed downloads.
