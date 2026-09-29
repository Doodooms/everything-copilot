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

import tomllib

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "agentic-core"


def _copy_installed_plugin(destination: Path) -> None:
    shutil.copytree(
        CORE,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", "*.py[cod]"),
    )


def _run_script(
    script: Path, cwd: Path, *arguments: str
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONNOUSERSITE"] = "1"
    uv = shutil.which("uv")
    command = (
        [uv, "run", "--no-project", "--script", str(script), *arguments]
        if uv
        else [sys.executable, str(script), *arguments]
    )
    return subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _file_map_digest(
    files: dict[str, bytes], executable_files: frozenset[str] = frozenset()
) -> str:
    digest = hashlib.sha256()
    for relative, content in sorted(files.items()):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(b"x" if relative in executable_files else b"-")
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def _tree_digest(root: Path) -> str:
    files = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix not in {".pyc", ".pyo"}
    }
    executable = frozenset(
        relative for relative in files if (root / relative).stat().st_mode & 0o111
    )
    return _file_map_digest(files, executable)


class CheckoutIndependentProjectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(
            prefix="agentic-core-installed-projections-"
        )
        self.root = Path(self.temporary.name)
        self.plugin = self.root / "installed" / "agentic-core"
        self.cwd = self.root / "consumer" / "unrelated-working-directory"
        self.cwd.mkdir(parents=True)
        _copy_installed_plugin(self.plugin)

    def tearDown(self):
        self.temporary.cleanup()

    def test_installed_plugin_contains_projection_runtime_and_canonical_inputs(self):
        expected_files = {
            "plugin.json",
            "core_agents.py",
            "agents/projections.json",
            "agents/projection-losses.json",
            "runtime/project_codex_agents.py",
            "runtime/project_antigravity_plugin.py",
            "runtime/projection_metadata.py",
            "runtime/expertise/targets/codex.py",
            "runtime/expertise/targets/antigravity_plugin.py",
        }
        for relative in expected_files:
            with self.subTest(relative=relative):
                self.assertTrue((self.plugin / relative).is_file())
        self.assertEqual(
            len(list((self.plugin / "agents").glob("*.md"))),
            9,
        )
        self.assertEqual(
            (self.plugin / "plugin.json").read_bytes(),
            (CORE / "plugin.json").read_bytes(),
        )
        self.assertFalse((self.plugin / ".git").exists())
        second_copy = self.root / "installed-second" / "agentic-core"
        second_copy.parent.mkdir()
        _copy_installed_plugin(second_copy)
        self.assertEqual(_tree_digest(self.plugin), _tree_digest(second_copy))

    def test_codex_projection_runs_from_installed_plugin_and_is_reproducible(self):
        script = self.plugin / "runtime" / "project_codex_agents.py"
        source_digest_before = _tree_digest(self.plugin)
        homes = [self.root / "codex-home-a", self.root / "codex-home-b"]
        summaries = []

        for home in homes:
            result = _run_script(script, self.cwd, "--codex-home", str(home))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            summary = json.loads(result.stdout)
            self.assertEqual(summary["status"], "projected")
            self.assertEqual(summary["target"], "codex")
            self.assertEqual(summary["agent_count"], 9)
            summaries.append(summary)

        agent_files = [home / "agents" for home in homes]
        first_names = {path.name for path in agent_files[0].glob("*.toml")}
        self.assertEqual(len(first_names), 9)
        self.assertEqual(
            first_names, {path.name for path in agent_files[1].glob("*.toml")}
        )
        self.assertFalse(list(agent_files[0].glob("*.md")))
        for summary, output in zip(summaries, agent_files, strict=True):
            self.assertEqual(_tree_digest(output), summary["artifact_sha256"])
            for path in output.glob("*.toml"):
                role = tomllib.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(role["name"], path.stem)
                self.assertTrue(role["developer_instructions"])
                self.assertNotEqual(
                    path.read_text(encoding="utf-8"),
                    (self.plugin / "agents" / f"{path.stem}.md").read_text(
                        encoding="utf-8"
                    ),
                )

        self.assertEqual(
            summaries[0]["artifact_sha256"], summaries[1]["artifact_sha256"]
        )
        self.assertEqual(summaries[0]["source_sha256"], summaries[1]["source_sha256"])
        self.assertEqual(summaries[0]["source_sha256"], source_digest_before)
        self.assertEqual(source_digest_before, _tree_digest(self.plugin))

        check = _run_script(
            script,
            self.cwd,
            "--codex-home",
            str(homes[0]),
            "--check",
        )
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
        self.assertEqual(json.loads(check.stdout)["status"], "current")

    def test_antigravity_projection_runs_from_installed_plugin_and_validates(self):
        script = self.plugin / "runtime" / "project_antigravity_plugin.py"
        source_digest_before = _tree_digest(self.plugin)
        outputs = [self.root / "antigravity-a", self.root / "antigravity-b"]
        summaries = []

        for output in outputs:
            result = _run_script(script, self.cwd, "--output", str(output))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            summary = json.loads(result.stdout)
            self.assertEqual(summary["status"], "projected")
            self.assertEqual(summary["target"], "antigravity")
            self.assertEqual(len(summary["skills"]), 11)
            self.assertEqual(summary["nested_workflows"], 59)
            self.assertEqual(len(summary["agents"]), 9)
            self.assertEqual(len(summary["mcp_servers"]), 3)
            self.assertEqual(_tree_digest(output), summary["artifact_sha256"])
            summaries.append(summary)

        self.assertEqual(
            summaries[0]["artifact_sha256"], summaries[1]["artifact_sha256"]
        )
        self.assertEqual(summaries[0]["source_sha256"], summaries[1]["source_sha256"])
        self.assertEqual(summaries[0]["source_sha256"], source_digest_before)
        self.assertEqual(summaries[0]["projector_package_sha256"], source_digest_before)
        self.assertEqual(source_digest_before, _tree_digest(self.plugin))
        source_manifest = json.loads(
            (self.plugin / "plugin.json").read_text(encoding="utf-8")
        )
        target_manifest = json.loads(
            (outputs[0] / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertNotEqual(source_manifest["$schema"], target_manifest["$schema"])
        self.assertNotIn("version", target_manifest)

        agy = shutil.which("agy")
        if agy is None:
            self.skipTest("Antigravity CLI is not installed")
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        environment.pop("PYTHONHOME", None)
        validation = subprocess.run(
            [agy, "plugin", "validate", str(outputs[0])],
            cwd=self.cwd,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(
            validation.returncode, 0, validation.stdout + validation.stderr
        )


if __name__ == "__main__":
    unittest.main()
