"""Source-checkout launcher for the installed Agentic Core Antigravity projector."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

PROJECTOR = (
    Path(__file__).resolve().parents[1]
    / "agentic-core"
    / "runtime"
    / "project_antigravity_plugin.py"
)


def main() -> int:
    if not PROJECTOR.is_file():
        print(
            f"packaged Antigravity projector is missing: {PROJECTOR}", file=sys.stderr
        )
        return 2
    sys.argv[0] = str(PROJECTOR)
    runpy.run_path(str(PROJECTOR), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
