#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import functools
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, cast
from urllib.parse import unquote, urlparse

import ladybug as lb
import networkx as nx
import typer
from pydantic import AnyUrl
from graphify.cluster import cluster
from graphify.extract import _get_extractor, extract
from graphify.export import to_json
from graphify.security import sanitize_label
from graphify.serve import (
    _filter_blank_stdin,
    _find_node,
    _query_graph_text,
    _score_nodes,
    _strip_diacritics,
)

app = typer.Typer(add_completion=False, help="Atomic Graphify and GitNexus indexing helpers.")

DEFAULT_ROOT = Path(".")
DEFAULT_GRAPH_JSON = Path("graphify-out/graph.json")
DEFAULT_GRAPH_REPORT = Path("graphify-out/GRAPH_REPORT.md")
DEFAULT_GRAPH_DB = Path(".graphify/lbug")
DEFAULT_TEXT_INDEX_DB = Path(".graphify/docs-fts.db")
DEFAULT_GITNEXUS_META = Path(".gitnexus/meta.json")
DEFAULT_GITNEXUS_PENDING = Path(".gitnexus/pending-patch-files.json")
DEFAULT_HOOK_STATUS = Path(".graphify/hook-status.json")
DEFAULT_VALIDATE_FILE = Path("graphify-out/.atomic-index-validate.md")
NATIVE_EXTRACTOR = "native"
SEMANTIC_IMPORT_EXTRACTOR = "semantic-import"
GRAPHIFY_SCHEMA_VERSION = "1"
GITNEXUS_COMMAND = ["npx", "-y", "@duytransipher/gitnexus@latest"]
SKIPPED_INDEX_PARTS = {
    ".git",
    ".graphify",
    ".gitnexus",
    ".venv",
    "__pycache__",
    "graphify-out",
    "node_modules",
}
HOOK_MUTATING_TOOL_MARKERS = (
    "apply_patch",
    "create_file",
    "edit_notebook_file",
    "rename",
    "run_in_terminal",
    "send_to_terminal",
    "write",
)
HOOK_FULL_SCAN_TOOL_MARKERS = (
    "rename",
    "run_in_terminal",
    "send_to_terminal",
)
HOOK_PATH_FIELD_MARKERS = {
    "file",
    "filepath",
    "filepaths",
    "newpath",
    "new_path",
    "oldpath",
    "old_path",
    "path",
    "paths",
    "uri",
    "uris",
}
PATCH_FILE_PATTERN = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+?)(?:\s*->\s*.+)?$", re.MULTILINE)
GITNEXUS_MUTATION_PATTERN = re.compile(r"\bgit\s+(commit|merge|rebase|cherry-pick|pull)(?:\s|$)")


@dataclass(frozen=True)
class NativeSignatures:
    node_ids_by_file: dict[str, set[str]]
    edge_keys_by_file: dict[str, set[tuple[str, str, str, str, str]]]


@dataclass(frozen=True)
class GraphifyPatchResult:
    file_path: str
    deleted: bool
    semantic_refresh_needed: bool
    node_count: int
    edge_count: int
    elapsed_seconds: float


@dataclass(frozen=True)
class ValidationResult:
    concurrent_read_seconds: float
    patch_seconds: float
    successive_patch_seconds: list[float]
    final_nodes: int
    final_edges: int


@dataclass(frozen=True)
class GitNexusPendingState:
    incremental_supported: bool
    pending_files: list[str]
    errors: list[str]
    stale: bool
    message: str | None


@dataclass(frozen=True)
class ReconcileResult:
    patched_files: list[str]
    deleted_files: list[str]
    skipped_files: list[str]
    semantic_refresh_files: list[str]
    gitnexus_pending_files: list[str]
    gitnexus_incremental_supported: bool
    gitnexus_stale: bool
    gitnexus_message: str | None
    errors: list[str]


@contextlib.contextmanager
def pushd(path: Path) -> Iterator[None]:
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


@contextlib.contextmanager
def open_connection(db_path: Path, *, read_only: bool = False) -> Iterator[lb.Connection]:
    if not read_only:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    database = lb.Database(str(db_path), read_only=read_only)
    connection = lb.Connection(database)
    try:
        yield connection
    finally:
        connection.close()
        database.close()


@contextlib.contextmanager
def open_transaction(connection: lb.Connection) -> Iterator[None]:
    connection.execute("BEGIN TRANSACTION")
    try:
        yield
    except Exception:
        with contextlib.suppress(Exception):
            connection.execute("ROLLBACK")
        raise
    else:
        connection.execute("COMMIT")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def md5_file(path: Path) -> str:
    digest = hashlib.md5()  # nosec B324 - deterministic cache key, not security.
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_repo_path(path_like: str | Path, root: Path) -> str:
    candidate = Path(path_like)
    absolute = candidate if candidate.is_absolute() else (root / candidate)
    try:
        relative = absolute.resolve(strict=False).relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"Path must stay inside the repository root: {path_like}") from exc
    return relative.as_posix()


def normalize_optional_repo_path(path_like: Any, root: Path) -> str:
    if not path_like:
        return ""
    return normalize_repo_path(path_like, root)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        tmp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


@contextlib.contextmanager
def open_text_index(index_path: Path, *, read_only: bool = False) -> Iterator[sqlite3.Connection]:
    if not read_only:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        database = str(index_path)
        uri = False
    else:
        if not index_path.exists():
            raise FileNotFoundError(index_path)
        database = f"file:{index_path.resolve().as_posix()}?mode=ro"
        uri = True

    connection = sqlite3.connect(database, uri=uri)
    connection.row_factory = sqlite3.Row
    try:
        if not read_only:
            connection.execute("PRAGMA journal_mode=WAL")
        yield connection
    except Exception:
        if not read_only:
            connection.rollback()
        raise
    else:
        if not read_only:
            connection.commit()
    finally:
        connection.close()


def ensure_text_index_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        "CREATE TABLE IF NOT EXISTS DocState("
        "path TEXT PRIMARY KEY, "
        "content_hash TEXT NOT NULL, "
        "indexed_at TEXT NOT NULL"
        ")"
    )
    try:
        connection.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS DocSearch USING fts5("
            "path UNINDEXED, "
            "title, "
            "content, "
            "tokenize='unicode61'"
            ")"
        )
    except sqlite3.OperationalError as exc:
        if "fts5" in str(exc).lower() or "no such module" in str(exc).lower():
            raise RuntimeError("SQLite FTS5 is not available in the current Python sqlite3 build.") from exc
        raise


def extract_document_title(relative_path: str, content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip()
            if title:
                return title
    return Path(relative_path).name


def load_text_index_states(index_path: Path) -> dict[str, str]:
    if not index_path.exists():
        return {}
    try:
        with open_text_index(index_path, read_only=True) as connection:
            rows = connection.execute("SELECT path, content_hash FROM DocState").fetchall()
    except (FileNotFoundError, sqlite3.OperationalError):
        return {}
    return {str(row["path"]): str(row["content_hash"] or "") for row in rows}


def delete_text_document(connection: sqlite3.Connection, relative_path: str) -> None:
    connection.execute("DELETE FROM DocSearch WHERE path = ?", (relative_path,))
    connection.execute("DELETE FROM DocState WHERE path = ?", (relative_path,))


def upsert_text_document(
    connection: sqlite3.Connection,
    *,
    relative_path: str,
    content_hash: str,
    content: str,
    indexed_at: str,
) -> None:
    delete_text_document(connection, relative_path)
    connection.execute(
        "INSERT INTO DocSearch(path, title, content) VALUES (?, ?, ?)",
        (relative_path, extract_document_title(relative_path, content), content),
    )
    connection.execute(
        "INSERT INTO DocState(path, content_hash, indexed_at) VALUES (?, ?, ?) "
        "ON CONFLICT(path) DO UPDATE SET "
        "content_hash=excluded.content_hash, indexed_at=excluded.indexed_at",
        (relative_path, content_hash, indexed_at),
    )


def sync_text_index(root: Path, index_path: Path) -> tuple[int, int]:
    current_files = iter_current_indexable_files(root)
    known_states = load_text_index_states(index_path)
    changed_files = sorted(
        path for path, content_hash in current_files.items() if known_states.get(path) != content_hash
    )
    deleted_files = sorted(path for path in known_states if path not in current_files)

    if not changed_files and not deleted_files and index_path.exists():
        return len(current_files), 0

    timestamp = utc_now_iso()
    with open_text_index(index_path, read_only=False) as connection:
        ensure_text_index_schema(connection)
        for relative_path in deleted_files:
            delete_text_document(connection, relative_path)
        for relative_path in changed_files:
            absolute_path = root / relative_path
            content = absolute_path.read_text(encoding="utf-8", errors="replace")
            upsert_text_document(
                connection,
                relative_path=relative_path,
                content_hash=current_files[relative_path],
                content=content,
                indexed_at=timestamp,
            )
    return len(current_files), len(changed_files) + len(deleted_files)


def patch_text_index(root: Path, file_path: Path, *, deleted: bool) -> None:
    index_path = root / DEFAULT_TEXT_INDEX_DB
    relative_path = normalize_repo_path(file_path, root)
    with open_text_index(index_path, read_only=False) as connection:
        ensure_text_index_schema(connection)
        if deleted:
            delete_text_document(connection, relative_path)
            return
        absolute_path = root / relative_path
        content = absolute_path.read_text(encoding="utf-8", errors="replace")
        upsert_text_document(
            connection,
            relative_path=relative_path,
            content_hash=md5_file(absolute_path),
            content=content,
            indexed_at=utc_now_iso(),
        )


def compile_text_search_query(query: str) -> tuple[str, str]:
    normalized = query.strip()
    if not normalized:
        raise ValueError("query must not be blank")
    tokens = re.findall(r"[A-Za-z0-9_./-]+", normalized)
    if not tokens:
        raise ValueError("query must contain at least one searchable token")
    fallback = " OR ".join(f'"{token}"' for token in tokens)
    return normalized, fallback


def search_docs_impl(root: Path, query: str, *, limit: int = 5) -> list[dict[str, Any]]:
    normalized_limit = max(1, min(int(limit), 20))
    index_path = root / DEFAULT_TEXT_INDEX_DB
    sync_text_index(root, index_path)
    raw_query, fallback_query = compile_text_search_query(query)

    sql = (
        "SELECT path, title, snippet(DocSearch, 2, '[', ']', '...', 12) AS snippet, bm25(DocSearch) AS score "
        "FROM DocSearch WHERE DocSearch MATCH ? ORDER BY score ASC, path ASC LIMIT ?"
    )
    fallback_like = f"%{query.strip().lower()}%"
    with open_text_index(index_path, read_only=True) as connection:
        rows: list[sqlite3.Row] = []
        for candidate_query in (raw_query, fallback_query):
            try:
                rows = connection.execute(sql, (candidate_query, normalized_limit)).fetchall()
            except sqlite3.OperationalError:
                rows = []
            if rows:
                break
        if not rows:
            rows = connection.execute(
                "SELECT path, title, substr(content, 1, 240) AS snippet, 0.0 AS score "
                "FROM DocSearch WHERE lower(path) LIKE ? OR lower(title) LIKE ? OR lower(content) LIKE ? "
                "ORDER BY path ASC LIMIT ?",
                (fallback_like, fallback_like, fallback_like, normalized_limit),
            ).fetchall()

    results: list[dict[str, Any]] = []
    for row in rows:
        path = str(row["path"])
        results.append(
            {
                "path": path,
                "title": str(row["title"] or Path(path).name),
                "snippet": str(row["snippet"] or ""),
                "score": float(row["score"] or 0.0),
            }
        )
    return results


def render_search_docs_results(query: str, results: Sequence[dict[str, Any]]) -> str:
    if not results:
        return f"No text-search matches for '{sanitize_label(query)}'."
    lines = [f"Text-search matches for '{sanitize_label(query)}' ({len(results)}):"]
    for index, result in enumerate(results, 1):
        lines.append(f"  {index}. {sanitize_label(str(result['path']))}")
        snippet = str(result.get("snippet") or "").strip()
        if snippet:
            lines.append(f"     {sanitize_label(snippet)}")
    return "\n".join(lines)


def delete_file_if_exists(path: Path) -> None:
    with contextlib.suppress(FileNotFoundError):
        path.unlink()


def should_skip_repo_path(relative_path: str) -> bool:
    return any(part in SKIPPED_INDEX_PARTS for part in Path(relative_path).parts)


def is_graphify_supported_path(relative_path: str) -> bool:
    return bool(relative_path) and not should_skip_repo_path(relative_path) and _get_extractor(Path(relative_path)) is not None


def iter_current_indexable_files(root: Path) -> dict[str, str]:
    current: dict[str, str] = {}
    for current_root, dirnames, filenames in os.walk(root, topdown=True):
        dirnames[:] = [name for name in dirnames if name not in SKIPPED_INDEX_PARTS]
        current_root_path = Path(current_root)
        for filename in filenames:
            absolute_path = current_root_path / filename
            if not absolute_path.is_file():
                continue
            relative_path = absolute_path.relative_to(root).as_posix()
            if not is_graphify_supported_path(relative_path):
                continue
            current[relative_path] = md5_file(absolute_path)
    return current


def load_graphify_file_states(db_path: Path) -> dict[str, dict[str, Any]]:
    if not db_path.exists():
        return {}
    with open_connection(db_path, read_only=True) as connection:
        rows = read_rows(
            connection,
            "MATCH (f:FileState) RETURN f.path, f.content_hash, f.semantic_refresh_needed, f.last_indexed_at",
        )
    state: dict[str, dict[str, Any]] = {}
    for path, content_hash, semantic_refresh_needed, last_indexed_at in rows:
        if not path:
            continue
        state[str(path)] = {
            "content_hash": str(content_hash or ""),
            "semantic_refresh_needed": bool(semantic_refresh_needed),
            "last_indexed_at": str(last_indexed_at or ""),
        }
    return state


def compute_graphify_full_deltas(root: Path, known_states: dict[str, dict[str, Any]]) -> tuple[list[str], list[str]]:
    current_files = iter_current_indexable_files(root)
    changed = sorted(
        path
        for path, content_hash in current_files.items()
        if known_states.get(path, {}).get("content_hash") != content_hash
    )
    deleted = sorted(path for path in known_states if path not in current_files and is_graphify_supported_path(path))
    return changed, deleted


def load_pending_paths(path: Path) -> list[str]:
    if not path.exists():
        return []
    try:
        payload = load_json(path)
    except json.JSONDecodeError:
        return []
    pending = payload.get("pending_files", [])
    if not isinstance(pending, list):
        return []
    return sorted({str(item) for item in pending if isinstance(item, str) and item})


def save_pending_paths(path: Path, pending_files: Sequence[str]) -> None:
    normalized = sorted({str(item) for item in pending_files if item})
    if not normalized:
        delete_file_if_exists(path)
        return
    write_json_atomic(
        path,
        {
            "updated_at": utc_now_iso(),
            "pending_files": normalized,
        },
    )


def tool_name_from_payload(payload: dict[str, Any]) -> str:
    value = payload.get("tool_name")
    if isinstance(value, str) and value:
        return value
    value = payload.get("toolName")
    return value if isinstance(value, str) else ""


def tool_input_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("tool_input")
    if isinstance(value, dict):
        return value
    value = payload.get("toolInput")
    return value if isinstance(value, dict) else {}


def tool_response_from_payload(payload: dict[str, Any]) -> Any:
    response = payload.get("tool_response")
    if response is not None:
        return response
    return payload.get("tool_output")


def tool_response_indicates_success(payload: dict[str, Any]) -> bool:
    response = tool_response_from_payload(payload)
    if isinstance(response, dict):
        for key in ("exit_code", "exitCode", "code"):
            value = response.get(key)
            if isinstance(value, int):
                return value == 0
        success = response.get("success")
        if isinstance(success, bool):
            return success
        status = response.get("status")
        if isinstance(status, str):
            lowered = status.lower()
            if lowered in {"failed", "error"}:
                return False
            if lowered in {"success", "succeeded", "ok", "completed"}:
                return True
    return True


def is_command_execution_tool(tool_name: str) -> bool:
    lowered = tool_name.lower()
    return "terminal" in lowered or lowered in {"bash", "shell", "run_in_terminal", "send_to_terminal"}


def extract_tool_command(tool_input: Any) -> str:
    if not isinstance(tool_input, dict):
        return ""
    command = tool_input.get("command")
    return command if isinstance(command, str) else ""


def load_gitnexus_meta(root: Path) -> tuple[str, bool]:
    meta_path = root / DEFAULT_GITNEXUS_META
    if not meta_path.exists():
        return "", False
    try:
        payload = load_json(meta_path)
    except json.JSONDecodeError:
        return "", False

    last_commit = payload.get("lastCommit")
    stats = payload.get("stats")
    embeddings = stats.get("embeddings") if isinstance(stats, dict) else 0
    had_embeddings = isinstance(embeddings, (int, float)) and embeddings > 0
    return (last_commit if isinstance(last_commit, str) else "", had_embeddings)


def current_git_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def gitnexus_changed_paths_since_commit(root: Path, last_commit: str, current_head: str) -> list[str]:
    commands: list[list[str]] = []
    if last_commit:
        commands.append(["git", "diff", "--name-only", "--diff-filter=ACDMRTUXB", f"{last_commit}..{current_head}"])
    commands.append(["git", "show", "--pretty=", "--name-only", "--diff-filter=ACDMRTUXB", current_head])

    for command in commands:
        result = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            continue
        paths = [
            normalized
            for normalized in (try_normalize_hook_path(line, root) for line in result.stdout.splitlines())
            if normalized and not should_skip_repo_path(normalized)
        ]
        if paths:
            return sorted(set(paths))
    return []


def render_gitnexus_analyze_command(*, had_embeddings: bool) -> str:
    command_parts = [*GITNEXUS_COMMAND, "analyze"]
    if had_embeddings:
        command_parts.append("--embeddings")
    return " ".join(command_parts)


def compute_gitnexus_staleness(root: Path) -> tuple[bool, list[str], str | None]:
    current_head = current_git_head(root)
    if not current_head:
        return False, [], None

    last_commit, had_embeddings = load_gitnexus_meta(root)
    if current_head == last_commit:
        return False, [], None

    changed_paths = gitnexus_changed_paths_since_commit(root, last_commit, current_head)
    message = (
        "GitNexus index is stale "
        f"(last indexed: {last_commit[:7] if last_commit else 'never'}). "
        f"Run `{render_gitnexus_analyze_command(had_embeddings=had_embeddings)}` to update the knowledge graph."
    )
    return True, changed_paths, message


def extract_gitnexus_post_tool_use_state(root: Path, payload: dict[str, Any]) -> tuple[bool, list[str], str | None]:
    tool_name = tool_name_from_payload(payload)
    if not is_command_execution_tool(tool_name) or not tool_response_indicates_success(payload):
        return False, [], None

    command = extract_tool_command(tool_input_from_payload(payload))
    if not command or not GITNEXUS_MUTATION_PATTERN.search(command):
        return False, [], None

    return compute_gitnexus_staleness(root)


def write_hook_status(root: Path, result: ReconcileResult) -> None:
    write_json_atomic(
        root / DEFAULT_HOOK_STATUS,
        {
            "updated_at": utc_now_iso(),
            "patched_files": result.patched_files,
            "deleted_files": result.deleted_files,
            "skipped_files": result.skipped_files,
            "semantic_refresh_files": result.semantic_refresh_files,
            "gitnexus_pending_files": result.gitnexus_pending_files,
            "gitnexus_incremental_supported": result.gitnexus_incremental_supported,
            "gitnexus_stale": result.gitnexus_stale,
            "gitnexus_message": result.gitnexus_message,
            "errors": result.errors,
        },
    )


def load_hook_status(root: Path) -> dict[str, Any]:
    path = root / DEFAULT_HOOK_STATUS
    if not path.exists():
        return {}
    try:
        return load_json(path)
    except json.JSONDecodeError:
        return {}


def try_normalize_hook_path(raw_value: str, root: Path) -> str | None:
    candidate = raw_value.strip()
    if not candidate or "\n" in candidate or "\r" in candidate:
        return None
    parsed = urlparse(candidate)
    if parsed.scheme:
        candidate = unquote(parsed.path)
    try:
        return normalize_repo_path(candidate, root)
    except ValueError:
        return None


def collect_hook_paths(root: Path, value: Any, key_hint: str | None = None) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            found.update(collect_hook_paths(root, child, key))
        return found
    if isinstance(value, list):
        for child in value:
            found.update(collect_hook_paths(root, child, key_hint))
        return found
    if not isinstance(value, str) or key_hint is None:
        return found
    lowered = key_hint.replace("-", "_").lower()
    if lowered not in HOOK_PATH_FIELD_MARKERS and not lowered.endswith("path") and not lowered.endswith("paths") and not lowered.endswith("uri") and not lowered.endswith("uris"):
        return found
    normalized = try_normalize_hook_path(value, root)
    if normalized:
        found.add(normalized)
    return found


def extract_patch_paths_from_input(patch_text: str, root: Path) -> set[str]:
    found: set[str] = set()
    for raw_path in PATCH_FILE_PATTERN.findall(patch_text):
        normalized = try_normalize_hook_path(raw_path, root)
        if normalized:
            found.add(normalized)
    return found


def tool_likely_mutates_workspace(tool_name: str) -> bool:
    lowered = tool_name.lower()
    return any(marker in lowered for marker in HOOK_MUTATING_TOOL_MARKERS)


def tool_requires_full_scan(tool_name: str) -> bool:
    lowered = tool_name.lower()
    return any(marker in lowered for marker in HOOK_FULL_SCAN_TOOL_MARKERS)


def extract_candidate_paths_from_tool_use(root: Path, tool_name: str, tool_input: Any) -> tuple[list[str], bool]:
    candidates: set[str] = set()
    if isinstance(tool_input, dict):
        if "apply_patch" in tool_name.lower() and isinstance(tool_input.get("input"), str):
            candidates.update(extract_patch_paths_from_input(str(tool_input["input"]), root))
        candidates.update(collect_hook_paths(root, tool_input))
    return sorted(candidates), tool_requires_full_scan(tool_name)


def update_gitnexus_pending_state(
    root: Path,
    touched_paths: Sequence[str],
    *,
    stale_paths: Sequence[str] = (),
    stale_message: str | None = None,
) -> GitNexusPendingState:
    pending_path = root / DEFAULT_GITNEXUS_PENDING
    pending = set(load_pending_paths(pending_path))
    errors: list[str] = []
    incremental_supported = gitnexus_incremental_supported(GITNEXUS_COMMAND)
    touched = sorted({path for path in touched_paths if path and not should_skip_repo_path(path)})
    stale_candidates = sorted({path for path in stale_paths if path and not should_skip_repo_path(path)})
    patch_targets = sorted(set(touched) | set(stale_candidates))
    message = stale_message

    if patch_targets:
        if incremental_supported:
            code = patch_gitnexus_impl(root, Path(patch_targets[0]), quiet=True)
            if code == 0:
                pending.clear()
                stale, _, refreshed_message = compute_gitnexus_staleness(root)
                message = refreshed_message if stale else None
            else:
                pending.update(patch_targets)
                errors.append(f"GitNexus incremental patch failed with exit code {code}.")
        else:
            pending.update(patch_targets)

    save_pending_paths(pending_path, sorted(pending))
    return GitNexusPendingState(
        incremental_supported=incremental_supported,
        pending_files=sorted(pending),
        errors=errors,
        stale=bool(message or pending),
        message=message,
    )


def render_reconcile_summary(result: ReconcileResult) -> str:
    parts = [
        f"patched={len(result.patched_files)}",
        f"deleted={len(result.deleted_files)}",
        f"skipped={len(result.skipped_files)}",
        f"semantic_refresh_needed={len(result.semantic_refresh_files)}",
        f"gitnexus_pending={len(result.gitnexus_pending_files)}",
        f"gitnexus_incremental_supported={str(result.gitnexus_incremental_supported).lower()}",
        f"gitnexus_stale={str(result.gitnexus_stale).lower()}",
    ]
    if result.errors:
        parts.append(f"errors={len(result.errors)}")
    return "Reconciled graphs: " + ", ".join(parts)


def reconcile_graphs_impl(
    *,
    root: Path,
    db_path: Path,
    graph_json_path: Path,
    candidate_paths: Sequence[str] | None = None,
    force_full_scan: bool = False,
    gitnexus_stale_paths: Sequence[str] | None = None,
    gitnexus_stale_message: str | None = None,
) -> ReconcileResult:
    patched_files: list[str] = []
    deleted_files: list[str] = []
    skipped_files: list[str] = []
    semantic_refresh_files: list[str] = []
    errors: list[str] = []
    normalized_candidates = sorted({normalize_repo_path(path, root) for path in (candidate_paths or [])})

    graphify_available = db_path.exists() or graph_json_path.exists()
    known_states: dict[str, dict[str, Any]] = {}
    changed_paths: set[str] = set()
    removed_paths: set[str] = set()

    if graphify_available:
        try:
            bootstrap_db_if_needed(root, db_path, graph_json_path)
            known_states = load_graphify_file_states(db_path)
        except Exception as exc:
            errors.append(f"Could not load Graphify state: {exc}")
            graphify_available = False

    for candidate in normalized_candidates:
        if should_skip_repo_path(candidate):
            skipped_files.append(candidate)
            continue
        absolute_path = root / candidate
        if absolute_path.exists():
            if not is_graphify_supported_path(candidate):
                skipped_files.append(candidate)
                continue
            if not graphify_available or known_states.get(candidate, {}).get("content_hash") != md5_file(absolute_path):
                changed_paths.add(candidate)
        elif candidate in known_states:
            removed_paths.add(candidate)

    if graphify_available and force_full_scan:
        try:
            full_changed, full_deleted = compute_graphify_full_deltas(root, known_states)
            changed_paths.update(full_changed)
            removed_paths.update(full_deleted)
        except Exception as exc:
            errors.append(f"Could not compute Graphify delta scan: {exc}")

    if graphify_available:
        for candidate in sorted(changed_paths):
            try:
                result = patch_graphify_impl(
                    root=root,
                    file_path=root / candidate,
                    db_path=db_path,
                    graph_json_path=graph_json_path,
                    deleted=False,
                )
            except Exception as exc:
                errors.append(f"Graphify patch failed for {candidate}: {exc}")
                continue
            patched_files.append(candidate)
            if result.semantic_refresh_needed:
                semantic_refresh_files.append(candidate)

        for candidate in sorted(removed_paths):
            try:
                patch_graphify_impl(
                    root=root,
                    file_path=root / candidate,
                    db_path=db_path,
                    graph_json_path=graph_json_path,
                    deleted=True,
                )
            except Exception as exc:
                errors.append(f"Graphify delete patch failed for {candidate}: {exc}")
                continue
            deleted_files.append(candidate)
    elif changed_paths or removed_paths or force_full_scan:
        errors.append("Graphify state is missing; run /graphify . or migrate-graphify before automatic patching.")

    touched_paths = sorted(changed_paths | removed_paths)
    gitnexus_state = update_gitnexus_pending_state(
        root,
        touched_paths,
        stale_paths=gitnexus_stale_paths or (),
        stale_message=gitnexus_stale_message,
    )
    errors.extend(gitnexus_state.errors)

    result = ReconcileResult(
        patched_files=patched_files,
        deleted_files=deleted_files,
        skipped_files=sorted(set(skipped_files)),
        semantic_refresh_files=sorted(set(semantic_refresh_files)),
        gitnexus_pending_files=gitnexus_state.pending_files,
        gitnexus_incremental_supported=gitnexus_state.incremental_supported,
        gitnexus_stale=gitnexus_state.stale,
        gitnexus_message=gitnexus_state.message,
        errors=errors,
    )
    write_hook_status(root, result)
    return result


def build_hook_response(result: ReconcileResult) -> dict[str, Any]:
    response: dict[str, Any] = {"continue": True}
    if result.errors:
        response["systemMessage"] = "; ".join(result.errors[:2])
    return response


def build_post_tool_use_response(result: ReconcileResult) -> dict[str, Any]:
    response = build_hook_response(result)
    if result.gitnexus_message:
        response["hookSpecificOutput"] = {
            "hookEventName": "PostToolUse",
            "additionalContext": result.gitnexus_message,
        }
    return response


def emit_hook_response(result: ReconcileResult) -> None:
    typer.echo(json.dumps(build_hook_response(result)))


def emit_post_tool_use_response(result: ReconcileResult) -> None:
    typer.echo(json.dumps(build_post_tool_use_response(result)))


def read_hook_payload() -> dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def graph_patch_status_impl(root: Path, db_path: Path, graph_json_path: Path) -> dict[str, Any]:
    gitnexus_stale, _, gitnexus_message = compute_gitnexus_staleness(root)
    pending_files = load_pending_paths(root / DEFAULT_GITNEXUS_PENDING)
    text_index_path = root / DEFAULT_TEXT_INDEX_DB
    status: dict[str, Any] = {
        "graphify_db_exists": db_path.exists(),
        "graphify_json_exists": graph_json_path.exists(),
        "text_index_exists": text_index_path.exists(),
        "text_indexed_files": 0,
        "indexed_files": 0,
        "semantic_refresh_needed": 0,
        "nodes": 0,
        "edges": 0,
        "gitnexus_incremental_supported": gitnexus_incremental_supported(GITNEXUS_COMMAND),
        "gitnexus_pending_files": pending_files,
        "gitnexus_stale": gitnexus_stale or bool(pending_files),
        "gitnexus_message": gitnexus_message,
        "last_hook": load_hook_status(root),
    }
    status["text_indexed_files"] = len(load_text_index_states(text_index_path))
    if db_path.exists():
        with open_connection(db_path, read_only=True) as connection:
            status["indexed_files"] = int(read_scalar(connection, "MATCH (f:FileState) RETURN count(f)") or 0)
            status["semantic_refresh_needed"] = int(
                read_scalar(
                    connection,
                    "MATCH (f:FileState) WHERE f.semantic_refresh_needed = true RETURN count(f)",
                )
                or 0
            )
        graph = load_graph_from_db(db_path)
        status["nodes"] = graph.number_of_nodes()
        status["edges"] = graph.number_of_edges()
    return status


def query_rows(connection: lb.Connection, query: str, parameters: dict[str, Any] | None = None) -> list[Any]:
    result = connection.execute(query, parameters=parameters or {})
    query_result = result[-1] if isinstance(result, list) else result
    rows = getattr(query_result, "get_all", None)
    if rows is None:
        return cast(list[Any], query_result)
    return cast(list[Any], rows())


def read_scalar(connection: lb.Connection, query: str, parameters: dict[str, Any] | None = None) -> Any:
    rows = query_rows(connection, query, parameters)
    if not rows:
        return None
    return rows[0][0]


def read_rows(connection: lb.Connection, query: str, parameters: dict[str, Any] | None = None) -> list[list[Any]]:
    rows = query_rows(connection, query, parameters)
    return [cast(list[Any], row) for row in rows]


def ensure_schema(connection: lb.Connection) -> None:
    connection.execute(
        "CREATE NODE TABLE IF NOT EXISTS Meta(key STRING PRIMARY KEY, value STRING)"
    )
    connection.execute(
        "CREATE NODE TABLE IF NOT EXISTS FileState("
        "path STRING PRIMARY KEY, "
        "content_hash STRING, "
        "extractor STRING, "
        "semantic_refresh_needed BOOL, "
        "last_indexed_at STRING"
        ")"
    )
    connection.execute(
        "CREATE NODE TABLE IF NOT EXISTS Entity("
        "id STRING PRIMARY KEY, "
        "label STRING, "
        "file_type STRING, "
        "source_file STRING, "
        "source_location STRING, "
        "source_url STRING, "
        "author STRING, "
        "contributor STRING, "
        "norm_label STRING, "
        "community INT64, "
        "community_name STRING, "
        "raw_json STRING, "
        "updated_at STRING"
        ")"
    )
    connection.execute(
        "CREATE REL TABLE IF NOT EXISTS MENTIONS("
        "FROM FileState TO Entity, "
        "extractor STRING, "
        "confidence STRING, "
        "origin_file STRING, "
        "raw_json STRING"
        ")"
    )
    connection.execute(
        "CREATE REL TABLE IF NOT EXISTS RELATES("
        "FROM Entity TO Entity, "
        "relation STRING, "
        "confidence STRING, "
        "confidence_score DOUBLE, "
        "source_file STRING, "
        "source_location STRING, "
        "weight DOUBLE, "
        "context STRING, "
        "origin_file STRING, "
        "extractor STRING, "
        "raw_json STRING"
        ")"
    )


def upsert_meta(connection: lb.Connection, key: str, value: str) -> None:
    exists = bool(read_scalar(connection, "MATCH (m:Meta {key:$key}) RETURN count(m)", {"key": key}))
    parameters = {"key": key, "value": value}
    if exists:
        connection.execute("MATCH (m:Meta {key:$key}) SET m.value = $value", parameters=parameters)
    else:
        connection.execute("CREATE (:Meta {key:$key, value:$value})", parameters=parameters)


def upsert_file_state(
    connection: lb.Connection,
    *,
    path: str,
    content_hash: str,
    extractor: str,
    semantic_refresh_needed: bool,
    last_indexed_at: str,
) -> None:
    exists = bool(read_scalar(connection, "MATCH (f:FileState {path:$path}) RETURN count(f)", {"path": path}))
    parameters = {
        "path": path,
        "content_hash": content_hash,
        "extractor": extractor,
        "semantic_refresh_needed": semantic_refresh_needed,
        "last_indexed_at": last_indexed_at,
    }
    if exists:
        connection.execute(
            "MATCH (f:FileState {path:$path}) "
            "SET f.content_hash = $content_hash, "
            "    f.extractor = $extractor, "
            "    f.semantic_refresh_needed = $semantic_refresh_needed, "
            "    f.last_indexed_at = $last_indexed_at",
            parameters=parameters,
        )
    else:
        connection.execute(
            "CREATE (:FileState {"
            "path:$path, "
            "content_hash:$content_hash, "
            "extractor:$extractor, "
            "semantic_refresh_needed:$semantic_refresh_needed, "
            "last_indexed_at:$last_indexed_at"
            "})",
            parameters=parameters,
        )


def normalize_node(node: dict[str, Any], root: Path) -> dict[str, Any]:
    normalized = dict(node)
    normalized["id"] = str(normalized["id"])
    normalized["label"] = str(normalized.get("label", normalized["id"]))
    normalized["file_type"] = str(normalized.get("file_type", ""))
    normalized["source_file"] = normalize_optional_repo_path(normalized.get("source_file"), root)
    normalized["source_location"] = str(normalized.get("source_location", ""))
    normalized["source_url"] = str(normalized.get("source_url", ""))
    normalized["author"] = str(normalized.get("author", ""))
    normalized["contributor"] = str(normalized.get("contributor", ""))
    normalized["norm_label"] = str(
        normalized.get("norm_label") or _strip_diacritics(normalized["label"]).lower()
    )
    community = normalized.get("community")
    normalized["community"] = int(community) if community not in (None, "") else -1
    normalized["community_name"] = str(normalized.get("community_name", ""))
    return normalized


def normalize_edge(edge: dict[str, Any], root: Path) -> dict[str, Any]:
    normalized = dict(edge)
    normalized["source"] = str(normalized["source"])
    normalized["target"] = str(normalized["target"])
    normalized["relation"] = str(normalized.get("relation", ""))
    normalized["confidence"] = str(normalized.get("confidence", "EXTRACTED"))
    score = normalized.get("confidence_score")
    if score in (None, ""):
        confidence = normalized["confidence"]
        score = 1.0 if confidence == "EXTRACTED" else 0.7 if confidence == "INFERRED" else 0.4
    normalized["confidence_score"] = float(score)
    normalized["source_file"] = normalize_optional_repo_path(normalized.get("source_file"), root)
    normalized["source_location"] = str(normalized.get("source_location", ""))
    weight = normalized.get("weight")
    normalized["weight"] = float(weight) if weight not in (None, "") else 1.0
    normalized["context"] = str(normalized.get("context", ""))
    if "_src" not in normalized:
        normalized["_src"] = normalized["source"]
    if "_tgt" not in normalized:
        normalized["_tgt"] = normalized["target"]
    return normalized


def upsert_entity(connection: lb.Connection, node: dict[str, Any], *, updated_at: str) -> None:
    payload = normalize_node(node, Path.cwd())
    raw_json = json.dumps(payload, sort_keys=True)
    exists = bool(read_scalar(connection, "MATCH (e:Entity {id:$id}) RETURN count(e)", {"id": payload["id"]}))
    parameters = {
        "id": payload["id"],
        "label": payload["label"],
        "file_type": payload["file_type"],
        "source_file": payload["source_file"],
        "source_location": payload["source_location"],
        "source_url": payload["source_url"],
        "author": payload["author"],
        "contributor": payload["contributor"],
        "norm_label": payload["norm_label"],
        "community": payload["community"],
        "community_name": payload["community_name"],
        "raw_json": raw_json,
        "updated_at": updated_at,
    }
    if exists:
        connection.execute(
            "MATCH (e:Entity {id:$id}) "
            "SET e.label = $label, "
            "    e.file_type = $file_type, "
            "    e.source_file = $source_file, "
            "    e.source_location = $source_location, "
            "    e.source_url = $source_url, "
            "    e.author = $author, "
            "    e.contributor = $contributor, "
            "    e.norm_label = $norm_label, "
            "    e.community = $community, "
            "    e.community_name = $community_name, "
            "    e.raw_json = $raw_json, "
            "    e.updated_at = $updated_at",
            parameters=parameters,
        )
    else:
        connection.execute(
            "CREATE (:Entity {"
            "id:$id, "
            "label:$label, "
            "file_type:$file_type, "
            "source_file:$source_file, "
            "source_location:$source_location, "
            "source_url:$source_url, "
            "author:$author, "
            "contributor:$contributor, "
            "norm_label:$norm_label, "
            "community:$community, "
            "community_name:$community_name, "
            "raw_json:$raw_json, "
            "updated_at:$updated_at"
            "})",
            parameters=parameters,
        )


def create_mention(
    connection: lb.Connection,
    *,
    file_path: str,
    entity_id: str,
    extractor: str,
    confidence: str,
    raw_json: str,
) -> None:
    connection.execute(
        "MATCH (f:FileState {path:$file_path}), (e:Entity {id:$entity_id}) "
        "CREATE (f)-[:MENTIONS {"
        "extractor:$extractor, "
        "confidence:$confidence, "
        "origin_file:$file_path, "
        "raw_json:$raw_json"
        "}]->(e)",
        parameters={
            "file_path": file_path,
            "entity_id": entity_id,
            "extractor": extractor,
            "confidence": confidence,
            "raw_json": raw_json,
        },
    )


def create_relation(
    connection: lb.Connection,
    edge: dict[str, Any],
    *,
    extractor: str,
    origin_file: str,
) -> None:
    payload = normalize_edge(edge, Path.cwd())
    connection.execute(
        "MATCH (src:Entity {id:$source}), (dst:Entity {id:$target}) "
        "CREATE (src)-[:RELATES {"
        "relation:$relation, "
        "confidence:$confidence, "
        "confidence_score:$confidence_score, "
        "source_file:$source_file, "
        "source_location:$source_location, "
        "weight:$weight, "
        "context:$context, "
        "origin_file:$origin_file, "
        "extractor:$extractor, "
        "raw_json:$raw_json"
        "}]->(dst)",
        parameters={
            "source": payload["source"],
            "target": payload["target"],
            "relation": payload["relation"],
            "confidence": payload["confidence"],
            "confidence_score": payload["confidence_score"],
            "source_file": payload["source_file"],
            "source_location": payload["source_location"],
            "weight": payload["weight"],
            "context": payload["context"],
            "origin_file": origin_file,
            "extractor": extractor,
            "raw_json": json.dumps(payload, sort_keys=True),
        },
    )


def extractable_source_files(graph_data: dict[str, Any], root: Path) -> list[str]:
    seen: set[str] = set()
    for bucket_name in ("nodes", "links", "edges"):
        for item in graph_data.get(bucket_name, []):
            source_file = normalize_optional_repo_path(item.get("source_file"), root)
            if not source_file or source_file in seen:
                continue
            source_path = root / source_file
            if source_path.exists() and _get_extractor(Path(source_file)) is not None:
                seen.add(source_file)
    return sorted(seen)


def edge_identity(edge: dict[str, Any]) -> tuple[str, str, str, str, str]:
    normalized = normalize_edge(edge, Path.cwd())
    return (
        normalized["source"],
        normalized["target"],
        normalized["relation"],
        normalized["source_location"],
        normalized["context"],
    )


def build_native_signatures(root: Path, graph_data: dict[str, Any]) -> NativeSignatures:
    node_ids_by_file: dict[str, set[str]] = {}
    edge_keys_by_file: dict[str, set[tuple[str, str, str, str, str]]] = {}
    for source_file in extractable_source_files(graph_data, root):
        try:
            with pushd(root):
                result = extract([Path(source_file)], cache_root=root)
        except Exception:
            continue
        node_ids_by_file[source_file] = {
            str(node.get("id"))
            for node in result.get("nodes", [])
            if str(node.get("id", ""))
        }
        edge_keys_by_file[source_file] = {edge_identity(edge) for edge in result.get("edges", [])}
    return NativeSignatures(node_ids_by_file=node_ids_by_file, edge_keys_by_file=edge_keys_by_file)


def classify_node_extractor(node: dict[str, Any], signatures: NativeSignatures, root: Path) -> str:
    source_file = normalize_optional_repo_path(node.get("source_file"), root)
    if source_file and str(node.get("id")) in signatures.node_ids_by_file.get(source_file, set()):
        return NATIVE_EXTRACTOR
    return SEMANTIC_IMPORT_EXTRACTOR


def classify_edge_extractor(edge: dict[str, Any], signatures: NativeSignatures, root: Path) -> str:
    source_file = normalize_optional_repo_path(edge.get("source_file"), root)
    with pushd(root):
        key = edge_identity(edge)
    if source_file and key in signatures.edge_keys_by_file.get(source_file, set()):
        return NATIVE_EXTRACTOR
    return SEMANTIC_IMPORT_EXTRACTOR


def reset_database(db_path: Path) -> None:
    for suffix in ("", ".wal", ".shm"):
        candidate = Path(str(db_path) + suffix)
        if candidate.exists():
            if candidate.is_dir():
                shutil.rmtree(candidate)
            else:
                candidate.unlink()


def bootstrap_db_if_needed(root: Path, db_path: Path, graph_json_path: Path) -> None:
    if db_path.exists():
        return
    if not graph_json_path.exists():
        raise FileNotFoundError(
            f"Graphify DB not found at {db_path} and graph.json not found at {graph_json_path}."
        )
    migrate_graphify_impl(root=root, graph_json_path=graph_json_path, db_path=db_path, force=False)


def migrate_graphify_impl(*, root: Path, graph_json_path: Path, db_path: Path, force: bool) -> tuple[int, int]:
    if force:
        reset_database(db_path)
    elif db_path.exists():
        raise RuntimeError(f"Graphify DB already exists at {db_path}. Pass --force to recreate it.")

    graph_data = load_json(graph_json_path)
    signatures = build_native_signatures(root, graph_data)
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("links", graph_data.get("edges", []))
    source_files = {
        normalize_optional_repo_path(item.get("source_file"), root)
        for item in [*nodes, *edges]
        if normalize_optional_repo_path(item.get("source_file"), root)
    }
    timestamp = utc_now_iso()

    with pushd(root):
        with open_connection(db_path, read_only=False) as connection:
            ensure_schema(connection)
            with open_transaction(connection):
                upsert_meta(connection, "schema_version", GRAPHIFY_SCHEMA_VERSION)
                upsert_meta(connection, "hyperedges_json", json.dumps(graph_data.get("hyperedges", []), sort_keys=True))
                upsert_meta(connection, "source_graph_json", str(graph_json_path))
                if graph_data.get("built_at_commit"):
                    upsert_meta(connection, "built_at_commit", str(graph_data["built_at_commit"]))

                for source_file in sorted(source_files):
                    source_path = root / source_file
                    content_hash = md5_file(source_path) if source_path.exists() else ""
                    upsert_file_state(
                        connection,
                        path=source_file,
                        content_hash=content_hash,
                        extractor="graphify-import",
                        semantic_refresh_needed=False,
                        last_indexed_at=timestamp,
                    )

                for raw_node in nodes:
                    node = normalize_node(raw_node, root)
                    upsert_entity(connection, node, updated_at=timestamp)
                    source_file = node["source_file"]
                    if source_file:
                        create_mention(
                            connection,
                            file_path=source_file,
                            entity_id=node["id"],
                            extractor=classify_node_extractor(node, signatures, root),
                            confidence=str(node.get("confidence", "EXTRACTED")),
                            raw_json=json.dumps(node, sort_keys=True),
                        )

                for raw_edge in edges:
                    edge = normalize_edge(raw_edge, root)
                    create_relation(
                        connection,
                        edge,
                        extractor=classify_edge_extractor(edge, signatures, root),
                        origin_file=edge["source_file"],
                    )

    sync_text_index(root, root / DEFAULT_TEXT_INDEX_DB)

    return len(nodes), len(edges)


def load_hyperedges(connection: lb.Connection) -> list[dict[str, Any]]:
    raw = read_scalar(connection, "MATCH (m:Meta {key:$key}) RETURN m.value", {"key": "hyperedges_json"})
    if not raw:
        return []
    try:
        return json.loads(str(raw))
    except json.JSONDecodeError:
        return []


def load_graph_from_db(db_path: Path) -> nx.Graph:
    with open_connection(db_path, read_only=True) as connection:
        graph = nx.Graph()
        for row in read_rows(connection, "MATCH (e:Entity) RETURN e.id, e.raw_json"):
            entity_id = str(row[0])
            raw_json = str(row[1] or "{}")
            try:
                data = json.loads(raw_json)
            except json.JSONDecodeError:
                data = {"id": entity_id, "label": entity_id}
            data["id"] = entity_id
            data.setdefault("label", entity_id)
            data.setdefault("norm_label", _strip_diacritics(data.get("label", entity_id)).lower())
            graph.add_node(entity_id, **data)

        for row in read_rows(connection, "MATCH (src:Entity)-[r:RELATES]->(dst:Entity) RETURN src.id, dst.id, r.raw_json"):
            source_id = str(row[0])
            target_id = str(row[1])
            raw_json = str(row[2] or "{}")
            try:
                data = json.loads(raw_json)
            except json.JSONDecodeError:
                data = {"source": source_id, "target": target_id}
            data.setdefault("source", source_id)
            data.setdefault("target", target_id)
            graph.add_edge(source_id, target_id, **data)

        graph.graph["hyperedges"] = load_hyperedges(connection)
        return graph


def load_graph_snapshot(db_path: Path) -> tuple[nx.Graph, dict[int, list[str]]]:
    graph = load_graph_from_db(db_path)
    communities = cluster(graph) if graph.number_of_nodes() else {}
    for community_id, node_ids in communities.items():
        for node_id in node_ids:
            graph.nodes[node_id]["community"] = community_id
    return graph, communities


def export_graph_json(db_path: Path, json_path: Path) -> tuple[int, int]:
    graph, communities = load_graph_snapshot(db_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=json_path.name + ".", suffix=".tmp", dir=json_path.parent)
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        if not to_json(graph, communities, str(tmp_path), force=True):
            raise RuntimeError("Graphify export refused to overwrite the JSON mirror.")
        os.replace(tmp_path, json_path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
    return graph.number_of_nodes(), graph.number_of_edges()


def relation_count(connection: lb.Connection, file_path: str, extractor: str) -> int:
    return int(
        read_scalar(
            connection,
            "MATCH (:Entity)-[r:RELATES]->(:Entity) "
            "WHERE r.origin_file = $file_path AND r.extractor = $extractor "
            "RETURN count(r)",
            {"file_path": file_path, "extractor": extractor},
        )
        or 0
    )


def mention_count(connection: lb.Connection, file_path: str, extractor: str) -> int:
    return int(
        read_scalar(
            connection,
            "MATCH (:FileState {path:$file_path})-[m:MENTIONS]->(:Entity) "
            "WHERE m.extractor = $extractor "
            "RETURN count(m)",
            {"file_path": file_path, "extractor": extractor},
        )
        or 0
    )


def collect_native_entity_ids(connection: lb.Connection, file_path: str, extractor: str) -> set[str]:
    rows = read_rows(
        connection,
        "MATCH (:FileState {path:$file_path})-[m:MENTIONS]->(e:Entity) "
        "WHERE m.extractor = $extractor "
        "RETURN e.id",
        {"file_path": file_path, "extractor": extractor},
    )
    return {str(row[0]) for row in rows}


def delete_mentions(connection: lb.Connection, file_path: str, extractor: str) -> None:
    connection.execute(
        "MATCH (:FileState {path:$file_path})-[m:MENTIONS]->(:Entity) "
        "WHERE m.extractor = $extractor DELETE m",
        parameters={"file_path": file_path, "extractor": extractor},
    )


def delete_relations(connection: lb.Connection, file_path: str, extractor: str) -> None:
    connection.execute(
        "MATCH (:Entity)-[r:RELATES]->(:Entity) "
        "WHERE r.origin_file = $file_path AND r.extractor = $extractor DELETE r",
        parameters={"file_path": file_path, "extractor": extractor},
    )


def entity_reference_count(connection: lb.Connection, entity_id: str) -> int:
    mentions = int(
        read_scalar(
            connection,
            "MATCH (:FileState)-[m:MENTIONS]->(e:Entity {id:$entity_id}) RETURN count(m)",
            {"entity_id": entity_id},
        )
        or 0
    )
    outgoing = int(
        read_scalar(
            connection,
            "MATCH (e:Entity {id:$entity_id})-[r:RELATES]->(:Entity) RETURN count(r)",
            {"entity_id": entity_id},
        )
        or 0
    )
    incoming = int(
        read_scalar(
            connection,
            "MATCH (:Entity)-[r:RELATES]->(e:Entity {id:$entity_id}) RETURN count(r)",
            {"entity_id": entity_id},
        )
        or 0
    )
    return mentions + outgoing + incoming


def delete_orphan_entities(connection: lb.Connection, entity_ids: Iterable[str]) -> None:
    for entity_id in sorted(set(entity_ids)):
        if entity_reference_count(connection, entity_id) != 0:
            continue
        connection.execute(
            "MATCH (e:Entity {id:$entity_id}) DETACH DELETE e",
            parameters={"entity_id": entity_id},
        )


def extract_single_file(root: Path, relative_path: str) -> dict[str, Any]:
    with pushd(root):
        return extract([Path(relative_path)], cache_root=root)


def patch_graphify_impl(
    *,
    root: Path,
    file_path: Path,
    db_path: Path,
    graph_json_path: Path,
    deleted: bool,
    before_commit: Any | None = None,
) -> GraphifyPatchResult:
    start = time.perf_counter()
    bootstrap_db_if_needed(root, db_path, graph_json_path)
    relative_path = normalize_repo_path(file_path, root)
    absolute_path = root / relative_path
    timestamp = utc_now_iso()

    if not deleted and _get_extractor(Path(relative_path)) is None:
        raise RuntimeError(f"Graphify cannot incrementally extract {relative_path}.")

    extracted = {"nodes": [], "edges": []}
    content_hash = ""
    if not deleted:
        if not absolute_path.exists():
            raise FileNotFoundError(f"File not found: {absolute_path}")
        extracted = extract_single_file(root, relative_path)
        content_hash = md5_file(absolute_path)

    with pushd(root):
        with open_connection(db_path, read_only=False) as connection:
            ensure_schema(connection)
            delete_extractors = [NATIVE_EXTRACTOR]
            if deleted:
                delete_extractors.append(SEMANTIC_IMPORT_EXTRACTOR)
            old_entity_ids: set[str] = set()
            for extractor_name in delete_extractors:
                old_entity_ids |= collect_native_entity_ids(connection, relative_path, extractor_name)

            with open_transaction(connection):
                for extractor_name in delete_extractors:
                    delete_relations(connection, relative_path, extractor_name)
                    delete_mentions(connection, relative_path, extractor_name)

                semantic_refresh_needed = False
                if deleted:
                    upsert_file_state(
                        connection,
                        path=relative_path,
                        content_hash="",
                        extractor=NATIVE_EXTRACTOR,
                        semantic_refresh_needed=False,
                        last_indexed_at=timestamp,
                    )
                else:
                    upsert_file_state(
                        connection,
                        path=relative_path,
                        content_hash=content_hash,
                        extractor=NATIVE_EXTRACTOR,
                        semantic_refresh_needed=False,
                        last_indexed_at=timestamp,
                    )
                    for node in extracted.get("nodes", []):
                        node = normalize_node(node, root)
                        upsert_entity(connection, node, updated_at=timestamp)
                        create_mention(
                            connection,
                            file_path=relative_path,
                            entity_id=node["id"],
                            extractor=NATIVE_EXTRACTOR,
                            confidence=str(node.get("confidence", "EXTRACTED")),
                            raw_json=json.dumps(node, sort_keys=True),
                        )
                    for edge in extracted.get("edges", []):
                        create_relation(
                            connection,
                            edge,
                            extractor=NATIVE_EXTRACTOR,
                            origin_file=relative_path,
                        )
                    semantic_refresh_needed = bool(
                        mention_count(connection, relative_path, SEMANTIC_IMPORT_EXTRACTOR)
                        or relation_count(connection, relative_path, SEMANTIC_IMPORT_EXTRACTOR)
                    )
                    upsert_file_state(
                        connection,
                        path=relative_path,
                        content_hash=content_hash,
                        extractor=NATIVE_EXTRACTOR,
                        semantic_refresh_needed=semantic_refresh_needed,
                        last_indexed_at=timestamp,
                    )

                if before_commit is not None:
                    before_commit()

            delete_orphan_entities(connection, old_entity_ids - {str(node.get("id")) for node in extracted.get("nodes", [])})

    node_count, edge_count = export_graph_json(db_path, graph_json_path)
    patch_text_index(root, file_path, deleted=deleted)
    elapsed = time.perf_counter() - start
    semantic_refresh_needed = False
    with open_connection(db_path, read_only=True) as connection:
        semantic_refresh_needed = bool(
            read_scalar(
                connection,
                "MATCH (f:FileState {path:$path}) RETURN f.semantic_refresh_needed",
                {"path": relative_path},
            )
        )

    return GraphifyPatchResult(
        file_path=relative_path,
        deleted=deleted,
        semantic_refresh_needed=semantic_refresh_needed,
        node_count=node_count,
        edge_count=edge_count,
        elapsed_seconds=elapsed,
    )


def graph_stats_text(graph: nx.Graph, communities: dict[int, list[str]]) -> str:
    confidences = [data.get("confidence", "EXTRACTED") for _, _, data in graph.edges(data=True)]
    total = len(confidences) or 1
    return (
        f"Nodes: {graph.number_of_nodes()}\n"
        f"Edges: {graph.number_of_edges()}\n"
        f"Communities: {len(communities)}\n"
        f"EXTRACTED: {round(confidences.count('EXTRACTED') / total * 100)}%\n"
        f"INFERRED: {round(confidences.count('INFERRED') / total * 100)}%\n"
        f"AMBIGUOUS: {round(confidences.count('AMBIGUOUS') / total * 100)}%\n"
    )


def default_community_labels(communities: dict[int, list[str]]) -> dict[int, str]:
    return {community_id: f"Community {community_id}" for community_id in communities}


def serve_graphify_impl(db_path: Path, report_path: Path) -> None:
    try:
        from mcp import types
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
    except ImportError as exc:
        raise RuntimeError("mcp is not installed in the current environment.") from exc

    server = Server("graphify")
    root = Path.cwd().resolve()

    def load_snapshot() -> tuple[nx.Graph, dict[int, list[str]]]:
        return load_graph_snapshot(db_path)

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="query_graph",
                description="Search the knowledge graph using BFS or DFS. Returns relevant nodes and edges as text context.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "Natural language question or keyword search"},
                        "mode": {"type": "string", "enum": ["bfs", "dfs"], "default": "bfs"},
                        "depth": {"type": "integer", "default": 3},
                        "token_budget": {"type": "integer", "default": 2000},
                        "context_filter": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional explicit edge-context filter.",
                        },
                    },
                    "required": ["question"],
                },
            ),
            types.Tool(
                name="get_node",
                description="Get full details for a specific node by label or ID.",
                inputSchema={
                    "type": "object",
                    "properties": {"label": {"type": "string"}},
                    "required": ["label"],
                },
            ),
            types.Tool(
                name="get_neighbors",
                description="Get all direct neighbors of a node with edge details.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "label": {"type": "string"},
                        "relation_filter": {"type": "string"},
                    },
                    "required": ["label"],
                },
            ),
            types.Tool(
                name="get_community",
                description="Get all nodes in a community by community ID.",
                inputSchema={
                    "type": "object",
                    "properties": {"community_id": {"type": "integer"}},
                    "required": ["community_id"],
                },
            ),
            types.Tool(
                name="god_nodes",
                description="Return the most connected nodes in the graph.",
                inputSchema={"type": "object", "properties": {"top_n": {"type": "integer", "default": 10}}},
            ),
            types.Tool(
                name="graph_stats",
                description="Return summary statistics for the graph.",
                inputSchema={"type": "object", "properties": {}},
            ),
            types.Tool(
                name="shortest_path",
                description="Find the shortest path between two concepts.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "target": {"type": "string"},
                        "max_hops": {"type": "integer", "default": 8},
                    },
                    "required": ["source", "target"],
                },
            ),
            types.Tool(
                name="search_docs",
                description="Search raw file text across Graphify-tracked files using the local SQLite FTS5 index.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Natural-language text query."},
                        "limit": {"type": "integer", "default": 5},
                    },
                    "required": ["query"],
                },
            ),
        ]

    @server.list_resources()
    async def list_resources() -> list[types.Resource]:
        return [
            types.Resource(uri=AnyUrl("graphify://report"), name="Graph Report", description="Full GRAPH_REPORT.md", mimeType="text/markdown"),
            types.Resource(uri=AnyUrl("graphify://stats"), name="Graph Stats", description="Node and edge counts", mimeType="text/plain"),
            types.Resource(uri=AnyUrl("graphify://god-nodes"), name="God Nodes", description="Most-connected nodes", mimeType="text/plain"),
            types.Resource(uri=AnyUrl("graphify://surprises"), name="Surprising Connections", description="Cross-community surprises", mimeType="text/plain"),
            types.Resource(uri=AnyUrl("graphify://audit"), name="Confidence Audit", description="Edge confidence breakdown", mimeType="text/plain"),
            types.Resource(uri=AnyUrl("graphify://questions"), name="Suggested Questions", description="Suggested graph questions", mimeType="text/plain"),
        ]

    def tool_query_graph(arguments: dict[str, Any]) -> str:
        graph, _communities = load_snapshot()
        return _query_graph_text(
            graph,
            arguments["question"],
            mode=str(arguments.get("mode", "bfs")),
            depth=min(int(arguments.get("depth", 3)), 6),
            token_budget=int(arguments.get("token_budget", 2000)),
            context_filters=arguments.get("context_filter"),
        )

    def tool_get_node(arguments: dict[str, Any]) -> str:
        label = str(arguments["label"]).lower()
        graph, _communities = load_snapshot()
        matches = [
            (node_id, data)
            for node_id, data in graph.nodes(data=True)
            if label in str(data.get("label", "")).lower() or label == node_id.lower()
        ]
        if not matches:
            return f"No node matching '{label}' found."
        node_id, data = matches[0]
        return "\n".join(
            [
                f"Node: {sanitize_label(str(data.get('label', node_id)))}",
                f"  ID: {sanitize_label(node_id)}",
                f"  Source: {sanitize_label(str(data.get('source_file', '')))} {sanitize_label(str(data.get('source_location', '')))}",
                f"  Type: {sanitize_label(str(data.get('file_type', '')))}",
                f"  Community: {sanitize_label(str(data.get('community', '')))}",
                f"  Degree: {graph.degree(node_id)}",
            ]
        )

    def tool_get_neighbors(arguments: dict[str, Any]) -> str:
        graph, _communities = load_snapshot()
        matches = _find_node(graph, str(arguments["label"]))
        if not matches:
            return f"No node matching '{arguments['label']}' found."
        node_id = matches[0]
        relation_filter = str(arguments.get("relation_filter", "")).lower()
        lines = [f"Neighbors of {sanitize_label(str(graph.nodes[node_id].get('label', node_id)))}:"]
        for neighbor in graph.neighbors(node_id):
            edge_data = graph.edges[node_id, neighbor]
            relation = str(edge_data.get("relation", ""))
            if relation_filter and relation_filter not in relation.lower():
                continue
            lines.append(
                f"  --> {sanitize_label(str(graph.nodes[neighbor].get('label', neighbor)))} "
                f"[{sanitize_label(relation)}] [{sanitize_label(str(edge_data.get('confidence', '')))}]"
            )
        return "\n".join(lines)

    def tool_get_community(arguments: dict[str, Any]) -> str:
        graph, communities = load_snapshot()
        community_id = int(arguments["community_id"])
        nodes = communities.get(community_id, [])
        if not nodes:
            return f"Community {community_id} not found."
        lines = [f"Community {community_id} ({len(nodes)} nodes):"]
        for node_id in nodes:
            data = graph.nodes[node_id]
            lines.append(
                f"  {sanitize_label(str(data.get('label', node_id)))} "
                f"[{sanitize_label(str(data.get('source_file', '')))}]"
            )
        return "\n".join(lines)

    def tool_god_nodes(arguments: dict[str, Any]) -> str:
        graph, _communities = load_snapshot()
        top_n = int(arguments.get("top_n", 10))
        ordered = sorted(graph.degree, key=lambda item: item[1], reverse=True)[:top_n]
        lines = ["God nodes (most connected):"]
        for index, (node_id, degree) in enumerate(ordered, 1):
            lines.append(f"  {index}. {graph.nodes[node_id].get('label', node_id)} - {degree} edges")
        return "\n".join(lines)

    def tool_graph_stats(_: dict[str, Any]) -> str:
        graph, communities = load_snapshot()
        return graph_stats_text(graph, communities)

    def tool_shortest_path(arguments: dict[str, Any]) -> str:
        graph, _communities = load_snapshot()
        source_matches = _score_nodes(graph, [token.lower() for token in str(arguments["source"]).split()])
        target_matches = _score_nodes(graph, [token.lower() for token in str(arguments["target"]).split()])
        if not source_matches:
            return f"No node matching source '{arguments['source']}' found."
        if not target_matches:
            return f"No node matching target '{arguments['target']}' found."
        source_id = source_matches[0][1]
        target_id = target_matches[0][1]
        max_hops = int(arguments.get("max_hops", 8))
        try:
            path_nodes = nx.shortest_path(graph, source_id, target_id)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return (
                f"No path found between '{graph.nodes[source_id].get('label', source_id)}' "
                f"and '{graph.nodes[target_id].get('label', target_id)}'."
            )
        hops = len(path_nodes) - 1
        if hops > max_hops:
            return f"Path exceeds max_hops={max_hops} ({hops} hops found)."
        segments: list[str] = []
        for index in range(len(path_nodes) - 1):
            left = path_nodes[index]
            right = path_nodes[index + 1]
            edge_data = graph.edges[left, right]
            relation = str(edge_data.get("relation", ""))
            confidence = str(edge_data.get("confidence", ""))
            confidence_suffix = f" [{confidence}]" if confidence else ""
            if index == 0:
                segments.append(str(graph.nodes[left].get("label", left)))
            segments.append(f"--{relation}{confidence_suffix}--> {graph.nodes[right].get('label', right)}")
        return f"Shortest path ({hops} hops):\n  " + " ".join(segments)

    def tool_search_docs(arguments: dict[str, Any]) -> str:
        query = str(arguments["query"])
        results = search_docs_impl(root, query, limit=int(arguments.get("limit", 5)))
        return render_search_docs_results(query, results)

    handlers = {
        "query_graph": tool_query_graph,
        "get_node": tool_get_node,
        "get_neighbors": tool_get_neighbors,
        "get_community": tool_get_community,
        "god_nodes": tool_god_nodes,
        "graph_stats": tool_graph_stats,
        "shortest_path": tool_shortest_path,
        "search_docs": tool_search_docs,
    }

    @server.read_resource()
    async def read_resource(uri: AnyUrl) -> str:
        uri_str = str(uri)
        graph, communities = load_snapshot()
        if uri_str == "graphify://report":
            if report_path.exists():
                return report_path.read_text(encoding="utf-8")
            return "GRAPH_REPORT.md not found. Run /graphify for a full semantic rebuild if you need the report."
        if uri_str == "graphify://stats":
            return graph_stats_text(graph, communities)
        if uri_str == "graphify://god-nodes":
            return tool_god_nodes({"top_n": 10})
        if uri_str == "graphify://surprises":
            try:
                from graphify.analyze import surprising_connections

                surprises = surprising_connections(graph, communities, top_n=10)
            except Exception as exc:
                return f"Could not compute surprising connections: {exc}"
            if not surprises:
                return "No surprising connections found."
            lines = ["Surprising cross-community connections:"]
            for surprise in surprises:
                lines.append(
                    f"  {surprise.get('source', '')} <-> {surprise.get('target', '')} "
                    f"[{surprise.get('relation', '')}]"
                )
            return "\n".join(lines)
        if uri_str == "graphify://audit":
            confidences = [data.get("confidence", "EXTRACTED") for _, _, data in graph.edges(data=True)]
            total = len(confidences) or 1
            return (
                f"Total edges: {len(confidences)}\n"
                f"EXTRACTED: {confidences.count('EXTRACTED')} ({round(confidences.count('EXTRACTED') / total * 100)}%)\n"
                f"INFERRED: {confidences.count('INFERRED')} ({round(confidences.count('INFERRED') / total * 100)}%)\n"
                f"AMBIGUOUS: {confidences.count('AMBIGUOUS')} ({round(confidences.count('AMBIGUOUS') / total * 100)}%)\n"
            )
        if uri_str == "graphify://questions":
            try:
                from graphify.analyze import suggest_questions

                questions = suggest_questions(graph, communities, default_community_labels(communities), top_n=10)
            except Exception as exc:
                return f"Could not generate questions: {exc}"
            if not questions:
                return "No suggested questions available."
            lines = ["Suggested questions:"]
            for question in questions:
                if isinstance(question, dict):
                    lines.append(f"  - {question.get('question', '')}")
                else:
                    lines.append(f"  - {question}")
            return "\n".join(lines)
        raise ValueError(f"Unknown resource: {uri_str}")

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
        handler = handlers.get(name)
        if handler is None:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
        try:
            return [types.TextContent(type="text", text=handler(arguments))]
        except Exception as exc:
            return [types.TextContent(type="text", text=f"Error executing {name}: {exc}")]

    async def main() -> None:
        async with stdio_server() as streams:
            await server.run(streams[0], streams[1], server.create_initialization_options())

    import asyncio

    _filter_blank_stdin()
    asyncio.run(main())


@functools.lru_cache(maxsize=8)
def _gitnexus_incremental_supported(command_prefix: tuple[str, ...]) -> bool:
    try:
        result = subprocess.run(
            [*command_prefix, "analyze", "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return False
    return "--incremental" in (result.stdout + result.stderr)


def gitnexus_incremental_supported(command_prefix: Sequence[str]) -> bool:
    return _gitnexus_incremental_supported(tuple(command_prefix))


def patch_gitnexus_impl(root: Path, file_path: Path, *, quiet: bool = False) -> int:
    relative_path = normalize_repo_path(file_path, root)
    if not gitnexus_incremental_supported(GITNEXUS_COMMAND):
        if not quiet:
            typer.echo(
                "Installed GitNexus CLI does not expose a safe incremental analyze path. "
                "patch-gitnexus.sh will not mutate .gitnexus/lbug or trigger a full rebuild.",
                err=True,
            )
            typer.echo(
                f"Requested file: {relative_path}",
                err=True,
            )
        return 2

    result = subprocess.run(
        [*GITNEXUS_COMMAND, "analyze", "--incremental", str(root)],
        cwd=root,
        capture_output=quiet,
        text=quiet,
        check=False,
    )
    return result.returncode


def validate_graphify_impl(root: Path, source_graph_json: Path) -> ValidationResult:
    validation_dir = root / "graphify-out"
    validation_dir.mkdir(parents=True, exist_ok=True)
    temp_db_root = Path(tempfile.mkdtemp(prefix="atomic-index-", dir=str(root / "graphify-out")))
    temp_db = temp_db_root / "graphify.lbug"
    temp_json = temp_db_root / "graph.json"
    validation_file = DEFAULT_VALIDATE_FILE
    validation_path = root / validation_file

    try:
        migrate_graphify_impl(root=root, graph_json_path=source_graph_json, db_path=temp_db, force=False)
        validation_path.write_text("# Atomic validation\n\nInitial content.\n", encoding="utf-8")
        patch_graphify_impl(
            root=root,
            file_path=validation_path,
            db_path=temp_db,
            graph_json_path=temp_json,
            deleted=False,
        )

        reader_release = threading.Event()
        writer_ready = threading.Event()
        writer_done = threading.Event()
        concurrent_read_seconds = 0.0

        def before_commit() -> None:
            writer_ready.set()
            if not reader_release.wait(timeout=5):
                raise RuntimeError("Reader did not observe the graph before writer commit.")

        def writer() -> None:
            try:
                validation_path.write_text("# Atomic validation\n\nConcurrent write check.\n", encoding="utf-8")
                patch_graphify_impl(
                    root=root,
                    file_path=validation_path,
                    db_path=temp_db,
                    graph_json_path=temp_json,
                    deleted=False,
                    before_commit=before_commit,
                )
            finally:
                writer_done.set()

        thread = threading.Thread(target=writer, daemon=True)
        thread.start()
        if not writer_ready.wait(timeout=5):
            raise RuntimeError("Writer did not reach the transaction window.")
        read_start = time.perf_counter()
        graph, _communities = load_graph_snapshot(temp_db)
        concurrent_read_seconds = time.perf_counter() - read_start
        if graph.number_of_nodes() == 0:
            raise RuntimeError("Concurrent read returned an empty graph snapshot.")
        reader_release.set()
        if not writer_done.wait(timeout=10):
            raise RuntimeError("Writer did not finish after the reader released it.")

        validation_path.write_text("# Atomic validation\n\nLatency probe.\n", encoding="utf-8")
        patch_start = time.perf_counter()
        patch_graphify_impl(
            root=root,
            file_path=validation_path,
            db_path=temp_db,
            graph_json_path=temp_json,
            deleted=False,
        )
        patch_seconds = time.perf_counter() - patch_start
        if patch_seconds >= 1.0:
            raise RuntimeError(f"Single-file patch took {patch_seconds:.3f}s, expected < 1.0s.")

        successive_patch_seconds: list[float] = []
        for index in range(10):
            validation_path.write_text(
                f"# Atomic validation {index}\n\nPatch round {index}.\n\n```bash\necho {index}\n```\n",
                encoding="utf-8",
            )
            round_start = time.perf_counter()
            patch_graphify_impl(
                root=root,
                file_path=validation_path,
                db_path=temp_db,
                graph_json_path=temp_json,
                deleted=False,
            )
            successive_patch_seconds.append(time.perf_counter() - round_start)
            graph, _communities = load_graph_snapshot(temp_db)
            if graph.number_of_nodes() == 0:
                raise RuntimeError(f"Graph became empty after patch round {index}.")

        final_graph, _communities = load_graph_snapshot(temp_db)
        return ValidationResult(
            concurrent_read_seconds=concurrent_read_seconds,
            patch_seconds=patch_seconds,
            successive_patch_seconds=successive_patch_seconds,
            final_nodes=final_graph.number_of_nodes(),
            final_edges=final_graph.number_of_edges(),
        )
    finally:
        with contextlib.suppress(FileNotFoundError):
            validation_path.unlink()
        shutil.rmtree(temp_db_root, ignore_errors=True)


@app.command("migrate-graphify")
def migrate_graphify(
    root: Path = typer.Option(DEFAULT_ROOT, "--root", help="Repository root."),
    graph_json_path: Path = typer.Option(DEFAULT_GRAPH_JSON, "--graph-json", help="Existing Graphify graph.json."),
    db_path: Path = typer.Option(DEFAULT_GRAPH_DB, "--db-path", help="Destination Ladybug database path."),
    force: bool = typer.Option(False, "--force", help="Replace an existing DB."),
) -> None:
    root = root.resolve()
    graph_json_path = graph_json_path.resolve() if graph_json_path.is_absolute() else (root / graph_json_path)
    db_path = db_path.resolve() if db_path.is_absolute() else (root / db_path)
    nodes, edges = migrate_graphify_impl(root=root, graph_json_path=graph_json_path, db_path=db_path, force=force)
    mirror_nodes, mirror_edges = export_graph_json(db_path, graph_json_path)
    typer.echo(
        f"Migrated Graphify into {db_path} ({nodes} imported nodes, {edges} imported edges; "
        f"{mirror_nodes} mirror nodes, {mirror_edges} mirror edges)."
    )


@app.command("patch-graphify")
def patch_graphify(
    file_path: Path = typer.Argument(..., help="Changed file to patch into the Graphify DB."),
    root: Path = typer.Option(DEFAULT_ROOT, "--root", help="Repository root."),
    db_path: Path = typer.Option(DEFAULT_GRAPH_DB, "--db-path", help="Graphify Ladybug database path."),
    graph_json_path: Path = typer.Option(DEFAULT_GRAPH_JSON, "--graph-json", help="JSON mirror path."),
    deleted: bool = typer.Option(False, "--deleted", help="Treat the file as deleted."),
) -> None:
    root = root.resolve()
    db_path = db_path.resolve() if db_path.is_absolute() else (root / db_path)
    graph_json_path = graph_json_path.resolve() if graph_json_path.is_absolute() else (root / graph_json_path)
    result = patch_graphify_impl(
        root=root,
        file_path=file_path,
        db_path=db_path,
        graph_json_path=graph_json_path,
        deleted=deleted,
    )
    typer.echo(
        f"Patched Graphify for {result.file_path} in {result.elapsed_seconds:.3f}s "
        f"({result.node_count} nodes, {result.edge_count} edges, "
        f"semantic_refresh_needed={str(result.semantic_refresh_needed).lower()})."
    )


@app.command("serve-graphify")
def serve_graphify(
    db_path: Path = typer.Option(DEFAULT_GRAPH_DB, "--db-path", help="Graphify Ladybug database path."),
    report_path: Path = typer.Option(DEFAULT_GRAPH_REPORT, "--report-path", help="Graph report path."),
) -> None:
    serve_graphify_impl(db_path.resolve(), report_path.resolve())


@app.command("reconcile-graphs")
def reconcile_graphs(
    root: Path = typer.Option(DEFAULT_ROOT, "--root", help="Repository root."),
    db_path: Path = typer.Option(DEFAULT_GRAPH_DB, "--db-path", help="Graphify Ladybug database path."),
    graph_json_path: Path = typer.Option(DEFAULT_GRAPH_JSON, "--graph-json", help="Graphify JSON mirror path."),
) -> None:
    root = root.resolve()
    db_path = db_path.resolve() if db_path.is_absolute() else (root / db_path)
    graph_json_path = graph_json_path.resolve() if graph_json_path.is_absolute() else (root / graph_json_path)
    result = reconcile_graphs_impl(
        root=root,
        db_path=db_path,
        graph_json_path=graph_json_path,
        force_full_scan=True,
    )
    typer.echo(render_reconcile_summary(result))
    if result.errors:
        raise typer.Exit(code=1)


@app.command("graph-patch-status")
def graph_patch_status(
    root: Path = typer.Option(DEFAULT_ROOT, "--root", help="Repository root."),
    db_path: Path = typer.Option(DEFAULT_GRAPH_DB, "--db-path", help="Graphify Ladybug database path."),
    graph_json_path: Path = typer.Option(DEFAULT_GRAPH_JSON, "--graph-json", help="Graphify JSON mirror path."),
) -> None:
    root = root.resolve()
    db_path = db_path.resolve() if db_path.is_absolute() else (root / db_path)
    graph_json_path = graph_json_path.resolve() if graph_json_path.is_absolute() else (root / graph_json_path)
    status = graph_patch_status_impl(root, db_path, graph_json_path)
    last_hook = status.get("last_hook") or {}
    typer.echo(
        "\n".join(
            [
                f"graphify_db_exists={str(status['graphify_db_exists']).lower()}",
                f"graphify_json_exists={str(status['graphify_json_exists']).lower()}",
                f"text_index_exists={str(status['text_index_exists']).lower()}",
                f"text_indexed_files={status['text_indexed_files']}",
                f"indexed_files={status['indexed_files']}",
                f"semantic_refresh_needed={status['semantic_refresh_needed']}",
                f"nodes={status['nodes']}",
                f"edges={status['edges']}",
                f"gitnexus_incremental_supported={str(status['gitnexus_incremental_supported']).lower()}",
                f"gitnexus_pending_files={len(status['gitnexus_pending_files'])}",
                f"gitnexus_stale={str(status['gitnexus_stale']).lower()}",
                f"last_hook_updated_at={last_hook.get('updated_at', '')}",
                f"last_hook_errors={len(last_hook.get('errors', []))}",
            ]
        )
    )


@app.command("search-docs")
def search_docs(
    query: str = typer.Argument(..., help="Text query to run against the local SQLite FTS5 index."),
    root: Path = typer.Option(DEFAULT_ROOT, "--root", help="Repository root."),
    limit: int = typer.Option(5, "--limit", min=1, max=20, help="Maximum number of results to return."),
) -> None:
    root = root.resolve()
    typer.echo(render_search_docs_results(query, search_docs_impl(root, query, limit=limit)))


@app.command("hook-post-tool-use")
def hook_post_tool_use(
    db_path: Path = typer.Option(DEFAULT_GRAPH_DB, "--db-path", help="Graphify Ladybug database path."),
    graph_json_path: Path = typer.Option(DEFAULT_GRAPH_JSON, "--graph-json", help="Graphify JSON mirror path."),
) -> None:
    payload = read_hook_payload()
    root = Path(str(payload.get("cwd") or DEFAULT_ROOT)).resolve()
    tool_name = tool_name_from_payload(payload)
    tool_input = tool_input_from_payload(payload)
    gitnexus_stale, gitnexus_stale_paths, gitnexus_stale_message = extract_gitnexus_post_tool_use_state(root, payload)
    if not tool_likely_mutates_workspace(tool_name) and not gitnexus_stale:
        typer.echo(json.dumps({"continue": True}))
        return

    db_path = db_path.resolve() if db_path.is_absolute() else (root / db_path)
    graph_json_path = graph_json_path.resolve() if graph_json_path.is_absolute() else (root / graph_json_path)
    candidate_paths, force_full_scan = extract_candidate_paths_from_tool_use(root, tool_name, tool_input)
    if gitnexus_stale:
        force_full_scan = True
    result = reconcile_graphs_impl(
        root=root,
        db_path=db_path,
        graph_json_path=graph_json_path,
        candidate_paths=candidate_paths,
        force_full_scan=force_full_scan,
        gitnexus_stale_paths=gitnexus_stale_paths,
        gitnexus_stale_message=gitnexus_stale_message,
    )
    emit_post_tool_use_response(result)


@app.command("hook-stop")
def hook_stop(
    db_path: Path = typer.Option(DEFAULT_GRAPH_DB, "--db-path", help="Graphify Ladybug database path."),
    graph_json_path: Path = typer.Option(DEFAULT_GRAPH_JSON, "--graph-json", help="Graphify JSON mirror path."),
) -> None:
    payload = read_hook_payload()
    root = Path(str(payload.get("cwd") or DEFAULT_ROOT)).resolve()
    db_path = db_path.resolve() if db_path.is_absolute() else (root / db_path)
    graph_json_path = graph_json_path.resolve() if graph_json_path.is_absolute() else (root / graph_json_path)
    result = reconcile_graphs_impl(
        root=root,
        db_path=db_path,
        graph_json_path=graph_json_path,
        force_full_scan=True,
    )
    emit_hook_response(result)


@app.command("patch-gitnexus")
def patch_gitnexus(
    file_path: Path = typer.Argument(..., help="Changed file that would require GitNexus re-indexing."),
    root: Path = typer.Option(DEFAULT_ROOT, "--root", help="Repository root."),
) -> None:
    root = root.resolve()
    code = patch_gitnexus_impl(root, file_path)
    raise typer.Exit(code=code)


@app.command("validate-graphify")
def validate_graphify(
    root: Path = typer.Option(DEFAULT_ROOT, "--root", help="Repository root."),
    graph_json_path: Path = typer.Option(DEFAULT_GRAPH_JSON, "--graph-json", help="Source graph.json for the validation fixture."),
) -> None:
    root = root.resolve()
    graph_json_path = graph_json_path.resolve() if graph_json_path.is_absolute() else (root / graph_json_path)
    result = validate_graphify_impl(root=root, source_graph_json=graph_json_path)
    typer.echo(
        "Validation passed: "
        f"concurrent_read={result.concurrent_read_seconds:.3f}s, "
        f"single_patch={result.patch_seconds:.3f}s, "
        f"successive_patches={[round(value, 3) for value in result.successive_patch_seconds]}, "
        f"final_graph={result.final_nodes} nodes/{result.final_edges} edges."
    )


if __name__ == "__main__":
    app()
