# Graphify Setup Guide

Source: https://github.com/safishamsi/graphify

## Installation

```
pip install graphifyy
```

Note: the PyPI package name is `graphifyy` (double-y). Other `graphify*` packages
on PyPI are unaffiliated.

## First Run

```
cd <your-project-root>

# Code-only extraction (free, local, no API):
graphify extract .

# Code + docs/PDFs/images (requires LLM API key):
graphify extract . --backend openai   # set OPENAI_API_KEY
graphify extract . --backend claude   # set ANTHROPIC_API_KEY
graphify extract . --backend gemini   # set GOOGLE_API_KEY
graphify extract . --backend ollama   # local model, no API key
```

## VS Code Copilot Integration (one-time setup)

```
graphify vscode install
```

This writes a config to VS Code user settings that automatically injects
`graphify-out/GRAPH_REPORT.md` into Copilot Chat context before answering
codebase questions.

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
