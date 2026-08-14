# Conformance Traceability Map

**Generated**: 2026-08-14 · **Source**: `Covers:` tags in `backend/*/test*.py`, plus the nine AS-BUILT baselines under `specs/`
**Regenerate**: `python docs/conformance/build-traceability-map.py`

This document is generated in full. Edit the generator, not this file.

## What this answers, and what it does not

One question per requirement: **can we currently demonstrate that the system does what the baseline says?**

Evidence is read from `Covers: B<n> FR-xxx` tags in the test docstrings, then from each baseline's §Verified Behavior Evidence. **The tags are the authoritative direction.** Once a baseline is accepted its requirement content is immutable under Constitution III, so a test written afterwards could never be recorded in that baseline's evidence section — tagging the test keeps this map regenerable for the life of the project.

It does **not** read application code to judge conformance. `test-cited` means a tagged test exists and passes; it does not re-verify that the test proves the whole requirement.

## Status vocabulary

| Status | Meaning |
| --- | --- |
| `test-cited` | A tagged automated test demonstrates it, and no gap is recorded against it. |
| `partly-met` | Passing evidence **and** a recorded gap — an `expectedFailure` test, a register row, or both. |
| `known-gap` | A recorded gap with no passing evidence. The system is known **not** to satisfy it. |
| `unverified` | Neither — conformance is unknown. |

A test marked `@unittest.expectedFailure` proves the opposite of conformance, so it is never counted as evidence. `partly-met` exists because collapsing it either way misleads: folding it into `test-cited` inflates the demonstrated count, and folding it into `known-gap` buries real evidence and never notices a register row going stale — B9's rows 1-4 are recorded closed in its own conformance update and are still listed. Only `test-cited` counts as demonstrated below.

## Verifiability classes

| Class | Count | Automatable today? |
| --- | --- | --- |
| `backend` | 181 | **Yes** — the actionable set. |
| `ui` | 94 | **No** — no frontend runner is configured. |
| `governance` | 16 | **No, and never** — requirements about the specification itself. |

Classification is heuristic from requirement wording; treat boundary cases as a first pass to review.

## Headline numbers

- **291 requirements** across the nine baselines.
- **147 test-cited · 47 partly-met · 11 known-gap · 86 unverified.**
- Of the **181 backend** requirements automatable today:
  **109 test-cited · 23 partly-met · 4 known-gap · 45 unverified**.

**60% of the automatable set is fully demonstrated**, from 8% at the start, with a further 13% partly met. Two moves got it there: tagging the existing suite (+69, no new tests), then writing a conformance suite for whichever baseline was weakest at the time — B8, then B9, B6, B7, and B8 and B9 again.

0 tests are marked `expectedFailure`. They document requirements the code does not satisfy, so the suite stays green against known gaps while the runner reports an unexpected success the moment one is fixed.

The 47 `partly-met` requirements are the most useful column to work: each already has a test harness and a named defect, so closing one is a small change rather than a new investigation.

## Per baseline

| Baseline | Total | backend | test-cited | partly-met | known-gap | unverified |
| --- | --- | --- | --- | --- | --- | --- |
| B1 `003-identity-access-baseline` | 18 | 12 | 13 | 0 | 0 | 5 |
| B2 `001-asset-register-lifecycle-baseline` | 26 | 24 | 15 | 0 | 0 | 11 |
| B3 `005-checkout-checkin-baseline` | 38 | 24 | 11 | 10 | 4 | 13 |
| B4 `006-transfer-baseline` | 28 | 20 | 16 | 0 | 0 | 12 |
| B5 `007-service-record-baseline` | 43 | 21 | 12 | 10 | 5 | 16 |
| B6 `002-procurement-vendor-catalog-baseline` | 33 | 23 | 18 | 0 | 0 | 15 |
| B7 `008-warranty-amc-baseline` | 47 | 31 | 25 | 15 | 2 | 5 |
| B8 `004-notifications-audit-baseline` | 29 | 17 | 22 | 0 | 0 | 7 |
| B9 `009-dashboard-reports-exports-baseline` | 29 | 9 | 15 | 12 | 0 | 2 |

**B5 is now the weakest** at 12 fully demonstrated against 16 unverified.

## Full map

### B1 — `003-identity-access-baseline`

| Requirement | Class | Status | Evidence | Failing clause | In register |
| --- | --- | --- | --- | --- | --- |
| ALR-001 | ui | test-cited | `test_a_profile_without_a_login_account_can_be_disabled`, `test_an_active_profile_keeps_its_token`, `test_disabled_profile_is_denied_even_with_a_live_token`, `test_disabling_outside_the_api_revokes_the_token`, `test_disabling_through_the_api_revokes_the_token`, `test_revoked_token_no_longer_authenticates` | — | — |
| ALR-002 | ui | test-cited | `PrivacyAuthorizationTests`, `test_ordinary_user_cannot_read_privileged_apis`, `test_settings_access_does_not_expose_admin_configuration` | — | — |
| ALR-003 | backend | test-cited | `PrivacyAuthorizationTests`, `test_asset_user_gets_only_minimal_active_user_directory` | — | — |
| ALR-004 | backend | unverified | — | — | — |
| ALR-005 | ui | test-cited | `test_employee_cannot_download_someone_elses_transfer_document`, `test_employee_cannot_reach_another_holders_asset_by_id`, `test_employee_is_denied_the_user_directory`, `test_user_manager_can_read_full_user_records` | — | — |
| FR-001 | backend | test-cited | `PrivacyAuthorizationTests`, `test_a_common_password_is_rejected_even_though_it_is_long_enough`, `test_a_strong_password_is_accepted`, `test_ordinary_user_cannot_read_privileged_apis` | — | — |
| FR-002 | backend | test-cited | `PrivacyAuthorizationTests`, `test_user_manager_can_read_full_user_records` | — | — |
| FR-003 | backend | test-cited | `PrivacyAuthorizationTests`, `test_asset_user_gets_only_minimal_active_user_directory` | — | — |
| FR-004 | backend | test-cited | `PrivacyAuthorizationTests`, `test_asset_user_gets_only_minimal_active_user_directory` | — | — |
| FR-005 | backend | test-cited | `PrivacyAuthorizationTests`, `test_settings_access_does_not_expose_admin_configuration` | — | — |
| FR-006 | backend | test-cited | `CheckoutTransferEndpointTests`, `ServiceRecordEndpointTests`, `test_checkout_create_requires_asset_custody_manage_permission`, `test_service_create_requires_asset_custody_manage_permission` | — | — |
| FR-007 | backend | test-cited | `CheckoutTransferEndpointTests`, `test_transfer_request_requires_transfer_request_permission` | — | — |
| FR-008 | backend | test-cited | `test_employee_sees_only_assets_it_holds` | — | — |
| FR-009 | ui | unverified | — | — | — |
| FR-010 | backend | unverified | — | — | — |
| FR-011 | backend | unverified | — | — | — |
| FR-012 | governance | test-cited | `test_a_global_reader_still_sees_every_record`, `test_a_non_employee_role_still_reads_globally`, `test_employee_dashboard_counts_only_its_own_assets`, `test_employee_is_denied_procurement_entirely`, `test_employee_is_denied_the_user_directory`, `test_employee_lists_only_transfers_it_is_party_to`, `test_employee_may_download_the_document_for_a_transfer_it_is_party_to`, `test_employee_sees_files_only_for_assets_it_holds`, `test_employee_sees_only_assets_it_holds`, `test_employee_sees_only_its_own_checkouts`, `test_employee_sees_service_records_only_for_assets_it_holds`, `test_the_employee_role_gets_no_b6_surface` | — | — |
| FR-013 | ui | unverified | — | — | — |

### B2 — `001-asset-register-lifecycle-baseline`

| Requirement | Class | Status | Evidence | Failing clause | In register |
| --- | --- | --- | --- | --- | --- |
| ALR-001 | ui | unverified | — | — | — |
| ALR-002 | backend | unverified | — | — | — |
| ALR-003 | backend | unverified | — | — | — |
| ALR-004 | backend | test-cited | `CheckoutLifecycleTests`, `CheckoutTransferEndpointTests`, `test_approve_reassigns_custodian_department_and_condition`, `test_cannot_enter_assigned_by_direct_edit`, `test_cannot_leave_assigned_by_direct_edit`, `test_cannot_move_directly_between_assigned_and_under_repair` | — | — |
| ALR-005 | backend | test-cited | `ServiceRecordEndpointTests`, `ServiceRecordLifecycleTests`, `test_cannot_enter_under_repair_by_direct_edit`, `test_cannot_leave_under_repair_by_direct_edit`, `test_cannot_move_directly_between_assigned_and_under_repair`, `test_open_service_clears_custodian_and_marks_under_repair` | — | — |
| ALR-006 | backend | test-cited | `AssetStatusTransitionTests`, `test_cannot_reverse_out_of_a_terminal_status`, `test_entering_lost_retains_custodian_even_if_payload_clears_it`, `test_entering_sold_clears_custodian_even_if_payload_keeps_it`, `test_entering_terminal_status_closes_the_open_checkout`, `test_entering_terminal_status_closes_the_open_service_record` | — | — |
| ALR-007 | backend | test-cited | `test_create_rejects_a_custodian`, `test_create_rejects_a_lifecycle_managed_status`, `test_edit_cannot_assign_a_custodian_directly` | — | — |
| ALR-008 | backend | unverified | — | — | — |
| ALR-009 | backend | test-cited | `test_a_non_employee_role_still_reads_globally`, `test_employee_cannot_reach_another_holders_asset_by_id`, `test_employee_sees_only_assets_it_holds` | — | — |
| ALR-010 | backend | unverified | — | — | — |
| ALR-011 | ui | unverified | — | — | — |
| FR-001 | backend | unverified | — | — | — |
| FR-002 | backend | test-cited | `test_administrative_status_edits_are_unaffected`, `test_editing_unrelated_fields_without_a_status_change_is_unaffected` | — | — |
| FR-003 | backend | unverified | — | — | — |
| FR-004 | backend | unverified | — | — | — |
| FR-005 | backend | unverified | — | — | — |
| FR-006 | backend | test-cited | `test_approve_reassigns_custodian_department_and_condition`, `test_check_in_returns_asset_to_available_with_new_condition`, `test_check_out_assigns_asset_to_user_and_their_department` | — | — |
| FR-007 | backend | test-cited | `test_close_service_returns_asset_to_available_without_reassigning_custodian`, `test_open_service_clears_custodian_and_marks_under_repair` | — | — |
| FR-008 | backend | test-cited | `test_cannot_reverse_out_of_a_terminal_status` | — | — |
| FR-009 | backend | test-cited | `test_entering_lost_retains_custodian_even_if_payload_clears_it`, `test_entering_sold_clears_custodian_even_if_payload_keeps_it`, `test_marking_an_asset_lost_still_retains_its_custodian` | — | — |
| FR-010 | backend | unverified | — | — | — |
| FR-011 | backend | test-cited | `test_check_in_rejects_an_invalid_condition` | — | — |
| FR-012 | backend | test-cited | `test_cannot_enter_assigned_by_direct_edit`, `test_cannot_enter_under_repair_by_direct_edit`, `test_cannot_leave_assigned_by_direct_edit`, `test_cannot_leave_under_repair_by_direct_edit`, `test_cannot_move_directly_between_assigned_and_under_repair` | — | — |
| FR-013 | backend | test-cited | `test_create_rejects_a_custodian`, `test_create_rejects_a_lifecycle_managed_status`, `test_create_still_accepts_available_and_in_storage` | — | — |
| FR-014 | backend | test-cited | `test_disposal_is_still_allowed_directly_from_assigned`, `test_lost_is_still_allowed_directly_from_under_repair` | — | — |
| FR-015 | backend | test-cited | `test_check_in_clears_department_and_logs_the_inspection` | — | — |

### B3 — `005-checkout-checkin-baseline`

| Requirement | Class | Status | Evidence | Failing clause | In register |
| --- | --- | --- | --- | --- | --- |
| ALR-001 | ui | test-cited | `test_checkout_create_requires_asset_custody_manage_permission` | — | — |
| ALR-002 | backend | unverified | — | — | — |
| ALR-003 | ui | test-cited | `test_checkout_create_requires_asset_custody_manage_permission` | — | — |
| ALR-004 | backend | test-cited | `test_check_in_rejects_an_already_closed_checkout`, `test_check_in_rejects_an_invalid_condition`, `test_check_in_requires_a_return_condition`, `test_check_out_rejects_an_unavailable_asset` | — | — |
| ALR-005 | ui | known-gap | — | — | yes |
| ALR-006 | ui | unverified | — | — | — |
| ALR-007 | backend | unverified | — | — | — |
| ALR-008 | ui | unverified | — | — | — |
| FR-001 | backend | partly-met | `test_a_returned_checkout_does_not_block_the_next_one`, `test_an_asset_cannot_have_two_open_checkouts`, `test_check_out_assigns_asset_to_user_and_their_department`, `test_checkout_create_and_checkin_round_trip` | — | yes |
| FR-002 | backend | test-cited | `test_check_in_returns_asset_to_available_with_new_condition`, `test_checkout_create_and_checkin_round_trip` | — | — |
| FR-003 | backend | unverified | — | — | — |
| FR-004 | backend | test-cited | `test_check_out_assigns_asset_to_user_and_their_department` | — | — |
| FR-005 | backend | unverified | — | — | — |
| FR-006 | backend | partly-met | `test_check_out_assigns_asset_to_user_and_their_department`, `test_checkout_to_a_user_with_no_department_clears_the_previous_one` | — | yes |
| FR-007 | backend | partly-met | `test_a_returned_checkout_does_not_block_the_next_one`, `test_an_asset_cannot_have_two_open_checkouts`, `test_cannot_enter_assigned_by_direct_edit`, `test_cannot_leave_assigned_by_direct_edit` | — | yes |
| FR-008 | backend | test-cited | `test_check_out_rejects_an_unavailable_asset` | — | — |
| FR-009 | backend | test-cited | `test_check_in_rejects_an_already_closed_checkout` | — | — |
| FR-010 | backend | test-cited | `test_check_in_rejects_an_invalid_condition` | — | — |
| FR-011 | backend | partly-met | `test_an_asset_cannot_have_two_open_checkouts` | — | yes |
| FR-012 | backend | test-cited | `test_check_in_rejects_an_already_closed_checkout` | — | — |
| FR-013 | ui | unverified | — | — | — |
| FR-014 | ui | partly-met | `test_a_return_in_a_worse_condition_requires_return_remarks`, `test_a_worse_return_is_accepted_once_it_is_explained`, `test_an_improved_condition_needs_no_explanation`, `test_an_interrupting_closure_also_preserves_intake_remarks`, `test_check_in_returns_asset_to_available_with_new_condition`, `test_check_out_persists_intake_remarks`, `test_returning_a_new_asset_in_good_order_needs_no_explanation` | — | yes |
| FR-015 | backend | test-cited | `test_open_service_closes_the_open_checkout_it_interrupts` | — | — |
| FR-016 | backend | test-cited | `test_entering_terminal_status_closes_the_open_checkout` | — | — |
| FR-017 | backend | unverified | — | — | — |
| FR-018 | ui | known-gap | — | — | yes |
| FR-019 | backend | unverified | — | — | — |
| FR-020 | ui | partly-met | `test_check_out_notifies_the_new_custodian` | — | yes |
| FR-021 | governance | unverified | — | — | — |
| FR-022 | governance | unverified | — | — | — |
| FR-023 | backend | partly-met | `test_check_in_clears_department_and_logs_the_inspection`, `test_check_in_returns_asset_to_available_with_new_condition` | — | yes |
| FR-024 | backend | partly-met | `test_check_in_requires_a_return_condition` | — | yes |
| FR-025 | backend | partly-met | `test_check_in_clears_department_and_logs_the_inspection` | — | yes |
| FR-026 | ui | known-gap | — | — | yes |
| FR-027 | backend | known-gap | — | — | yes |
| FR-028 | backend | partly-met | `test_a_genuine_check_in_is_not_marked_as_interrupted`, `test_an_interrupted_checkout_is_marked_as_such`, `test_an_interrupting_closure_also_preserves_intake_remarks`, `test_open_service_closes_the_open_checkout_it_interrupts` | — | yes |
| FR-029 | ui | unverified | — | — | — |
| FR-030 | ui | unverified | — | — | — |

### B4 — `006-transfer-baseline`

| Requirement | Class | Status | Evidence | Failing clause | In register |
| --- | --- | --- | --- | --- | --- |
| ALR-001 | ui | test-cited | `test_transfer_request_requires_transfer_request_permission` | — | — |
| ALR-002 | backend | test-cited | `test_approve_reassigns_custodian_department_and_condition` | — | — |
| ALR-003 | backend | test-cited | `test_approve_rejects_an_already_processed_transfer`, `test_approve_rejects_an_asset_sent_for_service_after_the_request`, `test_approve_rejects_an_asset_that_turned_terminal_after_the_request`, `test_reject_leaves_the_asset_untouched`, `test_reject_rejects_an_already_processed_transfer`, `test_request_transfer_rejects_a_terminal_asset`, `test_request_transfer_rejects_an_asset_under_repair` | — | — |
| ALR-004 | backend | test-cited | `test_approve_rejects_an_already_processed_transfer`, `test_reject_rejects_an_already_processed_transfer` | — | — |
| ALR-005 | backend | unverified | — | — | — |
| ALR-006 | backend | unverified | — | — | — |
| ALR-007 | ui | test-cited | `test_a_new_request_is_allowed_once_the_previous_one_is_decided`, `test_transfer_rejects_a_second_pending_request`, `test_transfer_rejects_the_current_custodian_as_target` | — | — |
| FR-001 | backend | test-cited | `test_transfer_rejects_the_current_custodian_as_target` | — | — |
| FR-002 | backend | test-cited | `test_transfer_request_requires_transfer_request_permission` | — | — |
| FR-003 | backend | unverified | — | — | — |
| FR-004 | backend | test-cited | `test_a_non_employee_role_still_sees_every_transfer`, `test_employee_lists_only_transfers_it_is_party_to` | — | — |
| FR-005 | backend | test-cited | `TransferLifecycleTests`, `test_request_transfer_captures_the_current_owner_and_department`, `test_transfer_rejects_a_second_pending_request`, `test_transfer_request_and_approve_round_trip` | — | — |
| FR-006 | ui | unverified | — | — | — |
| FR-007 | backend | test-cited | `test_request_transfer_captures_the_current_owner_and_department` | — | — |
| FR-008 | backend | test-cited | `test_approve_reassigns_custodian_department_and_condition`, `test_reject_leaves_the_asset_untouched`, `test_transfer_reject_round_trip`, `test_transfer_request_and_approve_round_trip` | — | — |
| FR-009 | backend | test-cited | `test_request_transfer_rejects_a_terminal_asset`, `test_request_transfer_rejects_an_asset_under_repair` | — | — |
| FR-010 | backend | test-cited | `test_approve_rejects_an_asset_sent_for_service_after_the_request`, `test_approve_rejects_an_asset_that_turned_terminal_after_the_request` | — | — |
| FR-011 | backend | unverified | — | — | — |
| FR-012 | backend | unverified | — | — | — |
| FR-013 | backend | unverified | — | — | — |
| FR-014 | ui | unverified | — | — | — |
| FR-015 | backend | test-cited | `test_asset_view_holder_may_download_the_transfer_document`, `test_employee_cannot_download_someone_elses_transfer_document`, `test_employee_may_download_the_document_for_a_transfer_it_is_party_to` | — | — |
| FR-016 | backend | test-cited | `test_request_transfer_notifies_users_with_approval_permission` | — | — |
| FR-017 | ui | test-cited | `test_request_transfer_notifies_users_with_approval_permission` | — | — |
| FR-018 | backend | unverified | — | — | — |
| FR-019 | governance | unverified | — | — | — |
| FR-020 | ui | unverified | — | — | — |
| FR-021 | ui | unverified | — | — | — |

### B5 — `007-service-record-baseline`

| Requirement | Class | Status | Evidence | Failing clause | In register |
| --- | --- | --- | --- | --- | --- |
| ALR-001 | ui | test-cited | `test_service_create_requires_asset_custody_manage_permission` | — | — |
| ALR-002 | backend | test-cited | `test_employee_sees_service_records_only_for_assets_it_holds` | — | — |
| ALR-003 | ui | test-cited | `test_service_create_requires_asset_custody_manage_permission` | — | — |
| ALR-004 | backend | unverified | — | — | — |
| ALR-005 | backend | partly-met | `test_closing_re_checks_that_the_asset_is_still_under_repair` | — | yes |
| ALR-006 | backend | test-cited | `test_a_negative_cost_is_rejected`, `test_close_service_rejects_an_already_closed_record`, `test_closing_without_a_cost_is_rejected`, `test_open_service_rejects_a_terminal_asset`, `test_open_service_rejects_an_asset_already_under_repair` | — | — |
| ALR-007 | backend | test-cited | `test_open_service_closes_the_open_checkout_it_interrupts` | — | — |
| ALR-008 | backend | unverified | — | — | — |
| ALR-009 | ui | unverified | — | — | — |
| FR-001 | ui | unverified | — | — | — |
| FR-002 | backend | unverified | — | — | — |
| FR-003 | backend | test-cited | `test_open_service_clears_custodian_and_marks_under_repair`, `test_service_open_and_close_round_trip` | — | — |
| FR-004 | backend | test-cited | `test_open_service_clears_custodian_and_marks_under_repair` | — | — |
| FR-005 | ui | partly-met | `test_opening_a_service_record_clears_the_department` | — | yes |
| FR-006 | backend | test-cited | `test_cannot_enter_under_repair_by_direct_edit`, `test_cannot_leave_under_repair_by_direct_edit` | — | — |
| FR-007 | backend | test-cited | `test_open_service_rejects_a_terminal_asset`, `test_open_service_rejects_an_asset_already_under_repair` | — | — |
| FR-008 | ui | partly-met | `test_an_in_storage_asset_is_refused_for_service`, `test_open_service_rejects_a_terminal_asset` | — | yes |
| FR-009 | backend | unverified | — | — | — |
| FR-010 | backend | partly-met | `test_close_service_returns_asset_to_available_without_reassigning_custodian`, `test_closing_re_checks_that_the_asset_is_still_under_repair`, `test_service_open_and_close_round_trip` | — | yes |
| FR-011 | ui | partly-met | `test_a_negative_cost_is_rejected`, `test_closing_without_a_cost_is_rejected`, `test_zero_cost_means_no_charge_and_is_accepted` | — | yes |
| FR-012 | ui | test-cited | `test_close_service_returns_asset_to_available_without_reassigning_custodian` | — | — |
| FR-013 | backend | test-cited | `test_close_service_rejects_an_already_closed_record` | — | — |
| FR-014 | backend | partly-met | `test_open_service_closes_the_open_checkout_it_interrupts` | — | yes |
| FR-015 | backend | partly-met | `test_an_interrupted_service_record_is_marked_as_such` | — | yes |
| FR-016 | backend | test-cited | `test_entering_terminal_status_closes_the_open_service_record` | — | — |
| FR-017 | backend | unverified | — | — | — |
| FR-018 | backend | unverified | — | — | — |
| FR-019 | backend | known-gap | — | — | yes |
| FR-020 | ui | unverified | — | — | — |
| FR-021 | ui | partly-met | `test_closing_notifies_every_custody_operator`, `test_open_service_notifies_the_previous_custodian` | — | yes |
| FR-022 | ui | partly-met | `test_closing_notifies_every_custody_operator` | — | yes |
| FR-023 | ui | known-gap | — | — | yes |
| FR-024 | governance | unverified | — | — | — |
| FR-025 | governance | unverified | — | — | — |
| FR-026 | ui | known-gap | — | — | yes |
| FR-028 | ui | known-gap | — | — | yes |
| FR-029 | ui | known-gap | — | — | yes |
| FR-030 | ui | partly-met | `test_closing_remarks_do_not_overwrite_the_reason_it_was_sent` | — | yes |
| FR-031 | ui | unverified | — | — | — |
| FR-032 | backend | unverified | — | — | — |
| FR-033 | ui | unverified | — | — | — |
| FR-034 | governance | unverified | — | — | — |
| FR-035 | ui | unverified | — | — | — |

### B6 — `002-procurement-vendor-catalog-baseline`

| Requirement | Class | Status | Evidence | Failing clause | In register |
| --- | --- | --- | --- | --- | --- |
| ALR-001 | ui | test-cited | `test_a_role_with_neither_code_is_denied` | — | — |
| ALR-002 | backend | test-cited | `test_a_reader_without_the_write_code_cannot_create_a_procurement`, `test_a_rejected_link_leaves_every_association_untouched`, `test_master_writes_require_settings_access` | — | — |
| ALR-003 | ui | test-cited | `ProtectedMasterDataTests`, `test_delete_api_returns_conflict_for_referenced_master_records`, `test_referenced_master_records_cannot_delete_operational_data` | — | — |
| ALR-004 | backend | unverified | — | — | — |
| ALR-005 | backend | unverified | — | — | — |
| ALR-006 | backend | unverified | — | — | — |
| ALR-007 | backend | unverified | — | — | — |
| ALR-008 | ui | unverified | — | — | — |
| ALR-009 | ui | unverified | — | — | — |
| FR-001 | backend | unverified | — | — | — |
| FR-002 | backend | unverified | — | — | — |
| FR-003 | backend | test-cited | `test_one_vendor_serves_both_procurement_and_service_record`, `test_procurement_references_a_managed_vendor_not_free_text` | — | — |
| FR-004 | ui | test-cited | `test_dates_in_the_accepted_order_are_recorded`, `test_procurement_references_a_managed_vendor_not_free_text` | — | — |
| FR-005 | backend | unverified | — | — | — |
| FR-006 | backend | test-cited | `ProtectedMasterDataTests`, `test_referenced_master_records_cannot_delete_operational_data` | — | — |
| FR-007 | backend | test-cited | `ProtectedMasterDataTests`, `test_a_brand_cannot_be_deleted_while_a_model_names_it`, `test_delete_api_returns_conflict_for_referenced_master_records`, `test_referenced_master_records_cannot_delete_operational_data` | — | — |
| FR-008 | backend | test-cited | `ProtectedMasterDataTests`, `test_unused_master_records_can_still_be_deleted` | — | — |
| FR-009 | backend | test-cited | `test_an_arrival_without_the_attestation_is_still_refused`, `test_an_attested_arrival_records_its_date_location_and_attester`, `test_saving_a_procurement_requires_an_arrival_record_and_attestation` | — | — |
| FR-010 | backend | test-cited | `test_a_future_purchase_date_is_rejected`, `test_a_purchase_date_after_the_invoice_date_is_rejected`, `test_dates_in_the_accepted_order_are_recorded` | — | — |
| FR-011 | backend | test-cited | `test_an_archived_procurement_leaves_the_working_list_but_stays_readable`, `test_removing_a_procurement_archives_it_rather_than_deleting_it` | — | — |
| FR-012 | backend | test-cited | `test_attaching_an_asset_records_who_did_it_and_why`, `test_detaching_an_asset_records_a_reason_and_a_history_entry` | — | — |
| FR-013 | backend | test-cited | `test_a_procurement_cannot_be_left_without_any_asset`, `test_an_asset_holds_at_most_one_current_procurement`, `test_linking_an_unlinked_asset_succeeds` | — | — |
| FR-014 | ui | unverified | — | — | — |
| FR-015 | ui | test-cited | `test_a_role_with_neither_code_is_denied`, `test_asset_view_may_read_master_data`, `test_employee_is_denied_procurement_entirely`, `test_settings_access_may_read_the_master_data_it_maintains`, `test_the_employee_role_gets_no_b6_surface` | — | — |
| FR-016 | backend | test-cited | `test_a_reader_without_the_write_code_cannot_create_a_procurement`, `test_master_writes_require_settings_access`, `test_settings_access_may_read_the_master_data_it_maintains` | — | — |
| FR-017 | backend | test-cited | `test_a_purchase_order_number_is_globally_unique_when_present`, `test_an_invoice_number_is_not_reused_for_the_same_vendor`, `test_several_procurements_may_omit_the_purchase_order_number`, `test_the_same_invoice_number_is_allowed_for_a_different_vendor` | — | — |
| FR-018 | backend | unverified | — | — | — |
| FR-019 | ui | test-cited | `test_a_stored_name_keeps_its_display_text_but_loses_stray_whitespace`, `test_each_master_type_rejects_a_duplicate_name`, `test_master_names_are_compared_case_insensitively_after_trimming`, `test_vendor_contact_details_are_optional_and_outside_identity` | — | — |
| FR-020 | backend | test-cited | `test_a_brand_cannot_be_deleted_while_a_model_names_it`, `test_a_model_belongs_to_exactly_one_brand`, `test_the_same_model_name_may_exist_under_two_brands` | — | — |
| FR-021 | ui | unverified | — | — | — |
| FR-022 | ui | unverified | — | — | — |
| FR-023 | backend | unverified | — | — | — |
| FR-024 | backend | unverified | — | — | — |

### B7 — `008-warranty-amc-baseline`

| Requirement | Class | Status | Evidence | Failing clause | In register |
| --- | --- | --- | --- | --- | --- |
| ALR-001 | ui | test-cited | `test_a_denied_renewal_leaves_every_contract_untouched` | — | — |
| ALR-002 | backend | partly-met | `test_a_failed_audit_write_rolls_back_the_end_support`, `test_a_failed_audit_write_rolls_back_the_renewal` | — | yes |
| ALR-003 | backend | partly-met | `test_a_denied_renewal_leaves_every_contract_untouched`, `test_end_amc_support_rejects_when_no_active_amc`, `test_end_amc_support_requires_a_reason`, `test_end_support_is_rejected_for_a_terminal_asset`, `test_renew_amc_rejects_a_terminal_asset`, `test_renew_amc_rejects_an_unparseable_date`, `test_renew_amc_rejects_end_before_start`, `test_renewal_is_rejected_for_a_terminal_asset_and_changes_nothing` | — | yes |
| ALR-004 | backend | partly-met | `test_renew_amc_ends_previous_contract_and_creates_new_one`, `test_renewal_preserves_the_superseded_contract_in_history`, `test_the_current_contract_is_chosen_by_dates_not_by_creation_order` | — | yes |
| ALR-005 | backend | test-cited | `test_a_lapsed_contract_stays_active_and_reads_as_expired_not_ended`, `test_the_expiry_sweep_changes_no_asset_and_no_contract` | — | — |
| ALR-006 | backend | test-cited | `test_the_expiry_sweep_changes_no_asset_and_no_contract` | — | — |
| ALR-007 | backend | partly-met | `test_a_failed_audit_write_rolls_back_the_end_support`, `test_a_failed_audit_write_rolls_back_the_renewal` | — | yes |
| ALR-008 | backend | test-cited | `test_a_denied_renewal_leaves_every_contract_untouched`, `test_reading_amc_history_requires_asset_view` | — | — |
| FR-001 | backend | test-cited | `test_an_asset_records_warranty_as_a_start_and_an_end_date`, `test_warranty_and_amc_are_separate_and_neither_is_derived_from_the_other` | — | — |
| FR-002 | backend | test-cited | `test_warranty_and_amc_are_separate_and_neither_is_derived_from_the_other` | — | — |
| FR-003 | backend | test-cited | `test_warranty_carries_no_status_and_no_lifecycle_workflow` | — | — |
| FR-004 | backend | test-cited | `test_amc_coverage_is_queryable_by_date_rather_than_only_a_document` | — | — |
| FR-005 | backend | partly-met | `test_incomplete_contract_created_after_an_ended_one_is_correctly_latest`, `test_the_current_contract_is_chosen_by_dates_not_by_creation_order` | — | yes |
| FR-006 | ui | partly-met | `AmcExpiryReportTests`, `test_has_amc_is_false_once_the_contract_is_ended`, `test_has_amc_is_true_while_a_contract_is_incomplete`, `test_incomplete_contract_created_after_an_ended_one_is_correctly_latest`, `test_renewing_after_an_ended_contract_reports_has_amc_again`, `test_report_does_not_crash_on_a_contract_ended_before_dates_were_entered` | — | yes |
| FR-007 | ui | test-cited | `test_checking_has_amc_without_dates_creates_an_incomplete_contract`, `test_has_amc_is_true_while_a_contract_is_incomplete` | — | — |
| FR-008 | backend | test-cited | `test_supplying_dates_later_completes_the_incomplete_contract` | — | — |
| FR-009 | backend | test-cited | `test_renew_amc_ends_previous_contract_and_creates_new_one`, `test_renew_amc_sets_dates_and_notifies_it_manager`, `test_renew_amc_supersedes_an_incomplete_contract` | — | — |
| FR-010 | backend | test-cited | `test_renew_amc_rejects_an_unparseable_date`, `test_renew_amc_rejects_end_before_start` | — | — |
| FR-011 | backend | partly-met | `test_end_support_is_rejected_for_a_terminal_asset`, `test_renew_amc_rejects_a_terminal_asset`, `test_renewal_is_rejected_for_a_terminal_asset_and_changes_nothing` | — | yes |
| FR-012 | backend | test-cited | `test_end_amc_support_can_end_an_incomplete_contract`, `test_end_amc_support_rejects_when_no_active_amc`, `test_end_amc_support_requires_a_reason`, `test_end_amc_support_sets_status_and_notifies_it_manager`, `test_the_end_support_notice_carries_the_recorded_reason` | — | — |
| FR-013 | backend | test-cited | `test_a_lapsed_contract_stays_active_and_reads_as_expired_not_ended` | — | — |
| FR-014 | backend | partly-met | `test_a_failed_audit_write_rolls_back_the_end_support`, `test_a_failed_audit_write_rolls_back_the_renewal` | — | yes |
| FR-015 | backend | test-cited | `test_renew_amc_ends_previous_contract_and_creates_new_one`, `test_renew_amc_supersedes_an_incomplete_contract`, `test_renewal_preserves_the_superseded_contract_in_history` | — | — |
| FR-016 | backend | test-cited | `test_a_date_short_of_a_threshold_is_silent`, `test_active_amc_at_a_threshold_notifies_recipients`, `test_warranty_at_a_threshold_notifies_recipients`, `test_warranty_not_at_a_threshold_is_silent` | — | — |
| FR-017 | ui | test-cited | `test_an_alert_is_delivered_in_app_and_addressed_to_a_specific_user`, `test_recipients_resolve_in_a_constant_number_of_queries`, `test_warranty_at_a_threshold_notifies_recipients` | — | — |
| FR-018 | ui | test-cited | `test_active_amc_at_a_threshold_notifies_recipients`, `test_warranty_at_a_threshold_notifies_recipients` | — | — |
| FR-019 | backend | test-cited | `test_ended_amc_at_a_threshold_is_silent` | — | — |
| FR-020 | ui | partly-met | `test_a_terminal_asset_generates_no_warranty_alert` | — | yes |
| FR-021 | ui | partly-met | `test_end_amc_support_sets_status_and_notifies_it_manager`, `test_only_active_holders_of_the_manager_grant_are_notified`, `test_renew_amc_sets_dates_and_notifies_it_manager`, `test_the_end_support_notice_carries_the_recorded_reason` | — | yes |
| FR-022 | ui | unverified | — | — | — |
| FR-023 | backend | test-cited | `test_reading_amc_history_requires_asset_view` | — | — |
| FR-024 | backend | known-gap | — | — | yes |
| FR-025 | backend | known-gap | — | — | yes |
| FR-026 | backend | test-cited | `test_a_service_record_neither_creates_nor_implies_amc_coverage` | — | — |
| FR-027 | governance | unverified | — | — | — |
| FR-028 | governance | unverified | — | — | — |
| FR-029 | governance | unverified | — | — | — |
| FR-030 | ui | partly-met | `test_initial_amc_entry_enforces_the_same_date_rules_as_renewal` | — | yes |
| FR-031 | ui | partly-met | `test_a_warranty_end_before_its_start_is_rejected` | — | yes |
| FR-032 | ui | partly-met | `test_initial_amc_entry_requires_a_managed_vendor_once_it_has_dates` | — | yes |
| FR-033 | backend | partly-met | `test_renew_amc_sets_dates_and_notifies_it_manager` | — | yes |
| FR-034 | ui | partly-met | `test_the_supersede_marker_is_held_apart_from_the_operator_reason` | — | yes |
| FR-035 | backend | test-cited | `test_an_alert_is_delivered_in_app_and_addressed_to_a_specific_user` | — | — |
| FR-036 | backend | test-cited | `test_a_warranty_start_alone_yields_no_alert_and_stays_distinguishable` | — | — |
| FR-037 | backend | test-cited | `test_renewing_after_an_ended_contract_reports_has_amc_again` | — | — |
| FR-038 | governance | unverified | — | — | — |
| FR-039 | backend | test-cited | `test_only_active_holders_of_the_manager_grant_are_notified` | — | — |

### B8 — `004-notifications-audit-baseline`

| Requirement | Class | Status | Evidence | Failing clause | In register |
| --- | --- | --- | --- | --- | --- |
| ALR-001 | backend | test-cited | `test_delivering_a_notification_changes_no_asset_state`, `test_the_facility_authorizes_nothing_of_its_own` | — | — |
| ALR-002 | backend | test-cited | `test_a_recipient_cannot_mark_another_users_notification_read`, `test_a_recipient_reads_only_their_own_notifications`, `test_the_facility_retains_a_notification_for_the_recipient_the_capability_chose`, `test_the_unread_count_counts_only_the_readers_own_unread_records` | — | — |
| ALR-003 | ui | test-cited | `test_an_admin_reads_the_audit_trail_globally`, `test_an_anonymous_request_reaches_no_audit_data`, `test_an_it_manager_reads_the_audit_trail_globally`, `test_an_ordinary_role_is_denied_at_the_data_boundary` | — | — |
| ALR-004 | backend | test-cited | `test_delivering_a_notification_changes_no_asset_state` | — | — |
| ALR-005 | ui | test-cited | `test_a_failed_audit_write_rejects_the_business_action`, `test_a_notification_failure_leaves_completed_business_work_intact` | — | — |
| ALR-006 | ui | test-cited | `test_an_anonymous_request_reaches_no_audit_data`, `test_an_ordinary_role_is_denied_at_the_data_boundary` | — | — |
| FR-001 | backend | test-cited | `test_delivery_to_an_absent_recipient_is_a_no_op_rather_than_an_error`, `test_the_facility_retains_a_notification_for_the_recipient_the_capability_chose` | — | — |
| FR-002 | backend | unverified | — | — | — |
| FR-003 | backend | test-cited | `test_an_asset_mutation_is_audited_and_raises_no_notification`, `test_an_asset_update_and_delete_are_each_audited_without_notifying` | — | — |
| FR-004 | backend | test-cited | `test_a_procurement_mutation_is_audited_and_raises_no_notification` | — | — |
| FR-005 | backend | unverified | — | — | — |
| FR-006 | ui | unverified | — | — | — |
| FR-007 | backend | test-cited | `test_the_audit_record_carries_no_physical_verification_semantics` | — | — |
| FR-008 | backend | test-cited | `test_delivering_a_notification_sends_no_email`, `test_group_delivery_sends_no_email_either` | — | — |
| FR-009 | governance | unverified | — | — | — |
| FR-010 | governance | unverified | — | — | — |
| FR-011 | backend | test-cited | `test_a_failed_audit_write_rejects_the_business_action` | — | — |
| FR-012 | backend | test-cited | `test_a_delivery_that_cannot_be_retained_stays_visible_to_an_operator`, `test_a_notification_failure_leaves_completed_business_work_intact`, `test_a_transient_delivery_failure_is_retried_without_duplicating` | — | — |
| FR-013 | ui | unverified | — | — | — |
| FR-014 | backend | test-cited | `test_a_catalog_master_mutation_is_audited`, `test_a_failed_login_is_audited`, `test_a_failed_login_records_the_attempt_without_the_password`, `test_a_procurement_mutation_is_audited_and_raises_no_notification`, `test_a_rejected_audit_access_is_itself_audited`, `test_an_asset_mutation_is_audited_and_raises_no_notification`, `test_an_asset_update_and_delete_are_each_audited_without_notifying`, `test_exporting_a_report_creates_an_audit_entry`, `test_notification_reads_create_no_audit_entries`, `test_reading_the_audit_report_is_itself_audited` | — | — |
| FR-015 | backend | test-cited | `test_a_failed_login_records_the_attempt_without_the_password`, `test_a_password_change_records_no_credential_material` | — | — |
| FR-016 | ui | test-cited | `test_a_rejected_audit_access_is_itself_audited`, `test_admin_reads_lists_and_exports_the_audit_report`, `test_an_admin_reads_the_audit_trail_globally`, `test_an_it_manager_reads_the_audit_trail_globally`, `test_report_access_alone_cannot_export_the_audit_report`, `test_report_access_alone_cannot_read_the_audit_report` | — | — |
| FR-017 | backend | test-cited | `test_an_audit_entry_outlives_its_actor`, `test_expired_records_are_purged_on_their_retention_schedule`, `test_notifications_are_removed_when_their_recipient_is_deleted`, `test_re_marking_a_read_notification_does_not_restart_its_retention_clock`, `test_the_retention_job_is_scheduled`, `test_the_time_a_notification_became_read_is_retained` | — | — |
| FR-018 | backend | unverified | — | — | — |
| FR-019 | ui | test-cited | `test_a_notification_is_created_unread`, `test_mark_all_read_clears_the_unread_count`, `test_marking_an_already_read_notification_is_idempotent`, `test_marking_read_moves_unread_to_read`, `test_no_operation_returns_a_read_notification_to_unread`, `test_re_marking_a_read_notification_does_not_restart_its_retention_clock`, `test_the_time_a_notification_became_read_is_retained`, `test_the_unread_count_counts_only_the_readers_own_unread_records` | — | — |
| FR-020 | ui | test-cited | `test_a_recipient_reads_only_their_own_notifications`, `test_an_empty_notification_list_is_a_normal_outcome` | — | — |
| FR-021 | backend | test-cited | `test_a_filter_matching_nothing_returns_empty_rather_than_everything`, `test_module_filtering_is_an_exact_match`, `test_results_are_ordered_newest_first`, `test_supplying_both_filters_narrows_to_entries_satisfying_both`, `test_username_filtering_is_case_insensitive_and_partial` | — | — |
| FR-022 | ui | test-cited | `test_a_truncated_audit_view_discloses_the_limit_and_the_omission` | — | — |
| FR-023 | ui | test-cited | `test_a_forwarded_header_is_honoured_from_a_configured_proxy`, `test_a_forwarded_header_is_not_trusted_from_an_untrusted_peer` | — | — |

### B9 — `009-dashboard-reports-exports-baseline`

| Requirement | Class | Status | Evidence | Failing clause | In register |
| --- | --- | --- | --- | --- | --- |
| ALR-001 | ui | partly-met | `test_an_unauthorized_reader_receives_neither_report_nor_export`, `test_anonymous_request_is_rejected`, `test_asset_viewer_may_read_dashboard_and_charts`, `test_both_export_formats_are_produced_server_side_under_authorization`, `test_csv_export_is_produced_server_side_like_the_other_formats`, `test_disabled_profile_is_denied_even_with_a_live_token`, `test_every_report_and_both_exports_are_authorized_server_side`, `test_revoked_token_no_longer_authenticates`, `test_unknown_chart_still_returns_404_for_a_permitted_reader`, `test_user_without_asset_view_is_denied` | — | yes |
| ALR-002 | backend | test-cited | `test_reading_the_audit_report_is_audited_while_ordinary_reports_write_nothing`, `test_reading_the_dashboard_and_charts_mutates_nothing`, `test_reading_the_dashboard_and_every_report_notifies_nobody`, `test_running_and_exporting_every_report_mutates_nothing` | — | — |
| ALR-003 | ui | partly-met | `test_a_reader_scoped_dashboard_counts_only_their_visible_assets` | — | yes |
| ALR-004 | backend | test-cited | `test_a_source_address_past_its_retention_window_is_not_presented`, `test_audit_report_content_follows_b8_access_rather_than_report_access` | — | — |
| ALR-005 | backend | partly-met | `test_an_unauthorized_reader_receives_neither_report_nor_export`, `test_both_export_formats_are_produced_server_side_under_authorization`, `test_csv_export_is_produced_server_side_like_the_other_formats`, `test_every_report_and_both_exports_are_authorized_server_side` | — | yes |
| ALR-006 | ui | test-cited | `test_a_chart_follows_the_same_mapping_as_the_dashboard`, `test_the_dashboard_requires_asset_view_and_reports_require_report_access` | — | — |
| FR-001 | backend | partly-met | `test_vendor_service_reporting_groups_by_vendor` | — | yes |
| FR-002 | backend | test-cited | `test_the_lost_report_presents_lost_assets_with_their_retained_custodian` | — | — |
| FR-003 | ui | partly-met | `test_no_report_claims_the_reserved_asset_audit_name` | — | yes |
| FR-004 | backend | test-cited | `test_reading_the_dashboard_and_every_report_notifies_nobody` | — | — |
| FR-005 | ui | partly-met | `test_a_transfer_with_no_previous_holder_gets_no_placeholder_identity`, `test_no_report_catalogue_entry_uses_the_rejected_assignment_term`, `test_report_does_not_crash_on_a_contract_ended_before_dates_were_entered`, `test_the_register_report_names_the_custodian_column_canonically`, `test_the_report_presents_no_status_the_source_baseline_does_not_define` | — | yes |
| FR-006 | ui | test-cited | `test_the_register_report_follows_the_status_the_source_baseline_owns`, `test_the_report_presents_no_status_the_source_baseline_does_not_define` | — | — |
| FR-007 | ui | partly-met | `test_a_reader_scoped_dashboard_counts_only_their_visible_assets`, `test_asset_viewer_may_read_dashboard_and_charts`, `test_employee_dashboard_counts_only_its_own_assets`, `test_the_dashboard_requires_asset_view_and_reports_require_report_access`, `test_user_without_asset_view_is_denied` | — | yes |
| FR-008 | ui | partly-met | `test_audit_report_content_follows_b8_access_rather_than_report_access`, `test_ordinary_reports_remain_open_to_report_access`, `test_report_access_alone_cannot_export_the_audit_report`, `test_report_access_alone_cannot_read_the_audit_report`, `test_the_audit_report_is_hidden_from_the_catalog_it_cannot_open` | — | yes |
| FR-009 | ui | partly-met | `test_a_rejected_audit_report_read_is_itself_audited`, `test_exporting_a_report_creates_an_audit_entry`, `test_reading_the_audit_report_is_audited_while_ordinary_reports_write_nothing`, `test_reading_the_audit_report_is_itself_audited` | — | yes |
| FR-010 | backend | partly-met | `test_a_source_address_past_its_retention_window_is_not_presented` | — | yes |
| FR-011 | backend | test-cited | `test_the_transfer_custody_document_is_not_a_b9_report` | — | — |
| FR-012 | ui | test-cited | `test_a_chart_follows_the_same_mapping_as_the_dashboard`, `test_every_report_and_both_exports_are_authorized_server_side`, `test_the_dashboard_requires_asset_view_and_reports_require_report_access` | — | — |
| FR-013 | ui | test-cited | `test_reading_the_dashboard_and_charts_mutates_nothing`, `test_running_and_exporting_every_report_mutates_nothing` | — | — |
| FR-014 | governance | unverified | — | — | — |
| FR-015 | governance | unverified | — | — | — |
| FR-016 | ui | test-cited | `test_a_reader_scoped_dashboard_counts_only_their_visible_assets` | — | — |
| FR-017 | ui | partly-met | `test_total_value_counts_only_assets_the_organization_still_holds` | — | yes |
| FR-018 | ui | partly-met | `test_one_asset_appears_in_exactly_one_expiry_band` | — | yes |
| FR-019 | ui | test-cited | `test_one_asset_appears_in_exactly_one_expiry_band` | — | — |
| FR-020 | ui | test-cited | `test_total_value_counts_only_assets_the_organization_still_holds` | — | — |
| FR-021 | ui | test-cited | `test_a_report_with_no_matching_records_returns_an_empty_row_set` | — | — |
| FR-022 | backend | test-cited | `test_a_transfer_with_no_previous_holder_gets_no_placeholder_identity` | — | — |
| FR-023 | governance | test-cited | `test_no_report_claims_the_reserved_asset_audit_name` | — | — |

## How to use this

1. **Tag as you write.** Every new test gets a `Covers:` line; the map regenerates.
2. **Record a gap as `expectedFailure`, not an omission** — the requirement stays
   executable and the runner tells you when it starts passing.
3. **Work the backend column in risk order** — authorization and privacy, then
   lifecycle integrity, then audit and retention, then presentation.
4. **Translate the acceptance scenarios.** 290 Given/When/Then cases are written.
5. **Reconcile as you go.** A failing test whose requirement is *not* in a gap
   register means the register was incomplete.
6. **Decide the UI question separately** — the `ui` rows need a frontend runner.
