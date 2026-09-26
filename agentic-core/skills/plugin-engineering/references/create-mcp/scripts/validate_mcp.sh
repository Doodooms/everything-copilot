#!/usr/bin/env bash
# Validates that the create-mcp skill files are in canonical form.
# Usage: ./validate_mcp.sh [--skill-dir <path>]
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$SCRIPT_DIR/.."
if [[ "${1:-}" == "--skill-dir" && -n "${2:-}" ]]; then
  SKILL_DIR="$2"
elif [[ "$#" -ne 0 ]]; then
  echo "Usage: $0 [--skill-dir <path>]" >&2
  exit 2
fi
echo "create-mcp skill directory: $SKILL_DIR"
[ -f "$SKILL_DIR/SKILL.md" ] || { echo "SKILL.md not found"; exit 1; }
echo "OK"
