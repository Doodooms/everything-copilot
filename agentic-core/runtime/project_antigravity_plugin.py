# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML>=6.0,<7"]
# ///
"""Project an Agentic Core plugin directory into Antigravity's plugin format."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RUNTIME_ROOT = Path(__file__).resolve().parent
PLUGIN_ROOT = RUNTIME_ROOT.parent
sys.path[:0] = [str(RUNTIME_ROOT), str(PLUGIN_ROOT)]

from projection_metadata import (
    file_map_digest,
    plugin_identity,
    plugin_tree_digest,
)

from expertise.errors import TargetError
from expertise.targets.antigravity_plugin import (
    AntigravityProjection,
    materialize_projection,
    project_core_plugin,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Project an Agentic Core plugin into Antigravity format."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=PLUGIN_ROOT,
        help="Agentic Core source plugin root (defaults to this installed plugin).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="new output directory for the standalone Antigravity plugin package",
    )
    return parser


def _summary(
    projection: AntigravityProjection,
    output: Path,
    source_root: Path,
) -> dict[str, object]:
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
        "target": "antigravity",
        "plugin": plugin_identity(source_root),
        "source_sha256": plugin_tree_digest(source_root),
        "projector_package_sha256": plugin_tree_digest(PLUGIN_ROOT),
        "artifact_sha256": file_map_digest(files, projection.executable_files),
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
        source_root = args.source
        projection = project_core_plugin(source_root)
        output = materialize_projection(projection, args.output)
        print(
            json.dumps(
                _summary(projection, output, source_root),
                ensure_ascii=False,
                indent=2,
            )
        )
    except (TargetError, OSError, TypeError, ValueError) as exc:
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
