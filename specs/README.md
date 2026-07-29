# Feature specifications

Spec Kit creates one durable directory per feature:

```text
specs/<feature-id>-<feature-slug>/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|-- checklists/
|-- tasks.md
`-- issues/
```

`spec.md` is the feature requirements source of truth. The other Spec Kit
artifacts refine the design and task graph. After review, `to-tickets` publishes
the approved implementation slices as separate files under `issues/`; those
files are authoritative for execution.

Brownfield baseline specs remain editable while their status is `Draft`. Once
accepted, their requirement and acceptance content is immutable. Later
substantive changes use a new feature directory, with reciprocal `Extends`,
`Supersedes`, or `Superseded by` links between the records. Adding lineage
metadata is the only permitted semantic-neutral edit to an accepted spec.

Code and automated tests are evidence of current behavior, not product intent
by themselves. A baseline must distinguish authoritative or stakeholder-
confirmed intent, test-verified behavior, implementation-only observations, and
unresolved conflicts.

Do not place durable feature artifacts under `.specify/`. That directory is
managed Spec Kit infrastructure.
