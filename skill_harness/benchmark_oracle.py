from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class OracleResult:
    passed: bool
    checks: dict[str, bool]
    failures: tuple[str, ...]
    metadata: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "checks": self.checks,
            "failures": list(self.failures),
            "metadata": self.metadata,
        }


def load_oracle_manifest(root: Path) -> dict[str, dict[str, Any]]:
    path = root / "adapter_manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    tasks = payload.get("tasks")
    if not isinstance(tasks, dict):
        raise ValueError(f"adapter manifest tasks must be a mapping: {path}")
    task_files = {task.stem for task in (root / "tasks").glob("*.yaml")}
    manifest_tasks = set(tasks)
    if task_files != manifest_tasks:
        missing = sorted(task_files - manifest_tasks)
        extra = sorted(manifest_tasks - task_files)
        details = []
        if missing:
            details.append(f"missing metadata for: {', '.join(missing)}")
        if extra:
            details.append(f"metadata has no task: {', '.join(extra)}")
        raise ValueError(f"adapter manifest does not match Waza tasks: {'; '.join(details)}")
    for task_id, metadata in tasks.items():
        if not isinstance(metadata, dict):
            raise ValueError(f"oracle metadata must be an object: {task_id}")
        if metadata.get("task_id") != task_id:
            raise ValueError(f"oracle metadata task_id mismatch: {task_id}")
        if not isinstance(metadata.get("should_trigger"), bool):
            raise ValueError(f"oracle metadata should_trigger must be boolean: {task_id}")
        if not isinstance(metadata.get("family"), str):
            raise ValueError(f"oracle metadata family must be a string: {task_id}")
    return tasks


def _mentions_provenance(text: str, provenance_path: str) -> bool:
    return provenance_path in text or Path(provenance_path).name in text


def _script_is_self_contained(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return False
    forbidden = {"skill_harness", "skillopt", "waza"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[0] in forbidden for alias in node.names):
                return False
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            if (node.module or "").split(".")[0] in forbidden:
                return False
    return True


def evaluate_task(task_id: str, task_metadata: dict[str, Any], candidate_root: Path) -> OracleResult:
    required_paths = [str(path) for path in task_metadata.get("required_paths", [])]
    required_support = [str(path) for path in task_metadata.get("required_support_files", [])]
    fixture_root = candidate_root / "fixtures"
    checks: dict[str, bool] = {}
    failures: list[str] = []

    missing_paths = [path for path in required_paths if not (candidate_root / path).is_file()]
    checks["package_shape"] = not missing_paths
    if missing_paths:
        failures.append(f"missing required package paths: {', '.join(missing_paths)}")

    changed_support = []
    missing_support = []
    for relative in required_support:
        candidate_path = candidate_root / ".github/skills/create-skill" / relative
        fixture_path = fixture_root / ".github/skills/create-skill" / relative
        if not fixture_path.is_file() or not candidate_path.is_file():
            missing_support.append(relative)
        elif candidate_path.read_bytes() != fixture_path.read_bytes():
            changed_support.append(relative)
    checks["support_files"] = not missing_support and not changed_support
    if missing_support:
        failures.append(f"missing required frozen support files: {', '.join(missing_support)}")
    if changed_support:
        failures.append(f"frozen support files were mutated: {', '.join(changed_support)}")

    skill_path = candidate_root / ".github/skills/create-skill/SKILL.md"
    provenance_path = str(task_metadata.get("provenance_path", ""))
    skill_text = skill_path.read_text(encoding="utf-8") if skill_path.is_file() else ""
    provenance_ok = (candidate_root / provenance_path).is_file() and _mentions_provenance(
        skill_text, provenance_path
    )
    checks["provenance"] = provenance_ok
    if not provenance_ok:
        failures.append(f"candidate does not preserve provenance: {provenance_path}")

    script_failures = [
        relative
        for relative in required_support
        if relative.startswith("scripts/")
        and (candidate_root / ".github/skills/create-skill" / relative).is_file()
        and not _script_is_self_contained(candidate_root / ".github/skills/create-skill" / relative)
    ]
    checks["script_self_containment"] = not script_failures
    if script_failures:
        failures.append(f"non-self-contained scripts: {', '.join(script_failures)}")

    should_trigger = bool(task_metadata.get("should_trigger", True))
    routing_ok = isinstance(task_metadata.get("family"), str)
    if not should_trigger:
        routing_ok = routing_ok and task_metadata.get("family") == "routing-near-miss"
    checks["routing_metadata"] = routing_ok
    if not routing_ok:
        failures.append("routing metadata does not describe a deterministic near-miss gate")

    metadata = {
        "task_id": task_id,
        "family": task_metadata.get("family"),
        "should_trigger": should_trigger,
        "support_files_optimized": False,
        "support_files_source": "frozen fixture",
        "required_support_files": required_support,
        "downstream_execution": "unavailable; Waza judges package guidance only",
    }
    return OracleResult(not failures, checks, tuple(failures), metadata)


_UNAUTHORIZED_RESULT = re.compile(
    r"(?:create[- ]skill|skill package|\.github/skills/|\bSKILL\.md\b)", re.IGNORECASE
)


def apply_routing_gate(row: dict[str, Any], should_trigger: bool) -> tuple[bool, str | None]:
    if should_trigger:
        return True, None
    evidence = " ".join(
        str(row.get(key, ""))
        for key in ("output", "final_output", "response", "rationale", "text")
    )
    if _UNAUTHORIZED_RESULT.search(evidence):
        return False, "near-miss response indicates an unauthorized create-skill result"
    return True, None