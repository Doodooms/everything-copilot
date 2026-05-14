import json
import subprocess
import textwrap
from pathlib import Path

import anyio
from mcp import ClientSession, StdioServerParameters, stdio_client


REPO_ROOT = Path(__file__).resolve().parents[1]
AHK_PACKAGE = (REPO_ROOT / "node_modules" / "@cardor" / "agent-harness-kit").resolve()
AHK_CLI_ENTRY_PATH = (AHK_PACKAGE / "bin" / "ahk.js").resolve()
AHK_CLI_ENTRY_URI = AHK_CLI_ENTRY_PATH.as_uri()
QUIET_AHK_SERVE_SCRIPT = textwrap.dedent(
    f"""
    globalThis.fetch = async () => {{
        throw new Error('disable update checks during MCP tests');
    }};
    process.argv = ['node', 'serve'];
    await import({json.dumps(AHK_CLI_ENTRY_URI)});
    """
).strip()
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


def test_workspace_registers_ahk_mcp_server() -> None:
    mcp_config_path = REPO_ROOT / ".vscode" / "mcp.json"
    assert mcp_config_path.exists(), ".vscode/mcp.json must exist"

    mcp_config = json.loads(mcp_config_path.read_text(encoding="utf-8"))
    assert "ahk" in mcp_config.get("servers", {}), "AHK MCP server must be registered"

    ahk_server = mcp_config["servers"]["ahk"]
    assert ahk_server["type"] == "stdio"
    assert ahk_server["command"] == "npx"
    assert ahk_server["args"] == ["--no-install", "ahk", "serve"]


def test_repo_health_gate_passes() -> None:
    result = subprocess.run(
        ["bash", "health.sh"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (result.stdout + "\n" + result.stderr).strip()
    _assert_forbidden_repo_artifacts_absent()


def test_ahk_cli_status_and_sync_pass() -> None:
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
        assert result.returncode == 0, (result.stdout + "\n" + result.stderr).strip()

    _assert_forbidden_repo_artifacts_absent()


def test_ahk_server_exposes_expected_tools() -> None:
    tool_manifest = anyio.run(_get_ahk_tool_manifest, REPO_ROOT)
    tool_names = set(tool_manifest)

    assert EXPECTED_AHK_TOOLS.issubset(tool_names), (
        f"Missing expected AHK tools: {sorted(EXPECTED_AHK_TOOLS - tool_names)}"
    )
    _assert_forbidden_repo_artifacts_absent()


def test_ahk_tool_schemas_cover_core_lifecycle() -> None:
    tool_manifest = anyio.run(_get_ahk_tool_manifest, REPO_ROOT)

    for tool_name, required_fields in EXPECTED_REQUIRED_FIELDS.items():
        assert tool_name in tool_manifest
        schema = tool_manifest[tool_name]
        assert set(schema.get("required", [])) == required_fields, (
            f"Unexpected required fields for {tool_name}"
        )

    _assert_forbidden_repo_artifacts_absent()


def test_ahk_end_to_end_workspace_tools() -> None:
    result = anyio.run(_exercise_workspace_tools)

    assert result["tasks"], "Expected at least one pending AHK task"
    assert all(task["status"] == "pending" for task in result["tasks"]), (
        "Expected pending task results from tasks.get"
    )
    assert result["docs"], "Expected docs.search to return matching documentation rows"
    assert any(entry["file"] in {"PLAN.md", "README.md"} for entry in result["docs"]), (
        "Expected docs.search to return PLAN.md or README.md"
    )
    _assert_forbidden_repo_artifacts_absent()


def test_ahk_isolated_task_lifecycle_persists_sections_and_fallback(tmp_path: Path) -> None:
    sandbox_root = tmp_path
    _write_sandbox_workspace(sandbox_root)
    result = anyio.run(_exercise_isolated_workspace, sandbox_root)

    assert result["added"]["status"] == "pending"
    assert result["claimed"]["status"] == "in_progress"
    assert result["started"]["status"] == "in_progress"
    assert result["completed"]["status"] == "completed"
    assert result["updated"]["status"] == "done"
    assert result["history"], "Expected at least one recorded action"
    sections = result["history"][0]["sections"]
    section_types = {section["section_type"] for section in sections}
    assert section_types == {"result", "next_steps"}
    assert "Lifecycle exercised." in {section["content"] for section in sections}
    assert any(entry["file"] == "guide.md" for entry in result["docs"])
    assert "No tasks in progress" in result["current_md"]
    assert result["db_exists"], "Expected the sandbox SQLite DB to exist"
    _assert_forbidden_repo_artifacts_absent()


def _assert_forbidden_repo_artifacts_absent() -> None:
    forbidden_paths = [
        path for path in FORBIDDEN_REPO_ARTIFACTS if (REPO_ROOT / path).exists()
    ]
    assert forbidden_paths == [], f"Unexpected provider artifacts in repo root: {forbidden_paths}"
    leaked_temp_paths = sorted(path.name for path in REPO_ROOT.glob(".tmp-*"))
    assert leaked_temp_paths == [], f"Unexpected repo-root temp artifacts: {leaked_temp_paths}"


async def _get_ahk_tool_manifest(cwd: Path) -> dict[str, dict[str, object]]:
    server_parameters = _ahk_stdio_server_parameters(cwd)

    async with stdio_client(server_parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools_result = await session.list_tools()

    return {tool.name: tool.inputSchema for tool in tools_result.tools}


async def _exercise_workspace_tools() -> dict[str, list[dict[str, object]]]:
    server_parameters = _ahk_stdio_server_parameters(REPO_ROOT)

    async with stdio_client(server_parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tasks_result = await session.call_tool("tasks.get", {"status": "pending"})
            docs_result = await session.call_tool("docs.search", {"query": "Graphify"})

    assert not tasks_result.isError
    assert not docs_result.isError

    tasks = json.loads(tasks_result.content[0].text)
    docs = json.loads(docs_result.content[0].text)
    return {"tasks": tasks, "docs": docs}


async def _exercise_isolated_workspace(sandbox_root: Path) -> dict[str, object]:
    server_parameters = _ahk_stdio_server_parameters(sandbox_root)

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
            assert not added_result.isError
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
            assert not claimed_result.isError
            assert not started_result.isError

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
        assert not result.isError

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


def _write_sandbox_workspace(sandbox_root: Path) -> None:
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


def _ahk_stdio_server_parameters(cwd: Path) -> StdioServerParameters:
    return StdioServerParameters(
        command="node",
        args=["--input-type=module", "-e", QUIET_AHK_SERVE_SCRIPT],
        cwd=cwd,
    )