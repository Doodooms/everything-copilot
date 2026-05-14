from __future__ import annotations

import difflib
import json
import re
import sys
from pathlib import Path
from typing import Any

import typer
import yaml

app = typer.Typer(add_completion=False, no_args_is_help=True)

FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)
TOOL_SNAPSHOT_PATH = Path(".vscode") / "copilot-tools.snapshot.json"
AGENT_FILE_PATTERNS = (
    ".github/agents/*.agent.md",
    ".github/agents/**/*.agent.md",
)
BUILTIN_AGENT_TOOL_NAMES = {
    "agent",
    "browser",
    "edit",
    "execute",
    "execute/getTerminalOutput",
    "read",
    "read/terminalLastCommand",
    "search",
    "search/codebase",
    "search/usages",
    "todo",
    "vscode/askQuestions",
    "vscode/memory",
    "vscode/vscodeAPI",
    "web",
    "web/fetch",
}
EXTENSION_MANIFEST_PATTERNS = (
    ".vscode/extensions/*/package.json",
    ".vscode-insiders/extensions/*/package.json",
    ".vscode-server/extensions/*/package.json",
    ".vscode-server/bin/*/extensions/*/package.json",
    ".vscode-insiders-server/extensions/*/package.json",
    ".vscode-insiders-server/bin/*/extensions/*/package.json",
)
WRONG_LAYER_TOOL_SUGGESTIONS = {
    "copilot_listDirectory": ["read"],
    "copilot_readFile": ["read"],
    "copilot_searchCodebase": ["search", "search/codebase"],
    "create_and_run_task": ["execute"],
    "explore_subagent": ["agent"],
    "run_in_terminal": ["execute"],
    "run_task": ["execute"],
    "runSubagent": ["agent"],
    "search_subagent": ["agent", "search/codebase"],
    "vscode_askQuestions": ["vscode/askQuestions"],
}


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
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


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_string_list(value: Any, field_name: str, errors: list[str]) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        errors.append(f"`{field_name}` must be a YAML list of strings.")
        return []

    cleaned: list[str] = []
    for item in value:
        if not _is_non_empty_string(item):
            errors.append(f"`{field_name}` entries must be non-empty strings.")
            return []
        cleaned.append(item.strip())
    return cleaned


def _relative_to_cwd(path: Path) -> Path:
    try:
        return path.relative_to(Path.cwd())
    except ValueError:
        return path


def _read_frontmatter(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        data = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def _find_workspace_root(start: Path) -> Path | None:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() or (candidate / ".vscode").exists() or (candidate / ".github").exists():
            return candidate
    return None


def _add_toolset_member(groups: dict[str, dict[str, set[str]]], toolset_name: str, tool_name: str, source: str) -> None:
    if not toolset_name:
        return

    entry = groups.get(toolset_name)
    if not entry:
        entry = {"members": set(), "sources": set()}
        groups[toolset_name] = entry

    entry["members"].add(tool_name)
    entry["sources"].add(source)


def _build_toolset_names(tools: list[dict[str, Any]]) -> set[str]:
    groups: dict[str, dict[str, set[str]]] = {}
    for tool in tools:
        tool_name = tool.get("name")
        if not isinstance(tool_name, str) or not tool_name:
            continue

        prefix = tool.get("prefix")
        if isinstance(prefix, str) and prefix:
            _add_toolset_member(groups, prefix, tool_name, "name-prefix")

        for tag in tool.get("tags", []):
            if isinstance(tag, str) and tag:
                _add_toolset_member(groups, tag, tool_name, "tag")

    return {
        toolset_name
        for toolset_name, group in groups.items()
        if len(group["members"]) > 1
    }


def _load_tool_snapshot(agent_file: Path) -> tuple[dict[str, Any] | None, str | None]:
    workspace_root = _find_workspace_root(agent_file)
    if not workspace_root:
        return None, None

    snapshot_path = workspace_root / TOOL_SNAPSHOT_PATH
    if not snapshot_path.exists():
        return None, None

    try:
        data = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, f"Tool snapshot could not be parsed: {snapshot_path} ({exc})"

    tool_names = {
        item.get("name")
        for item in data.get("tools", [])
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    toolset_names = {
        item.get("name")
        for item in data.get("toolSets", [])
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }

    return {
        "label": f"tool snapshot {snapshot_path}",
        "method": data.get("_method", "runtime-snapshot"),
        "tool_names": {name for name in tool_names if name},
        "toolset_names": {name for name in toolset_names if name},
    }, None


def _iter_extension_manifest_paths():
    seen_paths: set[Path] = set()
    home = Path.home()
    for pattern in EXTENSION_MANIFEST_PATTERNS:
        for manifest_path in sorted(home.glob(pattern)):
            resolved = manifest_path.resolve()
            if resolved in seen_paths:
                continue
            seen_paths.add(resolved)
            yield resolved


def _scan_extension_manifests() -> tuple[dict[str, Any] | None, str | None]:
    tools_by_name: dict[str, dict[str, Any]] = {}
    manifest_paths = list(_iter_extension_manifest_paths())
    if not manifest_paths:
        return None, "No VS Code extension manifests were found for static tool validation."

    for manifest_path in manifest_paths:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        tool_entries = manifest.get("contributes", {}).get("languageModelTools", [])
        if not isinstance(tool_entries, list):
            continue

        for tool_entry in tool_entries:
            if not isinstance(tool_entry, dict):
                continue

            tool_name = tool_entry.get("name")
            if not isinstance(tool_name, str) or not tool_name:
                continue

            tags = [
                tag
                for tag in tool_entry.get("tags", [])
                if isinstance(tag, str) and tag
            ]
            description = (
                tool_entry.get("modelDescription")
                or tool_entry.get("userDescription")
                or tool_entry.get("description")
                or ""
            )

            existing = tools_by_name.get(tool_name)
            if not existing:
                tools_by_name[tool_name] = {
                    "name": tool_name,
                    "description": description,
                    "tags": tags,
                    "prefix": tool_name.split("/", 1)[0] if "/" in tool_name else None,
                }
                continue

            existing_tags = set(existing.get("tags", []))
            existing_tags.update(tags)
            existing["tags"] = sorted(existing_tags)
            if len(description) > len(existing.get("description", "")):
                existing["description"] = description

    if not tools_by_name:
        return None, "No installed extension manifests contributed languageModelTools for static validation."

    tools = sorted(tools_by_name.values(), key=lambda item: item["name"])
    return {
        "label": "installed extension manifests",
        "method": "static-manifest-scan",
        "tool_names": {tool["name"] for tool in tools},
        "toolset_names": _build_toolset_names(tools),
    }, None


def _load_runtime_tool_catalog(agent_file: Path) -> tuple[dict[str, Any] | None, list[str]]:
    warnings: list[str] = []
    catalogs: list[dict[str, Any]] = []

    snapshot_catalog, snapshot_error = _load_tool_snapshot(agent_file)
    if snapshot_error:
        warnings.append(snapshot_error)
    if snapshot_catalog:
        catalogs.append(snapshot_catalog)

    manifest_catalog, manifest_error = _scan_extension_manifests()
    if manifest_error and not snapshot_catalog:
        warnings.append(manifest_error)
    if manifest_catalog:
        catalogs.append(manifest_catalog)

    if not catalogs:
        return None, warnings

    return {
        "label": " + ".join(catalog["label"] for catalog in catalogs),
        "method": "+".join(catalog["method"] for catalog in catalogs),
        "tool_names": set().union(*(catalog["tool_names"] for catalog in catalogs)),
        "toolset_names": set().union(*(catalog["toolset_names"] for catalog in catalogs)),
    }, warnings


def _build_tool_suggestions(tool_name: str, valid_tool_names: set[str]) -> list[str]:
    suggestions: list[str] = []

    for alias_suggestion in WRONG_LAYER_TOOL_SUGGESTIONS.get(tool_name, []):
        if alias_suggestion in valid_tool_names and alias_suggestion not in suggestions:
            suggestions.append(alias_suggestion)

    close_matches = difflib.get_close_matches(tool_name, sorted(valid_tool_names), n=5, cutoff=0.45)
    for suggestion in close_matches:
        if suggestion not in suggestions:
            suggestions.append(suggestion)

    return suggestions


def _slug_from_agent_path(path: Path) -> str:
    if path.name.endswith(".agent.md"):
        return path.name[:-len(".agent.md")]
    return path.stem


def _load_workspace_agent_names(agent_file: Path) -> tuple[set[str] | None, list[str]]:
    workspace_root = _find_workspace_root(agent_file)
    if not workspace_root:
        return None, [
            "Workspace root could not be determined; `agents:` and `handoffs` targets could not be checked deterministically."
        ]

    agent_names: set[str] = set()
    for pattern in AGENT_FILE_PATTERNS:
        for candidate in sorted(workspace_root.glob(pattern)):
            if not candidate.is_file():
                continue
            frontmatter = _read_frontmatter(candidate)
            if isinstance(frontmatter, dict):
                name = frontmatter.get("name")
                if _is_non_empty_string(name):
                    agent_names.add(name.strip())
            agent_names.add(_slug_from_agent_path(candidate))

    return agent_names, []


def _validate_agent_body_sections(body: str, errors: list[str]) -> None:
    stripped_lines = [line.strip() for line in body.splitlines() if line.strip()]
    required_tokens = ["# Role", "## Responsibilities", "## Constraints", "## Output Contract"]
    token_positions: dict[str, int] = {}
    for token in required_tokens:
        try:
            token_positions[token] = stripped_lines.index(token)
        except ValueError:
            errors.append(
                "Agent body must include # Role, ## Responsibilities, ## Constraints, and ## Output Contract headings."
            )
            return

    workflow_heading = "## Workflow" if "## Workflow" in stripped_lines else None
    if workflow_heading is None and "## Approach" in stripped_lines:
        workflow_heading = "## Approach"
    if workflow_heading is None:
        errors.append(
            "Agent body must include either a ## Workflow or ## Approach heading."
        )
        return
    token_positions[workflow_heading] = stripped_lines.index(workflow_heading)

    if not (
        token_positions["# Role"]
        < token_positions["## Responsibilities"]
        < token_positions[workflow_heading]
        < token_positions["## Constraints"]
        < token_positions["## Output Contract"]
    ):
        errors.append(
            "Agent body must keep the canonical order: # Role, ## Responsibilities, ## Workflow or ## Approach, ## Constraints, ## Output Contract."
        )


@app.command()
def validate_agent(
    agent_file: Path = typer.Option(
        ...,
        "--agent-file",
        exists=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
        help="Path to the .agent.md file to validate.",
    )
) -> None:
    """Validate a generated workspace custom agent file."""

    errors: list[str] = []
    warnings: list[str] = []

    if not agent_file.name.endswith(".agent.md"):
        errors.append("Agent files created by this skill must end with `.agent.md`.")

    relative_path = _relative_to_cwd(agent_file)
    if tuple(relative_path.parts[:2]) != (".github", "agents"):
        warnings.append(
            "Repository convention is to store workspace custom agents under `.github/agents/`."
        )

    text = agent_file.read_text(encoding="utf-8")
    try:
        frontmatter, body = _split_frontmatter(text)
    except ValueError as exc:
        errors.append(str(exc))
        frontmatter = {}
        body = ""

    description = frontmatter.get("description")
    if not _is_non_empty_string(description):
        errors.append("`description` is required and must be a non-empty string.")
    else:
        lowered_description = description.lower()
        if "what:" not in lowered_description:
            warnings.append("`description` should include `What:` to state the agent's primary job clearly.")
        if "use when:" not in lowered_description:
            warnings.append("`description` should include `Use when:` phrases for reliable routing.")

    name = frontmatter.get("name")
    if name is not None and not _is_non_empty_string(name):
        errors.append("`name`, when present, must be a non-empty string.")

    argument_hint = frontmatter.get("argument-hint")
    if argument_hint is not None and not _is_non_empty_string(argument_hint):
        errors.append("`argument-hint`, when present, must be a non-empty string.")

    tools = _validate_string_list(frontmatter.get("tools"), "tools", errors)
    if tools:
        duplicate_tools = sorted({tool for tool in tools if tools.count(tool) > 1})
        if duplicate_tools:
            warnings.append(f"Duplicate tool entries found: {', '.join(duplicate_tools)}")
        if len(tools) > 8:
            warnings.append("Tool list is broad; remove tools the agent does not truly need.")

    runtime_tool_catalog, runtime_tool_catalog_warnings = _load_runtime_tool_catalog(agent_file)
    warnings.extend(runtime_tool_catalog_warnings)
    valid_tool_names = set(BUILTIN_AGENT_TOOL_NAMES)
    if runtime_tool_catalog:
        valid_tool_names.update(runtime_tool_catalog["tool_names"])
        valid_tool_names.update(runtime_tool_catalog["toolset_names"])

    for tool_name in sorted(set(tools)):
        if tool_name in valid_tool_names and tool_name not in WRONG_LAYER_TOOL_SUGGESTIONS:
            continue

        suggestions = _build_tool_suggestions(tool_name, valid_tool_names)
        suggestion_text = f" Closest matches: {', '.join(suggestions)}" if suggestions else ""
        wrong_layer_text = " Wrong-layer raw tool name detected." if tool_name in WRONG_LAYER_TOOL_SUGGESTIONS else ""
        runtime_text = ""
        if runtime_tool_catalog and tool_name in (runtime_tool_catalog["tool_names"] | runtime_tool_catalog["toolset_names"]):
            runtime_text = " This name exists in the raw runtime registry but is not the preferred agent-facing alias."
        errors.append(
            f"`tools` entry not found in the workspace tool catalog: {tool_name}.{wrong_layer_text}{runtime_text}{suggestion_text}"
        )

    agents_field = frontmatter.get("agents")
    allowed_subagents: list[str] = []
    if agents_field is not None:
        if isinstance(agents_field, str):
            if agents_field != "*":
                errors.append("`agents` as a string must be exactly `*`.")
        elif isinstance(agents_field, list):
            invalid_entries = [entry for entry in agents_field if not _is_non_empty_string(entry)]
            if invalid_entries:
                errors.append("`agents` list entries must be non-empty strings.")
            else:
                allowed_subagents = [entry.strip() for entry in agents_field]
                duplicate_agents = sorted({entry for entry in allowed_subagents if allowed_subagents.count(entry) > 1})
                if duplicate_agents:
                    warnings.append(f"Duplicate `agents` entries found: {', '.join(duplicate_agents)}")
        else:
            errors.append("`agents` must be `*` or a YAML list of strings.")

        if "agent" not in tools:
            errors.append("`agents` requires the `agent` tool in `tools`.")

    if "agent" in tools and agents_field is None:
        warnings.append("`agent` in `tools` is broad without an `agents` allowlist; add `agents:` or remove `agent`.")
    if agents_field == "*":
        warnings.append("`agents: *` grants broad delegation; use an explicit allowlist unless broad delegation is intentional.")

    model = frontmatter.get("model")
    if model is not None:
        if isinstance(model, str):
            if not model.strip():
                errors.append("`model` must not be empty.")
        elif isinstance(model, list):
            if any(not _is_non_empty_string(item) for item in model):
                errors.append("`model` lists must contain only non-empty strings.")
        else:
            errors.append("`model` must be a string or a YAML list of strings.")

    for boolean_field in ("user-invocable", "disable-model-invocation"):
        value = frontmatter.get(boolean_field)
        if value is not None and not isinstance(value, bool):
            errors.append(f"`{boolean_field}` must be a boolean when present.")

    if "infer" in frontmatter:
        warnings.append("`infer` is deprecated; use `user-invocable` and `disable-model-invocation`.")

    target = frontmatter.get("target")
    if target is not None and not _is_non_empty_string(target):
        errors.append("`target`, when present, must be a non-empty string.")

    handoffs = frontmatter.get("handoffs")
    handoff_targets: list[tuple[int, str]] = []
    if handoffs is not None:
        if not isinstance(handoffs, list):
            errors.append("`handoffs` must be a YAML list.")
        else:
            for index, handoff in enumerate(handoffs, start=1):
                if not isinstance(handoff, dict):
                    errors.append(f"`handoffs[{index}]` must be a mapping.")
                    continue
                if not _is_non_empty_string(handoff.get("label")):
                    errors.append(f"`handoffs[{index}].label` is required.")
                if not _is_non_empty_string(handoff.get("agent")):
                    errors.append(f"`handoffs[{index}].agent` is required.")
                else:
                    handoff_targets.append((index, handoff["agent"].strip()))
                prompt = handoff.get("prompt")
                if prompt is not None and not _is_non_empty_string(prompt):
                    errors.append(f"`handoffs[{index}].prompt` must be a non-empty string when present.")
                send = handoff.get("send")
                if send is not None and not isinstance(send, bool):
                    errors.append(f"`handoffs[{index}].send` must be a boolean when present.")
                handoff_model = handoff.get("model")
                if handoff_model is not None and not _is_non_empty_string(handoff_model):
                    errors.append(f"`handoffs[{index}].model` must be a non-empty string when present.")

    hooks = frontmatter.get("hooks")
    if hooks is not None and not isinstance(hooks, dict):
        errors.append("`hooks` must be a YAML mapping when present.")

    workspace_agent_names, workspace_agent_name_warnings = _load_workspace_agent_names(agent_file)
    warnings.extend(workspace_agent_name_warnings)
    current_agent_names = {_slug_from_agent_path(agent_file)}
    if _is_non_empty_string(name):
        current_agent_names.add(name.strip())

    for candidate_name in sorted(set(allowed_subagents)):
        if candidate_name in current_agent_names:
            errors.append("`agents` must not reference the current agent itself.")
            continue
        if workspace_agent_names is not None and candidate_name not in workspace_agent_names:
            errors.append(f"`agents` references unknown workspace agent: {candidate_name}.")

    for index, handoff_target in handoff_targets:
        if handoff_target in current_agent_names:
            errors.append(f"`handoffs[{index}].agent` must not reference the current agent itself.")
            continue
        if workspace_agent_names is not None and handoff_target not in workspace_agent_names:
            errors.append(f"`handoffs[{index}].agent` references unknown workspace agent: {handoff_target}.")

    if not body:
        errors.append("Agent body is empty.")
    else:
        _validate_agent_body_sections(body, errors)

    if frontmatter.get("user-invocable") is False and frontmatter.get("disable-model-invocation") is True:
        warnings.append(
            "This agent is hidden from the picker and blocked from subagent use; ensure that fully internal behavior is intentional."
        )

    if errors:
        print("ERRORS:")
        for error in errors:
            print(f"  - {error}")
    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        raise typer.Exit(code=1)

    print("Validation passed.")


if __name__ == "__main__":
    app()