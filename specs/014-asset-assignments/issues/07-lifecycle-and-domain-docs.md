# 07 — Preserve lifecycle and domain records

**What to build:** Service and terminal actions end active custody without invented returns or automatic reissue; Lost retains accountability.

**Blocked by:** 02, 03, 04 and 06.

**Status:** ready-for-agent

**Tasks:** T027–T029. **Requirements:** FR-001/007–014, ALR-002–005; AS-015.

- [x] Service and terminal actions end active custody without invented returns or automatic reissue; Lost retains accountability.
- [x] Details, lists, reports and PDF show accurate custody; CONTEXT.md, ADR-0001 and lineage reflect only accepted decision.
- [x] Fail-before integration tests, focused green exits and a stable local checkpoint are recorded.

## Comments

- Fail-before API: service interruption left an ongoing Assignment Open, fabricated a Checkout return date/condition, and Lost left ongoing custody Open (3 failures, `itams-014-issue07-red-api.log`, exit 1). A terminal interruption fabricated a vendor return date (`itams-014-issue07-service-return-red.log`, exit 1). The accepted Sold/Scrapped eligibility case found Assigned → Sold returned 200 instead of rejecting until the Asset is Available (`itams-014-issue07-eligibility-red.log`, exit 1); Lost allowed a payload to erase the retained department (`itams-014-issue07-lost-department-red.log`, exit 1). A service audit omitted the interrupted Assignment ID (`itams-014-issue07-audit-detail-red.log`, exit 1). Generic Asset DELETE returned 204 and erased active and closed Assignment/Checkout plus Transfer history (`itams-014-issue07-delete-red.log`, exit 1). An earlier Assigned → Sold test expectation was incorrect and is excluded from accepted fail-before evidence.
- The custody interruption now records administrative closure, actor/time/reason and affected IDs without physical return or inspection fields. Sold/Scrapped retain their Available/In Storage eligibility and clear Custodian/department; Lost keeps both. Generic Asset deletion rejects any custody snapshot or history under the same Asset transaction/row lock used by custody operations, while an unrelated unused Asset remains deletable. Detail/list and register/lost report cases verify the current holder/type; existing authorized Transfer PDF/history tests remain in the complete suite.
- Focused green: lifecycle, legacy status/service and interruption checks 61/61 (`itams-014-issue07-focused-complete.log`, exit 0); custody-history deletion 1/1 (`itams-014-issue07-delete-green-final.log`, exit 0); corrected prior interruption assertions 2/2 (`itams-014-issue07-legacy-oracle-green.log`, exit 0). Audit rollback was already green before the audit-detail change (`itams-014-issue07-audit-red.log`, exit 0), so it is not claimed as fail-before.
- Complete Django first found two prior assertions for fabricated return fields (331 tests, 2 failures; `itams-014-issue07-full-django.log`, exit 1). After correcting those assertions, one attempted rerun lost its process handle after database creation and has no terminal result (`itams-014-issue07-full-django-final.log`); it is not counted as passing. Recovered full Django: 331/331, exit 0 (`itams-014-issue07-full-django-recovered.log`). Full frontend Vitest: 57/57, exit 0 (`itams-014-issue07-frontend-test.log`); ESLint exit 0 with 14 warnings (`itams-014-issue07-frontend-lint.log`); Vite build exit 0 (`itams-014-issue07-frontend-build.log`). Django migration check reported no changes. Logs are under `C:\Users\aflah.vk\AppData\Local\Temp` and terminal results include exit markers.
- `CONTEXT.md` and ADR-0001 now describe temporary Checkout, ongoing Assignment and deliberate post-service reissue. Accepted predecessor specifications received reciprocal `Extended by` metadata only. A verified local Git checkpoint records this issue's source, tests, domain text and evidence; no remote action was performed.
