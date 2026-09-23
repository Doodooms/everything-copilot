from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, median, pvariance
from typing import Iterable


@dataclass(frozen=True)
class RoutingTrial:
    expected_route: str | None
    actual_route: str | None
    discovery_expected: bool
    discovery_actual: bool
    admission_expected: bool | None = None
    admission_actual: bool | None = None
    tool_calls: int = 0
    tokens: int = 0
    sentinel_events: int = 0
    post_sentinel_tool_calls: int = 0


@dataclass(frozen=True)
class NumericSummary:
    mean: float
    median: float
    p95: float
    variance: float


def summarize(values: Iterable[int | float]) -> NumericSummary:
    numbers = [float(value) for value in values]
    if not numbers:
        return NumericSummary(0.0, 0.0, 0.0, 0.0)
    ordered = sorted(numbers)
    index = min(len(ordered) - 1, int((len(ordered) - 1) * 0.95))
    return NumericSummary(mean(numbers), median(numbers), ordered[index], pvariance(numbers))


def _binary_rates(values: list[tuple[bool, bool]]) -> tuple[float, float, float]:
    if not values:
        return 0.0, 0.0, 0.0
    true_positive = sum(expected and actual for expected, actual in values)
    false_positive = sum(not expected and actual for expected, actual in values)
    false_negative = sum(expected and not actual for expected, actual in values)
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def aggregate_trials(trials: Iterable[RoutingTrial]) -> dict[str, object]:
    rows = list(trials)
    discovery = _binary_rates([(row.discovery_expected, row.discovery_actual) for row in rows])
    admission_rows = [
        (row.admission_expected, row.admission_actual)
        for row in rows
        if row.admission_expected is not None and row.admission_actual is not None
    ]
    false_positive_discovery = sum(not row.discovery_expected and row.discovery_actual for row in rows)
    false_negative_discovery = sum(row.discovery_expected and not row.discovery_actual for row in rows)
    rejected_discovered = [row for row in rows if not row.discovery_expected and row.discovery_actual]
    return {
        "trial_count": len(rows),
        "discovery": {"precision": discovery[0], "recall": discovery[1], "f1": discovery[2]},
        "discovery_false_positive_rate": false_positive_discovery / len(rows) if rows else 0.0,
        "discovery_false_negative_rate": false_negative_discovery / len(rows) if rows else 0.0,
        "route_accuracy": (
            sum(row.expected_route == row.actual_route for row in rows if row.expected_route is not None)
            / sum(row.expected_route is not None for row in rows)
            if any(row.expected_route is not None for row in rows)
            else 0.0
        ),
        "no_route_rate": sum(row.actual_route is None for row in rows) / len(rows) if rows else 0.0,
        "admission": {
            "precision": _binary_rates(admission_rows)[0],
            "recall": _binary_rates(admission_rows)[1],
            "f1": _binary_rates(admission_rows)[2],
        },
        "false_positive_recovery_rate": (
            sum(row.admission_actual is False for row in rejected_discovered) / len(rejected_discovered)
            if rejected_discovered else 0.0
        ),
        "false_positive_final_rate": (
            sum(row.sentinel_events > 0 for row in rejected_discovered) / len(rejected_discovered)
            if rejected_discovered else 0.0
        ),
        "reject_route_accuracy": (
            sum(row.actual_route == row.expected_route for row in rows if row.expected_route is not None)
            / sum(row.expected_route is not None for row in rows)
            if any(row.expected_route is not None for row in rows) else 0.0
        ),
        "reject_without_route_rate": sum(
            row.actual_route is None for row in rows if row.admission_actual is False
        ) / sum(row.admission_actual is False for row in rows)
        if any(row.admission_actual is False for row in rows) else 0.0,
        "expected_workflow_entry_rate": sum(
            row.discovery_expected and row.admission_expected is True for row in rows
        ) / len(rows) if rows else 0.0,
        "unexpected_workflow_entry_rate": sum(
            row.discovery_expected is False and row.sentinel_events > 0 for row in rows
        ) / len(rows) if rows else 0.0,
        "workflow_entry_after_reject": sum(
            row.admission_expected is False and row.actual_route is not None for row in rows
        ),
        "post_sentinel_tool_calls": sum(row.post_sentinel_tool_calls for row in rows),
        "tokens": summarize(row.tokens for row in rows).__dict__,
        "tool_calls": summarize(row.tool_calls for row in rows).__dict__,
    }
