from __future__ import annotations

from collections.abc import Iterable


class ExpertiseError(ValueError):
    """Base error for bounded, deterministic Expertise Pack operations."""


class PackValidationError(ExpertiseError):
    """A pack source has schema, reference, or content validation findings."""

    def __init__(self, diagnostics: Iterable[str]):
        self.diagnostics = tuple(sorted(set(diagnostics)))
        super().__init__("; ".join(self.diagnostics))


class RegistryError(ExpertiseError):
    """A local registry contains duplicate or inconsistent pack sources."""


class ResolutionError(ExpertiseError):
    """A declared capability cannot be resolved under the supplied approved sets."""


class TargetError(ExpertiseError):
    """A target cannot be compiled or safely materialized."""
