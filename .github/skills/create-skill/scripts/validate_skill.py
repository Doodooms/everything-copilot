from __future__ import annotations

from pathlib import Path

import typer

from skill_lint_core import (
    LintResult,
    _print_result,
    lint_skill_markdown,
    split_frontmatter,
)


def main(
    skill_dir: Path = typer.Option(
        ...,
        "--skill-dir",
        exists=True,
        file_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to the skill directory containing SKILL.md.",
    )
) -> None:
    skill_file = skill_dir / "SKILL.md"
    result = LintResult()

    if not skill_file.exists():
        result.errors.append(f"SKILL.md not found in {skill_dir}")
        _print_result(result)
        raise typer.Exit(code=3)

    text = skill_file.read_text(encoding="utf-8")
    try:
        frontmatter, _ = split_frontmatter(text)
    except ValueError as exc:
        result.errors.append(str(exc))
    else:
        for key in ("name", "description", "user-invocable"):
            if key not in frontmatter:
                result.errors.append(f"Missing frontmatter key: {key}")
        if "name" in frontmatter and frontmatter["name"] != skill_dir.name:
            result.warnings.append(
                f"Frontmatter name '{frontmatter.get('name')}' != folder name '{skill_dir.name}'"
            )
        if "context" in frontmatter and "compatibility" not in frontmatter:
            result.warnings.append(
                "Frontmatter uses `context` without `compatibility`; declare compatibility bounds for version-gated behavior"
            )

    result.extend(lint_skill_markdown(skill_dir, text))

    _print_result(result)
    if result.errors:
        raise typer.Exit(code=3)

    typer.echo("Validation passed (warnings may need attention).")
    raise typer.Exit(code=0)


if __name__ == "__main__":
    typer.run(main)