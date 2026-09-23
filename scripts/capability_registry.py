from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


_CAPABILITY_PATTERN = re.compile(r"(?<!\w)capability:([A-Za-z0-9_.:/-]+)")


@dataclass
class CapabilityResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    data: dict[str, object] = field(default_factory=dict)

    def extend(self, other: "CapabilityResult") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.data.update(other.data)


def extract_capability_refs(text: str) -> list[str]:
    return [match.group(1) for match in _CAPABILITY_PATTERN.finditer(text)]


def find_workspace_root(start: Path) -> Path | None:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".github" / "runtime").is_dir() and (candidate / ".vscode" / "mcp.json").is_file():
            return candidate
    return None


def validate_skill_capability_refs(workspace_root: Path, text: str, source_name: str) -> CapabilityResult:
    result = CapabilityResult()
    refs = extract_capability_refs(text)
    result.data["capability_refs"] = refs
    registry = workspace_root / ".github" / "runtime"
    for ref in refs:
        if not any(path.is_file() and ref in path.read_text(encoding="utf-8") for path in registry.rglob("*")):
            result.errors.append(f"Unknown capability reference '{ref}' in {source_name}")
    return result
