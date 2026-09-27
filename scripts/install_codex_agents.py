from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

import tomllib

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
AGENT_SOURCE_DIR = REPOSITORY_ROOT / "agentic-core" / "com.github.copilot" / "agents"
sys.path.insert(0, str(REPOSITORY_ROOT))

from expertise.targets.codex import render_codex_agent


def _codex_home(explicit: Path | None) -> Path:
    if explicit is not None:
        result = explicit
    else:
        configured = os.environ.get("CODEX_HOME")
        result = Path(configured) if configured else Path.home() / ".codex"
    if not result.is_absolute():
        raise ValueError("CODEX_HOME must be an absolute path")
    return result


def _projected_agents() -> dict[str, bytes]:
    sources = sorted(AGENT_SOURCE_DIR.glob("*.agent.md"))
    if not sources:
        raise ValueError(f"no canonical Copilot agents found in {AGENT_SOURCE_DIR}")

    projected: dict[str, bytes] = {}
    for source in sources:
        agent_id = source.name.removesuffix(".agent.md")
        filename = f"{agent_id}.toml"
        if filename in projected:
            raise ValueError(f"duplicate Codex agent output: {filename}")
        content = render_codex_agent(
            agent_id,
            source.read_bytes(),
            source_name=source.relative_to(REPOSITORY_ROOT).as_posix(),
        )
        try:
            role = tomllib.loads(content.decode("utf-8"))
        except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
            raise ValueError(f"invalid generated Codex role: {filename}") from exc
        if role.get("name") != agent_id:
            raise ValueError(f"generated role name does not match {filename}")
        projected[filename] = content
    return projected


def _atomic_write(path: Path, content: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _run(*, codex_home: Path, check: bool, force: bool) -> int:
    projected = _projected_agents()
    agents_dir = codex_home / "agents"
    if check:
        if agents_dir.is_symlink() or not agents_dir.is_dir():
            print(f"Codex agents directory is missing or not a directory: {agents_dir}")
            return 1
        mismatches = [
            filename
            for filename, content in projected.items()
            if not (agents_dir / filename).is_file()
            or (agents_dir / filename).is_symlink()
            or (agents_dir / filename).read_bytes() != content
        ]
        if mismatches:
            print("Codex agent projection is missing or out of date:")
            for filename in mismatches:
                print(f"- {agents_dir / filename}")
            return 1
        print(
            f"Codex agent projection is current ({len(projected)} roles): {agents_dir}"
        )
        return 0

    if codex_home.is_symlink() or (agents_dir.exists() and agents_dir.is_symlink()):
        raise ValueError(
            "refusing to write through a symlinked CODEX_HOME or agents directory"
        )

    conflicts: list[Path] = []
    for filename, content in projected.items():
        path = agents_dir / filename
        if path.is_symlink():
            raise ValueError(f"refusing to replace symlink: {path}")
        if path.exists() and not path.is_file():
            raise ValueError(f"Codex agent destination is not a regular file: {path}")
        if path.exists() and path.read_bytes() != content and not force:
            conflicts.append(path)
    if conflicts:
        details = "\n".join(f"- {path}" for path in conflicts)
        raise ValueError(
            "existing Codex agent files differ from the generated projection; "
            f"inspect them or rerun with --force:\n{details}"
        )

    agents_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    unchanged = 0
    for filename, content in projected.items():
        path = agents_dir / filename
        if path.is_file() and path.read_bytes() == content:
            unchanged += 1
            continue
        _atomic_write(path, content)
        written += 1
    print(
        f"Codex agent projection installed: {written} written, "
        f"{unchanged} unchanged, {len(projected)} total ({agents_dir})"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Project canonical agentic-core agents through the Codex target adapter "
            "into CODEX_HOME/agents."
        )
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        help="Codex home directory (defaults to CODEX_HOME or ~/.codex).",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="verify installed files without writing anything.",
    )
    mode.add_argument(
        "--force",
        action="store_true",
        help="replace conflicting generated agent files.",
    )
    args = parser.parse_args()
    try:
        return _run(
            codex_home=_codex_home(args.codex_home),
            check=args.check,
            force=args.force,
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
