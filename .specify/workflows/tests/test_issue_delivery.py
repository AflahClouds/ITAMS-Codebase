"""Regression checks for issue-sized Clouds delivery passes."""

from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


STEP_FILE = Path(__file__).resolve().parents[1] / "steps" / "clouds-delivery-pass" / "__init__.py"
SPEC = importlib.util.spec_from_file_location("clouds_delivery_pass_tested", STEP_FILE)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
Step = MODULE.CloudsDeliveryPassStep
DeliveryEvidenceError = MODULE.DeliveryEvidenceError


class IssueDeliveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.feature = self.root / "specs" / "014-test"
        self.issues = self.feature / "issues"
        self.issues.mkdir(parents=True)
        self.identity = {"feature_directory": "specs/014-test"}
        self.first = self.issues / "01-first.md"
        self.second = self.issues / "02-second.md"
        self.first.write_text("- [ ] test\n- [ ] code\n", encoding="utf-8")
        self.second.write_text("- [ ] next\n", encoding="utf-8")
        self.tasks = self.feature / "tasks.md"
        self.tasks.write_text("- [ ] T001\n- [ ] T002\n", encoding="utf-8")
        self.step = Step()
        self.before = self.step._issues_evidence(self.root, self.identity)
        self.tasks_before = self.step._task_evidence(self.tasks)

    def finish(self):
        with patch.object(self.step, "_verify_baseline_worktree"), patch.object(
            self.step, "_current_head", return_value="a" * 40
        ):
            return self.step._finish_issue_pass(
                self.root, self.identity, "01-first.md", self.before,
                self.tasks_before, "done", "gpt-6-sol", "gpt-6-sol",
                "false", "approved", "high-risk-deterministic", "complete:test",
            )

    def test_one_issue_advances_without_reviewing_incomplete_feature(self):
        self.first.write_text("- [x] test\n- [x] code\n", encoding="utf-8")
        self.tasks.write_text("- [x] T001\n- [ ] T002\n", encoding="utf-8")
        result = self.finish()
        self.assertEqual(result.output["status"], "issue_completed")
        self.assertEqual(result.output["completed_issue"], "01-first.md")
        self.assertEqual(result.output["next_issue"], "02-second.md")

    def test_later_issue_change_is_rejected(self):
        self.first.write_text("- [x] test\n- [x] code\n", encoding="utf-8")
        self.second.write_text("- [x] next\n", encoding="utf-8")
        self.tasks.write_text("- [x] T001\n- [ ] T002\n", encoding="utf-8")
        with self.assertRaisesRegex(DeliveryEvidenceError, "outside the bound issue"):
            self.finish()

    def test_issue_cannot_close_without_task_progress(self):
        self.first.write_text("- [x] test\n- [x] code\n", encoding="utf-8")
        with self.assertRaisesRegex(DeliveryEvidenceError, "without reducing unchecked tasks"):
            self.finish()

    def test_issue_cannot_report_complete_with_open_checks(self):
        self.tasks.write_text("- [x] T001\n- [ ] T002\n", encoding="utf-8")
        with self.assertRaisesRegex(DeliveryEvidenceError, "remains open"):
            self.finish()

    def test_last_issue_requires_all_tasks_before_review(self):
        self.first.write_text("- [x] test\n- [x] code\n", encoding="utf-8")
        self.tasks.write_text("- [x] T001\n- [ ] T002\n", encoding="utf-8")
        self.before = self.step._issues_evidence(self.root, self.identity)
        self.second.write_text("- [x] next\n", encoding="utf-8")
        self.tasks.write_text("- [x] T001\n- [x] T002\n", encoding="utf-8")
        with patch.object(self.step, "_verify_baseline_worktree"), patch.object(
            self.step, "_current_head", return_value="a" * 40
        ), patch.object(self.step, "_verify_identity"), patch.object(
            self.step, "_run_convergence", return_value="review dispatched"
        ) as review:
            result = self.step._finish_issue_pass(
                self.root, self.identity, "02-second.md", self.before,
                {"unchecked": 1}, "done", "gpt-6-sol", "gpt-6-sol",
                "false", "approved", "high-risk-deterministic", "complete:test",
            )
        self.assertEqual(result, "review dispatched")
        review.assert_called_once()


class RunnerProgressTests(unittest.TestCase):
    def test_progress_omits_commands_outputs_and_messages(self):
        raw = json.dumps({
            "type": "item.completed",
            "item": {"type": "command_execution", "status": "completed",
                     "exit_code": 0, "command": "secret command",
                     "aggregated_output": "private output", "text": "private message"},
        })
        self.assertEqual(Step._progress_event(raw), {
            "event": "item.completed", "item_type": "command_execution",
            "status": "completed", "exit_code": 0,
        })

    def test_runner_preserves_builder_and_reviewer_permissions(self):
        for command, permission in (("speckit.implement", "workspace-write"),
                                    ("speckit.converge", "read-only")):
            with self.subTest(permission=permission), tempfile.TemporaryDirectory() as directory:
                child = MagicMock()
                child.__enter__.return_value = child
                child.stdout = io.StringIO('{"type":"turn.completed"}\n')
                child.stderr = io.StringIO("warning\n")
                child.pid, child.returncode = 123, 0
                login = subprocess.CompletedProcess([], 0, "Logged in using ChatGPT", "")
                with patch.dict(MODULE.os.environ, {
                    "SPECKIT_INTEGRATION_CODEX_EXECUTABLE": "codex.exe",
                    "SPECKIT_INTEGRATION_CODEX_EXTRA_ARGS": "",
                    "OPENAI_API_KEY": "test-secret",
                }), patch.object(MODULE.subprocess, "run", return_value=login), patch.object(
                    MODULE.subprocess, "Popen", return_value=child
                ) as launch:
                    result = Step._run_codex(command, "diagnostic", Path(directory), "gpt-6-sol")
                argv = launch.call_args.args[0]
                self.assertNotIn("OPENAI_API_KEY", launch.call_args.kwargs["env"])
                self.assertIn("--ephemeral", argv)
                self.assertIn("--json", argv)
                if permission == "workspace-write":
                    self.assertIn("--approve-for-me", argv)
                    self.assertNotIn("--sandbox", argv)
                else:
                    self.assertNotIn("--approve-for-me", argv)
                    self.assertEqual(argv[argv.index("--sandbox") + 1], "read-only")
                self.assertEqual(result.stdout, '{"type":"turn.completed"}\n')
                self.assertEqual(result.stderr, "warning\n")
                log = next((Path(directory) / ".specify/workflows/runs/child-progress").glob("*.jsonl"))
                records = [json.loads(line) for line in log.read_text().splitlines()]
                self.assertEqual([entry["event"] for entry in records],
                                 ["child_started", "turn.completed", "child_exited"])


if __name__ == "__main__":
    unittest.main()
