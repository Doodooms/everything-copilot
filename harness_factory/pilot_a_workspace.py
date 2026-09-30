from __future__ import annotations

import os
import re
import shutil
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from expertise.errors import TargetError
from expertise.parser import parse_pack
from expertise.targets import compile_target
from expertise.targets.common import validate_target_files

from .errors import HarnessFactoryError

_PACK_ID = re.compile(r"^[a-z][a-z0-9-]*$")
_AGENT_ID = re.compile(r"^[a-z][a-z0-9-]*$")


@dataclass(frozen=True)
class PilotASeedRepository:
    """A local-only Git seed containing one generated Codex pack projection."""

    repository_root: Path
    revision: str
    pack_id: str
    source_digest: str
    projection_digest: str
    plugin_relative_path: str
    project_files: tuple[str, ...]


def create_pilot_a_seed_repository(
    pack_root: Path,
    seed_repository_root: Path,
) -> PilotASeedRepository:
    """Compile a canonical pack and commit only its Codex projection locally.

    The generated Agent Plugin is placed under the scratch project's local
    marketplace directory. Codex agent TOML sidecars are placed in the
    project-level ``.codex/agents`` directory expected by the Codex harness.
    The function deliberately creates no remote and never copies source files.
    """
    raw_pack_root = Path(pack_root)
    raw_seed_root = Path(seed_repository_root)
    if not raw_seed_root.is_absolute():
        raise HarnessFactoryError("Pilot A seed repository path must be absolute")
    if raw_seed_root.exists() or raw_seed_root.is_symlink():
        raise HarnessFactoryError(
            f"Pilot A seed repository destination already exists: {raw_seed_root}"
        )

    try:
        pack_source = parse_pack(raw_pack_root)
        artifact = compile_target(pack_source, "codex")
    except (OSError, TargetError, ValueError) as exc:
        raise HarnessFactoryError(
            f"could not compile Codex projection for Pilot A: {exc}"
        ) from exc

    if pack_source.ir.id != artifact.pack.id:
        raise HarnessFactoryError("compiled Codex projection pack identity changed")
    if not _PACK_ID.fullmatch(pack_source.ir.id):
        raise HarnessFactoryError("Pilot A pack ID is not a safe project path")
    if pack_source.ir.mcp_config is not None or pack_source.ir.mcp_servers:
        raise HarnessFactoryError("Pilot A local seed must not declare MCP servers")

    pack_path = pack_source.root.resolve(strict=True)
    seed_path = raw_seed_root.resolve(strict=False)
    source_repository = _source_repository_root(pack_path)
    if _paths_overlap(source_repository, seed_path):
        raise HarnessFactoryError(
            "Pilot A seed repository must be outside the canonical source repository"
        )

    plugin_relative_path = f".agents/plugins/{pack_source.ir.id}"
    project_files = _project_files(artifact.files, plugin_relative_path)
    if not project_files:
        raise HarnessFactoryError("Codex projection contains no project files")
    if any(_is_mcp_path(path) for path in project_files):
        raise HarnessFactoryError("Pilot A local seed must not contain MCP files")

    created = False
    try:
        raw_seed_root.mkdir(parents=True, exist_ok=False)
        created = True
        for relative, content in sorted(project_files.items()):
            target = raw_seed_root / PurePosixPath(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(content)

        _run_git(raw_seed_root, "init", "--quiet")
        _run_git(raw_seed_root, "add", "--all")
        _run_git(
            raw_seed_root,
            "-c",
            "user.name=Plugin Factory Pilot A",
            "-c",
            "user.email=pilot-a@localhost",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--quiet",
            "-m",
            f"Add generated {pack_source.ir.id} Codex projection",
        )

        expected_paths = set(project_files)
        tracked_paths = set(_run_git(raw_seed_root, "ls-files").splitlines())
        if tracked_paths != expected_paths:
            raise HarnessFactoryError(
                "Pilot A seed Git tree differs from the generated project files"
            )
        if _run_git(raw_seed_root, "remote"):
            raise HarnessFactoryError("Pilot A local seed unexpectedly has a remote")
        if _run_git(raw_seed_root, "status", "--porcelain"):
            raise HarnessFactoryError("Pilot A local seed is not clean after commit")

        return PilotASeedRepository(
            repository_root=raw_seed_root.resolve(strict=True),
            revision=_run_git(raw_seed_root, "rev-parse", "HEAD"),
            pack_id=pack_source.ir.id,
            source_digest=pack_source.ir.content_digest,
            projection_digest=artifact.digest,
            plugin_relative_path=plugin_relative_path,
            project_files=tuple(sorted(expected_paths)),
        )
    except (OSError, subprocess.SubprocessError) as exc:
        if created:
            shutil.rmtree(raw_seed_root, ignore_errors=True)
        raise HarnessFactoryError(
            f"could not create local Pilot A seed repository: {type(exc).__name__}"
        ) from exc
    except Exception:
        if created:
            shutil.rmtree(raw_seed_root, ignore_errors=True)
        raise


def _project_files(files: Mapping[str, bytes], plugin_path: str) -> dict[str, bytes]:
    try:
        validated = validate_target_files(files)
    except TargetError as exc:
        raise HarnessFactoryError("Codex projection contains an unsafe path") from exc

    projected: dict[str, bytes] = {}
    for source_path, content in validated.items():
        source_parts = PurePosixPath(source_path).parts
        if ".git" in source_parts:
            raise HarnessFactoryError("Codex projection cannot write Git metadata")
        if source_parts[0] == "codex-agents":
            if (
                len(source_parts) != 2
                or not source_parts[1].endswith(".toml")
                or not _AGENT_ID.fullmatch(source_parts[1][:-5])
            ):
                raise HarnessFactoryError(
                    f"invalid generated Codex agent sidecar: {source_path}"
                )
            target_path = f".codex/agents/{source_parts[1]}"
        else:
            target_path = f"{plugin_path}/{source_path}"
        if target_path in projected:
            raise HarnessFactoryError(f"Codex projection path collision: {target_path}")
        projected[target_path] = content
    return projected


def _is_mcp_path(path: str) -> bool:
    parts = PurePosixPath(path).parts
    return any(
        part.casefold() in {"mcp", "mcpservers", "mcp-servers"} for part in parts
    ) or PurePosixPath(path).name.casefold() in {
        "mcp.json",
        "mcp.yaml",
        "mcp.yml",
    }


def _paths_overlap(first: Path, second: Path) -> bool:
    return first == second or first in second.parents or second in first.parents


def _source_repository_root(pack_path: Path) -> Path:
    try:
        result = subprocess.run(
            ["git", "-C", str(pack_path), "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return pack_path
    if result.returncode != 0 or not result.stdout.strip():
        return pack_path
    return Path(result.stdout.strip()).resolve(strict=True)


def _run_git(repository: Path, *arguments: str) -> str:
    environment = os.environ.copy()
    environment["GIT_TERMINAL_PROMPT"] = "0"
    try:
        completed = subprocess.run(
            ["git", "-C", str(repository), *arguments],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            env=environment,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise HarnessFactoryError(
            f"local Pilot A Git command failed: {type(exc).__name__}"
        ) from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise HarnessFactoryError(
            f"local Pilot A Git command exited {completed.returncode}: {detail}"
        )
    return completed.stdout.strip()
