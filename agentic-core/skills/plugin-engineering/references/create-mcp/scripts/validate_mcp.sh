#!/usr/bin/env bash
# Checks the canonical MCP workflow and its shared transport/security reference.
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
[[ -f "$DOMAIN_DIR/SKILL.md" ]] || { echo "plugin-engineering/SKILL.md not found" >&2; exit 1; }
[[ -f "$WORKFLOW_FILE" ]] || { echo "Canonical MCP workflow not found: $WORKFLOW_FILE" >&2; exit 1; }
[[ -f "$COMMON_FILE" ]] || { echo "Shared MCP transport/security reference not found: $COMMON_FILE" >&2; exit 1; }
[[ -f "$DOMAIN_DIR/references/create-skill/scripts/validate.py" ]] || {
  echo "Canonical workflow validator not found under $DOMAIN_DIR" >&2
  exit 1
}

COMMON_REFERENCE="../references/create-mcp/common-transport-security.md"
grep -Fq "$COMMON_REFERENCE" "$WORKFLOW_FILE" || {
  echo "create-mcp does not reference the shared MCP security guidance" >&2
  exit 1
}
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
  'official `rmcp` SDK' \
  'architectural exception' \
  'exact published `rmcp` version' \
  'Choose exactly one transport' \
  'initialize' \
  'graceful shutdown'; do
  grep -Fq "$required" "$WORKFLOW_FILE" || {
    echo "create-mcp is missing canonical contract text: $required" >&2
    exit 1
  }
done

echo "Canonical MCP workflow scaffold checks passed under $DOMAIN_DIR."
echo "Run references/create-skill/scripts/validate.py --skill-dir $DOMAIN_DIR for canonical package and reference validation."
