# GitHub Spec Kit adoption for ITAMS

**Researched:** 2026-07-28  
**Target:** Existing ITAMS repository on Windows, using Codex and PowerShell  
**Official Spec Kit release checked:** v0.14.2

## Decision

Keep Spec Kit infrastructure and durable feature artifacts separate:

- `.specify/` contains managed Spec Kit scripts, templates, memory, and
  integration metadata.
- `specs/<feature-id>-<feature-slug>/` contains feature-authored requirements,
  plans, design artifacts, task graphs, and local implementation tickets.

This replaces the repository's earlier `.scratch/` convention. The application
did not use `.scratch/`; it was only the local Markdown issue tracker configured
for the installed engineering skills. Because no feature history existed there,
the convention was migrated before initializing Spec Kit.

The separation follows Spec Kit's normal layout and keeps durable specifications
outside managed project infrastructure. The official upgrade guide confirms
that `specs/` is excluded from template packages and is preserved during project
file upgrades:
[Spec Kit upgrade guide](https://github.github.com/spec-kit/upgrade.html).

## Repository mapping

| Concern | Location |
| --- | --- |
| Spec Kit infrastructure | `.specify/` |
| Codex Spec Kit skills | `.agents/skills/speckit-*/SKILL.md` |
| Feature specification | `specs/<feature-id>-<feature-slug>/spec.md` |
| Technical plan | `specs/<feature-id>-<feature-slug>/plan.md` |
| Research and data design | `specs/<feature-id>-<feature-slug>/research.md`, `data-model.md` |
| Interfaces and checks | `specs/<feature-id>-<feature-slug>/contracts/`, `checklists/` |
| Spec Kit task graph | `specs/<feature-id>-<feature-slug>/tasks.md` |
| Authoritative local tickets | `specs/<feature-id>-<feature-slug>/issues/<NN>-<slug>.md` |
| Shared domain language | `CONTEXT.md` |
| Architectural decisions | `docs/adr/` |

`tasks.md` is a planning and consistency-analysis artifact. The existing
`to-tickets` skill remains responsible for publishing approved tracer-bullet
tickets as separate Markdown files under the feature's `issues/` directory.
The built-in `taskstoissues` command should not be used because its publication
target is GitHub Issues.

## Installation

Install or repair the pinned CLI release:

```powershell
uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git@v0.14.2
specify version
```

Initialize the existing repository from its root:

```powershell
specify init --here --force --integration codex --script ps
```

If Codex executable detection fails when Codex is supplied by the desktop
application, add the documented `--ignore-agent-tools` flag.

The Codex integration installs skills under `.agents/skills/` and invokes them
as `$speckit-<command>`:
[integration reference](https://github.github.com/spec-kit/reference/integrations.html).

Git branch management is an optional extension and is intentionally not enabled
initially:
[core command reference](https://github.github.com/spec-kit/reference/core.html).

## ITAMS governance

The project constitution must require:

1. `CONTEXT.md` is the authoritative domain glossary.
2. Relevant ADRs are read before planning or implementation, and conflicts are
   surfaced explicitly.
3. Feature artifacts live in the active `specs/<feature-id>-<feature-slug>/`
   directory.
4. The local Markdown issue tracker is authoritative for implementation work.
5. `tasks.md` does not replace one-file-per-ticket issues.
6. Acceptance criteria remain traceable to tests and observable end-to-end
   behavior.
7. Existing repository conventions and test commands take precedence over
   generic generated examples.

## Feature workflow

```text
$speckit-specify <Describe what users need and why.>
$speckit-clarify
$speckit-plan <Provide technical constraints and architecture choices.>
$speckit-checklist
$speckit-tasks
$speckit-analyze
```

After analysis is clean, use `$to-tickets` to publish local tickets in the
active feature directory, review their blocking edges, and implement them
through the repository's existing workflow.

## Upgrade policy

The CLI and repository-installed integration files have separate upgrade paths:

```powershell
specify self check
specify self upgrade
specify integration status
specify integration upgrade codex
specify extension update
```

Use `specify init --here --force --integration codex` only for initial setup or
recovery. Review the generated diff whenever managed project files are updated.
