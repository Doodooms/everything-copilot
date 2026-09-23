from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .manifest import canonical_hash


class BenchmarkMutationError(ValueError):
    """Raised when frozen benchmark content no longer matches its lock."""


@dataclass(frozen=True)
class BenchmarkLock:
    benchmark_hash: str
    files: dict[str, str]

    def as_dict(self) -> dict[str, Any]:
        return {"benchmark_hash": self.benchmark_hash, "files": dict(sorted(self.files.items()))}


def _files_hash(root: Path, excluded: set[str] | None = None) -> dict[str, str]:
    excluded = excluded or set()
    files = {}
    for path in sorted(path for path in root.rglob("*") if path.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative in excluded:
            continue
        files[relative] = canonical_hash(path.read_bytes().decode("utf-8"))
    return files


def freeze_benchmark(root: Path, lock_path: Path) -> BenchmarkLock:
    excluded = {lock_path.relative_to(root).as_posix()} if lock_path.is_relative_to(root) else set()
    files = _files_hash(root, excluded)
    lock = BenchmarkLock(canonical_hash(files), files)
    lock_path.write_text(json.dumps(lock.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def verify_benchmark(root: Path, lock_path: Path) -> BenchmarkLock:
    payload = json.loads(lock_path.read_text(encoding="utf-8"))
    expected = BenchmarkLock(payload["benchmark_hash"], payload["files"])
    excluded = {lock_path.relative_to(root).as_posix()} if lock_path.is_relative_to(root) else set()
    actual_files = _files_hash(root, excluded)
    if actual_files != expected.files or canonical_hash(actual_files) != expected.benchmark_hash:
        raise BenchmarkMutationError(f"benchmark changed after freeze: {root}")
    return expected
