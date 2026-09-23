from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScaffoldConfig:
    architecture_id: str
    required_files: tuple[str, ...]
    mutable_markers: tuple[str, ...]

    @classmethod
    def from_file(cls, path: Path) -> "ScaffoldConfig":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            architecture_id=payload["architecture_id"],
            required_files=tuple(payload["required_files"]),
            mutable_markers=tuple(payload.get("mutable_markers", [])),
        )

    def digest(self) -> str:
        canonical = json.dumps(
            {
                "architecture_id": self.architecture_id,
                "required_files": list(self.required_files),
                "mutable_markers": list(self.mutable_markers),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def scaffold_skill(destination: Path, config: ScaffoldConfig, original_spec: str) -> dict[str, object]:
    destination.mkdir(parents=True, exist_ok=True)
    for relative in config.required_files:
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)
    original_path = destination / "references" / "original-spec.md"
    original_path.parent.mkdir(parents=True, exist_ok=True)
    if original_path.exists() and original_path.read_text(encoding="utf-8") not in ("", original_spec):
        raise ValueError(f"original specification already differs: {original_path}")
    original_path.write_text(original_spec, encoding="utf-8")
    return {
        "architecture_id": config.architecture_id,
        "architecture_hash": config.digest(),
        "created_files": sorted(config.required_files),
        "original_spec": original_path.as_posix(),
    }


def validate_scaffold(destination: Path, config: ScaffoldConfig) -> None:
    missing = [relative for relative in config.required_files if not (destination / relative).is_file()]
    if missing:
        raise ValueError(f"scaffold is missing required files: {', '.join(missing)}")
    if not (destination / "references" / "original-spec.md").is_file():
        raise ValueError("scaffold is missing references/original-spec.md")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a canonical skill scaffold without workspace imports.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--original-spec", type=Path, required=True)
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    config = ScaffoldConfig.from_file(args.config)
    summary = scaffold_skill(args.output, config, args.original_spec.read_text(encoding="utf-8"))
    if args.validate:
        validate_scaffold(args.output, config)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())