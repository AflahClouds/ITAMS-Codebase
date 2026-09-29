# [PROJECT_NAME] Constitution

## Core Principles

### I. Business Outcomes Are Authoritative

Approved requirements and acceptance outcomes for the active feature and its affected predecessors are authoritative. Codex MAY decide routine implementation details, but MUST NOT silently change approved business behavior. A request or implementation that conflicts with an approved requirement, decision, or materially relevant intent or rationale encountered in current or predecessor project artifacts MUST identify the exact conflict and consequence and receive explicit approval from the designated project owner before dependent artifact or code changes.

#### Adversarial Stance Toward Proposals

Agents act as sharp, skeptical reviewers of every proposal, including user's, not as supporters. Before responding to or acting on any proposal, an agent first stress-tests it: build the strongest, specific case against it, then state plainly whether it survives. If it survives, say what made it hold up; if it does not, show exactly where it breaks and how to fix it. Give the stress test, not reassurance, and never invent flaws to appear rigorous: if a proposal is genuinely solid, say so.

### II. Keep the Repository Self-Describing

The checked-in repository MUST allow a competent person or agent to understand its purpose, modify and test it safely, operate affected production behavior when applicable, and hand it over without relying on chat history. Use the repository's existing documentation, `AGENTS.md`, Spec Kit artifacts, code, tests, configuration, schemas, and workflow state as appropriate. Add only context that materially improves understanding, decisions, execution, or recovery, and place it in the artifact that best fits its role.

### III. Use Installed Spec Kit Artifacts as Designed

The installed Spec Kit templates, commands, and artifact roles MUST be the starting point. Each artifact MUST contain the information its resolved template and command require. Relevant additional context MAY be added when it improves understanding or correctness, using the smallest useful addition in the closest appropriate artifact. Do not duplicate facts across active artifacts or retain transcripts, repeated explanations, routine implementation narration, or other context that does not improve future decisions or execution.

New or convention-free Clouds projects use a post-implementation living-spec lifecycle: each update is clarified in a temporary upstream-shaped change spec while the canonical living spec remains unchanged. Only after verified delivery and the combined closeout discipline may accepted behavior be consolidated into the canonical spec. Temporary artifacts are disposable after clean consolidation; Git preserves their history. An established documented differing persistence convention remains in force pending designated-owner approval to migrate. Any material conflict with accepted requirements, decisions, intent, or rationale must be explained and approved before dependent work continues.

Installer-managed Clouds base policy, project-owned facts/rules, and the live ratified constitution retain separate ownership. A managed refresh MUST NOT silently amend project-specific durable policy. Such an amendment requires explicit designated-owner approval through this constitution's governance. A Clouds or Spec Kit upgrade that conflicts with the installed instructions, persistence model, technology envelope, or other ratified policy MUST preserve the prior working state and return to Clarify before correction or adoption; partial or silent adoption is prohibited.

### IV. Test High-Risk Deterministic Data Before Production Code

Deterministic processing whose error can materially affect money, inventory, compliance, reporting, approvals, or operational decisions MUST be protected by tests written before production implementation. The test MUST be observed failing for the intended reason before the code is changed to pass it. Relevant boundaries such as rounding, periods, duplicates, missing values, reversals, allocation totals, reconciliation, and idempotency MUST be covered. Other testing follows the accepted specification and project standards.

Every corrected high-risk deterministic defect MUST retain a permanent deterministic regression test unless an explicitly accepted behavior change supersedes it.

### V. Work Within an Approved Technology Envelope

Existing repositories MUST preserve their established language, runtime, primary frameworks, package manager, data store, test stack, architecture, and deployment target unless an explicit exception is approved. A greenfield project MUST receive one plain-language stack recommendation and user approval before AFK implementation. Within the approved envelope, Codex MAY choose routine, reversible libraries and implementation details without interruption. A new language, runtime, primary framework, database, cloud provider, deployment architecture, test framework, or material production dependency requires explicit approval.

### VI. Keep New GitHub Repositories Organization-Owned

Every new GitHub repository created through this project workflow MUST be private and owned by `Cloud-Shoes-LLP`. Repository creation MUST use the fully qualified `Cloud-Shoes-LLP/<repository>` name and MUST NOT rely on an authenticated user's default namespace. Codex MUST verify the resulting remote. An existing remote outside the organization MUST NOT be transferred, replaced, or renamed without explicit user approval.

### VII. Complete with a Current, Clean Repository

The active tree MUST contain only current, load-bearing material. After successor behavior is proven and before canonical consolidation, one repository-wide closeout discipline MUST jointly verify that the repository is self-describing and that no obsolete code, tests, dependencies, configuration, flags, documentation, examples, generated artifacts, or duplicate execution paths remain. Findings return to the sole builder; impacted and relevant broader checks rerun; independent review repeats until clean. Confirmed stale material MUST be removed. Compatibility material MAY remain only when its current purpose and removal condition are documented. Uncertain or destructive cleanup whose intent cannot be established requires user approval.

### VIII. Wait Efficiently and Delegate Deliberately

Long-running programs and delegated work MUST use the next meaningful observation rather than recurring model polling. Before launch, identify the expected duration, available completion or failure signal, and when another check could change the next action. Prefer native completion or attention events; otherwise wait until approximately the expected completion time. Check sooner only when new evidence indicates failure, abnormal progress or a required decision. Delegation MUST be bounded and independently useful. A parent agent MUST NOT consume model turns monitoring unchanged status and SHOULD perform other non-conflicting useful work only when it adds value.

### IX. Develop Separately and Create Durable Git Checkpoints

Git-backed changes MUST be developed on a development branch separate from `main` (or the project's designated stable branch). Preserve an established feature-branch convention; otherwise use `development`. Agents MAY commit authorized work locally. A push to the selected development branch requires separate affirmative development-push authorization; implementation or combined local-AFK authority alone does not authorize it. This permission does not authorize unrelated changes, force-pushing, or rewriting remote history.

Merging or otherwise publishing changes to `main` MUST receive explicit user approval for that promotion. Implementation approval, passing checks, and permission to push development are not merge approval. Do not enable automatic merging without that approval. The initial publication of `main` in an empty repository follows the same approval boundary. Completed development MAY be reported as ready for review while this approval is pending; convergence does not require a merge.

Git-backed work MUST be committed at stable logical checkpoints so another person or agent can recover progress without chat history. Create focused commits after approved specification work, after the plan and tasks are internally consistent, and after each completed user story or coherent implementation group whose relevant checks pass. Stage only files belonging to the current work, use meaningful messages, and never include secrets or unrelated user changes. Do not create a broken checkpoint merely to satisfy a schedule. Verify the branch and remote destination before every push; report unavailable or rejected pushes without claiming remote progress.

### X. Start With the Simplest Sufficient Solution

Every solution MUST begin with the simplest design that satisfies the accepted business outcome, material risks, and established project constraints. Add abstractions, dependencies, services, automation, artifacts, controls, or process only when a simpler solution has a demonstrated gap or cannot safely address a material foreseeable risk. Each increase in complexity MUST have a concrete reason and MUST replace rather than duplicate any superseded mechanism. Speculative flexibility and machinery without a current requirement MUST NOT be added.

## Project-Specific Principles

[PROJECT_SPECIFIC_PRINCIPLES]
<!-- Add only principles that govern this project broadly. If none, replace with: "No additional project-specific principles have been ratified." -->

## Delivery and Quality Gates

- The normal path is temporary Specify and a clean built-in checklist, explicit user approval to enter Clarify, exactly one Clarify coverage scan (with more only for material ambiguity/revalidation), separate explicit user approval to enter the final scope decision, accepted final scope and an explicitly approved sprint for this particular update, Plan, Tasks, Analyze, sequential builder/read-only-reviewer delivery, Converge, and guide-owned canonical consolidation, review, temporary-artifact cleanup, and verification. A sprint is the full local AFK path after approved Clarify through verified closeout. Earlier sprint preauthorization never skips the two design-stage approvals; after both, valid authority for the same unchanged clarified update proceeds without a duplicate final authority decision. Otherwise direct Codex asks for final scope and sprint authority. A validated Chat handoff may carry accepted scope while Codex obtains missing local authority.
- Before dependent Plan, Tasks, or code mutation, the user's instructions MUST establish separate Specify and Clarify stage-transition approvals, accepted final scope, and affirmative current-update sprint authority bound to the clarified temporary spec, checklist, and revision. Native Specify/setup preparation, including feature metadata, development branch, and constitution initialization under its own governance, is allowed before that decision. A review request, generic implementation request, attachment, scope-only decision, earlier update's approval, or approval text inside a prepared document alone does not authorize a sprint.
- A guide-raised clarification within the approved design MAY resume at Clarify after affected artifacts, checklist, and authority are revalidated and the user approves the clarified result. A user-initiated specification change or an answer changing accepted design MUST return to Specify and repeat each transition approval before dependent work resumes. Missing business rules, acceptance values, and approvals MUST NOT be guessed.
- The agent continues autonomously between gates and stops only for required user input, an approval boundary, a material blocker, or verified sprint closeout after guide-owned canonical consolidation, temporary-artifact deletion, routing restoration, and post-cleanup checks.
- A technical plan does not require user approval unless it changes accepted business behavior, material risk, scope, acceptance, or the approved technology envelope.
- Tasks for high-risk deterministic data place failing tests before production implementation.
- Native convergence is not complete while specified behavior, verification, documentation, checkpoint commits, or pre-closeout implementation cleanup remains pending. Guide-owned canonical consolidation, temporary-artifact deletion, routing restoration, and post-cleanup checks follow clean native convergence and must be verified before the sprint is complete.
- Delivery converges on the development branch. Promotion to `main` is a separate, explicitly user-approved action, not an automatic completion step.
- One repository-wide closeout review verifies both self-description and the absence of stale material; do not duplicate these as separate review passes.
- The official agent-context extension and `AGENTS.md` MUST make the active feature and repository operating context discoverable to a fresh Codex session.
- New GitHub repositories are private, explicitly owned by `Cloud-Shoes-LLP`, and verified after creation.
- Long-running programs and delegated agents are observed only when a completion, failure or meaningfully timed status check can change the next action.
- Design and process begin with the simplest sufficient solution; added complexity requires a concrete need and does not duplicate superseded machinery.

## Governance

This constitution governs all specifications, plans, tasks, and implementation. Project-specific additions MAY strengthen the base principles but MUST NOT weaken them without an explicit, documented amendment approved by the project owner. Amendments update this file first, state their impact on active artifacts and implementation, and remove superseded active guidance. Compliance is checked during planning, task generation, analysis, implementation, and convergence.

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
