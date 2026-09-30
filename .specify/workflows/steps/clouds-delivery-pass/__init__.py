"""Evidence-checked implementation/convergence pass for Clouds delivery."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from specify_cli.workflows.base import StepBase, StepContext, StepResult, StepStatus


_IMPLEMENT_STATUSES = frozenset({"completed", "approval_required", "blocked"})
_CONVERGE_STATUSES = frozenset(
    {"clean", "tasks_appended", "approval_required", "blocked"}
)
_UNCHECKED_TASK = re.compile(r"(?m)^\s*- \[ \]")
_STATUS_LINE = re.compile(
    r"^CLOUDS_(IMPLEMENTATION|CONVERGENCE): "
    r"(completed|clean|tasks_appended|approval_required|blocked)$"
)
_FINDINGS_LINE = re.compile(r"^CLOUDS_FINDINGS_JSON: (.+)$")
_TASK_CLASSES = frozenset(
    {
        "unknown",
        "mechanical",
        "routine",
        "high-risk-deterministic",
        "consequential",
        "ambiguous",
    }
)
_ASSIGNMENT_TRANSITION_KEYS = frozenset(
    {
        "role",
        "previous_assignment_id",
        "new_assignment_id",
        "selected_model",
        "bounded_purpose_digest",
        "bounded_purpose_description",
        "payload_digest",
        "expected_head",
        "rationale",
        "authority_ref",
    }
)
_ROLE_PURPOSES = {
    "builder": "Implement the accepted feature one local issue at a time and repair verified findings.",
    "reviewer": "Independently review the stable candidate without writing.",
}
_PHASE_PROMPTS = {
    "implementation": "Implement one bound local issue as the sole writer.",
    "repair": "Repair only the canonicalized reviewer findings as the sole writer.",
    "review": "Independently review the frozen candidate without writing.",
    "re-review": "Re-review the repaired frozen candidate without writing.",
}


class DeliveryEvidenceError(RuntimeError):
    """Raised when the agent result or repository evidence is not trustworthy."""


class CloudsDeliveryPassStep(StepBase):
    """Run one bounded delivery pass and verify its result independently."""

    type_key = "clouds-delivery-pass"

    def validate(self, config: dict[str, Any]) -> list[str]:
        errors = super().validate(config)
        previous = config.get("previous_step")
        if previous is not None and (not isinstance(previous, str) or not previous):
            errors.append(
                f"Clouds delivery step {config.get('id', '?')!r}: "
                "'previous_step' must be a non-empty string when present."
            )
        if "prepare_only" in config and not isinstance(config["prepare_only"], bool):
            errors.append(
                f"Clouds delivery step {config.get('id', '?')!r}: "
                "'prepare_only' must be a boolean when present."
            )
        return errors

    def execute(self, config: dict[str, Any], context: StepContext) -> StepResult:
        try:
            return self._execute(config, context)
        except DeliveryEvidenceError as exc:
            return StepResult(status=StepStatus.FAILED, error=str(exc))
        except (OSError, ValueError, KeyError, UnicodeError, json.JSONDecodeError) as exc:
            return StepResult(
                status=StepStatus.FAILED,
                error=f"Clouds delivery evidence check failed: {exc}",
            )

    def _execute(self, config: dict[str, Any], context: StepContext) -> StepResult:
        root = Path(context.project_root or ".").resolve()
        if not root.is_dir():
            raise DeliveryEvidenceError(f"Project root does not exist: {root}")

        step_id = str(config.get("id", ""))
        prior_self = self._step_output(context, step_id)
        prior = prior_self or self._step_output(context, config.get("previous_step"))

        authorization_ref = str(context.inputs.get("authorization_ref", "")).strip()
        if not authorization_ref:
            raise DeliveryEvidenceError(
                "Clouds delivery requires a non-empty authorization_ref naming the "
                "user's explicit local scope and implementation authorization."
            )
        requested_model = str(context.inputs.get("model", "")).strip()
        task_class = self._normalize_task_class(context.inputs.get("task_class", "unknown"))
        oracle_evidence = self._normalize_oracle_evidence(
            context.inputs.get("oracle_evidence", "")
        )
        model = self._require_selected_model(
            requested_model, task_class, oracle_evidence
        )
        astra_user_requested = str(
            context.inputs.get("astra_user_requested", "false")
        ).strip().lower()
        reviewer_model = str(context.inputs.get("reviewer_model", "")).strip()
        if not reviewer_model:
            raise DeliveryEvidenceError("Clouds delivery requires a non-empty reviewer model.")
        if (
            model.lower() == "gpt-6-astra" or reviewer_model.lower() == "gpt-6-astra"
        ) and astra_user_requested != "true":
            raise DeliveryEvidenceError(
                "Astra requires an explicit user request recorded in authorization evidence."
            )

        transition_raw = str(context.inputs.get("assignment_transition", ""))

        if config.get("prepare_only") is True:
            identity = prior_self.get("identity")
            if identity:
                self._verify_identity(
                    root, identity, model, reviewer_model, astra_user_requested,
                    authorization_ref, task_class, oracle_evidence
                )
            else:
                identity = self._capture_identity(
                    root, model, reviewer_model, astra_user_requested,
                    authorization_ref, task_class, oracle_evidence
                )
            return StepResult(
                status=StepStatus.COMPLETED,
                output={"status": "identity_captured", "identity": identity},
            )

        if prior_self.get("status") == "approval_required":
            return self._resume_approval(
                context,
                root,
                prior_self,
                authorization_ref,
                model,
                reviewer_model,
                astra_user_requested,
                task_class,
                oracle_evidence,
            )

        identity = prior.get("identity")
        if not isinstance(identity, dict):
            raise DeliveryEvidenceError(
                "Delivery run has no persisted authorization identity. Start a new "
                "authorized workflow run instead of resuming this legacy run."
            )
        transition_payload = self._resolve_transition_payload(
            transition_raw,
            str(context.inputs.get("reassessment_payload", "")),
            prior.get("review_findings", []),
        )
        self._apply_assignment_transition(
            identity,
            transition_raw,
            requested_model=model,
            requested_reviewer_model=reviewer_model,
            payload=transition_payload,
        )
        if transition_raw:
            context.inputs["assignment_transition"] = ""
            context.inputs["reassessment_payload"] = ""
        self._verify_identity(
            root, identity, model, reviewer_model, astra_user_requested,
            authorization_ref, task_class, oracle_evidence
        )

        if not prior_self and prior.get("status") == "clean":
            expected_tasks = prior.get("tasks_after_phase")
            if not isinstance(expected_tasks, dict):
                raise DeliveryEvidenceError(
                    "Previously clean delivery state has no valid task evidence. "
                    "Start a new authorized workflow run."
                )
            current_tasks = self._task_evidence(
                self._feature_file(root, identity, "tasks.md")
            )
            if current_tasks != expected_tasks:
                raise DeliveryEvidenceError(
                    "Previously clean task evidence changed before delivery resumed."
                )
            clean_revision = prior.get("clean_revision")
            if not isinstance(clean_revision, str) or not clean_revision:
                raise DeliveryEvidenceError(
                    "Previously clean delivery state has no final revision evidence. "
                    "Start a new authorized workflow run."
                )
            if self._current_head(root) != clean_revision:
                raise DeliveryEvidenceError(
                    "Git revision changed after the prior clean delivery result."
                )
            self._verify_baseline_worktree(root, identity)
            return StepResult(
                status=StepStatus.SKIPPED,
                output={**prior, "skipped": True, "reason": "already converged"},
            )

        tasks_path = self._feature_file(root, identity, "tasks.md")
        self._verify_baseline_worktree(root, identity)
        issues_before = self._issues_evidence(root, identity)
        active_issue = (
            None if prior.get("review_findings") else self._next_issue(issues_before)
        )
        if active_issue is None and not prior.get("review_findings"):
            raise DeliveryEvidenceError(
                "No open local issue remains for an implementation pass."
            )
        tasks_before = self._task_evidence(tasks_path)
        builder_head = self._require_expected_head(root, identity)
        self._record_invocation_binding(
            identity,
            "builder",
            "repair" if prior.get("review_findings") else "implementation",
            transition_payload
            if active_issue is None
            else {"issue": active_issue, "sha256": issues_before[active_issue]["sha256"]},
        )
        issue_prompt = (
            "Continue the active authorized feature. The user approved one local "
            "issue per builder pass. For this invocation, complete only "
            f"{identity['feature_directory']}/issues/{active_issue}, its listed "
            "tasks and tests, issue evidence, and one stable local checkpoint. "
            "Leave later issues untouched. Do not push or perform remote operations."
            if active_issue else
            "Repair the structured reviewer findings as the same bounded builder. "
            "Complete any affected tasks and verification, then commit a stable "
            "local checkpoint. Do not push or perform remote operations."
        )
        implementation = self._invoke(
            "implementation",
            "speckit.implement",
            issue_prompt + self._review_finding_context(prior),
            root,
            model,
        )
        self._advance_expected_head(
            identity,
            role="builder",
            before=builder_head,
            after=self._current_head(root),
        )
        if implementation["status"] == "approval_required":
            return self._pause(
                identity,
                "implementation",
                implementation,
                tasks_before,
                active_issue=active_issue,
                issues_before=issues_before,
            )
        if implementation["status"] == "blocked":
            raise DeliveryEvidenceError(
                "Implementation reported a blocker: " + implementation["message"]
            )

        self._verify_identity(
            root, identity, model, reviewer_model, astra_user_requested,
            authorization_ref, task_class, oracle_evidence
        )
        if active_issue is not None:
            return self._finish_issue_pass(
                root, identity, active_issue, issues_before, tasks_before,
                implementation["message"],
                model, reviewer_model, astra_user_requested,
                authorization_ref, task_class, oracle_evidence,
            )
        return self._run_convergence(
            root,
            model,
            reviewer_model,
            astra_user_requested,
            authorization_ref,
            identity,
            task_class,
            oracle_evidence,
            self._task_evidence(tasks_path),
            implementation["message"],
        )

    def _finish_issue_pass(
        self,
        root: Path,
        identity: dict[str, Any],
        active_issue: str,
        issues_before: dict[str, dict[str, Any]],
        tasks_before: dict[str, Any],
        implementation_message: str,
        model: str,
        reviewer_model: str,
        astra_user_requested: str,
        authorization_ref: str,
        task_class: str,
        oracle_evidence: str,
    ) -> StepResult:
        issues_after = self._issues_evidence(root, identity)
        if self._next_issue(issues_before) != active_issue:
            raise DeliveryEvidenceError("Completed issue was not the next open local issue.")
        if set(issues_after) != set(issues_before):
            raise DeliveryEvidenceError("Builder changed the local issue inventory.")
        for name in issues_before:
            if name != active_issue and issues_after[name] != issues_before[name]:
                raise DeliveryEvidenceError(
                    f"Builder changed {name} outside the bound issue pass."
                )
        if issues_after[active_issue]["unchecked"] != 0:
            raise DeliveryEvidenceError(
                f"Builder reported completion while {active_issue} remains open."
            )
        tasks_after = self._task_evidence(self._feature_file(root, identity, "tasks.md"))
        if tasks_after["unchecked"] >= tasks_before["unchecked"]:
            raise DeliveryEvidenceError(
                f"Builder completed {active_issue} without reducing unchecked tasks."
            )
        self._verify_baseline_worktree(root, identity)
        next_issue = self._next_issue(issues_after)
        if next_issue is not None:
            return StepResult(
                status=StepStatus.COMPLETED,
                output={
                    "status": "issue_completed",
                    "identity": identity,
                    "completed_issue": active_issue,
                    "next_issue": next_issue,
                    "issues_after_phase": issues_after,
                    "tasks_after_phase": tasks_after,
                    "implementation_message": implementation_message,
                    "pass_head": self._current_head(root),
                },
            )
        if tasks_after["unchecked"] != 0:
            raise DeliveryEvidenceError(
                "All local issues closed while tasks.md still has unchecked work."
            )
        self._verify_identity(
            root, identity, model, reviewer_model, astra_user_requested,
            authorization_ref, task_class, oracle_evidence,
        )
        return self._run_convergence(
            root, model, reviewer_model, astra_user_requested,
            authorization_ref, identity, task_class, oracle_evidence,
            tasks_after, implementation_message,
        )

    def _resume_approval(
        self,
        context: StepContext,
        root: Path,
        paused: dict[str, Any],
        authorization_ref: str,
        model: str,
        reviewer_model: str,
        astra_user_requested: str,
        task_class: str,
        oracle_evidence: str,
    ) -> StepResult:
        action = str(context.inputs.get("approval_action", "")).strip().lower()
        response = str(context.inputs.get("approval_response", "")).strip()
        if not action:
            return StepResult(status=StepStatus.PAUSED, output=paused)
        if action == "abort":
            return StepResult(
                status=StepStatus.FAILED,
                output={**paused, "aborted": True},
                error="Clouds delivery was aborted by the user at an approval boundary.",
            )
        if action != "resume" or not response:
            raise DeliveryEvidenceError(
                "Resume requires approval_action=resume and a non-empty "
                "approval_response containing the user's decision."
            )

        identity = paused.get("identity")
        if not isinstance(identity, dict):
            raise DeliveryEvidenceError("Paused delivery state has no valid run identity.")
        transition_raw = str(context.inputs.get("assignment_transition", ""))
        transition_payload = self._resolve_transition_payload(
            transition_raw,
            str(context.inputs.get("reassessment_payload", "")),
            paused.get("review_findings", []),
        )
        self._apply_assignment_transition(
            identity,
            transition_raw,
            requested_model=model,
            requested_reviewer_model=reviewer_model,
            payload=transition_payload,
        )
        if transition_raw:
            context.inputs["assignment_transition"] = ""
            context.inputs["reassessment_payload"] = ""
        self._verify_identity(
            root, identity, model, reviewer_model, astra_user_requested,
            authorization_ref, task_class, oracle_evidence
        )

        context.inputs["approval_action"] = ""
        context.inputs["approval_response"] = ""
        phase = paused.get("phase")
        prompt_suffix = (
            " The user has now answered the approval question: "
            + json.dumps(response, ensure_ascii=False)
            + ". Apply only that authorized decision."
        )
        tasks_path = self._feature_file(root, identity, "tasks.md")

        if phase == "implementation":
            active_issue = paused.get("active_issue")
            issues_before = paused.get("issues_before_phase")
            if active_issue is not None and (
                not isinstance(active_issue, str)
                or not isinstance(issues_before, dict)
                or active_issue not in issues_before
            ):
                raise DeliveryEvidenceError("Paused issue binding is invalid.")
            builder_head = self._require_expected_head(root, identity)
            self._record_invocation_binding(
                identity,
                "builder",
                "repair" if paused.get("review_findings") else "implementation",
                transition_payload
                if active_issue is None
                else {"issue": active_issue, "sha256": issues_before[active_issue]["sha256"]},
            )
            issue_prompt = (
                f"Resume only {identity['feature_directory']}/issues/{active_issue}. "
                "Finish its tests, task markers, issue evidence, and local checkpoint. "
                "Leave later issues untouched."
                if active_issue is not None
                else "Resume the paused reviewer-finding repair."
            )
            implementation = self._invoke(
                "implementation",
                "speckit.implement",
                issue_prompt
                + self._review_finding_context(paused)
                + prompt_suffix,
                root,
                model,
            )
            self._advance_expected_head(
                identity,
                role="builder",
                before=builder_head,
                after=self._current_head(root),
            )
            if implementation["status"] == "approval_required":
                return self._pause(
                    identity,
                    "implementation",
                    implementation,
                    self._task_evidence(tasks_path),
                    active_issue=active_issue,
                    issues_before=issues_before,
                )
            if implementation["status"] == "blocked":
                raise DeliveryEvidenceError(
                    "Implementation reported a blocker: "
                    + implementation["message"]
                )
            self._verify_identity(
                root, identity, model, reviewer_model, astra_user_requested,
                authorization_ref, task_class, oracle_evidence
            )
            if active_issue is not None:
                return self._finish_issue_pass(
                    root, identity, active_issue, issues_before,
                    paused.get("tasks_before_phase", {}), implementation["message"],
                    model, reviewer_model, astra_user_requested,
                    authorization_ref, task_class, oracle_evidence,
                )
            return self._run_convergence(
                root,
                model,
                reviewer_model,
                astra_user_requested,
                authorization_ref,
                identity,
                task_class,
                oracle_evidence,
                self._task_evidence(tasks_path),
                implementation["message"],
            )

        if phase == "convergence":
            reviewer_head = self._require_expected_head(root, identity)
            self._record_invocation_binding(
                identity, "reviewer", "review", paused.get("review_findings", [])
            )
            convergence = self._invoke(
                "convergence",
                "speckit.converge",
                "Resume the paused independent convergence review." + prompt_suffix,
                root,
                reviewer_model,
            )
            self._advance_expected_head(
                identity,
                role="reviewer",
                before=reviewer_head,
                after=self._current_head(root),
            )
            return self._finish_convergence(
                root,
                model,
                reviewer_model,
                astra_user_requested,
                authorization_ref,
                identity,
                task_class,
                oracle_evidence,
                paused.get("tasks_before_phase", {}),
                convergence,
                paused.get("implementation_message", ""),
            )

        raise DeliveryEvidenceError(f"Unknown paused phase: {phase!r}")

    def _run_convergence(
        self,
        root: Path,
        model: str,
        reviewer_model: str,
        astra_user_requested: str,
        authorization_ref: str,
        identity: dict[str, Any],
        task_class: str,
        oracle_evidence: str,
        tasks_before: dict[str, Any],
        implementation_message: str,
    ) -> StepResult:
        reviewer_head = self._require_expected_head(root, identity)
        phase = "re-review" if identity.get("review_generation", 0) else "review"
        self._record_invocation_binding(identity, "reviewer", phase, [])
        convergence = self._invoke(
            "convergence",
            "speckit.converge",
            "Independently assess the active feature as a read-only reviewer. Do not "
            "edit files, append tasks, or apply corrections. Report no findings as "
            "CLOUDS_FINDINGS_JSON: []; otherwise report a JSON array of objects with "
            "id, finding, and required_action before the terminal status. Do not trust "
            "the delivery loop as evidence of its own correctness.",
            root,
            reviewer_model,
        )
        self._advance_expected_head(
            identity,
            role="reviewer",
            before=reviewer_head,
            after=self._current_head(root),
        )
        identity["review_generation"] = int(identity.get("review_generation", 0)) + 1
        return self._finish_convergence(
            root,
            model,
            reviewer_model,
            astra_user_requested,
            authorization_ref,
            identity,
            task_class,
            oracle_evidence,
            tasks_before,
            convergence,
            implementation_message,
        )

    def _finish_convergence(
        self,
        root: Path,
        model: str,
        reviewer_model: str,
        astra_user_requested: str,
        authorization_ref: str,
        identity: dict[str, Any],
        task_class: str,
        oracle_evidence: str,
        tasks_before: dict[str, Any],
        convergence: dict[str, str],
        implementation_message: str,
    ) -> StepResult:
        self._verify_identity(
            root, identity, model, reviewer_model, astra_user_requested,
            authorization_ref, task_class, oracle_evidence
        )
        tasks_path = self._feature_file(root, identity, "tasks.md")
        tasks_after = self._task_evidence(tasks_path)
        status = convergence["status"]
        findings = convergence.get("findings", [])

        if status == "approval_required":
            if tasks_after != tasks_before:
                raise DeliveryEvidenceError(
                    "Convergence changed tasks while requesting approval."
                )
            return self._pause(
                identity,
                "convergence",
                convergence,
                tasks_before,
                implementation_message,
            )
        if status == "blocked":
            raise DeliveryEvidenceError(
                "Convergence reported a blocker: " + convergence["message"]
            )
        clean_revision = ""
        if status == "clean":
            if tasks_after != tasks_before:
                raise DeliveryEvidenceError(
                    "Convergence reported clean but changed tasks.md."
                )
            if tasks_after["unchecked"] != 0:
                raise DeliveryEvidenceError(
                    "Convergence reported clean while tasks.md still has unchecked tasks."
                )
            self._verify_baseline_worktree(root, identity)
            clean_revision = self._current_head(root)
        elif status == "tasks_appended":
            if tasks_after != tasks_before:
                raise DeliveryEvidenceError(
                    "Read-only convergence changed tasks.md; only the builder may apply corrections."
                )
            if not findings:
                raise DeliveryEvidenceError(
                    "Convergence reported tasks_appended without structured findings."
                )
        else:
            raise DeliveryEvidenceError(f"Unsupported convergence status: {status!r}")

        output = {
            "status": status,
            "identity": identity,
            "tasks_before_phase": tasks_before,
            "tasks_after_phase": tasks_after,
            "implementation_message": implementation_message,
            "convergence_message": convergence["message"],
            "review_findings": findings,
        }
        if clean_revision:
            output["clean_revision"] = clean_revision
            output["pass_head"] = clean_revision
        return StepResult(status=StepStatus.COMPLETED, output=output)

    def _pause(
        self,
        identity: dict[str, Any],
        phase: str,
        result: dict[str, str],
        tasks_before: dict[str, Any],
        implementation_message: str = "",
        *,
        active_issue: str | None = None,
        issues_before: dict[str, dict[str, Any]] | None = None,
    ) -> StepResult:
        question = self._message_body(result["message"])
        if not question:
            raise DeliveryEvidenceError(
                f"{phase.title()} requested approval without a concrete question."
            )
        return StepResult(
            status=StepStatus.PAUSED,
            output={
                "status": "approval_required",
                "phase": phase,
                "question": question,
                "identity": identity,
                "tasks_before_phase": tasks_before,
                "implementation_message": implementation_message,
                "pause_head": identity.get("expected_head", ""),
                "active_issue": active_issue,
                "issues_before_phase": issues_before,
            },
        )

    def _invoke(
        self,
        kind: str,
        command: str,
        args: str,
        root: Path,
        model: str,
        *,
        permission: str | None = None,
    ) -> dict[str, str]:
        completed = (
            self._run_codex(command, args, root, model)
            if permission is None
            else self._run_codex(
                command, args, root, model, permission=permission
            )
        )
        if completed.returncode != 0:
            # JSONL carries the actual turn error on stdout; stderr often has
            # only startup warnings. Keep the failure actionable without
            # dumping the full child transcript or tool arguments.
            failures: list[str] = []
            for raw in completed.stdout.splitlines():
                try:
                    event = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if not isinstance(event, dict):
                    continue
                if event.get("type") in {"error", "turn.failed"}:
                    value = event.get("error") or event.get("message")
                    failures.append(str(value)[:1200])
            detail = (
                " | ".join(failures[-3:])
                or (completed.stderr or completed.stdout or "no diagnostic").strip()[-1800:]
            )
            raise DeliveryEvidenceError(
                f"Codex {kind} command exited with {completed.returncode}: {detail}"
            )
        allowed = _IMPLEMENT_STATUSES if kind == "implementation" else _CONVERGE_STATUSES
        return self._parse_jsonl(completed.stdout, kind, allowed)

    @staticmethod
    def _require_selected_model(model: str, task_class: str, oracle_evidence: str) -> str:
        """Reject missing selections; the guide owns evidence-based model routing."""
        if not model:
            raise DeliveryEvidenceError("Clouds delivery requires a non-empty builder model.")
        normalized = oracle_evidence.lower()
        if task_class == "high-risk-deterministic" and (
            not normalized.startswith("complete:")
            or not normalized.removeprefix("complete:").strip()
        ):
            raise DeliveryEvidenceError(
                "High-risk deterministic delivery requires complete fail-before oracle evidence."
            )
        return model

    @staticmethod
    def _normalize_task_class(value: Any) -> str:
        task_class = str(value).strip().lower()
        return task_class if task_class in _TASK_CLASSES else "unknown"

    @staticmethod
    def _normalize_oracle_evidence(value: Any) -> str:
        return " ".join(str(value).split())

    @staticmethod
    def _oracle_evidence_sha256(oracle_evidence: str) -> str:
        return hashlib.sha256(oracle_evidence.encode("utf-8")).hexdigest()

    @staticmethod
    def _review_finding_context(prior: dict[str, Any]) -> str:
        findings = prior.get("review_findings")
        if not findings:
            return ""
        return (
            " Apply the following read-only reviewer findings; the builder alone must "
            "make any task or implementation changes: "
            + json.dumps(findings, ensure_ascii=False, sort_keys=True)
            + "."
        )

    @staticmethod
    def _run_codex(
        command: str,
        args: str,
        root: Path,
        model: str,
        *,
        permission: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        from specify_cli.integrations import get_integration

        integration = get_integration("codex")
        if integration is None:
            raise DeliveryEvidenceError("The official Codex integration is unavailable.")

        extra_args = os.environ.get("SPECKIT_INTEGRATION_CODEX_EXTRA_ARGS", "").strip()
        if extra_args:
            raise DeliveryEvidenceError(
                "SPECKIT_INTEGRATION_CODEX_EXTRA_ARGS is not allowed in the "
                "Clouds autonomous delivery loop because it can change permissions."
            )
        executable = os.environ.get(
            "SPECKIT_INTEGRATION_CODEX_EXECUTABLE", ""
        ).strip() or shutil.which("codex")
        if not executable:
            raise DeliveryEvidenceError("Codex CLI was not found.")

        child_env = os.environ.copy()
        for name in (
            "OPENAI_API_KEY",
            "OPENAI_BASE_URL",
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
        ):
            child_env.pop(name, None)

        try:
            login = subprocess.run(
                [executable, "login", "status"],
                cwd=str(root),
                env=child_env,
                text=True,
                capture_output=True,
                timeout=30,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise DeliveryEvidenceError("Codex login status timed out.") from exc
        login_text = (login.stdout + "\n" + login.stderr).lower()
        if login.returncode != 0 or "chatgpt" not in login_text or "api key" in login_text:
            raise DeliveryEvidenceError(
                "Codex must be signed in through ChatGPT before autonomous delivery; "
                "API-key or paid-API fallback is not allowed."
            )

        expected_permission = (
            "read-only" if command == "speckit.converge" else "workspace-write"
        )
        selected_permission = expected_permission if permission is None else permission
        if selected_permission not in {"read-only", "workspace-write"}:
            raise DeliveryEvidenceError("Codex dispatch has an invalid sandbox permission.")
        if command == "speckit.converge" and selected_permission != "read-only":
            raise DeliveryEvidenceError("Reviewer dispatch must use the read-only sandbox.")
        prompt = integration.build_command_invocation(command, args) if command else args
        argv = [
            executable,
            "exec",
            prompt,
            "--model",
            model,
        ]
        # Current Codex CLI makes --approve-for-me (workspace-write with
        # automatic approval review) mutually exclusive with --sandbox.
        # Preserve the builder's reviewed write sandbox and the reviewer's
        # explicit read-only sandbox as separate, valid launch modes.
        if selected_permission == "workspace-write":
            argv.append("--approve-for-me")
        else:
            argv.extend(("--sandbox", selected_permission))
        argv.extend(("--ephemeral", "--json"))
        try:
            return subprocess.run(
                argv,
                cwd=str(root),
                env=child_env,
                stdin=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=7200,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise DeliveryEvidenceError(
                f"Codex {command} exceeded the two-hour execution limit."
            ) from exc

    @staticmethod
    def _parse_jsonl(
        output: str, kind: str, allowed: frozenset[str]
    ) -> dict[str, str]:
        messages: list[str] = []
        for number, raw in enumerate(output.splitlines(), 1):
            if not raw.strip():
                continue
            try:
                event = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise DeliveryEvidenceError(
                    f"Codex {kind} output line {number} is not valid JSONL."
                ) from exc
            if not isinstance(event, dict):
                raise DeliveryEvidenceError(
                    f"Codex {kind} output line {number} is not a JSON object."
                )
            item = event.get("item")
            if (
                event.get("type") == "item.completed"
                and isinstance(item, dict)
                and item.get("type") == "agent_message"
                and isinstance(item.get("text"), str)
            ):
                messages.append(item["text"])

        if not messages:
            raise DeliveryEvidenceError(
                f"Codex {kind} output has no completed agent message."
            )
        message = messages[-1].strip()
        exact = [
            match
            for line in message.splitlines()
            if (match := _STATUS_LINE.fullmatch(line.strip()))
        ]
        if len(exact) != 1:
            raise DeliveryEvidenceError(
                f"Codex {kind} result must contain exactly one exact terminal status."
            )
        marker = exact[0]
        expected_kind = "IMPLEMENTATION" if kind == "implementation" else "CONVERGENCE"
        if marker.group(1) != expected_kind or marker.group(2) not in allowed:
            raise DeliveryEvidenceError(
                f"Codex {kind} returned an invalid terminal status."
            )
        if message.splitlines()[-1].strip() != marker.group(0):
            raise DeliveryEvidenceError(
                f"Codex {kind} terminal status is not the final non-empty line."
            )
        findings: list[dict[str, str]] = []
        if kind == "convergence":
            finding_lines = [
                match.group(1)
                for line in message.splitlines()
                if (match := _FINDINGS_LINE.fullmatch(line.strip()))
            ]
            if len(finding_lines) != 1:
                raise DeliveryEvidenceError(
                    "Codex convergence result must contain exactly one CLOUDS_FINDINGS_JSON line."
                )
            try:
                parsed_findings = json.loads(finding_lines[0])
            except json.JSONDecodeError as exc:
                raise DeliveryEvidenceError("Codex convergence findings are not valid JSON.") from exc
            if not isinstance(parsed_findings, list) or not all(
                isinstance(item, dict)
                and set(item) == {"id", "finding", "required_action"}
                and all(isinstance(item[key], str) and item[key].strip() for key in item)
                for item in parsed_findings
            ):
                raise DeliveryEvidenceError(
                    "Codex convergence findings must be a JSON array of id, finding, and required_action objects."
                )
            findings = parsed_findings
            if marker.group(2) == "clean" and findings:
                raise DeliveryEvidenceError("Clean convergence may not report unresolved findings.")
            if marker.group(2) == "tasks_appended" and not findings:
                raise DeliveryEvidenceError("tasks_appended convergence requires at least one finding.")
        return {"status": marker.group(2), "message": message, "findings": findings}

    @staticmethod
    def _message_body(message: str) -> str:
        lines = message.strip().splitlines()
        return "\n".join(lines[:-1]).strip() if lines else ""

    @staticmethod
    def _step_output(context: StepContext, step_id: Any) -> dict[str, Any]:
        if not isinstance(step_id, str) or not step_id:
            return {}
        data = context.steps.get(step_id, {})
        output = data.get("output", {}) if isinstance(data, dict) else {}
        return output if isinstance(output, dict) else {}

    def _capture_identity(
        self,
        root: Path,
        model: str,
        reviewer_model: str,
        astra_user_requested: str,
        authorization_ref: str,
        task_class: str,
        oracle_evidence: str,
    ) -> dict[str, Any]:
        branch = self._git(root, "branch", "--show-current").strip()
        if not branch or branch.lower() in {"main", "master"}:
            raise DeliveryEvidenceError(
                "Clouds delivery requires a named local development/task branch, not main."
            )
        feature_file = root / ".specify" / "feature.json"
        if not feature_file.is_file():
            raise DeliveryEvidenceError("No active Spec Kit feature.json was found.")
        feature_data = json.loads(feature_file.read_text(encoding="utf-8-sig"))
        feature_dir = feature_data.get("feature_directory")
        if not isinstance(feature_dir, str) or not feature_dir.strip():
            raise DeliveryEvidenceError("feature.json has no feature_directory.")
        resolved_feature = Path(feature_dir)
        if not resolved_feature.is_absolute():
            resolved_feature = root / resolved_feature
        resolved_feature = resolved_feature.resolve()
        try:
            relative_feature = resolved_feature.relative_to(root).as_posix()
        except ValueError as exc:
            raise DeliveryEvidenceError("Active feature directory escapes the project.") from exc
        for name in ("spec.md", "plan.md", "tasks.md"):
            if not (resolved_feature / name).is_file():
                raise DeliveryEvidenceError(f"Active feature is missing {name}.")
        checklist = resolved_feature / "checklists" / "requirements.md"
        if not checklist.is_file():
            raise DeliveryEvidenceError(
                "Active feature is missing checklists/requirements.md."
            )
        initial_head = self._current_head(root)
        builder_purpose = _ROLE_PURPOSES["builder"]
        reviewer_purpose = _ROLE_PURPOSES["reviewer"]
        builder_purpose_digest = self._canonical_sha256(
            {"purpose": builder_purpose}
        )
        reviewer_purpose_digest = self._canonical_sha256(
            {"purpose": reviewer_purpose}
        )
        return {
            "branch": branch,
            "feature_directory": relative_feature,
            "spec_sha256": self._sha256(resolved_feature / "spec.md"),
            "plan_sha256": self._sha256(resolved_feature / "plan.md"),
            "requirements_checklist_sha256": self._sha256(checklist),
            "baseline_worktree": self._worktree_evidence(root),
            "model": model,
            "reviewer_model": reviewer_model,
            "astra_user_requested": astra_user_requested,
            "authorization_ref": authorization_ref,
            "task_class": task_class,
            "oracle_evidence_sha256": self._oracle_evidence_sha256(oracle_evidence),
            "initial_head": initial_head,
            "expected_head": initial_head,
            "tag_refs_sha256": self._tag_refs_sha256(root),
            "builder_purpose": builder_purpose,
            "builder_purpose_digest": builder_purpose_digest,
            "reviewer_purpose": reviewer_purpose,
            "reviewer_purpose_digest": reviewer_purpose_digest,
            "builder_assignment_id": self._assignment_id(
                role="builder",
                selected_model=model,
                bounded_purpose_digest=builder_purpose_digest,
                authority_ref=authorization_ref,
            ),
            "reviewer_assignment_id": self._assignment_id(
                role="reviewer",
                selected_model=reviewer_model,
                bounded_purpose_digest=reviewer_purpose_digest,
                authority_ref=authorization_ref,
            ),
            "assignment_generation": {"builder": 0, "reviewer": 0},
            "phase_contract_sha256": {
                name: self._canonical_sha256({"phase": name, "prompt": prompt})
                for name, prompt in _PHASE_PROMPTS.items()
            },
            "invocation_bindings": [],
            "assignment_transition": None,
        }

    def _verify_identity(
        self,
        root: Path,
        identity: dict[str, Any],
        model: str,
        reviewer_model: str,
        astra_user_requested: str,
        authorization_ref: str,
        task_class: str,
        oracle_evidence: str,
    ) -> None:
        if authorization_ref != identity.get("authorization_ref"):
            raise DeliveryEvidenceError(
                "authorization_ref changed during the delivery run. Start a new "
                "authorized run instead of reusing this approval."
            )
        branch = self._git(root, "branch", "--show-current").strip()
        if branch != identity.get("branch"):
            raise DeliveryEvidenceError("Git branch changed during the delivery run.")
        if model != identity.get("model"):
            raise DeliveryEvidenceError("Delivery model changed during the delivery run.")
        if reviewer_model != identity.get("reviewer_model"):
            raise DeliveryEvidenceError("Reviewer model changed during the delivery run.")
        if astra_user_requested != identity.get("astra_user_requested"):
            raise DeliveryEvidenceError(
                "Astra authorization evidence changed during the delivery run."
            )
        if task_class != identity.get("task_class"):
            raise DeliveryEvidenceError(
                "Delivery task_class changed during the delivery run."
            )
        if self._oracle_evidence_sha256(oracle_evidence) != identity.get(
            "oracle_evidence_sha256"
        ):
            raise DeliveryEvidenceError(
                "Delivery oracle evidence changed during the delivery run."
            )
        feature_file = root / ".specify" / "feature.json"
        data = json.loads(feature_file.read_text(encoding="utf-8-sig"))
        raw_feature = data.get("feature_directory")
        if not isinstance(raw_feature, str):
            raise DeliveryEvidenceError("Active feature identity is no longer valid.")
        current = Path(raw_feature)
        if not current.is_absolute():
            current = root / current
        try:
            relative = current.resolve().relative_to(root).as_posix()
        except ValueError as exc:
            raise DeliveryEvidenceError("Active feature directory escapes the project.") from exc
        if relative != identity.get("feature_directory"):
            raise DeliveryEvidenceError("Active feature changed during the delivery run.")
        feature = root / relative
        if self._sha256(feature / "spec.md") != identity.get("spec_sha256"):
            raise DeliveryEvidenceError("Approved spec.md changed during the delivery run.")
        if self._sha256(feature / "plan.md") != identity.get("plan_sha256"):
            raise DeliveryEvidenceError("Approved plan.md changed during the delivery run.")
        checklist = feature / "checklists" / "requirements.md"
        if self._sha256(checklist) != identity.get("requirements_checklist_sha256"):
            raise DeliveryEvidenceError(
                "Approved checklists/requirements.md changed during the delivery run."
            )
        self._require_expected_head(root, identity)
        if self._tag_refs_sha256(root) != identity.get("tag_refs_sha256"):
            raise DeliveryEvidenceError("Git tag refs changed during the delivery run.")
        baseline = identity.get("baseline_worktree")
        if not isinstance(baseline, dict) or not isinstance(
            baseline.get("dirty_files"), dict
        ):
            raise DeliveryEvidenceError(
                "Delivery run has no valid baseline content evidence. Start a new "
                "authorized workflow run."
            )

    def _verify_baseline_worktree(
        self, root: Path, identity: dict[str, Any]
    ) -> None:
        baseline = identity.get("baseline_worktree")
        if not isinstance(baseline, dict):
            raise DeliveryEvidenceError(
                "Delivery run predates baseline content evidence. Start a new "
                "authorized run instead of resuming it."
            )
        current = self._worktree_evidence(root)
        if current.get("status") != baseline.get("status"):
            raise DeliveryEvidenceError(
                "Convergence reported clean but the worktree differs from its "
                "authorized-run baseline. Commit completed work and preserve "
                "unrelated changes before retrying."
            )
        if current.get("dirty_files") != baseline.get("dirty_files"):
            raise DeliveryEvidenceError(
                "Convergence reported clean but baseline dirty content changed. "
                "Restore or explicitly reconcile the user's preexisting changes."
            )

    @staticmethod
    def _canonical_json(value: Any) -> str:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )

    @classmethod
    def _canonical_sha256(cls, value: Any) -> str:
        return hashlib.sha256(cls._canonical_json(value).encode("utf-8")).hexdigest()

    @classmethod
    def _parse_reassessment_payload(cls, raw: str) -> dict[str, Any]:
        if raw == "":
            return {}
        duplicates: list[str] = []

        def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            result: dict[str, Any] = {}
            for key, value in pairs:
                if key in result:
                    duplicates.append(key)
                result[key] = value
            return result

        try:
            parsed = json.loads(
                raw,
                object_pairs_hook=pairs_hook,
                parse_constant=lambda value: (_ for _ in ()).throw(
                    ValueError(f"non-finite JSON value {value}")
                ),
            )
        except (json.JSONDecodeError, ValueError) as exc:
            raise DeliveryEvidenceError(
                "reassessment_payload is not valid strict JSON."
            ) from exc
        if duplicates:
            raise DeliveryEvidenceError(
                "reassessment_payload contains duplicate keys: "
                + ", ".join(sorted(set(duplicates)))
            )
        if not isinstance(parsed, dict):
            raise DeliveryEvidenceError("reassessment_payload must be one JSON object.")
        if cls._canonical_json(parsed) != raw:
            raise DeliveryEvidenceError("reassessment_payload is not canonical JSON.")
        return parsed

    @classmethod
    def _resolve_transition_payload(
        cls, transition_raw: str, reassessment_raw: str, findings: Any
    ) -> Any:
        if not isinstance(findings, list):
            raise DeliveryEvidenceError("Stored review findings are not a JSON array.")
        reassessment = cls._parse_reassessment_payload(reassessment_raw)
        if findings and reassessment:
            raise DeliveryEvidenceError(
                "A transition cannot bind both review findings and reassessment_payload."
            )
        if reassessment and not transition_raw:
            raise DeliveryEvidenceError(
                "reassessment_payload requires assignment_transition."
            )
        if transition_raw and not findings and not reassessment:
            raise DeliveryEvidenceError(
                "A non-finding assignment_transition requires reassessment_payload."
            )
        return findings if findings else reassessment if transition_raw else []

    @classmethod
    def _assignment_id(
        cls,
        *,
        role: str,
        selected_model: str,
        bounded_purpose_digest: str,
        authority_ref: str,
    ) -> str:
        if role not in {"builder", "reviewer"}:
            raise DeliveryEvidenceError(f"Unsupported assignment role: {role!r}")
        if not all(
            isinstance(value, str) and value.strip()
            for value in (selected_model, bounded_purpose_digest, authority_ref)
        ):
            raise DeliveryEvidenceError("Assignment identity fields must be non-empty strings.")
        return cls._canonical_sha256(
            {
                "authority_ref": authority_ref,
                "bounded_purpose_digest": bounded_purpose_digest,
                "role": role,
                "selected_model": selected_model,
            }
        )

    @classmethod
    def _parse_assignment_transition(
        cls,
        raw: str,
        *,
        role: str,
        active_assignment_id: str,
        expected_head: str,
        authority_ref: str,
        payload: Any,
        expected_new_assignment_id: str,
    ) -> dict[str, str]:
        if not raw:
            raise DeliveryEvidenceError("An empty assignment transition has no parsed value.")
        duplicates: list[str] = []

        def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            result: dict[str, Any] = {}
            for key, value in pairs:
                if key in result:
                    duplicates.append(key)
                result[key] = value
            return result

        try:
            parsed = json.loads(raw, object_pairs_hook=pairs_hook)
        except json.JSONDecodeError as exc:
            raise DeliveryEvidenceError("assignment_transition is not valid JSON.") from exc
        if duplicates:
            raise DeliveryEvidenceError(
                "assignment_transition contains duplicate keys: "
                + ", ".join(sorted(set(duplicates)))
            )
        if not isinstance(parsed, dict):
            raise DeliveryEvidenceError("assignment_transition must be one JSON object.")
        keys = set(parsed)
        if keys != _ASSIGNMENT_TRANSITION_KEYS:
            missing = sorted(_ASSIGNMENT_TRANSITION_KEYS - keys)
            extra = sorted(keys - _ASSIGNMENT_TRANSITION_KEYS)
            raise DeliveryEvidenceError(
                f"assignment_transition keys are invalid; missing={missing}, extra={extra}."
            )
        if not all(isinstance(value, str) for value in parsed.values()):
            raise DeliveryEvidenceError("assignment_transition values must all be strings.")
        if cls._canonical_json(parsed) != raw:
            raise DeliveryEvidenceError("assignment_transition is not canonical JSON.")
        if any(not value.strip() for value in parsed.values()):
            raise DeliveryEvidenceError("assignment_transition fields must be non-empty.")
        if parsed["role"] != role:
            raise DeliveryEvidenceError("assignment_transition role does not match dispatch role.")
        if parsed["previous_assignment_id"] != active_assignment_id:
            raise DeliveryEvidenceError(
                "assignment_transition previous_assignment_id is not active."
            )
        if parsed["expected_head"] != expected_head:
            raise DeliveryEvidenceError("assignment_transition expected_head is stale.")
        if parsed["authority_ref"] != authority_ref:
            raise DeliveryEvidenceError("assignment_transition authority_ref changed.")
        if parsed["payload_digest"] != cls._canonical_sha256(payload):
            raise DeliveryEvidenceError("assignment_transition payload digest is invalid.")
        if parsed["bounded_purpose_digest"] != cls._canonical_sha256(
            {"purpose": parsed["bounded_purpose_description"]}
        ):
            raise DeliveryEvidenceError("assignment_transition purpose digest is invalid.")
        recomputed = cls._assignment_id(
            role=role,
            selected_model=parsed["selected_model"],
            bounded_purpose_digest=parsed["bounded_purpose_digest"],
            authority_ref=parsed["authority_ref"],
        )
        if parsed["new_assignment_id"] != recomputed:
            raise DeliveryEvidenceError("assignment_transition new_assignment_id is invalid.")
        if recomputed != expected_new_assignment_id:
            raise DeliveryEvidenceError(
                "assignment_transition does not match the requested model and purpose."
            )
        return {key: parsed[key] for key in sorted(parsed)}

    def _apply_assignment_transition(
        self,
        identity: dict[str, Any],
        raw: str,
        *,
        requested_model: str,
        requested_reviewer_model: str,
        payload: Any,
    ) -> None:
        if not raw:
            return
        raw_digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        if identity.get("assignment_transition_sha256") == raw_digest:
            stored = identity.get("assignment_transition")
            if not isinstance(stored, dict) or stored.get(
                "payload_digest"
            ) != self._canonical_sha256(payload):
                raise DeliveryEvidenceError(
                    "Replayed assignment_transition payload digest is invalid."
                )
            return
        try:
            preview = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise DeliveryEvidenceError("assignment_transition is not valid JSON.") from exc
        if not isinstance(preview, dict) or preview.get("role") not in {
            "builder",
            "reviewer",
        }:
            raise DeliveryEvidenceError("assignment_transition has no valid role.")
        role = str(preview["role"])
        model = requested_model if role == "builder" else requested_reviewer_model
        purpose_description = preview.get("bounded_purpose_description")
        purpose_digest = self._canonical_sha256({"purpose": purpose_description})
        expected_new = self._assignment_id(
            role=role,
            selected_model=model,
            bounded_purpose_digest=purpose_digest,
            authority_ref=str(identity.get("authorization_ref", "")),
        )
        parsed = self._parse_assignment_transition(
            raw,
            role=role,
            active_assignment_id=str(identity.get(f"{role}_assignment_id", "")),
            expected_head=str(identity.get("expected_head", "")),
            authority_ref=str(identity.get("authorization_ref", "")),
            payload=payload,
            expected_new_assignment_id=expected_new,
        )
        old_purpose_digest = identity.get(f"{role}_purpose_digest")
        old_model = identity.get("model" if role == "builder" else "reviewer_model")
        if parsed["new_assignment_id"] == parsed["previous_assignment_id"]:
            if model != old_model or purpose_digest != old_purpose_digest:
                raise DeliveryEvidenceError(
                    "A same-ID assignment continuation cannot change model or purpose."
                )
        else:
            generations = identity.setdefault("assignment_generation", {})
            generations[role] = int(generations.get(role, 0)) + 1
        identity[f"{role}_assignment_id"] = parsed["new_assignment_id"]
        identity[f"{role}_purpose"] = parsed["bounded_purpose_description"]
        identity[f"{role}_purpose_digest"] = parsed["bounded_purpose_digest"]
        identity["model" if role == "builder" else "reviewer_model"] = model
        identity["assignment_transition"] = parsed
        identity["assignment_transition_sha256"] = raw_digest
        identity["assignment_transition_payload_sha256"] = self._canonical_sha256(payload)
        identity["reassessment_payload"] = payload if isinstance(payload, dict) else {}

    @classmethod
    def _record_invocation_binding(
        cls,
        identity: dict[str, Any],
        role: str,
        phase: str,
        payload: Any,
        *,
        expected_head: str | None = None,
    ) -> dict[str, str]:
        phase_hashes = identity.get("phase_contract_sha256", {})
        if phase not in phase_hashes:
            raise DeliveryEvidenceError(f"Unauthorized delivery phase contract: {phase!r}")
        payload_digest = cls._canonical_sha256(payload)
        binding = {
            "assignment_id": str(identity.get(f"{role}_assignment_id", "")),
            "expected_head": str(
                identity.get("expected_head", "")
                if expected_head is None
                else expected_head
            ),
            "payload_digest": payload_digest,
            "phase": phase,
            "phase_contract_sha256": str(phase_hashes[phase]),
            "role": role,
        }
        binding["invocation_binding_id"] = cls._canonical_sha256(binding)
        identity.setdefault("invocation_bindings", []).append(binding)
        return binding

    @staticmethod
    def _current_head(root: Path) -> str:
        completed = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=str(root),
            text=True,
            encoding="utf-8",
            errors="strict",
            capture_output=True,
            timeout=30,
            check=False,
        )
        if completed.returncode == 0:
            value = completed.stdout.strip()
            if not re.fullmatch(r"[0-9a-fA-F]{40,64}", value):
                raise DeliveryEvidenceError("Git returned a malformed HEAD revision.")
            return value.lower()
        symbolic = subprocess.run(
            ["git", "symbolic-ref", "-q", "HEAD"],
            cwd=str(root),
            text=True,
            encoding="utf-8",
            errors="strict",
            capture_output=True,
            timeout=30,
            check=False,
        )
        if symbolic.returncode == 0 and symbolic.stdout.strip():
            return "UNBORN"
        raise DeliveryEvidenceError(
            "Unable to establish the current Git HEAD: "
            + (completed.stderr or completed.stdout).strip()
        )

    @classmethod
    def _require_expected_head(cls, root: Path, identity: dict[str, Any]) -> str:
        expected = identity.get("expected_head")
        if not isinstance(expected, str) or not (
            expected == "UNBORN" or re.fullmatch(r"[0-9a-f]{40,64}", expected)
        ):
            raise DeliveryEvidenceError("Delivery identity has no valid expected_head.")
        current = cls._current_head(root)
        if current != expected:
            raise DeliveryEvidenceError(
                f"Git HEAD drifted before dispatch/resume: expected {expected}, found {current}."
            )
        return current

    @staticmethod
    def _advance_expected_head(
        identity: dict[str, Any], *, role: str, before: str, after: str
    ) -> None:
        if before != identity.get("expected_head"):
            raise DeliveryEvidenceError("Dispatch did not start from expected_head.")
        if role == "reviewer" and after != before:
            raise DeliveryEvidenceError("Read-only reviewer changed Git HEAD.")
        if role != "builder" and role != "reviewer":
            raise DeliveryEvidenceError(f"Unsupported transition role: {role!r}")
        if role == "builder":
            if after == "UNBORN" and before != "UNBORN":
                raise DeliveryEvidenceError("Builder produced an invalid UNBORN transition.")
            identity["post_builder_head"] = after
            identity["expected_head"] = after

    @classmethod
    def _tag_refs_sha256(cls, root: Path) -> str:
        completed = subprocess.run(
            ["git", "for-each-ref", "--format=%(refname) %(objectname)", "refs/tags"],
            cwd=str(root),
            text=True,
            encoding="utf-8",
            errors="strict",
            capture_output=True,
            timeout=30,
            check=False,
        )
        if completed.returncode != 0:
            raise DeliveryEvidenceError(
                "Unable to inspect Git tag refs: "
                + (completed.stderr or completed.stdout).strip()
            )
        lines = sorted(line for line in completed.stdout.splitlines() if line)
        return hashlib.sha256(("\n".join(lines) + ("\n" if lines else "")).encode("utf-8")).hexdigest()

    @staticmethod
    def _feature_file(root: Path, identity: dict[str, Any], name: str) -> Path:
        feature = (root / str(identity["feature_directory"])).resolve()
        try:
            feature.relative_to(root)
        except ValueError as exc:
            raise DeliveryEvidenceError("Stored feature directory escapes the project.") from exc
        path = feature / name
        if not path.is_file():
            raise DeliveryEvidenceError(f"Active feature is missing {name}.")
        return path

    @staticmethod
    def _task_evidence(path: Path) -> dict[str, Any]:
        content = path.read_bytes()
        text = content.decode("utf-8-sig")
        return {
            "sha256": hashlib.sha256(content).hexdigest(),
            "unchecked": len(_UNCHECKED_TASK.findall(text)),
        }

    @staticmethod
    def _issues_evidence(
        root: Path, identity: dict[str, Any]
    ) -> dict[str, dict[str, Any]]:
        feature = (root / str(identity["feature_directory"])).resolve()
        try:
            feature.relative_to(root)
        except ValueError as exc:
            raise DeliveryEvidenceError("Stored feature directory escapes the project.") from exc
        issue_dir = feature / "issues"
        if not issue_dir.is_dir():
            raise DeliveryEvidenceError("Active feature has no local issues directory.")
        files = sorted(
            path for path in issue_dir.glob("[0-9][0-9]-*.md") if path.is_file()
        )
        if not files:
            raise DeliveryEvidenceError("Active feature has no numbered local issues.")
        evidence: dict[str, dict[str, Any]] = {}
        for path in files:
            try:
                path.resolve().relative_to(issue_dir.resolve())
            except ValueError as exc:
                raise DeliveryEvidenceError("Local issue escapes its directory.") from exc
            content = path.read_bytes()
            text = content.decode("utf-8-sig")
            total = len(re.findall(r"(?m)^\s*- \[[ xX]\]", text))
            if total == 0:
                raise DeliveryEvidenceError(f"Local issue {path.name} has no checkboxes.")
            evidence[path.name] = {
                "sha256": hashlib.sha256(content).hexdigest(),
                "unchecked": len(_UNCHECKED_TASK.findall(text)),
                "total": total,
            }
        return evidence

    @staticmethod
    def _next_issue(issues: dict[str, dict[str, Any]]) -> str | None:
        return next(
            (name for name in sorted(issues) if issues[name]["unchecked"]),
            None,
        )

    @staticmethod
    def _sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @classmethod
    def _worktree_evidence(cls, root: Path) -> dict[str, Any]:
        raw = cls._git(
            root,
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
            "--",
            ".",
            ":(exclude).specify/workflows/runs/**",
            ":(exclude).specify/feature.json",
        )
        tokens = raw.split("\0")
        statuses: list[str] = []
        paths: set[str] = set()
        index = 0
        while index < len(tokens):
            record = tokens[index]
            index += 1
            if not record:
                continue
            if len(record) < 4 or record[2] != " ":
                raise DeliveryEvidenceError("git status returned malformed evidence.")
            code = record[:2]
            path = record[3:]
            statuses.append(f"{code} {path}")
            paths.add(path)
            if "R" in code or "C" in code:
                if index >= len(tokens) or not tokens[index]:
                    raise DeliveryEvidenceError(
                        "git status returned incomplete rename evidence."
                    )
                source = tokens[index]
                index += 1
                statuses.append(f"{code} source:{source}")
                paths.add(source)

        return {
            "status": sorted(statuses),
            "dirty_files": {
                path: cls._dirty_path_evidence(root, path)
                for path in sorted(paths)
            },
        }

    @classmethod
    def _dirty_path_evidence(cls, root: Path, relative: str) -> dict[str, Any]:
        candidate = Path(os.path.abspath(root / Path(relative)))
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise DeliveryEvidenceError(
                "git status returned a path outside the project."
            ) from exc

        index_state = cls._git(root, "ls-files", "--stage", "--", relative).strip()
        if not os.path.lexists(candidate):
            return {"kind": "missing", "index": index_state}
        if candidate.is_symlink():
            return {
                "kind": "symlink",
                "target": os.readlink(candidate),
                "index": index_state,
            }
        if candidate.is_file():
            return {
                "kind": "file",
                "sha256": cls._sha256(candidate),
                "index": index_state,
            }
        if candidate.is_dir():
            raise DeliveryEvidenceError(
                "A dirty Git directory or gitlink cannot be safely fingerprinted. "
                f"Commit, restore, or explicitly reconcile it before delivery: {relative}"
            )
        stat_result = candidate.stat()
        return {
            "kind": "other",
            "mode": stat_result.st_mode,
            "size": stat_result.st_size,
            "index": index_state,
        }

    @staticmethod
    def _git(root: Path, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(root),
            text=True,
            encoding="utf-8",
            errors="strict",
            capture_output=True,
            timeout=30,
            check=False,
        )
        if completed.returncode != 0:
            raise DeliveryEvidenceError(
                f"git {' '.join(args)} failed: "
                + (completed.stderr or completed.stdout).strip()
            )
        return completed.stdout
