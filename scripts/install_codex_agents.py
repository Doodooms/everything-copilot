"""Source-checkout launcher for the installed Agentic Core Codex projector."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

PROJECTOR = (
    Path(__file__).resolve().parents[1]
    / "agentic-core"
    / "runtime"
    / "project_codex_agents.py"
)


def main() -> int:
    if not PROJECTOR.is_file():
        print(f"packaged Codex projector is missing: {PROJECTOR}", file=sys.stderr)
        return 2
    sys.argv[0] = str(PROJECTOR)
    runpy.run_path(str(PROJECTOR), run_name="__main__")
    return 0


def _projected_agents() -> dict[str, bytes]:
    """Keep the existing internal test seam on the packaged implementation."""
    namespace = runpy.run_path(str(PROJECTOR), run_name="agentic_core_codex_projector")
    return namespace["_projected_agents"]()


if __name__ == "__main__":
    raise SystemExit(main())
