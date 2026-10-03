"""Install Factory-generated Core agent profiles into a selected CODEX_HOME."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory.projection.codex import project

CORE_SOURCE = ROOT / "agentic-core"
EXPECTED_FILES = {
    "architect.toml",
    "challenger.toml",
    "devops.toml",
    "implementer.toml",
    "orchestrator.toml",
    "planner.toml",
    "quality-assurance.toml",
    "researcher.toml",
    "reviewer.toml",
}


def _codex_home(explicit: Path | None) -> Path:
    result = explicit or Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    if not result.is_absolute():
        raise ValueError("CODEX_HOME must be an absolute path")
    return result


def _projected_agents(source_root: Path = CORE_SOURCE) -> dict[str, bytes]:
    files = project(source_root).files
    if set(files) != EXPECTED_FILES:
        raise ValueError(
            "Agentic Core Codex projection must contain exactly nine agents"
        )
    return files


def _atomic_write(path: Path, content: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
    finally:
        Path(temporary_name).unlink(missing_ok=True)


def _run(*, source_root: Path, codex_home: Path, check: bool, force: bool) -> int:
    projection = project(source_root)
    if set(projection.files) != EXPECTED_FILES:
        raise ValueError(
            "Agentic Core Codex projection must contain exactly nine agents"
        )
    agents_dir = codex_home / "agents"

    if check:
        if agents_dir.is_symlink() or not agents_dir.is_dir():
            print(
                json.dumps(
                    {"status": "stale", "reason": "agents directory unavailable"}
                )
            )
            return 1
        mismatches = [
            name
            for name, content in projection.files.items()
            if (agents_dir / name).is_symlink()
            or not (agents_dir / name).is_file()
            or (agents_dir / name).read_bytes() != content
        ]
        sidecar = agents_dir / "agentic-core-codex.projection.json"
        expected_sidecar = _sidecar_bytes(projection.provenance)
        if (
            sidecar.is_symlink()
            or not sidecar.is_file()
            or sidecar.read_bytes() != expected_sidecar
        ):
            mismatches.append(sidecar.name)
        result = {
            "status": "stale" if mismatches else "current",
            **projection.provenance,
        }
        if mismatches:
            result["files"] = sorted(mismatches)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 1 if mismatches else 0

    if codex_home.is_symlink() or agents_dir.is_symlink():
        raise ValueError(
            "refusing to write through symlinked CODEX_HOME or agents directory"
        )
    conflicts = []
    for name, content in projection.files.items():
        path = agents_dir / name
        if path.is_symlink():
            raise ValueError(f"refusing to replace symlink: {path}")
        if path.exists() and not path.is_file():
            raise ValueError(f"Codex profile destination is not a regular file: {path}")
        if path.exists() and path.read_bytes() != content and not force:
            conflicts.append(name)
    if conflicts:
        raise ValueError(
            "generated Codex profiles differ; inspect them or rerun with --force: "
            + ", ".join(sorted(conflicts))
        )

    sidecar = agents_dir / "agentic-core-codex.projection.json"
    sidecar_content = _sidecar_bytes(projection.provenance)
    if sidecar.is_symlink():
        raise ValueError(f"refusing to replace symlink: {sidecar}")
    if sidecar.exists() and not sidecar.is_file():
        raise ValueError(
            f"Codex provenance destination is not a regular file: {sidecar}"
        )
    if sidecar.exists() and sidecar.read_bytes() != sidecar_content and not force:
        raise ValueError(
            "generated Codex provenance differs; inspect it or rerun with --force"
        )

    agents_dir.mkdir(parents=True, exist_ok=True)
    for name, content in projection.files.items():
        path = agents_dir / name
        if not path.is_file() or path.read_bytes() != content:
            _atomic_write(path, content)
    if not sidecar.is_file() or sidecar.read_bytes() != sidecar_content:
        _atomic_write(sidecar, sidecar_content)
    print(
        json.dumps(
            {"status": "projected", **projection.provenance},
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


def _sidecar_bytes(provenance: dict) -> bytes:
    return (
        json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=CORE_SOURCE)
    parser.add_argument(
        "--codex-home", type=Path, help="defaults to CODEX_HOME or ~/.codex"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="verify without writing")
    mode.add_argument(
        "--force", action="store_true", help="replace conflicting generated profiles"
    )
    args = parser.parse_args(argv)
    try:
        return _run(
            source_root=args.source_root,
            codex_home=_codex_home(args.codex_home),
            check=args.check,
            force=args.force,
        )
    except (OSError, TypeError, ValueError) as exc:
        print(
            json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
