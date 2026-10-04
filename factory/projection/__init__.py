"""Deterministic target projections for portable Agent Plugins."""

from .claude import ClaudeProjection, project_claude_plugin

__all__ = ["ClaudeProjection", "project_claude_plugin"]
