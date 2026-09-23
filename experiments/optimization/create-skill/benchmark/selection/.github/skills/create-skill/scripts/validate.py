from __future__ import annotations

from pathlib import Path

import typer

from skill_lint_core import LintResult, _print_result, lint_skill_markdown, split_frontmatter


def validate(skill_dir: Path) -> LintResult:
    result = LintResult()
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        result.errors.append(f"SKILL.md not found in {skill_dir}")
        return result
    text = skill_file.read_text(encoding="utf-8")
    try:
        frontmatter, _ = split_frontmatter(text)
    except ValueError as exc:
        result.errors.append(str(exc))
    else:
        for key in ("name", "description", "user-invocable"):
            if key not in frontmatter:
                result.errors.append(f"Missing frontmatter key: {key}")
        if frontmatter.get("name") != skill_dir.name:
            result.warnings.append(
                f"Frontmatter name '{frontmatter.get('name')}' != folder name '{skill_dir.name}'"
            )
        if "context" in frontmatter and "compatibility" not in frontmatter:
            result.warnings.append(
                "Frontmatter uses `context` without `compatibility`; declare compatibility bounds for version-gated behavior"
            )
    result.extend(lint_skill_markdown(skill_dir, text))
    return result


def main(
    skill_dir: Path = typer.Option(
        ...,
        "--skill-dir",
        exists=True,
        file_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to the skill directory containing SKILL.md.",
    ),
) -> None:
    result = validate(skill_dir)
    _print_result(result)
    if result.errors:
        raise typer.Exit(code=3)
    typer.echo("Validation passed (warnings may need attention).")


if __name__ == "__main__":
    typer.run(main)