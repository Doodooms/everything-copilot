from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

from expertise.parser import parse_pack
from expertise.targets import compile_target
from harness_factory.adapters import _codex_project_plugin
from harness_factory.errors import HarnessFactoryError
from harness_factory.models import RunMode
from harness_factory.pilot_a_workspace import create_pilot_a_seed_repository
from harness_factory.runs import HarnessRunManager

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PACK_ROOT = REPOSITORY_ROOT / "expertise/packs/migration-readiness"


class PilotAWorkspaceTests(unittest.TestCase):
    def test_seed_repository_contains_only_codex_projection_and_no_remote(self):
        source = parse_pack(PACK_ROOT)
        artifact = compile_target(source, "codex")
        expected_project_files = {
            f".agents/plugins/{source.ir.id}/{path}"
            for path in artifact.files
            if not path.startswith("codex-agents/")
        } | {
            f".codex/agents/{Path(path).name}"
            for path in artifact.files
            if path.startswith("codex-agents/")
        }

        with self.subTest("generated files are exactly bounded"):
            import tempfile

            with tempfile.TemporaryDirectory() as temporary:
                seed_root = Path(temporary) / "seed"
                seed = create_pilot_a_seed_repository(PACK_ROOT, seed_root)

                tracked = set(
                    subprocess.run(
                        ["git", "-C", str(seed_root), "ls-files"],
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout.splitlines()
                )
                self.assertEqual(tracked, expected_project_files)
                self.assertEqual(seed.source_digest, source.ir.content_digest)
                self.assertEqual(seed.projection_digest, artifact.digest)
                self.assertEqual(seed.pack_id, source.ir.id)
                self.assertEqual(
                    seed.plugin_relative_path, f".agents/plugins/{source.ir.id}"
                )
                self.assertEqual(set(seed.project_files), expected_project_files)
                self.assertEqual(seed.revision, _git(seed_root, "rev-parse", "HEAD"))
                self.assertEqual(_git(seed_root, "remote"), "")
                self.assertEqual(_git(seed_root, "status", "--porcelain"), "")
                self.assertFalse(any("mcp" in path.casefold() for path in tracked))
                self.assertTrue(
                    all((seed_root / path).is_file() for path in expected_project_files)
                )

    def test_existing_codex_project_plugin_owner_can_register_seed_without_losing_agents(
        self,
    ):
        import tempfile

        with tempfile.TemporaryDirectory() as temporary:
            seed_root = Path(temporary) / "seed"
            seed = create_pilot_a_seed_repository(PACK_ROOT, seed_root)
            manager = HarnessRunManager(
                seed_root,
                Path(temporary) / "run-state",
            )
            run = manager.create_run(
                harness="codex",
                base_revision=seed.revision,
                mode=RunMode.VALIDATION,
                owner="pilot-a-static-stage-0",
            )
            workspace = run.workspace
            sidecars_before = {
                path.relative_to(workspace).as_posix()
                for path in (workspace / ".codex/agents").glob("*.toml")
            }
            self.assertEqual(len(sidecars_before), 4)

            plugin_path = workspace / seed.plugin_relative_path
            try:
                with _codex_project_plugin(run, plugin_path):
                    self.assertTrue(
                        (workspace / ".agents/plugins/marketplace.json").is_file()
                    )
                    self.assertTrue((workspace / ".codex/config.toml").is_file())
                    self.assertEqual(
                        {
                            path.relative_to(workspace).as_posix()
                            for path in (workspace / ".codex/agents").glob("*.toml")
                        },
                        sidecars_before,
                    )

                self.assertFalse(
                    (workspace / ".agents/plugins/marketplace.json").exists()
                )
                self.assertFalse((workspace / ".codex/config.toml").exists())
                self.assertEqual(
                    {
                        path.relative_to(workspace).as_posix()
                        for path in (workspace / ".codex/agents").glob("*.toml")
                    },
                    sidecars_before,
                )
            finally:
                manager.cleanup(
                    run.run_id,
                    owner="pilot-a-static-stage-0",
                )

    def test_refuses_preexisting_seed_destination_without_overwriting(self):
        import tempfile

        with tempfile.TemporaryDirectory() as temporary:
            seed_root = Path(temporary) / "seed"
            seed_root.mkdir()
            sentinel = seed_root / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")

            with self.assertRaises(HarnessFactoryError):
                create_pilot_a_seed_repository(PACK_ROOT, seed_root)

            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")


def _git(repository: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


if __name__ == "__main__":
    unittest.main()
