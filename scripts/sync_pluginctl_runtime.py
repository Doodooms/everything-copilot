"""Synchronize the canonical Expertise framework into Agentic Core's package."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "expertise"
TARGET = ROOT / "agentic-core" / "runtime" / "expertise"


def _files(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix not in {".pyc", ".pyo"}
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="update the packaged copy from the canonical expertise/ source",
    )
    args = parser.parse_args()

    source_files = _files(SOURCE)
    packaged_files = _files(TARGET) if TARGET.is_dir() else {}
    stale = sorted(set(packaged_files) - set(source_files))
    if stale:
        print("stale packaged files require manual review:")
        for relative in stale:
            print(f"  {relative}")
        return 1

    differences = [
        relative
        for relative, content in source_files.items()
        if packaged_files.get(relative) != content
    ]
    if not differences:
        print("packaged Expertise runtime matches canonical source")
        return 0
    if not args.write:
        print("packaged Expertise runtime is out of sync:")
        for relative in differences:
            print(f"  {relative}")
        print("run scripts/sync_pluginctl_runtime.py --write to update it")
        return 1

    for relative in differences:
        destination = TARGET / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source_files[relative])
    print(f"synchronized {len(differences)} Expertise runtime files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
