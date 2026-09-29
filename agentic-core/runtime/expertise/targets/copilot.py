from __future__ import annotations

from pathlib import Path, PurePosixPath

from ..agent_validation import validate_agent_semantics
from ..errors import TargetError
from ..ir import PackSource
from .common import CompiledTarget, ensure_supported_agent_plugins
from .portable import (
    _compile_portable_core,
    _read_source_snapshot,
)

_COPILOT_TOOLS = frozenset(
    {
        "agent",
        "browser",
        "execute",
        "edit",
        "read",
        "search",
        "search/codebase",
        "search/usages",
        "skill",
        "todo",
        "vscode/askQuestions",
        "web",
        "mcp_github_mcp_se_get_commit",
        "mcp_github_mcp_se_get_file_contents",
        "mcp_github_mcp_se_issue_read",
        "mcp_github_mcp_se_list_commits",
        "mcp_github_mcp_se_list_releases",
        "mcp_github_mcp_se_pull_request_read",
        "mcp_github_mcp_se_search_code",
        "mcp_github_mcp_se_search_issues",
        "mcp_github_mcp_se_search_pull_requests",
        "mcp_github_mcp_se_search_repositories",
        "mcp_context7_query_docs",
        "mcp_context7_resolve_library_id",
        "mcp_semgrep_get_abstract_syntax_tree",
        "mcp_semgrep_get_supported_languages",
        "mcp_semgrep_semgrep_scan",
        "mcp_semgrep_semgrep_scan_with_custom_rule",
        "context7/query-docs",
        "context7/resolve-library-id",
        "github-mcp-server/get_commit",
        "github-mcp-server/get_file_contents",
        "github-mcp-server/issue_read",
        "github-mcp-server/list_commits",
        "github-mcp-server/list_releases",
        "github-mcp-server/pull_request_read",
        "github-mcp-server/search_code",
        "github-mcp-server/search_issues",
        "github-mcp-server/search_pull_requests",
        "github-mcp-server/search_repositories",
    }
)


def _validate_copilot_fields(
    metadata: dict[str, object],
    agent_id: str,
    source: PackSource | None,
    *,
    known_agents: frozenset[str] = frozenset(),
    canonical_orchestrator: bool = False,
) -> None:
    if metadata.get("target") != "vscode":
        raise TargetError(f"Copilot agent target must be vscode: {agent_id}")
    if "infer" in metadata:
        raise TargetError(f"Copilot agent uses deprecated infer metadata: {agent_id}")
    tools = metadata.get("tools", [])
    if not isinstance(tools, list) or any(not isinstance(tool, str) for tool in tools):
        raise TargetError(f"Copilot agent tools must be a list of strings: {agent_id}")
    projected = {
        tool
        for projection in (source.ir.projections if source else ())
        if projection.agent_id == agent_id
        for server in (source.ir.mcp_servers if source else ())
        if server.id in projection.mcp_servers
        for tool in server.tools
    }
    allowed_tools = _COPILOT_TOOLS | ({"github/*"} if canonical_orchestrator else set())
    unsupported = sorted(set(tools) - allowed_tools - projected)
    if unsupported:
        raise TargetError(
            f"Copilot agent declares unsupported tools for {agent_id}: {', '.join(unsupported)}"
        )
    agents = metadata.get("agents")
    if agents is not None:
        if not isinstance(agents, list) or any(
            not isinstance(agent, str) for agent in agents
        ):
            raise TargetError(
                f"Copilot agent recipients must be a list of strings: {agent_id}"
            )
        catalog = known_agents | (
            source.known_agents | {item.id for item in source.ir.agents.contributions}
            if source
            else frozenset()
        )
        unknown = sorted(set(agents) - catalog)
        if "*" in agents or agent_id in agents or unknown:
            raise TargetError(
                f"Copilot agent recipients are not in the agent catalog: {agent_id}"
            )


def _validate_agent(
    content: bytes, agent_path: Path, known_agents: frozenset[str]
) -> None:
    """Compatibility bridge for the controller's existing Core agent validation call."""
    agent_id = agent_path.name.removesuffix(".agent.md")
    parsed = validate_agent_semantics(content, agent_id, agent_path.name)
    _validate_copilot_fields(
        parsed.metadata,
        agent_id,
        None,
        known_agents=known_agents,
        canonical_orchestrator=agent_id == "orchestrator",
    )


def _validate_routing_file_refs(body: str, source_path: str, source_root: Path) -> None:
    uses_routing_refs = (
        "#file:./references/USEFOR.md" in body
        or "#file:./references/DONOTUSEFOR.md" in body
    )
    if not uses_routing_refs:
        return
    parent = PurePosixPath(source_path).parent
    if parent.name == "agents":
        raise TargetError(
            "Copilot agent routing-file references require a per-agent package directory"
        )
    root = source_root.resolve(strict=True)
    required = (
        parent / "references/USEFOR.md",
        parent / "references/DONOTUSEFOR.md",
    )
    for relative in required:
        candidate = root.joinpath(*relative.parts)
        current = root
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                raise TargetError(
                    f"Copilot agent routing reference must not use symlinks: {relative}"
                )
        try:
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(root)
        except (OSError, RuntimeError, ValueError) as exc:
            raise TargetError(
                f"Copilot agent routing reference is unavailable or outside the pack: {relative}"
            ) from exc
        if not resolved.is_file():
            raise TargetError(
                f"Copilot agent routing reference must be a regular file: {relative}"
            )


def compile_copilot(source: PackSource) -> CompiledTarget:
    if "copilot" not in source.ir.compatibility.targets:
        raise TargetError(f"pack {source.ir.id!r} does not support the Copilot target")

    ensure_supported_agent_plugins(source)
    source_snapshot = _read_source_snapshot(source)
    files = _compile_portable_core(source, source_snapshot).file_map()
    for contribution in source.ir.agents.contributions:
        try:
            agent_content = source_snapshot[contribution.source]
        except KeyError as exc:
            raise TargetError(
                f"agent source is absent from the validated snapshot: {contribution.source}"
            ) from exc
        parsed = validate_agent_semantics(
            agent_content, contribution.id, contribution.source
        )
        _validate_copilot_fields(parsed.metadata, contribution.id, source)
        _validate_routing_file_refs(parsed.body, contribution.source, source.root)
        target_path = f"com.github.copilot/agents/{contribution.id}.agent.md"
        if target_path in files:
            raise TargetError(f"duplicate Copilot output path: {target_path}")
        files[target_path] = agent_content

    return CompiledTarget.create(
        "copilot",
        source.ir.reference,
        files,
        source_digest=source.ir.content_digest,
    )
