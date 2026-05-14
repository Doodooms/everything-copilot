import json
import sys
from pathlib import Path

import anyio
from mcp import ClientSession, StdioServerParameters, stdio_client

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import atomic_index


SCRIPT_PATH = REPO_ROOT / "scripts" / "atomic_index.py"
MIN_GRAPH_JSON = {
    "directed": False,
    "multigraph": False,
    "graph": {"hyperedges": []},
    "nodes": [],
    "links": [],
}


def test_search_docs_tracks_patch_and_delete_lifecycle(tmp_path: Path) -> None:
    sandbox_root = tmp_path
    guide_path = sandbox_root / "guide.md"
    graph_json_path = sandbox_root / "graphify-out" / "graph.json"
    db_path = sandbox_root / ".graphify" / "lbug"

    guide_path.write_text("# Guide\n\nalpha-token appears here.\n", encoding="utf-8")
    graph_json_path.parent.mkdir(parents=True, exist_ok=True)
    graph_json_path.write_text(json.dumps(MIN_GRAPH_JSON), encoding="utf-8")

    atomic_index.migrate_graphify_impl(
        root=sandbox_root,
        graph_json_path=graph_json_path,
        db_path=db_path,
        force=False,
    )

    initial_results = atomic_index.search_docs_impl(sandbox_root, "alpha-token", limit=5)
    assert len(initial_results) == 1
    assert initial_results[0]["path"] == "guide.md"
    assert "alpha-token" in initial_results[0]["snippet"].lower()

    guide_path.write_text("# Guide\n\nbeta-token replaces the earlier text.\n", encoding="utf-8")
    atomic_index.patch_graphify_impl(
        root=sandbox_root,
        file_path=guide_path,
        db_path=db_path,
        graph_json_path=graph_json_path,
        deleted=False,
    )

    assert atomic_index.search_docs_impl(sandbox_root, "alpha-token", limit=5) == []
    updated_results = atomic_index.search_docs_impl(sandbox_root, "beta-token", limit=5)
    assert len(updated_results) == 1
    assert updated_results[0]["path"] == "guide.md"

    guide_path.unlink()
    atomic_index.patch_graphify_impl(
        root=sandbox_root,
        file_path=guide_path,
        db_path=db_path,
        graph_json_path=graph_json_path,
        deleted=True,
    )

    assert atomic_index.search_docs_impl(sandbox_root, "beta-token", limit=5) == []


def test_graphify_server_exposes_search_docs_tool(tmp_path: Path) -> None:
    sandbox_root = tmp_path
    guide_path = sandbox_root / "guide.md"
    graph_json_path = sandbox_root / "graphify-out" / "graph.json"
    report_path = sandbox_root / "graphify-out" / "GRAPH_REPORT.md"
    db_path = sandbox_root / ".graphify" / "lbug"

    guide_path.write_text("# Guide\n\nworkspace retrieval relies on search docs.\n", encoding="utf-8")
    graph_json_path.parent.mkdir(parents=True, exist_ok=True)
    graph_json_path.write_text(json.dumps(MIN_GRAPH_JSON), encoding="utf-8")
    report_path.write_text("# Report\n", encoding="utf-8")

    atomic_index.migrate_graphify_impl(
        root=sandbox_root,
        graph_json_path=graph_json_path,
        db_path=db_path,
        force=False,
    )

    result = anyio.run(_call_graphify_search_docs, sandbox_root, db_path, report_path)

    assert "search_docs" in result["tools"]
    assert "guide.md" in result["response"]
    assert "workspace" in result["response"].lower()


async def _call_graphify_search_docs(
    sandbox_root: Path,
    db_path: Path,
    report_path: Path,
) -> dict[str, object]:
    server_parameters = StdioServerParameters(
        command=sys.executable,
        args=[
            str(SCRIPT_PATH),
            "serve-graphify",
            "--db-path",
            str(db_path),
            "--report-path",
            str(report_path),
        ],
        cwd=sandbox_root,
    )

    async with stdio_client(server_parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            search_result = await session.call_tool(
                "search_docs",
                {"query": "workspace retrieval", "limit": 5},
            )

    assert not search_result.isError
    return {
        "tools": {tool.name for tool in tools_result.tools},
        "response": search_result.content[0].text,
    }