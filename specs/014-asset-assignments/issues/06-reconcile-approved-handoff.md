# 06 — Reconcile a verified historical handoff

**What to build:** Approved Transfer history proves A-to-B before IT supersedes A's stale Checkout; original dates remain, physical return stays empty and Transfer is linked.

**Blocked by:** 04 — Transfer an ongoing Assignment; 05 — Classify matching legacy Checkout.

**Status:** ready-for-agent

**Tasks:** T023–T024 and reconciliation portions of T025–T026. **Requirements:** FR-011/013, ALR-001–003; AS-023–024.

- [x] Approved Transfer history proves A-to-B before IT supersedes A's stale Checkout; original dates remain, physical return stays empty and Transfer is linked.
- [x] B stays Custodian with unchanged status/department and one IT-classified active arrangement; a copied recorded historical Transfer date is labeled “Legacy Transfer event date (event type unverified),” not a proven request, approval, physical issue, handoff or return time; invalid evidence and repeats fail safely.
- [x] Fail-before API/UI tests, focused green exits and a stable local checkpoint are recorded.

## Comments

- 2026-10-08 Clarify: the user selected the recorded historical Transfer date with an explicitly unverified event type, then approved the revised artifacts. Approved Transfer holder/department chain, rather than an unprovable request-time AuditLog, is the reconciliation evidence. The frozen recovery draft's future request-timestamp change and test were removed from this issue; existing Transfer approval behavior remains.
- Fail-before API: two reconstruction integration cases returned HTTP 400, “Current holder has no matching active arrangement,” before the missing-B implementation (2 failures; `itams-014-issue06-red-api.log`, terminal exit 1). Fail-before UI: missing Reconcile control and Superseded/date-basis history (2 failures, 6 existing passes; `itams-014-issue06-red-ui.log`, exit 1). The Transfer list provenance label independently failed before its display change (`itams-014-issue06-transfer-label-red.log`, exit 1). These are the intended behavioral red results; an interim misplaced test assertion later caused an unrelated test error and was corrected.
- Focused green: `LegacyReconciliationTests` plus `LegacyClassificationTests`, 12/12, exit 0 (`itams-014-issue06-placement-focused.log`); Checkout/Assignment UI, 18/18 before the additional permission test, exit 0 (`itams-014-issue06-ui-focus-1.log`). Complete suites include the new repeat, audit-rollback, and UI permission cases.
- Full Django from `backend/`: 324/324, exit 0 (`itams-014-issue06-full-django-final.log`). Full frontend Vitest: 57/57, exit 0 (`itams-014-issue06-full-frontend.log`). ESLint: exit 0 with 14 existing warnings (`itams-014-issue06-lint-final.log`). Vite build: exit 0 (`itams-014-issue06-build.log`). Django `makemigrations --check --dry-run`: no changes detected. The first repository-root Django discovery found zero tests and was not counted as validation. All named logs are under `C:\Users\aflah.vk\AppData\Local\Temp` and contain terminal exit markers.
- A verified local Git checkpoint records this issue's source, tests, migration, and evidence; no remote action was performed.
