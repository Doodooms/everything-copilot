from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import typer
import yaml


FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)
STEP_HEADING_PATTERN = re.compile(r"^##\s+Step\s+(\d+)\b", re.IGNORECASE)
VALID_AGENT_TOOLS = {
    "agent",
    "browser",
    "execute",
    "edit",
    "read",
    "search",
    "search/codebase",
    "search/usages",
    "todo",
    "vscode/askQuestions",
    "web",
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
REPO_ROOT = Path(__file__).resolve().parents[4]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"


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
        typer.echo("ERRORS:")
        for error in result.errors:
            typer.echo(f"  - {error}")
    if result.warnings:
        typer.echo("WARNINGS:")
        for warning in result.warnings:
            typer.echo(f"  - {warning}")


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


def lint_agent_frontmatter(frontmatter: dict[str, Any]) -> LintResult:
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
    for tool_name in tool_names:
        if tool_name in VALID_AGENT_TOOLS:
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
                continue
            if agent_name not in known_agents:
                result.errors.append(
                    f"Frontmatter `agents:` lists unknown agent `{agent_name}`."
                )

    return result


def _workspace_agent_names() -> set[str]:
    if not AGENTS_DIR.exists():
        return set()

    names = set()
    for candidate in AGENTS_DIR.rglob("*.agent.md"):
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
    )


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


def _validate_wrapped_agent_body(body: str, agent_file: Path) -> LintResult:
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
    if _looks_like_wrapped_agent(stripped_lines, body):
        return _validate_wrapped_agent_body(body, agent_file)

    result = _validate_legacy_agent_body_sections(body)
    if not result.errors:
        result.warnings.append(
            "Agent body uses the legacy unwrapped contract. New agents should use the wrapped role, rules, and ordered workflow contract."
        )
    return result
