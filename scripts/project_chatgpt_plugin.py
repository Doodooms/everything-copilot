#!/usr/bin/env python3
"""Project any canonical Expertise Pack as a ChatGPT plugin package."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from expertise.errors import ExpertiseError, TargetError
from expertise.parser import parse_pack
from expertise.targets.chatgpt import compile_chatgpt
from expertise.targets.common import validate_target_files
from expertise.validator import load_json_no_duplicate_keys


def _materialize(files: dict[str, bytes], output: Path) -> Path:
    if not output.is_absolute():
        raise TargetError("output path must be absolute")
    if output.exists() or output.is_symlink():
        raise TargetError(f"refusing to overwrite existing output: {output}")
    if output.parent.is_symlink() or not output.parent.is_dir():
        raise TargetError("output parent must be an existing real directory")
    output.mkdir()
    try:
        for relative, content in sorted(validate_target_files(files).items()):
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
    parser.add_argument("--pack-id", required=True)
    parser.add_argument(
        "--app-ids-json",
        type=Path,
        help="optional JSON object mapping canonical MCP server IDs to registered app IDs",
    )
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--tunnel-id")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        app_ids = (
            load_json_no_duplicate_keys(args.app_ids_json.read_bytes())
            if args.app_ids_json is not None
            else {}
        )
        if not isinstance(app_ids, dict) or any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in app_ids.items()
        ):
            raise TargetError("app ID mapping must be a JSON object of strings")
        source = parse_pack(ROOT / "expertise" / "packs" / args.pack_id)
        files, provenance = compile_chatgpt(
            source,
            app_ids,
            workspace=args.workspace,
            tunnel_id=args.tunnel_id,
        )
        output = _materialize(files, args.output)
        print(
            json.dumps(
                {
                    "status": "projected",
                    "target": "chatgpt-package",
                    "source_pack": provenance["source_pack"],
                    "source_digest": provenance["source_digest"],
                    "connection_status": provenance["connection_status"],
                    "mcp_servers": provenance["mcp_servers"],
                    "output": str(output),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0
    except (
        ExpertiseError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        ValueError,
    ) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
