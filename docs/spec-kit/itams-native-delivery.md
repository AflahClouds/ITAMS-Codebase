# ITAMS native delivery issue gate

The installed Clouds Spec Kit 1.5.0 step at
.specify/workflows/steps/clouds-delivery-pass/__init__.py contains a
project-owned adaptation authorized for feature 014 on 2026-09-30 and reaffirmed
on 2026-10-07. The upstream 1.5.0 step dispatched the whole feature in one
builder pass. ITAMS constitution 1.1.0 requires work from sequential local
Markdown issues. This adaptation is intentional installed-step customization,
separate from the project policy preset that composes command guidance.

The step retains the 1.5.0 native request and result schemas, request digests,
assignment and host-child bindings, revision and worktree checks, read-only
review snapshots, approval pauses, and twelve-pass workflow. It launches no
Codex CLI workers. An implementation request carries the next open numbered
issue and the full pre-pass issue inventory in its digest-bound payload. A
completed builder result must leave other issue files unchanged, keep every
acceptance criterion's text and checkbox, close the bound issue criteria,
reduce unchecked tasks,
and produce a clean local Git checkpoint. A middle issue returns
tasks_appended, letting the next native pass bind the next issue. No reviewer
is dispatched while another implementation issue remains. Approval resumes
retain the original issue inventory, task-progress baseline, and checkpoint
start; a non-finding assignment reassessment remains in the digest-bound
issue request.

The final issue has one criterion that can only be verified by independent
review. The builder may leave only its exact "Frozen candidate receives
independent read-only review..." checkbox open; every other final criterion and
task must be complete before the reviewer starts. The step rejects removal or
premature checking of that criterion. A clean review binds the same builder to
record the review evidence and commit it, then sends the stable result to the
same reviewer for re-review. Reviewer findings still follow the native
builder-repair and reviewer-re-review path. Clean completion requires no open
issue or task checkboxes and the original worktree baseline.

Before any later Clouds upgrade, compare the incoming step with this local
adaptation. Preserve the issue gate and run its regressions before replacing
the installed step; do not silently remove it or reinstate feature-wide
dispatch. The supported Spec Kit loader imports this installed step directly.
The project policy preset in docs/spec-kit/itams-policy-preset/ addresses
guidance composition; it does not generate the step. No remote publication is
authorized for feature 014.

Focused verification, using the pinned Spec Kit 1.0.13 interpreter:

    & 'C:\Users\aflah.vk\AppData\Roaming\uv\tools\specify-cli\Scripts\python.exe' -m unittest discover -s .specify/workflows/tests -p test_issue_delivery.py -v

The regression fixture uses a temporary Git repository and drives the native
step through paused requests and strict result JSON. Its first fail-before run
on the upgraded step exited 1 because the issue-selection gate was absent;
a later step-level red case demonstrated that the final review-owned criterion
could not advance to review. These failures were observed before the repair.
