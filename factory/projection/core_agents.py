"""Host projections for Agent Plugin agents with explicit source roots."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from expertise.targets.codex import render_codex_fields

_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", re.DOTALL)
_CAPABILITY = re.compile(r"\[\[capability:([a-z_/]+)\]\]")
_COPILOT_CAPABILITIES = {
    "agent": "#tool:agent",
    "browser": "#tool:browser",
    "execute": "#tool:execute",
    "read": "#tool:read",
    "search/usages": "#tool:search/usages",
    "search": "#tool:search",
    "skill": "#tool:skill",
    "web": "#tool:web",
    "question": "#tool:vscode/askQuestions",
}


@dataclass(frozen=True)
class PluginAgent:
    name: str
    description: str
    instructions: str
    projections: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class AgentProjection:
    target: str
    files: dict[str, bytes]
    provenance: dict[str, Any]


def load_plugin_agents(source_root: Path) -> dict[str, PluginAgent]:
    """Load neutral root agents and their explicit target projection parameters."""
    root = Path(source_root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("plugin source root must be a real directory")
    agent_root = root / "agents"
    if agent_root.is_symlink():
        raise ValueError("agent source directory must not be a symlink")
    profiles_path = agent_root / "projections.json"
    if profiles_path.is_symlink() or not profiles_path.is_file():
        raise ValueError("agent projection parameters must be a regular file")
    profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
    targets = {"copilot", "codex", "antigravity"}
    if not isinstance(profiles, dict) or set(profiles) != targets:
        raise ValueError(
            "agent projection parameters must define all supported targets"
        )
    if any(not isinstance(profiles[target], dict) for target in targets):
        raise TypeError("agent projection parameters must be target mappings")

    result: dict[str, PluginAgent] = {}
    for path in sorted(agent_root.glob("*.md")):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"agent source must be a regular file: {path.name}")
        match = _FRONTMATTER.match(path.read_text(encoding="utf-8"))
        if match is None:
            raise ValueError(f"agent source has invalid frontmatter: {path.name}")
        metadata = yaml.safe_load(match.group(1))
        name = path.stem
        if not isinstance(metadata, dict) or set(metadata) != {"name", "description"}:
            raise ValueError(
                f"agent metadata must contain name and description: {name}"
            )
        if metadata["name"] != name:
            raise ValueError(f"agent name does not match source path: {path.name}")
        description, body = metadata["description"], match.group(2)
        if (
            not isinstance(description, str)
            or not description.strip()
            or not body.strip()
        ):
            raise ValueError(f"agent description and instructions are required: {name}")
        agent_profiles = {}
        for target in targets:
            target_profiles = profiles[target]
            profile = target_profiles.get(name)
            if not isinstance(profile, dict):
                raise TypeError(
                    f"agent is missing {target} projection parameters: {name}"
                )
            agent_profiles[target] = profile
        result[name] = PluginAgent(name, description, body, agent_profiles)
    if not result or any(set(profiles[target]) != set(result) for target in targets):
        raise ValueError(
            "projection parameters must cover the complete source agent set"
        )
    return result


def _instructions(agent: PluginAgent, target: str) -> str:
    capabilities = (
        _COPILOT_CAPABILITIES
        if target == "copilot"
        else {
            name: (
                "the question tool" if name == "question" else name.replace("_", " ")
            )
            for name in _COPILOT_CAPABILITIES
        }
    )

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in capabilities:
            raise ValueError(f"unknown capability marker in {agent.name}: {key}")
        return capabilities[key]

    result = _CAPABILITY.sub(replace, agent.instructions)
    if "[[capability:" in result:
        raise ValueError(f"invalid capability marker in {agent.name}")
    return result


def project_copilot_agents(source_root: Path) -> dict[str, bytes]:
    projected: dict[str, bytes] = {}
    for name, agent in load_plugin_agents(source_root).items():
        metadata = {
            "name": name,
            "description": agent.description,
            **agent.projections["copilot"],
        }
        frontmatter = yaml.safe_dump(
            metadata, allow_unicode=True, default_flow_style=False, sort_keys=False
        ).rstrip()
        projected[f"{name}.agent.md"] = (
            f"---\n{frontmatter}\n---\n{_instructions(agent, 'copilot')}".encode()
        )
    return projected


def project_codex_agents(source_root: Path) -> dict[str, bytes]:
    projected: dict[str, bytes] = {}
    for name, agent in load_plugin_agents(source_root).items():
        profile = agent.projections["codex"]
        projected[f"{name}.toml"] = render_codex_fields(
            name,
            agent.description,
            _instructions(agent, "codex"),
            model=profile.get("model"),
            reasoning_effort=profile.get("reasoning-effort"),
        )
    return projected


def project_copilot_projection(source_root: Path) -> AgentProjection:
    return _with_provenance(source_root, "copilot", project_copilot_agents)


def project_codex_projection(source_root: Path) -> AgentProjection:
    return _with_provenance(source_root, "codex", project_codex_agents)


def _with_provenance(source_root: Path, target: str, project) -> AgentProjection:
    root = Path(source_root)
    files = project(root)
    manifest_path = root / "plugin.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("plugin.json must be a regular file for projection provenance")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise TypeError("plugin.json must contain an object")
    identity = {key: manifest.get(key) for key in ("name", "version")}
    if any(
        not isinstance(value, str) or not value.strip() for value in identity.values()
    ):
        raise ValueError("plugin.json must provide source name and version")
    losses_path = root / "agents" / "projection-losses.json"
    if losses_path.is_file() and not losses_path.is_symlink():
        loss_data = json.loads(losses_path.read_text(encoding="utf-8"))
        losses = loss_data.get(target, []) if isinstance(loss_data, dict) else []
    else:
        losses = []
    if not isinstance(losses, list) or not all(
        isinstance(item, str) for item in losses
    ):
        raise ValueError(f"projection loss metadata is invalid for {target}")
    provenance = {
        "source": {
            **identity,
            "sha256": _file_digest(_source_files(root)),
            **_git_provenance(root),
        },
        "target": target,
        "projector": {
            "name": "factory.projection.core_agents",
            "version": "0.1.0",
            **_git_provenance(Path(__file__).resolve().parents[2]),
        },
        "parameters": {"projection": "agent-only", "source_root_explicit": True},
        "artifact_sha256": _file_digest(files),
        "file_count": len(files),
        "adaptations": [
            {"classification": "DROPPED", "detail": item} for item in losses
        ],
    }
    return AgentProjection(target, files, provenance)


def _source_files(root: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            relative = path.relative_to(root).as_posix()
            raise ValueError(f"plugin source must not contain symlinks: {relative}")
        if (
            path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix not in {".pyc", ".pyo"}
        ):
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    return files


def _file_digest(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for path, content in sorted(files.items()):
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def _git_provenance(root: Path) -> dict[str, Any]:
    commit = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if commit.returncode != 0:
        return {"git_commit": None, "git_base_commit": None, "dirty": None}
    base = commit.stdout.strip()
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
    dirty = bool(status.stdout.strip()) if status.returncode == 0 else None
    return {
        "git_commit": base if dirty is False else None,
        "git_base_commit": base,
        "dirty": dirty,
    }
