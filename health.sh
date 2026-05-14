#!/usr/bin/env bash

set -euo pipefail

for forbidden_path in AGENTS.md CLAUDE.md .claude .opencode opencode.json; do
	if [[ -e "$forbidden_path" ]]; then
		echo "Forbidden provider artifact present: $forbidden_path" >&2
		exit 1
	fi
done

shopt -s nullglob
repo_temp_artifacts=(.tmp-*)
shopt -u nullglob

if (( ${#repo_temp_artifacts[@]} > 0 )); then
	echo "Forbidden repo-root temporary artifacts present: ${repo_temp_artifacts[*]}" >&2
	exit 1
fi

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