from __future__ import annotations

import sys
from pathlib import Path

import typer


app = typer.Typer(add_completion=False, no_args_is_help=True)

REPO_ROOT = Path(__file__).resolve().parents[1]
CREATE_SKILL_SCRIPTS = REPO_ROOT / ".github" / "skills" / "create-skill" / "scripts"
CREATE_AGENT_SCRIPTS = REPO_ROOT / ".github" / "skills" / "create-agent" / "scripts"

for scripts_dir in (CREATE_SKILL_SCRIPTS, CREATE_AGENT_SCRIPTS):
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

from skill_lint_core import (  # noqa: E402
    CANONICAL_CREATE_SURFACE_SKILL_NAMES,
    LintResult as SkillLintResult,
    _print_result as _print_skill_result,
    lint_skill_markdown,
    split_frontmatter,
)
from agent_lint_core import (  # noqa: E402
    LintResult as AgentLintResult,
    _print_result as _print_agent_result,
    lint_agent_frontmatter,
    lint_agent_markdown_contract,
    split_frontmatter as split_agent_frontmatter,
)

LintResult = SkillLintResult
_print_result = _print_skill_result


@app.command()
def agent(
    agent_file: Path = typer.Option(
        ...,
        "--agent-file",
        exists=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
        help="Path to the .agent.md file to lint.",
    )
) -> None:
    text = agent_file.read_text(encoding="utf-8")
    result = AgentLintResult()
    try:
        frontmatter, body = split_agent_frontmatter(text)
    except ValueError as exc:
        result.errors.append(str(exc))
        body = ""
    else:
        result.extend(lint_agent_frontmatter(frontmatter))

    if body:
        result.extend(lint_agent_markdown_contract(body, agent_file))
    else:
        result.errors.append("Agent body is empty.")

    _print_agent_result(result)
    if result.errors:
        raise typer.Exit(code=1)

    typer.echo("Lint passed.")
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
        help="Path to the skill directory containing SKILL.md.",
    )
) -> None:
    skill_file = skill_dir / "SKILL.md"
    result = SkillLintResult()
    if not skill_file.exists():
        result.errors.append(f"SKILL.md not found in {skill_dir}")
    else:
        result.extend(lint_skill_markdown(skill_dir, skill_file.read_text(encoding="utf-8")))

    _print_skill_result(result)
    if result.errors:
        raise typer.Exit(code=1)

    typer.echo("Lint passed.")
    raise typer.Exit(code=0)


@app.command("create-surfaces")
def create_surfaces(
    root: Path = typer.Option(
        Path.cwd(),
        "--root",
        exists=True,
        file_okay=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
        help="Repository root that contains the create-* skills.",
    )
) -> None:
    result = SkillLintResult()
    targets = [
        root / ".github" / "skills" / skill_name
        for skill_name in sorted(CANONICAL_CREATE_SURFACE_SKILL_NAMES)
    ]

    for target in targets:
        skill_file = target / "SKILL.md"
        if not skill_file.exists():
            result.errors.append(f"[{target.name}] SKILL.md not found: {skill_file}")
            continue

        lint_result = lint_skill_markdown(target, skill_file.read_text(encoding="utf-8"))
        result.errors.extend(f"[{target.name}] {error}" for error in lint_result.errors)
        result.warnings.extend(f"[{target.name}] {warning}" for warning in lint_result.warnings)

    _print_skill_result(result)
    if result.errors:
        raise typer.Exit(code=1)

    typer.echo("Lint passed.")
    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()