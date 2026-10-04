"""Copilot agent projection over neutral Agent Plugin sources."""

from pathlib import Path

from .core_agents import AgentProjection, project_copilot_projection


def project(source_root: Path) -> AgentProjection:
    return project_copilot_projection(source_root)
