# Issue tracker: Local Markdown

Issues and specs (you may know a spec as a PRD) for this repo live as Markdown files in `specs/`.
The feature directory is the directory created by Spec Kit, normally
`specs/<feature-id>-<feature-slug>/` (for example, `specs/001-asset-audit/`).

## Conventions

- One feature per directory: `specs/<feature-id>-<feature-slug>/`
- The spec is `specs/<feature-id>-<feature-slug>/spec.md`
- Spec Kit planning artifacts such as `plan.md`, `tasks.md`, `research.md`, `contracts/`, and `checklists/` live beside the spec
- Implementation issues are one file per ticket at `specs/<feature-id>-<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01` — never a single combined tickets file
- `tasks.md` is planning and analysis input; the separate issue files are authoritative for implementation
- Use `to-tickets` to publish reviewed slices locally; do not use `speckit-taskstoissues`
- Triage state is recorded as a `Status:` line near the top of each issue file (see `triage-labels.md` for the role strings)
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Create a new file under the relevant `specs/<feature-id>-<feature-slug>/` directory.

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a file with one **child** file per ticket.

- **Map**: `specs/<effort>/map.md` — the Notes / Decisions-so-far / Fog body.
- **Child ticket**: `specs/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`); a `Status:` line records `claimed`/`resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every file it lists is `resolved`.
- **Frontier**: scan `specs/<effort>/issues/` for files that are open, unblocked, and unclaimed; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`, then append a context pointer (gist + link) to the map's Decisions-so-far in `map.md`.
