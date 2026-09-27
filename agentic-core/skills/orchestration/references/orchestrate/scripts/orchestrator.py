# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.21,<5"]
# ///
"""Validate and persist the Orchestrator's manifest and task event ledgers."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from validate_exchange import validate_document

TASK_STATUSES = {
    "planned",
    "queued",
    "running",
    "completed",
    "partial",
    "failed",
    "blocked",
    "unknown",
    "cancelled",
}
TASK_TRANSITIONS = {
    None: {"planned", "queued"},
    "planned": {"queued", "cancelled"},
    "queued": {"running", "blocked", "cancelled"},
    "running": {
        "running",
        "completed",
        "partial",
        "failed",
        "blocked",
        "unknown",
        "cancelled",
    },
    "partial": {"queued", "running", "completed", "failed", "blocked", "cancelled"},
    "failed": {"queued", "cancelled"},
    "blocked": {"queued", "cancelled"},
    "unknown": {"queued", "running", "failed", "blocked", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}


def _timestamp() -> str:
    return (
        datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    )


def _validate_id(value: str, field: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value
    ):
        raise ValueError(f"{field} must be a 1-64 character path-safe identifier")
    return value


def _absolute_path_argument(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        raise argparse.ArgumentTypeError(
            "must be an absolute path; skill commands run from the skill directory"
        )
    return path


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")


def validate_manifest(
    manifest: dict[str, Any], repo: str | Path | None = None
) -> dict[str, Any]:
    errors = validate_document("manifest", manifest, repo=repo)
    if errors:
        return {"error": "MALFORMED_MANIFEST", "details": errors}
    return {"ok": True}


def extract_manifest_info(manifest: dict[str, Any]) -> dict[str, Any]:
    branch_name = manifest.get("branch_name", manifest.get("branch"))
    return {
        "worktree_path": manifest.get("worktree_path"),
        "branch_name": branch_name,
        "branch": branch_name,
        "commit_shas": manifest.get("commit_shas"),
        "pr_url": manifest.get("pr_url"),
        "pr_number": manifest.get("pr_number"),
    }


def validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    missing = []
    if not isinstance(payload, dict):
        return {"error": "MISSING_PAYLOAD", "missing": ["manifest"]}

    if "manifest" not in payload:
        missing.append("manifest")

    if missing:
        return {"error": "MISSING_PAYLOAD", "missing": missing}

    manifest = payload.get("manifest", {})
    if not isinstance(manifest, dict):
        return {"error": "MALFORMED_MANIFEST", "reason": "manifest must be an object"}
    mv = validate_manifest(manifest)
    if mv.get("error"):
        return mv

    return {"ok": True}


def generate_next_task_id(
    history_dir: str = "docs/harness-history", prefix: str = "task_"
) -> str:
    """Generate the next task id from task directories or manifest filenames."""
    root = Path(history_dir)
    if not root.exists():
        return f"{prefix}1"
    if not root.is_dir():
        raise NotADirectoryError(f"task history root is not a directory: {root}")

    nums = []
    for entry in root.iterdir():
        match = re.fullmatch(rf"{re.escape(prefix)}(\d+)", entry.name)
        if match:
            nums.append(int(match.group(1)))
    next_num = max(nums, default=0) + 1
    return f"{prefix}{next_num}"


def create_manifest_if_missing(
    manifest: Any,
    history_dir: str = "docs/harness-history",
    default_title: str | None = None,
    default_description: str | None = None,
) -> dict[str, Any]:
    """If `manifest` is not a dict, generate a minimal manifest object.

    The generated manifest is intentionally minimal and must be reviewed by
    the user or the Orchestrator before being used to dispatch work to
    subagents. This helper exists to support conversational flows where the
    Orchestrator is asked to 'create' a task without a pre-made manifest.
    """
    if isinstance(manifest, dict):
        return manifest

    task_id = generate_next_task_id(history_dir=history_dir)
    title = default_title or f"Auto-generated task {task_id}"
    description = (
        default_description
        or f"Auto-generated manifest for {task_id}. Review and expand before dispatch."
    )

    generated = {
        "id": task_id,
        "title": title,
        "description": description,
        "status": "planned",
        "updated_at": _timestamp(),
        "lifecycle": {
            "branch": None,
            "worktree": None,
            "commit_shas": [],
            "pull_request": None,
            "cleanup": "not_requested",
            "commit_status": "not_applicable",
            "commit_reason": "No repository commit is associated with this generated manifest.",
        },
    }
    return generated


def write_orchestration_record(
    task_id: str,
    manifest: dict[str, Any],
    plans: list[Any],
    responses: list[Any],
    status: str,
    history_dir: str = "docs/harness-history",
    repo: str | Path | None = None,
) -> str:
    task_id = _validate_id(task_id, "task_id")
    if not isinstance(manifest, dict):
        raise TypeError("manifest must be an object")
    if status not in {
        "planned",
        "in_progress",
        "success",
        "partial",
        "failed",
        "blocked",
    }:
        raise ValueError(f"unsupported orchestration status: {status}")
    if manifest["id"] != task_id:
        raise ValueError("task_id must match manifest.id")
    manifest = {**manifest, "status": status, "updated_at": _timestamp()}
    validation_errors = validate_document("manifest", manifest, repo=repo)
    if validation_errors:
        raise ValueError(
            "invalid orchestration manifest: " + "; ".join(validation_errors)
        )

    root = Path(history_dir)
    task_dir = root / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = task_dir / "manifest.json"

    record = {
        "task_id": task_id,
        "manifest": manifest,
        "status": status,
        "updated_at": _timestamp(),
    }
    record_errors = validate_document("manifest-record", record, repo=repo)
    if record_errors:
        raise ValueError("invalid orchestration record: " + "; ".join(record_errors))

    event_record = _prepare_harness_event(
        task_id,
        {
            "type": "orchestration_result",
            "status": status,
            "plan_refs": _artifact_refs(plans),
            "specialist_returns": responses,
        },
        repo=repo,
    )

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=task_dir,
            prefix=".manifest-",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            json.dump(record, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary_path, manifest_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    _append_jsonl(task_dir / "events.jsonl", event_record)
    return str(manifest_path)


def _artifact_refs(artifacts: list[Any]) -> list[Any]:
    references = []
    for artifact in artifacts:
        if isinstance(artifact, str):
            references.append(artifact)
        elif isinstance(artifact, dict):
            reference = {
                key: artifact[key]
                for key in ("id", "revision", "path", "status")
                if key in artifact
            }
            if reference:
                references.append(reference)
    return references


def append_harness_event(
    task_id: str,
    event: dict[str, Any],
    history_dir: str = "docs/harness-history",
    repo: str | Path | None = None,
) -> str:
    record = _prepare_harness_event(task_id, event, repo=repo)
    path = Path(history_dir) / task_id / "events.jsonl"
    _append_jsonl(path, record)
    return str(path)


def _prepare_harness_event(
    task_id: str,
    event: dict[str, Any],
    *,
    repo: str | Path | None = None,
) -> dict[str, Any]:
    task_id = _validate_id(task_id, "task_id")
    if (
        not isinstance(event, dict)
        or not isinstance(event.get("type"), str)
        or not event["type"]
    ):
        raise ValueError("event must be an object with a non-empty type")
    if event.get("schema_version") == "1.0.0":
        record = {**event, "task_id": task_id, "timestamp": _timestamp()}
    else:
        status = event.get("status")
        if not isinstance(status, str) or not status:
            raise ValueError("event must include a non-empty status")
        record = {
            "schema_version": "1.0.0",
            "event_id": str(uuid4()),
            "task_id": task_id,
            "timestamp": _timestamp(),
            "type": event["type"],
            "status": status,
            "data": {
                key: value
                for key, value in event.items()
                if key
                not in {
                    "schema_version",
                    "event_id",
                    "task_id",
                    "timestamp",
                    "type",
                    "status",
                }
            },
        }
    validation_errors = validate_document("event", record, repo=repo)
    if validation_errors:
        raise ValueError("invalid orchestration event: " + "; ".join(validation_errors))
    return record


def _read_task_status(path: Path, task_id: str) -> str | None:
    if not path.exists():
        return None
    latest = None
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"invalid task event at {path}:{line_number}: {exc}"
                ) from exc
            if not isinstance(event, dict):
                raise TypeError(
                    f"invalid task event at {path}:{line_number}: expected an object"
                )
            if event.get("schema_version") == "1.0.0":
                validation_errors = validate_document("transition", event)
                if validation_errors:
                    raise ValueError(
                        f"invalid task event at {path}:{line_number}: "
                        + "; ".join(validation_errors)
                    )
            if event.get("task_id") == task_id:
                latest = event.get("status")
                if latest not in TASK_STATUSES:
                    raise ValueError(
                        f"invalid task status at {path}:{line_number}: {latest!r}"
                    )
    return latest


def append_task_event(
    history_id: str,
    task_id: str,
    status: str,
    *,
    attempt_id: str | None = None,
    agent_id: str | None = None,
    evidence: Any = None,
    history_dir: str = "docs/tasks-history",
) -> str:
    history_id = _validate_id(history_id, "history_id")
    task_id = _validate_id(task_id, "task_id")
    if status not in TASK_STATUSES:
        raise ValueError(f"unsupported task status: {status}")
    if attempt_id is not None:
        _validate_id(attempt_id, "attempt_id")
    if agent_id is not None:
        _validate_id(agent_id, "agent_id")

    path = Path(history_dir) / f"{history_id}.jsonl"
    previous = _read_task_status(path, task_id)
    if status not in TASK_TRANSITIONS[previous]:
        raise ValueError(
            f"invalid task transition for {task_id}: {previous!r} -> {status!r}"
        )

    event = {
        "schema_version": "1.0.0",
        "event_id": str(uuid4()),
        "parent_task_id": history_id,
        "task_id": task_id,
        "attempt_id": attempt_id,
        "agent_id": agent_id,
        "status": status,
        "timestamp": _timestamp(),
        "evidence": [] if evidence is None else evidence,
    }
    validation_errors = validate_document("transition", event)
    if validation_errors:
        raise ValueError(
            "invalid task transition event: " + "; ".join(validation_errors)
        )
    _append_jsonl(path, event)
    return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    next_id = commands.add_parser("next-task-id", help="print the next task ID")
    next_id.add_argument(
        "--history-dir",
        required=True,
        type=_absolute_path_argument,
        help="absolute path to the target workspace's harness-history directory",
    )

    write_manifest = commands.add_parser(
        "record-manifest", help="validate and persist a manifest"
    )
    write_manifest.add_argument(
        "--manifest",
        required=True,
        type=_absolute_path_argument,
        help="absolute path to the target workspace manifest file",
    )
    write_manifest.add_argument("--status", required=True)
    write_manifest.add_argument(
        "--repo",
        type=_absolute_path_argument,
        help="absolute repository path for base/commit reference verification",
    )
    write_manifest.add_argument(
        "--history-dir",
        required=True,
        type=_absolute_path_argument,
        help="absolute path to the target workspace's harness-history directory",
    )

    harness_event = commands.add_parser(
        "append-harness-event",
        help="append a structured orchestration or handoff event",
    )
    harness_event.add_argument("task_id")
    harness_event.add_argument("--event", required=True, help="event JSON object")
    harness_event.add_argument(
        "--repo",
        type=_absolute_path_argument,
        help="absolute repository path for Git/artifact reference verification",
    )
    harness_event.add_argument(
        "--history-dir",
        required=True,
        type=_absolute_path_argument,
        help="absolute path to the target workspace's harness-history directory",
    )

    task_event = commands.add_parser(
        "append-task-event", help="append a task status transition"
    )
    task_event.add_argument("history_id")
    task_event.add_argument("task_id")
    task_event.add_argument("status", choices=sorted(TASK_STATUSES))
    task_event.add_argument("--attempt-id")
    task_event.add_argument("--agent-id")
    task_event.add_argument("--evidence", help="evidence JSON object")
    task_event.add_argument(
        "--history-dir",
        required=True,
        type=_absolute_path_argument,
        help="absolute path to the target workspace's task-history directory",
    )

    args = parser.parse_args(argv)
    if args.command == "next-task-id":
        print(generate_next_task_id(str(args.history_dir)))
    elif args.command == "record-manifest":
        payload = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("manifest file must contain a JSON object")
        if "manifest" in payload:
            manifest = payload["manifest"]
            if not isinstance(manifest, dict):
                raise ValueError("manifest envelope field 'manifest' must be an object")
            envelope_errors = validate_document(
                "manifest-record", payload, repo=args.repo
            )
            if envelope_errors:
                raise ValueError(
                    "invalid manifest envelope: " + "; ".join(envelope_errors)
                )
            if payload.get("task_id") is not None and payload.get(
                "task_id"
            ) != manifest.get("id"):
                raise ValueError("manifest envelope task_id must match manifest.id")
        else:
            manifest = payload
        manifest = {**manifest, "status": args.status}
        path = write_orchestration_record(
            manifest.get("id"),
            manifest,
            plans=[manifest.get("plan_ref", {})],
            responses=[],
            status=args.status,
            history_dir=str(args.history_dir),
            repo=args.repo,
        )
        print(path)
    elif args.command == "append-harness-event":
        event = json.loads(args.event)
        if not isinstance(event, dict):
            raise ValueError("event must be a JSON object")
        path = append_harness_event(
            args.task_id,
            event,
            history_dir=str(args.history_dir),
            repo=args.repo,
        )
        print(path)
    elif args.command == "append-task-event":
        evidence = json.loads(args.evidence) if args.evidence is not None else None
        path = append_task_event(
            args.history_id,
            args.task_id,
            args.status,
            attempt_id=args.attempt_id,
            agent_id=args.agent_id,
            evidence=evidence,
            history_dir=str(args.history_dir),
        )
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
