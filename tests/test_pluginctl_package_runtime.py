from __future__ import annotations

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
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"


class PluginctlPackageRuntimeTests(unittest.TestCase):
    def test_packaged_expertise_matches_canonical_source(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "sync_pluginctl_runtime.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_installed_package_runs_resolve_from_an_arbitrary_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            marketplace_root = fixture / "marketplace"
            installed_core = marketplace_root / "agentic-core"
            arbitrary_cwd = fixture / "unrelated" / "working-directory"
            workspace = fixture / "workspace"
            store = fixture / "private-store"
            marketplace_root.mkdir()
            arbitrary_cwd.mkdir(parents=True)
            workspace.mkdir()
            shutil.copyfile(MARKETPLACE, marketplace_root / "marketplace.json")
            shutil.copytree(
                CORE,
                installed_core,
                ignore=shutil.ignore_patterns("__pycache__", "*.py[cod]"),
            )

            catalog = json.loads(
                (marketplace_root / "marketplace.json").read_text(encoding="utf-8")
            )
            plugin = next(
                item for item in catalog["plugins"] if item["name"] == "agentic-core"
            )
            source_path = (marketplace_root / plugin["source"]["path"]).resolve()
            self.assertEqual(source_path, installed_core.resolve())
            manifest = json.loads(
                (source_path / "plugin.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["name"], "agentic-core")
            self.assertEqual(manifest["version"], "0.3.5")
            self.assertTrue(
                (source_path / "skills" / "orchestration" / "SKILL.md").is_file()
            )
            mcp_manifest = json.loads(
                (source_path / "mcp.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                set(mcp_manifest["mcpServers"]),
                {"context7", "github-mcp-server", "semgrep"},
            )

            environment = os.environ.copy()
            environment.pop("PYTHONPATH", None)
            environment.pop("PYTHONHOME", None)
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            entrypoint = installed_core / "runtime" / "pluginctl_cli.py"
            cli_args = [
                "--store-root",
                str(store),
                "--workspace-root",
                str(workspace),
                "resolve",
            ]
            uv = shutil.which("uv")
            command = (
                [uv, "run", "--script", str(entrypoint), *cli_args]
                if uv
                else [sys.executable, str(entrypoint), *cli_args]
            )
            result = subprocess.run(
                command,
                cwd=arbitrary_cwd,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "resolved")
            self.assertFalse(
                store.exists(), "read-only resolve created the private store"
            )
            self.assertFalse(
                (workspace / ".agentic").exists(),
                "read-only resolve created workspace state",
            )


if __name__ == "__main__":
    unittest.main()
