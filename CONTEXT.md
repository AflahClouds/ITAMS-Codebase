# ITAMS

IT Asset Management System — tracks IT assets (laptops, hardware) through their lifecycle: procurement, checkout to employees, transfer between employees/departments, and disposal.

## Language

**Asset**:
A physical IT item (laptop, monitor, etc.) tracked from procurement to end-of-life. Has a `status` (Available, Assigned, Under Repair, In Storage, Sold, Scrapped, Lost) and a `condition` (New, Good, Average, Damaged, Repair Required), independent of each other. `Sold`, `Scrapped`, and `Lost` are terminal statuses — an Asset in one of these has left circulation.
_Avoid_: Disposed (renamed to Sold — the org's only disposal path is selling the asset; "Disposed" was a vague catch-all).

Newly registered Assets start `In Storage`, without Procurement or a Custodian.
Adding valid Procurement makes a newly linked eligible Asset `Available`.
Removing an eligible Asset from Procurement returns it to `In Storage`.
An Asset cannot be deleted while linked to Procurement; existing custody-history
deletion protections also continue after detachment. These rules do not
retroactively reclassify historical Assets.

**Sold**:
Terminal Asset status — the asset was sold and has left the organization.

**Scrapped**:
Terminal Asset status — the asset was destroyed / sent to e-waste. Previously also existed as a `condition` value; dropped as redundant since `status = Scrapped` fully captures it.

**Lost**:
Terminal Asset status — the asset's whereabouts are unknown (stolen, misplaced, unaccounted for). Recorded reactively (someone reports it, or it surfaces during a Transfer/Service attempt) — there is no periodic physical audit process.
_Deferred_: scheduled/periodic asset audits (per-department or per-location physical verification against system records) — planned for the next version, not v1.

**Custodian**:
The `User` currently holding an Asset — set by temporary Checkout, ongoing Assign, or approved Transfer; cleared by Check-in, Take Back, or when a Service Record opens. An Asset with no Custodian is implicitly unassigned, though `status` is the authoritative field for availability.
_Exception_: on `status = Lost`, the Custodian is retained rather than cleared — it records who was accountable for the Asset at the time it went missing, deliberately breaking the "custodian = current holder" rule for the sake of accountability.

**Checkout**:
Temporary lending of an Asset from `Available → Assigned` to a user, ending with physical Check-in to `Available`. Purpose and an optional expected-return date describe the loan. It has no Pending approval step. IT performs every Checkout on the employee's behalf, in person; employees cannot check out an asset to themselves through the system.
_Avoid_: calling a temporary Checkout an ongoing Assignment, or describing IT-performed Checkout as employee self-service.
_Deferred_: opening Checkout to employee self-service (e.g. for pooled/available items) is a possible future scope if IT's checkout admin load becomes a bottleneck.

**Assignment**:
Ongoing employee custody, distinct from a temporary Checkout. IT directly **Assigns** an Available Asset to an employee with `asset_custody_manage`; **Take Back** records its physical return and inspection. An approved employee-to-employee Transfer ends one Assignment and starts another. Service or terminal interruption ends active custody administratively without claiming a physical return. Ongoing custody does not transfer company ownership to the employee.

**Transfer**:
An approval-gated handoff of an Asset's custody from one user (and department) to another. Moves `Pending → Approved` (custody reassigned) or `Pending → Rejected` (Asset untouched). Distinct from Checkout: always involves two users, always requires an approver. Requested by HR or IT Manager on an employee's behalf (not self-service by the employee); approved by IT (IT Manager or IT Staff).

**Procurement**:
A record of a completed asset purchase (vendor, invoice, PO), created by IT only, after the asset physically arrives at its location. Not a request workflow — unlike Transfer, there is no `requested_by`/approval stage; employees cannot ask for a new asset to be bought through the system.
Ordinary removal archives Procurement and retains its Asset links. A reasoned
edit may detach an eligible Asset while another Asset remains. To release the
last eligible Asset, an authorized operator explicitly **permanently deletes**
Procurement, its owned history and invoice versions/files. The Asset survives
unlinked `In Storage`, for a separate deletion if existing safeguards permit;
independent operational audit evidence remains. Purchase maintenance cannot
overwrite custody, servicing, or terminal states. This scoped retention exception
and the status transitions are recorded in
[`specs/016-asset-procurement-lifecycle/spec.md`](specs/016-asset-procurement-lifecycle/spec.md).
_Deferred_: an employee/team-lead-initiated procurement request stage is a possible future scope, intentionally left out for now.

**Service Record**:
One repair/maintenance event for an Asset — vendor, dates sent/returned, cost/bill, and outcome. Opening a Service Record ends any active Checkout or Assignment administratively, clears the Asset's Custodian and department, and moves `status → Under Repair`; it does not record a physical Check-in or Take Back. Closing a Service Record returns `status → Available` without restoring the previous Custodian; IT must deliberately start a fresh Assign or Checkout to issue it again. Distinct from `condition` (a snapshot label) and `AssetConditionLog` (a log of condition changes) — a Service Record is the fuller event that a condition change is often evidence of.

**Vendor**:
A first-class, managed entity (not free text) representing a third party the organization deals with — used by both Procurement (who an Asset was bought from) and Service Record (who is servicing/repairing an Asset). Exists so vendor-grouped reporting (e.g. "which vendor has pending repairs") is reliable.

**Warranty**:
The manufacturer's coverage period on an Asset (`warranty_start`/`warranty_end`). Distinct from AMC — a different contract, often with a different vendor and date range.

**AMC (Annual Maintenance Contract)**:
A separate, optional paid maintenance contract on an Asset, with its own start/end dates — not to be conflated with Warranty. An Asset accumulates a history of AMC contracts; each is `Incomplete`, `Active`, or `Ended`. `has_amc` is **derived from the current contract only** — true when the latest contract is `Active` or `Incomplete`, false when it is `Ended` or when no contract exists. It is not a flag anyone sets. `has_amc = True` with empty dates still means the AMC exists but hasn't been entered yet (the `Incomplete` state). Previously only existed as an `AssetDocument` type (an uploaded file) with no queryable dates.
_Avoid_: reading `has_amc = False` as "this asset deliberately has no AMC". That was the original intent, and it is no longer what the term means. Because the flag is derived, an Asset that never had an AMC and an Asset whose AMC was deliberately ended both report false, and **nothing distinguishes them**. That loss is accepted, not an oversight: recording a deliberate no-AMC decision would need a separate marker that the organization decided not to introduce.
_Consequence_: AMC data-completeness reporting can identify Assets with **no current AMC**; it cannot identify Assets that "still need an AMC decision", because that question is no longer answerable from the data. A report must not claim otherwise.
_Decision_: `ROADMAP.md` decision register, C4 — resolved 2026-08-05, recorded as FR-006 in `specs/008-warranty-amc-baseline/`. This entry was amended on 2026-08-12 to remove the contradiction that baseline's FR-029 required to be reconciled before acceptance.
Expiry alerts (for both Warranty and AMC) are proactively pushed, not just visible on a dashboard someone has to check: they fire at 30/15/7 days before expiry, to both IT Manager and IT Staff. IT Staff is expected to act on an AMC alert before the expiry date, by explicitly changing the AMC's status — either **Renew** (new dates recorded) or **End Support** (status changed to reflect the contract is deliberately discontinued, with a description/reason recorded — not simply inferred from the dates lapsing unattended). Either action notifies the IT Manager with the description of what was done. (Warranty dates are manufacturer-fixed and not renewable/endable the way AMC is — this status/renew/end workflow is AMC-specific.)
