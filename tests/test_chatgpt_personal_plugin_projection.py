from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "agentic-core"
MCP_URL = "https://control.example.invalid/mcp"
APP_ID = "asdk_app_fixture"


def _copy_installed_plugin(destination: Path) -> None:
    shutil.copytree(
        CORE,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", "*.py[cod]"),
    )


def _run_projector(
    script: Path, cwd: Path, output: Path, *extra: str
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONNOUSERSITE"] = "1"
    uv = shutil.which("uv")
    command = (
        [uv, "run", "--no-project", "--script", str(script)]
        if uv
        else [sys.executable, str(script)]
    )
    return subprocess.run(
        [
            *command,
            "--output",
            str(output),
            "--app-id",
            APP_ID,
            "--mcp-url",
            MCP_URL,
            *extra,
        ],
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if (
            not path.is_file()
            or "__pycache__" in path.parts
            or path.suffix in {".pyc", ".pyo"}
        ):
            continue
        relative = path.relative_to(root).as_posix()
        content = path.read_bytes()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(b"x" if path.stat().st_mode & 0o111 else b"-")
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


class ChatGPTPersonalPluginProjectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(
            prefix="chatgpt-personal-plugin-consumer-"
        )
        self.root = Path(self.temporary.name)
        self.plugin = self.root / "installed" / "agentic-core"
        self.cwd = self.root / "consumer" / "unrelated-working-directory"
        self.cwd.mkdir(parents=True)
        _copy_installed_plugin(self.plugin)

    def tearDown(self):
        self.temporary.cleanup()

    def test_projection_runs_from_external_installed_copy_and_is_deterministic(self):
        script = self.plugin / "runtime" / "project_chatgpt_personal_plugin.py"
        outputs = [self.root / "external-output-a", self.root / "external-output-b"]
        summaries = []

        for output in outputs:
            result = _run_projector(script, self.cwd, output)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            summary = json.loads(result.stdout)
            self.assertEqual(summary["status"], "projected")
            self.assertEqual(summary["target"], "chatgpt-personal")
            self.assertEqual(summary["mcp_servers"], ["control"])
            self.assertEqual(summary["tools"], ["control_ping"])
            self.assertEqual(summary["registered_apps"], ["control"])
            self.assertEqual(_tree_digest(output), summary["artifact_sha256"])
            summaries.append(summary)

        self.assertFalse((self.plugin / ".git").exists())
        self.assertFalse((self.plugin / "expertise").exists())
        self.assertEqual(_tree_digest(outputs[0]), _tree_digest(outputs[1]))
        self.assertEqual(
            summaries[0]["artifact_sha256"], summaries[1]["artifact_sha256"]
        )
        self.assertEqual(
            {path.relative_to(outputs[0]).as_posix() for path in outputs[0].rglob("*")},
            {
                "plugin.json",
                "mcp.json",
                ".app.json",
                "com.doodooms.agentic-workflow",
                "com.doodooms.agentic-workflow/integration.yaml",
                "com.doodooms.agentic-workflow/projection.json",
            },
        )

        plugin_manifest = json.loads(
            (outputs[0] / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            plugin_manifest["extensions"]["com.openai"]["apps"], "./.app.json"
        )
        self.assertEqual(
            json.loads((outputs[0] / ".app.json").read_text(encoding="utf-8")),
            {"apps": {"control": {"id": APP_ID}}},
        )
        mcp_manifest = json.loads((outputs[0] / "mcp.json").read_text(encoding="utf-8"))
        self.assertEqual(
            mcp_manifest["mcpServers"],
            {"control": {"type": "streamable-http", "url": MCP_URL}},
        )
        provenance = json.loads(
            (
                outputs[0] / "com.doodooms.agentic-workflow" / "projection.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(provenance["source_pack"], "control-ping-probe@0.1.0")
        self.assertEqual(provenance["mcp_tools"], ["control_ping"])
        self.assertEqual(provenance["registered_app_ids"], [APP_ID])
        self.assertEqual(
            provenance["mcp_url_sha256"],
            hashlib.sha256(MCP_URL.encode("utf-8")).hexdigest(),
        )
        self.assertNotIn("mcp_url", provenance)
        self.assertNotIn(MCP_URL, json.dumps(provenance))

    def test_projection_rejects_non_https_server_endpoint(self):
        script = self.plugin / "runtime" / "project_chatgpt_personal_plugin.py"
        output = self.root / "invalid-output"
        result = _run_projector(
            script,
            self.cwd,
            output,
            "--mcp-url",
            "http://control.example.invalid/mcp",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())

    def test_projection_rejects_urls_outside_the_mcp_endpoint_contract(self):
        script = self.plugin / "runtime" / "project_chatgpt_personal_plugin.py"
        invalid_urls = (
            "https://control.example.invalid/mcp/fixture-token-DO-NOT-USE",
            "https://control.\nexample.invalid/mcp",
            "https://control.example.invalid/mcp with-space",
            "https://user:secret@control.example.invalid/mcp",
            "https://control.example.invalid/mcp?token=secret",
            "https://control.example.invalid/mcp?",
            "https://control.example.invalid/mcp#fragment",
            "https://control.example.invalid/mcp#",
            "https://control.example.invalid/other",
            "https://control.example.invalid/\x01mcp",
            "https://control\x80.example.invalid/mcp",
            "https://control.example.invalid/mcp\u00a0",
        )

        for index, url in enumerate(invalid_urls):
            with self.subTest(url=url):
                output = self.root / f"invalid-output-{index}"
                result = _run_projector(
                    script,
                    self.cwd,
                    output,
                    "--mcp-url",
                    url,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())
                self.assertNotIn("fixture-token-DO-NOT-USE", result.stderr)
                self.assertNotIn("secret", result.stderr)


if __name__ == "__main__":
    unittest.main()
