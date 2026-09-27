from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)
STEP_HEADING_PATTERN = re.compile(r"^##\s+Step\s+(\d+)\b", re.IGNORECASE)
PACK_MCP_TOOL_PATTERN = re.compile(
    r"(?P<server>[a-z][a-z0-9]*(?:-[a-z0-9]+)*)/"
    r"(?P<tool>[^/\s]+)"
)
FORBIDDEN_MCP_SERVERS = {"capabilityd", "workflowd"}
VALID_AGENT_TOOLS = {
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
}
VALID_READ_ONLY_MCP_TOOLS = {
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
    "semgrep/get_abstract_syntax_tree",
    "semgrep/get_supported_languages",
    "semgrep/semgrep_scan",
    "semgrep/semgrep_scan_with_custom_rule",
}
WRONG_LAYER_TOOL_SUGGESTIONS = {
    "copilot_readFile": "read",
    "fetch_webpage": "web",
    "get_errors": "execute",
    "grep_search": "search",
    "read_file": "read",
    "runSubagent": "agent",
    "run_in_terminal": "execute",
    "semantic_search": "search/codebase",
    "send_to_terminal": "execute",
    "vscode_askQuestions": "vscode/askQuestions",
}
def _find_plugin_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (
            (parent / "plugin.json").is_file()
            and (parent / "skills").is_dir()
            and (parent / "com.github.copilot" / "agents").is_dir()
        ):
            return parent
    raise RuntimeError(
        "Could not locate the Agent Plugin root containing plugin.json, skills/, "
        "and com.github.copilot/agents/."
    )


PLUGIN_ROOT = _find_plugin_root()
CORE_AGENTS_DIR = PLUGIN_ROOT / "com.github.copilot" / "agents"
WORKSPACE_AGENTS_DIR = Path.cwd() / ".github" / "agents"
PACK_AGENTS_DIR = Path.cwd() / "expertise" / "packs"
AGENT_SOURCE_DIRS = (CORE_AGENTS_DIR, WORKSPACE_AGENTS_DIR)


@dataclass
class LintResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)

    def extend(self, other: "LintResult") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


def _print_result(result: LintResult) -> None:
    if result.errors:
        print("ERRORS:")
        for error in result.errors:
            print(f"  - {error}")
    if result.warnings:
        print("WARNINGS:")
        for warning in result.warnings:
            print(f"  - {warning}")


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    normalized = text.replace("\r\n", "\n").lstrip("\ufeff")
    match = FRONTMATTER_PATTERN.match(normalized)
    if not match:
        raise ValueError("Missing YAML frontmatter delimited by --- markers.")

    raw_frontmatter, body = match.groups()
    try:
        data = yaml.safe_load(raw_frontmatter) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Frontmatter is not valid YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("Frontmatter must parse to a YAML mapping.")

    return data, body.strip()


def _projected_pack_mcp_tools(
    agent_file: Path | None, agent_id: str
) -> tuple[set[str], str | None]:
    if agent_file is None:
        return set(), None

    try:
        parents = agent_file.resolve().parents
    except OSError:
        return set(), None

    pack_manifest = next(
        (
            parent / "pack.yaml"
            for parent in parents
            if (parent / "pack.yaml").is_file()
        ),
        None,
    )
    if pack_manifest is None:
        return set(), None
    if pack_manifest.is_symlink() or not pack_manifest.is_file():
        return set(), f"pack manifest is not a regular file: {pack_manifest}"

    try:
        manifest = yaml.safe_load(pack_manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        return set(), f"could not read pack manifest {pack_manifest}: {exc}"
    if not isinstance(manifest, dict):
        return set(), f"pack manifest must be a mapping: {pack_manifest}"

    raw_servers = manifest.get("mcp_servers")
    raw_projections = manifest.get("projections")
    if not isinstance(raw_servers, list) or not isinstance(raw_projections, list):
        return set(), "pack manifest must declare MCP servers and agent projections as lists"

    declared_tools: dict[str, set[str]] = {}
    for index, server in enumerate(raw_servers):
        if not isinstance(server, dict) or not isinstance(server.get("id"), str):
            return set(), f"mcp_servers[{index}] must declare a string `id`"
        server_id = server["id"]
        tool_names = server.get("tools", [])
        if not isinstance(tool_names, list) or any(
            not isinstance(tool_name, str)
            or not tool_name
            or "/" in tool_name
            or any(character.isspace() for character in tool_name)
            for tool_name in tool_names
        ):
            return set(), f"mcp_servers[{index}].tools must list exact MCP tool names"
        declared_tools[server_id] = set(tool_names)

    projected_servers: set[str] = set()
    for index, projection in enumerate(raw_projections):
        if not isinstance(projection, dict):
            return set(), f"projections[{index}] must be a mapping"
        if projection.get("agent_id") != agent_id:
            continue
        server_ids = projection.get("mcp_servers", [])
        if not isinstance(server_ids, list) or any(
            not isinstance(server_id, str) for server_id in server_ids
        ):
            return set(), f"projections[{index}].mcp_servers must be a list of server IDs"
        projected_servers.update(server_ids)

    unknown_servers = projected_servers - set(declared_tools)
    if unknown_servers:
        return set(), (
            "projection references undeclared MCP server(s): "
            + ", ".join(sorted(unknown_servers))
        )

    return {
        f"{server_id}/{tool_name}"
        for server_id in projected_servers
        for tool_name in declared_tools[server_id]
    }, None


def lint_agent_frontmatter(
    frontmatter: dict[str, Any], agent_file: Path | None = None
) -> LintResult:
    result = LintResult()

    name = frontmatter.get("name")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        result.errors.append("`name` must be a lowercase hyphenated agent slug.")

    if frontmatter.get("target") != "vscode":
        result.errors.append("Workspace agents must set `target: vscode`.")

    if "infer" in frontmatter:
        result.errors.append("`infer` is deprecated; use `user-invocable` and `disable-model-invocation`.")

    description = frontmatter.get("description")
    if isinstance(description, str) and description.strip():
        lowered_description = description.lower()
        for clause in ("what:", "invoke for:", "do not invoke for:"):
            if clause not in lowered_description:
                result.errors.append(
                    f"`description` must include `{clause[:-1].upper()}:` for description-first routing."
                )
    else:
        result.errors.append(
            "`description` is required and must include WHAT:, INVOKE FOR:, and DO NOT INVOKE FOR:."
        )

    tools = frontmatter.get("tools")
    if tools is not None and not isinstance(tools, list):
        result.errors.append("`tools` must be a YAML list of strings when present.")
        return result
    if isinstance(tools, list) and any(not isinstance(tool, str) for tool in tools):
        result.errors.append("`tools` must be a YAML list of strings when present.")
        return result

    tool_names = [tool for tool in tools or [] if isinstance(tool, str)]
    projected_pack_mcp_tools: set[str] | None = None
    for tool_name in tool_names:
        if tool_name in VALID_AGENT_TOOLS or tool_name in VALID_READ_ONLY_MCP_TOOLS:
            continue
        if tool_name == "github/*":
            canonical_orchestrator = (
                frontmatter.get("name") == "orchestrator"
                and agent_file.resolve()
                == (CORE_AGENTS_DIR / "orchestrator.agent.md").resolve()
            )
            if canonical_orchestrator:
                continue
            result.errors.append(
                "`github/*` is reserved for the canonical Orchestrator."
            )
            continue
        mcp_tool = PACK_MCP_TOOL_PATTERN.fullmatch(tool_name)
        if mcp_tool is not None:
            server_id = mcp_tool.group("server")
            if server_id in FORBIDDEN_MCP_SERVERS:
                result.errors.append(
                    f"Pack MCP tool `{tool_name}` uses a forbidden internal server."
                )
                continue
            if projected_pack_mcp_tools is None:
                projected_pack_mcp_tools, catalog_error = _projected_pack_mcp_tools(
                    agent_file, str(frontmatter.get("name", ""))
                )
                if catalog_error is not None:
                    result.errors.append(
                        f"Cannot validate pack MCP tools: {catalog_error}."
                    )
                    continue
            if tool_name in projected_pack_mcp_tools:
                continue
            result.errors.append(
                f"Pack MCP tool `{tool_name}` is not in this agent's exact projected `mcp_servers[].tools` catalog."
            )
            continue
        suggestion = WRONG_LAYER_TOOL_SUGGESTIONS.get(tool_name)
        if suggestion:
            result.errors.append(
                f"Tool `{tool_name}` is not recognized by the workspace tool catalog. Wrong-layer raw tool name detected; use `{suggestion}` instead."
            )
        else:
            result.errors.append(
                f"Tool `{tool_name}` is not recognized by the workspace tool catalog for agents."
            )

    allowed_agents = frontmatter.get("agents")
    if allowed_agents is not None and not isinstance(allowed_agents, list):
        result.errors.append("`agents` must be a YAML list of strings when present.")
        return result
    if isinstance(allowed_agents, list) and any(
        not isinstance(agent_name, str) for agent_name in allowed_agents
    ):
        result.errors.append("`agents` must be a YAML list of strings when present.")
        return result

    if allowed_agents is not None and "agent" not in tool_names:
        result.errors.append(
            "Frontmatter declares `agents:` but omits the `agent` tool."
        )

    if "agent" in tool_names and not allowed_agents:
        result.warnings.append(
            "Tool `agent` is broad without an `agents:` allowlist; declare an `agents:` allowlist or remove the tool."
        )

    if isinstance(allowed_agents, list):
        known_agents = _workspace_agent_names()
        for agent_name in allowed_agents:
            if agent_name == "*":
                result.errors.append(
                    "Frontmatter `agents:` must list explicit recipients; wildcard `*` is not allowed."
                )
                continue
            if agent_name == frontmatter.get("name"):
                result.errors.append(
                    f"Frontmatter `agents:` must not list itself (`{agent_name}`)."
                )
                continue
            if agent_name not in known_agents:
                result.errors.append(
                    f"Frontmatter `agents:` lists unknown agent `{agent_name}`."
                )

    return result


def _workspace_agent_names() -> set[str]:
    names = set()
    for agents_dir in (*AGENT_SOURCE_DIRS, PACK_AGENTS_DIR):
        if not agents_dir.exists():
            continue
        for candidate in agents_dir.rglob("*.agent.md"):
            name = candidate.name
            if name.endswith(".agent.md"):
                names.add(name[: -len(".agent.md")])
    return names


def _has_definition_bullet(body: str) -> bool:
    definitions_match = re.search(
        r"<definitions>(.*?)</definitions>", body, re.DOTALL | re.IGNORECASE
    )
    if not definitions_match:
        return False

    return bool(
        re.search(
            r"^\s*-\s+\*\*[^*]+\*\*\s*:\s+\S+",
            definitions_match.group(1),
            re.MULTILINE,
        )
    )


def _has_agent_admission_matrix(body: str) -> bool:
    lines = body.splitlines()
    for index, line in enumerate(lines):
        if re.match(r"^\s{0,3}#{1,6}\s+.*\badmission matrix\b", line, re.IGNORECASE):
            return True

        if "|" not in line:
            continue
        header_cells = [
            cell.strip().strip("`*_ ").upper()
            for cell in line.strip().strip("|").split("|")
        ]
        if not any("REQUEST SHAPE" in cell for cell in header_cells):
            continue
        if not any(re.fullmatch(r"INVOKE\??", cell) for cell in header_cells):
            continue

        has_yes = False
        has_no = False
        for row in lines[index + 1 :]:
            if "|" not in row:
                break
            cells = {
                cell.strip().strip("`*_ ").upper()
                for cell in row.strip().strip("|").split("|")
            }
            has_yes = has_yes or "YES" in cells
            has_no = has_no or "NO" in cells
            if has_yes and has_no:
                return True
    return False


def _has_agent_refusal_json(body: str) -> bool:
    return bool(
        re.search(
            r"\{[^{}]*[\"']status[\"']\s*:\s*[\"']refused[\"'][^{}]*\}",
            body,
            re.DOTALL | re.IGNORECASE,
        )
    )


def _has_agent_skills_entry(body: str) -> bool:
    match = re.search(
        r"<agent-skills>(.*?)</agent-skills>", body, re.DOTALL | re.IGNORECASE
    )
    if not match:
        return False
    return any(
        re.match(r"^\s*-\s+\S", line)
        for line in match.group(1).splitlines()
    )


def _normalize_agent_heading(text: str) -> str:
    return re.sub(r"[*_`]+", "", text).strip().upper()


def _has_embedded_routing_sections(stripped_lines: list[str]) -> bool:
    normalized_lines = {_normalize_agent_heading(line) for line in stripped_lines}
    return (
        "### INVOKE FOR" in normalized_lines
        and "### DO NOT INVOKE FOR" in normalized_lines
    ) or (
        "### USE FOR" in normalized_lines and "### DO NOT USE FOR" in normalized_lines
    )


def _uses_routing_file_refs(body: str) -> bool:
    return (
        "#file:./references/USEFOR.md" in body
        or "#file:./references/DONOTUSEFOR.md" in body
    )


def _looks_like_wrapped_agent(stripped_lines: list[str], body: str) -> bool:
    return (
        "## Role" in stripped_lines
        or "<workflow>" in stripped_lines
        or "<definitions>" in stripped_lines
        or "<rules>" in stripped_lines
    )


def _looks_like_canonical_wrapped_agent(stripped_lines: list[str]) -> bool:
    try:
        return (
            stripped_lines.index("<rules>")
            < stripped_lines.index("## Role")
            < stripped_lines.index("</rules>")
            < stripped_lines.index("<workflow>")
        )
    except ValueError:
        return False


def _validate_optional_wrapper(
    stripped_lines: list[str],
    *,
    tag: str,
    before_token: str,
    first_heading: str,
    last_heading: str,
    after_token: str | None,
    result: LintResult,
) -> None:
    open_tag = f"<{tag}>"
    close_tag = f"</{tag}>"
    has_open = open_tag in stripped_lines
    has_close = close_tag in stripped_lines

    if has_open != has_close:
        result.errors.append(
            f"Agent body must either omit `{open_tag}` entirely or use both `{open_tag}` and `{close_tag}` around the wrapped section."
        )
        return

    if not has_open:
        return

    try:
        before_index = stripped_lines.index(before_token)
        open_index = stripped_lines.index(open_tag)
        first_heading_index = stripped_lines.index(first_heading)
        last_heading_index = stripped_lines.index(last_heading)
        close_index = stripped_lines.index(close_tag)
    except ValueError:
        return

    if after_token is None:
        is_valid = open_index < first_heading_index < last_heading_index < close_index
    else:
        try:
            after_index = stripped_lines.index(after_token)
        except ValueError:
            return

        if first_heading_index == last_heading_index:
            is_valid = (
                before_index
                < open_index
                < first_heading_index
                < close_index
                < after_index
            )
        else:
            is_valid = (
                before_index
                < open_index
                < first_heading_index
                < last_heading_index
                < close_index
                < after_index
            )

    if not is_valid:
        heading_text = (
            first_heading
            if first_heading == last_heading
            else f"{first_heading} and {last_heading}"
        )
        result.errors.append(
            f"Agent body must keep `{open_tag}` and `{close_tag}` wrapped tightly around {heading_text}."
        )


def _validate_canonical_wrapped_agent_body(body: str, agent_file: Path) -> LintResult:
    result = LintResult()
    stripped_lines = [line.strip() for line in body.splitlines() if line.strip()]

    required_tags = (
        "<routing>",
        "</routing>",
        "<critical_rules>",
        "</critical_rules>",
        "<general_rules>",
        "</general_rules>",
        "<risk_assessment>",
        "</risk_assessment>",
        "<rules>",
        "</rules>",
        "<agent-skills>",
        "</agent-skills>",
        "<workflow>",
        "</workflow>",
    )
    tag_positions: dict[str, int] = {}
    for tag in required_tags:
        positions = [index for index, line in enumerate(stripped_lines) if line == tag]
        if len(positions) != 1:
            result.errors.append(
                f"Canonical wrapped agents must contain exactly one `{tag}` tag."
            )
            return result
        tag_positions[tag] = positions[0]

    definition_open_positions = [
        index for index, line in enumerate(stripped_lines) if line == "<definitions>"
    ]
    definition_close_positions = [
        index for index, line in enumerate(stripped_lines) if line == "</definitions>"
    ]
    if bool(definition_open_positions) != bool(definition_close_positions):
        result.errors.append(
            "Agent body must either omit `<definitions>` entirely or use both `<definitions>` and `</definitions>`."
        )
        return result
    if len(definition_open_positions) > 1 or len(definition_close_positions) > 1:
        result.errors.append("Canonical wrapped agents may contain only one definitions block.")
        return result

    rules_open = tag_positions["<rules>"]
    rules_close = tag_positions["</rules>"]
    routing_open = tag_positions["<routing>"]
    routing_close = tag_positions["</routing>"]
    critical_open = tag_positions["<critical_rules>"]
    critical_close = tag_positions["</critical_rules>"]
    general_open = tag_positions["<general_rules>"]
    general_close = tag_positions["</general_rules>"]
    risk_open = tag_positions["<risk_assessment>"]
    risk_close = tag_positions["</risk_assessment>"]
    skills_open = tag_positions["<agent-skills>"]
    skills_close = tag_positions["</agent-skills>"]
    workflow_open = tag_positions["<workflow>"]
    workflow_close = tag_positions["</workflow>"]
    if definition_open_positions:
        definitions_open = definition_open_positions[0]
        definitions_close = definition_close_positions[0]
        if not definitions_open < definitions_close < routing_open:
            result.errors.append(
                "When present, `<definitions>` must be non-empty and precede `<routing>`."
            )
            return result
        if not _has_definition_bullet(body):
            result.errors.append(
                "When present, `<definitions>` must contain at least one non-empty `- **term** : definition` bullet."
            )
            return result

    if not (
        routing_open
        < routing_close
        < critical_open
        < critical_close
        < general_open
        < general_close
        < risk_open
        < risk_close
        < rules_open
        < rules_close
        < skills_open
        < skills_close
        < workflow_open
        < workflow_close
    ):
        result.errors.append(
            "Canonical agents must order `<routing>`, `<critical_rules>`, `<general_rules>`, `<risk_assessment>`, `<rules>`, `<agent-skills>`, and `<workflow>` after optional `<definitions>`."
        )
        return result
    critical_lines = stripped_lines[critical_open + 1 : critical_close]
    general_lines = stripped_lines[general_open + 1 : general_close]
    risk_lines = stripped_lines[risk_open + 1 : risk_close]
    critical_text = "\n".join(critical_lines)
    general_text = "\n".join(general_lines)
    risk_text = "\n".join(risk_lines)
    if not any(re.match(r"^-\s+\S", line) for line in critical_lines) or not re.search(
        r"\bMUST(?:\s+NOT)?\b", critical_text
    ):
        result.errors.append(
            "`<critical_rules>` must contain at least one bulleted, non-negotiable MUST rule."
        )
        return result
    if not any(re.match(r"^-\s+\S", line) for line in general_lines) or not re.search(
        r"\b(?:SHOULD(?:\s+NOT)?|MAY)\b", general_text
    ):
        result.errors.append(
            "`<general_rules>` must contain at least one bulleted SHOULD/SHOULD NOT/MAY preference."
        )
        return result
    if agent_file.name == "orchestrator.agent.md":
        if (
            not all(re.search(rf"\bL{level}\b", risk_text) for level in range(4))
            or not all(
                re.search(term, risk_text, re.IGNORECASE)
                for term in (r"impact", r"reversib", r"security|data", r"uncertainty")
            )
            or "record" not in risk_text.lower()
        ):
            result.errors.append(
                "The Orchestrator `<risk_assessment>` must assign and record L0–L3 using impact, reversibility, security/data exposure, and uncertainty."
            )
            return result
    elif (
        "risk_level" not in risk_text
        or "downgrade" not in risk_text.lower()
        or "escalat" not in risk_text.lower()
    ):
        result.errors.append(
            "Specialist `<risk_assessment>` must consume the assigned `risk_level`, forbid downgrading it, and allow evidence-based escalation."
        )
        return result
    routing_lines = stripped_lines[routing_open + 1 : routing_close]
    routing_sections = ("## ACCEPT", "## REJECT")
    routing_positions = {
        section: [index for index, line in enumerate(routing_lines) if line == section]
        for section in routing_sections
    }
    if any(len(positions) != 1 for positions in routing_positions.values()):
        result.errors.append(
            "Canonical `<routing>` must contain exactly one `## ACCEPT` and one `## REJECT` section."
        )
        return result
    accept_position = routing_positions["## ACCEPT"][0]
    reject_position = routing_positions["## REJECT"][0]
    if accept_position >= reject_position:
        result.errors.append(
            "Canonical `<routing>` must place `## ACCEPT` before `## REJECT`."
        )
        return result
    accept_lines = routing_lines[accept_position + 1 : reject_position]
    reject_lines = routing_lines[reject_position + 1 :]
    if not any(re.match(r"^-\s+\S", line) for line in accept_lines):
        result.errors.append("Canonical `<routing>` `## ACCEPT` must contain a non-empty list.")
        return result
    reject_items = [line for line in reject_lines if re.match(r"^-\s+\S", line)]
    if not reject_items:
        result.errors.append("Canonical `<routing>` `## REJECT` must contain a non-empty list.")
        return result
    if any(
        not re.search(r"→\s*`[a-z0-9]+(?:-[a-z0-9]+)*`", line)
        for line in reject_items
    ):
        result.errors.append(
            "Every canonical `<routing>` `## REJECT` item must route to an exact agent identifier using `→ `agent-id``."
        )
        return result
    if not _has_agent_skills_entry(body):
        result.errors.append(
            "`<agent-skills>` must contain at least one skill/context entry or a statement that no skill is prescribed."
        )
        return result

    rules_lines = stripped_lines[rules_open + 1 : rules_close]
    required_rule_sections = (
        "## Role",
        "## Responsibilities",
        "## Constraints",
        "## Output Contract",
    )
    rule_positions = {}
    for section in required_rule_sections:
        positions = [index for index, line in enumerate(rules_lines) if line == section]
        if len(positions) != 1:
            result.errors.append(
                "Canonical `<rules>` must contain exactly one each of `## Role`, `## Responsibilities`, `## Constraints`, and `## Output Contract`."
            )
            return result
        rule_positions[section] = positions[0]

    if list(rule_positions.values()) != sorted(rule_positions.values()):
        result.errors.append(
            "Canonical `<rules>` sections must appear in this order: `## Role`, `## Responsibilities`, `## Constraints`, `## Output Contract`."
        )
        return result

    workflow_lines = stripped_lines[workflow_open + 1 : workflow_close]
    step_lines = [line for line in workflow_lines if STEP_HEADING_PATTERN.match(line)]
    all_step_lines = [
        line for line in stripped_lines if STEP_HEADING_PATTERN.match(line)
    ]
    step_patterns = (
        r"^##\s+Step\s+1\s+-\s+.+$",
        r"^##\s+Step\s+2\s+-\s+.+$",
        r"^##\s+Step\s+3\s+-\s+.+$",
    )
    if (
        len(all_step_lines) != len(step_patterns)
        or all_step_lines != step_lines
        or any(
            not re.fullmatch(pattern, line)
            for pattern, line in zip(step_patterns, all_step_lines)
        )
    ):
        result.errors.append(
            "Canonical agents must contain exactly `## Step 1 - ...`, "
            "`## Step 2 - ...`, and `## Step 3 - ...`, all inside "
            "`<workflow>` and in order."
        )
        return result
    step_1_position = workflow_lines.index(step_lines[0])
    step_2_position = workflow_lines.index(step_lines[1])
    step_1_text = "\n".join(workflow_lines[step_1_position + 1 : step_2_position])
    step_one_contract = (
        r"\b(?:risk(?:[_ -]assessment)?|assurance)\b"
        if agent_file.name == "orchestrator.agent.md"
        else r"\brisk_level\b"
    )
    if not re.search(step_one_contract, step_1_text, re.IGNORECASE):
        result.errors.append(
            "`<workflow>` Step 1 must assign Orchestrator risk or consume the inherited `risk_level` before substantive work."
        )
        return result

    if "<role>" in stripped_lines or "</role>" in stripped_lines:
        result.errors.append(
            "Agent markdown body should not wrap content in a `<role>` block; use the `## Role` heading instead."
        )
    if "# Role" in rules_lines:
        result.errors.append(
            "Canonical wrapped agents must use `## Role` inside `<rules>`, not `# Role`."
        )

    uses_routing_file_refs = _uses_routing_file_refs(body)
    if uses_routing_file_refs:
        if agent_file.parent.name == "agents":
            result.errors.append(
                "Legacy agents that still read sibling routing files must live in a dedicated package directory such as `.github/agents/<slug>/<slug>.agent.md` so those paths resolve per-agent."
            )
            return result

        for support_name in ("USEFOR.md", "DONOTUSEFOR.md"):
            support_path = agent_file.parent / "references" / support_name
            if not support_path.exists():
                result.errors.append(
                    f"Legacy agents that use sibling routing files must include the support file: {support_path}"
                )

    return result


def _validate_legacy_wrapped_agent_body(body: str, agent_file: Path) -> LintResult:
    result = LintResult()
    stripped_lines = [line.strip() for line in body.splitlines() if line.strip()]
    required_tokens = [
        "<definitions>",
        "</definitions>",
        "<workflow>",
        "## Role",
        "<rules>",
        "## Responsibilities",
        "## Constraints",
        "## Output Contract",
        "</rules>",
        "</workflow>",
    ]
    token_positions: dict[str, int] = {}
    for token in required_tokens:
        try:
            token_positions[token] = stripped_lines.index(token)
        except ValueError:
            has_open_rules = "<rules>" in stripped_lines
            has_close_rules = "</rules>" in stripped_lines
            if has_open_rules and not has_close_rules:
                result.errors.append(
                    "Partial `<rules>` block detected: either omit `<rules>` entirely or use both `<rules>` and `</rules>`."
                )
                return result
            result.errors.append(
                "Agent markdown body is missing expected sections. Wrapped agents must include <definitions>, <workflow>, ## Role, <rules> with ## Responsibilities, ## Constraints, ## Output Contract, and closing wrappers."
            )
            return result

    step_lines = [line for line in stripped_lines if STEP_HEADING_PATTERN.match(line)]
    step_patterns = [
        r"^##\s+Step\s+1\s+-\s+.+$",
        r"^##\s+Step\s+2\s+-\s+.+$",
        r"^##\s+Step\s+3\s+-\s+.+$",
    ]
    workflow_steps = [
        line for line in step_lines if re.match(r"^##\s+Step\s+[1-3]\b", line)
    ]
    if len(workflow_steps) != len(step_patterns) or any(
        not re.fullmatch(pattern, line)
        for pattern, line in zip(step_patterns, workflow_steps)
    ):
        result.errors.append(
            "Wrapped agents must keep workflow headings in this order: ## Step 1 - ..., ## Step 2 - ..., ## Step 3 - ..."
        )
        return result

    step_positions = {line: stripped_lines.index(line) for line in workflow_steps}
    if not (
        token_positions["<definitions>"]
        < token_positions["</definitions>"]
        < token_positions["<workflow>"]
        < token_positions["## Role"]
        < token_positions["<rules>"]
        < token_positions["## Responsibilities"]
        < token_positions["## Constraints"]
        < token_positions["## Output Contract"]
        < token_positions["</rules>"]
        < step_positions[workflow_steps[0]]
        < step_positions[workflow_steps[1]]
        < step_positions[workflow_steps[2]]
        < token_positions["</workflow>"]
    ):
        result.errors.append(
            "Wrapped agents must keep this order: <definitions>, <workflow>, ## Role, <rules>, ## Responsibilities, ## Constraints, ## Output Contract, </rules>, Step 1, Step 2, Step 3, </workflow>."
        )

    if "<role>" in stripped_lines or "</role>" in stripped_lines:
        result.errors.append(
            "Agent markdown body should not wrap content in a `<role>` block; use the `## Role` heading instead."
        )

    if "# Role" in stripped_lines:
        result.errors.append(
            "Wrapped agents must use `## Role` inside the workflow block, not `# Role`."
        )
    uses_routing_file_refs = _uses_routing_file_refs(body)

    if uses_routing_file_refs:
        if agent_file.parent.name == "agents":
            result.errors.append(
                "Legacy agents that still read sibling routing files must live in a dedicated package directory such as `.github/agents/<slug>/<slug>.agent.md` so those paths resolve per-agent."
            )
            return result

        for support_name in ("USEFOR.md", "DONOTUSEFOR.md"):
            support_path = agent_file.parent / "references" / support_name
            if not support_path.exists():
                result.errors.append(
                    f"Legacy agents that use sibling routing files must include the support file: {support_path}"
                )

    return result


def _validate_legacy_agent_body_sections(body: str) -> LintResult:
    result = LintResult()
    stripped_lines = [line.strip() for line in body.splitlines() if line.strip()]
    required_tokens = [
        "# Role",
        "## Responsibilities",
        "## Constraints",
        "## Output Contract",
    ]
    token_positions: dict[str, int] = {}
    for token in required_tokens:
        try:
            token_positions[token] = stripped_lines.index(token)
        except ValueError:
            result.errors.append(
                "Agent markdown body is missing expected sections: # Role, ## Responsibilities, ## Constraints, and ## Output Contract."
            )
            return result

    if "<role>" in stripped_lines or "</role>" in stripped_lines:
        result.errors.append(
            "Agent markdown body should not wrap content in a `<role>` block; use the `# Role` heading instead."
        )

    step_lines = [line for line in stripped_lines if STEP_HEADING_PATTERN.match(line)]
    if step_lines:
        step_patterns = [
            r"^##\s+Step\s+1\s*$",
            r"^##\s+Step\s+2\s*$",
            r"^##\s+Step\s+3\s*$",
        ]
        if len(step_lines) != len(step_patterns) or any(
            not re.fullmatch(pattern, line)
            for pattern, line in zip(step_patterns, step_lines)
        ):
            result.errors.append(
                "Legacy agent markdown must keep headings in this order: ## Step 1, ## Step 2, ## Step 3."
            )
            return result

        step_positions = {line: stripped_lines.index(line) for line in step_lines}
        if not (
            token_positions["# Role"]
            < token_positions["## Responsibilities"]
            < token_positions["## Constraints"]
            < token_positions["## Output Contract"]
            < step_positions[step_lines[0]]
            < step_positions[step_lines[1]]
            < step_positions[step_lines[2]]
        ):
            result.errors.append(
                "Legacy agent markdown must keep the canonical order: # Role, ## Responsibilities, ## Constraints, ## Output Contract, ## Step 1, ## Step 2, ## Step 3."
            )
        return result

    workflow_heading = "## Workflow" if "## Workflow" in stripped_lines else None
    if workflow_heading is None and "## Approach" in stripped_lines:
        workflow_heading = "## Approach"
    if workflow_heading is None:
        result.errors.append(
            "Agent markdown body is missing expected sections: add either a ## Workflow or ## Approach heading, or use legacy ## Step 1/2/3 sections."
        )
        return result
    token_positions[workflow_heading] = stripped_lines.index(workflow_heading)

    if not (
        token_positions["# Role"]
        < token_positions["## Responsibilities"]
        < token_positions[workflow_heading]
        < token_positions["## Constraints"]
        < token_positions["## Output Contract"]
    ):
        result.errors.append(
            "Agent body must keep the canonical order: # Role, ## Responsibilities, ## Workflow or ## Approach, ## Constraints, ## Output Contract."
        )

    _validate_optional_wrapper(
        stripped_lines,
        tag="workflow",
        before_token="## Responsibilities",
        first_heading=workflow_heading,
        last_heading=workflow_heading,
        after_token="## Constraints",
        result=result,
    )
    _validate_optional_wrapper(
        stripped_lines,
        tag="rules",
        before_token=workflow_heading,
        first_heading="## Constraints",
        last_heading="## Output Contract",
        after_token=None,
        result=result,
    )

    return result


def lint_agent_markdown_contract(
    body: str,
    agent_file: Path,
    frontmatter: dict[str, Any] | None = None,
) -> LintResult:
    stripped_lines = [line.strip() for line in body.splitlines() if line.strip()]
    result = LintResult()
    has_step_zero = any(
        re.match(r"^##\s+Step\s+0\b", line, re.IGNORECASE)
        for line in stripped_lines
    )
    if has_step_zero:
        result.errors.append(
            "Agent bodies must not include a Step 0; express admission in the "
            "frontmatter description and begin workflows at Step 1."
        )
    if _has_agent_admission_matrix(body):
        result.errors.append(
            "Agent bodies must not include a body-level admission matrix; use the frontmatter description for selection."
        )
    if _has_agent_refusal_json(body):
        result.errors.append(
            "Agent bodies must not require or include a refusal JSON admission contract."
        )
    if result.errors:
        return result
    if _looks_like_wrapped_agent(stripped_lines, body):
        if _looks_like_canonical_wrapped_agent(stripped_lines):
            return _validate_canonical_wrapped_agent_body(body, agent_file)
        result = _validate_legacy_wrapped_agent_body(body, agent_file)
        result.warnings.clear()
        result.errors.append(
            "Agent bodies must use the canonical shape: optional non-empty `<definitions>`, `<routing>`, separate `<critical_rules>`, `<general_rules>`, and `<risk_assessment>` blocks, a `<rules>` block containing Role, Responsibilities, Constraints, and Output Contract, `<agent-skills>`, and a separate `<workflow>` with Steps 1-3."
        )
        return result

    result = _validate_legacy_agent_body_sections(body)
    result.warnings.clear()
    result.errors.append(
        "Agent bodies must use the canonical shape: optional non-empty `<definitions>`, `<routing>`, separate `<critical_rules>`, `<general_rules>`, and `<risk_assessment>` blocks, a `<rules>` block containing Role, Responsibilities, Constraints, and Output Contract, `<agent-skills>`, and a separate `<workflow>` with Steps 1-3."
    )
    return result
