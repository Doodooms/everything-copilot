from __future__ import annotations

from pathlib import Path


class SentinelError(ValueError):
    """Raised when a routing sentinel cannot be safely managed."""


_SENTINEL_PREFIX = "<!-- skill-harness-routing-sentinel:"


def insert_sentinel(path: Path, event_id: str) -> str:
    content = path.read_text(encoding="utf-8")
    if _SENTINEL_PREFIX in content:
        raise SentinelError(f"sentinel already present in {path}")
    marker = f"{_SENTINEL_PREFIX}{event_id} -->\n"
    path.write_text(marker + content, encoding="utf-8")
    return marker


def remove_sentinel(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    filtered = [line for line in lines if not line.startswith(_SENTINEL_PREFIX)]
    path.write_text("".join(filtered), encoding="utf-8")


def count_sentinels(path: Path) -> int:
    return sum(
        line.startswith(_SENTINEL_PREFIX)
        for line in path.read_text(encoding="utf-8").splitlines()
    )
