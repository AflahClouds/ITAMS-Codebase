# Conformance Traceability Map

**Generated**: 2026-08-12 · **Source**: the nine AS-BUILT baselines under `specs/`
**Regenerate**: `python docs/conformance/build-traceability-map.py`

## What this answers, and what it does not

One question per requirement: **can we currently demonstrate that the system does what
the baseline says?** It is built entirely from what the specifications already assert —
each requirement's `*(Source: …)*` line and the bulk mappings in §Verified Behavior
Evidence — cross-checked against test symbols that actually exist in `backend/*/tests.py`.

It does **not** read application code to judge conformance. A `test-cited` row means a
named test is claimed as evidence and that test exists; it does not re-verify that the
test proves the whole requirement. Confirming conformance is the conformance suite's job.
This map sizes that job.

## Status vocabulary

| Status | Meaning |
| --- | --- |
| `test-cited` | The baseline names an automated test as evidence, and that test exists. |
| `known-gap` | The requirement appears in a conformance-gap register (U-005/U-006/U-007). The system is known **not** to satisfy it. |
| `unverified` | Neither. No test is claimed and no gap is recorded — the requirement's conformance is simply unknown. |

## Verifiability classes

| Class | Count | Can be automated today? |
| --- | --- | --- |
| `backend` | 181 | **Yes** — this is the actionable set. |
| `ui` | 94 | **No** — terminology, control visibility, and presentation need a frontend runner; `frontend/package.json` configures none. |
| `governance` | 16 | **No, and never** — requirements about the specification itself (evidence integrity, decision gates, reconciliation obligations). Verified by review. |

Classification is heuristic, from requirement wording. Treat the boundary cases as a
first pass to review, not a settled answer — a requirement mentioning a "surface" may
still have a backend rule worth testing.

## Headline numbers

- **291 requirements** across the nine baselines.
- **18 test-cited · 55 known-gap · 218 unverified.**
- Of the **181 backend** requirements that *could* be automated today:
  **15 test-cited · 24 known-gap · 142 unverified**.

So conformance is demonstrable for **15 of 181** automatable
requirements, known to fail for 24, and unknown for 142.
The dominant state is *unknown*, not *failing* — the 130 existing tests cover real
behavior, but almost none of it is traceable to a requirement.

## Per baseline

Ordered by the roadmap's dependency sequence.

| Baseline | Total | backend | test-cited | known-gap | unverified |
| --- | --- | --- | --- | --- | --- |
| B1 `003-identity-access-baseline` | 18 | 12 | 10 | 0 | 8 |
| B6 `002-procurement-vendor-catalog-baseline` | 33 | 23 | 4 | 0 | 29 |
| B2 `001-asset-register-lifecycle-baseline` | 26 | 24 | 3 | 0 | 23 |
| B8 `004-notifications-audit-baseline` | 29 | 17 | 0 | 0 | 29 |
| B3 `005-checkout-checkin-baseline` | 38 | 24 | 0 | 14 | 24 |
| B4 `006-transfer-baseline` | 28 | 20 | 1 | 0 | 27 |
| B5 `007-service-record-baseline` | 43 | 21 | 0 | 15 | 28 |
| B7 `008-warranty-amc-baseline` | 47 | 31 | 0 | 14 | 33 |
| B9 `009-dashboard-reports-exports-baseline` | 29 | 9 | 0 | 12 | 17 |

**B8 stands out**: 29 requirements, zero test-cited, zero recorded gaps — everything
unverified. It is also the baseline four others depend on. **B1 is the strongest** at 10
of 18 cited, because its privacy rules were written from passing tests rather than
toward them.

## Full map

### B1 — `003-identity-access-baseline`

| Requirement | Class | Status | Evidence |
| --- | --- | --- | --- |
| ALR-001 | ui | unverified | — |
| ALR-002 | ui | test-cited | `PrivacyAuthorizationTests`, `test_ordinary_user_cannot_read_privileged_apis` |
| ALR-003 | backend | test-cited | `PrivacyAuthorizationTests`, `test_asset_user_gets_only_minimal_active_user_directory` |
| ALR-004 | backend | unverified | — |
| ALR-005 | ui | test-cited | `test_user_manager_can_read_full_user_records` |
| FR-001 | backend | test-cited | `PrivacyAuthorizationTests`, `test_ordinary_user_cannot_read_privileged_apis` |
| FR-002 | backend | test-cited | `PrivacyAuthorizationTests`, `test_user_manager_can_read_full_user_records` |
| FR-003 | backend | test-cited | `PrivacyAuthorizationTests`, `test_asset_user_gets_only_minimal_active_user_directory` |
| FR-004 | backend | test-cited | `PrivacyAuthorizationTests`, `test_asset_user_gets_only_minimal_active_user_directory` |
| FR-005 | backend | test-cited | `PrivacyAuthorizationTests`, `test_settings_access_does_not_expose_admin_configuration` |
| FR-006 | backend | test-cited | `CheckoutTransferEndpointTests`, `ServiceRecordEndpointTests`, `test_checkout_create_requires_asset_custody_manage_permission`, `test_service_create_requires_asset_custody_manage_permission` |
| FR-007 | backend | test-cited | `CheckoutTransferEndpointTests`, `test_transfer_request_requires_transfer_request_permission` |
| FR-008 | backend | unverified | — |
| FR-009 | ui | unverified | — |
| FR-010 | backend | unverified | — |
| FR-011 | backend | unverified | — |
| FR-012 | governance | unverified | — |
| FR-013 | ui | unverified | — |

### B6 — `002-procurement-vendor-catalog-baseline`

| Requirement | Class | Status | Evidence |
| --- | --- | --- | --- |
| ALR-001 | ui | unverified | — |
| ALR-002 | backend | unverified | — |
| ALR-003 | ui | test-cited | `ProtectedMasterDataTests`, `test_delete_api_returns_conflict_for_referenced_master_records`, `test_referenced_master_records_cannot_delete_operational_data` |
| ALR-004 | backend | unverified | — |
| ALR-005 | backend | unverified | — |
| ALR-006 | backend | unverified | — |
| ALR-007 | backend | unverified | — |
| ALR-008 | ui | unverified | — |
| ALR-009 | ui | unverified | — |
| FR-001 | backend | unverified | — |
| FR-002 | backend | unverified | — |
| FR-003 | backend | unverified | — |
| FR-004 | ui | unverified | — |
| FR-005 | backend | unverified | — |
| FR-006 | backend | test-cited | `ProtectedMasterDataTests`, `test_referenced_master_records_cannot_delete_operational_data` |
| FR-007 | backend | test-cited | `ProtectedMasterDataTests`, `test_delete_api_returns_conflict_for_referenced_master_records`, `test_referenced_master_records_cannot_delete_operational_data` |
| FR-008 | backend | test-cited | `ProtectedMasterDataTests`, `test_unused_master_records_can_still_be_deleted` |
| FR-009 | backend | unverified | — |
| FR-010 | backend | unverified | — |
| FR-011 | backend | unverified | — |
| FR-012 | backend | unverified | — |
| FR-013 | backend | unverified | — |
| FR-014 | ui | unverified | — |
| FR-015 | ui | unverified | — |
| FR-016 | backend | unverified | — |
| FR-017 | backend | unverified | — |
| FR-018 | backend | unverified | — |
| FR-019 | ui | unverified | — |
| FR-020 | backend | unverified | — |
| FR-021 | ui | unverified | — |
| FR-022 | ui | unverified | — |
| FR-023 | backend | unverified | — |
| FR-024 | backend | unverified | — |

### B2 — `001-asset-register-lifecycle-baseline`

| Requirement | Class | Status | Evidence |
| --- | --- | --- | --- |
| ALR-001 | ui | unverified | — |
| ALR-002 | backend | unverified | — |
| ALR-003 | backend | unverified | — |
| ALR-004 | backend | test-cited | `CheckoutLifecycleTests`, `CheckoutTransferEndpointTests` |
| ALR-005 | backend | test-cited | `ServiceRecordEndpointTests`, `ServiceRecordLifecycleTests` |
| ALR-006 | backend | test-cited | `AssetStatusTransitionTests` |
| ALR-007 | backend | unverified | — |
| ALR-008 | backend | unverified | — |
| ALR-009 | backend | unverified | — |
| ALR-010 | backend | unverified | — |
| ALR-011 | ui | unverified | — |
| FR-001 | backend | unverified | — |
| FR-002 | backend | unverified | — |
| FR-003 | backend | unverified | — |
| FR-004 | backend | unverified | — |
| FR-005 | backend | unverified | — |
| FR-006 | backend | unverified | — |
| FR-007 | backend | unverified | — |
| FR-008 | backend | unverified | — |
| FR-009 | backend | unverified | — |
| FR-010 | backend | unverified | — |
| FR-011 | backend | unverified | — |
| FR-012 | backend | unverified | — |
| FR-013 | backend | unverified | — |
| FR-014 | backend | unverified | — |
| FR-015 | backend | unverified | — |

### B8 — `004-notifications-audit-baseline`

| Requirement | Class | Status | Evidence |
| --- | --- | --- | --- |
| ALR-001 | backend | unverified | — |
| ALR-002 | backend | unverified | — |
| ALR-003 | ui | unverified | — |
| ALR-004 | backend | unverified | — |
| ALR-005 | ui | unverified | — |
| ALR-006 | ui | unverified | — |
| FR-001 | backend | unverified | — |
| FR-002 | backend | unverified | — |
| FR-003 | backend | unverified | — |
| FR-004 | backend | unverified | — |
| FR-005 | backend | unverified | — |
| FR-006 | ui | unverified | — |
| FR-007 | backend | unverified | — |
| FR-008 | backend | unverified | — |
| FR-009 | governance | unverified | — |
| FR-010 | governance | unverified | — |
| FR-011 | backend | unverified | — |
| FR-012 | backend | unverified | — |
| FR-013 | ui | unverified | — |
| FR-014 | backend | unverified | — |
| FR-015 | backend | unverified | — |
| FR-016 | ui | unverified | — |
| FR-017 | backend | unverified | — |
| FR-018 | backend | unverified | — |
| FR-019 | ui | unverified | — |
| FR-020 | ui | unverified | — |
| FR-021 | backend | unverified | — |
| FR-022 | ui | unverified | — |
| FR-023 | ui | unverified | — |

### B3 — `005-checkout-checkin-baseline`

| Requirement | Class | Status | Evidence |
| --- | --- | --- | --- |
| ALR-001 | ui | unverified | — |
| ALR-002 | backend | unverified | — |
| ALR-003 | ui | unverified | — |
| ALR-004 | backend | unverified | — |
| ALR-005 | ui | known-gap | — |
| ALR-006 | ui | unverified | — |
| ALR-007 | backend | unverified | — |
| ALR-008 | ui | unverified | — |
| FR-001 | backend | known-gap | — |
| FR-002 | backend | unverified | — |
| FR-003 | backend | unverified | — |
| FR-004 | backend | unverified | — |
| FR-005 | backend | unverified | — |
| FR-006 | backend | known-gap | — |
| FR-007 | backend | known-gap | — |
| FR-008 | backend | unverified | — |
| FR-009 | backend | unverified | — |
| FR-010 | backend | unverified | — |
| FR-011 | backend | known-gap | — |
| FR-012 | backend | unverified | — |
| FR-013 | ui | unverified | — |
| FR-014 | ui | known-gap | — |
| FR-015 | backend | unverified | — |
| FR-016 | backend | unverified | — |
| FR-017 | backend | unverified | — |
| FR-018 | ui | known-gap | — |
| FR-019 | backend | unverified | — |
| FR-020 | ui | known-gap | — |
| FR-021 | governance | unverified | — |
| FR-022 | governance | unverified | — |
| FR-023 | backend | known-gap | — |
| FR-024 | backend | known-gap | — |
| FR-025 | backend | known-gap | — |
| FR-026 | ui | known-gap | — |
| FR-027 | backend | known-gap | — |
| FR-028 | backend | known-gap | — |
| FR-029 | ui | unverified | — |
| FR-030 | ui | unverified | — |

### B4 — `006-transfer-baseline`

| Requirement | Class | Status | Evidence |
| --- | --- | --- | --- |
| ALR-001 | ui | unverified | — |
| ALR-002 | backend | unverified | — |
| ALR-003 | backend | unverified | — |
| ALR-004 | backend | unverified | — |
| ALR-005 | backend | unverified | — |
| ALR-006 | backend | unverified | — |
| ALR-007 | ui | unverified | — |
| FR-001 | backend | unverified | — |
| FR-002 | backend | unverified | — |
| FR-003 | backend | unverified | — |
| FR-004 | backend | unverified | — |
| FR-005 | backend | test-cited | `TransferLifecycleTests`, `test_request_transfer_captures_the_current_owner_and_department` |
| FR-006 | ui | unverified | — |
| FR-007 | backend | unverified | — |
| FR-008 | backend | unverified | — |
| FR-009 | backend | unverified | — |
| FR-010 | backend | unverified | — |
| FR-011 | backend | unverified | — |
| FR-012 | backend | unverified | — |
| FR-013 | backend | unverified | — |
| FR-014 | ui | unverified | — |
| FR-015 | backend | unverified | — |
| FR-016 | backend | unverified | — |
| FR-017 | ui | unverified | — |
| FR-018 | backend | unverified | — |
| FR-019 | governance | unverified | — |
| FR-020 | ui | unverified | — |
| FR-021 | ui | unverified | — |

### B5 — `007-service-record-baseline`

| Requirement | Class | Status | Evidence |
| --- | --- | --- | --- |
| ALR-001 | ui | unverified | — |
| ALR-002 | backend | unverified | — |
| ALR-003 | ui | unverified | — |
| ALR-004 | backend | unverified | — |
| ALR-005 | backend | known-gap | — |
| ALR-006 | backend | unverified | — |
| ALR-007 | backend | unverified | — |
| ALR-008 | backend | unverified | — |
| ALR-009 | ui | unverified | — |
| FR-001 | ui | unverified | — |
| FR-002 | backend | unverified | — |
| FR-003 | backend | unverified | — |
| FR-004 | backend | unverified | — |
| FR-005 | ui | known-gap | — |
| FR-006 | backend | unverified | — |
| FR-007 | backend | unverified | — |
| FR-008 | ui | known-gap | — |
| FR-009 | backend | unverified | — |
| FR-010 | backend | known-gap | — |
| FR-011 | ui | known-gap | — |
| FR-012 | ui | unverified | — |
| FR-013 | backend | unverified | — |
| FR-014 | backend | known-gap | — |
| FR-015 | backend | known-gap | — |
| FR-016 | backend | unverified | — |
| FR-017 | backend | unverified | — |
| FR-018 | backend | unverified | — |
| FR-019 | backend | known-gap | — |
| FR-020 | ui | unverified | — |
| FR-021 | ui | known-gap | — |
| FR-022 | ui | known-gap | — |
| FR-023 | ui | known-gap | — |
| FR-024 | governance | unverified | — |
| FR-025 | governance | unverified | — |
| FR-026 | ui | known-gap | — |
| FR-028 | ui | known-gap | — |
| FR-029 | ui | known-gap | — |
| FR-030 | ui | known-gap | — |
| FR-031 | ui | unverified | — |
| FR-032 | backend | unverified | — |
| FR-033 | ui | unverified | — |
| FR-034 | governance | unverified | — |
| FR-035 | ui | unverified | — |

### B7 — `008-warranty-amc-baseline`

| Requirement | Class | Status | Evidence |
| --- | --- | --- | --- |
| ALR-001 | ui | unverified | — |
| ALR-002 | backend | unverified | — |
| ALR-003 | backend | known-gap | — |
| ALR-004 | backend | known-gap | — |
| ALR-005 | backend | unverified | — |
| ALR-006 | backend | unverified | — |
| ALR-007 | backend | unverified | — |
| ALR-008 | backend | unverified | — |
| FR-001 | backend | unverified | — |
| FR-002 | backend | unverified | — |
| FR-003 | backend | unverified | — |
| FR-004 | backend | unverified | — |
| FR-005 | backend | known-gap | — |
| FR-006 | ui | known-gap | `AmcExpiryReportTests`, `test_report_does_not_crash_on_a_contract_ended_before_dates_were_entered` |
| FR-007 | ui | unverified | — |
| FR-008 | backend | unverified | — |
| FR-009 | backend | unverified | — |
| FR-010 | backend | unverified | — |
| FR-011 | backend | known-gap | — |
| FR-012 | backend | unverified | — |
| FR-013 | backend | unverified | — |
| FR-014 | backend | unverified | — |
| FR-015 | backend | unverified | — |
| FR-016 | backend | unverified | — |
| FR-017 | ui | unverified | — |
| FR-018 | ui | unverified | — |
| FR-019 | backend | unverified | — |
| FR-020 | ui | known-gap | — |
| FR-021 | ui | known-gap | — |
| FR-022 | ui | unverified | — |
| FR-023 | backend | unverified | — |
| FR-024 | backend | known-gap | — |
| FR-025 | backend | known-gap | — |
| FR-026 | backend | unverified | — |
| FR-027 | governance | unverified | — |
| FR-028 | governance | unverified | — |
| FR-029 | governance | unverified | — |
| FR-030 | ui | known-gap | — |
| FR-031 | ui | known-gap | — |
| FR-032 | ui | known-gap | — |
| FR-033 | backend | known-gap | — |
| FR-034 | ui | known-gap | — |
| FR-035 | backend | unverified | — |
| FR-036 | backend | unverified | — |
| FR-037 | backend | unverified | — |
| FR-038 | governance | unverified | — |
| FR-039 | backend | unverified | — |

### B9 — `009-dashboard-reports-exports-baseline`

| Requirement | Class | Status | Evidence |
| --- | --- | --- | --- |
| ALR-001 | ui | known-gap | — |
| ALR-002 | backend | unverified | — |
| ALR-003 | ui | known-gap | — |
| ALR-004 | backend | unverified | — |
| ALR-005 | backend | known-gap | — |
| ALR-006 | ui | unverified | — |
| FR-001 | backend | known-gap | — |
| FR-002 | backend | unverified | — |
| FR-003 | ui | known-gap | — |
| FR-004 | backend | unverified | — |
| FR-005 | ui | known-gap | — |
| FR-006 | ui | unverified | — |
| FR-007 | ui | known-gap | — |
| FR-008 | ui | known-gap | — |
| FR-009 | ui | known-gap | — |
| FR-010 | backend | known-gap | — |
| FR-011 | backend | unverified | — |
| FR-012 | ui | unverified | — |
| FR-013 | ui | unverified | — |
| FR-014 | governance | unverified | — |
| FR-015 | governance | unverified | — |
| FR-016 | ui | unverified | — |
| FR-017 | ui | known-gap | — |
| FR-018 | ui | known-gap | — |
| FR-019 | ui | unverified | — |
| FR-020 | ui | unverified | — |
| FR-021 | ui | unverified | — |
| FR-022 | backend | unverified | — |
| FR-023 | governance | unverified | — |

## How to use this

1. **Tag first, write second.** The 130 existing tests already exercise real behavior;
   the cheapest coverage gain is naming the requirement each one proves, which converts
   `unverified` rows to `test-cited` without new tests.
2. **Work the backend column in risk order** — authorization and privacy, then lifecycle
   integrity, then audit and retention, then presentation.
3. **Translate the acceptance scenarios.** The baselines carry 290 Given/When/Then
   scenarios; those are test cases already written in prose.
4. **Reconcile as you go.** A new failing test whose requirement is *not* already in a
   gap register means the register was incomplete — that is the finding worth having.
5. **Decide the UI question separately.** 94 requirements stay unverifiable until a
   frontend test runner exists. That is a tooling decision, not a testing backlog.
