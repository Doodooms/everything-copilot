#!/usr/bin/env bash
# Checks the canonical MCP workflow's required local support and version-aware protocol contract.
# Usage: ./validate_mcp.sh [--skill-dir <plugin-engineering directory>]
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DOMAIN_DIR="$(cd -- "$SCRIPT_DIR/../../.." && pwd)"
if [[ "${1:-}" == "--skill-dir" && -n "${2:-}" && "$#" -eq 2 ]]; then
  DOMAIN_DIR="$2"
elif [[ "$#" -ne 0 ]]; then
  echo "Usage: $0 [--skill-dir <plugin-engineering directory>]" >&2
  exit 2
fi

WORKFLOW_FILE="$DOMAIN_DIR/workflows/create-mcp.md"
COMMON_FILE="$DOMAIN_DIR/references/create-mcp/common-transport-security.md"
PATTERNS_FILE="$DOMAIN_DIR/references/create-mcp/rust-server-patterns.md"
SOURCES_FILE="$DOMAIN_DIR/references/create-mcp/references/URIs.md"
[[ -f "$DOMAIN_DIR/SKILL.md" ]] || { echo "plugin-engineering/SKILL.md not found" >&2; exit 1; }
[[ -f "$WORKFLOW_FILE" ]] || { echo "Canonical MCP workflow not found: $WORKFLOW_FILE" >&2; exit 1; }
for file in "$COMMON_FILE" "$PATTERNS_FILE" "$SOURCES_FILE"; do
  [[ -f "$file" ]] || { echo "Required MCP support not found: $file" >&2; exit 1; }
done
[[ -f "$DOMAIN_DIR/references/create-skill/scripts/validate.py" ]] || {
  echo "Canonical workflow validator not found under $DOMAIN_DIR" >&2
  exit 1
}

for reference in \
  '../references/create-mcp/common-transport-security.md' \
  '../references/create-mcp/rust-server-patterns.md' \
  '../references/create-mcp/references/URIs.md'; do
  grep -Fq "$reference" "$WORKFLOW_FILE" || {
    echo "create-mcp does not declare required support: $reference" >&2
    exit 1
  }
done

grep -Fq 'id: create-mcp' "$WORKFLOW_FILE" || {
  echo "Canonical MCP workflow metadata ID does not match its filename" >&2
  exit 1
}

mapfile -t steps < <(sed -nE 's/^## Step ([0-9]+) .*/\1/p' "$WORKFLOW_FILE")
((${#steps[@]} > 0)) || { echo "create-mcp has no numbered procedure" >&2; exit 1; }
for index in "${!steps[@]}"; do
  expected=$((index + 1))
  [[ "${steps[$index]}" == "$expected" ]] || {
    echo "create-mcp step sequence is incomplete: expected $expected, found ${steps[$index]}" >&2
    exit 1
  }
done

for required in \
  'MUST implement every new standalone MCP server in Rust' \
  'architectural exception' \
  'exact published `rmcp` version' \
  'target MCP protocol versions' \
  'graceful shutdown'; do
  grep -Fq "$required" "$WORKFLOW_FILE" || {
    echo "create-mcp is missing canonical contract text: $required" >&2
    exit 1
  }
done

grep -Fq '2026-07-28' "$COMMON_FILE" || {
  echo "Shared MCP guidance does not identify the current stable protocol revision" >&2
  exit 1
}
grep -Fq 'server/discover` is an optional' "$COMMON_FILE" || {
  echo "Shared MCP guidance must treat server/discover as optional" >&2
  exit 1
}
grep -Fq 'Do not require `initialize` for every server' "$COMMON_FILE" || {
  echo "Shared MCP guidance does not distinguish modern and legacy lifecycle tests" >&2
  exit 1
}

echo "Canonical MCP workflow and support checks passed under $DOMAIN_DIR."
echo "Run references/create-skill/scripts/validate.py --skill-dir $DOMAIN_DIR for canonical package and link validation."
