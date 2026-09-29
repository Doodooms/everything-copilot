from __future__ import annotations

import json
import stat
import tempfile
import unittest
from pathlib import Path

import yaml

from expertise.errors import TargetError
from expertise.targets.antigravity_plugin import (
    ANTIGRAVITY_PLUGIN_SCHEMA,
    materialize_projection,
    project_core_plugin,
    validate_antigravity_layout,
)

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "agentic-core"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _agent(
    *,
    name: str,
    user_invocable: bool,
    tools: list[str],
    agents: list[str] | None = None,
    disable_model_invocation: bool = False,
) -> str:
    metadata = {
        "name": name,
        "description": f"WHAT: {name}. INVOKE FOR: test. DO NOT INVOKE FOR: other work.",
    }
    return (
        "---\n"
        + yaml.safe_dump(metadata, sort_keys=False)
        + "---\n"
        + (
            "<agent-skills>\n- MUST load `orchestration` for this test.\n</agent-skills>\n"
            "\nAgent instructions remain in the generated body.\n"
        )
    )


def _minimal_source(root: Path) -> None:
    _write(
        root / "plugin.json",
        json.dumps(
            {
                "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
                "name": "agentic-core",
                "description": "Fixture plugin",
                "version": "9.9.9",
                "author": {"name": "Source Author"},
                "keywords": ["source-only"],
            }
        ),
    )
    _write(
        root / "skills/orchestration/SKILL.md",
        "---\nname: orchestration\ndescription: Coordinates work.\n"
        "user-invocable: true\nmetadata:\n  source: copilot\n---\n"
        "Use the workflow at [method](./workflows/method.md).\n",
    )
    _write(
        root / "skills/orchestration/workflows/method.md",
        "---\nid: method\ndescription: A nested procedure.\n---\nFollow it.\n",
    )
    (root / "skills/empty-domain").mkdir(parents=True)
    _write(
        root / "agents/orchestrator.md",
        _agent(
            name="orchestrator",
            user_invocable=True,
            disable_model_invocation=True,
            tools=["vscode/askQuestions", "read", "agent", "skill", "todo"],
            agents=["helper"],
        ),
    )
    _write(
        root / "agents/helper.md",
        _agent(
            name="helper",
            user_invocable=False,
            tools=["read", "search", "edit", "execute", "skill", "web"],
        ),
    )
    _write(
        root / "agents/projections.json",
        json.dumps(
            {
                "copilot": {
                    "orchestrator": {
                        "target": "vscode",
                        "user-invocable": True,
                        "disable-model-invocation": True,
                        "tools": [
                            "vscode/askQuestions",
                            "read",
                            "agent",
                            "skill",
                            "todo",
                        ],
                        "agents": ["helper"],
                    },
                    "helper": {
                        "target": "vscode",
                        "user-invocable": False,
                        "tools": ["read", "search", "edit", "execute", "skill", "web"],
                    },
                },
                "codex": {
                    "orchestrator": {"model": "gpt-6-luna", "reasoning-effort": "high"},
                    "helper": {"model": "gpt-6-luna", "reasoning-effort": "high"},
                },
                "antigravity": {
                    "orchestrator": {
                        "tools": [
                            "ask_question",
                            "list_directory",
                            "view_file",
                            "invoke_subagent",
                        ],
                        "mainAgent": True,
                        "subagent": False,
                        "agents": ["helper"],
                    },
                    "helper": {
                        "tools": [
                            "list_directory",
                            "view_file",
                            "find_file",
                            "grep_search",
                            "search_directory",
                            "write_to_file",
                            "run_command",
                        ],
                        "mainAgent": False,
                        "subagent": True,
                    },
                },
            },
            indent=2,
        ),
    )
    _write(
        root / "agents/projection-losses.json",
        json.dumps(
            {
                "copilot": [],
                "codex": ["Codex test loss."],
                "antigravity": ["Antigravity test loss."],
            }
        ),
    )
    _write(
        root / "mcp.json",
        json.dumps(
            {
                "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
                "mcpServers": {
                    "github-mcp-server": {
                        "type": "stdio",
                        "command": "bash",
                        "args": ["runtime/mcp/github-app-stdio.sh"],
                        "cwd": "${PLUGIN_ROOT}",
                    }
                },
            }
        ),
    )
    _write(root / "runtime/mcp/github-app-stdio.sh", "#!/usr/bin/env bash\nexit 0\n")


class AntigravityProjectionTests(unittest.TestCase):
    def test_real_projection_has_eleven_domain_skills_and_fifty_nine_nested_workflows(
        self,
    ):
        projection = project_core_plugin(CORE)

        skill_entrypoints = sorted(
            path
            for path in projection.files
            if path.startswith("skills/")
            and path.count("/") == 2
            and path.endswith("/SKILL.md")
        )
        nested_workflows = [
            path
            for path in projection.files
            if path.startswith("skills/")
            and "/workflows/" in path
            and path.endswith(".md")
        ]
        self.assertEqual(len(skill_entrypoints), 11)
        self.assertEqual(len(nested_workflows), 58)
        self.assertFalse(any("/e2e-testing/" in path for path in projection.files))
        self.assertFalse(
            any("/test-coverage-review/" in path for path in projection.files)
        )
        self.assertFalse(
            any(
                path.count("/") == 2 and path.endswith("/SKILL.md")
                for path in nested_workflows
            )
        )

    def test_manifest_is_antigravity_specific_and_drops_source_only_metadata(self):
        projection = project_core_plugin(CORE)
        manifest = json.loads(projection.files["plugin.json"])

        self.assertEqual(
            manifest,
            {
                "$schema": ANTIGRAVITY_PLUGIN_SCHEMA,
                "name": "agentic-core",
                "description": json.loads(
                    (CORE / "plugin.json").read_text(encoding="utf-8")
                )["description"],
            },
        )
        self.assertNotIn("version", manifest)
        self.assertNotIn("author", manifest)
        self.assertNotIn("keywords", manifest)

    def test_agent_projection_uses_antigravity_roles_tools_and_preserves_bodies(self):
        projection = project_core_plugin(CORE)
        agent_files = sorted(
            path
            for path in projection.files
            if path.startswith("agents/") and path.endswith(".md")
        )
        agents = [
            yaml.safe_load(projection.files[path].decode("utf-8").split("---", 2)[1])
            for path in agent_files
        ]

        self.assertEqual(len(agent_files), 9)
        self.assertTrue(all(not path.endswith(".agent.md") for path in agent_files))
        orchestrator = next(
            metadata for metadata in agents if metadata["name"] == "orchestrator"
        )
        self.assertIs(orchestrator["mainAgent"], True)
        self.assertIs(orchestrator["subagent"], False)
        self.assertEqual(
            set(orchestrator["agents"]),
            {
                "architect",
                "challenger",
                "devops",
                "implementer",
                "planner",
                "quality-assurance",
                "researcher",
                "reviewer",
            },
        )
        helper_agents = [
            metadata for metadata in agents if metadata["name"] != "orchestrator"
        ]
        self.assertEqual(len(helper_agents), 8)
        self.assertTrue(
            all(metadata["mainAgent"] is False for metadata in helper_agents)
        )
        self.assertTrue(all(metadata["subagent"] is True for metadata in helper_agents))
        for metadata in agents:
            self.assertNotIn("target", metadata)
            self.assertNotIn("model", metadata)
            self.assertNotIn("reasoning-effort", metadata)
            self.assertNotIn("user-invocable", metadata)
            self.assertNotIn("disable-model-invocation", metadata)
            self.assertTrue(metadata["tools"])
            self.assertTrue(metadata["skills"])
        orchestrator_path = next(
            path for path in agent_files if path == "agents/orchestrator.md"
        )
        self.assertIn(b"<agent-skills>", projection.files[orchestrator_path])
        self.assertIn(
            b"resolve this agent's `<agent-skills>` policy",
            projection.files[orchestrator_path],
        )

    def test_mcp_projection_resolves_plugin_root_without_credentials(self):
        projection = project_core_plugin(CORE)
        config = json.loads(projection.files["mcp_config.json"])
        servers = config["mcpServers"]

        self.assertEqual(set(servers), {"context7", "github-mcp-server", "semgrep"})
        for server in servers.values():
            self.assertNotIn("type", server)
            self.assertNotIn("env", server)
        github = servers["github-mcp-server"]
        self.assertEqual(github["cwd"], ".")
        self.assertEqual(github["args"], ["runtime/mcp/github-app-stdio.sh"])
        self.assertIn("runtime/mcp/github-app-stdio.sh", projection.files)
        self.assertNotIn(
            b"GITHUB_APP_PRIVATE_KEY_PATH=", projection.files["mcp_config.json"]
        )
        self.assertNotIn(b"${PLUGIN_ROOT}", projection.files["mcp_config.json"])

    def test_internal_skill_links_and_executable_files_survive_projection(self):
        projection = project_core_plugin(CORE)
        parent = projection.files["skills/operations/SKILL.md"].decode("utf-8")
        linked_path = "skills/operations/workflows/install-agent-plugin.md"

        self.assertIn("./workflows/install-agent-plugin.md", parent)
        self.assertIn(linked_path, projection.files)
        self.assertIn(
            "skills/operations/references/verification-loop/scripts/collect_diff_status.sh",
            projection.executable_files,
        )

    def test_minimal_fixture_omits_empty_skills_and_validates_target_layout(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            _minimal_source(source)
            projection = project_core_plugin(source)

            self.assertIn("skills/orchestration/workflows/method.md", projection.files)
            self.assertNotIn("skills/empty-domain/SKILL.md", projection.files)
            validate_antigravity_layout(projection)

    def test_layout_validator_rejects_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            _minimal_source(source)
            projection = project_core_plugin(source)
            unsafe_files = dict(projection.files)
            unsafe_files["../outside.txt"] = b"unsafe"

            with self.assertRaises(TargetError):
                validate_antigravity_layout(unsafe_files)

    def test_materializer_preserves_executable_mode_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            _minimal_source(source)
            script = source / "skills/orchestration/scripts/run.sh"
            _write(script, "#!/usr/bin/env bash\nexit 0\n")
            script.chmod(0o755)
            projection = project_core_plugin(source)
            output = Path(temporary) / "generated-plugin"

            materialize_projection(projection, output)

            projected_script = output / "skills/orchestration/scripts/run.sh"
            self.assertTrue(projected_script.stat().st_mode & stat.S_IXUSR)
            with self.assertRaises(TargetError):
                materialize_projection(projection, output)


if __name__ == "__main__":
    unittest.main()
