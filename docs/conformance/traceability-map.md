# Conformance Traceability Map

**Generated**: 2026-08-12 · **Source**: `Covers:` tags in `backend/*/tests.py`, plus the nine AS-BUILT baselines under `specs/`
**Regenerate**: `python docs/conformance/build-traceability-map.py`

## What this answers, and what it does not

One question per requirement: **can we currently demonstrate that the system does what
the baseline says?**

Evidence is read from `Covers: B<n> FR-xxx` tags in the test docstrings, then from each
baseline's §Verified Behavior Evidence. **The tags are the authoritative direction.** Once
a baseline is accepted its requirement content is immutable under Constitution III, so a
test written afterwards could never be recorded in that baseline's evidence section —
tagging the test keeps this map regenerable for the life of the project.

It does **not** read application code to judge conformance. `test-cited` means a tagged
test exists and passes; it does not re-verify that the test proves the whole requirement.

## Status vocabulary

| Status | Meaning |
| --- | --- |
| `test-cited` | A tagged automated test demonstrates it. |
| `known-gap` | Named in a conformance-gap register (U-005/U-006/U-007). The system is known **not** to satisfy it. |
| `unverified` | Neither — conformance is unknown. |

## Verifiability classes

| Class | Count | Automatable today? |
| --- | --- | --- |
| `backend` | 181 | **Yes** — the actionable set. |
| `ui` | 94 | **No** — no frontend runner is configured. |
| `governance` | 16 | **No, and never** — requirements about the specification itself. |

Classification is heuristic from requirement wording; treat boundary cases as a first
pass to review.

## Headline numbers

- **291 requirements** across the nine baselines.
- **104 test-cited · 55 known-gap · 132 unverified.**
- Of the **181 backend** requirements automatable today:
  **77 test-cited · 24 known-gap · 80 unverified**.

**43% of the automatable set is demonstrated**, from 8% at the start.
Three moves got it there: tagging the existing suite (+69, no new tests), then writing
conformance suites for B8 (+10) and B9 (+7) — the two weakest baselines.

Seven tests are marked `expectedFailure`. They document requirements the code does not
satisfy — the Notification read timestamp, forwarded-header trust, the absent retention
job, server-side CSV, terminal-Asset exclusion, disjoint expiry bands, and the "Owner"
column heading — so the suite stays green against known gaps while the runner reports an
unexpected success the moment one is fixed.

## Per baseline

| Baseline | Total | backend | test-cited | known-gap | unverified |
| --- | --- | --- | --- | --- | --- |
| B1 `003-identity-access-baseline` | 18 | 12 | 13 | 0 | 5 |
| B6 `002-procurement-vendor-catalog-baseline` | 33 | 23 | 7 | 0 | 26 |
| B2 `001-asset-register-lifecycle-baseline` | 26 | 24 | 15 | 0 | 11 |
| B8 `004-notifications-audit-baseline` | 29 | 17 | 12 | 0 | 17 |
| B3 `005-checkout-checkin-baseline` | 38 | 24 | 11 | 14 | 13 |
| B4 `006-transfer-baseline` | 28 | 20 | 16 | 0 | 12 |
| B5 `007-service-record-baseline` | 43 | 21 | 12 | 15 | 16 |
| B7 `008-warranty-amc-baseline` | 47 | 31 | 11 | 14 | 22 |
| B9 `009-dashboard-reports-exports-baseline` | 29 | 9 | 7 | 12 | 10 |

**B6 is now the weakest** at 7 cited against 26 unverified — the Procurement and
catalog-master rules, most of which were specified in the 2026-08-03/04 clarifications
and never had tests written toward them.

## Full map

### B1 — `003-identity-access-baseline`

| Requirement | Class | Status | Evidence |
| --- | --- | --- | --- |
| ALR-001 | ui | test-cited | `test_a_profile_without_a_login_account_can_be_disabled`, `test_an_active_profile_keeps_its_token`, `test_disabled_profile_is_denied_even_with_a_live_token`, `test_disabling_outside_the_api_revokes_the_token`, `test_disabling_through_the_api_revokes_the_token`, `test_revoked_token_no_longer_authenticates` |
| ALR-002 | ui | test-cited | `PrivacyAuthorizationTests`, `test_ordinary_user_cannot_read_privileged_apis`, `test_settings_access_does_not_expose_admin_configuration` |
| ALR-003 | backend | test-cited | `PrivacyAuthorizationTests`, `test_asset_user_gets_only_minimal_active_user_directory` |
| ALR-004 | backend | unverified | — |
| ALR-005 | ui | test-cited | `test_employee_cannot_download_someone_elses_transfer_document`, `test_employee_cannot_reach_another_holders_asset_by_id`, `test_employee_is_denied_the_user_directory`, `test_user_manager_can_read_full_user_records` |
| FR-001 | backend | test-cited | `PrivacyAuthorizationTests`, `test_a_common_password_is_rejected_even_though_it_is_long_enough`, `test_a_strong_password_is_accepted`, `test_ordinary_user_cannot_read_privileged_apis` |
| FR-002 | backend | test-cited | `PrivacyAuthorizationTests`, `test_user_manager_can_read_full_user_records` |
| FR-003 | backend | test-cited | `PrivacyAuthorizationTests`, `test_asset_user_gets_only_minimal_active_user_directory` |
| FR-004 | backend | test-cited | `PrivacyAuthorizationTests`, `test_asset_user_gets_only_minimal_active_user_directory` |
| FR-005 | backend | test-cited | `PrivacyAuthorizationTests`, `test_settings_access_does_not_expose_admin_configuration` |
| FR-006 | backend | test-cited | `CheckoutTransferEndpointTests`, `ServiceRecordEndpointTests`, `test_checkout_create_requires_asset_custody_manage_permission`, `test_service_create_requires_asset_custody_manage_permission` |
| FR-007 | backend | test-cited | `CheckoutTransferEndpointTests`, `test_transfer_request_requires_transfer_request_permission` |
| FR-008 | backend | test-cited | `test_employee_sees_only_assets_it_holds` |
| FR-009 | ui | unverified | — |
| FR-010 | backend | unverified | — |
| FR-011 | backend | unverified | — |
| FR-012 | governance | test-cited | `test_a_global_reader_still_sees_every_record`, `test_a_non_employee_role_still_reads_globally`, `test_employee_dashboard_counts_only_its_own_assets`, `test_employee_is_denied_procurement_entirely`, `test_employee_is_denied_the_user_directory`, `test_employee_lists_only_transfers_it_is_party_to`, `test_employee_may_download_the_document_for_a_transfer_it_is_party_to`, `test_employee_sees_files_only_for_assets_it_holds`, `test_employee_sees_only_assets_it_holds`, `test_employee_sees_only_its_own_checkouts`, `test_employee_sees_service_records_only_for_assets_it_holds`, `test_the_employee_role_gets_no_b6_surface` |
| FR-013 | ui | unverified | — |

### B6 — `002-procurement-vendor-catalog-baseline`

| Requirement | Class | Status | Evidence |
| --- | --- | --- | --- |
| ALR-001 | ui | test-cited | `test_a_role_with_neither_code_is_denied` |
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
| FR-015 | ui | test-cited | `test_a_role_with_neither_code_is_denied`, `test_asset_view_may_read_master_data`, `test_employee_is_denied_procurement_entirely`, `test_settings_access_may_read_the_master_data_it_maintains`, `test_the_employee_role_gets_no_b6_surface` |
| FR-016 | backend | test-cited | `test_settings_access_may_read_the_master_data_it_maintains` |
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
| ALR-004 | backend | test-cited | `CheckoutLifecycleTests`, `CheckoutTransferEndpointTests`, `test_approve_reassigns_custodian_department_and_condition`, `test_cannot_enter_assigned_by_direct_edit`, `test_cannot_leave_assigned_by_direct_edit`, `test_cannot_move_directly_between_assigned_and_under_repair` |
| ALR-005 | backend | test-cited | `ServiceRecordEndpointTests`, `ServiceRecordLifecycleTests`, `test_cannot_enter_under_repair_by_direct_edit`, `test_cannot_leave_under_repair_by_direct_edit`, `test_cannot_move_directly_between_assigned_and_under_repair`, `test_open_service_clears_custodian_and_marks_under_repair` |
| ALR-006 | backend | test-cited | `AssetStatusTransitionTests`, `test_cannot_reverse_out_of_a_terminal_status`, `test_entering_lost_retains_custodian_even_if_payload_clears_it`, `test_entering_sold_clears_custodian_even_if_payload_keeps_it`, `test_entering_terminal_status_closes_the_open_checkout`, `test_entering_terminal_status_closes_the_open_service_record` |
| ALR-007 | backend | test-cited | `test_create_rejects_a_custodian`, `test_create_rejects_a_lifecycle_managed_status`, `test_edit_cannot_assign_a_custodian_directly` |
| ALR-008 | backend | unverified | — |
| ALR-009 | backend | test-cited | `test_a_non_employee_role_still_reads_globally`, `test_employee_cannot_reach_another_holders_asset_by_id`, `test_employee_sees_only_assets_it_holds` |
| ALR-010 | backend | unverified | — |
| ALR-011 | ui | unverified | — |
| FR-001 | backend | unverified | — |
| FR-002 | backend | test-cited | `test_administrative_status_edits_are_unaffected`, `test_editing_unrelated_fields_without_a_status_change_is_unaffected` |
| FR-003 | backend | unverified | — |
| FR-004 | backend | unverified | — |
| FR-005 | backend | unverified | — |
| FR-006 | backend | test-cited | `test_approve_reassigns_custodian_department_and_condition`, `test_check_in_returns_asset_to_available_with_new_condition`, `test_check_out_assigns_asset_to_user_and_their_department` |
| FR-007 | backend | test-cited | `test_close_service_returns_asset_to_available_without_reassigning_custodian`, `test_open_service_clears_custodian_and_marks_under_repair` |
| FR-008 | backend | test-cited | `test_cannot_reverse_out_of_a_terminal_status` |
| FR-009 | backend | test-cited | `test_entering_lost_retains_custodian_even_if_payload_clears_it`, `test_entering_sold_clears_custodian_even_if_payload_keeps_it`, `test_marking_an_asset_lost_still_retains_its_custodian` |
| FR-010 | backend | unverified | — |
| FR-011 | backend | test-cited | `test_check_in_rejects_an_invalid_condition` |
| FR-012 | backend | test-cited | `test_cannot_enter_assigned_by_direct_edit`, `test_cannot_enter_under_repair_by_direct_edit`, `test_cannot_leave_assigned_by_direct_edit`, `test_cannot_leave_under_repair_by_direct_edit`, `test_cannot_move_directly_between_assigned_and_under_repair` |
| FR-013 | backend | test-cited | `test_create_rejects_a_custodian`, `test_create_rejects_a_lifecycle_managed_status`, `test_create_still_accepts_available_and_in_storage` |
| FR-014 | backend | test-cited | `test_disposal_is_still_allowed_directly_from_assigned`, `test_lost_is_still_allowed_directly_from_under_repair` |
| FR-015 | backend | test-cited | `test_check_in_clears_department_and_logs_the_inspection` |

### B8 — `004-notifications-audit-baseline`

| Requirement | Class | Status | Evidence |
| --- | --- | --- | --- |
| ALR-001 | backend | test-cited | `test_delivering_a_notification_changes_no_asset_state` |
| ALR-002 | backend | test-cited | `test_a_recipient_cannot_mark_another_users_notification_read`, `test_a_recipient_reads_only_their_own_notifications`, `test_the_unread_count_counts_only_the_readers_own_unread_records` |
| ALR-003 | ui | unverified | — |
| ALR-004 | backend | test-cited | `test_delivering_a_notification_changes_no_asset_state` |
| ALR-005 | ui | unverified | — |
| ALR-006 | ui | unverified | — |
| FR-001 | backend | unverified | — |
| FR-002 | backend | unverified | — |
| FR-003 | backend | unverified | — |
| FR-004 | backend | unverified | — |
| FR-005 | backend | unverified | — |
| FR-006 | ui | unverified | — |
| FR-007 | backend | unverified | — |
| FR-008 | backend | test-cited | `test_delivering_a_notification_sends_no_email`, `test_group_delivery_sends_no_email_either` |
| FR-009 | governance | unverified | — |
| FR-010 | governance | unverified | — |
| FR-011 | backend | unverified | — |
| FR-012 | backend | unverified | — |
| FR-013 | ui | unverified | — |
| FR-014 | backend | test-cited | `test_a_failed_login_records_the_attempt_without_the_password`, `test_exporting_a_report_creates_an_audit_entry`, `test_reading_the_audit_report_is_itself_audited` |
| FR-015 | backend | test-cited | `test_a_failed_login_records_the_attempt_without_the_password`, `test_a_password_change_records_no_credential_material` |
| FR-016 | ui | test-cited | `test_admin_reads_lists_and_exports_the_audit_report`, `test_report_access_alone_cannot_export_the_audit_report`, `test_report_access_alone_cannot_read_the_audit_report` |
| FR-017 | backend | test-cited | `test_an_audit_entry_outlives_its_actor`, `test_expired_records_are_purged_on_their_retention_schedule`, `test_notifications_are_removed_when_their_recipient_is_deleted`, `test_the_time_a_notification_became_read_is_retained` |
| FR-018 | backend | unverified | — |
| FR-019 | ui | test-cited | `test_a_notification_is_created_unread`, `test_mark_all_read_clears_the_unread_count`, `test_marking_an_already_read_notification_is_idempotent`, `test_marking_read_moves_unread_to_read`, `test_the_time_a_notification_became_read_is_retained`, `test_the_unread_count_counts_only_the_readers_own_unread_records` |
| FR-020 | ui | test-cited | `test_a_recipient_reads_only_their_own_notifications`, `test_an_empty_notification_list_is_a_normal_outcome` |
| FR-021 | backend | test-cited | `test_a_filter_matching_nothing_returns_empty_rather_than_everything`, `test_module_filtering_is_an_exact_match`, `test_results_are_ordered_newest_first`, `test_supplying_both_filters_narrows_to_entries_satisfying_both`, `test_username_filtering_is_case_insensitive_and_partial` |
| FR-022 | ui | unverified | — |
| FR-023 | ui | test-cited | `test_a_forwarded_header_is_not_trusted_from_an_untrusted_peer` |

### B3 — `005-checkout-checkin-baseline`

| Requirement | Class | Status | Evidence |
| --- | --- | --- | --- |
| ALR-001 | ui | test-cited | `test_checkout_create_requires_asset_custody_manage_permission` |
| ALR-002 | backend | unverified | — |
| ALR-003 | ui | test-cited | `test_checkout_create_requires_asset_custody_manage_permission` |
| ALR-004 | backend | test-cited | `test_check_in_rejects_an_already_closed_checkout`, `test_check_in_rejects_an_invalid_condition`, `test_check_in_requires_a_return_condition`, `test_check_out_rejects_an_unavailable_asset` |
| ALR-005 | ui | known-gap | — |
| ALR-006 | ui | unverified | — |
| ALR-007 | backend | unverified | — |
| ALR-008 | ui | unverified | — |
| FR-001 | backend | known-gap | `test_check_out_assigns_asset_to_user_and_their_department`, `test_checkout_create_and_checkin_round_trip` |
| FR-002 | backend | test-cited | `test_check_in_returns_asset_to_available_with_new_condition`, `test_checkout_create_and_checkin_round_trip` |
| FR-003 | backend | unverified | — |
| FR-004 | backend | test-cited | `test_check_out_assigns_asset_to_user_and_their_department` |
| FR-005 | backend | unverified | — |
| FR-006 | backend | known-gap | `test_check_out_assigns_asset_to_user_and_their_department` |
| FR-007 | backend | known-gap | `test_cannot_enter_assigned_by_direct_edit`, `test_cannot_leave_assigned_by_direct_edit` |
| FR-008 | backend | test-cited | `test_check_out_rejects_an_unavailable_asset` |
| FR-009 | backend | test-cited | `test_check_in_rejects_an_already_closed_checkout` |
| FR-010 | backend | test-cited | `test_check_in_rejects_an_invalid_condition` |
| FR-011 | backend | known-gap | — |
| FR-012 | backend | test-cited | `test_check_in_rejects_an_already_closed_checkout` |
| FR-013 | ui | unverified | — |
| FR-014 | ui | known-gap | `test_an_interrupting_closure_also_preserves_intake_remarks`, `test_check_in_returns_asset_to_available_with_new_condition`, `test_check_out_persists_intake_remarks` |
| FR-015 | backend | test-cited | `test_open_service_closes_the_open_checkout_it_interrupts` |
| FR-016 | backend | test-cited | `test_entering_terminal_status_closes_the_open_checkout` |
| FR-017 | backend | unverified | — |
| FR-018 | ui | known-gap | — |
| FR-019 | backend | unverified | — |
| FR-020 | ui | known-gap | `test_check_out_notifies_the_new_custodian` |
| FR-021 | governance | unverified | — |
| FR-022 | governance | unverified | — |
| FR-023 | backend | known-gap | `test_check_in_clears_department_and_logs_the_inspection`, `test_check_in_returns_asset_to_available_with_new_condition` |
| FR-024 | backend | known-gap | `test_check_in_requires_a_return_condition` |
| FR-025 | backend | known-gap | `test_check_in_clears_department_and_logs_the_inspection` |
| FR-026 | ui | known-gap | — |
| FR-027 | backend | known-gap | — |
| FR-028 | backend | known-gap | `test_an_interrupting_closure_also_preserves_intake_remarks`, `test_open_service_closes_the_open_checkout_it_interrupts` |
| FR-029 | ui | unverified | — |
| FR-030 | ui | unverified | — |

### B4 — `006-transfer-baseline`

| Requirement | Class | Status | Evidence |
| --- | --- | --- | --- |
| ALR-001 | ui | test-cited | `test_transfer_request_requires_transfer_request_permission` |
| ALR-002 | backend | test-cited | `test_approve_reassigns_custodian_department_and_condition` |
| ALR-003 | backend | test-cited | `test_approve_rejects_an_already_processed_transfer`, `test_approve_rejects_an_asset_sent_for_service_after_the_request`, `test_approve_rejects_an_asset_that_turned_terminal_after_the_request`, `test_reject_leaves_the_asset_untouched`, `test_reject_rejects_an_already_processed_transfer`, `test_request_transfer_rejects_a_terminal_asset`, `test_request_transfer_rejects_an_asset_under_repair` |
| ALR-004 | backend | test-cited | `test_approve_rejects_an_already_processed_transfer`, `test_reject_rejects_an_already_processed_transfer` |
| ALR-005 | backend | unverified | — |
| ALR-006 | backend | unverified | — |
| ALR-007 | ui | test-cited | `test_a_new_request_is_allowed_once_the_previous_one_is_decided`, `test_transfer_rejects_a_second_pending_request`, `test_transfer_rejects_the_current_custodian_as_target` |
| FR-001 | backend | test-cited | `test_transfer_rejects_the_current_custodian_as_target` |
| FR-002 | backend | test-cited | `test_transfer_request_requires_transfer_request_permission` |
| FR-003 | backend | unverified | — |
| FR-004 | backend | test-cited | `test_a_non_employee_role_still_sees_every_transfer`, `test_employee_lists_only_transfers_it_is_party_to` |
| FR-005 | backend | test-cited | `TransferLifecycleTests`, `test_request_transfer_captures_the_current_owner_and_department`, `test_transfer_rejects_a_second_pending_request`, `test_transfer_request_and_approve_round_trip` |
| FR-006 | ui | unverified | — |
| FR-007 | backend | test-cited | `test_request_transfer_captures_the_current_owner_and_department` |
| FR-008 | backend | test-cited | `test_approve_reassigns_custodian_department_and_condition`, `test_reject_leaves_the_asset_untouched`, `test_transfer_reject_round_trip`, `test_transfer_request_and_approve_round_trip` |
| FR-009 | backend | test-cited | `test_request_transfer_rejects_a_terminal_asset`, `test_request_transfer_rejects_an_asset_under_repair` |
| FR-010 | backend | test-cited | `test_approve_rejects_an_asset_sent_for_service_after_the_request`, `test_approve_rejects_an_asset_that_turned_terminal_after_the_request` |
| FR-011 | backend | unverified | — |
| FR-012 | backend | unverified | — |
| FR-013 | backend | unverified | — |
| FR-014 | ui | unverified | — |
| FR-015 | backend | test-cited | `test_asset_view_holder_may_download_the_transfer_document`, `test_employee_cannot_download_someone_elses_transfer_document`, `test_employee_may_download_the_document_for_a_transfer_it_is_party_to` |
| FR-016 | backend | test-cited | `test_request_transfer_notifies_users_with_approval_permission` |
| FR-017 | ui | test-cited | `test_request_transfer_notifies_users_with_approval_permission` |
| FR-018 | backend | unverified | — |
| FR-019 | governance | unverified | — |
| FR-020 | ui | unverified | — |
| FR-021 | ui | unverified | — |

### B5 — `007-service-record-baseline`

| Requirement | Class | Status | Evidence |
| --- | --- | --- | --- |
| ALR-001 | ui | test-cited | `test_service_create_requires_asset_custody_manage_permission` |
| ALR-002 | backend | test-cited | `test_employee_sees_service_records_only_for_assets_it_holds` |
| ALR-003 | ui | test-cited | `test_service_create_requires_asset_custody_manage_permission` |
| ALR-004 | backend | unverified | — |
| ALR-005 | backend | known-gap | — |
| ALR-006 | backend | test-cited | `test_a_negative_cost_is_rejected`, `test_close_service_rejects_an_already_closed_record`, `test_closing_without_a_cost_is_rejected`, `test_open_service_rejects_a_terminal_asset`, `test_open_service_rejects_an_asset_already_under_repair` |
| ALR-007 | backend | test-cited | `test_open_service_closes_the_open_checkout_it_interrupts` |
| ALR-008 | backend | unverified | — |
| ALR-009 | ui | unverified | — |
| FR-001 | ui | unverified | — |
| FR-002 | backend | unverified | — |
| FR-003 | backend | test-cited | `test_open_service_clears_custodian_and_marks_under_repair`, `test_service_open_and_close_round_trip` |
| FR-004 | backend | test-cited | `test_open_service_clears_custodian_and_marks_under_repair` |
| FR-005 | ui | known-gap | — |
| FR-006 | backend | test-cited | `test_cannot_enter_under_repair_by_direct_edit`, `test_cannot_leave_under_repair_by_direct_edit` |
| FR-007 | backend | test-cited | `test_open_service_rejects_a_terminal_asset`, `test_open_service_rejects_an_asset_already_under_repair` |
| FR-008 | ui | known-gap | `test_open_service_rejects_a_terminal_asset` |
| FR-009 | backend | unverified | — |
| FR-010 | backend | known-gap | `test_close_service_returns_asset_to_available_without_reassigning_custodian`, `test_service_open_and_close_round_trip` |
| FR-011 | ui | known-gap | `test_a_negative_cost_is_rejected`, `test_closing_without_a_cost_is_rejected`, `test_zero_cost_means_no_charge_and_is_accepted` |
| FR-012 | ui | test-cited | `test_close_service_returns_asset_to_available_without_reassigning_custodian` |
| FR-013 | backend | test-cited | `test_close_service_rejects_an_already_closed_record` |
| FR-014 | backend | known-gap | `test_open_service_closes_the_open_checkout_it_interrupts` |
| FR-015 | backend | known-gap | — |
| FR-016 | backend | test-cited | `test_entering_terminal_status_closes_the_open_service_record` |
| FR-017 | backend | unverified | — |
| FR-018 | backend | unverified | — |
| FR-019 | backend | known-gap | — |
| FR-020 | ui | unverified | — |
| FR-021 | ui | known-gap | `test_closing_notifies_every_custody_operator`, `test_open_service_notifies_the_previous_custodian` |
| FR-022 | ui | known-gap | `test_closing_notifies_every_custody_operator` |
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
| ALR-003 | backend | known-gap | `test_end_amc_support_rejects_when_no_active_amc`, `test_end_amc_support_requires_a_reason`, `test_renew_amc_rejects_a_terminal_asset`, `test_renew_amc_rejects_an_unparseable_date`, `test_renew_amc_rejects_end_before_start` |
| ALR-004 | backend | known-gap | `test_renew_amc_ends_previous_contract_and_creates_new_one` |
| ALR-005 | backend | unverified | — |
| ALR-006 | backend | unverified | — |
| ALR-007 | backend | unverified | — |
| ALR-008 | backend | unverified | — |
| FR-001 | backend | unverified | — |
| FR-002 | backend | unverified | — |
| FR-003 | backend | unverified | — |
| FR-004 | backend | unverified | — |
| FR-005 | backend | known-gap | `test_incomplete_contract_created_after_an_ended_one_is_correctly_latest` |
| FR-006 | ui | known-gap | `AmcExpiryReportTests`, `test_has_amc_is_false_once_the_contract_is_ended`, `test_has_amc_is_true_while_a_contract_is_incomplete`, `test_incomplete_contract_created_after_an_ended_one_is_correctly_latest`, `test_renewing_after_an_ended_contract_reports_has_amc_again`, `test_report_does_not_crash_on_a_contract_ended_before_dates_were_entered` |
| FR-007 | ui | test-cited | `test_checking_has_amc_without_dates_creates_an_incomplete_contract`, `test_has_amc_is_true_while_a_contract_is_incomplete` |
| FR-008 | backend | test-cited | `test_supplying_dates_later_completes_the_incomplete_contract` |
| FR-009 | backend | test-cited | `test_renew_amc_ends_previous_contract_and_creates_new_one`, `test_renew_amc_sets_dates_and_notifies_it_manager`, `test_renew_amc_supersedes_an_incomplete_contract` |
| FR-010 | backend | test-cited | `test_renew_amc_rejects_an_unparseable_date`, `test_renew_amc_rejects_end_before_start` |
| FR-011 | backend | known-gap | `test_renew_amc_rejects_a_terminal_asset` |
| FR-012 | backend | test-cited | `test_end_amc_support_can_end_an_incomplete_contract`, `test_end_amc_support_rejects_when_no_active_amc`, `test_end_amc_support_requires_a_reason`, `test_end_amc_support_sets_status_and_notifies_it_manager` |
| FR-013 | backend | unverified | — |
| FR-014 | backend | unverified | — |
| FR-015 | backend | test-cited | `test_renew_amc_ends_previous_contract_and_creates_new_one`, `test_renew_amc_supersedes_an_incomplete_contract` |
| FR-016 | backend | test-cited | `test_active_amc_at_a_threshold_notifies_recipients`, `test_warranty_at_a_threshold_notifies_recipients`, `test_warranty_not_at_a_threshold_is_silent` |
| FR-017 | ui | test-cited | `test_recipients_resolve_in_a_constant_number_of_queries`, `test_warranty_at_a_threshold_notifies_recipients` |
| FR-018 | ui | test-cited | `test_active_amc_at_a_threshold_notifies_recipients`, `test_warranty_at_a_threshold_notifies_recipients` |
| FR-019 | backend | test-cited | `test_ended_amc_at_a_threshold_is_silent` |
| FR-020 | ui | known-gap | — |
| FR-021 | ui | known-gap | `test_end_amc_support_sets_status_and_notifies_it_manager`, `test_renew_amc_sets_dates_and_notifies_it_manager` |
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
| FR-033 | backend | known-gap | `test_renew_amc_sets_dates_and_notifies_it_manager` |
| FR-034 | ui | known-gap | — |
| FR-035 | backend | unverified | — |
| FR-036 | backend | unverified | — |
| FR-037 | backend | test-cited | `test_renewing_after_an_ended_contract_reports_has_amc_again` |
| FR-038 | governance | unverified | — |
| FR-039 | backend | unverified | — |

### B9 — `009-dashboard-reports-exports-baseline`

| Requirement | Class | Status | Evidence |
| --- | --- | --- | --- |
| ALR-001 | ui | known-gap | `test_an_unauthorized_reader_receives_neither_report_nor_export`, `test_anonymous_request_is_rejected`, `test_asset_viewer_may_read_dashboard_and_charts`, `test_both_export_formats_are_produced_server_side_under_authorization`, `test_csv_export_is_produced_server_side_like_the_other_formats`, `test_disabled_profile_is_denied_even_with_a_live_token`, `test_revoked_token_no_longer_authenticates`, `test_unknown_chart_still_returns_404_for_a_permitted_reader`, `test_user_without_asset_view_is_denied` |
| ALR-002 | backend | test-cited | `test_reading_the_dashboard_and_charts_mutates_nothing`, `test_running_and_exporting_every_report_mutates_nothing` |
| ALR-003 | ui | known-gap | `test_a_reader_scoped_dashboard_counts_only_their_visible_assets` |
| ALR-004 | backend | unverified | — |
| ALR-005 | backend | known-gap | `test_an_unauthorized_reader_receives_neither_report_nor_export`, `test_both_export_formats_are_produced_server_side_under_authorization`, `test_csv_export_is_produced_server_side_like_the_other_formats` |
| ALR-006 | ui | unverified | — |
| FR-001 | backend | known-gap | `test_vendor_service_reporting_groups_by_vendor` |
| FR-002 | backend | test-cited | `test_the_lost_report_presents_lost_assets_with_their_retained_custodian` |
| FR-003 | ui | known-gap | — |
| FR-004 | backend | unverified | — |
| FR-005 | ui | known-gap | `test_no_report_catalogue_entry_uses_the_rejected_assignment_term`, `test_report_does_not_crash_on_a_contract_ended_before_dates_were_entered`, `test_the_register_report_names_the_custodian_column_canonically` |
| FR-006 | ui | unverified | — |
| FR-007 | ui | known-gap | `test_a_reader_scoped_dashboard_counts_only_their_visible_assets`, `test_asset_viewer_may_read_dashboard_and_charts`, `test_employee_dashboard_counts_only_its_own_assets`, `test_user_without_asset_view_is_denied` |
| FR-008 | ui | known-gap | `test_ordinary_reports_remain_open_to_report_access`, `test_report_access_alone_cannot_export_the_audit_report`, `test_report_access_alone_cannot_read_the_audit_report`, `test_the_audit_report_is_hidden_from_the_catalog_it_cannot_open` |
| FR-009 | ui | known-gap | `test_exporting_a_report_creates_an_audit_entry`, `test_reading_the_audit_report_is_itself_audited` |
| FR-010 | backend | known-gap | — |
| FR-011 | backend | unverified | — |
| FR-012 | ui | unverified | — |
| FR-013 | ui | test-cited | `test_reading_the_dashboard_and_charts_mutates_nothing`, `test_running_and_exporting_every_report_mutates_nothing` |
| FR-014 | governance | unverified | — |
| FR-015 | governance | unverified | — |
| FR-016 | ui | test-cited | `test_a_reader_scoped_dashboard_counts_only_their_visible_assets` |
| FR-017 | ui | known-gap | `test_total_value_counts_only_assets_the_organization_still_holds` |
| FR-018 | ui | known-gap | `test_one_asset_appears_in_exactly_one_expiry_band` |
| FR-019 | ui | test-cited | `test_one_asset_appears_in_exactly_one_expiry_band` |
| FR-020 | ui | test-cited | `test_total_value_counts_only_assets_the_organization_still_holds` |
| FR-021 | ui | test-cited | `test_a_report_with_no_matching_records_returns_an_empty_row_set` |
| FR-022 | backend | unverified | — |
| FR-023 | governance | unverified | — |

## How to use this

1. **Tag as you write.** Every new test gets a `Covers:` line; the map regenerates.
2. **Record a gap as `expectedFailure`, not an omission** — the requirement stays
   executable and the runner tells you when it starts passing.
3. **Work the backend column in risk order** — authorization and privacy, then lifecycle
   integrity, then audit and retention, then presentation.
4. **Translate the acceptance scenarios.** 290 Given/When/Then cases are already written.
5. **Reconcile as you go.** A failing test whose requirement is *not* in a gap register
   means the register was incomplete.
6. **Decide the UI question separately** — the `ui` rows need a frontend runner.
