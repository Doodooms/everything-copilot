from __future__ import annotations

import re
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


def _validate_prompt_body(body: str, errors: list[str], warnings: list[str]) -> None:
    stripped_lines = [line.strip() for line in body.splitlines() if line.strip()]
    if not stripped_lines:
        errors.append("Prompt body is empty.")
        return

    has_h1 = any(line.startswith("# ") for line in stripped_lines)
    has_h2 = any(line.startswith("## ") for line in stripped_lines)

    if not has_h1:
        errors.append("Prompt body must include a top-level `#` heading such as `# Task` or `# Role`.")

    if len(stripped_lines) >= 10 and not has_h2:
        warnings.append(
            "Longer prompt bodies should use short `##` sections such as `## Inputs`, `## Constraints`, or `## Output Contract` to avoid becoming visually flat."
        )


@app.command()
def validate_prompt(
    prompt_file: Path = typer.Option(
        ...,
        "--prompt-file",
        exists=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
        help="Path to the .prompt.md file to validate.",
    )
) -> None:
    """Validate a reusable workspace prompt file."""

    errors: list[str] = []
    warnings: list[str] = []

    if not prompt_file.name.endswith(".prompt.md"):
        errors.append("Prompt files created by this skill must end with `.prompt.md`.")

    relative_path = _relative_to_cwd(prompt_file)
    if tuple(relative_path.parts[:2]) != (".github", "prompts"):
        warnings.append("Repository convention is to store workspace prompts under `.github/prompts/`.")

    text = prompt_file.read_text(encoding="utf-8")
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
            warnings.append("`description` should include `What:` to state the prompt's job clearly.")
        if "use when:" not in lowered_description:
            warnings.append("`description` should include `Use when:` phrases for reliable routing.")

    for string_field in ("name", "argument-hint", "agent"):
        value = frontmatter.get(string_field)
        if value is not None and not _is_non_empty_string(value):
            errors.append(f"`{string_field}`, when present, must be a non-empty string.")

    tools = _validate_string_list(frontmatter.get("tools"), "tools", errors)
    if len(tools) > 8:
        warnings.append("Tool list is broad; remove tools the prompt does not truly need.")

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

    _validate_prompt_body(body, errors, warnings)

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