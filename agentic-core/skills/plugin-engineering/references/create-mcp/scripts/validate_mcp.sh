#!/usr/bin/env bash
# Checks the two MCP workflow subskills and their shared domain reference.
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

COMMON_REFERENCE="../references/create-mcp/common-transport-security.md"
COMMON_FILE="$DOMAIN_DIR/references/create-mcp/common-transport-security.md"
[[ -f "$DOMAIN_DIR/SKILL.md" ]] || { echo "plugin-engineering/SKILL.md not found" >&2; exit 1; }
[[ -f "$COMMON_FILE" ]] || { echo "Shared MCP transport/security reference not found: $COMMON_FILE" >&2; exit 1; }
[[ -f "$DOMAIN_DIR/references/create-skill/scripts/validate.py" ]] || {
  echo "Canonical workflow validator not found under $DOMAIN_DIR" >&2
  exit 1
}

for workflow in create-mcp create-mcp-rust; do
  workflow_file="$DOMAIN_DIR/workflows/$workflow.md"
  [[ -f "$workflow_file" ]] || { echo "Workflow not found: $workflow_file" >&2; exit 1; }
  grep -Fq "$COMMON_REFERENCE" "$workflow_file" || {
    echo "$workflow does not reference the shared MCP guidance" >&2
    exit 1
  }
  grep -Fq "id: $workflow" "$workflow_file" || {
    echo "$workflow metadata ID does not match its filename" >&2
    exit 1
  }

  mapfile -t steps < <(sed -nE 's/^## Step ([0-9]+) .*/\1/p' "$workflow_file")
  ((${#steps[@]} > 0)) || { echo "$workflow has no numbered procedure" >&2; exit 1; }
  for index in "${!steps[@]}"; do
    expected=$((index + 1))
    [[ "${steps[$index]}" == "$expected" ]] || {
      echo "$workflow step sequence is incomplete: expected $expected, found ${steps[$index]}" >&2
      exit 1
    }
  done
done

echo "MCP workflow scaffold checks passed under $DOMAIN_DIR."
echo "Run references/create-skill/scripts/validate.py --skill-dir $DOMAIN_DIR for canonical package and reference validation."
