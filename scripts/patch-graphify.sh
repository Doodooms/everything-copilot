#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

extra_args=()
if [[ $# -gt 0 ]] && [[ "$1" != -* ]] && [[ ! -e "$1" ]]; then
  extra_args+=(--deleted)
fi

exec uv run python scripts/atomic_index.py patch-graphify "${extra_args[@]}" "$@"
