from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomllib

from expertise.errors import ExpertiseError
from expertise.parser import parse_pack
from expertise.targets import CompiledTarget, compile_target
from expertise.targets.common import validate_target_files
from expertise.targets.validation import (
    validate_mcp_manifest,
    validate_plugin_manifest,
)
from expertise.validator import DuplicateJSONKeyError, load_json_no_duplicate_keys

from .errors import HarnessFactoryError
from .models import HARNESS_NAMES

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_AGENT_VALIDATOR = (
    _REPOSITORY_ROOT
    / "agentic-core/skills/plugin-engineering/references/create-agent/scripts/validate_agent.py"
)
_SKILL_VALIDATOR = (
    _REPOSITORY_ROOT
    / "agentic-core/skills/plugin-engineering/references/create-skill/scripts/validate.py"
)
_SOURCE_SKILL_VALIDATOR = Path(
    "skills/plugin-engineering/references/create-skill/scripts/validate.py"
)
_SOURCE_AGENT_VALIDATOR = Path(
    "skills/plugin-engineering/references/create-agent/scripts/validate_agent.py"
)
_IGNORED_COMPONENTS = {"__pycache__"}
_IGNORED_FILES = {".workflow-routes.tmp"}


@dataclass(frozen=True)
class ValidationResult:
    target: str
    source_kind: str
    source_digest: str
    files: tuple[str, ...]
    checks: tuple[dict[str, Any], ...]
    warnings: tuple[str, ...] = ()

    @property
    def status(self) -> str:
        return "passed"

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "target": self.target,
            "source_kind": self.source_kind,
            "source_digest": self.source_digest,
            "files": list(self.files),
            "checks": list(self.checks),
            "warnings": list(self.warnings),
        }


def validate_source(source_root: Path, target: str) -> ValidationResult:
    if target not in HARNESS_NAMES:
        raise HarnessFactoryError(f"unsupported harness target: {target!r}")
    root = Path(source_root)
    if root.is_symlink():
        raise HarnessFactoryError("plugin source root must not be a symlink")
    try:
        root = root.resolve(strict=True)
    except OSError as exc:
        raise HarnessFactoryError(
            f"plugin source root is unavailable: {source_root}"
        ) from exc
    if not root.is_dir():
        raise HarnessFactoryError("plugin source root must be a directory")

    if (root / "pack.yaml").is_file():
        try:
            source = parse_pack(root)
            artifact = compile_target(source, target)
        except ExpertiseError as exc:
            raise HarnessFactoryError(
                f"Expertise Pack conformance failed: {exc}"
            ) from exc
        _validate_artifact(artifact)
        return ValidationResult(
            target=target,
            source_kind="expertise-pack",
            source_digest=artifact.source_digest,
            files=tuple(sorted(artifact.files)),
            checks=(
                {"name": "pack-schema-and-source-snapshot", "passed": True},
                {"name": f"{target}-projection", "passed": True},
                {"name": "target-paths", "passed": True},
            ),
        )

    return _validate_plugin_directory(root, target)


def materialize_source(
    source_root: Path,
    target: str,
    *,
    workspace: Path,
    run_id: str,
) -> Path:
    if re.fullmatch(r"[0-9a-f]{32}", run_id) is None:
        raise HarnessFactoryError("run_id must be a lowercase 32-character UUID")
    raw_root = Path(source_root)
    if raw_root.is_symlink():
        raise HarnessFactoryError("plugin source root must not be a symlink")
    root = raw_root.resolve(strict=True)
    workspace_root = Path(workspace).resolve(strict=True)
    try:
        root.relative_to(workspace_root)
    except ValueError as exc:
        raise HarnessFactoryError(
            "smoke source must come from the pinned run workspace"
        ) from exc

    result = validate_source(root, target)
    if result.source_kind == "agent-plugin":
        return root

    source = parse_pack(root)
    artifact = compile_target(source, target)
    dist_root = workspace_root / "dist"
    output_root = dist_root / "harness-factory" / run_id / target
    _write_compiled_target(artifact, output_root, dist_root)
    return output_root


def _validate_plugin_directory(root: Path, target: str) -> ValidationResult:
    files = _read_plugin_files(root)
    try:
        files = dict(validate_target_files(files))
    except ExpertiseError as exc:
        raise HarnessFactoryError(f"plugin file layout is invalid: {exc}") from exc

    manifest_content = files.get("plugin.json")
    if manifest_content is None:
        raise HarnessFactoryError("plugin source is missing plugin.json")
    try:
        manifest = load_json_no_duplicate_keys(manifest_content)
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        DuplicateJSONKeyError,
        TypeError,
    ) as exc:
        raise HarnessFactoryError("plugin.json is not valid JSON") from exc
    try:
        validate_plugin_manifest(manifest)
    except ExpertiseError as exc:
        raise HarnessFactoryError(f"plugin manifest is invalid: {exc}") from exc

    checks: list[dict[str, Any]] = [
        {"name": "plugin-manifest", "passed": True},
        {"name": "safe-file-layout", "passed": True},
    ]
    mcp_content = files.get("mcp.json")
    if mcp_content is not None:
        try:
            mcp_manifest = load_json_no_duplicate_keys(mcp_content)
        except (
            OSError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            DuplicateJSONKeyError,
            TypeError,
        ) as exc:
            raise HarnessFactoryError("mcp.json is not valid JSON") from exc
        try:
            validate_mcp_manifest(mcp_manifest)
        except ExpertiseError as exc:
            raise HarnessFactoryError(f"MCP manifest is invalid: {exc}") from exc
        checks.append({"name": "mcp-manifest", "passed": True})

    skill_paths = sorted(
        path
        for path in files
        if path.startswith("skills/") and path.endswith("/SKILL.md")
    )
    warnings: list[str] = []
    skill_validator = _source_validator(root, _SOURCE_SKILL_VALIDATOR, _SKILL_VALIDATOR)
    for relative in skill_paths:
        skill_dir = root / Path(relative).parent
        result = _run_canonical_validator(
            skill_validator,
            ("--skill-dir", str(skill_dir)),
            label=f"skill {relative}",
        )
        warnings.extend(_warnings_from_validator(result))
    checks.append(
        {"name": "skill-manifests", "passed": True, "count": len(skill_paths)}
    )

    if target == "copilot":
        codex_agent_paths = sorted(
            path
            for path in files
            if path.startswith("codex-agents/") and path.endswith(".toml")
        )
        if codex_agent_paths:
            warnings.append(
                "Codex agent sidecars are not validated as Copilot agent definitions"
            )
        agent_paths = sorted(
            path
            for path in files
            if path.startswith("com.github.copilot/agents/")
            and path.endswith(".agent.md")
        )
        agent_validator = _source_validator(
            root, _SOURCE_AGENT_VALIDATOR, _AGENT_VALIDATOR
        )
        for relative in agent_paths:
            _run_canonical_validator(
                agent_validator,
                ("--agent-file", str(root / Path(relative))),
                label=f"agent {relative}",
            )
        checks.append(
            {
                "name": "copilot-agent-manifests",
                "passed": True,
                "count": len(agent_paths),
            }
        )
    else:
        copilot_agent_paths = sorted(
            path
            for path in files
            if path.startswith("com.github.copilot/agents/")
            and path.endswith(".agent.md")
        )
        if copilot_agent_paths:
            warnings.append(
                "Copilot agent definitions are not validated as Codex agent sidecars"
            )
        agent_paths = sorted(
            path
            for path in files
            if path.startswith("codex-agents/") and path.endswith(".toml")
        )
        for relative in agent_paths:
            _validate_codex_agent(relative, files[relative])
        checks.append(
            {"name": "codex-agent-sidecars", "passed": True, "count": len(agent_paths)}
        )

    return ValidationResult(
        target=target,
        source_kind="agent-plugin",
        source_digest=_digest_files(files),
        files=tuple(sorted(files)),
        checks=tuple(checks),
        warnings=tuple(warnings),
    )


def _raise_walk_error(error: OSError) -> None:
    raise HarnessFactoryError(f"could not enumerate plugin files: {error}") from error


def _source_validator(root: Path, relative_path: Path, fallback: Path) -> Path:
    source_validator = root / relative_path
    return source_validator if source_validator.is_file() else fallback


def _read_plugin_files(root: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for current, directories, filenames in os.walk(
        root,
        topdown=True,
        followlinks=False,
        onerror=_raise_walk_error,
    ):
        current_path = Path(current)
        for name in list(directories):
            directory = current_path / name
            if directory.is_symlink():
                raise HarnessFactoryError(
                    f"plugin must not contain symlink directories: {directory}"
                )
            if name in _IGNORED_COMPONENTS:
                directories.remove(name)
        for filename in filenames:
            path = current_path / filename
            if path.is_symlink():
                raise HarnessFactoryError(
                    f"plugin must not contain symlink files: {path}"
                )
            if filename in _IGNORED_FILES or path.suffix == ".pyc":
                continue
            relative = path.relative_to(root).as_posix()
            try:
                files[relative] = path.read_bytes()
            except OSError as exc:
                raise HarnessFactoryError(
                    f"could not read plugin file: {relative}"
                ) from exc
    return files


def _run_canonical_validator(
    script: Path,
    arguments: tuple[str, ...],
    *,
    label: str,
) -> subprocess.CompletedProcess[str]:
    if not script.is_file():
        raise HarnessFactoryError(f"canonical validator is unavailable: {script}")
    environment = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    for key in ("HOME", "SYSTEMROOT", "WINDIR", "LANG", "LC_ALL", "TMPDIR"):
        if key in os.environ:
            environment[key] = os.environ[key]
    try:
        completed = subprocess.run(
            [sys.executable, str(script), *arguments],
            cwd=_REPOSITORY_ROOT,
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            env=environment,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise HarnessFactoryError(
            f"{label} validation failed to execute: {type(exc).__name__}"
        ) from exc
    if completed.returncode != 0:
        details = (completed.stdout + completed.stderr).strip()
        raise HarnessFactoryError(f"{label} validation failed: {details}")
    return completed


def _warnings_from_validator(result: subprocess.CompletedProcess[str]) -> list[str]:
    return [
        line[4:].strip()
        for line in result.stdout.splitlines()
        if line.startswith("  - ")
    ]


def _validate_codex_agent(relative: str, content: bytes) -> None:
    try:
        parsed = tomllib.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise HarnessFactoryError(f"invalid Codex agent sidecar: {relative}") from exc
    if not isinstance(parsed.get("name"), str) or not parsed["name"].strip():
        raise HarnessFactoryError(f"Codex agent sidecar lacks name: {relative}")
    if (
        not isinstance(parsed.get("description"), str)
        or not parsed["description"].strip()
    ):
        raise HarnessFactoryError(f"Codex agent sidecar lacks description: {relative}")
    if (
        not isinstance(parsed.get("developer_instructions"), str)
        or not parsed["developer_instructions"].strip()
    ):
        raise HarnessFactoryError(
            f"Codex agent sidecar lacks developer_instructions: {relative}"
        )


def _validate_artifact(artifact: CompiledTarget) -> None:
    try:
        validate_target_files(artifact.files)
    except ExpertiseError as exc:
        raise HarnessFactoryError(
            f"compiled target contains unsafe files: {exc}"
        ) from exc


def _write_compiled_target(
    artifact: CompiledTarget,
    output_root: Path,
    dist_root: Path,
) -> None:
    try:
        from expertise.targets import materialize_target

        materialize_target(
            artifact,
            output_dir=output_root,
            dist_root=dist_root,
        )
    except ExpertiseError as exc:
        raise HarnessFactoryError(f"could not materialize target: {exc}") from exc
    except OSError as exc:
        raise HarnessFactoryError(f"could not materialize target: {exc}") from exc


def _digest_files(files: dict[str, bytes]) -> str:
    hasher = hashlib.sha256()
    for relative, content in sorted(files.items()):
        hasher.update(relative.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(len(content).to_bytes(8, "big"))
        hasher.update(content)
    return hasher.hexdigest()
