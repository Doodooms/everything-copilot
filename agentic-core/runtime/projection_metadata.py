"""Small provenance helpers for the packaged Core projection commands."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path


def file_map_digest(
    files: Mapping[str, bytes], executable_files: frozenset[str] = frozenset()
) -> str:
    digest = hashlib.sha256()
    for relative, content in sorted(files.items()):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(b"x" if relative in executable_files else b"-")
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def plugin_tree_digest(plugin_root: Path) -> str:
    root = Path(plugin_root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"plugin root must be a real directory: {root}")

    files: dict[str, bytes] = {}
    executable: set[str] = set()
    for path in sorted(root.rglob("*")):
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.is_symlink():
            raise ValueError(f"plugin tree must not contain symlinks: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"plugin tree contains a non-regular file: {path}")
        relative = path.relative_to(root).as_posix()
        files[relative] = path.read_bytes()
        if path.stat().st_mode & 0o111:
            executable.add(relative)
    return file_map_digest(files, frozenset(executable))


def plugin_identity(plugin_root: Path) -> dict[str, str]:
    manifest_path = Path(plugin_root) / "plugin.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("plugin.json must be a regular file")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise TypeError("plugin.json must contain a JSON object")
    name = manifest.get("name")
    version = manifest.get("version")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("plugin.json must provide a non-empty name")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("plugin.json must provide a non-empty version")
    return {"name": name, "version": version}
