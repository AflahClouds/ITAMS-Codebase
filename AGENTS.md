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
