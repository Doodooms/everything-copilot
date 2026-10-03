"""Build a target projection from an explicit Agent Plugin source."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory.projection import codex, copilot
from factory.projection.claude import project_claude_plugin


def _write_projection(output_dir: Path, projection, check: bool, force: bool) -> int:
    output = Path(output_dir)
    files = projection.files
    target = projection.provenance["target"]
    sidecar = output.with_name(
        f"{output.name}.projection.json"
        if target == "claude"
        else f"{output.name}.{target}.projection.json"
    )
    sidecar_content = (
        json.dumps(projection.provenance, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    if check:
        mismatches = [
            name
            for name, content in files.items()
            if not (output / name).is_file()
            or (output / name).is_symlink()
            or (output / name).read_bytes() != content
        ]
        if mismatches:
            print(json.dumps({"status": "stale", "files": mismatches}))
            return 1
        if (
            sidecar.is_symlink()
            or not sidecar.is_file()
            or sidecar.read_bytes() != sidecar_content
        ):
            print(
                json.dumps({"status": "stale", "reason": "provenance sidecar differs"})
            )
            return 1
        print(
            json.dumps({"status": "current", **projection.provenance}, sort_keys=True)
        )
        return 0

    if target == "claude":
        projection.write(output, replace=force)
        print(
            json.dumps({"status": "projected", **projection.provenance}, sort_keys=True)
        )
        return 0

    output.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        destination = output / name
        if destination.is_symlink():
            raise ValueError(f"refusing to write through symlink: {destination}")
        if destination.exists() and destination.read_bytes() != content and not force:
            raise ValueError(
                f"refusing to replace differing generated file: {destination}"
            )
        if not destination.exists() or destination.read_bytes() != content:
            destination.write_bytes(content)
    if sidecar.is_symlink():
        raise ValueError(f"refusing to write through symlink: {sidecar}")
    if sidecar.exists() and sidecar.read_bytes() != sidecar_content and not force:
        raise ValueError(f"refusing to replace differing provenance sidecar: {sidecar}")
    sidecar.write_bytes(sidecar_content)
    print(json.dumps({"status": "projected", **projection.provenance}, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", choices=("codex", "copilot", "claude"))
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--force", action="store_true", help="replace only generated projection files"
    )
    args = parser.parse_args(argv)
    try:
        if args.target == "claude":
            projection = project_claude_plugin(args.source_root)
        else:
            projector = codex.project if args.target == "codex" else copilot.project
            projection = projector(args.source_root)
        return _write_projection(args.output_dir, projection, args.check, args.force)
    except (OSError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
