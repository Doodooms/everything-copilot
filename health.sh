#!/usr/bin/env bash

set -euo pipefail

command -v uv >/dev/null
command -v node >/dev/null
command -v npm >/dev/null

test -f pyproject.toml
test -f package.json
test -f .vscode/mcp.json
test -f agent-harness-kit.config.ts
test -f .harness/feature_list.json

uv run python -c "import graphify, ladybug, mcp, typer, yaml"
npx --no-install ahk --version >/dev/null

echo "agentic-workflow health check passed."