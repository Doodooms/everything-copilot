from __future__ import annotations

import re
from pathlib import Path

from .manifest import ManifestError
from .scaffold import ScaffoldConfig, validate_scaffold

_PLACEHOLDER_PATTERN = re.compile(r"<([A-Z][A-Z0-9_ -]+)>")


def validate_skill_structure(skill_dir: Path, config: ScaffoldConfig) -> None:
    """Validate immutable package structure before any model evaluation."""
    validate_scaffold(skill_dir, config)
    skill_file = skill_dir / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text:
        raise ManifestError("SKILL.md is missing YAML frontmatter")
    if f"name: {skill_dir.name}" not in text:
        raise ManifestError("SKILL.md name does not match its directory")
    unresolved = _PLACEHOLDER_PATTERN.findall(text)
    if unresolved:
        raise ManifestError(f"unresolved scaffold placeholders: {', '.join(unresolved)}")
    for marker in config.mutable_markers:
        if marker not in text:
            raise ManifestError(f"missing canonical mutable marker: {marker}")
