from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .errors import HarnessFactoryError, RunOwnershipError
from .models import (
    HARNESS_NAMES,
    CrossHarnessRequest,
    Purpose,
    RunMode,
    RunStatus,
)

_RUN_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")
_ROOT_MARKER = ".harness-factory-root"
_ROOT_MARKER_CONTENT = "harness-factory-state-v1\n"
_WORKSPACE_MARKER = ".harness-factory-run"
_STATUS_TRANSITIONS = {
    RunStatus.PREPARED: {RunStatus.RUNNING, RunStatus.FAILED, RunStatus.CLEANED},
    RunStatus.RUNNING: {RunStatus.COMPLETED, RunStatus.FAILED},
    RunStatus.COMPLETED: {RunStatus.CLEANED},
    RunStatus.FAILED: {RunStatus.CLEANED},
    RunStatus.CLEANED: set(),
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _git(repo_root: Path, *arguments: str, timeout: int = 30) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_root), *arguments],
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise HarnessFactoryError(f"git command failed: {type(exc).__name__}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise HarnessFactoryError(
            f"git {' '.join(arguments)} exited {completed.returncode}: {detail}"
        )
    return completed.stdout.strip()


@dataclass(frozen=True)
class HarnessRun:
    run_id: str
    harness: str
    base_revision: str
    workspace: Path
    state_directory: Path
    mode: RunMode
    owner: str
    status: RunStatus
    created_at: str
    updated_at: str
    allowed_mutations: bool
    origin_harness: str | None = None
    call_depth: int = 0
    cross_harness_request: CrossHarnessRequest | None = None

    def __post_init__(self) -> None:
        if (
            not isinstance(self.run_id, str)
            or _RUN_ID_PATTERN.fullmatch(self.run_id) is None
        ):
            raise ValueError("run_id must be a lowercase 32-character UUID")
        if not isinstance(self.harness, str) or self.harness not in HARNESS_NAMES:
            raise ValueError("run harness is not supported")
        if (
            not isinstance(self.base_revision, str)
            or re.fullmatch(r"[0-9a-f]{40,64}", self.base_revision) is None
        ):
            raise ValueError("run base_revision must be a resolved commit SHA")
        if (
            not isinstance(self.workspace, Path)
            or not isinstance(self.state_directory, Path)
            or not self.workspace.is_absolute()
            or not self.state_directory.is_absolute()
        ):
            raise ValueError("run workspace and state directory must be absolute")
        if not isinstance(self.mode, RunMode) or not isinstance(self.status, RunStatus):
            raise TypeError("run mode and status must use their enums")
        if not isinstance(self.owner, str) or not self.owner.strip():
            raise ValueError("run owner must be non-empty")
        if not isinstance(self.created_at, str) or not self.created_at:
            raise ValueError("run created_at must be non-empty")
        if not isinstance(self.updated_at, str) or not self.updated_at:
            raise ValueError("run updated_at must be non-empty")
        if type(self.allowed_mutations) is not bool:
            raise ValueError("allowed_mutations must be a boolean")
        if self.allowed_mutations != (self.mode is RunMode.DEVELOPMENT):
            raise ValueError("mutation permission must match run mode")
        if type(self.call_depth) is not int or self.call_depth < 0:
            raise ValueError("run call_depth must be a non-negative integer")
        if self.cross_harness_request is not None and not isinstance(
            self.cross_harness_request, CrossHarnessRequest
        ):
            raise ValueError("cross_harness_request must be a CrossHarnessRequest")
        if self.cross_harness_request is None:
            if self.origin_harness is not None or self.call_depth != 0:
                raise ValueError("ordinary runs must have no cross-harness origin")
        else:
            if self.mode is not RunMode.VALIDATION or self.allowed_mutations:
                raise ValueError("cross-harness runs must be read-only validation")
            if (
                self.origin_harness != self.cross_harness_request.origin_harness
                or self.call_depth != self.cross_harness_request.call_depth
                or self.harness != self.cross_harness_request.target_harness
                or self.run_id != self.cross_harness_request.run_id
            ):
                raise ValueError("run does not match its cross-harness request")

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "run_id": self.run_id,
            "harness": self.harness,
            "base_revision": self.base_revision,
            "workspace": str(self.workspace),
            "state_directory": str(self.state_directory),
            "mode": self.mode.value,
            "owner": self.owner,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "allowed_mutations": self.allowed_mutations,
            "origin_harness": self.origin_harness,
            "call_depth": self.call_depth,
            "cross_harness_request": (
                self.cross_harness_request.as_dict()
                if self.cross_harness_request is not None
                else None
            ),
        }


class HarnessRunManager:
    """Creates one disposable Git worktree per harness run and owns its cleanup."""

    def __init__(self, repo_root: Path, state_root: Path):
        raw_repo_root = Path(repo_root)
        if raw_repo_root.is_symlink():
            raise HarnessFactoryError("repository root must not be a symlink")
        try:
            self.repo_root = raw_repo_root.resolve(strict=True)
        except OSError as exc:
            raise HarnessFactoryError(
                f"repository root is unavailable: {raw_repo_root}"
            ) from exc
        if not self.repo_root.is_dir():
            raise HarnessFactoryError("repository root must be a directory")

        root_from_git = Path(
            _git(self.repo_root, "rev-parse", "--show-toplevel")
        ).resolve(strict=True)
        if root_from_git != self.repo_root:
            raise HarnessFactoryError("repo_root must be the top-level Git directory")

        raw_state_root = Path(state_root)
        if not raw_state_root.is_absolute():
            raise HarnessFactoryError("state_root must be an absolute path")
        if raw_state_root.is_symlink():
            raise HarnessFactoryError("state_root must not be a symlink")
        self.state_root = raw_state_root.resolve(strict=False)
        try:
            self.state_root.relative_to(self.repo_root)
        except ValueError:
            pass
        else:
            raise HarnessFactoryError(
                "state_root must be outside the source repository"
            )
        if self.state_root == self.repo_root.parent:
            raise HarnessFactoryError("state_root must not be the repository's parent")
        if self.state_root.parent == self.state_root:
            raise HarnessFactoryError("state_root must not be a filesystem root")

        self.records_root = self.state_root / "runs"
        self.workspaces_root = self.state_root / "workspaces"

    def create_run(
        self,
        *,
        harness: str,
        base_revision: str,
        mode: RunMode,
        owner: str,
        run_id: str | None = None,
        cross_harness_request: CrossHarnessRequest | None = None,
    ) -> HarnessRun:
        if harness not in HARNESS_NAMES:
            raise HarnessFactoryError(f"unsupported harness: {harness!r}")
        if not isinstance(mode, RunMode):
            raise HarnessFactoryError("mode must be a RunMode")
        if not isinstance(owner, str) or not owner.strip():
            raise HarnessFactoryError("owner must be a non-empty string")

        resolved_revision = self.resolve_revision(base_revision)
        selected_run_id = run_id or uuid.uuid4().hex
        if _RUN_ID_PATTERN.fullmatch(selected_run_id) is None:
            raise HarnessFactoryError("run_id must be a lowercase 32-character UUID")
        if cross_harness_request is not None:
            if cross_harness_request.run_id != selected_run_id:
                raise HarnessFactoryError("cross-harness request run_id does not match")
            if cross_harness_request.target_harness != harness:
                raise HarnessFactoryError(
                    "cross-harness request targets a different harness"
                )
            if cross_harness_request.base_revision != resolved_revision:
                raise HarnessFactoryError(
                    "cross-harness request base revision does not match"
                )
            if cross_harness_request.requested_by != owner:
                raise HarnessFactoryError(
                    "run owner must match cross-harness requester"
                )
            if mode is not RunMode.VALIDATION:
                raise HarnessFactoryError("cross-harness runs must use validation mode")
        if mode is RunMode.DEVELOPMENT and cross_harness_request is not None:
            raise HarnessFactoryError(
                "development runs cannot be cross-harness requests"
            )

        self._ensure_roots()
        state_directory = self.records_root / selected_run_id
        workspace = self.workspaces_root / selected_run_id
        if state_directory.exists() or state_directory.is_symlink():
            raise HarnessFactoryError(f"run state already exists: {selected_run_id}")
        if workspace.exists() or workspace.is_symlink():
            raise HarnessFactoryError(
                f"run workspace already exists: {selected_run_id}"
            )

        state_directory.mkdir(mode=0o700)
        try:
            _git(
                self.repo_root,
                "worktree",
                "add",
                "--detach",
                str(workspace),
                resolved_revision,
                timeout=60,
            )
        except HarnessFactoryError:
            state_directory.rmdir()
            raise
        try:
            _write_workspace_marker(workspace, selected_run_id)
        except OSError as exc:
            raise HarnessFactoryError(
                "worktree was created but its ownership marker could not be written; "
                f"preserve it for recovery: {workspace}"
            ) from exc

        now = _utc_now()
        record = HarnessRun(
            run_id=selected_run_id,
            harness=harness,
            base_revision=resolved_revision,
            workspace=workspace,
            state_directory=state_directory,
            mode=mode,
            owner=owner,
            status=RunStatus.PREPARED,
            created_at=now,
            updated_at=now,
            allowed_mutations=mode is RunMode.DEVELOPMENT,
            origin_harness=(
                cross_harness_request.origin_harness
                if cross_harness_request is not None
                else None
            ),
            call_depth=(
                cross_harness_request.call_depth
                if cross_harness_request is not None
                else 0
            ),
            cross_harness_request=cross_harness_request,
        )
        try:
            self._write_record(record)
        except OSError as exc:
            raise HarnessFactoryError(
                "worktree was created but run metadata could not be persisted; "
                f"preserve it for recovery: {workspace}"
            ) from exc
        return record

    def get_run(self, run_id: str) -> HarnessRun:
        self._verify_root_marker()
        if (
            self.records_root.is_symlink()
            or self.workspaces_root.is_symlink()
            or self.state_root.is_symlink()
        ):
            raise RunOwnershipError("managed run state paths must not be symlinks")
        path = self._record_path(run_id)
        if path.parent.is_symlink():
            raise RunOwnershipError("run state directory must not be a symlink")
        if path.is_symlink() or not path.is_file():
            raise HarnessFactoryError(f"run record is unavailable: {run_id}")
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise HarnessFactoryError(f"run record is invalid: {run_id}") from exc
        record = self._parse_record(raw, path.parent)
        if path.parent.name != record.run_id:
            raise RunOwnershipError("run record ID does not match its directory")
        expected_workspace = (self.workspaces_root / record.run_id).resolve(
            strict=False
        )
        if record.workspace.resolve(strict=False) != expected_workspace:
            raise RunOwnershipError("run workspace does not match its managed run ID")
        return record

    def transition(
        self,
        run_id: str,
        *,
        owner: str,
        status: RunStatus,
    ) -> HarnessRun:
        if not isinstance(status, RunStatus):
            raise HarnessFactoryError("status must be a RunStatus")
        record = self.get_run(run_id)
        self._assert_owner(record, owner)
        if status not in _STATUS_TRANSITIONS[record.status]:
            raise HarnessFactoryError(
                f"invalid run status transition: {record.status.value} -> {status.value}"
            )
        updated = HarnessRun(
            **{
                **record.__dict__,
                "status": status,
                "updated_at": _utc_now(),
            }
        )
        self._write_record(updated)
        return updated

    def cleanup(self, run_id: str, *, owner: str) -> HarnessRun:
        record = self.get_run(run_id)
        self._assert_owner(record, owner)
        if record.status is RunStatus.CLEANED:
            return record
        if record.status is RunStatus.RUNNING:
            raise HarnessFactoryError("cannot clean a running harness workspace")

        expected_workspace = (self.workspaces_root / record.run_id).resolve(
            strict=False
        )
        if record.workspace.resolve(strict=False) != expected_workspace:
            raise RunOwnershipError(
                "run workspace is not inside the managed workspaces root"
            )
        if record.workspace.is_symlink():
            raise RunOwnershipError("managed run workspace must not be a symlink")
        _verify_workspace_marker(record)

        registered = self._registered_worktrees()
        if record.workspace.resolve(strict=False) not in registered:
            if record.workspace.exists():
                raise RunOwnershipError("workspace is not a registered Git worktree")
            raise HarnessFactoryError(
                "run worktree is missing; preserving the run record for inspection"
            )

        changes = _git(
            record.workspace,
            "status",
            "--porcelain",
            "--untracked-files=all",
            "--ignored=matching",
            "--",
            ".",
            f":(exclude){_WORKSPACE_MARKER}",
        )
        if changes:
            raise HarnessFactoryError(
                "run workspace has uncommitted changes; preserving it: "
                f"{record.workspace}"
            )

        marker = record.workspace / _WORKSPACE_MARKER
        marker.unlink()
        try:
            _git(
                self.repo_root, "worktree", "remove", str(record.workspace), timeout=60
            )
        except HarnessFactoryError:
            try:
                _write_workspace_marker(record.workspace, record.run_id)
            except OSError as marker_error:
                raise HarnessFactoryError(
                    "worktree removal failed and its ownership marker could not be "
                    f"restored; inspect it manually: {record.workspace}"
                ) from marker_error
            raise
        cleaned = HarnessRun(
            **{
                **record.__dict__,
                "status": RunStatus.CLEANED,
                "updated_at": _utc_now(),
            }
        )
        self._write_record(cleaned)
        return cleaned

    def list_runs(self) -> tuple[HarnessRun, ...]:
        if not self.state_root.exists():
            return ()
        self._verify_root_marker()
        if self.records_root.is_symlink():
            raise HarnessFactoryError("runs directory must not be a symlink")
        if not self.records_root.exists():
            return ()
        if not self.records_root.is_dir():
            raise HarnessFactoryError("runs path is not a directory")
        records = [
            self.get_run(path.parent.name)
            for path in sorted(self.records_root.glob("*/run.json"))
            if not path.is_symlink()
        ]
        return tuple(records)

    def resolve_revision(self, revision: str) -> str:
        if not isinstance(revision, str) or not revision.strip():
            raise HarnessFactoryError("base_revision must be explicit")
        resolved = _git(
            self.repo_root,
            "rev-parse",
            "--verify",
            "--end-of-options",
            f"{revision}^{{commit}}",
        )
        if not re.fullmatch(r"[0-9a-f]{40,64}", resolved):
            raise HarnessFactoryError("base_revision did not resolve to a commit SHA")
        return resolved

    def _ensure_roots(self) -> None:
        for path in (self.state_root, self.records_root, self.workspaces_root):
            if path.is_symlink():
                raise HarnessFactoryError(
                    f"managed state path must not be a symlink: {path}"
                )
        if not self.state_root.exists():
            self.state_root.mkdir(parents=True, mode=0o700)
        if not self.state_root.is_dir():
            raise HarnessFactoryError("state_root must be a directory")
        marker = self.state_root / _ROOT_MARKER
        if marker.is_symlink():
            raise RunOwnershipError("state root marker must not be a symlink")
        if marker.exists():
            self._verify_root_marker()
        else:
            if any(self.state_root.iterdir()):
                raise HarnessFactoryError(
                    "state_root is non-empty and not owned by harness-factory"
                )
            try:
                with marker.open("x", encoding="utf-8") as stream:
                    stream.write(_ROOT_MARKER_CONTENT)
            except FileExistsError:
                self._verify_root_marker()
        self.records_root.mkdir(mode=0o700, exist_ok=True)
        self.workspaces_root.mkdir(mode=0o700, exist_ok=True)

    def _verify_root_marker(self) -> None:
        marker = self.state_root / _ROOT_MARKER
        if marker.is_symlink() or not marker.is_file():
            raise HarnessFactoryError(
                "state_root is not initialized by harness-factory"
            )
        try:
            content = marker.read_text(encoding="utf-8")
        except OSError as exc:
            raise HarnessFactoryError(
                "could not read harness-factory state marker"
            ) from exc
        if content != _ROOT_MARKER_CONTENT:
            raise HarnessFactoryError("state_root marker has an unknown format")

    def _record_path(self, run_id: str) -> Path:
        if not isinstance(run_id, str) or _RUN_ID_PATTERN.fullmatch(run_id) is None:
            raise HarnessFactoryError("run_id must be a lowercase 32-character UUID")
        return self.records_root / run_id / "run.json"

    def _write_record(self, record: HarnessRun) -> None:
        directory = record.state_directory
        if directory.is_symlink() or not directory.is_dir():
            raise HarnessFactoryError("run state directory is unavailable")
        destination = self._record_path(record.run_id)
        if destination.parent.resolve(strict=True) != directory.resolve(strict=True):
            raise RunOwnershipError(
                "run record path does not match its state directory"
            )
        if directory.name != record.run_id:
            raise RunOwnershipError("run state directory does not match its run ID")
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".run-",
            suffix=".tmp",
            dir=directory,
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                os.fchmod(stream.fileno(), 0o600)
                json.dump(record.as_dict(), stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            os.replace(temporary, destination)
        except OSError:
            try:
                temporary.unlink(missing_ok=True)
            finally:
                raise

    def _parse_record(self, raw: Any, state_directory: Path) -> HarnessRun:
        required = {
            "schema_version",
            "run_id",
            "harness",
            "base_revision",
            "workspace",
            "state_directory",
            "mode",
            "owner",
            "status",
            "created_at",
            "updated_at",
            "allowed_mutations",
            "origin_harness",
            "call_depth",
            "cross_harness_request",
        }
        if not isinstance(raw, dict) or set(raw) != required:
            raise HarnessFactoryError("run record has invalid fields")
        if type(raw["schema_version"]) is not int or raw["schema_version"] != 1:
            raise HarnessFactoryError("run record schema_version must be 1")
        if raw["state_directory"] != str(state_directory):
            raise RunOwnershipError(
                "run record state directory does not match its location"
            )
        if not isinstance(raw["run_id"], str) or state_directory.name != raw["run_id"]:
            raise RunOwnershipError("run record ID does not match its state directory")
        if not isinstance(raw["workspace"], str):
            raise HarnessFactoryError("run workspace must be a path string")
        request_raw = raw["cross_harness_request"]
        request = None
        if request_raw is not None:
            request_fields = {
                "run_id",
                "requested_by",
                "target_harness",
                "purpose",
                "artifact_under_test",
                "base_revision",
                "allowed_mutations",
                "timeout_or_budget",
                "expected_output",
                "origin_harness",
                "call_depth",
            }
            if not isinstance(request_raw, dict) or set(request_raw) != request_fields:
                raise HarnessFactoryError(
                    "cross_harness_request must be an object or null"
                )
            try:
                request = CrossHarnessRequest(
                    run_id=request_raw["run_id"],
                    requested_by=request_raw["requested_by"],
                    target_harness=request_raw["target_harness"],
                    purpose=Purpose(request_raw["purpose"]),
                    artifact_under_test=request_raw["artifact_under_test"],
                    base_revision=request_raw["base_revision"],
                    allowed_mutations=request_raw["allowed_mutations"],
                    timeout_or_budget=request_raw["timeout_or_budget"],
                    expected_output=request_raw["expected_output"],
                    origin_harness=request_raw["origin_harness"],
                    call_depth=request_raw["call_depth"],
                )
            except (TypeError, ValueError) as exc:
                raise HarnessFactoryError(
                    "run record contains invalid cross-harness request values"
                ) from exc
        try:
            record = HarnessRun(
                run_id=raw["run_id"],
                harness=raw["harness"],
                base_revision=raw["base_revision"],
                workspace=Path(raw["workspace"]),
                state_directory=state_directory,
                mode=RunMode(raw["mode"]),
                owner=raw["owner"],
                status=RunStatus(raw["status"]),
                created_at=raw["created_at"],
                updated_at=raw["updated_at"],
                allowed_mutations=raw["allowed_mutations"],
                origin_harness=raw["origin_harness"],
                call_depth=raw["call_depth"],
                cross_harness_request=request,
            )
        except (TypeError, ValueError) as exc:
            raise HarnessFactoryError("run record contains invalid values") from exc
        return record

    def _registered_worktrees(self) -> set[Path]:
        listing = _git(self.repo_root, "worktree", "list", "--porcelain")
        paths: set[Path] = set()
        for line in listing.splitlines():
            if line.startswith("worktree "):
                paths.add(Path(line.removeprefix("worktree ")).resolve(strict=False))
        return paths

    @staticmethod
    def _assert_owner(record: HarnessRun, owner: str) -> None:
        if not isinstance(owner, str) or owner != record.owner:
            raise RunOwnershipError("run operation requested by a non-owner")


def _write_workspace_marker(workspace: Path, run_id: str) -> None:
    marker = workspace / _WORKSPACE_MARKER
    descriptor = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        stream.write(f"{run_id}\n")


def _verify_workspace_marker(record: HarnessRun) -> None:
    marker = record.workspace / _WORKSPACE_MARKER
    if marker.is_symlink() or not marker.is_file():
        raise RunOwnershipError("run workspace ownership marker is missing or unsafe")
    try:
        content = marker.read_text(encoding="utf-8")
    except OSError as exc:
        raise RunOwnershipError("run workspace ownership marker is unreadable") from exc
    if content != f"{record.run_id}\n":
        raise RunOwnershipError("run workspace ownership marker does not match the run")
