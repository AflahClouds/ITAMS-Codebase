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

Do not place durable feature artifacts under `.specify/`. That directory is
managed Spec Kit infrastructure.
