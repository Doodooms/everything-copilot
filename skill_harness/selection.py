from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .manifest import canonical_hash


@dataclass(frozen=True)
class SelectionConstraints:
    max_false_positive_final_rate: float = 0.0
    min_false_positive_recovery_rate: float = 0.0
    min_reject_route_accuracy: float = 0.0
    max_unexpected_workflow_entry_rate: float = 0.0
    max_post_sentinel_tool_calls: int = 0


@dataclass(frozen=True)
class ArchitectureResult:
    architecture_id: str
    metrics: dict[str, Any]


def _passes(result: ArchitectureResult, constraints: SelectionConstraints) -> bool:
    metrics = result.metrics
    return (
        metrics.get("false_positive_final_rate", 1.0) <= constraints.max_false_positive_final_rate
        and metrics.get("false_positive_recovery_rate", 0.0) >= constraints.min_false_positive_recovery_rate
        and metrics.get("reject_route_accuracy", 0.0) >= constraints.min_reject_route_accuracy
        and metrics.get("unexpected_workflow_entry_rate", 1.0)
        <= constraints.max_unexpected_workflow_entry_rate
        and metrics.get("post_sentinel_tool_calls", 1) <= constraints.max_post_sentinel_tool_calls
    )


def select_architecture(
    results: list[ArchitectureResult], constraints: SelectionConstraints
) -> tuple[ArchitectureResult | None, dict[str, Any]]:
    passing = [result for result in results if _passes(result, constraints)]
    passing.sort(
        key=lambda result: (
            result.metrics.get("discovery", {}).get("f1", 0.0),
            result.metrics.get("admission", {}).get("f1", 0.0),
            result.metrics.get("reject_route_accuracy", 0.0),
            -result.metrics.get("tool_calls", {}).get("mean", 0.0),
            -result.metrics.get("tokens", {}).get("mean", 0.0),
        ),
        reverse=True,
    )
    selected = passing[0] if passing else None
    report = {
        "constraints": constraints.__dict__,
        "selected": selected.architecture_id if selected else None,
        "passing": [result.architecture_id for result in passing],
        "rejected": [result.architecture_id for result in results if result not in passing],
    }
    return selected, report


def write_selection_report(path: Path, report: dict[str, Any]) -> None:
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_canonical_architecture(path: Path, architecture: dict[str, Any]) -> None:
    payload = dict(architecture)
    payload["selection_hash"] = canonical_hash(payload)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
