# 01 — Establish versioned private Procurement invoices

**What to build:** Create the private, Procurement-owned invoice capability that
accepts a validated document, retains replacement versions, guarantees at most
one current version, and cleans up a newly written file if the operation fails.
The capability remains internal until a user workflow adopts it.

**Blocked by:** None — can start immediately.

**Status:** ready-for-human

- [x] A valid invoice can be stored once for a Procurement with version 1 current.
- [x] A replacement retains the old version and makes exactly one later version current.
- [x] Unsupported, unsafe, or over-25-MB files are rejected without retained state or files.
- [x] Invoice content is stored outside the publicly served media root.
- [x] Automated tests demonstrate the behavior before implementation.

## Comments

- Published from the reviewed foundation tasks T001–T006 on 2026-09-23.
- Focused domain/API suite passes 17 tests; migration drift check reports no changes.
