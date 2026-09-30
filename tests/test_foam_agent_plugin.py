from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from expertise.errors import TargetError
from expertise.foam_binding import FOAM_WORKSPACE_PLACEHOLDER, bind_foam_workspace
from expertise.ir import MCPServer
from expertise.parser import parse_pack
from expertise.targets import compile_target
from expertise.targets.chatgpt import CONNECTION_PATH, compile_chatgpt

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "expertise" / "packs" / "foam-agent-plugin"


def _tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        content = path.read_bytes()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


class FoamAgentPackTests(unittest.TestCase):
    def setUp(self):
        self.source = parse_pack(PACK)

    def test_canonical_pack_contains_three_explicit_skills_and_direct_foam_tools(self):
        self.assertEqual(
            {skill.id for skill in self.source.ir.skills},
            {"process-inbox", "materialize-idea", "capture-source"},
        )
        self.assertEqual([server.id for server in self.source.ir.mcp_servers], ["foam"])
        self.assertEqual(
            set(self.source.ir.mcp_servers[0].tools),
            {
                "list_resources",
                "get_resource",
                "read_resource",
                "create_resource",
                "update_resource",
                "delete_resource",
                "move_resource",
                "list_queries",
                "get_query",
                "run_query",
                "get_outline",
                "get_connections",
                "get_orphans",
                "get_deadends",
                "get_placeholders",
                "traverse_graph",
                "get_graph_summary",
                "get_workspace_info",
                "search_resources",
                "search_by_property",
                "list_tags",
                "search_by_tag",
                "add_tags",
                "remove_tags",
                "rename_tag",
            },
        )

    def test_portable_and_codex_keep_one_source_and_workspace_binding_is_local(self):
        portable = compile_target(self.source, "portable")
        codex = compile_target(self.source, "codex")
        self.assertEqual(portable.source_digest, codex.source_digest)
        self.assertEqual(portable.file_map(), codex.file_map())
        canonical_mcp = json.loads(portable.files["mcp.json"])
        self.assertEqual(
            canonical_mcp["mcpServers"]["foam"]["args"],
            ["mcp", "--workspace", FOAM_WORKSPACE_PLACEHOLDER, "--allow-writes"],
        )

        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "Ideas Workspace"
            workspace.mkdir()
            bound = bind_foam_workspace(portable.file_map(), workspace)
            bound_mcp = json.loads(bound["mcp.json"])
            self.assertEqual(
                bound_mcp["mcpServers"]["foam"]["args"],
                ["mcp", "--workspace", str(workspace.resolve()), "--allow-writes"],
            )
            self.assertEqual(portable.files["mcp.json"], codex.files["mcp.json"])
            canonical_sources = b"\n".join(self.source.source_snapshot.values())
            self.assertNotIn(str(workspace).encode(), canonical_sources)

    def test_binding_requires_existing_absolute_workspace_and_refuses_wrong_config(
        self,
    ):
        artifact = compile_target(self.source, "portable").file_map()
        with self.assertRaisesRegex(TargetError, "filesystem root"):
            bind_foam_workspace(artifact, Path("/"))
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            workspace.mkdir()
            with self.assertRaisesRegex(TargetError, "absolute"):
                bind_foam_workspace(artifact, Path("relative"))
            invalid = dict(artifact)
            invalid["mcp.json"] = (
                b'{"mcpServers":{"foam":{"type":"stdio","command":"other"}}}'
            )
            with self.assertRaisesRegex(TargetError, "command"):
                bind_foam_workspace(invalid, workspace)

    def test_generic_chatgpt_projection_maps_registered_app_without_claiming_connection(
        self,
    ):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "Bound Workspace"
            workspace.mkdir()
            files, provenance = compile_chatgpt(
                self.source,
                {"foam": "asdk_app_fixture"},
                workspace=workspace,
                tunnel_id="tunnel_fixture",
            )
        self.assertEqual(provenance["connection_status"], "not_connected_by_projection")
        self.assertIn(CONNECTION_PATH, files)
        app_manifest = json.loads(files[".app.json"])
        self.assertEqual(app_manifest, {"apps": {"foam": {"id": "asdk_app_fixture"}}})
        plugin_manifest = json.loads(files["plugin.json"])
        self.assertEqual(
            plugin_manifest["extensions"]["com.openai"]["apps"], "./.app.json"
        )
        guide = files[CONNECTION_PATH].decode("utf-8")
        self.assertIn("tunnel-client init", guide)
        self.assertIn("--mcp-command", guide)
        self.assertIn("foam mcp --workspace", guide)
        self.assertIn("CONTROL_PLANE_API_KEY", guide)
        self.assertNotIn("FOAM_WORKSPACE__", guide)

    def test_chatgpt_package_precedes_app_registration_and_requires_workspace_binding(
        self,
    ):
        with tempfile.TemporaryDirectory() as temporary:
            files, provenance = compile_chatgpt(
                self.source, {}, workspace=Path(temporary)
            )
        self.assertEqual(json.loads(files[".app.json"]), {"apps": {}})
        self.assertEqual(provenance["connection_status"], "not_connected_by_projection")
        self.assertIn(
            "create the ChatGPT developer-mode app",
            files[CONNECTION_PATH].decode("utf-8"),
        )
        with self.assertRaisesRegex(TargetError, "workspace binding"):
            compile_chatgpt(self.source, {})
        with (
            tempfile.TemporaryDirectory() as temporary,
            self.assertRaisesRegex(TargetError, "tunnel ID"),
        ):
            compile_chatgpt(
                self.source,
                {"foam": "asdk_app_fixture"},
                workspace=Path(temporary),
                tunnel_id="tunnel_fixture; touch /tmp/unexpected",
            )

    def test_chatgpt_projection_rejects_partial_app_registration_mapping(self):
        second_server = MCPServer(
            id="remote",
            capabilities=("read",),
            permissions=("read",),
            tools=("remote_tool",),
        )
        source_with_two_servers = replace(
            self.source,
            ir=replace(
                self.source.ir,
                mcp_servers=(*self.source.ir.mcp_servers, second_server),
            ),
        )
        with (
            tempfile.TemporaryDirectory() as temporary,
            self.assertRaisesRegex(TargetError, "cover every Pack MCP server ID"),
        ):
            compile_chatgpt(
                source_with_two_servers,
                {"foam": "asdk_app_fixture"},
                workspace=Path(temporary),
            )

    def test_repository_projectors_run_from_external_cwd_and_are_deterministic(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "local Foam workspace"
            workspace.mkdir()
            app_mapping = root / "app-ids.json"
            app_mapping.write_text('{"foam":"asdk_app_fixture"}\n', encoding="utf-8")
            outputs = [root / "chatgpt-a", root / "chatgpt-b"]
            for output in outputs:
                result = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "scripts" / "project_chatgpt_plugin.py"),
                        "--pack-id",
                        "foam-agent-plugin",
                        "--app-ids-json",
                        str(app_mapping),
                        "--workspace",
                        str(workspace),
                        "--output",
                        str(output),
                    ],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(_tree_digest(outputs[0]), _tree_digest(outputs[1]))
            mcp = json.loads((outputs[0] / "mcp.json").read_text(encoding="utf-8"))
            self.assertEqual(
                mcp["mcpServers"]["foam"]["args"],
                ["mcp", "--workspace", str(workspace.resolve()), "--allow-writes"],
            )


if __name__ == "__main__":
    unittest.main()
