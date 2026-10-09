# Quickstart Validation: Procurement Purchase Invoice Attachment

## Prerequisites

- Backend dependencies from `backend/requirements.txt` are installed.
- Frontend dependencies from `frontend/package.json` are installed.
- A test User has `asset_view`, `asset_create`, and `asset_edit`.
- Test Assets, Vendor, Purchase Mode, Location, arrival evidence, and attestation
  satisfy existing Procurement rules.
- Prepare a valid small PDF, a file with a disallowed extension, and a file over
  25 MB.

## Automated Validation

From `backend/`:

```powershell
python manage.py test assets.tests_procurement_invoice
python manage.py test
```

From `frontend/`:

```powershell
npm test -- src/pages/procurement/Create.test.jsx src/pages/procurement/Edit.test.jsx src/pages/asset/Detail.test.jsx
npm test
npm run lint
npm run build
```

## Scenario 1: Optional create

1. Create Procurement for at least two Assets without choosing an invoice.
2. Confirm the save succeeds and both Assets remain linked.
3. Create another Procurement for at least two different Assets and choose the
   valid PDF.
4. Confirm the save succeeds, the Procurement response reports version 1, and
   every linked Asset reports the same invoice identity.

Expected: no placeholder or AssetDocument copies exist for the no-file case;
the file case stores one invoice-version row and one file.

## Scenario 2: Later add and replacement

1. Edit the Procurement created without an invoice and upload the valid PDF.
2. Confirm all linked Assets expose version 1.
3. Edit again without choosing a file.
4. Confirm version 1 is unchanged.
5. Upload a different valid invoice.
6. Confirm version 2 is current for Procurement and every linked Asset, version
   1 remains retained, one audit entry records the replacement, and the existing
   IT-Manager-equivalent recipients receive the replacement Notification after
   commit.

## Scenario 3: Mapping follows current links

1. Link a new Asset to a Procurement that has a current invoice.
2. Confirm the new Asset exposes the same current invoice without another file
   or invoice-version row.
3. Detach one Asset while preserving the existing B6 cardinality rules.
4. Confirm the detached Asset no longer exposes the invoice, while Procurement,
   version history, audit history, and link history remain.

## Scenario 4: Validation and atomicity

1. Attempt create and replacement with the disallowed extension.
2. Repeat with the file larger than 25 MB.
3. Inject a storage failure after validation in the focused backend test.

Expected: each request returns an actionable error. No partial Procurement,
version, current marker, Asset mapping, AuditLog, Notification, or orphaned new
file remains; an existing current invoice is unchanged.

## Scenario 5: Authorization and protected download

1. Repeat create-with-file as a reader lacking `asset_create`.
2. Repeat later add/replace as a reader lacking `asset_edit`.
3. Request the Procurement invoice as a User outside the Procurement surface.
4. Request the Asset-context invoice for an Asset outside the reader's scope.
5. Request the raw storage path if one can be inferred.

Expected: every request is denied or not found without returning invoice
content or metadata and without changing state. An authorized reader can stream
the file through the appropriate protected Procurement or Asset action.

## Validation Record — 2026-09-23

- `python manage.py makemigrations --check --dry-run`: passed; no model drift.
- `python manage.py test assets.tests_procurement_invoice`: 17/17 passed.
- `python manage.py test`: 290/290 passed with no Django system-check issues.
- Focused invoice component/page tests: passed.
- Complete Vitest suite, serialized: 51/51 passed across 11 files.
- `npm run lint`: passed with 0 errors. Thirteen existing hook-dependency
  warnings remain outside this feature boundary; no warning blocks the build.
- `npm run build`: passed. Vite reports the existing large-bundle advisory.

The first parallel Vitest run timed out in the unrelated `Audit.test.jsx` file;
that file passed 4/4 immediately in isolation, and the complete suite then
passed when run with one worker. Concurrent invoice replacement is protected by
the Procurement row lock plus database uniqueness constraints; SQLite coverage
exercises the constraint and replacement ordering rather than thread timing.

Scenarios 1–5 are covered by the focused API/page tests: optional multi-Asset
create, later add/replace/omit, five-Asset shared identity and detach, invalid
extension/oversize/storage/audit rollback, own-record scope, denied Procurement
scope, and protected streamed content.
