# agentic-workflow

This repository stores a deterministic GitHub Copilot workflow: skills, agents, prompts, instructions, hooks, and MCP configuration that can be reused across projects.

## Prerequisites

- VS Code with a compatible GitHub Copilot extension
- `uv`
- Python 3.10+

## Setup

From the repository root, run:

```bash
uv sync
```

This creates or updates the local `.venv` from [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock).

## Graphify

This repository uses `graphifyy` as the semantic graph tool for workspace exploration. It is installed through the root uv project and is intended to map the repository's markdown-heavy orchestration content, not just its small amount of code.

Preferred mode in this repository: use the workspace `/graphify` prompt in Copilot Chat. That prompt uses GitHub Copilot itself as the semantic extraction backend, so no external API keys are required.

Build the graph in Copilot Chat with:

```text
/graphify .
```

That prompt lives in [.github/prompts/graphify.prompt.md](.github/prompts/graphify.prompt.md) and serves as the user-facing entrypoint to the canonical graphify workflow in [.github/skills/graphify/SKILL.md](.github/skills/graphify/SKILL.md).

Build the graph from the repository root:

```bash
uv run graphify extract . --backend <backend>
```

Use the headless command above only when you explicitly have external backend credentials configured. For this repository, most important content lives in `.md` files, so the Copilot-native `/graphify` prompt is the default path.

If you want MCP tool access after the graph exists, the workspace MCP config starts graphify from the local uv environment with:

```bash
uv run python -m graphify.serve graphify-out/graph.json
```

Optional VS Code Copilot Chat integration:

```bash
uv run graphify vscode install
```

That command installs graphify's vendor-managed user-level Copilot skill. It is optional here because the repository already provides a workspace-local `/graphify` prompt.

## Daily usage

1. Open the repository in VS Code.
2. Read [.github/PLAN.md](.github/PLAN.md) for the repository structure and operating model.
3. Read [.github/copilot-instructions.md](.github/copilot-instructions.md) for always-on agent rules.
4. Use Copilot Chat with the repository skills, prompts, and agents.

## Running repository Python tooling

Prefer `uv run` so commands use the repository environment without manual activation.

Examples:

```bash
uv run python .github/skills/create-skill/scripts/validate_skill.py --skill-dir .github/skills/create-skill
uv run python -c "import typer, yaml, mcp"
```

If you prefer direct interpreter paths after syncing, `./.venv/bin/python` remains valid.

## Updating dependencies

Use `uv` to modify the manifest, then refresh the lockfile.

```bash
uv add <package>
uv remove <package>
uv lock
uv sync
```

Commit both [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock) when dependencies change.

## Notes

- This repository is not published as a Python package. The root [pyproject.toml](pyproject.toml) exists to manage local tooling dependencies reproducibly.
- Current local tooling dependencies include `graphifyy`, `mcp`, `pyyaml`, and `typer`.
- `uv sync` removes packages that are not declared in [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock).
- `graphify` is managed by the root uv project in this repository.
- `gitnexus` remains an external prerequisite managed outside the root uv project.
- For markdown-heavy graphify runs without external API keys, use the workspace [/graphify prompt](.github/prompts/graphify.prompt.md).