from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from expertise.cli import main

ROOT = Path(__file__).resolve().parents[1]


class LocalWorkspaceWorkflowTests(unittest.TestCase):
    def test_local_plugin_authoring_can_start_without_control_plane_state(self) -> None:
        orchestrator = (ROOT / "agentic-core/agents/orchestrator.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "Workspace-local authoring and validation do not depend on Control Plane state",
            orchestrator,
        )

        with tempfile.TemporaryDirectory() as workspace:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                scaffold_status = main(
                    [
                        "scaffold",
                        "local-workflow-check",
                        "--name",
                        "Local Workflow Check",
                        "--description",
                        "A locally authored pack used to check the authoring workflow.",
                        "--capability",
                        "local.check",
                        "--skill-id",
                        "local-check",
                        "--skill-description",
                        "Check a local plugin authoring workflow.",
                        "--publisher",
                        "Local Test",
                        "--source",
                        "Temporary test workspace",
                        "--target",
                        "portable",
                    ],
                    repo_root=Path(workspace),
                )
                test_status = main(
                    ["test", "local-workflow-check"], repo_root=Path(workspace)
                )

            self.assertEqual(scaffold_status, 0)
            self.assertEqual(test_status, 0)
            self.assertTrue(
                (
                    Path(workspace) / "expertise/packs/local-workflow-check/pack.yaml"
                ).is_file()
            )
            results = [
                json.loads(document)
                for document in output.getvalue()
                .replace("}\n{", "}\n---\n{")
                .split("\n---\n")
            ]
            result = results[-1]
            self.assertEqual(result["status"], "passed")
            self.assertEqual(result["pack"], "local-workflow-check")


if __name__ == "__main__":
    unittest.main()
