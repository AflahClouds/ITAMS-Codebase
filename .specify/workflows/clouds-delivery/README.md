# Clouds AFK Delivery workflow

This native Spec Kit workflow starts only after `$speckit-guide` has produced and checked the upstream spec, built-in checklist, plan, research, and tasks. One native step persists the authorized branch, feature, spec/plan/checklist hashes, `initial_head`/`expected_head`, tag-ref digest, bounded builder/reviewer assignments, authorization reference, and dirty-worktree evidence before any Codex child runs. Twelve following delivery steps persist a strict native subagent request and pause internally. The active guide dispatches and awaits native builders/reviewers using upstream `speckit.implement`/`speckit.converge` procedures, then resumes the same pass with a verified host-child result. The custom step validates the exact request digest, role, status and child binding against repository evidence. It never launches a CLI worker.

Delivery is sequential: a bound builder finishes before a fresh read-only reviewer starts; findings return to the same bounded builder assignment; the same bounded reviewer assignment re-reviews. Host child identities are retained and recovered from native inventory after interruption, before any replacement dispatch. Every dispatch binds the phase, exact expected HEAD, and canonical findings/reassessment payload digest. The optional `assignment_transition` input is empty for ordinary dispatch; otherwise it must be byte-for-byte canonical JSON with exactly the ten documented fields. A non-finding transition also requires the separate strict canonical-object `reassessment_payload`; it defaults to the empty string and cannot be supplied without a transition. Invalid, duplicate, missing, extra, non-string, stale, or tampered transitions stop before launch.

The final task-ledger item completes the combined stale-material/self-description review before native convergence can be clean. After native convergence is clean, the guide owns separate post-implementation living-spec closeout: independent canonical consolidation and checklist review, temporary-artifact deletion, routing restoration, and post-cleanup checks. None of that guide-owned work is an unchecked task-ledger item. Material findings return to the same bounded builder and read-only reviewer. The distributed step does not require any Clouds maintainer release files or build a workspace-skill ZIP inside an installed project. This repository's local/manual-upload candidate is prepared separately from its final reviewed source with `scripts/New-CloudsReleaseCandidate.ps1`; preparation does not install, upload, push, publish, merge, release, or promote it.

Run it on the current task's development branch, separate from `main`. Each authorized development commit triggers the guide's automatic verified connected development-push attempt, honoring project restrictions. Failed or uncertain publication remains pending and does not block verified local closeout. The workflow completes with development ready for review; it does not merge or enable automatic merging. Promotion to `main` requires separate, explicit user approval, and pending approval does not cause another convergence pass.

Install from the Clouds source checkout with PowerShell 7 (`pwsh`); Windows PowerShell 5.1 is unsupported:

```powershell
pwsh -NoProfile -File .\scripts\Install-CloudsSpecKit.ps1 -TargetPath "C:\path\to\the-application"
```

For a published version, use that version's checksummed bootstrap with
`-InstallMode Catalog`. Both routes install the custom step first, then use
official `specify workflow add --dev <workflow-directory>` on Spec Kit v1.0.13.
Source custom-step copying remains necessary because official step installation
accepts catalog IDs only; remove that bridge only after an official local-source
step installation is proven equivalent.

Run from an initialized target repository:

```powershell
specify workflow run clouds-delivery -i model="<guide-selected-builder-model>" -i reviewer_model="<guide-selected-reviewer-model>" -i authorization_ref="<accepted-revision-bound-combined-decision>" -i task_class="<unknown|mechanical|routine|high-risk-deterministic|consequential|ambiguous>" -i oracle_evidence="<complete-fail-before-oracle-for-high-risk-deterministic>" -i assignment_transition="" -i reassessment_payload=""
```

Add `-i astra_user_requested="true"` only when the user explicitly requested Astra. Builder and reviewer models are chosen independently; they may be the same model, but their assignments and host child identities remain separate; reviewer read-only instructions are checked by before/after HEAD/index/content snapshots.

Spec Kit persists run state under `.specify/workflows/runs/`. Use `specify workflow status` and `specify workflow resume <run-id>` after interruption. When a pass requests approval, answer the concrete question and resume the same run with `-i approval_action=resume -i approval_response="<user decision>"`. At the twelve-pass limit, abort non-interactively with `-i limit_action=abort`; there is no thirteenth pass.

An internal `dispatch_required` pause keeps the root active. Discover and verify the existing Spec Kit v1.0.13 tool interpreter using the installed guide, then read the named request with `<verified-specify-python> .specify/workflows/steps/clouds-delivery-pass/__init__.py --project-root . --run-id <run-id>`, prove its child via native host events, and resume with compact strict `dispatch_result` JSON bounded to 8 KiB UTF-8 in total for Windows argument transport. Verify the encoded size before submitting; concise wording must preserve all required findings and actions. Ordinary wait intervals and healthy durations beyond two hours never mean completion; no scheduled wakeups are used. Full protocol and recovery instructions belong to the installed guide.

Source and Catalog upgrades preflight native runs before snapshot or target writes. Any unfinished, failed, aborted, unknown, missing, malformed or mismatched Clouds run blocks refresh and preserves the installed version. A legacy aborted state alone does not prove its CLI process stopped. Independently inspect processes and worktree activity, establish quiescence, preserve needed evidence, and manually retire the stale native run only when safe; then rerun the installer. Do not merely edit its status to completed or start another worker.
