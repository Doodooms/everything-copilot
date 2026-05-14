import json
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

import anyio
from mcp import ClientSession, StdioServerParameters, stdio_client


REPO_ROOT = Path(__file__).resolve().parents[1]
AHK_BIN = REPO_ROOT / "node_modules" / ".bin" / "ahk"
AHK_PACKAGE = (REPO_ROOT / "node_modules" / "@cardor" / "agent-harness-kit").resolve()
FORBIDDEN_REPO_ARTIFACTS = (
    "AGENTS.md",
    "CLAUDE.md",
    ".claude",
    ".opencode",
    "opencode.json",
)
EXPECTED_AHK_TOOLS = {
    "tasks.get",
    "tasks.claim",
    "tasks.update",
    "tasks.add",
    "tasks.acceptance.update",
    "actions.start",
    "actions.write",
    "actions.complete",
    "actions.get",
    "actions.record_file",
    "actions.record_tool",
    "docs.search",
}
EXPECTED_REQUIRED_FIELDS = {
    "tasks.add": {"title"},
    "tasks.claim": {"id", "agent"},
    "tasks.update": {"id", "status"},
    "actions.start": {"taskId", "agent"},
    "actions.write": {"actionId", "sectionType", "content"},
    "actions.complete": {"actionId", "summary"},
    "actions.record_tool": {"actionId", "toolName"},
    "actions.record_file": {"actionId", "filePath", "operation"},
    "docs.search": {"query"},
}


class AhkIntegrationTest(unittest.TestCase):
    def test_workspace_registers_ahk_mcp_server(self) -> None:
        mcp_config_path = REPO_ROOT / ".vscode" / "mcp.json"
        self.assertTrue(mcp_config_path.exists(), ".vscode/mcp.json must exist")

        mcp_config = json.loads(mcp_config_path.read_text(encoding="utf-8"))
        self.assertIn("ahk", mcp_config.get("servers", {}), "AHK MCP server must be registered")

        ahk_server = mcp_config["servers"]["ahk"]
        self.assertEqual(ahk_server["type"], "stdio")
        self.assertEqual(ahk_server["command"], "npx")
        self.assertEqual(ahk_server["args"], ["--no-install", "ahk", "serve"])

    def test_repo_health_gate_passes(self) -> None:
        result = subprocess.run(
            ["bash", "health.sh"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(
            result.returncode,
            0,
            msg=(result.stdout + "\n" + result.stderr).strip(),
        )
        self._assert_forbidden_repo_artifacts_absent()

    def test_ahk_cli_status_and_sync_pass(self) -> None:
        for command in (
            ["npx", "--no-install", "ahk", "sync", "--direction", "in"],
            ["npx", "--no-install", "ahk", "status"],
        ):
            result = subprocess.run(
                command,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                result.returncode,
                0,
                msg=(result.stdout + "\n" + result.stderr).strip(),
            )

        self._assert_forbidden_repo_artifacts_absent()

    def test_ahk_server_exposes_expected_tools(self) -> None:
        tool_manifest = anyio.run(self._get_ahk_tool_manifest, REPO_ROOT)
        tool_names = set(tool_manifest)
        self.assertTrue(
            EXPECTED_AHK_TOOLS.issubset(tool_names),
            msg=f"Missing expected AHK tools: {sorted(EXPECTED_AHK_TOOLS - tool_names)}",
        )
        self._assert_forbidden_repo_artifacts_absent()

    def test_ahk_tool_schemas_cover_core_lifecycle(self) -> None:
        tool_manifest = anyio.run(self._get_ahk_tool_manifest, REPO_ROOT)

        for tool_name, required_fields in EXPECTED_REQUIRED_FIELDS.items():
            self.assertIn(tool_name, tool_manifest)
            schema = tool_manifest[tool_name]
            self.assertEqual(
                set(schema.get("required", [])),
                required_fields,
                msg=f"Unexpected required fields for {tool_name}",
            )

        self._assert_forbidden_repo_artifacts_absent()

    def test_ahk_end_to_end_workspace_tools(self) -> None:
        result = anyio.run(self._exercise_workspace_tools)

        self.assertTrue(result["tasks"], "Expected at least one pending AHK task")
        self.assertTrue(
            all(task["status"] == "pending" for task in result["tasks"]),
            "Expected pending task results from tasks.get",
        )
        self.assertTrue(
            result["docs"],
            "Expected docs.search to return matching documentation rows",
        )
        self.assertTrue(
            any(entry["file"] in {"PLAN.md", "README.md"} for entry in result["docs"]),
            "Expected docs.search to return PLAN.md or README.md",
        )
        self._assert_forbidden_repo_artifacts_absent()

    def test_ahk_isolated_task_lifecycle_persists_sections_and_fallback(self) -> None:
        with tempfile.TemporaryDirectory(prefix=".tmp-ahk-") as temp_dir:
            sandbox_root = Path(temp_dir)
            self._write_sandbox_workspace(sandbox_root)
            result = anyio.run(self._exercise_isolated_workspace, sandbox_root)

        self.assertEqual(result["added"]["status"], "pending")
        self.assertEqual(result["claimed"]["status"], "in_progress")
        self.assertEqual(result["started"]["status"], "in_progress")
        self.assertEqual(result["completed"]["status"], "completed")
        self.assertEqual(result["updated"]["status"], "done")
        self.assertTrue(result["history"], "Expected at least one recorded action")
        sections = result["history"][0]["sections"]
        section_types = {section["section_type"] for section in sections}
        self.assertEqual(section_types, {"result", "next_steps"})
        self.assertIn("Lifecycle exercised.", {section["content"] for section in sections})
        self.assertTrue(any(entry["file"] == "guide.md" for entry in result["docs"]))
        self.assertIn("No tasks in progress", result["current_md"])
        self.assertTrue(result["db_exists"], "Expected the sandbox SQLite DB to exist")
        self._assert_forbidden_repo_artifacts_absent()

    def _assert_forbidden_repo_artifacts_absent(self) -> None:
        forbidden_paths = [path for path in FORBIDDEN_REPO_ARTIFACTS if (REPO_ROOT / path).exists()]
        self.assertEqual(forbidden_paths, [], msg=f"Unexpected provider artifacts in repo root: {forbidden_paths}")
        leaked_temp_paths = sorted(path.name for path in REPO_ROOT.glob(".tmp-*"))
        self.assertEqual(leaked_temp_paths, [], msg=f"Unexpected repo-root temp artifacts: {leaked_temp_paths}")

    async def _get_ahk_tool_manifest(self, cwd: Path) -> dict[str, dict[str, object]]:
        server_parameters = StdioServerParameters(
            command="npx",
            args=["--no-install", "ahk", "serve"],
            cwd=cwd,
        )

        async with stdio_client(server_parameters) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools_result = await session.list_tools()

        return {tool.name: tool.inputSchema for tool in tools_result.tools}

    async def _exercise_workspace_tools(self) -> dict[str, list[dict[str, object]]]:
        server_parameters = StdioServerParameters(
            command="npx",
            args=["--no-install", "ahk", "serve"],
            cwd=REPO_ROOT,
        )

        async with stdio_client(server_parameters) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tasks_result = await session.call_tool("tasks.get", {"status": "pending"})
                docs_result = await session.call_tool("docs.search", {"query": "Graphify"})

        self.assertFalse(tasks_result.isError)
        self.assertFalse(docs_result.isError)

        tasks = json.loads(tasks_result.content[0].text)
        docs = json.loads(docs_result.content[0].text)
        return {"tasks": tasks, "docs": docs}

    async def _exercise_isolated_workspace(self, sandbox_root: Path) -> dict[str, object]:
        self.assertTrue(AHK_BIN.exists(), f"Expected AHK binary at {AHK_BIN}")
        server_parameters = StdioServerParameters(
            command=str(AHK_BIN.resolve()),
            args=["serve"],
            cwd=sandbox_root,
        )

        async with stdio_client(server_parameters) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                added_result = await session.call_tool(
                    "tasks.add",
                    {
                        "title": "Generated Task",
                        "slug": "generated-task",
                        "description": "Exercise the AHK task lifecycle.",
                        "acceptance": ["claimable", "recordable"],
                    },
                )
                self.assertFalse(added_result.isError)
                added = json.loads(added_result.content[0].text)
                task_id = added["id"]

                claimed_result = await session.call_tool(
                    "tasks.claim",
                    {"id": task_id, "agent": "builder"},
                )
                started_result = await session.call_tool(
                    "actions.start",
                    {"taskId": task_id, "agent": "builder"},
                )
                self.assertFalse(claimed_result.isError)
                self.assertFalse(started_result.isError)

                claimed = json.loads(claimed_result.content[0].text)
                started = json.loads(started_result.content[0].text)
                action_id = started["actionId"]

                record_tool_result = await session.call_tool(
                    "actions.record_tool",
                    {
                        "actionId": action_id,
                        "toolName": "Read",
                        "argsJson": json.dumps({"path": "guide.md"}),
                        "resultSummary": "Read sandbox guide.",
                    },
                )
                record_file_result = await session.call_tool(
                    "actions.record_file",
                    {
                        "actionId": action_id,
                        "filePath": "docs/guide.md",
                        "operation": "read",
                        "notes": "Validated docs search target.",
                    },
                )
                result_section = await session.call_tool(
                    "actions.write",
                    {
                        "actionId": action_id,
                        "sectionType": "result",
                        "content": "Lifecycle exercised.",
                    },
                )
                next_steps_section = await session.call_tool(
                    "actions.write",
                    {
                        "actionId": action_id,
                        "sectionType": "next_steps",
                        "content": "No further action.",
                    },
                )
                history_result = await session.call_tool("actions.get", {"taskId": task_id})
                completed_result = await session.call_tool(
                    "actions.complete",
                    {"actionId": action_id, "summary": "Completed lifecycle."},
                )
                updated_result = await session.call_tool(
                    "tasks.update",
                    {"id": task_id, "status": "done"},
                )
                docs_result = await session.call_tool("docs.search", {"query": "Graphify"})

        for result in (
            record_tool_result,
            record_file_result,
            result_section,
            next_steps_section,
            history_result,
            completed_result,
            updated_result,
            docs_result,
        ):
            self.assertFalse(result.isError)

        current_md = (sandbox_root / ".harness" / "current.md").read_text(encoding="utf-8")
        return {
            "added": added,
            "claimed": claimed,
            "started": started,
            "history": json.loads(history_result.content[0].text),
            "completed": json.loads(completed_result.content[0].text),
            "updated": json.loads(updated_result.content[0].text),
            "docs": json.loads(docs_result.content[0].text),
            "current_md": current_md,
            "db_exists": (sandbox_root / ".harness" / "harness.db").exists(),
        }

    def _write_sandbox_workspace(self, sandbox_root: Path) -> None:
        (sandbox_root / ".harness").mkdir(parents=True, exist_ok=True)
        (sandbox_root / "docs").mkdir(parents=True, exist_ok=True)
        (sandbox_root / "agent-harness-kit.config.ts").write_text(
                        textwrap.dedent(
                                """
                                import { defineHarness } from '__AHK_PACKAGE__';

                                export default defineHarness({
                                    project: {
                                        name: 'ahk-test-workspace',
                                        description: 'Temporary AHK stability sandbox.',
                                        docsPath: './docs',
                                    },
                                    provider: 'claude-code',
                                    agents: {
                                        lead: { instructionsPath: null, context: 'Lead' },
                                        explorer: { instructionsPath: null, context: 'Explorer' },
                                        builder: { instructionsPath: null, context: 'Builder' },
                                        reviewer: { instructionsPath: null, context: 'Reviewer' },
                                        custom: [],
                                    },
                                    storage: {
                                        dir: '.harness',
                                        tasks: { adapter: 'local' },
                                        sections: {
                                            toolsUsed: true,
                                            filesModified: true,
                                            result: true,
                                            blockers: true,
                                            nextSteps: true,
                                        },
                                        markdownFallback: {
                                            enabled: true,
                                            path: '.harness/current.md',
                                        },
                                    },
                                    database: {
                                        type: 'sqlite',
                                        path: '.harness/harness.db',
                                    },
                                    health: {
                                        required: false,
                                    },
                                    tools: {
                                        mcp: {
                                            enabled: true,
                                            port: 3742,
                                        },
                                        scripts: {
                                            enabled: false,
                                            outputDir: './.harness/scripts',
                                        },
                                    },
                                });
                                """
                        ).replace("__AHK_PACKAGE__", AHK_PACKAGE.as_posix()).strip()
            + "\n",
            encoding="utf-8",
        )
        (sandbox_root / ".harness" / "feature_list.json").write_text(
            json.dumps(
                [
                    {
                        "slug": "seed-task",
                        "title": "Seed Task",
                        "description": "Seeded pending task.",
                        "acceptance": ["seeded"],
                    }
                ],
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (sandbox_root / "docs" / "guide.md").write_text(
            "# Sandbox Guide\n\nGraphify and AHK are both documented here.\n",
            encoding="utf-8",
        )