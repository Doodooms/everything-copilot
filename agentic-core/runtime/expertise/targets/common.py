from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from ..errors import TargetError
from ..ir import PackReference, PackSource
from ..ontology import (
    AGENT_PLUGINS_VERSION,
    parse_agent_plugins_requirement,
    parse_version,
)


def ensure_supported_agent_plugins(source: PackSource) -> None:
    try:
        requirement, minimum = parse_agent_plugins_requirement(
            source.ir.compatibility.agent_plugins
        )
    except (TypeError, ValueError) as exc:
        raise TargetError(
            f"pack {source.ir.id!r} has an invalid Agent Plugins compatibility constraint"
        ) from exc
    if minimum > parse_version(AGENT_PLUGINS_VERSION):
        raise TargetError(
            f"pack {source.ir.id!r} requires Agent Plugins {requirement}, "
            f"but target supports {AGENT_PLUGINS_VERSION}"
        )


def validate_target_files(files: Mapping[str, bytes]) -> Mapping[str, bytes]:
    if not isinstance(files, Mapping):
        raise TargetError("target files must be a mapping")
    normalized: dict[str, bytes] = {}
    for path, content in sorted(files.items(), key=lambda item: str(item[0])):
        if not isinstance(path, str) or not path or path.startswith("/"):
            raise TargetError(f"target file path must be relative: {path!r}")
        parts = path.split("/")
        if (
            "\\" in path
            or ":" in path
            or any(
                part in {"", ".", ".."} or part.rstrip(" .") in {"", ".", ".."}
                for part in parts
            )
        ):
            raise TargetError(f"target file path is not safe: {path!r}")
        if ".github" in path.split("/"):
            raise TargetError(
                "target output must not materialize consumer .github content"
            )
        if not isinstance(content, bytes):
            raise TargetError(f"target file content must be bytes: {path}")
        if path in normalized:
            raise TargetError(f"duplicate target file path: {path}")
        normalized[path] = content
    return MappingProxyType(normalized)


@dataclass(frozen=True)
class CompiledTarget:
    target: str
    pack: PackReference
    source_digest: str
    files: Mapping[str, bytes]

    def __post_init__(self) -> None:
        if (
            not isinstance(self.source_digest, str)
            or len(self.source_digest) != 64
            or any(
                character not in "0123456789abcdef" for character in self.source_digest
            )
        ):
            raise TargetError(
                "target source digest must be a lowercase SHA-256 hex digest"
            )
        object.__setattr__(self, "files", validate_target_files(self.files))

    @classmethod
    def create(
        cls,
        target: str,
        pack: PackReference,
        files: Mapping[str, bytes],
        *,
        source_digest: str,
    ) -> CompiledTarget:
        return cls(target, pack, source_digest, files)

    @property
    def digest(self) -> str:
        hasher = hashlib.sha256()
        for path, content in sorted(self.files.items()):
            hasher.update(path.encode("utf-8"))
            hasher.update(b"\0")
            hasher.update(len(content).to_bytes(8, "big"))
            hasher.update(content)
        return hasher.hexdigest()

    def file_map(self) -> dict[str, bytes]:
        return dict(self.files)
