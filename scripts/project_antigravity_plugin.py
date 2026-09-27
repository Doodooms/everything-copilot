from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from expertise.errors import TargetError
from expertise.targets.antigravity_plugin import (
    AntigravityProjection,
    materialize_projection,
    project_core_plugin,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Project the canonical Agentic Core plugin into Antigravity format."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=REPOSITORY_ROOT / "agentic-core",
        help="Agentic Core source plugin root (default: repository agentic-core/)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="new output directory for the standalone Antigravity plugin package",
    )
    return parser


def _summary(projection: AntigravityProjection, output: Path) -> dict[str, object]:
    files = projection.files
    skills = sorted(
        path.split("/")[1]
        for path in files
        if path.startswith("skills/")
        and path.count("/") == 2
        and path.endswith("/SKILL.md")
    )
    workflows = sorted(
        path
        for path in files
        if path.startswith("skills/") and "/workflows/" in path and path.endswith(".md")
    )
    agents = sorted(
        path.removeprefix("agents/").removesuffix(".md")
        for path in files
        if path.startswith("agents/") and path.endswith(".md")
    )
    mcp_config = json.loads(files["mcp_config.json"].decode("utf-8"))
    return {
        "status": "projected",
        "output": str(output),
        "skills": skills,
        "nested_workflows": len(workflows),
        "agents": agents,
        "mcp_servers": sorted(mcp_config["mcpServers"]),
        "hooks": "not emitted (no source hooks.json)",
        "commands": "not emitted (skills provide slash invocation)",
        "file_count": len(files),
        "executable_file_count": len(projection.executable_files),
        "mapping_losses": list(projection.mapping_losses),
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        projection = project_core_plugin(args.source)
        output = materialize_projection(projection, args.output)
    except (TargetError, OSError) as exc:
        print(
            json.dumps(
                {
                    "status": "error",
                    "error": type(exc).__name__,
                    "message": str(exc),
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(_summary(projection, output), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
