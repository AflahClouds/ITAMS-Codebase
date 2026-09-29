## Clouds v1 planning policy

## Clouds living-spec addition

- Only after separate explicit Specify and Clarify stage approvals, accepted final scope, and current-update sprint authority, planning continues without a routine user gate. Analyze runs automatically when plan and tasks exist.
- Plan temporary-to-canonical traceability and one combined closeout discipline, but do not create or modify the canonical living spec before verified delivery.
- Record the trusted source, expected Git/checklist identity, assignment boundaries, durable-policy owner, hard stops, and applicable Sites destination decision. Start with the simplest sufficient solution; justify added runtime/token/context/maintenance cost and remove superseded overlap.
- Plan guide-owned canonical review and safe temporary-artifact cleanup with relevant post-cleanup verification. Do not make an installed project's delivery workflow run this repository's candidate or release checks.

- Existing repositories stay inside the technology envelope recorded in `AGENTS.md`. For greenfield work, planning may proceed only after that envelope has been approved. A new language, runtime, primary framework, database, cloud provider, deployment architecture, test framework, or material production dependency is an exception requiring explicit approval.
- Follow upstream Phase 0: consolidate researched unknowns, dependencies, integrations, and technology choices in `research.md` using Decision, Rationale, and Alternatives considered. Do not copy that reasoning into `spec.md`, promote it into a Clouds-specific register, or create a separate decision file.
- Identify every affected predecessor that the plan will supersede: code, tests, dependencies, configuration, feature flags, documentation, and duplicate execution paths. State how successor behavior will be proven before removal. Keep the scan bounded to the behavior and architecture being changed.
- A routine technical plan inside the accepted behavior and approved envelope does not require user approval.
- Provide a concise business-facing plan review when the user asks for one or when planning exposes a material choice. Cover requirement traceability, operational impact, controls, data obligations, material risks, exclusions, and acceptance coverage. Pause only when resolving the issue would change accepted business behavior, scope, acceptance, material risk, or the approved technology envelope.
- Treat the temporary feature as a disposable delivery artifact: plan its traceable consolidation into the canonical living specification and deletion only after clean post-workflow review and verification.
