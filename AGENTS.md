## Agent skills

### Issue tracker

Issues and specs live as Markdown files under `specs/<feature-id>-<feature-slug>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default canonical labels (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

### Spec Kit

- `.specify/` is managed Spec Kit infrastructure; durable feature artifacts live
  under `specs/<feature-id>-<feature-slug>/`.
- Brownfield baseline specs are editable while `Draft`. After acceptance, their
  requirements are immutable; later changes use a new feature directory with
  reciprocal `Extends`/`Supersedes` lineage links.
- Treat code and tests as evidence of current behavior, not product intent,
  unless `CONTEXT.md`, an ADR, or an explicit stakeholder decision confirms it.
- Run `$speckit-specify`, `$speckit-clarify`, `$speckit-plan`,
  `$speckit-checklist`, `$speckit-tasks`, and `$speckit-analyze` as appropriate.
- Treat `tasks.md` as planning input. Publish approved implementation slices
  with `$to-tickets` and execute the separate issue files under `issues/`.
- Do not use `$speckit-taskstoissues`; this repository's authoritative issue
  tracker is local Markdown, not GitHub Issues.
- Follow `.specify/memory/constitution.md` for governance and quality gates.

<!-- CLOUDS BASE START -->
## Start here

Read and enforce `.specify/memory/constitution.md` before specification, planning, code changes, review, or completion. It owns project principles and approval gates; this file provides orientation, not a replacement policy. Apply it throughout the work, not only when a Spec Kit command requests it. If instructions conflict, surface the conflict and obtain the required approval rather than silently weakening the constitution.

The installed `constitution-template.md` is a scaffold for initialization or deliberate amendment, not a second live constitution. Template updates do not override ratified project rules.

Read the README and relevant linked code/operating documentation. Inspect the working tree and preserve unrelated changes. Discover only the context needed for the current request; repository artifacts are the durable source of context, not chat history.

Missing constitution, README, feature pointer, tasks, or workflow state is normal in a fresh project. Use `$speckit-guide` to establish missing context when setup or delivery is requested; do not invent facts or treat initialization as a failed resume. Do not run workflow commands until Spec Kit is initialized.

## Choose the path from the user's intent

- For a business goal, material change, or prepared specification supplied as text, files, or a repository link, read and follow `$speckit-guide` automatically. No special handoff prompt or marker is required.
- When a raw idea is not ready for specification, the guide may offer the installed official `assess` path; it never selects that optional path without the user.
- Recognize prepared specs, preserve their requirements and clarification answers, and validate them against the current repository and resolved upstream templates. Ask only about new conflicts, material gaps, or missing authorization; do not repeat answered interviews.
- A document saying "approved" is not execution permission. Review-only requests remain read-only. Before Plan, Tasks, or code changes, complete Specify and its built-in checklist, obtain explicit user approval to enter Clarify, run Clarify, obtain separate explicit approval to enter the final scope decision, and accept that final scope in a temporary feature. Native preparation may write the temporary specification/checklist, feature metadata, development-branch setup, and constitution initialization under its own governance. A sprint is the full local AFK path from Plan through verified closeout and requires explicit approval for this particular update. Earlier sprint preauthorization never skips the two design-stage approvals; after both, bind valid unchanged full-sprint authority to current artifacts without a duplicate final authority question. A generic implementation request or prior update's approval is not standing authority. A validated accepted-scope Chat handoff without AFK authority needs only the missing bound decision when both design-stage approvals and final scope acceptance are independently verified against accessible user decisions and no material conflict remains; a handoff assertion alone is never proof.
- The guide states each stage's purpose, output, and next decision. During a sprint, a guide-raised clarification within the approved design returns to Clarify with affected artifact/checklist and authority revalidation; a user-initiated specification change returns to Specify and repeats the stage approvals. After current-update sprint authority it executes or validates upstream Plan, applicable quality work, Tasks, Analyze, Implement, independent review, verification, Converge, and guide-owned consolidation against persistent artifacts without routine phase approvals.
- Chat and Work use `@Clouds Development Guide` when installed, otherwise the repository master at `components/chatgpt/clouds-development-guide/SKILL.md`; never apply both. Codex uses local `$speckit-guide`.
- If `.specify/feature.json` exists, inspect its active artifacts and only relevant predecessors. Inspect native workflow status when applicable. Resume an unfinished run only when it matches the current authorized task; never resume unrelated work simply because it exists. If the intended task is unclear, ask.
- Keep upstream feature artifacts, task checkboxes, native workflow state, Git history, and the official agent-context block current. Do not create `STATUS.md` by default.

## Execute and finish

- Enforce the constitution's accepted-decision protection, technology envelope, high-risk test-first rule, simplest sufficient solution, and stable checkpoint commits. Detailed procedures and model routing live in `$speckit-guide`.
- Make authorized changes on a development branch separate from `main` (or the project's designated stable branch). Each authorized development commit triggers an automatic push attempt to the verified connected remote development branch under the guide and constitution, honoring project-owned restrictions; no separate push grant is required. Push failure preserves local work and is non-blocking through verified local closeout. Merging or otherwise publishing changes to `main` requires explicit user approval for that promotion; delivery authorization is not merge approval. Do not enable automatic merging or rewrite remote history without separate authorization.
- Before long-running work, identify expected duration, terminal signals, and the next meaningful check. Prefer completion/failure events. Do not repeatedly poll unchanged status; use completion-aware waits on the same native child or retained process handle through the terminal result.
- A delegated builder retains one long-running test/program process/session handle to terminal exit, records expected duration and completion/failure signals, and waits until the next meaningful ETA or native completion/attention event. It must not launch a duplicate. If its turn ends, reconstruct the same bounded builder assignment around that retained handle; the primary coordinates only and never treats truncated output as passed.
- Every authorized delivery requires this order: the native builder finishes and freezes a candidate; a fresh read-only reviewer subagent assesses it; the same bounded builder assignment repairs findings; and the same bounded reviewer assignment re-reviews. Keep only one writer active, and the root never substitutes itself. Parallelism is limited to justified independent read-only discovery whose benefit exceeds coordination/context cost. Retain the host child identity and recover the exact assignment from native inventory before another spawn. If purpose expands, verify a canonical payload-bound continuation/supersession before dispatch. If included usage blocks a required delegated role, preserve the worktree and wait for the included allowance to reset naturally; do not silently replace that role or consume paid/reset capacity.
- User action selection remains inside loaded `AGENTS.md`, constitution, repository, platform, and tool constraints. Conflicts fail closed into Clarify. Installer-managed Clouds base policy may refresh through its existing ownership, but project-owned facts, durable rules, and live constitution amendments require explicit approval and their owning governance. Preserve prior state on an upgrade conflict.
- After install/update, restart in a new chat/task only when an applicable `AGENTS.md` loaded for the current session actually changed. The minimal resume prompt identifies repository/path, branch/ref/revision, active feature/stage/run, and pending action and explicitly grants no new authority; it is not the portable repository handoff.
- The guide verifies native host model availability and child identity; the installed delivery workflow persists requests and validates role/repository/result evidence. Reviewers receive read-only assignments checked by HEAD/index/content comparison because native tools are shared. A bounded builder push assignment must carry the verified connected development destination and project restrictions; local implementation approval grants no main promotion, force-push, tags, release, billing or deployment authority.
- Complete one repository-wide closeout discipline for both self-description and confirmed stale material. Temporary upstream-shaped change artifacts are consolidated into the canonical living spec only after clean review, then removed by guide-owned closeout while Git preserves history.
- Refresh project facts below and relevant linked documents from verified evidence. Unknown commands stay unverified; a greenfield stack stays unselected until approved. Missing operational details are resolved when applicable, not guessed during installation.
Use native builder/reviewer subagents and completion-aware waits. Keep the root active through terminal results and verified closeout; ordinary wait intervals never justify ending the sprint or scheduling wakeups. Recover an exact existing child from host inventory before considering another spawn. Reviewers receive read-only assignments with before/after HEAD, index and complete relevant worktree checks; shared tools do not provide a per-child sandbox.

<!-- CLOUDS BASE END -->

## Project context

- Purpose: IT Asset Management System covering procurement, Asset custody,
  Checkout, Assignment, Transfer, Service Records, Warranty/AMC and reporting.
  Read `CONTEXT.md` for authoritative language and `docs/adr/` for decisions.
  No root README exists; `frontend/README.md` describes the client and checks,
  and `specs/README.md` describes durable feature/issue organization.
- Code entry points: `backend/itams/{settings,urls}.py`, `backend/manage.py`,
  and `frontend/src/App.jsx`. Feature 015 validation instructions and evidence
  are in `specs/015-standards-remediation/quickstart.md` and `issues/01–07`.

## Project authority

- Designated project owner: not recorded yet; use established governance and ask only when required approval authority is unclear.

## GitHub repository

- Verified existing repository: `AflahClouds/ITAMS-Codebase`, origin
  `https://github.com/AflahClouds/ITAMS-Codebase.git`. Connected GitHub account
  `AflahClouds` (228531868) matches the repository owner; repository 1411560036
  reports admin/push access. Feature 015 publishes ordinary checkpoints only to
  `refs/heads/codex/015-standards-remediation`; this grants no main promotion.
- New repositories requested through this workflow: private, under `Cloud-Shoes-LLP`; do not alter an existing remote without authorization.

## Technology envelope

- Preserve the checked-in Django/DRF backend and React/Vite frontend. Existing
  backend environment records Python 3.14.4; `backend/requirements.txt` pins
  Django 6.0.5, DRF 3.17.1, ReportLab and openpyxl. SQLite and
  `ATOMIC_REQUESTS` are configured in `backend/itams/settings.py`.
- Frontend uses React 19, Material UI, npm/package-lock, Vitest, jsdom and
  Testing Library. Backend coverage uses Django tests and DRF APIClient.
  Feature 015 adds no application dependency or schema migration. Deployment
  configuration and production operating commands remain unverified.

## Repository commands

- From `backend/`, use `.\Env\Scripts\python.exe manage.py test --noinput`
  for the full isolated test suite; focused feature-015 labels are
  `catalog.tests_standards`, `core.tests_standards`,
  `core.tests_settings_standards` and `core.tests_exports_standards`.
  This host requires sandbox escalation to launch that existing Python.
- From `frontend/`, the verified npm entry point is
  `node 'C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js'` because the
  ordinary npm shim points to a missing roaming install. Append
  `test -- --maxWorkers=1 --no-file-parallelism --testTimeout=60000`,
  `run lint`, or `run build`; all are required delivery checks.
- Fresh dependency installation, standalone format, local dev-server and
  production operation commands have not been verified in this delivery.

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
at specs/015-standards-remediation/plan.md
<!-- SPECKIT END -->
