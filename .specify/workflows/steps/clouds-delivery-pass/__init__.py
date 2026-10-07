"""Evidence-checked implementation/convergence pass for Clouds delivery.

ITAMS project-owned issue gate: see docs/spec-kit/itams-native-delivery.md before
refreshing this installed Clouds step.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

# Parse help before importing the pinned engine; dispatch reads use its existing interpreter.
if __name__ == "__main__":
    import argparse
    import importlib.metadata
    parser = argparse.ArgumentParser(description="Read the exact paused native Clouds dispatch request.")
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    try:
        if importlib.metadata.version("specify-cli") != "1.0.13":
            parser.exit(1, "Use the existing Spec Kit v1.0.13 tool interpreter.\n")
    except importlib.metadata.PackageNotFoundError:
        parser.exit(1, "Use the existing Spec Kit v1.0.13 tool interpreter.\n")

from specify_cli.workflows.base import StepBase, StepContext, StepResult, StepStatus


_IMPLEMENT_STATUSES = frozenset({"completed", "approval_required", "blocked"})
_RESULT_MAX_BYTES = 8192  # Leaves headroom for Windows quoting of the resume argument.
_CONVERGE_STATUSES = frozenset(
    {"clean", "tasks_appended", "approval_required", "blocked"}
)
_UNCHECKED_TASK = re.compile(r"(?m)^\s*- \[ \]")
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
_REVIEW_CRITERION = (
    "Frozen candidate receives independent read-only review; the same builder repairs "
    "and the same reviewer re-reviews; commits stay local."
)
_ROLE_PURPOSES = {
    "builder": "Implement the bound local issue, repair verified findings, or record verified final review evidence.",
    "reviewer": "Independently review the stable candidate without writing.",
}
_PHASE_PROMPTS = {
    "implementation": "Implement one bound local issue, its tests and tasks, and a stable checkpoint as the sole writer.",
    "repair": "Repair canonicalized reviewer findings or record verified final review evidence as the sole writer.",
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
            return StepResult(status=StepStatus.FAILED, error=str(exc), output=self._step_output(context, config.get("id")))
        except (OSError, ValueError, KeyError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
            return StepResult(
                status=StepStatus.FAILED,
                error=f"Clouds delivery evidence check failed: {exc}",
                output=self._step_output(context, config.get("id")),
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

        identity = prior.get("identity")
        if not isinstance(identity, dict):
            raise DeliveryEvidenceError("Delivery has no persisted identity; do not resume a legacy run.")
        # A result may advance only the exact role request already saved by the engine.
        result_raw = context.inputs.pop("dispatch_result", "")
        context.inputs["dispatch_result"] = ""
        if prior_self.get("status") == "dispatch_required":
            request = self._verify_pending_request(prior_self.get("request"), identity)
            if request["run_id"] != context.run_id or request["step_id"] != step_id:
                raise DeliveryEvidenceError("Pending request belongs to another run or pass.")
            role = request["role"]
            if transition_raw or context.inputs.get("reassessment_payload"):
                raise DeliveryEvidenceError("Cannot change an assignment while its child is pending.")
            if not result_raw:
                self._verify_identity(root, identity, model, reviewer_model, astra_user_requested, authorization_ref, task_class, oracle_evidence)
                return StepResult(status=StepStatus.PAUSED, output=prior_self)
            result = self._parse_result(result_raw, request)
            if role == "reviewer":
                after = self._review_snapshot(root, str(context.run_id))
                if after != prior_self.get("review_snapshot"):
                    return StepResult(status=StepStatus.FAILED, error="Read-only reviewer changed HEAD, index or worktree; preserve evidence and recover safely.", output={**prior_self, "review_after": after, "rejected_result": result})
            bindings = identity.setdefault("child_bindings", {})
            assignment = request["assignment_id"]
            bound = bindings.get(assignment)
            if bound and bound != result["child_id"]:
                raise DeliveryEvidenceError("Result conflicts with the assignment's existing host child.")
            if result["child_id"] in [child for key, child in bindings.items() if key != assignment]:
                raise DeliveryEvidenceError("Builder and reviewer must be distinct host children.")
            bindings[assignment] = result["child_id"]
            self._advance_expected_head(identity, role=role, before=request["expected_head"], after=self._current_head(root))
            self._verify_identity(root, identity, model, reviewer_model, astra_user_requested, authorization_ref, task_class, oracle_evidence)
            identity.setdefault("consumed_requests", []).append(request["digest"])
            if result["status"] == "blocked":
                return StepResult(status=StepStatus.FAILED, error=result["message"], output={**prior_self, "terminal_result": result})
            if result["status"] == "approval_required":
                if not result["message"].strip():
                    raise DeliveryEvidenceError("Approval requires a concrete question.")
                return StepResult(status=StepStatus.PAUSED, output={"status": "approval_required", "identity": identity, "role": role, "phase": request["phase"], "question": result["message"], "review_findings": request["payload"] if isinstance(request["payload"], list) else [], "resume_payload": request["payload"], "tasks_before_phase": request["payload"].get("tasks_before", request["tasks"]) if isinstance(request["payload"], dict) else request["tasks"], "issue_initial_head": request["payload"].get("issue_initial_head", request["expected_head"]) if isinstance(request["payload"], dict) else request["expected_head"], "implementation_message": prior_self.get("implementation_message", "")})
            if role == "builder":
                if request["phase"] == "implementation":
                    return self._finish_issue_pass(
                        context, config, root, identity, request, result["message"]
                    )
                if request["phase"] == "repair" and isinstance(request["payload"], dict):
                    if "review_completion_issue" in request["payload"]:
                        return self._finish_review_evidence(
                            context, config, root, identity, request, result["message"]
                        )
                    wrapper = request["payload"]
                    if (set(wrapper) != {"approval_response", "prior_payload"} or
                            not isinstance(wrapper["approval_response"], str) or
                            not wrapper["approval_response"].strip() or
                            not isinstance(wrapper["prior_payload"], list) or
                            not wrapper["prior_payload"]):
                        raise DeliveryEvidenceError("Repair approval lost its bound review findings.")
                return self._dispatch(context, config, root, identity, "reviewer", "re-review" if identity.get("review_generation") else "review", [], result["message"])
            identity["review_generation"] = int(identity.get("review_generation", 0)) + 1
            tasks_after = self._task_evidence(self._feature_file(root, identity, "tasks.md"))
            if tasks_after != request["tasks"]:
                raise DeliveryEvidenceError("Read-only reviewer changed tasks evidence.")
            if result["status"] == "clean":
                if tasks_after["unchecked"]:
                    raise DeliveryEvidenceError("Clean result has unchecked tasks.")
                issues_after = self._issues_evidence(root, identity)
                open_issue = self._next_issue(issues_after)
                self._verify_baseline_worktree(root, identity)
                if open_issue:
                    if not self._review_criterion_pending(
                        root, identity, open_issue, issues_after
                    ):
                        raise DeliveryEvidenceError(
                            "Clean review left unrelated local issue criteria open."
                        )
                    return self._dispatch(
                        context, config, root, identity, "builder", "repair",
                        {
                            "review_completion_issue": open_issue,
                            "issues_before": issues_after,
                            "review_child_id": result["child_id"],
                        },
                        result["message"],
                    )
            return StepResult(status=StepStatus.COMPLETED, output={"status": result["status"], "identity": identity, "review_findings": result["findings"], "tasks_after_phase": tasks_after, "clean_revision": self._current_head(root) if result["status"] == "clean" else "", "convergence_message": result["message"]})
        if result_raw:
            raise DeliveryEvidenceError("Stale or replayed result without a pending request.")
        payload = self._resolve_transition_payload(transition_raw, str(context.inputs.get("reassessment_payload", "")), prior.get("review_findings", []))
        self._apply_assignment_transition(identity, transition_raw, requested_model=model, requested_reviewer_model=reviewer_model, payload=payload)
        if transition_raw:
            context.inputs["assignment_transition"] = ""
            context.inputs["reassessment_payload"] = ""
        self._verify_identity(root, identity, model, reviewer_model, astra_user_requested, authorization_ref, task_class, oracle_evidence)
        if prior_self.get("status") == "approval_required":
            action = context.inputs.pop("approval_action", "")
            response = context.inputs.pop("approval_response", "")
            context.inputs.update(approval_action="", approval_response="")
            if not action:
                return StepResult(status=StepStatus.PAUSED, output=prior_self)
            if action == "abort":
                return StepResult(status=StepStatus.FAILED, output={**prior_self, "aborted": True}, error="User aborted delivery.")
            if action != "resume" or not isinstance(response, str) or not response.strip():
                raise DeliveryEvidenceError("Resume requires approval_action=resume and a concrete user response.")
            if prior_self["role"] == "builder" and prior_self["phase"] == "implementation":
                bound = prior_self.get("resume_payload")
                if not isinstance(bound, dict) or not {"issue", "issues_before"} <= set(bound):
                    raise DeliveryEvidenceError("Approval resume lost its bound local issue.")
                resumed = dict(bound)
                resumed["approval_response"] = response
                resumed["tasks_before"] = prior_self["tasks_before_phase"]
                resumed["issue_initial_head"] = prior_self["issue_initial_head"]
                if transition_raw:
                    resumed["reassessment"] = payload
                payload = resumed
            elif (
                prior_self["role"] == "builder"
                and prior_self["phase"] == "repair"
                and isinstance(prior_self.get("resume_payload"), dict)
                and "review_completion_issue" in prior_self["resume_payload"]
            ):
                bound = prior_self["resume_payload"]
                if set(bound) != {"review_completion_issue", "issues_before", "review_child_id"}:
                    raise DeliveryEvidenceError("Approval resume lost its bound final review evidence.")
                resumed = dict(bound)
                resumed["approval_response"] = response
                if transition_raw:
                    resumed["reassessment"] = payload
                payload = resumed
            elif prior_self["role"] == "builder" and prior_self["phase"] == "repair":
                bound = prior_self.get("resume_payload")
                if isinstance(bound, dict):
                    if set(bound) != {"approval_response", "prior_payload"}:
                        raise DeliveryEvidenceError("Repair approval lost its bound review findings.")
                    bound = bound["prior_payload"]
                if not isinstance(bound, list) or not bound:
                    raise DeliveryEvidenceError("Repair approval has no bound review findings.")
                payload = {
                    "approval_response": response,
                    "prior_payload": payload if transition_raw else bound,
                }
            else:
                payload = {"approval_response": response, "prior_payload": payload if transition_raw else prior_self.get("resume_payload", payload)}
            return self._dispatch(context, config, root, identity, prior_self["role"], prior_self["phase"], payload, prior_self.get("implementation_message", ""))
        if prior.get("status") == "clean":
            if self._task_evidence(self._feature_file(root, identity, "tasks.md")) != prior.get("tasks_after_phase") or self._current_head(root) != prior.get("clean_revision"):
                raise DeliveryEvidenceError("Previously clean task or revision evidence changed.")
            self._verify_baseline_worktree(root, identity)
            return StepResult(status=StepStatus.SKIPPED, output={**prior, "skipped": True})
        if prior.get("review_findings"):
            return self._dispatch(context, config, root, identity, "builder", "repair", payload)
        if prior.get("completed_issue"):
            if (self._current_head(root) != prior.get("pass_head") or
                    self._task_evidence(self._feature_file(root, identity, "tasks.md")) != prior.get("tasks_after_phase") or
                    self._issues_evidence(root, identity) != prior.get("issues_after_phase")):
                raise DeliveryEvidenceError("Completed local issue evidence changed before the next pass.")
            self._verify_baseline_worktree(root, identity)
        return self._dispatch(
            context, config, root, identity, "builder", "implementation",
            self._issue_payload(root, identity, payload if transition_raw else None),
        )

    def _finish_issue_pass(
        self, context, config, root, identity, request, implementation_message
    ):
        payload = request["payload"]
        allowed = {"issue", "issues_before", "reassessment", "approval_response", "tasks_before", "issue_initial_head"}
        if (not isinstance(payload, dict) or not {"issue", "issues_before"} <= set(payload) or
                not set(payload) <= allowed):
            raise DeliveryEvidenceError("Implementation request has no bound local issue.")
        if ("reassessment" in payload and
                payload["reassessment"] != identity.get("reassessment_payload")):
            raise DeliveryEvidenceError("Bound issue reassessment payload changed.")
        active_issue, issues_before = payload["issue"], payload["issues_before"]
        if (not isinstance(active_issue, str) or not isinstance(issues_before, dict) or
                self._next_issue(issues_before) != active_issue):
            raise DeliveryEvidenceError("Implementation request did not bind the next open issue.")
        issues_after = self._issues_evidence(root, identity)
        if set(issues_after) != set(issues_before):
            raise DeliveryEvidenceError("Builder changed the local issue inventory.")
        for name in issues_before:
            if name != active_issue and issues_after[name] != issues_before[name]:
                raise DeliveryEvidenceError(
                    f"Builder changed {name} outside the bound issue pass."
                )
        before = issues_before[active_issue]
        after = issues_after[active_issue]
        review_owned = self._review_criterion_pending(
            root, identity, active_issue, issues_after
        )
        if (not isinstance(before, dict) or before.get("unchecked", 0) == 0 or
                after["total"] != before.get("total") or
                after["criteria"] != before.get("criteria") or
                (after["unchecked"] != 0 and not review_owned) or
                (before.get("review_criterion") == "unchecked" and not review_owned)):
            raise DeliveryEvidenceError(
                f"Builder reported completion while {active_issue} criteria remain open or were removed."
            )
        if (active_issue == sorted(issues_after)[-1] and
                self._review_criterion_state(root, identity, active_issue) == "checked"):
            raise DeliveryEvidenceError(
                "Final review criterion was checked before independent review."
            )
        tasks_after = self._task_evidence(self._feature_file(root, identity, "tasks.md"))
        tasks_before = payload.get("tasks_before", request["tasks"])
        if not isinstance(tasks_before, dict) or tasks_after["unchecked"] >= tasks_before["unchecked"]:
            raise DeliveryEvidenceError(
                f"Builder completed {active_issue} without reducing unchecked tasks."
            )
        if self._current_head(root) == payload.get("issue_initial_head", request["expected_head"]):
            raise DeliveryEvidenceError(
                f"Builder completed {active_issue} without a Git checkpoint."
            )
        self._verify_baseline_worktree(root, identity)
        next_issue = self._next_issue(issues_after)
        if next_issue and not review_owned:
            return StepResult(
                status=StepStatus.COMPLETED,
                output={
                    "status": "tasks_appended",
                    "identity": identity,
                    "completed_issue": active_issue,
                    "next_issue": next_issue,
                    "issues_after_phase": issues_after,
                    "tasks_after_phase": tasks_after,
                    "implementation_message": implementation_message,
                    "pass_head": self._current_head(root),
                    "review_findings": [],
                },
            )
        if tasks_after["unchecked"]:
            raise DeliveryEvidenceError(
                "Final review cannot begin while tasks.md still has unchecked work."
            )
        return self._dispatch(
            context, config, root, identity, "reviewer",
            "re-review" if identity.get("review_generation") else "review",
            [], implementation_message,
        )

    def _finish_review_evidence(
        self, context, config, root, identity, request, implementation_message
    ):
        payload = request["payload"]
        required = {"review_completion_issue", "issues_before", "review_child_id"}
        optional = {"approval_response", "reassessment"}
        if (not isinstance(payload, dict) or not required <= set(payload) or
                not set(payload) <= required | optional or
                ("approval_response" in payload and
                 (not isinstance(payload["approval_response"], str) or
                  not payload["approval_response"].strip())) or
                ("reassessment" in payload and
                 payload["reassessment"] != identity.get("reassessment_payload")) or
                not isinstance(payload["review_child_id"], str) or
                payload["review_child_id"] != identity.get("child_bindings", {}).get(
                    identity["reviewer_assignment_id"]
                )):
            raise DeliveryEvidenceError("Final review evidence request is not bound to the verified reviewer.")
        issue = payload["review_completion_issue"]
        issues_before = payload["issues_before"]
        if (not isinstance(issue, str) or not isinstance(issues_before, dict) or
                issue not in issues_before or issue != sorted(issues_before)[-1] or
                issues_before[issue]["unchecked"] != 1 or
                issues_before[issue].get("review_criterion") != "unchecked"):
            raise DeliveryEvidenceError("Final review evidence did not start from the one review-owned criterion.")
        issues_after = self._issues_evidence(root, identity)
        if set(issues_after) != set(issues_before):
            raise DeliveryEvidenceError("Review evidence changed the local issue inventory.")
        for name in issues_before:
            if name != issue and issues_after[name] != issues_before[name]:
                raise DeliveryEvidenceError(
                    f"Builder changed {name} outside the bound review evidence pass."
                )
        if (issues_after[issue]["total"] != issues_before[issue]["total"] or
                issues_after[issue]["criteria"] != issues_before[issue]["criteria"] or
                issues_after[issue]["unchecked"] != 0 or
                self._review_criterion_state(root, identity, issue) != "checked"):
            raise DeliveryEvidenceError("Verified final review criterion remains open or was removed.")
        if self._task_evidence(self._feature_file(root, identity, "tasks.md")) != request["tasks"]:
            raise DeliveryEvidenceError("Final review evidence changed the completed task ledger.")
        if self._current_head(root) == request["expected_head"]:
            raise DeliveryEvidenceError("Final review evidence has no Git checkpoint.")
        self._verify_baseline_worktree(root, identity)
        return self._dispatch(
            context, config, root, identity, "reviewer", "re-review",
            [], implementation_message,
        )

    def _dispatch(self, context, config, root, identity, role, phase, payload, implementation_message=""):
        self._require_expected_head(root, identity)
        binding = self._record_invocation_binding(identity, role, phase, payload)
        request = {
            "protocol_version": 1, "run_id": context.run_id, "step_id": config["id"],
            "role": role, "phase": phase, "assignment_id": identity[f"{role}_assignment_id"],
            "selected_model": identity["model" if role == "builder" else "reviewer_model"],
            "purpose": identity[f"{role}_purpose"], "expected_head": identity["expected_head"],
            "tasks": self._task_evidence(self._feature_file(root, identity, "tasks.md")),
            "payload": payload, "invocation_binding_id": binding["invocation_binding_id"],
            "sequence": len(identity.get("invocation_bindings", [])),
        }
        request["digest"] = self._canonical_sha256(request)
        self._validate_request(request)
        output = {"status": "dispatch_required", "identity": identity, "request": request, "implementation_message": implementation_message}
        if role == "reviewer":
            output["review_snapshot"] = self._review_snapshot(root, str(context.run_id))
        return StepResult(status=StepStatus.PAUSED, output=output)

    @staticmethod
    def _strict_json(raw, limit=65536):
        if not isinstance(raw, str) or len(raw.encode("utf-8")) > limit:
            raise DeliveryEvidenceError("JSON input exceeds its byte limit or is not text.")
        def pairs(items):
            value = {}
            for key, item in items:
                if key in value:
                    raise DeliveryEvidenceError("JSON contains duplicate keys.")
                value[key] = item
            return value
        try:
            return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda value: (_ for _ in ()).throw(DeliveryEvidenceError("Nonfinite JSON value.")))
        except (ValueError, RecursionError) as exc:
            raise DeliveryEvidenceError("Malformed or excessively nested JSON input.") from exc

    @classmethod
    def _validate_request(cls, request):
        keys = {"protocol_version", "run_id", "step_id", "role", "phase", "assignment_id", "selected_model", "purpose", "expected_head", "tasks", "payload", "invocation_binding_id", "sequence", "digest"}
        if not isinstance(request, dict) or set(request) != keys or type(request["protocol_version"]) is not int or request["protocol_version"] != 1:
            raise DeliveryEvidenceError("Invalid native request schema.")
        if len(cls._canonical_json(request).encode("utf-8")) > 65536:
            raise DeliveryEvidenceError("Native request exceeds byte limit.")
        for key in keys - {"protocol_version", "tasks", "payload", "sequence"}:
            if not isinstance(request[key], str) or not request[key].strip() or len(request[key]) > (16000 if key == "purpose" else 256):
                raise DeliveryEvidenceError("Invalid native request field: " + key)
        if request["role"] not in {"builder", "reviewer"} or request["phase"] not in ({"implementation", "repair"} if request["role"] == "builder" else {"review", "re-review"}):
            raise DeliveryEvidenceError("Invalid native request role/phase.")
        if not isinstance(request["payload"], (dict, list)) or not isinstance(request["tasks"], dict) or set(request["tasks"]) != {"sha256", "unchecked"} or type(request["tasks"]["unchecked"]) is not int or request["tasks"]["unchecked"] < 0:
            raise DeliveryEvidenceError("Invalid request task/payload evidence.")
        if type(request["sequence"]) is not int or request["sequence"] < 1 or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", request["run_id"]):
            raise DeliveryEvidenceError("Invalid request sequence or run ID.")
        for value in (request["assignment_id"], request["invocation_binding_id"], request["digest"], request["tasks"]["sha256"]):
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                raise DeliveryEvidenceError("Invalid request digest evidence.")
        if request["digest"] != cls._canonical_sha256({k:v for k,v in request.items() if k != "digest"}):
            raise DeliveryEvidenceError("Native request digest mismatch.")
        return request

    @classmethod
    def _verify_pending_request(cls, request, identity):
        request = cls._validate_request(request)
        if not isinstance(identity, dict):
            raise DeliveryEvidenceError("Pending request has no retained identity/binding.")
        role, phase = request["role"], request["phase"]
        bindings = identity.get("invocation_bindings")
        contracts = identity.get("phase_contract_sha256")
        if (not isinstance(bindings, list) or not bindings or
                request["sequence"] != len(bindings) or
                not isinstance(contracts, dict) or phase not in contracts):
            raise DeliveryEvidenceError("Pending request sequence/phase conflicts with retained binding.")
        binding = {
            "assignment_id": request["assignment_id"],
            "expected_head": request["expected_head"],
            "payload_digest": cls._canonical_sha256(request["payload"]),
            "phase": phase, "phase_contract_sha256": contracts[phase], "role": role,
        }
        binding["invocation_binding_id"] = cls._canonical_sha256(binding)
        if (bindings[-1] != binding or request["invocation_binding_id"] != binding["invocation_binding_id"] or
                request["assignment_id"] != identity.get(f"{role}_assignment_id") or
                request["selected_model"] != identity.get("model" if role == "builder" else "reviewer_model") or
                request["purpose"] != identity.get(f"{role}_purpose") or
                request["expected_head"] != identity.get("expected_head") or
                request["digest"] in identity.get("consumed_requests", [])):
            raise DeliveryEvidenceError("Pending request conflicts with retained identity/binding or was consumed.")
        return request

    @classmethod
    def _parse_result(cls, raw, request):
        result = cls._strict_json(raw, _RESULT_MAX_BYTES)
        keys = {"protocol_version", "request_digest", "child_id", "role", "status", "message", "findings"}
        if not isinstance(result, dict) or set(result) != keys or type(result["protocol_version"]) is not int or result["protocol_version"] != 1:
            raise DeliveryEvidenceError("Invalid native result schema or unknown field.")
        if result["request_digest"] != request["digest"] or result["role"] != request["role"]:
            raise DeliveryEvidenceError("Stale native result digest or wrong role.")
        if not isinstance(result["child_id"], str) or not result["child_id"].strip() or len(result["child_id"]) > 256:
            raise DeliveryEvidenceError("Missing bounded host child identity.")
        allowed = _IMPLEMENT_STATUSES if result["role"] == "builder" else _CONVERGE_STATUSES
        if result["status"] not in allowed or not isinstance(result["message"], str) or len(result["message"]) > 4000:
            raise DeliveryEvidenceError("Invalid role status or message limit.")
        findings = result["findings"]
        if not isinstance(findings, list) or len(findings) > 100:
            raise DeliveryEvidenceError("Findings exceed count limit.")
        seen = set()
        for item in findings:
            if not isinstance(item, dict) or set(item) != {"id", "finding", "required_action"}:
                raise DeliveryEvidenceError("Invalid finding fields.")
            for key, value in item.items():
                if not isinstance(value, str) or not value.strip() or len(value) > (128 if key == "id" else 4000):
                    raise DeliveryEvidenceError("Invalid finding text limit.")
            if item["id"] in seen:
                raise DeliveryEvidenceError("Duplicate finding ID.")
            seen.add(item["id"])
        if (result["status"] == "tasks_appended") != bool(findings):
            raise DeliveryEvidenceError("Status and findings disagree.")
        return result

    @classmethod
    def _review_snapshot(cls, root, run_id):
        # Only this engine run's bookkeeping can change around a paused dispatch.
        prefix = f".specify/workflows/runs/{run_id}/"
        def bookkeeping(path):
            if not path.startswith(prefix):
                return False
            name = path[len(prefix):]
            return name in {"state.json", "inputs.json", "log.jsonl"} or bool(
                re.fullmatch(r"\.(state|inputs)\.json\.[^/]+\.tmp", name)
            )
        paths = cls._git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split("\0")
        inventory = sorted({p for p in paths if p and not bookkeeping(p)})
        index = cls._git(root, "ls-files", "--stage", "-z")
        # Engine bookkeeping never stages files, so every index entry is covered.
        index_entries = sorted(p for p in index.split("\0") if p)
        files = {}
        for relative in inventory:
            candidate = root / relative
            if not candidate.resolve().is_relative_to(root) and not candidate.is_symlink():
                raise DeliveryEvidenceError("Review path escapes the project.")
            if candidate.is_symlink():
                files[relative] = {"kind": "symlink", "target": os.readlink(candidate)}
            elif not os.path.lexists(candidate):
                files[relative] = {"kind": "missing"}
            elif candidate.is_file():
                files[relative] = {"kind": "file", "sha256": cls._sha256(candidate), "executable": bool(candidate.stat().st_mode & 0o111)}
            else:
                raise DeliveryEvidenceError("Review cannot fingerprint a gitlink/directory or special file: " + relative)
        return {"head": cls._current_head(root), "index": index_entries, "files": files}

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
        files = sorted(path for path in issue_dir.glob("[0-9][0-9]-*.md") if path.is_file())
        if not files:
            raise DeliveryEvidenceError("Active feature has no numbered local issues.")
        evidence = {}
        for path in files:
            try:
                path.resolve().relative_to(issue_dir.resolve())
            except ValueError as exc:
                raise DeliveryEvidenceError("Local issue escapes its directory.") from exc
            content = path.read_bytes()
            text = content.decode("utf-8-sig")
            total = len(re.findall(r"(?m)^\s*- \[[ xX]\]", text))
            if not total:
                raise DeliveryEvidenceError(f"Local issue {path.name} has no checkboxes.")
            lines = text.splitlines()
            review_criterion = (
                "unchecked" if f"- [ ] {_REVIEW_CRITERION}" in lines
                else "checked" if f"- [x] {_REVIEW_CRITERION}" in lines
                else None
            )
            evidence[path.name] = {
                "sha256": hashlib.sha256(content).hexdigest(),
                "unchecked": len(_UNCHECKED_TASK.findall(text)),
                "total": total,
                "criteria": re.findall(r"(?m)^\s*- \[[ xX]\] (.*)$", text),
                "review_criterion": review_criterion,
            }
        return evidence

    @staticmethod
    def _review_criterion_state(
        root: Path, identity: dict[str, Any], issue: str
    ) -> str | None:
        path = root / str(identity["feature_directory"]) / "issues" / issue
        text = path.read_text(encoding="utf-8-sig")
        unchecked = f"- [ ] {_REVIEW_CRITERION}"
        checked = f"- [x] {_REVIEW_CRITERION}"
        if unchecked in text.splitlines():
            return "unchecked"
        if checked in text.splitlines():
            return "checked"
        return None

    @classmethod
    def _review_criterion_pending(
        cls, root: Path, identity: dict[str, Any], issue: str,
        issues: dict[str, dict[str, Any]]
    ) -> bool:
        if issue != sorted(issues)[-1] or issues[issue]["unchecked"] != 1:
            return False
        if cls._review_criterion_state(root, identity, issue) != "unchecked":
            return False
        path = root / str(identity["feature_directory"]) / "issues" / issue
        unchecked = re.findall(r"(?m)^\s*- \[ \] (.*)$", path.read_text(encoding="utf-8-sig"))
        return unchecked == [_REVIEW_CRITERION]

    @staticmethod
    def _next_issue(issues: dict[str, dict[str, Any]]) -> str | None:
        return next(
            (name for name in sorted(issues) if issues[name]["unchecked"]),
            None,
        )

    def _issue_payload(
        self, root: Path, identity: dict[str, Any],
        reassessment: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        issues = self._issues_evidence(root, identity)
        active = self._next_issue(issues)
        if active is None:
            raise DeliveryEvidenceError("No open local issue remains for an implementation pass.")
        payload = {"issue": active, "issues_before": issues}
        if reassessment is not None:
            if not isinstance(reassessment, dict) or not reassessment:
                raise DeliveryEvidenceError("Non-finding issue reassessment must be a nonempty object.")
            payload["reassessment"] = reassessment
        return payload

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


def read_native_request(project_root: Path, run_id: str) -> dict[str, Any]:
    """Read only one pinned v1.0.13 engine run, never an alternate state store."""
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", run_id):
        raise DeliveryEvidenceError("Invalid run ID.")
    root = project_root.resolve()
    run = root / ".specify" / "workflows" / "runs" / run_id
    for candidate in (run, run / "state.json", run / "workflow.yml"):
        if not candidate.resolve().is_relative_to(root) or candidate.is_symlink():
            raise DeliveryEvidenceError("Run path is linked or escapes the project.")
    state = CloudsDeliveryPassStep._strict_json((run / "state.json").read_text(encoding="utf-8"), 16 * 1024 * 1024)
    fields = {"run_id", "workflow_id", "installed_workflow_id", "installed_registry_root", "status", "current_step_index", "current_step_id", "step_results", "workflow_dir", "created_at", "updated_at", "error"}
    if not isinstance(state, dict) or set(state) != fields or state["run_id"] != run_id or state["workflow_id"] != "clouds-delivery" or state["status"] != "paused" or type(state["current_step_index"]) is not int:
        raise DeliveryEvidenceError("Not a pinned paused clouds-delivery run.")
    from specify_cli.workflows.engine import RunState, WorkflowDefinition
    RunState.load(run_id, root)  # Upstream owns persisted-state shape validation.
    definition = WorkflowDefinition.from_yaml(run / "workflow.yml")
    index = state["current_step_index"]
    if definition.id != "clouds-delivery" or str(definition.schema_version) != "1.0" or index < 0 or index >= len(definition.steps) or definition.steps[index].get("id") != state["current_step_id"] or definition.steps[index].get("type") != "clouds-delivery-pass":
        raise DeliveryEvidenceError("Pinned workflow/pass identity mismatch.")
    entry = state["step_results"].get(state["current_step_id"], {})
    output = entry.get("output", {})
    if entry.get("status") != "paused" or output.get("status") != "dispatch_required":
        raise DeliveryEvidenceError("Paused run does not require native dispatch.")
    request = CloudsDeliveryPassStep._verify_pending_request(output.get("request"), output.get("identity"))
    if request["run_id"] != run_id or request["step_id"] != state["current_step_id"]:
        raise DeliveryEvidenceError("Request does not match the pinned run/pass.")
    feature = output.get("identity", {}).get("feature_directory")
    if not isinstance(feature, str) or not (root / feature).resolve().is_relative_to(root):
        raise DeliveryEvidenceError("Feature path escapes the project.")
    return request


if __name__ == "__main__":
    try:
        print(CloudsDeliveryPassStep._canonical_json(read_native_request(args.project_root, args.run_id)))
    except (DeliveryEvidenceError, OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, str(exc) + "\n")
