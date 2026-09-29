from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "agentic-core") not in sys.path:
    sys.path.insert(0, str(ROOT / "agentic-core"))

from core_agents import (  # noqa: E402
    CORE_AGENT_ROOT,
    load_core_agents,
    render_copilot_agent,
)


def project_copilot_agents(source_root: Path = CORE_AGENT_ROOT) -> dict[str, bytes]:
    projected = {
        f"{name}.agent.md": render_copilot_agent(agent)
        for name, agent in load_core_agents(source_root).items()
    }
    expected = {
        "architect.agent.md",
        "challenger.agent.md",
        "devops.agent.md",
        "implementer.agent.md",
        "orchestrator.agent.md",
        "planner.agent.md",
        "quality-assurance.agent.md",
        "researcher.agent.md",
        "reviewer.agent.md",
    }
    if set(projected) != expected:
        raise ValueError("Copilot Core-agent projection must contain all nine agents")
    return projected


def _run(output_dir: Path, source_root: Path, check: bool) -> int:
    projected = project_copilot_agents(source_root)
    if check:
        mismatches = [
            filename
            for filename, content in projected.items()
            if not (output_dir / filename).is_file()
            or (output_dir / filename).read_bytes() != content
        ]
        if mismatches:
            print("Copilot Core-agent projection is missing or out of date:")
            for filename in mismatches:
                print(f"- {output_dir / filename}")
            return 1
        print(f"Copilot Core-agent projection is current ({len(projected)} agents)")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in projected.items():
        (output_dir / filename).write_bytes(content)
    print(f"Copilot Core-agent projection generated ({len(projected)} agents)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the Copilot projection of the nine neutral Core agents."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "agentic-core/com.github.copilot/agents",
    )
    parser.add_argument("--source-root", type=Path, default=CORE_AGENT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        return _run(args.output_dir, args.source_root, args.check)
    except (OSError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
