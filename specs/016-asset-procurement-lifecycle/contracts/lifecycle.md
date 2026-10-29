# Asset and Procurement Contract

## Asset create/edit/delete

- POST /assets/: valid registration stores In Storage; no direct Procurement,
  Custodian or department assignment. UI removes Available create choice.
  Conflicting explicit status is rejected or consistently normalized to Storage.
- Asset PUT/PATCH cannot directly change Procurement or promote new unprocured
  Assets to Available. Procurement owns association validation.
- DELETE /assets/{id}/: current Procurement (including archived) gives 400 with
  removal guidance. Custody-history protection remains; eligible unlinked is 204.

## Procurement association

Existing POST/PUT/PATCH formats retain arrival/date/attestation and optional
invoice_file. New eligible Storage links become Available. Removed eligible
Assets become Storage/unlinked. Already-selected Assets and metadata-only edits
preserve their current state. Empty selection gives 400 with complete-deletion
guidance for last Asset. Invalid/denied/protected/stale operations leave no
partial mutation. Retain reasoned history.

## Explicit permanent deletion

POST /procurement/{id}/permanent-delete/ uses asset_delete and existing role/scope.
Exactly one eligible linked Asset is required; wrong cardinality/protected state
gives 400, denied permission follows existing 403 behavior.
204 means purchase and owned history/arrivals/invoice versions are gone, Asset
survives unlinked Storage, exact files cleaned after commit, audit retained.
Existing DELETE /procurement/{id}/ remains archive-only with current links.

## UI sequence

Show actionable linked-Asset errors with purchase navigation. Multi-Asset edits
detach before separate Asset deletion. Singleton release has a clearly named
permanent-delete action and confirmation naming purchase/invoice/history loss,
only with deletion authority. Return to a surviving route, refresh state.
Cancellation/failure must not claim success; server authorization is authoritative.