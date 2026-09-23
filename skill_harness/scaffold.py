from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .manifest import ManifestError, canonical_hash


@dataclass(frozen=True)
class ScaffoldConfig:
    architecture_id: str
    required_files: tuple[str, ...]
    mutable_markers: tuple[str, ...]

    @classmethod
    def from_file(cls, path: Path) -> "ScaffoldConfig":
        payload = json.loads(path.read_text(encoding="utf-8"))
        try:
            config = cls(
                architecture_id=payload["architecture_id"],
                required_files=tuple(payload["required_files"]),
                mutable_markers=tuple(payload["mutable_markers"]),
            )
        except (KeyError, TypeError) as exc:
            raise ManifestError(f"invalid canonical architecture config: {path}") from exc
        if not config.architecture_id or not config.required_files:
            raise ManifestError("canonical architecture must declare an id and files")
        return config

    def as_dict(self) -> dict[str, Any]:
        return {
            "architecture_id": self.architecture_id,
            "required_files": list(self.required_files),
            "mutable_markers": list(self.mutable_markers),
        }

    @property
    def config_hash(self) -> str:
        return canonical_hash(self.as_dict())


def scaffold_skill(
    destination: Path,
    config: ScaffoldConfig,
    original_spec: str,
) -> dict[str, Any]:
    destination.mkdir(parents=True, exist_ok=True)
    for relative in config.required_files:
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("", encoding="utf-8")
    original_path = destination / "references" / "original-spec.md"
    original_path.parent.mkdir(parents=True, exist_ok=True)
    if original_path.exists() and original_path.read_text(encoding="utf-8") != original_spec:
        raise ManifestError(f"original specification already differs: {original_path}")
    original_path.write_text(original_spec, encoding="utf-8")
    return {
        "architecture_id": config.architecture_id,
        "architecture_hash": config.config_hash,
        "created_files": sorted(config.required_files),
        "original_spec": original_path.as_posix(),
    }


def validate_scaffold(destination: Path, config: ScaffoldConfig) -> None:
    missing = [relative for relative in config.required_files if not (destination / relative).is_file()]
    if missing:
        raise ManifestError(f"scaffold is missing required files: {', '.join(missing)}")
    if not (destination / "references" / "original-spec.md").is_file():
        raise ManifestError("scaffold is missing references/original-spec.md")
