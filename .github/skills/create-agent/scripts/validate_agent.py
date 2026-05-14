from __future__ import annotations

import sys
from pathlib import Path

import typer


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.customization_lint import (  # noqa: E402
    LintResult,
    _print_result,
    lint_agent_frontmatter,
    lint_agent_markdown_contract,
    split_frontmatter,
)


def main(
    agent_file: Path = typer.Option(
        ...,
        "--agent-file",
        exists=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to the .agent.md file to validate.",
    )
) -> None:
    text = agent_file.read_text(encoding="utf-8")
    result = LintResult()

    try:
        frontmatter, body = split_frontmatter(text)
    except ValueError as exc:
        result.errors.append(str(exc))
        body = ""
    else:
        result.extend(lint_agent_frontmatter(frontmatter))

    if body:
        result.extend(lint_agent_markdown_contract(body, agent_file))
    else:
        result.errors.append("Agent body is empty.")

    _print_result(result)
    if result.errors:
        raise typer.Exit(code=1)

    typer.echo("Validation passed.")
    raise typer.Exit(code=0)


if __name__ == "__main__":
    typer.run(main)