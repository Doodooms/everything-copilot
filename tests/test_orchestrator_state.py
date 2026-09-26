import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(
        ROOT
        / "agentic-core"
        / "skills"
        / "orchestration"
        / "references"
        / "orchestrate"
        / "scripts"
    ),
)

import orchestrator


ORCHESTRATE_METHOD_ROOT = (
    ROOT / "agentic-core/skills/orchestration/references/orchestrate"
)
ORCHESTRATOR_SCRIPT = ORCHESTRATE_METHOD_ROOT / "scripts/orchestrator.py"


class OrchestratorStateTests(unittest.TestCase):
    def run_next_task_id(
        self, skill_root: Path, *arguments: str
    ) -> subprocess.CompletedProcess[str]:
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                sys.executable,
                "scripts/orchestrator.py",
                "next-task-id",
                *arguments,
            ],
            cwd=skill_root,
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )

    def test_relative_script_path_works_from_source_and_packaged_method_roots(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temporary_root = Path(temp_dir)
            history = temporary_root / "workspace" / "docs" / "harness-history"
            history.mkdir(parents=True)
            (history / "task_2").mkdir()
            (history / "task_5").mkdir()

            installed_plugin_root = temporary_root / "installed-plugin"
            installed_plugin_root.mkdir()
            shutil.copy2(ROOT / "agentic-core/plugin.json", installed_plugin_root / "plugin.json")
            installed_method_root = (
                installed_plugin_root
                / "skills"
                / "orchestration"
                / "references"
                / "orchestrate"
            )
            installed_scripts = installed_method_root / "scripts"
            installed_scripts.mkdir(parents=True)
            shutil.copy2(ORCHESTRATOR_SCRIPT, installed_scripts / "orchestrator.py")
            self.assertNotIn(ROOT, installed_method_root.parents)

            for method_root in (ORCHESTRATE_METHOD_ROOT, installed_method_root):
                with self.subTest(method_root=method_root):
                    result = self.run_next_task_id(
                        method_root, "--history-dir", str(history)
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.strip(), "task_6")

    def test_cli_requires_an_absolute_workspace_history_directory(self):
        implicit = self.run_next_task_id(ORCHESTRATE_METHOD_ROOT)
        self.assertNotEqual(implicit.returncode, 0)
        self.assertIn("--history-dir", implicit.stderr)

        relative = self.run_next_task_id(
            ORCHESTRATE_METHOD_ROOT, "--history-dir", "docs/harness-history"
        )
        self.assertNotEqual(relative.returncode, 0)
        self.assertIn("absolute", relative.stderr.lower())

    def test_record_manifest_cli_rejects_relative_manifest_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = Path(temp_dir) / "workspace" / "docs" / "harness-history"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/orchestrator.py",
                    "record-manifest",
                    "--manifest",
                    "manifest.json",
                    "--status",
                    "planned",
                    "--history-dir",
                    str(history),
                ],
                cwd=ORCHESTRATE_METHOD_ROOT,
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("absolute", result.stderr.lower())

    def test_generate_next_task_id_uses_harness_history_without_creating_it(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = Path(temp_dir) / "harness-history"

            self.assertEqual(orchestrator.generate_next_task_id(str(history)), "task_1")
            self.assertFalse(history.exists())

            history.mkdir()
            (history / "task_2").mkdir()
            (history / "task_7").mkdir()
            (history / "other").mkdir()

            self.assertEqual(orchestrator.generate_next_task_id(str(history)), "task_8")

    def test_generated_manifest_does_not_assume_a_risk_level(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = orchestrator.create_manifest_if_missing(
                None, history_dir=str(Path(temp_dir) / "harness-history")
            )

        self.assertNotIn("risk_level", manifest)
        self.assertNotIn("required_gates", manifest)

    def test_manifest_validation_accepts_lightweight_task_state(self):
        manifest = {
            "id": "task_1",
            "title": "Implement a feature",
            "description": "Bounded work",
        }

        self.assertEqual(orchestrator.validate_manifest(manifest), {"ok": True})
        self.assertEqual(orchestrator.validate_payload({"manifest": manifest}), {"ok": True})

    def test_orchestration_record_is_atomic_and_uses_canonical_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = {
                "id": "task_1",
                "title": "Implement a feature",
                "description": "Bounded work",
            }

            result = orchestrator.write_orchestration_record(
                "task_1",
                manifest,
                [{"id": "plan-r1", "revision": 1, "path": "plan-r1.md"}],
                [{"agent_id": "implementer", "status": "success"}],
                "success",
                history_dir=str(Path(temp_dir) / "harness-history"),
            )

            path = Path(result)
            self.assertEqual(
                path.relative_to(temp_dir).as_posix(),
                "harness-history/task_1/manifest.json",
            )
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["manifest"], manifest)
            event = json.loads(
                (path.parent / "events.jsonl").read_text(encoding="utf-8").splitlines()[0]
            )
            self.assertEqual(event["type"], "orchestration_result")
            self.assertEqual(
                event["plan_refs"],
                [{"id": "plan-r1", "revision": 1, "path": "plan-r1.md"}],
            )
            self.assertEqual(
                event["specialist_returns"],
                [{"agent_id": "implementer", "status": "success"}],
            )
            self.assertEqual(list(path.parent.glob("*.tmp")), [])

    def test_task_events_record_status_transitions_and_retry_attempts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = Path(temp_dir) / "tasks-history"
            statuses = [
                "planned",
                "queued",
                "running",
                "partial",
                "queued",
                "running",
                "completed",
            ]

            for index, status in enumerate(statuses):
                orchestrator.append_task_event(
                    "task_1",
                    "TASK-1",
                    status,
                    attempt_id="attempt-2" if index > 3 else "attempt-1",
                    agent_id="implementer",
                    evidence={"ref": f"evidence-{index}"},
                    history_dir=str(history),
                )

            events = [
                json.loads(line)
                for line in (history / "task_1.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual([event["status"] for event in events], statuses)
            self.assertEqual(events[3]["attempt_id"], "attempt-1")
            self.assertEqual(events[4]["attempt_id"], "attempt-2")
            self.assertTrue(all(event["parent_task_id"] == "task_1" for event in events))

    def test_task_events_reject_invalid_transition_and_path_ids(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = str(Path(temp_dir) / "tasks-history")
            orchestrator.append_task_event("task_1", "TASK-1", "planned", history_dir=history)

            with self.assertRaisesRegex(ValueError, "invalid task transition"):
                orchestrator.append_task_event(
                    "task_1", "TASK-1", "completed", history_dir=history
                )

            with self.assertRaisesRegex(ValueError, "path-safe identifier"):
                orchestrator.append_task_event(
                    "../escape", "TASK-2", "planned", history_dir=history
                )

    def test_task_events_fail_explicitly_on_corrupt_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = Path(temp_dir) / "tasks-history"
            history.mkdir()
            (history / "task_1.jsonl").write_text("{not-json}\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "invalid task event"):
                orchestrator.append_task_event(
                    "task_1",
                    "TASK-1",
                    "planned",
                    history_dir=str(history),
                )


if __name__ == "__main__":
    unittest.main()
