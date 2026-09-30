"""Pilot A invocation budgeting and source-backed Codex observations."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

PILOT_A_ARMS = ("baseline", "candidate")
PILOT_A_CASE_COUNT = 12
PILOT_A_MAX_INVOCATIONS = PILOT_A_CASE_COUNT * len(PILOT_A_ARMS)
_ALLOWED_ENFORCEMENT_DIMENSIONS = frozenset(
    {"harness_invocations", "provider_model_calls"}
)


@dataclass(frozen=True)
class PilotABudget:
    """Declared Pilot A enforcement requirements and a local invocation cap."""

    max_harness_invocations: int = PILOT_A_MAX_INVOCATIONS
    required_enforcement: tuple[str, ...] = ("harness_invocations",)
    provider_model_calls: str = "unknown"
    retries_per_pair: int = 0
    stop_on_first_failure: bool = True

    def __post_init__(self) -> None:
        if (
            type(self.max_harness_invocations) is not int
            or not 0 <= self.max_harness_invocations <= PILOT_A_MAX_INVOCATIONS
        ):
            raise ValueError(
                f"max_harness_invocations must be between 0 and {PILOT_A_MAX_INVOCATIONS}"
            )
        if isinstance(self.required_enforcement, str):
            raise TypeError("required_enforcement must be a sequence of dimensions")
        dimensions = tuple(self.required_enforcement)
        if (
            not dimensions
            or len(dimensions) != len(set(dimensions))
            or set(dimensions) - _ALLOWED_ENFORCEMENT_DIMENSIONS
            or "harness_invocations" not in dimensions
        ):
            raise ValueError(
                "Pilot A must require unique supported dimensions including harness_invocations"
            )
        if "provider_model_calls" in dimensions:
            raise ValueError(
                "provider_model_calls cannot be declared enforced by the Pilot A runner"
            )
        if self.provider_model_calls != "unknown":
            raise ValueError(
                "provider_model_calls is telemetry and must remain unknown"
            )
        if type(self.retries_per_pair) is not int or self.retries_per_pair != 0:
            raise ValueError("Pilot A schedule does not permit retries")
        if (
            type(self.stop_on_first_failure) is not bool
            or not self.stop_on_first_failure
        ):
            raise ValueError("Pilot A must stop on the first invocation/result failure")
        object.__setattr__(self, "required_enforcement", dimensions)

    def as_dict(self) -> dict[str, Any]:
        return {
            "max_harness_invocations": self.max_harness_invocations,
            "required_enforcement": list(self.required_enforcement),
            "provider_model_calls": self.provider_model_calls,
            "retries_per_pair": self.retries_per_pair,
            "stop_on_first_failure": self.stop_on_first_failure,
        }


@dataclass(frozen=True)
class CaseArm:
    case_id: str
    arm: str


@dataclass(frozen=True)
class ScheduledInvocation:
    invocation_number: int
    case_id: str
    arm: str
    status: str
    provider_model_calls: int | None = None
    model_turns: int | None = None
    error: str | None = None
    retry_count: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "invocation_number": self.invocation_number,
            "case_id": self.case_id,
            "arm": self.arm,
            "status": self.status,
            "provider_model_calls": (
                self.provider_model_calls
                if self.provider_model_calls is not None
                else "unknown"
            ),
            "model_turns": self.model_turns
            if self.model_turns is not None
            else "unknown",
            "error": self.error or "unknown",
            "retry_count": self.retry_count,
        }


@dataclass(frozen=True)
class PilotAScheduleResult:
    status: str
    invocations: tuple[ScheduledInvocation, ...]
    stop_reason: str | None = None

    @property
    def harness_invocations(self) -> int:
        return len(self.invocations)

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "harness_invocations": self.harness_invocations,
            "provider_model_calls": self.provider_model_calls,
            "model_turns": self.model_turns,
            "stop_reason": self.stop_reason or "unknown",
            "invocations": [item.as_dict() for item in self.invocations],
        }

    @property
    def provider_model_calls(self) -> int | str:
        if not self.invocations:
            return 0
        counts = [item.provider_model_calls for item in self.invocations]
        if any(count is None for count in counts):
            return "unknown"
        return sum(count for count in counts if count is not None)

    @property
    def model_turns(self) -> int | str:
        if not self.invocations:
            return "unknown"
        counts = [item.model_turns for item in self.invocations]
        if any(count is None for count in counts):
            return "unknown"
        return sum(count for count in counts if count is not None)


def make_pilot_a_schedule(
    case_ids: Sequence[str], *, arms: Sequence[str] = PILOT_A_ARMS
) -> tuple[CaseArm, ...]:
    """Create the frozen case-major baseline/candidate schedule."""

    cases = tuple(case_ids)
    selected_arms = tuple(arms)
    if (
        len(cases) != PILOT_A_CASE_COUNT
        or any(not isinstance(case, str) or not case.strip() for case in cases)
        or len(cases) != len(set(cases))
    ):
        raise ValueError(
            f"Pilot A requires {PILOT_A_CASE_COUNT} unique non-empty cases"
        )
    if selected_arms != PILOT_A_ARMS:
        raise ValueError(f"Pilot A arms are fixed: {', '.join(PILOT_A_ARMS)}")
    return tuple(
        CaseArm(case_id=case_id, arm=arm) for case_id in cases for arm in selected_arms
    )


def execute_pilot_a_schedule(
    schedule: Sequence[CaseArm],
    *,
    budget: PilotABudget,
    invoke: Callable[[CaseArm], Mapping[str, Any]],
) -> PilotAScheduleResult:
    """Execute sequentially, enforcing the local cap and stopping on first failure."""

    if not isinstance(budget, PilotABudget):
        raise TypeError("Pilot A requires a validated PilotABudget")
    selected = tuple(schedule)
    if any(
        not isinstance(pair, CaseArm) or pair.arm not in PILOT_A_ARMS
        for pair in selected
    ):
        raise ValueError("Pilot A schedule contains an invalid case/arm pair")
    if (
        len(selected) != PILOT_A_MAX_INVOCATIONS
        or len({(pair.case_id, pair.arm) for pair in selected})
        != PILOT_A_MAX_INVOCATIONS
    ):
        raise ValueError("Pilot A schedule must contain 24 unique case/arm pairs")
    if len(selected) > budget.max_harness_invocations:
        return PilotAScheduleResult(
            status="blocked",
            invocations=(),
            stop_reason="local harness invocation budget is below the frozen schedule",
        )
    if not callable(invoke):
        raise TypeError("invoke must be callable")

    outcomes: list[ScheduledInvocation] = []
    for invocation_number, pair in enumerate(selected, start=1):
        try:
            result = invoke(pair)
            if not isinstance(result, Mapping):
                raise TypeError("invocation result must be an object")
            status = result.get("status")
            if status not in {"passed", "failed", "blocked"}:
                raise ValueError(
                    "invocation result status must be passed, failed, or blocked"
                )
            calls = _optional_nonnegative_integer(
                result.get("provider_model_calls"), "provider_model_calls"
            )
            turns = _optional_nonnegative_integer(
                result.get("model_turns"), "model_turns"
            )
            error = result.get("error")
            if error is not None and not isinstance(error, str):
                raise ValueError("invocation result error must be a string or null")
            outcomes.append(
                ScheduledInvocation(
                    invocation_number=invocation_number,
                    case_id=pair.case_id,
                    arm=pair.arm,
                    status=status,
                    provider_model_calls=calls,
                    model_turns=turns,
                    error=error,
                    retry_count=0,
                )
            )
            if status != "passed":
                return PilotAScheduleResult(
                    status="blocked" if status == "blocked" else "failed",
                    invocations=tuple(outcomes),
                    stop_reason=error or f"invocation returned {status}",
                )
        except Exception as exc:  # noqa: BLE001 - first invocation failure is durable
            outcomes.append(
                ScheduledInvocation(
                    invocation_number=invocation_number,
                    case_id=pair.case_id,
                    arm=pair.arm,
                    status="failed",
                    error=f"{type(exc).__name__}: {exc}",
                )
            )
            return PilotAScheduleResult(
                status="failed",
                invocations=tuple(outcomes),
                stop_reason=f"{type(exc).__name__}: {exc}",
            )
    return PilotAScheduleResult(status="completed", invocations=tuple(outcomes))


@dataclass(frozen=True)
class DelegationObservation:
    confirmed: bool = False
    sender_thread_id: str | None = None
    receiver_thread_id: str | None = None
    state: str | None = None
    requested_role: str | None = None
    observed_role: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "confirmed": self.confirmed,
            "sender_thread_id": self.sender_thread_id or "unknown",
            "receiver_thread_id": self.receiver_thread_id or "unknown",
            "state": self.state or "unknown",
            "requested_role": self.requested_role or "unknown",
            "observed_role": self.observed_role or "unknown",
        }


@dataclass(frozen=True)
class CodexRouteObservation:
    requested_route: str | None
    actual_trigger: bool | None
    actual_route: str | None
    invoke_types: tuple[str, ...]
    delegation: DelegationObservation

    def as_dict(self) -> dict[str, Any]:
        return {
            "requested_route": self.requested_route or "unknown",
            "actual_trigger": (
                self.actual_trigger if self.actual_trigger is not None else "unknown"
            ),
            "actual_route": self.actual_route or "unknown",
            "invoke_types": list(self.invoke_types),
            "delegation": self.delegation.as_dict(),
        }


def observe_codex_events(
    events: Iterable[Mapping[str, Any]],
    *,
    requested_route: str | None = None,
    requested_role: str | None = None,
) -> CodexRouteObservation:
    """Read only known Codex JSONL collaboration items and documented OTLP metrics."""

    if isinstance(events, (str, bytes, Mapping)):
        raise TypeError("events must be an iterable of decoded event objects")
    skill_names: set[str] = set()
    invoke_types: set[str] = set()
    delegation = DelegationObservation(requested_role=requested_role)
    for event in events:
        if not isinstance(event, Mapping):
            continue
        for skill, invoke_type in _documented_skill_injections(event):
            skill_names.add(skill)
            if invoke_type:
                invoke_types.add(invoke_type)
        item = event.get("item")
        if not isinstance(item, Mapping):
            continue
        if item.get("type") != "collab_tool_call" or item.get("tool") != "spawn_agent":
            continue
        sender = _nonempty_text(item.get("sender_thread_id"))
        receiver = _nonempty_text(item.get("receiver_thread_id"))
        if sender is None or receiver is None:
            continue
        state = _nonempty_text(item.get("state"))
        observed_role = _nonempty_text(item.get("role"))
        delegation = DelegationObservation(
            confirmed=True,
            sender_thread_id=sender,
            receiver_thread_id=receiver,
            state=state,
            requested_role=requested_role,
            observed_role=observed_role,
        )
        break
    ordered_skills = tuple(sorted(skill_names))
    return CodexRouteObservation(
        requested_route=requested_route,
        actual_trigger=True if ordered_skills else None,
        actual_route=ordered_skills[0] if len(ordered_skills) == 1 else None,
        invoke_types=tuple(sorted(invoke_types)),
        delegation=delegation,
    )


def _documented_skill_injections(
    event: Mapping[str, Any],
) -> tuple[tuple[str, str | None], ...]:
    """Parse only the Codex skill metric in the documented OTLP JSON hierarchy."""

    found: list[tuple[str, str | None]] = []
    resource_metrics = event.get("resourceMetrics")
    if not isinstance(resource_metrics, list):
        return ()
    for resource_metric in resource_metrics:
        if not isinstance(resource_metric, Mapping):
            continue
        scope_metrics = resource_metric.get("scopeMetrics")
        if not isinstance(scope_metrics, list):
            continue
        for scope_metric in scope_metrics:
            if not isinstance(scope_metric, Mapping):
                continue
            metrics = scope_metric.get("metrics")
            if not isinstance(metrics, list):
                continue
            for metric in metrics:
                if (
                    not isinstance(metric, Mapping)
                    or metric.get("name") != "codex.skill.injected"
                ):
                    continue
                measurement = metric.get("sum")
                if not isinstance(measurement, Mapping):
                    continue
                data_points = measurement.get("dataPoints")
                if not isinstance(data_points, list):
                    continue
                for data_point in data_points:
                    if not isinstance(data_point, Mapping):
                        continue
                    attributes = data_point.get("attributes")
                    if not isinstance(attributes, list):
                        continue
                    values: dict[str, str] = {}
                    for attribute in attributes:
                        if not isinstance(attribute, Mapping):
                            continue
                        key = attribute.get("key")
                        value = attribute.get("value")
                        if not isinstance(key, str) or not isinstance(value, Mapping):
                            continue
                        text = value.get("stringValue")
                        if isinstance(text, str) and text.strip():
                            values[key] = text.strip()
                    skill = values.get("skill")
                    if skill:
                        found.append((skill, values.get("invoke_type")))
    return tuple(found)


@dataclass(frozen=True)
class PilotACaseObservation:
    run_id: str
    case_id: str
    arm: str
    expected_trigger: bool
    actual_trigger: bool | None
    expected_route: str | None
    actual_route: str | None
    completion: str
    invocation_count: int
    provider_model_calls: int | None = None
    model_turns: int | None = None
    tokens: Mapping[str, int] | None = None
    latency_ms: int | None = None
    delegation: DelegationObservation = DelegationObservation()
    validation_failures: tuple[str, ...] = ()
    package_digest: str = "unknown"
    canonical_revision: str = "unknown"
    raw_reference: str = "unknown"

    def __post_init__(self) -> None:
        for name in ("run_id", "case_id", "arm", "completion"):
            if (
                not isinstance(getattr(self, name), str)
                or not getattr(self, name).strip()
            ):
                raise ValueError(f"{name} must be non-empty text")
        if self.arm not in PILOT_A_ARMS:
            raise ValueError("arm must be baseline or candidate")
        if type(self.expected_trigger) is not bool or (
            self.actual_trigger is not None and type(self.actual_trigger) is not bool
        ):
            raise ValueError("trigger observations must be booleans or unknown")
        if type(self.invocation_count) is not int or self.invocation_count < 0:
            raise ValueError("invocation_count must be a non-negative integer")
        _optional_nonnegative_integer(self.provider_model_calls, "provider_model_calls")
        _optional_nonnegative_integer(self.model_turns, "model_turns")
        _optional_nonnegative_integer(self.latency_ms, "latency_ms")
        if self.tokens is not None and any(
            not isinstance(name, str) or type(count) is not int or count < 0
            for name, count in self.tokens.items()
        ):
            raise ValueError("tokens must contain non-negative integer values")
        if any(
            not isinstance(item, str) or not item for item in self.validation_failures
        ):
            raise ValueError("validation_failures must contain non-empty text")

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "case_id": self.case_id,
            "arm": self.arm,
            "expected_trigger": self.expected_trigger,
            "actual_trigger": (
                self.actual_trigger if self.actual_trigger is not None else "unknown"
            ),
            "expected_route": self.expected_route or "unknown",
            "actual_route": self.actual_route or "unknown",
            "completion": self.completion,
            "invocation_count": self.invocation_count,
            "provider_model_calls": (
                self.provider_model_calls
                if self.provider_model_calls is not None
                else "unknown"
            ),
            "model_turns": self.model_turns
            if self.model_turns is not None
            else "unknown",
            "tokens": dict(self.tokens) if self.tokens is not None else "unknown",
            "latency_ms": self.latency_ms if self.latency_ms is not None else "unknown",
            "delegation": self.delegation.as_dict(),
            "validation_failures": list(self.validation_failures),
            "package_digest": self.package_digest,
            "canonical_revision": self.canonical_revision,
            "raw_reference": self.raw_reference,
        }


def pilot_a_metrics(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Return standard binary FP rate and the historical all-row discovery rate."""

    values = list(rows)
    known = [
        (row.get("expected_trigger"), row.get("actual_trigger"))
        for row in values
        if type(row.get("expected_trigger")) is bool
        and type(row.get("actual_trigger")) is bool
    ]
    false_positives = sum(
        expected is False and actual is True for expected, actual in known
    )
    true_negatives = sum(
        expected is False and actual is False for expected, actual in known
    )
    denominator = false_positives + true_negatives
    legacy_false_positives = sum(
        row.get("expected_trigger") is False and row.get("actual_trigger") is True
        for row in values
    )
    return {
        "trial_count": len(values),
        "known_trigger_observations": len(known),
        "trigger_false_positive_rate": (
            false_positives / denominator if denominator else "unknown"
        ),
        "legacy_discovery_false_positive_rate": (
            legacy_false_positives / len(values) if values else "unknown"
        ),
        "false_positives": false_positives,
        "true_negatives": true_negatives,
    }


def _optional_nonnegative_integer(value: Any, label: str) -> int | None:
    if value is None:
        return None
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} must be a non-negative integer or null")
    return value


def _nonempty_text(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None
