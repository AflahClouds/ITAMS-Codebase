# Quickstart Validation: Standards Remediation

Use the existing installed dependencies; do not operate on the live database or media to prove these fixes. API tests use Django's isolated test database and temporary storage. Every new regression must fail for the intended pre-fix behavior before its production fix.

From backend/:

```powershell
.\Env\Scripts\python.exe manage.py test catalog core --noinput
.\Env\Scripts\python.exe manage.py test --noinput
```

Builder records the final concrete focused test labels in issue evidence. The complete backend baseline ran 354 tests in 499 seconds; expect roughly 8–12 minutes, retaining the same session until exit. Add makemigrations --check --dry-run only if model declarations change.

From frontend/ (the working npm CLI path avoids this host's broken roaming npm shim):

```powershell
node 'C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js' test -- --maxWorkers=1 --no-file-parallelism --testTimeout=60000
node 'C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js' run lint
node 'C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js' run build
```

Expected checks: Models retain Brand; duplicate names return validation conflicts and one durable audit; audit reads/Setting mutations create one private audit record and fail closed; PDF text stays literal with no resource loads; reopened XLSX values preserve string/non-string types. Public API integration proves authorization and delivered file content. A browser walkthrough and visual PDF inspection, if not executed, remain explicitly unverified.

Independent reviewer compares frozen HEAD/index/full relevant worktree before/after and reports findings read-only. The same builder repairs and same reviewer re-reviews. No main merge or deployment is part of this validation.
