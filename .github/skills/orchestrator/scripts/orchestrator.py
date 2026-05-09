"""Orchestrator helper API moved into the orchestrator skill.

Provides lightweight helpers used by agents and unit tests for manifest
validation, payload validation, file access checks, and writing orchestration
records. This file replaces the previous copy that lived in the `scripts`
skill and the legacy `.github/scripts/` folder.
"""
import os
import re
import json
from datetime import datetime
from typing import Any, Dict, List


def validate_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    required = [
        "worktree_path",
        "branch",
        "commit_shas",
        "pr_url",
        "pr_number",
    ]
    missing = [k for k in required if k not in manifest]
    if missing:
        return {"error": "MALFORMED_MANIFEST", "missing": missing}
    return {"ok": True}


def extract_manifest_info(manifest: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "worktree_path": manifest.get("worktree_path"),
        "branch": manifest.get("branch"),
        "commit_shas": manifest.get("commit_shas"),
        "pr_url": manifest.get("pr_url"),
        "pr_number": manifest.get("pr_number"),
    }


def validate_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing = []
    if not isinstance(payload, dict):
        return {"error": "MISSING_PAYLOAD", "missing": ["manifest", "plan_snapshot"]}

    if "manifest" not in payload:
        missing.append("manifest")
    if "plan_snapshot" not in payload:
        missing.append("plan_snapshot")

    if missing:
        return {"error": "MISSING_PAYLOAD", "missing": missing}

    manifest = payload.get("manifest", {})
    # Enforce Copilot manifest contract only when Copilot keys are present.
    copilot_keys = ["worktree_path", "branch", "commit_shas", "pr_url", "pr_number"]
    if any(k in manifest for k in copilot_keys):
        mv = validate_manifest(manifest)
        if mv.get("error"):
            return mv

    return {"ok": True}

def generate_next_task_id(history_dir: str = ".github/plan_history", prefix: str = "task_") -> str:
    """Generate a simple incremental task id by scanning the orchestration
    history directory for prior task ids. Returns prefix + integer.

    This is intentionally simple (1,2,3) to support lightweight workflows.
    """
    try:
        os.makedirs(history_dir, exist_ok=True)
        entries = os.listdir(history_dir)
    except Exception:
        entries = []

    nums: List[int] = []
    for e in entries:
        # common patterns: task_1.json, task-2.json, task1.PLAN.2026.md
        m = re.search(r"task[_-]?(\d+)", e)
        if m:
            try:
                nums.append(int(m.group(1)))
            except Exception:
                continue
        else:
            m2 = re.search(r"task.*?(\d+)", e)
            if m2:
                try:
                    nums.append(int(m2.group(1)))
                except Exception:
                    continue

    next_num = max(nums) + 1 if nums else 1
    return f"{prefix}{next_num}"


def create_manifest_if_missing(manifest: Any, history_dir: str = ".github/plan_history", default_title: str = None, default_description: str = None) -> Dict[str, Any]:
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
    description = default_description or f"Auto-generated manifest for {task_id}. Review and expand before dispatch."

    generated = {
        "id": task_id,
        "title": title,
        "description": description,
        "change_type": "patch",
        "plan_index": {"repo_structure": [], "sections": []},
        "test_commands": [],
        "risk_level": "low",
        "apply_policy": "require_manual",
    }
    return generated


def write_orchestration_record(task_id: str, manifest: Dict[str, Any], plans: List[Any], responses: List[Any], status: str, history_dir: str = ".") -> str:
    os.makedirs(history_dir, exist_ok=True)

    # Defensive: do NOT invent or propagate non-dict manifests.
    # If callers mistakenly pass the task id or another non-dict value as the
    # `manifest` argument, record an explicit sentinel so auditors can see
    # that no authoritative manifest object was provided.
    manifest_to_write = manifest if isinstance(manifest, dict) else "no_manifest_found"

    record = {
        "task_id": task_id,
        "manifest": manifest_to_write,
        "plans": plans,
        "responses": responses,
        "status": status,
        "created_at": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
    }

    # If a canonical plan file exists in the repo, snapshot it into the
    # orchestration history for auditability. This is non-destructive and
    # best-effort: failures to snapshot are recorded in the orchestration
    # record but do not prevent writing the main record.
    try:
        plan_src = os.path.join(os.getcwd(), ".github", "PLAN.md")
        if os.path.isfile(plan_src):
            ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            snapshot_name = f"{task_id}.PLAN.{ts}.md"
            snapshot_path = os.path.join(history_dir, snapshot_name)
            with open(plan_src, "r", encoding="utf-8") as pf:
                plan_content = pf.read()
            with open(snapshot_path, "w", encoding="utf-8") as sf:
                sf.write(plan_content)
            record["plan_snapshot_path"] = snapshot_path
    except Exception as e:
        record["plan_snapshot_error"] = str(e)

    path = os.path.join(history_dir, f"{task_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f)
    return path
