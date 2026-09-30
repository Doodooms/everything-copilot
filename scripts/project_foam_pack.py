#!/usr/bin/env python3
"""Build a local Foam Pack projection and bind it to one workspace."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from expertise.errors import ExpertiseError, TargetError
from expertise.foam_binding import bind_foam_workspace
from expertise.parser import parse_pack
from expertise.targets import compile_target
from expertise.targets.common import validate_target_files

PACK_ID = "foam-agent-plugin"


def _materialize(files: dict[str, bytes], output: Path) -> Path:
    if not output.is_absolute():
        raise TargetError("output path must be absolute")
    if output.exists() or output.is_symlink():
        raise TargetError(f"refusing to overwrite existing output: {output}")
    parent = output.parent
    if parent.is_symlink() or not parent.is_dir():
        raise TargetError(f"output parent must be an existing real directory: {parent}")
    validated = validate_target_files(files)
    output.mkdir()
    try:
        for relative, content in sorted(validated.items()):
            target = output.joinpath(*relative.split("/"))
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(content)
    except OSError:
        shutil.rmtree(output, ignore_errors=True)
        raise
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("portable", "codex"), required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        source = parse_pack(ROOT / "expertise" / "packs" / PACK_ID)
        artifact = compile_target(source, args.target)
        files = bind_foam_workspace(artifact.file_map(), args.workspace)
        output = _materialize(files, args.output)
        print(
            json.dumps(
                {
                    "status": "projected",
                    "pack": f"{source.ir.id}@{source.ir.version}",
                    "target": args.target,
                    "source_digest": artifact.source_digest,
                    "workspace": str(args.workspace.resolve(strict=True)),
                    "output": str(output),
                    "files": sorted(files),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0
    except (ExpertiseError, OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
