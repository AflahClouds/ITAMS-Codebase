# Data Model: Asset Procurement Lifecycle

## Asset

Retain identity/catalog/condition/location/custody fields. Status default becomes
In Storage, with no new vocabulary. Procurement remains nullable, at most one
current purchase. Default-only migration changes no existing rows.

| Operation | Preconditions | Outcome |
| --- | --- | --- |
| Register | Authorized, valid identity, no Custodian/department | Storage, unlinked |
| New association | Eligible Storage, no conflicting purchase, valid arrival/attestation | Available, linked |
| Detach | Eligible unheld Available/Storage; another Asset remains | Storage, unlinked |
| Singleton release | Exactly one eligible Asset, deletion authority | Purchase removed; Asset retained Storage/unlinked |
| Asset delete | Unlinked and existing history safeguards permit | Asset deleted |

Protected Assigned/Under Repair/terminal states and live custody conflicts cannot
be reset or detached into invalid operational state. Metadata edits preserve state.

## Procurement

Existing fields and one-or-more current Assets remain. Ordinary archive retains
record and links. Explicit singleton deletion removes ProcurementArrival,
ProcurementAssetLink and ProcurementInvoiceVersion rows and the purchase.
Asset remains. Existing previous_procurement SET_NULL semantics remain.

## History, audit and files

Ordinary link changes retain reasons/append-only history; singleton deletion is
the confirmed Procurement-owned history exception. Independent AuditLog survives,
identifying actor/purchase/released Asset/status. Applicable notifications use
surviving targets. Clean exact invoice files only after commit; rollback keeps
metadata, links, status and files.

## Concurrency

Re-read/lock and conditionally update affected rows; do not act on stale inputs
or counts. Preserve cardinality, valid states and independent authorization.
Identity/uniqueness rules stay unchanged.