"""Project a portable Agent Plugin into Claude Code's native plugin layout."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml

PROJECTOR_VERSION = "0.1.0"
_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", re.DOTALL)
_CAPABILITY = re.compile(r"\[\[capability:([a-z_/]+)\]\]")
_CLAUDE_CAPABILITIES = {
    "agent": ("Task", "ADAPTED"),
    "browser": ("browser capability", "UNSUPPORTED"),
    "execute": ("Bash", "ADAPTED"),
    "read": ("Read", "PRESERVED"),
    "search": ("Glob/Grep", "ADAPTED"),
    "search/usages": ("Grep", "ADAPTED"),
    "skill": ("Claude plugin skill", "ADAPTED"),
    "web": ("web capability", "UNSUPPORTED"),
    "question": ("question tool", "UNSUPPORTED"),
}


@dataclass(frozen=True)
class ClaudeProjection:
    files: dict[str, bytes]
    provenance: dict[str, Any]

    def write(self, output_root: Path, *, replace: bool = False) -> Path:
        """Materialize the plugin and a sibling provenance sidecar."""
        root = Path(output_root)
        if root.exists() and (root.is_symlink() or not root.is_dir()):
            raise ValueError("projection output must be a real directory")
        root.mkdir(parents=True, exist_ok=True)
        for relative, content in sorted(self.files.items()):
            destination = _safe_destination(root, relative)
            if destination.exists() and destination.is_symlink():
                raise ValueError(f"refusing to write through symlink: {destination}")
            if (
                destination.exists()
                and destination.read_bytes() != content
                and not replace
            ):
                raise ValueError(
                    f"refusing to replace differing projected file: {destination}"
                )
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.exists() or destination.read_bytes() != content:
                _atomic_write(destination, content)
        sidecar = root.with_name(f"{root.name}.projection.json")
        sidecar_content = (
            json.dumps(self.provenance, ensure_ascii=False, indent=2) + "\n"
        ).encode("utf-8")
        if sidecar.is_symlink():
            raise ValueError(f"refusing to write through provenance symlink: {sidecar}")
        if sidecar.exists() and sidecar.read_bytes() != sidecar_content and not replace:
            raise ValueError(
                f"refusing to replace differing provenance sidecar: {sidecar}"
            )
        if not sidecar.exists() or sidecar.read_bytes() != sidecar_content:
            sidecar.parent.mkdir(parents=True, exist_ok=True)
            _atomic_write(sidecar, sidecar_content)
        return sidecar


def project_claude_plugin(source_root: Path) -> ClaudeProjection:
    """Build a deterministic Claude plugin from an explicit portable source."""
    source = Path(source_root)
    if source.is_symlink() or not source.is_dir():
        raise ValueError("source_root must be a real plugin directory")
    manifest = _read_json(source / "plugin.json", "plugin.json")
    identity = _plugin_identity(manifest)
    files: dict[str, bytes] = {
        ".claude-plugin/plugin.json": _render_manifest(manifest),
    }
    capability_findings: dict[str, tuple[str, str]] = {}

    agents = source / "agents"
    if agents.is_symlink():
        raise ValueError("agent source directory must not be a symlink")
    if agents.is_dir():
        for path in sorted(agents.glob("*.md")):
            _add_agent(files, path, capability_findings)
    if not any(path.startswith("agents/") for path in files):
        raise ValueError("plugin must contain at least one canonical agent")

    skills = source / "skills"
    if skills.is_symlink():
        raise ValueError("skill source directory must not be a symlink")
    if skills.is_dir():
        _copy_tree(files, skills, "skills")
        link_findings = []
        for relative, content in files.items():
            if relative.startswith("skills/") and relative.endswith(".md"):
                if relative.endswith("/SKILL.md"):
                    _validate_skill(relative, content)
                link_findings.extend(
                    _validate_relative_skill_links(source, skills, relative, content)
                )
    else:
        link_findings = []

    mcp_path = source / "mcp.json"
    if mcp_path.is_file():
        files[".mcp.json"] = _render_mcp(source, mcp_path)

    source_git = _git_provenance(source)
    projector_git = _git_provenance(Path(__file__).resolve().parents[2])
    provenance: dict[str, Any] = {
        "source": {
            **identity,
            "sha256": _directory_digest(source),
            **source_git,
        },
        "target": "claude",
        "projector": {
            "name": "factory.projection.claude",
            "version": PROJECTOR_VERSION,
            **projector_git,
        },
        "parameters": {"layout": "claude-code-plugin", "hooks": "not emitted"},
        "artifact_sha256": _file_map_digest(files),
        "file_count": len(files),
        "resource_findings": link_findings,
        "capability_mappings": [
            {
                "capability": capability,
                "classification": result[1],
                "claude_form": result[0],
            }
            for capability, result in sorted(capability_findings.items())
        ],
        "adaptations": [
            {
                "classification": "ADAPTED",
                "item": "agent frontmatter",
                "detail": "Only canonical name and description are emitted; host execution metadata uses Claude defaults.",
            },
            {
                "classification": "ADAPTED",
                "item": "MCP local paths",
                "detail": "Packaged paths use CLAUDE_PLUGIN_ROOT; source cwd is omitted after local script paths are made plugin-relative.",
            },
            {
                "classification": "PRESERVED",
                "item": "canonical agent and skill bodies",
                "detail": "Agent instructions and recursive skill resources are copied without flattening.",
            },
            {
                "classification": "DROPPED",
                "item": "canonical plugin schema field",
                "detail": "The Agent Plugins $schema declaration is not part of Claude's native plugin manifest.",
            },
        ],
    }
    return ClaudeProjection(files, provenance)


def _add_agent(
    files: dict[str, bytes],
    path: Path,
    capability_findings: dict[str, tuple[str, str]],
) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"agent source must be a regular file: {path.name}")
    text = path.read_text(encoding="utf-8")
    match = _FRONTMATTER.match(text)
    if match is None:
        raise ValueError(f"agent source has invalid frontmatter: {path.name}")
    metadata = yaml.safe_load(match.group(1))
    if not isinstance(metadata, dict):
        raise TypeError(f"agent frontmatter must be a mapping: {path.name}")
    name, description = metadata.get("name"), metadata.get("description")
    if name != path.stem:
        raise ValueError(f"agent name does not match source path: {path.name}")
    if not isinstance(description, str) or not description.strip():
        raise ValueError(f"agent description is empty: {path.name}")

    def render_capability(item: re.Match[str]) -> str:
        capability = item.group(1)
        if capability not in _CLAUDE_CAPABILITIES:
            raise ValueError(
                f"unsupported capability marker in {path.name}: {capability}"
            )
        capability_findings[capability] = _CLAUDE_CAPABILITIES[capability]
        return _CLAUDE_CAPABILITIES[capability][0]

    body = _CAPABILITY.sub(render_capability, match.group(2))
    if "[[capability:" in body:
        raise ValueError(f"agent has an invalid capability marker: {path.name}")
    frontmatter = yaml.safe_dump(
        {"name": name, "description": description},
        allow_unicode=True,
        sort_keys=False,
    ).rstrip()
    files[f"agents/{path.name}"] = f"---\n{frontmatter}\n---\n{body}".encode()


def _render_manifest(source: dict[str, Any]) -> bytes:
    target = {
        key: source[key]
        for key in (
            "name",
            "description",
            "version",
            "author",
            "homepage",
            "repository",
            "license",
            "keywords",
        )
        if key in source
    }
    if isinstance(target.get("author"), dict):
        target["author"] = {
            key: value
            for key, value in target["author"].items()
            if key in {"name", "email", "url"}
        }
    return (json.dumps(target, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _render_mcp(source_root: Path, path: Path) -> bytes:
    config = _read_json(path, "mcp.json")
    servers = config.get("mcpServers")
    if not isinstance(servers, dict):
        raise TypeError("mcp.json must define an mcpServers object")
    projected: dict[str, Any] = {}
    for server_id, raw in sorted(servers.items()):
        if not isinstance(raw, dict):
            raise TypeError(f"MCP server must be an object: {server_id}")
        server = {key: value for key, value in raw.items() if key != "cwd"}
        if isinstance(raw.get("cwd"), str) and Path(raw["cwd"]).is_absolute():
            raise ValueError(
                f"MCP cwd must not be an absolute machine path: {server_id}"
            )
        if "command" in server and not isinstance(server["command"], str):
            raise TypeError(f"MCP command must be a string: {server_id}")
        if (
            isinstance(server.get("command"), str)
            and Path(server["command"]).is_absolute()
        ):
            raise ValueError(
                f"MCP command must not be an absolute machine path: {server_id}"
            )
        args = server.get("args", [])
        if not isinstance(args, list) or not all(
            isinstance(item, str) for item in args
        ):
            raise TypeError(f"MCP args must be a string array: {server_id}")
        server["args"] = [_project_local_arg(source_root, item) for item in args]
        if isinstance(raw.get("cwd"), str) and _is_plugin_root(raw["cwd"]):
            server["args"] = [
                _project_local_arg(source_root, item, force=True) for item in args
            ]
        projected[server_id] = server
    return (
        json.dumps({"mcpServers": projected}, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")


def _project_local_arg(source_root: Path, value: str, *, force: bool = False) -> str:
    candidate = Path(value)
    if candidate.is_absolute():
        raise ValueError("MCP args must not contain absolute machine paths")
    normalized = value.removeprefix("${PLUGIN_ROOT}/")
    path = source_root / normalized
    resolved_root = source_root.resolve()
    resolved_path = path.resolve()
    if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
        raise ValueError(f"MCP argument escapes the plugin root: {value}")
    if (
        force or value.startswith("${PLUGIN_ROOT}/") or path.exists()
    ) and path.is_file():
        return (
            "${CLAUDE_PLUGIN_ROOT}/"
            + resolved_path.relative_to(resolved_root).as_posix()
        )
    return value


def _is_plugin_root(value: str) -> bool:
    return value in {"${PLUGIN_ROOT}", "${CLAUDE_PLUGIN_ROOT}"}


def _validate_skill(relative: str, content: bytes) -> None:
    text = content.decode("utf-8")
    match = _FRONTMATTER.match(text)
    if match is None:
        raise ValueError(f"skill has invalid Claude frontmatter: {relative}")
    metadata = yaml.safe_load(match.group(1))
    if not isinstance(metadata, dict) or not isinstance(metadata.get("name"), str):
        raise TypeError(f"skill frontmatter is missing name: {relative}")
    if (
        not isinstance(metadata.get("description"), str)
        or not metadata["description"].strip()
    ):
        raise TypeError(f"skill frontmatter is missing description: {relative}")


def _validate_relative_skill_links(
    plugin_root: Path, skills_root: Path, relative: str, content: bytes
) -> list[dict[str, str]]:
    text = content.decode("utf-8")
    targets = re.findall(r"!?(?:\[[^\]]*\])\(([^)]+)\)", text)
    targets.extend(re.findall(r"^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)", text, re.MULTILINE))
    findings: list[dict[str, str]] = []
    for raw_target in targets:
        target = raw_target.strip().strip("<>").split(" ", 1)[0]
        parsed = urlsplit(target)
        if parsed.scheme or target.startswith("#") or not parsed.path:
            continue
        path = Path(unquote(parsed.path))
        if path.is_absolute():
            continue
        resolved = (
            plugin_root / "skills" / Path(relative).relative_to("skills").parent / path
        ).resolve()
        if skills_root.resolve() not in resolved.parents:
            raise ValueError(
                f"skill link escapes packaged skills: {relative} -> {target}"
            )
        if resolved.is_dir():
            findings.append(
                {
                    "classification": "PRESERVED",
                    "resource_type": "directory",
                    "source": relative,
                    "target": target,
                    "detail": "relative directory resource exists and its files are copied recursively",
                }
            )
        elif not resolved.is_file():
            findings.append(
                {
                    "classification": "UNSUPPORTED",
                    "resource_type": "missing",
                    "source": relative,
                    "target": target,
                    "detail": "relative skill resource is referenced but absent from the canonical package",
                }
            )
    return findings


def _copy_tree(files: dict[str, bytes], source: Path, target: str) -> None:
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"plugin resources must not contain symlinks: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"plugin resource must be a regular file: {path}")
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        relative = path.relative_to(source).as_posix()
        files[f"{target}/{relative}"] = path.read_bytes()


def _plugin_identity(manifest: dict[str, Any]) -> dict[str, str]:
    name, version = manifest.get("name"), manifest.get("version")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("plugin.json must provide a non-empty name")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("plugin.json must provide a non-empty version")
    return {"name": name, "version": version}


def _read_json(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} must be a regular file")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{label} must contain an object")
    return value


def _safe_destination(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe projection path: {relative}")
    destination = root / path
    if root.resolve() not in destination.resolve().parents:
        raise ValueError(f"projection path escapes output root: {relative}")
    return destination


def _directory_digest(root: Path) -> str:
    files: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"plugin source must not contain symlinks: {path}")
        if (
            path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix not in {".pyc", ".pyo"}
        ):
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    return _file_map_digest(files)


def _file_map_digest(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for name, content in sorted(files.items()):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def _git_provenance(root: Path) -> dict[str, Any]:
    base = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if base.returncode != 0:
        return {"git_commit": None, "git_base_commit": None, "dirty": None}
    base_commit = base.stdout.strip()
    status = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "status",
            "--porcelain",
            "--untracked-files=all",
            "--",
            ".",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if status.returncode != 0:
        return {"git_commit": None, "git_base_commit": base_commit, "dirty": None}
    dirty = bool(status.stdout.strip())
    return {
        "git_commit": None if dirty else base_commit,
        "git_base_commit": base_commit,
        "dirty": dirty,
    }


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
