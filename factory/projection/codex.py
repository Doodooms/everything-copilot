"""Codex agent projection over neutral Agent Plugin sources."""

from pathlib import Path

from .core_agents import AgentProjection, project_codex_projection


def project(source_root: Path) -> AgentProjection:
    return project_codex_projection(source_root)
