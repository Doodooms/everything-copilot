# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML>=6.0,<7"]
# ///
"""Project the installed Agentic Core agents into Codex's agents directory."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import tomllib

RUNTIME_ROOT = Path(__file__).resolve().parent
PLUGIN_ROOT = RUNTIME_ROOT.parent
sys.path[:0] = [str(RUNTIME_ROOT), str(PLUGIN_ROOT)]

from core_agents import load_core_agents
from projection_metadata import (
    file_map_digest,
    plugin_identity,
    plugin_tree_digest,
)

from expertise.targets.codex import render_codex_fields


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
    projected: dict[str, bytes] = {}
    for agent_id, agent in load_core_agents().items():
        filename = f"{agent_id}.toml"
        if filename in projected:
            raise ValueError(f"duplicate Codex agent output: {filename}")
        codex_profile = agent.projection("codex")
        content = render_codex_fields(
            agent.name,
            agent.description,
            agent.instructions_for("codex"),
            model=codex_profile.get("model"),
            reasoning_effort=codex_profile.get("reasoning-effort"),
        )
        try:
            role = tomllib.loads(content.decode("utf-8"))
        except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
            raise ValueError(f"invalid generated Codex role: {filename}") from exc
        if role.get("name") != agent_id:
            raise ValueError(f"generated role name does not match {filename}")
        projected[filename] = content
    if not projected:
        raise ValueError("Agentic Core source set is empty")
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


def _summary(
    status: str, codex_home: Path, projected: dict[str, bytes]
) -> dict[str, object]:
    identity = plugin_identity(PLUGIN_ROOT)
    return {
        "status": status,
        "target": "codex",
        "plugin": identity,
        "source_sha256": plugin_tree_digest(PLUGIN_ROOT),
        "artifact_sha256": file_map_digest(projected),
        "agent_count": len(projected),
        "agents": sorted(path.removesuffix(".toml") for path in projected),
        "output": str(codex_home / "agents"),
    }


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
            json.dumps(_summary("current", codex_home, projected), ensure_ascii=False)
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
    for filename, content in projected.items():
        path = agents_dir / filename
        if path.is_file() and path.read_bytes() == content:
            continue
        _atomic_write(path, content)
    print(json.dumps(_summary("projected", codex_home, projected), ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Project canonical Agentic Core agents into CODEX_HOME/agents. "
            "This command runs from the installed Agentic Core plugin directory."
        )
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        help="Codex home directory (defaults to CODEX_HOME or ~/.codex).",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="verify without writing")
    mode.add_argument("--force", action="store_true", help="replace conflicting files")
    args = parser.parse_args(argv)
    try:
        return _run(
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
