# ITAMS

IT Asset Management System — tracks IT assets (laptops, hardware) through their lifecycle: procurement, checkout to employees, transfer between employees/departments, and disposal.

## Language

**Asset**:
A physical IT item (laptop, monitor, etc.) tracked from procurement to disposal. Has a `status` (Available, Assigned, Under Repair, In Storage, Disposed, Scrapped) and a `condition` (New, Good, Average, Damaged, Repair Required, Scrapped), independent of each other.

**Custodian**:
The `User` currently holding an Asset — set by Checkout or Transfer, cleared on check-in. An Asset with no custodian is implicitly unassigned, though `status` is the authoritative field for availability.

**Checkout**:
A self-service loop: an Asset moves `Available → Assigned` to a user, and back to `Available` on check-in. No approval gate — the requester and the custodian are the same user. Distinct from Transfer, which moves custody *between* two different users and requires approval.
_Avoid_: Assignment (used loosely elsewhere in the UI, but Checkout is the precise term for this state machine).

**Transfer**:
An approval-gated handoff of an Asset's custody from one user (and department) to another. Moves `Pending → Approved` (custody reassigned) or `Pending → Rejected` (Asset untouched). Distinct from Checkout: always involves two users, always requires an approver.
