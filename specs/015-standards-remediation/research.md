# Research: Standards Remediation

## Catalog identity and Brand membership

Decision: Extend existing serializers and master viewsets, expose a required Brand on new Model writes, retain nullable storage for legacy rows, and add Brand selection/display to the existing master form.
Rationale: B6 already defines Brand-scoped Model identity; the schema relation exists but the serializer omits it. A destructive backfill is unnecessary and outside scope.
Alternatives considered: Making the database field immediately nonnull would require guessing or separately reconciling legacy data; accepting unbranded new Models fails FR-001.

## Normalized conflicts and audit durability

Decision: Use existing normalize_name semantics before lookup, exclude current PK, scope Model by Brand, and convert only recognized normalized identity conflicts into a useful validation response. Cover save-time races in a rolled-back savepoint and retain one rejection audit outside that failed boundary.
Rationale: DRF's generic validation exception rolls back ATOMIC_REQUESTS, so logging inside a rejected transaction can silently disappear. Existing AuditDenialMiddleware documents this boundary. Reuse existing log_action and permissions; do not swallow unrelated IntegrityError or required-audit failure.
Alternatives considered: Database-only uniqueness causes 500s; exact-only serializer UniqueValidator misses whitespace/case; treating every IntegrityError as a duplicate conceals defects. A general audit framework is unnecessary.

## Direct audit reads and Setting mutations

Decision: Extend current direct list/retrieve and Setting mutation hooks, preserving the response shape, filters, limits, permission mapping and POST upsert. Exactly one minimized required audit per action; fail closed on audit write failure.
Rationale: Existing API request transactions already provide mutation/audit atomicity. Direct retrieval needs an unsliced queryset; limiting remains a list presentation rule.
Alternatives considered: Frontend-only controls cannot repair backend accountability; removing supported Setting methods changes the accepted interface.

## Literal PDF and Excel text

Decision: Escape user-provided text at every shared PDF paragraph boundary and preserve application-owned markup. Explicitly mark string-valued XLSX cells as strings while leaving non-strings typed.
Rationale: Verified review probes: '<b>broken' raises ValueError in the current PDF builder and '=1+1' becomes an XLSX formula. Shared builders cover actual report/Transfer outputs without duplicating per-report policy.
Alternatives considered: Stripping characters destroys business data; prepending visible apostrophes changes exported values; converting every cell to text loses number/date/bool meaning. No new package is needed.

## Existing execution tools

Decision: Use backend/Env/Scripts/python.exe and installed Node/npm CLI; request sandbox escalation for the Python launcher/Spec Kit as needed. Use the separately user-authorized isolated Spec Kit 1.0.13 environment under .clouds-install-source/runtimes/specify-1.0.13, preserving global CLI 1.2.0.
Rationale: The sandbox cannot launch the Python base executable, while the existing elevated test run succeeds. The npm shim points to a missing roaming installation; node 'C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js' works. Application verification uses the existing production dependencies without reinstalling them. The separately approved isolated workflow CLI repair did install Spec Kit 1.0.13 under the ignored local runtime directory, preserving the global CLI and production stack.
Alternatives considered: Altering global CLI 1.2.0 or bypassing the pinned reader would weaken the recorded workflow. The user approved the isolated compatible runtime after the missing-version blocker was demonstrated. No application dependencies were reinstalled. Preserve one retained process per long test run.

All technical questions are resolved from checked-in evidence and verified local probes. No external research or new dependency choice is required.
