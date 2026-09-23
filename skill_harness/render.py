from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from .manifest import (
    ArchitectureVariant,
    ManifestError,
    SemanticManifest,
    assert_semantic_equivalence,
)

Renderer = Callable[[SemanticManifest, Mapping[str, Any]], SemanticManifest]


@dataclass(frozen=True)
class RenderedVariant:
    architecture: ArchitectureVariant
    manifest: SemanticManifest
    semantic_hash: str


class RendererRegistry:
    """Explicit registry for renderers supplied by the experiment owner."""

    def __init__(self) -> None:
        self._renderers: dict[str, Renderer] = {}

    def register(self, name: str, renderer: Renderer) -> None:
        if not name.strip():
            raise ManifestError("renderer name must not be empty")
        if name in self._renderers:
            raise ManifestError(f"renderer already registered: {name}")
        self._renderers[name] = renderer

    def render(
        self,
        architecture: ArchitectureVariant,
        semantic: SemanticManifest,
    ) -> RenderedVariant:
        try:
            renderer = self._renderers[architecture.renderer]
        except KeyError as exc:
            raise ManifestError(
                f"renderer is not registered: {architecture.renderer}"
            ) from exc
        rendered = renderer(semantic, architecture.config)
        if not isinstance(rendered, SemanticManifest):
            raise ManifestError("renderer must return SemanticManifest")
        assert_semantic_equivalence(semantic, rendered)
        return RenderedVariant(architecture, rendered, rendered.semantic_hash)
