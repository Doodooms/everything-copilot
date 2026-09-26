import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PLUGINCTL_RUNTIME = ROOT / "agentic-core" / "runtime"
if str(PLUGINCTL_RUNTIME) not in sys.path:
    sys.path.insert(0, str(PLUGINCTL_RUNTIME))
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))

from expertise.parser import parse_pack  # noqa: E402
from pluginctl import (  # noqa: E402
    PluginControlError,
    PluginController,
    TrustedRegistry,
    TrustedSource,
)
from pluginctl.cli import main as pluginctl_main  # noqa: E402
from test_expertise_framework import write_pack  # noqa: E402


def trusted_registry_for(source):
    return TrustedRegistry(
        [
            TrustedSource(
                reference=source.ir.reference,
                source_root=source.root,
                digest=source.ir.content_digest,
                publisher=source.ir.trust.publisher,
                source=source.ir.trust.source,
            )
        ]
    )


def run_cli(args):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = pluginctl_main(args)
    return code, json.loads(output.getvalue())


class PluginctlLifecycleTests(unittest.TestCase):
    def test_core_profile_uses_complete_skills_and_excludes_route_temporaries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspace"
            workspace.mkdir()
            controller = PluginController(
                root / "private-store",
                workspace_root=workspace,
            )

            _, _, files, skill_ids = controller._load_core()

        published_skill_manifests = {
            path
            for path in files
            if path.startswith("skills/") and path.endswith("/SKILL.md")
        }
        self.assertEqual(
            published_skill_manifests,
            {f"skills/{skill_id}/SKILL.md" for skill_id in skill_ids},
        )
        self.assertFalse(
            any(path.endswith("/.workflow-routes.tmp") for path in files)
        )

    def test_store_root_is_required_and_install_needs_trust_digest_and_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspace"
            workspace.mkdir()
            source = parse_pack(write_pack(root / "source"))
            store = root / "private-store"
            controller = PluginController(
                store,
                workspace_root=workspace,
                trusted_registry=trusted_registry_for(source),
            )

            with self.assertRaises(TypeError):
                PluginController(workspace_root=workspace)
            self.assertEqual(controller.check(source.root)["state"], "AVAILABLE")
            with self.assertRaisesRegex(PluginControlError, "explicit user approval"):
                controller.install(source.ir.id, source.ir.version, approved=False)
            with self.assertRaisesRegex(PluginControlError, "digest"):
                controller.install(
                    source.ir.id,
                    source.ir.version,
                    approved=True,
                    expected_digest="0" * 64,
                )
            self.assertFalse(store.exists())

            result = controller.install(
                source.ir.id,
                source.ir.version,
                approved=True,
                expected_digest=source.ir.content_digest,
            )
            installed_root = (
                store / "packs" / source.ir.id / source.ir.version / "source"
            )
            installed = parse_pack(installed_root)
            installed_skill = (
                installed_root / "skills/demo-pack-skill/SKILL.md"
            ).read_bytes()
            source_skill = (
                source.root / "skills/demo-pack-skill/SKILL.md"
            ).read_bytes()
            self.assertEqual(installed_skill, source_skill)

        self.assertEqual(result["state"], "INSTALLED")
        self.assertEqual(installed.ir.content_digest, source.ir.content_digest)

    def test_managed_profile_composes_core_pack_and_pending_runtime_without_github(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspace"
            workspace.mkdir()
            store = root / "private-store"
            source = parse_pack(write_pack(root / "source"))
            controller = PluginController(
                store,
                workspace_root=workspace,
                trusted_registry=trusted_registry_for(source),
                host_capabilities=["host.search.inspect"],
            )
            controller.install(
                source.ir.id,
                source.ir.version,
                approved=True,
                expected_digest=source.ir.content_digest,
            )

            resolved = controller.resolve()
            self.assertEqual(resolved.core.id, "agentic-core")
            self.assertEqual(resolved.packs.host_capabilities, ("host.search.inspect",))
            self.assertEqual(resolved.packs.packs, ())

            activated = controller.activate(
                source.ir.id,
                source.ir.version,
                capabilities=["demo.read"],
            )
            materialized = controller.materialize()
            inspected = controller.inspect()
            lock = json.loads(
                (workspace / ".agentic/profile.lock").read_text(encoding="utf-8")
            )
            profile = Path(materialized["profile_path"])
            profile_has_plugin = (profile / "plugin.json").is_file()
            profile_has_skill = (
                profile / "skills/demo-pack-skill/SKILL.md"
            ).is_file()
            profile_has_agent = (
                profile
                / "com.github.copilot/agents/demo-pack-engineer.agent.md"
            ).is_file()
            profile_has_no_github = not (profile / ".github").exists()
            profile_is_outside_workspace = ".github" not in profile.parts

        self.assertEqual(activated["state"], "MATERIALIZED_PENDING_ACTIVATION")
        self.assertFalse(activated["runtime_visible"])
        self.assertEqual(materialized["state"], "MATERIALIZED_PENDING_ACTIVATION")
        self.assertFalse(materialized["runtime_visible"])
        self.assertEqual(inspected["runtime_state"], "MATERIALIZED_PENDING_ACTIVATION")
        self.assertTrue(inspected["installed"][0]["desired_active"])
        self.assertEqual(lock["active_set"]["capabilities"], ["demo.read"])
        self.assertEqual(lock["effective_ir"]["core"]["id"], "agentic-core")
        self.assertEqual(
            lock["effective_ir"]["core"]["content_digest"],
            resolved.core_digest,
        )
        projections = {
            projection["agent_id"]: projection
            for projection in lock["effective_ir"]["packs"]["agent_projections"]
        }
        self.assertEqual(projections["reviewer"]["skills"], [])
        self.assertEqual(projections["reviewer"]["mcp_servers"], [])
        self.assertIn("demo-pack-skill", projections["researcher"]["skills"])
        self.assertEqual(
            lock["effective_ir"]["packs"]["provenance"][0]["pack"]["id"],
            "demo-pack",
        )
        self.assertTrue(profile_has_plugin)
        self.assertTrue(profile_has_skill)
        self.assertTrue(profile_has_agent)
        self.assertTrue(profile_has_no_github)
        self.assertTrue(profile_is_outside_workspace)

    def test_failed_activation_preserves_active_set_and_profile_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspace"
            workspace.mkdir()
            store = root / "private-store"
            first = parse_pack(
                write_pack(
                    root / "first",
                    pack_id="first-pack",
                    capability_id="first.read",
                )
            )
            missing_capability = parse_pack(
                write_pack(
                    root / "missing",
                    pack_id="missing-pack",
                    capability_id="missing.provide",
                )
            )
            controller = PluginController(
                store,
                workspace_root=workspace,
                trusted_registry=TrustedRegistry(
                    [
                        TrustedSource(
                            first.ir.reference,
                            first.root,
                            first.ir.content_digest,
                            first.ir.trust.publisher,
                            first.ir.trust.source,
                        ),
                        TrustedSource(
                            missing_capability.ir.reference,
                            missing_capability.root,
                            missing_capability.ir.content_digest,
                            missing_capability.ir.trust.publisher,
                            missing_capability.ir.trust.source,
                        ),
                    ]
                ),
            )
            for source in (first, missing_capability):
                controller.install(
                    source.ir.id,
                    source.ir.version,
                    approved=True,
                    expected_digest=source.ir.content_digest,
                )
            controller.activate(
                first.ir.id, first.ir.version, capabilities=["first.read"]
            )
            profile_yaml = (workspace / ".agentic/profile.yaml").read_bytes()
            profile_lock = (workspace / ".agentic/profile.lock").read_bytes()

            with self.assertRaisesRegex(PluginControlError, "unknown capability"):
                controller.activate(
                    missing_capability.ir.id,
                    missing_capability.ir.version,
                    capabilities=["unknown.permission"],
                )
            self.assertEqual(
                (workspace / ".agentic/profile.yaml").read_bytes(), profile_yaml
            )
            self.assertEqual(
                (workspace / ".agentic/profile.lock").read_bytes(), profile_lock
            )

    def test_staged_profile_failure_keeps_previous_workspace_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspace"
            workspace.mkdir()
            first = parse_pack(
                write_pack(
                    root / "first",
                    pack_id="first-pack",
                    capability_id="first.read",
                )
            )
            second = parse_pack(
                write_pack(
                    root / "second",
                    pack_id="second-pack",
                    capability_id="second.read",
                )
            )
            controller = PluginController(
                root / "private-store",
                workspace_root=workspace,
                trusted_registry=TrustedRegistry(
                    [
                        TrustedSource(
                            item.ir.reference,
                            item.root,
                            item.ir.content_digest,
                            item.ir.trust.publisher,
                            item.ir.trust.source,
                        )
                        for item in (first, second)
                    ]
                ),
            )
            for source in (first, second):
                controller.install(
                    source.ir.id,
                    source.ir.version,
                    approved=True,
                    expected_digest=source.ir.content_digest,
                )
            controller.activate(
                first.ir.id, first.ir.version, capabilities=["first.read"]
            )
            previous_yaml = (workspace / ".agentic/profile.yaml").read_bytes()
            previous_lock = (workspace / ".agentic/profile.lock").read_bytes()

            with patch.object(
                controller,
                "_materialize_artifact",
                side_effect=PluginControlError("staged target validation failed"),
            ):
                with self.assertRaisesRegex(
                    PluginControlError, "staged target validation failed"
                ):
                    controller.activate(
                        second.ir.id,
                        second.ir.version,
                        capabilities=["second.read"],
                    )

            self.assertEqual(
                (workspace / ".agentic/profile.yaml").read_bytes(), previous_yaml
            )
            self.assertEqual(
                (workspace / ".agentic/profile.lock").read_bytes(), previous_lock
            )

    def test_deactivate_and_rollback_recompose_from_the_previous_active_set(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspace"
            workspace.mkdir()
            source = parse_pack(write_pack(root / "source"))
            controller = PluginController(
                root / "private-store",
                workspace_root=workspace,
                trusted_registry=trusted_registry_for(source),
            )
            controller.install(
                source.ir.id,
                source.ir.version,
                approved=True,
            )
            activated = controller.activate(
                source.ir.id,
                source.ir.version,
                capabilities=["demo.read"],
            )
            deactivated = controller.deactivate(source.ir.id, source.ir.version)
            rolled_back = controller.rollback()

        self.assertEqual(activated["state"], "MATERIALIZED_PENDING_ACTIVATION")
        self.assertEqual(deactivated["state"], "CORE_ONLY")
        self.assertEqual(rolled_back["state"], "MATERIALIZED_PENDING_ACTIVATION")
        self.assertEqual(rolled_back["profile_hash"], activated["profile_hash"])
        self.assertFalse(rolled_back["runtime_visible"])

    def test_cli_exposes_bounded_lifecycle_commands_with_explicit_store_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspace"
            workspace.mkdir()
            store = root / "private-store"
            source = parse_pack(write_pack(root / "source"))
            store.mkdir()
            (store / "trusted-registry.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "sources": [
                            {
                                "id": source.ir.id,
                                "version": source.ir.version,
                                "path": str(source.root),
                                "digest": source.ir.content_digest,
                                "publisher": source.ir.trust.publisher,
                                "source": source.ir.trust.source,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            common = [
                "--store-root",
                str(store),
                "--workspace-root",
                str(workspace),
            ]
            check_code, checked = run_cli([*common, "check", str(source.root)])
            install_code, installed = run_cli(
                [
                    *common,
                    "install",
                    source.ir.id,
                    source.ir.version,
                    "--approve",
                ]
            )
            resolve_code, resolved = run_cli([*common, "resolve"])
            activate_code, activated = run_cli(
                [
                    *common,
                    "activate",
                    source.ir.id,
                    source.ir.version,
                    "--capability",
                    "demo.read",
                ]
            )
            materialize_code, materialized = run_cli([*common, "materialize"])
            inspect_code, inspected = run_cli([*common, "inspect"])
            deactivate_code, deactivated = run_cli(
                [*common, "deactivate", source.ir.id, source.ir.version]
            )
            rollback_code, rolled_back = run_cli([*common, "rollback"])

        self.assertEqual(
            [
                check_code,
                install_code,
                resolve_code,
                activate_code,
                materialize_code,
                inspect_code,
                deactivate_code,
                rollback_code,
            ],
            [0] * 8,
        )
        self.assertTrue(checked["trusted"])
        self.assertEqual(installed["state"], "INSTALLED")
        self.assertEqual(resolved["status"], "resolved")
        self.assertEqual(activated["state"], "MATERIALIZED_PENDING_ACTIVATION")
        self.assertEqual(materialized["state"], "MATERIALIZED_PENDING_ACTIVATION")
        self.assertEqual(inspected["runtime_visible"], False)
        self.assertEqual(deactivated["state"], "CORE_ONLY")
        self.assertEqual(rolled_back["state"], "MATERIALIZED_PENDING_ACTIVATION")
