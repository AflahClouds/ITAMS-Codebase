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

The new focused module is planned until builder creates it. Record actual legacy
labels, terminal exits/counts, red-before-green evidence in each issue.

From frontend, use verified npm entry point:

~~~powershell
node 'C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js' test -- --maxWorkers=1 --no-file-parallelism --testTimeout=60000
node 'C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js' run lint
node 'C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js' run build
~~~

Full backend baseline takes 8–12 minutes. Builder retains each run's handle to
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