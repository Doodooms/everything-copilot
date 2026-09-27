from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any

HARNESS_NAMES = ("copilot", "codex")
COPILOT_MIN_AI_CREDITS = 30
CAPABILITY_NAMES = (
    "plugin_installation",
    "skills",
    "custom_agents",
    "mcp",
    "non_interactive_execution",
    "structured_output",
    "model_selection",
    "sandboxing",
    "token_usage_reporting",
)
_REVISION_PATTERN = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


class CapabilityState(str, Enum):
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"
    HOST_SPECIFIC = "host_specific"


class RunMode(str, Enum):
    DEVELOPMENT = "development"
    VALIDATION = "validation"


class RunStatus(str, Enum):
    PREPARED = "prepared"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CLEANED = "cleaned"


class Purpose(str, Enum):
    VALIDATION = "validation"
    SMOKE_TEST = "smoke-test"
    CONFORMANCE_TEST = "conformance-test"
    BENCHMARK = "benchmark"


class ResultStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class CapabilityObservation:
    state: CapabilityState
    evidence: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {"status": self.state.value, "evidence": list(self.evidence)}


@dataclass(frozen=True)
class HarnessCapabilities:
    harness: str
    cli_installed: bool
    executable: str | None
    version: str | None
    capabilities: Mapping[str, CapabilityObservation]
    diagnostics: tuple[str, ...] = ()
    observed_options: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.harness not in HARNESS_NAMES:
            raise ValueError(f"unsupported harness name: {self.harness!r}")
        if type(self.cli_installed) is not bool:
            raise ValueError("cli_installed must be a boolean")
        if self.cli_installed and not self.executable:
            raise ValueError("an installed CLI requires its resolved executable path")
        if not self.cli_installed and self.executable is not None:
            raise ValueError("an absent CLI must not have an executable path")
        if set(self.capabilities) != set(CAPABILITY_NAMES):
            raise ValueError(
                "capability report must include the complete capability set"
            )
        if any(
            not isinstance(value, CapabilityObservation)
            for value in self.capabilities.values()
        ):
            raise ValueError("capabilities must contain CapabilityObservation values")
        object.__setattr__(
            self,
            "capabilities",
            MappingProxyType(
                {name: self.capabilities[name] for name in CAPABILITY_NAMES}
            ),
        )
        object.__setattr__(
            self,
            "observed_options",
            tuple(sorted(set(self.observed_options))),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "harness": self.harness,
            "cli_installed": self.cli_installed,
            "executable": self.executable,
            "version": self.version,
            "capabilities": {
                name: self.capabilities[name].as_dict() for name in CAPABILITY_NAMES
            },
            "diagnostics": list(self.diagnostics),
            "observed_options": list(self.observed_options),
        }


@dataclass(frozen=True)
class CrossHarnessRequest:
    run_id: str
    requested_by: str
    target_harness: str
    purpose: Purpose
    artifact_under_test: str
    base_revision: str
    allowed_mutations: bool = False
    timeout_or_budget: str | int | Mapping[str, int] | None = None
    expected_output: str | None = None
    origin_harness: str = ""
    call_depth: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.run_id, str) or not self.run_id.strip():
            raise ValueError("cross-harness request requires run_id")
        if not isinstance(self.requested_by, str) or not self.requested_by.strip():
            raise ValueError("cross-harness request requires requested_by")
        if self.target_harness not in HARNESS_NAMES:
            raise ValueError("cross-harness request has an unknown target_harness")
        if self.origin_harness not in HARNESS_NAMES:
            raise ValueError("cross-harness request requires a known origin_harness")
        if self.origin_harness == self.target_harness:
            raise ValueError("cross-harness request must target a different harness")
        if not isinstance(self.purpose, Purpose):
            raise TypeError("cross-harness request has an unsupported purpose")
        if (
            not isinstance(self.artifact_under_test, str)
            or not self.artifact_under_test.strip()
        ):
            raise ValueError("cross-harness request requires artifact_under_test")
        if not isinstance(self.base_revision, str):
            raise TypeError("base_revision must be a resolved commit SHA")
        if _REVISION_PATTERN.fullmatch(self.base_revision) is None:
            raise ValueError("base_revision must be a resolved commit SHA")
        if type(self.allowed_mutations) is not bool or self.allowed_mutations:
            raise ValueError("cross-harness validation requests must be read-only")
        if type(self.call_depth) is not int or self.call_depth != 1:
            raise ValueError("cross-harness call depth must be exactly one")
        if isinstance(self.timeout_or_budget, str):
            if not self.timeout_or_budget.strip():
                raise ValueError("timeout_or_budget must be non-empty")
        elif type(self.timeout_or_budget) is int:
            if self.timeout_or_budget <= 0:
                raise ValueError("timeout_or_budget must be positive")
        elif isinstance(self.timeout_or_budget, Mapping):
            if any(
                not isinstance(key, str) or type(value) is not int or value <= 0
                for key, value in self.timeout_or_budget.items()
            ):
                raise ValueError("timeout_or_budget entries must be positive integers")
            object.__setattr__(
                self,
                "timeout_or_budget",
                MappingProxyType(dict(self.timeout_or_budget)),
            )
        elif self.timeout_or_budget is not None:
            raise ValueError(
                "timeout_or_budget must be a string, integer, mapping, or null"
            )
        if self.expected_output is not None and not isinstance(
            self.expected_output, str
        ):
            raise ValueError("expected_output must be a string or null")

    def as_dict(self) -> dict[str, Any]:
        budget = self.timeout_or_budget
        if isinstance(budget, Mapping):
            budget = dict(budget)
        return {
            "run_id": self.run_id,
            "requested_by": self.requested_by,
            "target_harness": self.target_harness,
            "purpose": self.purpose.value,
            "artifact_under_test": self.artifact_under_test,
            "base_revision": self.base_revision,
            "allowed_mutations": self.allowed_mutations,
            "timeout_or_budget": budget,
            "expected_output": self.expected_output,
            "origin_harness": self.origin_harness,
            "call_depth": self.call_depth,
        }


@dataclass(frozen=True)
class HarnessScenario:
    scenario_id: str
    prompt: str
    expected_output: str
    timeout_seconds: int = 90
    max_ai_credits: int = 30
    required_observations: tuple[str, ...] = ()
    forbidden_observations: tuple[str, ...] = ()
    optional_observations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.scenario_id, str) or not self.scenario_id.strip():
            raise ValueError("scenario_id must be non-empty")
        if not isinstance(self.prompt, str) or not self.prompt.strip():
            raise ValueError("scenario prompt must be non-empty")
        if (
            not isinstance(self.expected_output, str)
            or not self.expected_output.strip()
        ):
            raise ValueError("expected_output must be non-empty")
        if (
            type(self.timeout_seconds) is not int
            or type(self.max_ai_credits) is not int
            or self.timeout_seconds <= 0
            or self.max_ai_credits <= 0
        ):
            raise ValueError("scenario timeout and credit budget must be positive")
        for field_name in (
            "required_observations",
            "forbidden_observations",
            "optional_observations",
        ):
            values = getattr(self, field_name)
            if isinstance(values, str):
                raise TypeError(f"{field_name} must be a sequence of strings")
            try:
                normalized = tuple(values)
            except TypeError as exc:
                raise TypeError(f"{field_name} must be a sequence of strings") from exc
            if any(
                not isinstance(value, str) or not value.strip() for value in normalized
            ):
                raise ValueError(f"{field_name} must contain non-empty strings")
            if len(normalized) != len(set(normalized)):
                raise ValueError(f"{field_name} cannot contain duplicates")
            object.__setattr__(self, field_name, normalized)
        if set(self.required_observations) & set(self.forbidden_observations):
            raise ValueError("an observation cannot be both required and forbidden")


@dataclass(frozen=True)
class HarnessResult:
    run_id: str
    harness: str
    status: ResultStatus
    scenario: str
    base_revision: str
    observations: Mapping[str, Any]
    assertions: tuple[Mapping[str, Any], ...]
    artifacts: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    token_usage: Mapping[str, int] | None = None
    latency_ms: int | None = None
    errors: tuple[str, ...] = ()
    model_turns: int | None = None
    model_calls: int | None = None

    def __post_init__(self) -> None:
        if self.harness not in HARNESS_NAMES:
            raise ValueError(f"unsupported harness name: {self.harness!r}")
        if self.latency_ms is not None and self.latency_ms < 0:
            raise ValueError("latency_ms must be non-negative or unknown")
        if self.model_turns is not None and (
            type(self.model_turns) is not int or self.model_turns < 0
        ):
            raise ValueError("model_turns must be a non-negative integer or unknown")
        if self.model_calls is not None and (
            type(self.model_calls) is not int or self.model_calls < 0
        ):
            raise ValueError("model_calls must be a non-negative integer or unknown")
        if self.token_usage is not None and any(
            not isinstance(key, str) or type(value) is not int or value < 0
            for key, value in self.token_usage.items()
        ):
            raise ValueError("token_usage must contain non-negative integer values")
        object.__setattr__(
            self, "observations", MappingProxyType(dict(self.observations))
        )
        object.__setattr__(
            self,
            "assertions",
            tuple(MappingProxyType(dict(item)) for item in self.assertions),
        )
        if self.token_usage is not None:
            object.__setattr__(
                self, "token_usage", MappingProxyType(dict(self.token_usage))
            )

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "harness": self.harness,
            "status": self.status.value,
            "scenario": self.scenario,
            "base_revision": self.base_revision,
            "observations": dict(self.observations),
            "assertions": [dict(item) for item in self.assertions],
            "artifacts": list(self.artifacts),
            "evidence": list(self.evidence),
            "token_usage": (
                dict(self.token_usage) if self.token_usage is not None else "unknown"
            ),
            "latency_ms": self.latency_ms if self.latency_ms is not None else "unknown",
            "model_turns": (
                self.model_turns if self.model_turns is not None else "unknown"
            ),
            "model_calls": (
                self.model_calls if self.model_calls is not None else "unknown"
            ),
            "errors": list(self.errors),
        }
