from __future__ import annotations

import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


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
    task_files = set()
    for task_path in (root / "tasks").glob("*.yaml"):
        task_files.add(task_path.stem)
        try:
            task_payload = yaml.safe_load(task_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise ValueError(f"invalid task YAML: {task_path}") from exc
        if not isinstance(task_payload, dict) or task_payload.get("id") != task_path.stem:
            raise ValueError(f"task id does not match filename: {task_path}")
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


_BENCHMARK_ALLOWED_IMPORTS = {"typer", "yaml"}


def _package_import_roots(package_root: Path) -> set[str]:
    roots = {path.stem for path in package_root.rglob("*.py")}
    roots.update(path.name for path in package_root.iterdir() if path.is_dir())
    return roots


def _script_is_self_contained(
    path: Path,
    package_root: Path,
    allowed_imports: set[str] | None = None,
) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return False
    allowed = set(sys.stdlib_module_names) | (allowed_imports or set())
    package_imports = _package_import_roots(package_root)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(
                alias.name.split(".")[0] not in allowed
                and alias.name.split(".")[0] not in package_imports
                for alias in node.names
            ):
                return False
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            root = (node.module or "").split(".")[0]
            if root not in allowed and root not in package_imports:
                return False
    return True


def _safe_candidate_path(candidate_root: Path, relative: str, base: Path | None = None) -> Path | None:
    candidate_root = candidate_root.resolve()
    raw_path = Path(relative)
    if raw_path.is_absolute():
        return None
    base = (base or candidate_root).resolve()
    resolved = (base / raw_path).resolve()
    try:
        resolved.relative_to(candidate_root)
    except ValueError:
        return None
    return resolved


def evaluate_task(task_id: str, task_metadata: dict[str, Any], candidate_root: Path) -> OracleResult:
    required_paths = [str(path) for path in task_metadata.get("required_paths", [])]
    required_support = [str(path) for path in task_metadata.get("required_support_files", [])]
    fixture_root = candidate_root / "fixtures"
    package_root = candidate_root / ".github/skills/create-skill"
    checks: dict[str, bool] = {}
    failures: list[str] = []

    resolved_paths = {path: _safe_candidate_path(candidate_root, path) for path in required_paths}
    invalid_paths = [path for path, resolved in resolved_paths.items() if resolved is None]
    missing_paths = [
        path for path, resolved in resolved_paths.items() if resolved is not None and not resolved.is_file()
    ]
    checks["package_shape"] = not invalid_paths and not missing_paths
    if invalid_paths:
        failures.append(f"required package paths escape candidate root: {', '.join(invalid_paths)}")
    if missing_paths:
        failures.append(f"missing required package paths: {', '.join(missing_paths)}")

    changed_support = []
    missing_support = []
    resolved_support = {
        relative: _safe_candidate_path(candidate_root, relative, package_root)
        for relative in required_support
    }
    invalid_support = [relative for relative, resolved in resolved_support.items() if resolved is None]
    for relative in required_support:
        candidate_path = resolved_support[relative]
        fixture_path = _safe_candidate_path(fixture_root, relative, fixture_root / ".github/skills/create-skill")
        if candidate_path is None or fixture_path is None:
            continue
        if not fixture_path.is_file() or not candidate_path.is_file():
            missing_support.append(relative)
        elif candidate_path.read_bytes() != fixture_path.read_bytes():
            changed_support.append(relative)
    checks["support_files"] = not invalid_support and not missing_support and not changed_support
    if invalid_support:
        failures.append(f"required support paths escape candidate root: {', '.join(invalid_support)}")
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
        and resolved_support[relative] is not None
        and resolved_support[relative].is_file()
        and not _script_is_self_contained(
            resolved_support[relative], package_root, _BENCHMARK_ALLOWED_IMPORTS
        )
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