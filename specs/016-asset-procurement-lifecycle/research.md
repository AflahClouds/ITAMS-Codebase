# Research: Asset Procurement Lifecycle

Authority is the accepted user decisions in spec.md. Local code is evidence of
current behavior only. Read-only research completed without writes or tests.

## Association/status ownership

- **Decision**: One transactional procurement_lifecycle domain seam; serializers
  own input/arrival validation and views retain authorization/audit/notifications.
- **Rationale**: ProcurementSerializer bulk writes skip status/locked revalidation.
  AssetSerializer fields="__all__" exposes direct procurement writes. Existing
  custody.py/checkout.py use locks plus conditional writes for SQLite.
- **Alternatives considered**: Duplicated view mutations, signals/global save
  hooks, or general framework; all obscure ownership or add unjustified cost.
  Reject direct Asset linking instead of bypassing purchase arrival/history.

## Destructive release versus ordinary archive

- **Decision**: Retain existing archive DELETE; explicit permanent-delete action
  requires asset_delete and exactly one eligible Asset.
- **Rationale**: User confirms singleton hard-delete exception; ordinary archive
  is excluded and already tested. Reject protected states/stale links.
- **Alternatives considered**: Hard-delete all DELETE calls (out of scope),
  automatic deletion from Asset DELETE (wrong sequence), archive-and-detach
  (explicitly rejected).

## Private invoices

- **Decision**: Capture exact file names/storage objects and clean after successful
  commit, with rollback and committed cleanup integration coverage.
- **Rationale**: Django cascade deletes rows, not FileField bytes.
  procurement_invoices.py handles upload rollback but not deletion lifecycle.
- **Alternatives considered**: Pre-commit file deletion loses rollback evidence;
  retaining all files fails the approved complete-deletion outcome.

## Defaults and fixtures

- **Decision**: Change model/serializer/form defaults to In Storage and add
  default-only AlterField migration; preserve existing data. Fixtures requiring
  Available stock declare it explicitly or use valid Procurement.
- **Rationale**: All three current defaults independently use Available.
- **Alternatives considered**: Bulk historical reclassification (not authorized),
  frontend-only change (bypass), weakening unrelated custody tests (invalid).

## Quality, surfaces and runtime

- **Decision**: Reuse APIClient, Vitest and existing commands; fail-before
  permanent regressions and mandatory full checks. No new harness.
- **Rationale**: Existing tests cover cardinality, archives, invoice rollback and
  custody deletion. Frontend asset/Delete.jsx lacks error catching, Procurement
  Delete is archive-specific, and Edit lacks last-Asset guidance/link reason.
- **Alternatives considered**: Private helper tests alone cannot prove public
  behavior; new dependencies increase cost without value.
- **Runtime evidence**: Existing isolated Spec Kit 1.0.13 verified. Old
  feature-015 run dc44aeed completed; no new feature-016 run yet.