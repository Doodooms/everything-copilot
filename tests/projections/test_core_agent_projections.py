from __future__ import annotations

import contextlib
import hashlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path

import tomllib
import yaml

from factory.projection.core_agents import (
    project_codex_projection,
    project_copilot_projection,
)
from scripts.install_codex_agents import _projected_agents as packaged_codex_projection
from scripts.install_codex_agents import _run as install_codex_agents
from scripts.project_plugin_agents import main as project_plugin_agents

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "agentic-core"


class CoreAgentProjectionTests(unittest.TestCase):
    def test_symlinked_agents_directory_fails_before_creating_projection_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source = workspace / "source"
            shutil.copytree(
                SOURCE, source, ignore=shutil.ignore_patterns("com.github.copilot")
            )
            (source / "agents").rename(source / "agents-original")
            (source / "agents").symlink_to(SOURCE / "agents", target_is_directory=True)
            output = workspace / "projection"
            args = [
                "codex",
                "--source-root",
                str(source),
                "--output-dir",
                str(output),
            ]

            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(project_plugin_agents(args), 2)

            self.assertFalse(output.exists())

    def test_symlinked_agent_file_fails_before_creating_projection_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source = workspace / "source"
            shutil.copytree(
                SOURCE, source, ignore=shutil.ignore_patterns("com.github.copilot")
            )
            agent = source / "agents/architect.md"
            agent.unlink()
            agent.symlink_to(SOURCE / "agents/architect.md")
            output = workspace / "projection"
            args = [
                "codex",
                "--source-root",
                str(source),
                "--output-dir",
                str(output),
            ]

            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(project_plugin_agents(args), 2)

            self.assertFalse(output.exists())

    def test_source_symlink_is_rejected_instead_of_omitted_from_provenance(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            shutil.copytree(
                SOURCE, source, ignore=shutil.ignore_patterns("com.github.copilot")
            )
            (source / "README-alias.md").symlink_to(source / "README.md")

            with self.assertRaisesRegex(ValueError, "source must not contain symlinks"):
                project_codex_projection(source)

    def test_projection_cli_builds_and_checks_all_targets_in_temporary_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            for target in ("codex", "copilot", "claude"):
                output = workspace / target
                args = [
                    target,
                    "--source-root",
                    str(SOURCE),
                    "--output-dir",
                    str(output),
                ]
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(project_plugin_agents(args), 0)
                    self.assertEqual(project_plugin_agents([*args, "--check"]), 0)
                sidecar = (
                    output.with_name(f"{output.name}.projection.json")
                    if target == "claude"
                    else output.with_name(f"{output.name}.{target}.projection.json")
                )
                self.assertTrue(sidecar.is_file())

    def test_codex_installer_is_checkable_and_force_is_scoped_to_generated_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            codex_home = Path(temporary) / "codex-home"
            agents = codex_home / "agents"
            agents.mkdir(parents=True)
            unrelated = agents / "custom.toml"
            unrelated.write_text("preserve", encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    install_codex_agents(
                        source_root=SOURCE,
                        codex_home=codex_home,
                        check=False,
                        force=False,
                    ),
                    0,
                )
                self.assertEqual(
                    install_codex_agents(
                        source_root=SOURCE,
                        codex_home=codex_home,
                        check=True,
                        force=False,
                    ),
                    0,
                )
            provenance = agents / "agentic-core-codex.projection.json"
            self.assertTrue(provenance.is_file())
            (agents / "orchestrator.toml").write_text("stale", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(ValueError, "--force"):
                    install_codex_agents(
                        source_root=SOURCE,
                        codex_home=codex_home,
                        check=False,
                        force=False,
                    )
                self.assertEqual(
                    install_codex_agents(
                        source_root=SOURCE,
                        codex_home=codex_home,
                        check=False,
                        force=True,
                    ),
                    0,
                )
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "preserve")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    install_codex_agents(
                        source_root=SOURCE,
                        codex_home=codex_home,
                        check=True,
                        force=False,
                    ),
                    0,
                )

    def test_explicit_source_builds_stable_codex_and_copilot_outputs(self):
        before = _source_digest(SOURCE)

        copilot_first = project_copilot_projection(SOURCE)
        copilot_second = project_copilot_projection(SOURCE)
        codex_first = project_codex_projection(SOURCE)
        codex_second = project_codex_projection(SOURCE)

        self.assertEqual(before, _source_digest(SOURCE))
        self.assertEqual(copilot_first.files, copilot_second.files)
        self.assertEqual(copilot_first.provenance, copilot_second.provenance)
        self.assertEqual(codex_first.files, codex_second.files)
        self.assertEqual(codex_first.provenance, codex_second.provenance)
        self.assertEqual(len(copilot_first.files), 9)
        self.assertEqual(len(codex_first.files), 9)
        self.assertEqual(copilot_first.provenance["target"], "copilot")
        self.assertEqual(codex_first.provenance["target"], "codex")
        self.assertEqual(copilot_first.provenance["source"]["name"], "agentic-core")
        for provenance in (
            copilot_first.provenance["source"],
            copilot_first.provenance["projector"],
        ):
            self.assertIn(provenance["dirty"], (None, True, False))
            if provenance["dirty"] is True:
                self.assertIsNone(provenance["git_commit"])
            elif provenance["dirty"] is False:
                self.assertEqual(
                    provenance["git_commit"], provenance["git_base_commit"]
                )
            else:
                self.assertIsNone(provenance["git_commit"])
                self.assertIsNone(provenance["git_base_commit"])
        self.assertEqual(len(copilot_first.provenance["source"]["sha256"]), 64)
        self.assertEqual(len(copilot_first.provenance["artifact_sha256"]), 64)
        self.assertEqual(codex_first.files, packaged_codex_projection())
        self.assertEqual(
            set(copilot_first.files),
            {
                path.name
                for path in (SOURCE / "com.github.copilot/agents").glob("*.agent.md")
            },
        )
        for name, content in copilot_first.files.items():
            self.assertEqual(
                content,
                (SOURCE / "com.github.copilot/agents" / name).read_bytes(),
            )
            metadata = yaml.safe_load(content.decode("utf-8").split("---", 2)[1])
            self.assertEqual(metadata["name"], name.removesuffix(".agent.md"))
        for name, content in codex_first.files.items():
            role = tomllib.loads(content.decode("utf-8"))
            self.assertEqual(role["name"], name.removesuffix(".toml"))
            self.assertTrue(role["developer_instructions"])


def _source_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file() and not path.is_symlink():
            if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            digest.update(path.relative_to(root).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
    return digest.hexdigest()


if __name__ == "__main__":
    unittest.main()
