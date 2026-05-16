from __future__ import annotations

from pathlib import Path

import typer

try:
    from scripts.capability_registry import (
        ValidationResult,
        find_workspace_root,
        validate_repository,
        validate_skill_capability_refs,
    )
except ImportError:
    from capability_registry import (  # type: ignore
        ValidationResult,
        find_workspace_root,
        validate_repository,
        validate_skill_capability_refs,
    )


app = typer.Typer(add_completion=False, no_args_is_help=True)


def _print_result(result: ValidationResult) -> None:
    if result.errors:
        typer.echo("ERRORS:")
        for error in result.errors:
            typer.echo(f"  - {error}")
    if result.warnings:
        typer.echo("WARNINGS:")
        for warning in result.warnings:
            typer.echo(f"  - {warning}")


@app.command()
def repo(
    root: Path = typer.Option(
        Path.cwd(),
        "--root",
        exists=True,
        file_okay=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
        help="Repository root containing .github/capabilities, .github/runtime, and .vscode/mcp.json.",
    )
) -> None:
    result = validate_repository(root)
    _print_result(result)
    if result.errors:
        raise typer.Exit(code=1)

    typer.echo("Validation passed.")
    raise typer.Exit(code=0)


@app.command()
def skill(
    skill_dir: Path = typer.Option(
        ...,
        "--skill-dir",
        exists=True,
        file_okay=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
        help="Skill directory containing SKILL.md.",
    )
) -> None:
    workspace_root = find_workspace_root(skill_dir)
    result = ValidationResult()
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        result.errors.append(f"SKILL.md not found in {skill_dir}")
    elif workspace_root is None:
        result.errors.append(f"Could not locate workspace root for {skill_dir}")
    else:
        result.extend(
            validate_skill_capability_refs(
                workspace_root,
                skill_file.read_text(encoding="utf-8"),
                source_name=skill_file.relative_to(workspace_root).as_posix(),
            )
        )

    _print_result(result)
    if result.errors:
        raise typer.Exit(code=1)

    typer.echo("Validation passed.")
    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()