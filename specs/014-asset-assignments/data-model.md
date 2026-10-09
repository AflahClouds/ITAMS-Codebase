# Data Model: Asset Custody

This design refines [FR-001–014 and ALR-001–005](spec.md). It preserves current Asset statuses and the existing Checkout and Transfer records.

## Asset snapshot

Existing `Asset.status`, `condition`, `custodian` and `department` remain the current snapshot. `Available` has no Custodian or department; `Assigned` has one Custodian and department follows that User. Condition is independent of status, so `Available` with `Damaged` or `Repair Required` remains valid after Take Back. Lost retains the last Custodian for accountability, without an active circulation arrangement.

Expose `custody_type` as a read-only derived value: Temporary when one active classified Checkout matches the Custodian, Ongoing when one active Assignment matches, Unclassified for a legacy open Checkout awaiting IT review, and None when no current circulation arrangement exists. A mismatched legacy Checkout must be represented as Conflicting rather than guessed.

## Ongoing Assignment

One record represents one employee's continuous ongoing custody.

| Field | Meaning |
| --- | --- |
| Asset, User | Physical item and employee who holds it during this arrangement |
| `issued_at`, `issued_by`, `issue_condition` | Issue time, operator and condition snapshot |
| `status` | Open or Closed; at most one Open Assignment per Asset |
| `closed_at`, `closed_by`, `closure_reason` | Administrative end event: Take Back, approved Transfer, Service, terminal transition, or correction |
| `return_condition`, `return_remarks` | Actual physical Take Back only; absent for handoff/interruption |
| `source_transfer`, `source_checkout`, `superseded_by_transfer` | Optional links to an approved handoff or a legacy classification/reconciliation |

An Open Assignment must match `Asset.status = Assigned` and the same Custodian. A Transfer closes the source and creates a target Assignment in one transaction. Take Back closes it and clears the Asset snapshot in one transaction. Service/terminal transitions close it with an interruption reason and no fabricated return inspection.

## Temporary Checkout

Preserve existing `AssetCheckout` issue, expected-return, physical return, condition and note fields. Add explicit `classification` with values Unclassified and Temporary for active records. A migrated existing Open Checkout begins Unclassified; every new Checkout is Temporary. A closed historical Checkout may retain Unknown historical classification rather than be mislabeled.

Add a closure state or reason that distinguishes physical Returned from Reclassified as ongoing, Superseded by approved Transfer, and Interrupted by service/terminal state. Add `closed_at`, `classified_at`, `classified_by`, and `superseded_by_transfer` as applicable. Keep `checkout_date` and `expected_return_date` unchanged during classification/reconciliation. `return_date` and `return_condition` mean physical Check-in only for a newly reconciled record; administrative closure uses separate metadata. Preserve existing `closed_as_interrupted` history rather than rewriting old rows.

Temporary classification leaves the Checkout Open and leaves the Asset snapshot unchanged. Ongoing classification closes the old Checkout administratively and creates a corresponding Open Assignment for the same current holder, using the original issue condition and issue time where known. Neither path creates a physical return.

## Transfer

Keep `AssetTransfer` request/approval status and captured source and target fields. Link new requests to the current Open Assignment identity in addition to the existing Custodian/department snapshot. Approval requires that exact arrangement still be Open and match the Asset, and that the target User is eligible. It closes the source Assignment and opens the target Assignment atomically. Rejection changes neither arrangement nor Asset snapshot.

Historical approved Transfers remain immutable evidence for reconciliation. A verified chain ending at the Asset's current Custodian is required before a stale Checkout can be superseded by that Transfer. Reconciliation records the source Checkout, approved Transfer evidence, deciding IT operator and time. It closes A's Checkout administratively and creates or confirms B's single classified current arrangement without changing B's Asset snapshot.

Historical Approved Transfers may have had `transfer_date` overwritten at approval, and older request audits cannot reliably identify the original request time for a specific Transfer. When B has no active record, a reconstructed B arrangement links the final approved Transfer and is explicitly marked `Administrative reconstruction`. Its stored start timestamp may copy that Transfer's recorded historical date only as an administrative marker; reads must show the basis “Legacy Transfer event date (event type unverified)” and must not assert request, approval, physical issue, handoff or return time. Missing original request-time evidence alone does not invalidate an otherwise verified approved holder chain. For Temporary custody, create an Open Checkout for B with this provenance, no return date/inspection and no invented expected-return date or purpose. For Ongoing custody, create an Open Assignment with the same provenance. If B already has a matching active arrangement, verify its holder/type and link the reconciliation without creating a duplicate or rewriting its known start. The original A Checkout's `checkout_date` and `expected_return_date` are never changed.

## Return inspection and audit

Take Back requires explicit actual condition and creates an `AssetConditionLog` inspection even if the value is unchanged. Worsening from issue condition requires remarks under the established B3 order and New-to-Good exception. Physical return fields stay empty on Transfer, service, terminal and administrative reconciliation.

Audit records identify actor, Asset, affected employees, action, old/new status and custody values, relevant Checkout/Assignment/Transfer identities and reason. The audit write is in the same transaction as the state change. Notifications to active recipients occur after successful commit and do not roll back custody on delivery failure.

## State transitions and invariants

| Action | Precondition | Snapshot and active-history effect |
| --- | --- | --- |
| Assign | Available, no active custody, active target User | Assigned to target; new Open Assignment |
| Checkout | Available, no active custody, active target User | Assigned to target; new Open Temporary Checkout |
| Check-in | Current Open Temporary Checkout; no later holder | Available, no Custodian/department; physical Returned Checkout |
| Take Back | Current Open Assignment; no Pending Transfer | Available, no Custodian/department; physical return closes Assignment |
| Request Transfer | Current Open Assignment; no Pending Transfer; different active target | Pending request only; snapshot unchanged |
| Approve Transfer | Same source Assignment and snapshot as request | Source closes; target opens; Asset holder/department changes |
| Reject Transfer | Pending request | Request closes as Rejected; custody unchanged |
| Open Service | Eligible nonterminal Asset | Active custody closes as Interrupted; Under Repair, no Custodian |
| Close Service | Matching Open Service Record | Available, no automatic reissue |
| Record Lost | Eligible nonterminal Asset | Active arrangement ends; Asset retains last Custodian for accountability |
| Classify legacy | Open Unclassified Checkout matching Asset holder | Temporary remains Open, or old Checkout closes administratively and ongoing Assignment opens |
| Reconcile legacy | Verified approved Transfer chain establishes current holder | Stale Checkout closes as Superseded; original dates remain; current holder/type recorded without physical Check-in |

An old Take Back, Check-in or approval must match the exact active arrangement identity, not only the same employee id. The domain operation re-reads the current Asset and arrangement under a transaction and rejects stale input without partial writes. Add database uniqueness where each table supports it and integration tests for the cross-table invariant, including SQLite's limited row-lock behavior.
