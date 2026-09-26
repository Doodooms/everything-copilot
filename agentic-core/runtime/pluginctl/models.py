from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from expertise.errors import ExpertiseError, RegistryError
from expertise.ir import EffectiveIR, PackReference
from expertise.ontology import PACK_ID_PATTERN, VERSION_PATTERN, canonical_digest
from expertise.validator import load_json_no_duplicate_keys


_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class PluginControlError(ExpertiseError):
    """A bounded, deterministic plugin lifecycle operation failed."""


@dataclass(frozen=True)
class TrustedSource:
    reference: PackReference
    source_root: Path
    digest: str
    publisher: str
    source: str


class TrustedRegistry:
    """Explicit local source pins; membership is not installation or activation."""

    def __init__(self, entries: Iterable[TrustedSource] = ()):
        indexed: dict[PackReference, TrustedSource] = {}
        for entry in entries:
            if not isinstance(entry, TrustedSource):
                raise PluginControlError("trusted registry entries must be TrustedSource values")
            if entry.reference in indexed:
                raise RegistryError(
                    "duplicate trusted source for "
                    f"{entry.reference.id}@{entry.reference.version}"
                )
            self._validate_entry(entry)
            indexed[entry.reference] = entry
        self._entries: Mapping[PackReference, TrustedSource] = MappingProxyType(
            dict(sorted(indexed.items()))
        )

    @staticmethod
    def _validate_entry(entry: TrustedSource) -> None:
        if not isinstance(entry.reference, PackReference):
            raise PluginControlError("trusted source requires a PackReference")
        if not isinstance(entry.source_root, Path):
            raise PluginControlError("trusted source path must be a pathlib Path")
        if (
            not isinstance(entry.reference.id, str)
            or not PACK_ID_PATTERN.fullmatch(entry.reference.id)
            or len(entry.reference.id) > 64
        ):
            raise PluginControlError("trusted registry contains an invalid pack ID")
        if (
            not isinstance(entry.reference.version, str)
            or VERSION_PATTERN.fullmatch(entry.reference.version) is None
        ):
            raise PluginControlError("trusted registry contains an invalid pack version")
        if not entry.source_root.is_absolute():
            raise PluginControlError("trusted source path must be absolute")
        if not isinstance(entry.digest, str) or _DIGEST_PATTERN.fullmatch(entry.digest) is None:
            raise PluginControlError("trusted source digest must be lowercase SHA-256 hex")
        if not isinstance(entry.publisher, str) or not entry.publisher.strip():
            raise PluginControlError("trusted source publisher must be non-empty")
        if not isinstance(entry.source, str) or not entry.source.strip():
            raise PluginControlError("trusted source identity must be non-empty")

    @classmethod
    def from_file(cls, path: Path) -> "TrustedRegistry":
        path = Path(path)
        if path.is_symlink() or not path.is_file():
            raise PluginControlError(f"trusted registry is unavailable: {path}")
        try:
            document = load_json_no_duplicate_keys(path.read_bytes())
        except Exception as exc:
            raise PluginControlError(f"trusted registry is not valid JSON: {path}") from exc
        if not isinstance(document, dict) or set(document) != {"schema_version", "sources"}:
            raise PluginControlError("trusted registry must contain only schema_version and sources")
        if type(document.get("schema_version")) is not int or document["schema_version"] != 1:
            raise PluginControlError("trusted registry schema_version must be integer 1")
        sources = document.get("sources")
        if not isinstance(sources, list):
            raise PluginControlError("trusted registry sources must be an array")

        entries: list[TrustedSource] = []
        required = {"id", "version", "path", "digest", "publisher", "source"}
        for index, item in enumerate(sources):
            if not isinstance(item, dict) or set(item) != required:
                raise PluginControlError(
                    f"trusted registry sources[{index}] has invalid fields"
                )
            if any(not isinstance(item[key], str) for key in required):
                raise PluginControlError(
                    f"trusted registry sources[{index}] fields must be strings"
                )
            source_path = Path(item["path"])
            if not source_path.is_absolute():
                raise PluginControlError(
                    f"trusted registry sources[{index}].path must be absolute"
                )
            entries.append(
                TrustedSource(
                    reference=PackReference(item["id"], item["version"]),
                    source_root=source_path,
                    digest=item["digest"].removeprefix("sha256:"),
                    publisher=item["publisher"],
                    source=item["source"],
                )
            )
        return cls(entries)

    @property
    def references(self) -> tuple[PackReference, ...]:
        return tuple(self._entries)

    @property
    def entries(self) -> Mapping[PackReference, TrustedSource]:
        return self._entries

    def get(self, reference: PackReference) -> TrustedSource | None:
        return self._entries.get(reference)

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "sources": [
                {
                    "id": entry.reference.id,
                    "version": entry.reference.version,
                    "path": str(entry.source_root),
                    "digest": entry.digest,
                    "publisher": entry.publisher,
                    "source": entry.source,
                }
                for entry in self._entries.values()
            ],
        }


@dataclass(frozen=True)
class ActiveSet:
    packs: tuple[tuple[PackReference, str], ...] = ()
    capabilities: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "active_packs": [
                {
                    "id": reference.id,
                    "version": reference.version,
                    "digest": digest,
                }
                for reference, digest in self.packs
            ],
            "capabilities": list(self.capabilities),
        }


@dataclass(frozen=True)
class ManagedEffectiveIR:
    """Core-aware immutable composition around the shared Expertise EffectiveIR."""

    core: PackReference
    core_digest: str
    packs: EffectiveIR
    requested_capabilities: tuple[str, ...]
    target: str
    permission_projections: tuple[
        tuple[str, PackReference, str, tuple[str, ...]], ...
    ] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "core": {
                "id": self.core.id,
                "version": self.core.version,
                "content_digest": self.core_digest,
            },
            "packs": self.packs.as_dict(),
            "requested_capabilities": list(self.requested_capabilities),
            "target": self.target,
            "permission_projections": [
                {
                    "agent_id": agent_id,
                    "pack": {"id": reference.id, "version": reference.version},
                    "mcp_server": server_id,
                    "permissions": list(permissions),
                }
                for agent_id, reference, server_id, permissions in self.permission_projections
            ],
        }

    @property
    def fingerprint(self) -> str:
        return canonical_digest(self.as_dict())


@dataclass(frozen=True)
class EffectiveProfile:
    profile_hash: str
    artifact_digest: str
    target: str
    store_path: Path
    effective_ir: ManagedEffectiveIR
    runtime_state: str

    def as_dict(self) -> dict[str, object]:
        return {
            "profile_hash": self.profile_hash,
            "artifact_digest": self.artifact_digest,
            "target": self.target,
            "store_path": str(self.store_path),
            "runtime_state": self.runtime_state,
            "effective_ir": self.effective_ir.as_dict(),
        }
