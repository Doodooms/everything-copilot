#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.21,<5"]
# ///
"""Validate versioned task exchanges and verify local Git/artifact claims."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"
SCHEMA_FILES = {
    "handoff": "handoff.schema.json",
    "manifest": "manifest.schema.json",
    "manifest-record": "manifest-record.schema.json",
    "event": "orchestration-event.schema.json",
    "transition": "task-transition.schema.json",
}


def _load_schema(kind: str) -> dict[str, Any]:
    schema_path = SCHEMA_DIR / SCHEMA_FILES[kind]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load schema {schema_path}: {exc}") from exc
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise ValueError(f"invalid schema {schema_path}: {exc.message}") from exc
    return schema


def validate_document(
    kind: str,
    payload: Any,
    *,
    repo: str | Path | None = None,
    repository_id: str | None = None,
) -> list[str]:
    """Return all structural and requested local-verification errors."""
    if kind not in SCHEMA_FILES:
        raise ValueError(f"unknown exchange kind: {kind}")

    schema = _load_schema(kind)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [
        f"{_format_path(error.absolute_path)}: {error.message}"
        for error in sorted(
            validator.iter_errors(payload),
            key=lambda item: _format_path(item.absolute_path),
        )
    ]
    if errors or not isinstance(payload, dict):
        return errors

    if kind == "handoff":
        errors.extend(_verify_handoff(payload, repo=repo, repository_id=repository_id))
    elif kind == "manifest":
        if payload.get("base_revision"):
            errors.extend(
                _verify_commit(repo, payload["base_revision"], "base_revision")
            )
        lifecycle = payload.get("lifecycle", {})
        for index, sha in enumerate(lifecycle.get("commit_shas", [])):
            errors.extend(_verify_commit(repo, sha, f"lifecycle.commit_shas[{index}]"))
    elif kind == "manifest-record":
        manifest = payload["manifest"]
        if payload["task_id"] != manifest.get("id"):
            errors.append("task_id must match manifest.id")
        if payload["status"] != manifest.get("status"):
            errors.append("status must match manifest.status")
        errors.extend(validate_document("manifest", manifest, repo=repo))
    elif kind == "event":
        errors.extend(_verify_event(payload, repo=repo))
    return errors


def _format_path(path: Any) -> str:
    parts = list(path)
    return "$" + "".join(
        f"[{part}]" if isinstance(part, int) else f".{part}" for part in parts
    )


def _verify_handoff(
    payload: dict[str, Any],
    *,
    repo: str | Path | None,
    repository_id: str | None,
) -> list[str]:
    errors: list[str] = []
    commit_refs = payload.get("git_commits", [])
    artifact_refs = payload.get("artifacts", [])
    if not commit_refs and not artifact_refs:
        return errors
    if repo is None:
        if commit_refs:
            errors.append("Git commit claims are unverified; pass --repo")
        if artifact_refs:
            errors.append("artifact digests are unverified; pass --repo")
        return errors

    repo_path = Path(repo).expanduser().resolve()
    if not repo_path.is_dir():
        return [f"repository path is not a directory: {repo_path}"]
    top_level_result = _git(repo_path, "rev-parse", "--show-toplevel")
    if top_level_result.returncode != 0:
        return [f"--repo is not inside a Git worktree: {repo_path}"]
    root = Path(top_level_result.stdout.strip()).resolve()

    for index, commit in enumerate(commit_refs):
        field = f"git_commits[{index}]"
        if repository_id is not None and commit.get("repository") != repository_id:
            errors.append(
                f"{field}.repository does not match --repository-id {repository_id!r}"
            )
            continue
        sha = commit["commit_sha"]
        commit_errors, actual_paths = _verify_commit_paths(root, sha, field)
        errors.extend(commit_errors)
        declared_paths = set(commit["changed_paths"])
        missing_from_declaration = actual_paths - declared_paths
        if missing_from_declaration:
            errors.append(
                f"{field}.changed_paths omits paths present in commit {sha}: "
                + ", ".join(sorted(missing_from_declaration))
            )
        absent_from_commit = declared_paths - actual_paths
        if absent_from_commit:
            errors.append(
                f"{field}.changed_paths lists paths absent from commit {sha}: "
                + ", ".join(sorted(absent_from_commit))
            )

    for index, artifact in enumerate(artifact_refs):
        field = f"artifacts[{index}]"
        path_error, artifact_path = _resolve_artifact(root, artifact["path"])
        if path_error:
            errors.append(f"{field}.path: {path_error}")
            continue
        actual_digest = _sha256(artifact_path)
        if actual_digest.casefold() != artifact["sha256"].casefold():
            errors.append(
                f"{field}.sha256 mismatch for {artifact['path']}: expected "
                f"{artifact['sha256']}, got {actual_digest}"
            )
    return errors


def _verify_event(payload: dict[str, Any], *, repo: str | Path | None) -> list[str]:
    data = payload.get("data", {})
    commit_shas = data.get("commit_shas", [])
    artifacts = data.get("artifacts", [])
    if (commit_shas or artifacts) and repo is None:
        return ["event Git/artifact claims are unverified; pass --repo"]
    if repo is None:
        return []

    errors: list[str] = []
    for index, sha in enumerate(commit_shas):
        errors.extend(_verify_commit(repo, sha, f"data.commit_shas[{index}]"))

    repo_path = Path(repo).expanduser().resolve()
    top_level = _git(repo_path, "rev-parse", "--show-toplevel")
    if top_level.returncode != 0 and artifacts:
        return errors + [
            "event artifacts cannot be checked: --repo is not inside a Git worktree"
        ]
    if artifacts:
        root = Path(top_level.stdout.strip()).resolve()
        for index, artifact in enumerate(artifacts):
            field = f"data.artifacts[{index}]"
            path_error, artifact_path = _resolve_artifact(root, artifact["path"])
            if path_error:
                errors.append(f"{field}.path: {path_error}")
                continue
            actual_digest = _sha256(artifact_path)
            if actual_digest.casefold() != artifact["sha256"].casefold():
                errors.append(f"{field}.sha256 mismatch for {artifact['path']}")
    return errors


def _verify_commit(repo: str | Path | None, sha: str, field: str) -> list[str]:
    if repo is None:
        return [f"{field} is structurally valid but unverified; pass --repo"]
    root = Path(repo).expanduser().resolve()
    if not root.is_dir():
        return [f"{field} cannot be resolved: repository path is not a directory"]
    result = _git(root, "rev-parse", "--show-toplevel")
    if result.returncode != 0:
        return [f"{field} cannot be resolved: --repo is not inside a Git worktree"]
    errors, _ = _verify_commit_paths(Path(result.stdout.strip()).resolve(), sha, field)
    return errors


def _verify_commit_paths(
    repo: Path, sha: str, field: str
) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    object_format = _git(repo, "rev-parse", "--show-object-format")
    if object_format.returncode != 0:
        return [
            f"{field}.sha cannot be checked: unable to read Git object format"
        ], set()
    expected_length = 64 if object_format.stdout.strip() == "sha256" else 40
    if len(sha) != expected_length:
        return [
            f"{field}.sha length does not match this {object_format.stdout.strip()} repository"
        ], set()

    resolved = _git(repo, "rev-parse", "--verify", f"{sha}^{{commit}}")
    if resolved.returncode != 0 or resolved.stdout.strip().casefold() != sha.casefold():
        return [
            f"{field}.sha is not an exact commit object in the supplied repository"
        ], set()

    parents = _git(repo, "rev-list", "--parents", "-n", "1", sha)
    if parents.returncode != 0:
        return [f"{field}.sha resolved but its parents could not be read"], set()
    parent_ids = parents.stdout.strip().split()[1:]
    if len(parent_ids) > 1:
        # A merge handoff reports the complete tree change relative to its first parent.
        changed = _git(
            repo,
            "diff",
            "--name-only",
            "--no-renames",
            "-z",
            f"{sha}^1",
            sha,
        )
    else:
        changed = _git(
            repo,
            "diff-tree",
            "--root",
            "--no-commit-id",
            "--name-only",
            "--no-renames",
            "-r",
            "-z",
            sha,
        )
    if changed.returncode != 0:
        return [f"{field}.sha resolved but its changed paths could not be read"], set()
    return errors, {item for item in changed.stdout.split("\0") if item}


def _resolve_artifact(repo: Path, relative_path: str) -> tuple[str | None, Path | None]:
    pure_path = PurePosixPath(relative_path)
    if (
        pure_path.is_absolute()
        or not pure_path.parts
        or pure_path.as_posix() != relative_path
        or (len(pure_path.parts[0]) >= 2 and pure_path.parts[0][1] == ":")
        or any(part in {"", ".", ".."} for part in pure_path.parts)
        or "\\" in relative_path
    ):
        return "path must be a normalized repository-relative path", None
    try:
        resolved = repo.joinpath(*pure_path.parts).resolve(strict=True)
    except OSError as exc:
        return f"cannot resolve artifact: {exc}", None
    if not resolved.is_relative_to(repo):
        return "resolved path escapes the repository", None
    if not resolved.is_file():
        return "artifact is not a regular file", None
    return None, resolved


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", required=True, choices=sorted(SCHEMA_FILES))
    parser.add_argument(
        "--input", required=True, type=Path, help="JSON document to validate"
    )
    parser.add_argument(
        "--repo", type=Path, help="local repository/workspace for reference checks"
    )
    parser.add_argument(
        "--repository-id",
        help="expected logical repository name in git_commits entries",
    )
    args = parser.parse_args(argv)

    try:
        document_kind = args.kind
        if args.input.suffix == ".jsonl":
            if args.kind not in {"event", "transition"}:
                raise ValueError(
                    "JSONL input is supported only for event and transition ledgers"
                )
            documents = []
            for line_number, line in enumerate(
                args.input.read_text(encoding="utf-8").splitlines(), start=1
            ):
                if line.strip():
                    try:
                        documents.append((line_number, json.loads(line)))
                    except json.JSONDecodeError as exc:
                        raise ValueError(
                            f"invalid JSON at line {line_number}: {exc}"
                        ) from exc
            if not documents:
                raise ValueError("JSONL ledger contains no records")
        else:
            payload = json.loads(args.input.read_text(encoding="utf-8"))
            if (
                args.kind == "manifest"
                and isinstance(payload, dict)
                and "manifest" in payload
            ):
                document_kind = "manifest-record"
            documents = [(None, payload)]
        all_errors: list[str] = []
        for line_number, payload in documents:
            errors = validate_document(
                document_kind,
                payload,
                repo=args.repo,
                repository_id=args.repository_id,
            )
            if line_number is not None:
                all_errors.extend(f"line {line_number}: {error}" for error in errors)
            else:
                all_errors.extend(errors)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1

    if all_errors:
        print("Validation failed:")
        for error in all_errors:
            print(f"- {error}")
        return 1
    print(f"Validation passed: {args.kind} ({len(documents)} record(s), {args.input})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
