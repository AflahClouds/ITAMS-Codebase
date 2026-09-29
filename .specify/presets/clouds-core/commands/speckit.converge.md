## Clouds v1 convergence policy

## Clouds living-spec addition

Treat closeout as a repair/recheck/re-review discipline: findings return to the sole builder, impacted and relevant broader checks rerun, and independent review repeats until clean. Do not delete temporary artifacts or restore canonical routing during the task ledger; those are guide-owned post-workflow obligations.

After native convergence is clean, return control to the guide for post-convergence canonical consolidation and checklist review, temporary-artifact deletion, routing restoration, and post-cleanup checks. None of these guide-owned obligations is an unchecked `tasks.md` item. The native delivery step does not run this maintainer repository's release/candidate checks in an installed project. Any closeout finding returns to the same builder and read-only reviewer sequence; uncertain destructive work or missing external authority still stops.

Extend the upstream intent inventory with the predecessor list and the final pre-closeout repository-wide task from `tasks.md`. In one review, inspect the entire active tree for both outcomes:

- repository context is sufficient for a fresh competent person or agent to understand the system, modify and test it safely, operate affected production behavior when applicable, and resume unfinished work without chat history;
- no confirmed stale or superseded code, tests, dependency, configuration, flag, documentation, example, generated artifact, or duplicate execution path remains.

For normal/manual upstream `$speckit-converge`, append traceable pre-closeout context, implementation cleanup, checkpoint, or verification tasks using the upstream append-only contract; never edit implementation or documentation during converge. A separate `STATUS.md` is not required when the existing feature artifacts, tasks, native workflow state, Git history, and agent-context block make resumption unambiguous. If a potential implementation deletion is uncertain or its intent cannot be established, append a user-approval task rather than assuming.

When the existing `clouds-delivery` workflow invokes this command as its automated reviewer, that invocation is read-only: do not edit files, append tasks, or apply corrections. Return `CLOUDS_FINDINGS_JSON: []` when clean; otherwise return a JSON array of finding objects with `id`, `finding`, and `required_action`. In this automated-reviewer mode, `CLOUDS_CONVERGENCE: tasks_appended` means findings were returned for the builder to apply, not that the reviewer mutated `tasks.md`.

Temporary change directories are disposable working artifacts, not intentional completed flow-forward history. Do not delete them during convergence; after clean convergence, require the guide-owned canonical review and checklist/reference validation before deletion.

Convergence assesses local development work, not push or promotion to `main`. Awaiting affirmative push or merge approval is not an implementation gap: do not append a publication task solely to obtain a converged result, perform a push or merge, or enable automatic merging. Changes reach `main` only through a separately, explicitly user-approved promotion.

Before declaring convergence, check the active tree's tracked project files as appropriate, including dependency manifests, references to removed paths or names, project documentation, repository commands, deterministic test coverage, Git checkpoint coverage, and the latest verification results. Missing pre-closeout context, implementation cleanup, checkpoint, or verification work means the result is `tasks_appended`; guide-owned post-convergence work is not a convergence blocker.

End the response with exactly one machine-readable line after all other output:

- `CLOUDS_CONVERGENCE: tasks_appended` for normal/manual upstream converge when one or more tasks were appended; for the automated `clouds-delivery` reviewer when non-empty structured findings were returned and `tasks.md` is unchanged.
- `CLOUDS_CONVERGENCE: clean` only when `tasks.md` is byte-for-byte unchanged and all Clouds checks are clean.
- `CLOUDS_CONVERGENCE: approval_required` when a specific user decision is required; state the concrete question before this final line.
- `CLOUDS_CONVERGENCE: blocked` when work cannot continue; state the blocker before this final line.
