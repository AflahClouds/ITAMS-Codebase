"""Project regression tests for issue-sized native Clouds delivery."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


STEP_FILE = Path(__file__).resolve().parents[1] / "steps" / "clouds-delivery-pass" / "__init__.py"
SPEC = importlib.util.spec_from_file_location("clouds_delivery_pass_tested", STEP_FILE)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
Step = MODULE.CloudsDeliveryPassStep
DeliveryEvidenceError = MODULE.DeliveryEvidenceError


class NativeIssueDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.feature = self.root / "specs" / "014-test"
        self.issues = self.feature / "issues"
        self.issues.mkdir(parents=True)
        self.first = self.issues / "01-first.md"
        self.second = self.issues / "02-second.md"
        self.third = self.issues / "03-third.md"
        self.first.write_text("# First\n- [x] done\n", encoding="utf-8")
        self.second.write_text("# Second\n- [ ] test\n- [ ] code\n", encoding="utf-8")
        self.third.write_text("# Third\n- [ ] implementation\n- [ ] Frozen candidate receives independent read-only review; the same builder repairs and the same reviewer re-reviews; commits stay local.\n", encoding="utf-8")
        (self.feature / "spec.md").write_text("# Accepted spec\n", encoding="utf-8")
        (self.feature / "plan.md").write_text("# Accepted plan\n", encoding="utf-8")
        checklist = self.feature / "checklists" / "requirements.md"
        checklist.parent.mkdir()
        checklist.write_text("# Requirements checklist\n", encoding="utf-8")
        specify = self.root / ".specify"
        specify.mkdir()
        (specify / "feature.json").write_text(json.dumps({"feature_directory": "specs/014-test"}), encoding="utf-8")
        self.tasks = self.feature / "tasks.md"
        self.tasks.write_text("- [x] T001\n- [ ] T002\n- [ ] T003\n", encoding="utf-8")
        self.git("init", "-b", "codex/test")
        self.git("config", "user.name", "Workflow Test")
        self.git("config", "user.email", "workflow@example.invalid")
        self.commit()
        self.step = Step()
        self.identity = {
            "feature_directory": "specs/014-test",
            "expected_head": self.step._current_head(self.root),
            "baseline_worktree": self.step._worktree_evidence(self.root),
        }

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, text=True, capture_output=True, check=True
        ).stdout.strip()

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-m", "fixture checkpoint")

    def request(self):
        return {
            "role": "builder",
            "phase": "implementation",
            "expected_head": self.identity["expected_head"],
            "tasks": self.step._task_evidence(self.tasks),
            "payload": self.step._issue_payload(self.root, self.identity),
        }

    def finish(self, request):
        context = SimpleNamespace(run_id="test-run")
        return self.step._finish_issue_pass(
            context, {"id": "delivery-pass-01"}, self.root, self.identity,
            request, "builder completed",
        )

    def test_dispatch_binds_next_open_issue_and_full_issue_inventory(self):
        payload = self.step._issue_payload(self.root, self.identity)
        self.assertEqual(payload["issue"], "02-second.md")
        self.assertEqual(
            set(payload["issues_before"]),
            {"01-first.md", "02-second.md", "03-third.md"},
        )
        self.assertEqual(
            payload["issues_before"]["02-second.md"]["sha256"],
            self.step._sha256(self.second),
        )

    def test_completed_issue_advances_without_premature_final_review(self):
        request = self.request()
        self.second.write_text("# Second\n- [x] test\n- [x] code\n", encoding="utf-8")
        self.tasks.write_text("- [x] T001\n- [x] T002\n- [ ] T003\n", encoding="utf-8")
        self.commit()
        with patch.object(self.step, "_dispatch") as review:
            result = self.finish(request)
        review.assert_not_called()
        self.assertEqual(result.output["status"], "tasks_appended")
        self.assertEqual(result.output["completed_issue"], "02-second.md")
        self.assertEqual(result.output["next_issue"], "03-third.md")

    def test_builder_cannot_change_later_issue(self):
        request = self.request()
        self.second.write_text("# Second\n- [x] test\n- [x] code\n", encoding="utf-8")
        self.third.write_text("# Third\n- [x] later\n", encoding="utf-8")
        self.tasks.write_text("- [x] T001\n- [x] T002\n- [ ] T003\n", encoding="utf-8")
        self.commit()
        with self.assertRaisesRegex(DeliveryEvidenceError, "outside the bound issue"):
            self.finish(request)

    def test_builder_cannot_close_issue_with_unchecked_or_deleted_criteria(self):
        for second_text in (
            "# Second\n- [x] test\n- [ ] code\n",
            "# Second\n- [x] test\n",
        ):
            with self.subTest(second_text=second_text), tempfile.TemporaryDirectory():
                request = self.request()
                self.second.write_text(second_text, encoding="utf-8")
                self.tasks.write_text("- [x] T001\n- [x] T002\n- [ ] T003\n", encoding="utf-8")
                self.commit()
                with self.assertRaisesRegex(DeliveryEvidenceError, "criteria"):
                    self.finish(request)
                self.git("reset", "--hard", request["expected_head"])

    def test_builder_needs_task_progress_and_committed_checkpoint(self):
        request = self.request()
        self.second.write_text("# Second\n- [x] test\n- [x] code\n", encoding="utf-8")
        self.commit()
        with self.assertRaisesRegex(DeliveryEvidenceError, "unchecked tasks"):
            self.finish(request)
        self.tasks.write_text("- [x] T001\n- [x] T002\n- [ ] T003\n", encoding="utf-8")
        with self.assertRaisesRegex(DeliveryEvidenceError, "checkpoint|baseline"):
            self.finish(request)

    def test_final_issue_enters_native_reviewer_after_all_tasks(self):
        self.second.write_text("# Second\n- [x] test\n- [x] code\n", encoding="utf-8")
        self.tasks.write_text("- [x] T001\n- [x] T002\n- [ ] T003\n", encoding="utf-8")
        self.commit()
        self.identity["expected_head"] = self.step._current_head(self.root)
        request = {
            "role": "builder",
            "phase": "implementation",
            "expected_head": self.identity["expected_head"],
            "tasks": self.step._task_evidence(self.tasks),
            "payload": self.step._issue_payload(self.root, self.identity),
        }
        self.third.write_text("# Third\n- [x] implementation\n- [ ] Frozen candidate receives independent read-only review; the same builder repairs and the same reviewer re-reviews; commits stay local.\n", encoding="utf-8")
        self.tasks.write_text("- [x] T001\n- [x] T002\n- [x] T003\n", encoding="utf-8")
        self.commit()
        with patch.object(self.step, "_dispatch", return_value="review dispatched") as review:
            result = self.finish(request)
        self.assertEqual(result, "review dispatched")
        self.assertEqual(review.call_args.args[4:6], ("reviewer", "review"))


    def native_context(self):
        return SimpleNamespace(
            project_root=str(self.root),
            run_id="native-issue-test",
            inputs={
                "model": "gpt-6-sol",
                "reviewer_model": "gpt-6-sol",
                "astra_user_requested": "false",
                "authorization_ref": "accepted local feature scope",
                "task_class": "high-risk-deterministic",
                "oracle_evidence": "complete: accepted custody fail-before cases",
                "dispatch_result": "",
                "assignment_transition": "",
                "reassessment_payload": "",
            },
            steps={},
        )

    def native_start(self):
        context = self.native_context()
        prepared = self.step.execute(
            {"id": "delivery-identity", "prepare_only": True}, context
        )
        self.assertEqual(prepared.output["status"], "identity_captured", prepared.error)
        context.steps["delivery-identity"] = {"output": prepared.output}
        return context, self.native_pass(context, 1, "delivery-identity")

    def native_pass(self, context, number, previous):
        config = {"id": f"delivery-pass-{number:02d}", "previous_step": previous}
        outcome = self.step.execute(config, context)
        context.steps[config["id"]] = {"output": outcome.output}
        return outcome

    def native_result(self, context, number, role, status, *, child_id, findings=None):
        config = {"id": f"delivery-pass-{number:02d}"}
        request = context.steps[config["id"]]["output"]["request"]
        context.inputs["dispatch_result"] = json.dumps({
            "protocol_version": 1,
            "request_digest": request["digest"],
            "child_id": child_id,
            "role": role,
            "status": status,
            "message": f"{role} {status}",
            "findings": findings or [],
        })
        outcome = self.step.execute(config, context)
        context.steps[config["id"]] = {"output": outcome.output}
        return outcome

    def test_native_pass_binds_next_issue_then_advances_to_next_issue(self):
        context, first = self.native_start()
        request = first.output["request"]
        self.assertEqual(first.output["status"], "dispatch_required", first.error)
        self.assertEqual((request["role"], request["payload"]["issue"]),
                         ("builder", "02-second.md"))
        self.second.write_text("# Second\n- [x] test\n- [x] code\n", encoding="utf-8")
        self.tasks.write_text("- [x] T001\n- [x] T002\n- [ ] T003\n", encoding="utf-8")
        self.commit()
        completed = self.native_result(
            context, 1, "builder", "completed", child_id="native-builder"
        )
        self.assertEqual(completed.output["status"], "tasks_appended", completed.error)
        self.assertEqual(completed.output["next_issue"], "03-third.md")
        second = self.native_pass(context, 2, "delivery-pass-01")
        self.assertEqual(second.output["status"], "dispatch_required", second.error)
        next_request = second.output["request"]
        self.assertEqual((next_request["role"], next_request["payload"]["issue"]),
                         ("builder", "03-third.md"))
        self.assertEqual(next_request["assignment_id"], request["assignment_id"])
        self.assertEqual(next_request["expected_head"], self.step._current_head(self.root))

    def test_native_result_rejects_later_issue_mutation(self):
        context, first = self.native_start()
        self.assertEqual(first.output["request"]["payload"]["issue"], "02-second.md")
        self.second.write_text("# Second\n- [x] test\n- [x] code\n", encoding="utf-8")
        self.third.write_text("# Third\n- [x] implementation\n- [ ] Frozen candidate receives independent read-only review; the same builder repairs and the same reviewer re-reviews; commits stay local.\n", encoding="utf-8")
        self.tasks.write_text("- [x] T001\n- [x] T002\n- [ ] T003\n", encoding="utf-8")
        self.commit()
        outcome = self.native_result(
            context, 1, "builder", "completed", child_id="native-builder"
        )
        self.assertEqual(outcome.status, MODULE.StepStatus.FAILED)
        self.assertIn("outside the bound issue", outcome.error)

    def test_native_result_rejects_incomplete_criteria(self):
        context, _ = self.native_start()
        self.second.write_text("# Second\n- [x] test\n- [ ] code\n", encoding="utf-8")
        self.tasks.write_text("- [x] T001\n- [x] T002\n- [ ] T003\n", encoding="utf-8")
        self.commit()
        outcome = self.native_result(
            context, 1, "builder", "completed", child_id="native-builder"
        )
        self.assertEqual(outcome.status, MODULE.StepStatus.FAILED)
        self.assertIn("criteria", outcome.error)

    def test_native_result_rejects_rewritten_acceptance_criterion(self):
        context, _ = self.native_start()
        self.second.write_text(
            "# Second\n- [x] test\n- [x] easier replacement\n",
            encoding="utf-8",
        )
        self.tasks.write_text(
            "- [x] T001\n- [x] T002\n- [ ] T003\n", encoding="utf-8"
        )
        self.commit()
        outcome = self.native_result(
            context, 1, "builder", "completed", child_id="native-builder"
        )
        self.assertEqual(outcome.status, MODULE.StepStatus.FAILED)
        self.assertIn("criteria", outcome.error)

    def native_dispatch_final_issue(self):
        context, _ = self.native_start()
        self.second.write_text("# Second\n- [x] test\n- [x] code\n", encoding="utf-8")
        self.tasks.write_text("- [x] T001\n- [x] T002\n- [ ] T003\n", encoding="utf-8")
        self.commit()
        completed = self.native_result(
            context, 1, "builder", "completed", child_id="native-builder"
        )
        self.assertEqual(completed.output["status"], "tasks_appended", completed.error)
        final = self.native_pass(context, 2, "delivery-pass-01")
        self.assertEqual(final.output["request"]["payload"]["issue"], "03-third.md")
        return context

    def test_native_rejects_removed_final_review_criterion(self):
        context = self.native_dispatch_final_issue()
        self.third.write_text(
            "# Third\n- [x] implementation\n- [x] review claimed without evidence\n",
            encoding="utf-8",
        )
        self.tasks.write_text("- [x] T001\n- [x] T002\n- [x] T003\n", encoding="utf-8")
        self.commit()
        outcome = self.native_result(
            context, 2, "builder", "completed", child_id="native-builder"
        )
        self.assertEqual(outcome.status, MODULE.StepStatus.FAILED)
        self.assertIn("criteria", outcome.error)

    def test_native_rejects_final_review_checked_before_review(self):
        context = self.native_dispatch_final_issue()
        review_line = "Frozen candidate receives independent read-only review; the same builder repairs and the same reviewer re-reviews; commits stay local."
        self.third.write_text(
            f"# Third\n- [x] implementation\n- [x] {review_line}\n",
            encoding="utf-8",
        )
        self.tasks.write_text("- [x] T001\n- [x] T002\n- [x] T003\n", encoding="utf-8")
        self.commit()
        outcome = self.native_result(
            context, 2, "builder", "completed", child_id="native-builder"
        )
        self.assertEqual(outcome.status, MODULE.StepStatus.FAILED)
        self.assertIn("criteria", outcome.error)

    def test_native_review_findings_return_to_same_builder_assignment(self):
        context = self.native_dispatch_final_issue()
        review_line = "Frozen candidate receives independent read-only review; the same builder repairs and the same reviewer re-reviews; commits stay local."
        self.third.write_text(
            f"# Third\n- [x] implementation\n- [ ] {review_line}\n",
            encoding="utf-8",
        )
        self.tasks.write_text("- [x] T001\n- [x] T002\n- [x] T003\n", encoding="utf-8")
        self.commit()
        review = self.native_result(
            context, 2, "builder", "completed", child_id="native-builder"
        )
        self.assertEqual(review.output["request"]["role"], "reviewer", review.error)
        finding = {
            "id": "REVIEW-001",
            "finding": "Documented outcome is incomplete.",
            "required_action": "Repair and verify the affected issue evidence.",
        }
        returned = self.native_result(
            context, 2, "reviewer", "tasks_appended",
            child_id="native-reviewer", findings=[finding],
        )
        self.assertEqual(returned.output["status"], "tasks_appended", returned.error)
        repair = self.native_pass(context, 3, "delivery-pass-02")
        self.assertEqual(repair.output["status"], "dispatch_required", repair.error)
        request = repair.output["request"]
        self.assertEqual((request["role"], request["phase"]), ("builder", "repair"))
        self.assertEqual(request["payload"], [finding])
        self.assertEqual(
            request["assignment_id"],
            context.steps["delivery-pass-02"]["output"]["identity"]["builder_assignment_id"],
        )

    def test_native_approval_resume_keeps_bound_issue(self):
        context, first = self.native_start()
        original = first.output["request"]
        paused = self.native_result(
            context, 1, "builder", "approval_required", child_id="native-builder"
        )
        self.assertEqual(paused.output["status"], "approval_required", paused.error)
        context.inputs["approval_action"] = "resume"
        context.inputs["approval_response"] = "Continue within accepted scope."
        resumed = self.native_pass(context, 1, "delivery-identity")
        self.assertEqual(resumed.output["status"], "dispatch_required", resumed.error)
        request = resumed.output["request"]
        self.assertEqual(request["payload"]["issue"], original["payload"]["issue"])
        self.assertEqual(request["payload"]["issues_before"], original["payload"]["issues_before"])
        self.assertEqual(request["payload"]["approval_response"], "Continue within accepted scope.")

    def test_native_findings_repair_approval_resume_keeps_findings(self):
        context = self.native_dispatch_final_issue()
        review_line = "Frozen candidate receives independent read-only review; the same builder repairs and the same reviewer re-reviews; commits stay local."
        self.third.write_text(
            f"# Third\n- [x] implementation\n- [ ] {review_line}\n",
            encoding="utf-8",
        )
        self.tasks.write_text(
            "- [x] T001\n- [x] T002\n- [x] T003\n", encoding="utf-8"
        )
        self.commit()
        review = self.native_result(
            context, 2, "builder", "completed", child_id="native-builder"
        )
        self.assertEqual(review.output["request"]["role"], "reviewer", review.error)
        finding = {
            "id": "REVIEW-001",
            "finding": "The local evidence needs repair.",
            "required_action": "Correct the evidence before re-review.",
        }
        returned = self.native_result(
            context, 2, "reviewer", "tasks_appended",
            child_id="native-reviewer", findings=[finding],
        )
        self.assertEqual(returned.output["status"], "tasks_appended", returned.error)
        repair = self.native_pass(context, 3, "delivery-pass-02")
        self.assertEqual(repair.output["request"]["payload"], [finding], repair.error)
        paused = self.native_result(
            context, 3, "builder", "approval_required", child_id="native-builder"
        )
        self.assertEqual(paused.output["status"], "approval_required", paused.error)
        context.inputs["approval_action"] = "resume"
        context.inputs["approval_response"] = "Continue the bounded repair."
        resumed = self.native_pass(context, 3, "delivery-pass-02")
        self.assertEqual(
            resumed.output["request"]["payload"],
            {"approval_response": "Continue the bounded repair.", "prior_payload": [finding]},
            resumed.error,
        )
        completed = self.native_result(
            context, 3, "builder", "completed", child_id="native-builder"
        )
        self.assertEqual(completed.output["request"]["role"], "reviewer", completed.error)
        self.assertEqual(completed.output["request"]["phase"], "re-review", completed.error)

    def test_reassessment_remains_in_issue_request_payload(self):
        reassessment = {"reason": "same bounded builder purpose"}
        payload = self.step._issue_payload(self.root, self.identity, reassessment)
        self.assertEqual(payload["issue"], "02-second.md")
        self.assertEqual(payload["reassessment"], reassessment)

    def native_pause_final_review_evidence(self):
        context = self.native_dispatch_final_issue()
        review_line = "Frozen candidate receives independent read-only review; the same builder repairs and the same reviewer re-reviews; commits stay local."
        self.third.write_text(
            f"# Third\n- [x] implementation\n- [ ] {review_line}\n",
            encoding="utf-8",
        )
        self.tasks.write_text(
            "- [x] T001\n- [x] T002\n- [x] T003\n", encoding="utf-8"
        )
        self.commit()
        review = self.native_result(
            context, 2, "builder", "completed", child_id="native-builder"
        )
        self.assertEqual(review.output["request"]["role"], "reviewer", review.error)
        closure = self.native_result(
            context, 2, "reviewer", "clean", child_id="native-reviewer"
        )
        self.assertEqual(closure.output["request"]["role"], "builder", closure.error)
        original = closure.output["request"]["payload"]
        paused = self.native_result(
            context, 2, "builder", "approval_required", child_id="native-builder"
        )
        self.assertEqual(paused.output["status"], "approval_required", paused.error)
        context.inputs["approval_action"] = "resume"
        context.inputs["approval_response"] = "Record the completed review locally."
        resumed = self.native_pass(context, 2, "delivery-pass-01")
        self.assertEqual(resumed.output["status"], "dispatch_required", resumed.error)
        return context, original, resumed.output["request"], review_line

    def test_native_review_evidence_approval_resume_keeps_binding(self):
        context, original, resumed, review_line = self.native_pause_final_review_evidence()
        self.assertEqual(resumed["payload"]["review_completion_issue"], original["review_completion_issue"])
        self.assertEqual(resumed["payload"]["issues_before"], original["issues_before"])
        self.assertEqual(resumed["payload"]["review_child_id"], "native-reviewer")
        self.assertEqual(resumed["payload"]["approval_response"], "Record the completed review locally.")
        self.third.write_text(
            f"# Third\n- [x] implementation\n- [x] {review_line}\n",
            encoding="utf-8",
        )
        self.commit()
        result = self.native_result(
            context, 2, "builder", "completed", child_id="native-builder"
        )
        self.assertEqual(result.output["request"]["role"], "reviewer", result.error)
        self.assertEqual(result.output["request"]["phase"], "re-review", result.error)
        clean = self.native_result(
            context, 2, "reviewer", "clean", child_id="native-reviewer"
        )
        self.assertEqual(clean.output["status"], "clean", clean.error)

    def test_native_review_evidence_approval_resume_rejects_altered_criterion(self):
        context, _, _, review_line = self.native_pause_final_review_evidence()
        self.third.write_text(
            f"# Third\n- [x] easier replacement\n- [x] {review_line}\n",
            encoding="utf-8",
        )
        self.commit()
        outcome = self.native_result(
            context, 2, "builder", "completed", child_id="native-builder"
        )
        self.assertEqual(outcome.status, MODULE.StepStatus.FAILED)
        self.assertIn("criterion", outcome.error)

    def test_native_final_review_closes_review_owned_criterion_truthfully(self):
        context, _ = self.native_start()
        self.second.write_text("# Second\n- [x] test\n- [x] code\n", encoding="utf-8")
        self.tasks.write_text("- [x] T001\n- [x] T002\n- [ ] T003\n", encoding="utf-8")
        self.commit()
        completed = self.native_result(
            context, 1, "builder", "completed", child_id="native-builder"
        )
        self.assertEqual(completed.output["status"], "tasks_appended", completed.error)
        second_pass = self.native_pass(context, 2, "delivery-pass-01")
        self.assertEqual(second_pass.output["request"]["payload"]["issue"], "03-third.md")
        review_line = "Frozen candidate receives independent read-only review; the same builder repairs and the same reviewer re-reviews; commits stay local."
        self.third.write_text(f"# Third\n- [x] implementation\n- [ ] {review_line}\n", encoding="utf-8")
        self.tasks.write_text("- [x] T001\n- [x] T002\n- [x] T003\n", encoding="utf-8")
        self.commit()
        review = self.native_result(
            context, 2, "builder", "completed", child_id="native-builder"
        )
        self.assertEqual(review.output["status"], "dispatch_required", review.error)
        self.assertEqual(review.output["request"]["role"], "reviewer")
        self.assertEqual(review.output["request"]["phase"], "review")
        closure = self.native_result(
            context, 2, "reviewer", "clean", child_id="native-reviewer"
        )
        self.assertEqual(closure.output["status"], "dispatch_required", closure.error)
        self.assertEqual(closure.output["request"]["role"], "builder")
        self.assertEqual(closure.output["request"]["phase"], "repair")
        self.third.write_text(f"# Third\n- [x] implementation\n- [x] {review_line}\n\nReviewed by native-reviewer.\n", encoding="utf-8")
        self.commit()
        re_review = self.native_result(
            context, 2, "builder", "completed", child_id="native-builder"
        )
        self.assertEqual(re_review.status, MODULE.StepStatus.PAUSED, re_review.error)
        self.assertEqual(re_review.output["status"], "dispatch_required", re_review.error)
        self.assertEqual(re_review.output["request"]["role"], "reviewer")
        self.assertEqual(re_review.output["request"]["phase"], "re-review")
        clean = self.native_result(
            context, 2, "reviewer", "clean", child_id="native-reviewer"
        )
        self.assertEqual(clean.output["status"], "clean", clean.error)
        self.assertEqual(clean.output["clean_revision"], self.step._current_head(self.root))


if __name__ == "__main__":
    unittest.main()
