from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import typer
import yaml

app = typer.Typer(add_completion=False, no_args_is_help=True)

FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)


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
    elif "use when:" not in description.lower():
        warnings.append("`description` should include `Use when:` phrases for reliable routing.")

    name = frontmatter.get("name")
    if name is not None and not _is_non_empty_string(name):
        errors.append("`name`, when present, must be a non-empty string.")

    tools = _validate_string_list(frontmatter.get("tools"), "tools", errors)
    if tools:
        duplicate_tools = sorted({tool for tool in tools if tools.count(tool) > 1})
        if duplicate_tools:
            warnings.append(f"Duplicate tool entries found: {', '.join(duplicate_tools)}")
        if len(tools) > 8:
            warnings.append("Tool list is broad; remove tools the agent does not truly need.")

    agents = frontmatter.get("agents")
    if agents is not None:
        if isinstance(agents, str):
            if agents != "*":
                errors.append("`agents` as a string must be exactly `*`.")
        elif isinstance(agents, list):
            invalid_entries = [entry for entry in agents if not _is_non_empty_string(entry)]
            if invalid_entries:
                errors.append("`agents` list entries must be non-empty strings.")
        else:
            errors.append("`agents` must be `*` or a YAML list of strings.")

        if "agent" not in tools:
            errors.append("`agents` requires the `agent` tool in `tools`.")

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

    if not body:
        errors.append("Agent body is empty.")
    elif all(section not in body for section in ("## Workflow", "## Approach", "## Constraints", "## Output")):
        warnings.append(
            "Agent body has no explicit workflow, constraints, or output headings; consider making the contract clearer."
        )

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