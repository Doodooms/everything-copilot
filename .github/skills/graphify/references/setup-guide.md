# Graphify Setup Guide

Source: https://github.com/safishamsi/graphify

## Installation

```
uv sync
```

Note: the PyPI package name is `graphifyy` (double-y). Other `graphify*` packages
on PyPI are unaffiliated.

## First Run

Preferred in this repository: use the workspace [/graphify prompt](../../../prompts/graphify.prompt.md) in Copilot Chat. It is the user-facing entrypoint and delegates to the canonical workflow owned by [../SKILL.md](../SKILL.md).

```
/graphify .
```

Headless CLI mode remains available when explicit backend credentials exist:

```
cd <your-project-root>

# Code-only extraction (free, local, no API):
uv run graphify extract .

# Code + docs/PDFs/images (requires LLM API key):
uv run graphify extract . --backend openai   # set OPENAI_API_KEY
uv run graphify extract . --backend claude   # set ANTHROPIC_API_KEY
uv run graphify extract . --backend gemini   # set GOOGLE_API_KEY or GEMINI_API_KEY
uv run graphify extract . --backend ollama   # local model, no API key
```

## VS Code Copilot Integration (one-time setup)

```
uv run graphify vscode install
```

This installs graphify's vendor-managed user-level Copilot integration. It is optional in this repository because the workspace already provides [/graphify prompt](../../../prompts/graphify.prompt.md) backed by [../SKILL.md](../SKILL.md).

## .graphifyignore

Create `.graphifyignore` in the project root (same syntax as `.gitignore`):

```
# Build outputs
dist/
build/
*.pyc
__pycache__/

# Package managers
node_modules/
.venv/
venv/

# Generated files
*.min.js
*.bundle.js
migrations/
graphify-out/

# Binary assets
*.png
*.jpg
*.pdf
*.mp4
```

## .graphifyinclude

`graphify.detect()` skips hidden directories by default. If important content lives under hidden directories such as `.github/` or `.vscode/`, allowlist them explicitly in `.graphifyinclude`:

```
/.github/
/.vscode/
```

Use `.graphifyignore` to subtract noisy subpaths afterward, for example:

```
.github/plan_history/
.github/tasks/
.vscode/copilot-tools.snapshot.json
```

## Git: What to commit

Commit:
- `graphify-out/graph.json`
- `graphify-out/GRAPH_REPORT.md`
- `graphify-out/graph.html`

Do NOT commit:
- `graphify-out/manifest.json` (local mtime tracking)
- `graphify-out/cost.json` (API usage tracking)
- `graphify-out/cache/` (large SHA256 cache)

Add to `.gitignore`:
```
graphify-out/manifest.json
graphify-out/cost.json
graphify-out/cache/
```

## Git hooks (optional, keeps graph fresh)

```
graphify hooks install
```

Installs a post-commit hook that incrementally rebuilds only changed files (AST only,
no API cost). Keeps graph in sync with code without manual re-runs.

## Multi-repo global graph

```
graphify extract . --global --as my-backend-service
graphify extract ../frontend --global --as my-frontend-app
graphify query "shortest path between UserController and PaymentService"
```

Global graph is stored at `~/.graphify/global.json`.
