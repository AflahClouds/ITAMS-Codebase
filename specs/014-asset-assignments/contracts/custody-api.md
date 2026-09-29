# Custody API Contract

The service keeps the existing `/asset/`, `/checkout/` and `/transfer/` routes. New actions use explicit endpoints; arbitrary update/delete requests are not custody operations. All error responses use the existing `{ "detail": "..." }` shape. The exact response field names may follow the established serializers, but the behavior below is binding.

## Current custody reads

- `GET /asset/{id}/` and asset list entries expose `status`, `condition`, `custodian`, `department` and a read-only `custody_type` of Temporary, Ongoing, Unclassified, Conflicting or None. Lost may show the retained last Custodian with no active custody type.
- `GET /checkout/` retains temporary and historical Checkout records, visibly distinguishing physical Returned, administratively Reclassified, Superseded and Interrupted outcomes.
- `GET /assignment/` lists ongoing Assignment history, filtered by existing Asset read scope. An active Assignment identifies its Asset, holder, issue condition, issue time and operator; a closed one identifies the end reason and any actual return condition.
- `GET /transfer/` retains Pending/Approved/Rejected requests and the existing document download. Ordinary readers receive only records allowed by `asset_view` and the existing Employee scope.

## Assign

`POST /assignment/` requires `asset_custody_manage`.

```json
{ "asset": 17, "user": 42, "remarks": "Everyday laptop" }
```

The server captures the Asset's issue condition. Success creates an Open ongoing Assignment and changes the Asset from Available/no Custodian to Assigned/target User/target department. No Pending approval is created. A held, service, storage or terminal Asset, inactive target, or unclassified/conflicting legacy custody returns a validation error with no partial mutation. The response identifies the Assignment and current Asset custody.

## Take Back

`POST /assignment/{id}/take-back/` requires `asset_custody_manage`.

```json
{ "condition": "Damaged", "remarks": "Screen cracked on return" }
```

Condition is required and has no server- or client-selected default. Remarks are required only for deterioration under the existing condition comparison. Success closes the current Assignment as an actual Take Back, creates an inspection, sets the Asset to Available with that selected condition, and clears Custodian and department. If any Transfer for the Asset is Pending, return `400 { "detail": "Transfer request is not closed." }`; the Asset, Assignment, Transfer and condition remain unchanged. A stale or repeated Take Back also fails without mutation.

## Temporary Checkout and Transfer

- `POST /checkout/` and `POST /checkout/{id}/checkin/` retain their existing request/response shapes, with new Checkouts explicitly Temporary.
- `POST /transfer/` requires `transfer_request` and a current ongoing Assignment. An Asset on a confirmed temporary Checkout fails with a message such as “This asset is being temporarily held by another employee.” No Pending Transfer is created. Same-holder, ineligible target, unclassified/conflicting and existing-Pending requests also fail.
- `POST /transfer/{id}/approve/` requires `asset_custody_manage`, rechecks the captured source Assignment and current Asset. A valid approval closes A's arrangement and opens B's ongoing arrangement together with the Asset update and condition rule. A stale approval fails without mutation.
- `POST /transfer/{id}/reject/` retains the existing rejection semantics. IT can reject a Pending request before Take Back.

## Legacy classification

`POST /checkout/{id}/classify/` requires `asset_custody_manage`.

```json
{ "custody_type": "Ongoing", "remarks": "Everyday device verified by IT" }
```

Only an Open Unclassified legacy Checkout naming the current Asset Custodian may be classified directly. Temporary keeps it Open; Ongoing ends it as administrative Reclassified and opens an Assignment for the same holder. Neither path records a physical return or changes the current Asset Custodian. If Checkout and Asset disagree, return an error describing the conflicting records and direct IT to reconciliation. Retries do not create duplicate arrangements.

`POST /checkout/{id}/reconcile/` requires `asset_custody_manage`.

```json
{ "approved_transfer": 9, "custody_type": "Ongoing", "remarks": "Verified handoff to current holder" }
```

The server verifies an approved Transfer or approved chain from the stale Checkout holder to the Asset's current Custodian. On success, it marks that Checkout Superseded by the Transfer, preserves original issue/expected-return dates, leaves physical return fields empty, retains the current Custodian/status/department and records one active arrangement of the chosen type for that current holder. It records operator/time and source links in audit/history. If the approved history does not establish the current holder, return a conflict error without mutation. A repeated reconciliation is rejected or safely returns the prior result without creating a second arrangement.

If B has no matching active arrangement, the newly recorded Temporary Checkout or Ongoing Assignment is labeled `Administrative reconstruction` and links the final approved Transfer. The legacy Transfer's `transfer_date` is request time, not approval time: expose any copied date as the earliest documented Transfer request, never as a proven physical issue, Checkout or approval timestamp. Leave return inspection, expected-return date and unsupported purpose empty. If B already has a current arrangement, verify and retain it rather than creating a second one.

## Authorization, audit and notifications

Backend permission checks are authoritative for every action; the frontend hides only unavailable actions. Successful state changes and required audit write in one transaction. Assign notifies the receiving active employee; Take Back notifies the former employee only while their account is active. Preserve existing Checkout/Transfer notifications. Notification delivery failure cannot undo committed custody.
