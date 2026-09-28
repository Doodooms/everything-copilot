from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "AGENTS.md"
OUTPUT = ROOT / ".github/copilot-instructions.md"
MARKER = b"</risk_assessment>"


def project_instructions(source: bytes) -> bytes:
    """Return source bytes through the unique line-aligned risk marker."""
    lines = source.splitlines(keepends=True)
    marker_positions = []
    for index, line in enumerate(lines):
        content = line.removesuffix(b"\n").removesuffix(b"\r")
        if content == MARKER:
            marker_positions.append(index)
    if len(marker_positions) != 1:
        raise ValueError(
            "AGENTS.md must contain exactly one line-aligned </risk_assessment> marker"
        )
    return b"".join(lines[: marker_positions[0] + 1])


def _run(source_path: Path, output_path: Path, check: bool) -> int:
    projected = project_instructions(source_path.read_bytes())
    if check:
        if not output_path.is_file() or output_path.read_bytes() != projected:
            print(
                f"Copilot instructions projection is missing or out of date: {output_path}"
            )
            return 1
        print(f"Copilot instructions projection is current: {output_path}")
        return 0

    if not output_path.is_file() or output_path.read_bytes() != projected:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(projected)
    print(f"Copilot instructions projection generated: {output_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Project shared policy from AGENTS.md into Copilot instructions."
    )
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        return _run(args.source, args.output, args.check)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
