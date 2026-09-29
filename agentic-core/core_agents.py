"""Private canonical source and target metadata for the nine Core agents."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

CORE_AGENT_ROOT = Path(__file__).resolve().parent / "agents"
_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", re.DOTALL)
_CAPABILITY = re.compile(r"\[\[capability:([a-z_]+)\]\]")
_COPILOT_CAPABILITIES = {
    "agent": "#tool:agent",
    "browser": "#tool:browser",
    "execute": "#tool:execute",
    "read": "#tool:read",
    "search": "#tool:search",
    "skill": "#tool:skill",
    "web": "#tool:web",
    "question": "#tool:vscode/askQuestions",
}
_NEUTRAL_CAPABILITIES = {
    **{name: name for name in _COPILOT_CAPABILITIES if name != "question"},
    "question": "the question tool",
}


@dataclass(frozen=True)
class CoreAgent:
    name: str
    description: str
    instructions: str
    projections: dict[str, dict[str, Any]]

    def projection(self, target: str) -> dict[str, Any]:
        try:
            return self.projections[target]
        except KeyError as exc:
            raise ValueError(
                f"Core agent has no {target!r} projection: {self.name}"
            ) from exc

    def instructions_for(self, target: str) -> str:
        render_map = (
            _COPILOT_CAPABILITIES if target == "copilot" else _NEUTRAL_CAPABILITIES
        )

        def render(match: re.Match[str]) -> str:
            capability = match.group(1)
            try:
                return render_map[capability]
            except KeyError as exc:
                raise ValueError(
                    f"Core agent uses an unknown capability marker: {capability}"
                ) from exc

        instructions = _CAPABILITY.sub(render, self.instructions)
        if "[[capability:" in instructions:
            raise ValueError(
                f"Core agent has an invalid capability marker: {self.name}"
            )
        return instructions

    @property
    def capabilities(self) -> frozenset[str]:
        return frozenset(_CAPABILITY.findall(self.instructions))


def load_core_agents(source_root: Path = CORE_AGENT_ROOT) -> dict[str, CoreAgent]:
    """Load the private neutral source and explicit host projections."""
    root = Path(source_root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Core agent source root must be a real directory")
    profiles_path = root / "projections.json"
    if profiles_path.is_symlink() or not profiles_path.is_file():
        raise ValueError("Core agent projection metadata must be a regular file")
    profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
    if not isinstance(profiles, dict) or set(profiles) != {
        "copilot",
        "codex",
        "antigravity",
    }:
        raise ValueError(
            "Core agent projections must define Copilot, Codex, and Antigravity"
        )
    if any(not isinstance(profiles[target], dict) for target in profiles):
        raise ValueError("Core agent projection metadata must be target mappings")

    loaded: dict[str, CoreAgent] = {}
    for path in sorted(root.glob("*.md")):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Core agent source must be a regular file: {path.name}")
        match = _FRONTMATTER.match(path.read_text(encoding="utf-8"))
        if match is None:
            raise ValueError(f"Core agent source has invalid frontmatter: {path.name}")
        metadata = yaml.safe_load(match.group(1))
        if not isinstance(metadata, dict) or set(metadata) != {"name", "description"}:
            raise ValueError(f"Core agent source metadata is not neutral: {path.name}")
        name = path.stem
        if metadata["name"] != name:
            raise ValueError(f"Core agent name does not match source path: {path.name}")
        description = metadata["description"]
        instructions = match.group(2)
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"Core agent description is empty: {name}")
        if not instructions.strip():
            raise ValueError(f"Core agent instructions are empty: {name}")
        agent_profiles: dict[str, dict[str, Any]] = {}
        for target in ("copilot", "codex", "antigravity"):
            target_profiles = profiles[target]
            target_profile = target_profiles.get(name)
            if not isinstance(target_profile, dict):
                raise TypeError(f"Core agent is missing {target} metadata: {name}")
            agent_profiles[target] = target_profile
        loaded[name] = CoreAgent(name, description, instructions, agent_profiles)

    expected = set(loaded)
    if not expected:
        raise ValueError("Core agent source set is empty")
    if any(set(profiles[target]) != expected for target in profiles):
        raise ValueError("Core agent projection metadata must cover every source agent")
    return loaded


def load_core_projection_losses(
    source_root: Path = CORE_AGENT_ROOT,
) -> dict[str, tuple[str, ...]]:
    path = Path(source_root) / "projection-losses.json"
    if path.is_symlink() or not path.is_file():
        raise ValueError("Core agent projection losses must be a regular file")
    raw = json.loads(path.read_text(encoding="utf-8"))
    expected_targets = {"copilot", "codex", "antigravity"}
    if not isinstance(raw, dict) or set(raw) != expected_targets:
        raise ValueError("Core agent projection losses must define all three targets")
    losses: dict[str, tuple[str, ...]] = {}
    for target, values in raw.items():
        if not isinstance(values, list) or not all(
            isinstance(value, str) and value.strip() for value in values
        ):
            raise ValueError(f"Core agent projection losses are invalid: {target}")
        losses[target] = tuple(values)
    return losses


def render_copilot_agent(agent: CoreAgent) -> bytes:
    metadata = {
        "name": agent.name,
        "description": agent.description,
        **agent.projection("copilot"),
    }
    frontmatter = yaml.safe_dump(
        metadata, allow_unicode=True, default_flow_style=False, sort_keys=False
    ).rstrip()
    return f"---\n{frontmatter}\n---\n{agent.instructions_for('copilot')}".encode()


def render_neutral_agent(agent: CoreAgent, target: str) -> bytes:
    metadata = {"name": agent.name, "description": agent.description}
    frontmatter = yaml.safe_dump(
        metadata, allow_unicode=True, default_flow_style=False, sort_keys=False
    ).rstrip()
    return f"---\n{frontmatter}\n---\n{agent.instructions_for(target)}".encode()
