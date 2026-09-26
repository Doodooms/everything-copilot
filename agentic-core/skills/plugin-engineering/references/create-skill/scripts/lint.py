from __future__ import annotations

from pathlib import Path

import typer

from skill_lint_core import LintResult, _print_result, lint_skill_markdown


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
    skill_file = skill_dir / "SKILL.md"
    result = LintResult()
    if not skill_file.exists():
        result.errors.append(f"SKILL.md not found in {skill_dir}")
    else:
        result = lint_skill_markdown(skill_dir, skill_file.read_text(encoding="utf-8"))
    _print_result(result)
    if result.errors:
        raise typer.Exit(code=3)
    typer.echo("Lint passed (warnings may need attention).")


if __name__ == "__main__":
    typer.run(main)