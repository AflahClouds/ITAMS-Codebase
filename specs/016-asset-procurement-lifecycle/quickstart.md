# Validation: Asset Procurement Lifecycle

Use existing dependencies and isolated Django test databases. No production
database, deployment or dependency installation is part of verification.

## Commands

From backend (existing Env Python requires host sandbox escalation):

~~~powershell
.\Env\Scripts\python.exe manage.py test assets.tests_procurement_lifecycle --noinput
.\Env\Scripts\python.exe manage.py test --noinput
.\Env\Scripts\python.exe manage.py makemigrations --check --dry-run
~~~

The focused module covers the three journeys plus stale validation/write, audit
rollback and private-file commit boundaries. Existing Procurement/invoice/custody
regressions remain; terminal evidence is recorded in issues 01–05.

From frontend, use verified npm entry point:

~~~powershell
node 'C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js' test -- --maxWorkers=1 --no-file-parallelism --testTimeout=60000
node 'C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js' run lint
node 'C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js' run build
~~~

Verified full backend runs took about 10–13 minutes. Builder retains each run's handle to
terminal exit; no duplicate healthy run. Root coordinates. Do not claim browser
acceptance unless a browser was actually used.

## Acceptance walk-through

1. Register A/B: Storage. Direct Available/procurement writes cannot bypass staging.
2. Create valid purchase P linked to both: Available, optional invoice allowed.
3. Delete A while linked: rejection, A/P unchanged.
4. Remove A with reason: A Storage/unlinked, P retains B; separately delete
   eligible A. Custody-history Assets remain protected.
5. Empty P via edit: rejected with complete-deletion guidance.
6. Explicitly delete singleton P: purchase/history/invoices removed; B retained
   Storage/unlinked, separately deletable only if ordinary safeguards permit.
7. Ordinary archive retains links. Denied/protected/stale/audit-failure requests
   preserve data/files.

## Evidence

Issue comments capture red/green; final issue records full checks and combined
stale-material/self-description review. This guide is not verification evidence.

Initial verified builder results (2026-10-29): full Django 410/410, full frontend
16 files/81 tests, lint/build exit 0, migration drift No changes detected.
See issues/04-verification.md for retained process identities and terminal
counts, including superseded fixture failures. Independent review and guide
closeout follow the frozen builder candidate; browser acceptance is unperformed.

F001 review repair: success and manager notification now open the existing
/asset/detail/:id route. Focused backend 35/35 and full frontend 17 files/82 tests
pass; lint/build exit 0. The new actual-App routing regression freshly loads
the retained unlinked In Storage Asset. See issues/05-retained-asset-navigation.md.
The prior full 410-test backend green remains broader evidence for this URL-only
backend repair; no schema or lifecycle logic changed.

Native run bfc1a11c completed after the same fresh read-only reviewer confirmed
F001 resolved with no further findings at e63184b. All 21 tasks and five local
issues are complete. Final current-domain/README/agent-fact consolidation is
guide-owned and changes no application behavior or accepted requirements.

Guide closeout completed after clean independent documentation review. Current
CONTEXT.md, frontend README, agent project facts, feature metadata and evidence
agree with the accepted behavior. All relevant pointers resolve to this retained
authoritative feature; historical requirements and unrelated state are preserved.
No application change followed the verified repair. Browser/manual acceptance,
production database migration, deployment and main promotion remain unperformed.

F002 confirmation-intent correction: Archive retains /procurement/delete/:id and
opens only archive confirmation. The singleton table and edit permanent actions
use /procurement/permanent-delete/:id and open only permanent confirmation.
Entry/cancel never mutate; direct ineligible permanent entry fails closed.
Focused frontend 5 files/32 tests and full frontend 17 files/89 tests pass;
lint/build exit 0. See issues/06-distinct-procurement-confirmations.md for red/green,
retained terminal handles and the combined current-reference review. Backend,
accepted business rules and dependencies are unchanged by this UI correction.
