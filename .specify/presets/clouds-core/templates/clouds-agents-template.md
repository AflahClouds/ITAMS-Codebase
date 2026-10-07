# AGENTS.md

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

- Purpose and documentation entry point: repository README when available; Codex establishes it from the accepted business goal.
- Code and operating documentation: not established yet; link relevant entry points as they become available.

## Project authority

- Designated project owner: not recorded yet; use established governance and ask only when required approval authority is unclear.

## GitHub repository

- Full repository name: not verified yet; discover from origin when available.
- New repositories requested through this workflow: private, under `Cloud-Shoes-LLP`; do not alter an existing remote without authorization.

## Technology envelope

- Not established yet. Discover and preserve an existing stack from checked-in evidence; for greenfield work, recommend one and obtain approval before implementation. Record the approved language/runtime, framework, package manager, data store, tests, architecture/deployment, and material dependencies here.

## Repository commands

- Not verified yet. Discover setup, fast checks, full tests, lint/format, build/run, and applicable operation commands from checked-in sources. Record each only after verification; mark unavailable or inapplicable commands explicitly.

<!-- SPECKIT START -->
<!-- Managed by the official Spec Kit agent-context extension. -->
<!-- SPECKIT END -->
