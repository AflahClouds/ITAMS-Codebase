# Service Record clears custodian and does not auto-restore it

Servicing/repair was previously untracked (Excel, no vendor/cost/date history). We introduced
Service Record as a first-class concept and had to decide how it interacts with an Asset's
Custodian and `status`.

Decision: opening a Service Record clears the Asset's Custodian and sets `status → Under Repair`,
the same pattern Checkout already uses on check-in. Closing a Service Record sets
`status → Available` — it does **not** automatically reassign the Asset back to whoever held it
before. IT must perform a fresh Checkout to hand it back out.

We considered keeping the Custodian in place through servicing (asset "still belongs" to the
employee while at the vendor) and considered auto-restoring the previous Custodian on close. Both
were rejected: retaining custodian while the asset is physically elsewhere is ambiguous about who
actually has it, and auto-restoring skips the deliberate check IT should make (the employee may
have left, been given a replacement, etc. in the meantime). Reusing the existing
Checkout/check-in pattern also keeps the state machine consistent — one Asset, one clear state at
a time — rather than adding a second, different rule for how custody clears and returns.

Vendor was made a first-class entity (shared with Procurement) rather than free text, since
vendor-grouped reporting ("which vendor has pending repairs") needs reliable matching, not
free-typed names.
