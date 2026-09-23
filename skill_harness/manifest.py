from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping


class ManifestError(ValueError):
    """Raised when a semantic or architecture manifest is invalid."""


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonicalize(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise ManifestError(f"Unsupported manifest value: {type(value).__name__}")


def canonical_json(value: Any) -> str:
    return json.dumps(_canonicalize(value), ensure_ascii=True, separators=(",", ":"))


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SemanticManifest:
    """The invariant semantic input shared by every architecture candidate."""

    name: str
    description: str
    fixtures: tuple[Mapping[str, Any], ...]
    workflow: tuple[Mapping[str, Any], ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name or self.name != self.name.lower() or " " in self.name:
            raise ManifestError("name must be a non-empty lowercase identifier")
        if not self.description.strip():
            raise ManifestError("description must not be empty")
        if not self.fixtures:
            raise ManifestError("at least one fixture is required")
        if not self.workflow:
            raise ManifestError("at least one workflow step is required")

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "fixtures": list(self.fixtures),
            "workflow": list(self.workflow),
            "metadata": dict(self.metadata),
        }

    @property
    def semantic_hash(self) -> str:
        return canonical_hash(self.as_dict())


@dataclass(frozen=True)
class ArchitectureVariant:
    """A user-supplied renderer declaration; no candidate is invented here."""

    id: str
    renderer: str
    config: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not self.id or not self.renderer:
            raise ManifestError("architecture id and renderer are required")

    def as_dict(self) -> dict[str, Any]:
        return {"id": self.id, "renderer": self.renderer, "config": dict(self.config)}


def assert_semantic_equivalence(
    expected: SemanticManifest, rendered: SemanticManifest
) -> None:
    if expected.semantic_hash != rendered.semantic_hash:
        raise ManifestError(
            "architecture rendered a different semantic manifest "
            f"(expected {expected.semantic_hash}, got {rendered.semantic_hash})"
        )
