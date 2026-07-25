# ITAMS

IT Asset Management System — tracks IT assets (laptops, hardware) through their lifecycle: procurement, checkout to employees, transfer between employees/departments, and disposal.

## Language

**Asset**:
A physical IT item (laptop, monitor, etc.) tracked from procurement to end-of-life. Has a `status` (Available, Assigned, Under Repair, In Storage, Sold, Scrapped, Lost) and a `condition` (New, Good, Average, Damaged, Repair Required), independent of each other. `Sold`, `Scrapped`, and `Lost` are terminal statuses — an Asset in one of these has left circulation.
_Avoid_: Disposed (renamed to Sold — the org's only disposal path is selling the asset; "Disposed" was a vague catch-all).

**Sold**:
Terminal Asset status — the asset was sold and has left the organization.

**Scrapped**:
Terminal Asset status — the asset was destroyed / sent to e-waste. Previously also existed as a `condition` value; dropped as redundant since `status = Scrapped` fully captures it.

**Lost**:
Terminal Asset status — the asset's whereabouts are unknown (stolen, misplaced, unaccounted for). Recorded reactively (someone reports it, or it surfaces during a Transfer/Service attempt) — there is no periodic physical audit process.
_Deferred_: scheduled/periodic asset audits (per-department or per-location physical verification against system records) — planned for the next version, not v1.

**Custodian**:
The `User` currently holding an Asset — set by Checkout or Transfer, cleared on check-in or when a Service Record opens. An Asset with no custodian is implicitly unassigned, though `status` is the authoritative field for availability.
_Exception_: on `status = Lost`, the Custodian is retained rather than cleared — it records who was accountable for the Asset at the time it went missing, deliberately breaking the "custodian = current holder" rule for the sake of accountability.

**Checkout**:
An Asset moves `Available → Assigned` to a user, and back to `Available` on check-in. No approval gate in the state machine — there's no separate Pending step like Transfer has. Distinct from Transfer, which moves custody *between* two different users and requires approval.
_Avoid_: Assignment (used loosely elsewhere in the UI, but Checkout is the precise term for this state machine). Also avoid calling this "self-service" without qualification — the state machine has no approval step, but in practice only IT Manager/IT Staff hold the `asset_transfer` permission needed to create a Checkout; employees cannot check out an asset to themselves through the system. IT performs every Checkout on the employee's behalf, in person.
_Deferred_: opening Checkout to employee self-service (e.g. for pooled/available items) is a possible future scope if IT's checkout admin load becomes a bottleneck.

**Transfer**:
An approval-gated handoff of an Asset's custody from one user (and department) to another. Moves `Pending → Approved` (custody reassigned) or `Pending → Rejected` (Asset untouched). Distinct from Checkout: always involves two users, always requires an approver. Requested by HR or IT Manager on an employee's behalf (not self-service by the employee); approved by IT (IT Manager or IT Staff).

**Procurement**:
A record of a completed asset purchase (vendor, invoice, PO), created by IT only, after the asset physically arrives at its location. Not a request workflow — unlike Transfer, there is no `requested_by`/approval stage; employees cannot ask for a new asset to be bought through the system.
_Deferred_: an employee/team-lead-initiated procurement request stage is a possible future scope, intentionally left out for now.

**Service Record**:
One repair/maintenance event for an Asset — vendor, dates sent/returned, cost/bill, and outcome. Opening a Service Record clears the Asset's Custodian and moves `status → Under Repair`, mirroring Checkout's check-in (same pattern: one Asset, one clear state at a time). Closing a Service Record returns `status → Available` — the Asset is not auto-restored to its previous Custodian; IT must perform a fresh Checkout. Distinct from `condition` (a snapshot label) and `AssetConditionLog` (a log of condition changes) — a Service Record is the fuller event that a condition change is often evidence of.

**Vendor**:
A first-class, managed entity (not free text) representing a third party the organization deals with — used by both Procurement (who an Asset was bought from) and Service Record (who is servicing/repairing an Asset). Exists so vendor-grouped reporting (e.g. "which vendor has pending repairs") is reliable.

**Warranty**:
The manufacturer's coverage period on an Asset (`warranty_start`/`warranty_end`). Distinct from AMC — a different contract, often with a different vendor and date range.

**AMC (Annual Maintenance Contract)**:
A separate, optional paid maintenance contract on an Asset, with its own start/end dates — not to be conflated with Warranty. Has a `has_amc` flag distinct from the dates: `has_amc = False` means the asset deliberately has no AMC (dates stay empty, excluded from alerts and data-completeness reports); `has_amc = True` with empty dates means the AMC exists but hasn't been entered yet (flagged as incomplete). Previously only existed as an `AssetDocument` type (an uploaded file) with no queryable dates.
_Deferred_: proactive expiry alerts (for both Warranty and AMC) — currently expiry is dashboard/report-only (pull), no scheduled push notification exists yet. When built: alerts fire at 30/15/7 days before expiry, to both IT Manager and IT Staff. IT Staff is expected to act on an AMC alert before the expiry date, by explicitly changing the AMC's status — either **Renew** (new dates recorded) or **End Support** (status changed to reflect the contract is deliberately discontinued, with a description/reason recorded — not simply inferred from the dates lapsing unattended). Either action notifies the IT Manager with the description of what was done. (Warranty dates are manufacturer-fixed and not renewable/endable the way AMC is — this status/renew/end workflow is AMC-specific.)
