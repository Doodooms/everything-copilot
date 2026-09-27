from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Protocol

from .models import CapabilityObservation, CapabilityState

EXECUTION_CAPABILITY_NAMES = (
    "stateless_execution",
    "headless",
    "structured_output",
    "read_only",
    "workspace_write",
    "parallel",
    "process_supervision",
)


@dataclass(frozen=True)
class BackendCapabilities:
    """Observable capabilities belonging to one concrete execution backend."""

    backend_id: str
    capabilities: Mapping[str, CapabilityObservation]

    def __post_init__(self) -> None:
        if not isinstance(self.backend_id, str) or not self.backend_id.strip():
            raise ValueError("backend_id must be non-empty")
        if set(self.capabilities) != set(EXECUTION_CAPABILITY_NAMES):
            raise ValueError("backend capabilities must include the complete set")
        if any(
            not isinstance(value, CapabilityObservation)
            for value in self.capabilities.values()
        ):
            raise ValueError("backend capabilities must use CapabilityObservation")
        object.__setattr__(
            self,
            "capabilities",
            MappingProxyType(
                {name: self.capabilities[name] for name in EXECUTION_CAPABILITY_NAMES}
            ),
        )

    def satisfies(self, required: Sequence[str]) -> bool:
        """Only explicitly supported observations satisfy hard requirements."""
        return all(
            self.capabilities[name].state is CapabilityState.SUPPORTED
            for name in required
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "backend_id": self.backend_id,
            "capabilities": {
                name: self.capabilities[name].as_dict()
                for name in EXECUTION_CAPABILITY_NAMES
            },
        }


@dataclass(frozen=True)
class ExecutionConstraints:
    timeout_seconds: int = 120
    read_only: bool = True

    def __post_init__(self) -> None:
        if type(self.timeout_seconds) is not int or self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive integer")
        if type(self.read_only) is not bool:
            raise TypeError("read_only must be a boolean")


@dataclass(frozen=True)
class ExecutionRequest:
    """One attempt's input and constraints; durable task state lives elsewhere."""

    task_id: str
    attempt_id: str
    input: str
    working_directory: Path
    required_capabilities: tuple[str, ...] = ()
    constraints: ExecutionConstraints = field(default_factory=ExecutionConstraints)

    def __post_init__(self) -> None:
        for name in ("task_id", "attempt_id", "input"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if not isinstance(self.working_directory, Path):
            raise TypeError("working_directory must be a pathlib.Path")
        if not self.working_directory.is_absolute():
            raise ValueError("working_directory must be absolute")
        if not self.working_directory.is_dir():
            raise ValueError("working_directory must be an existing directory")
        if not isinstance(self.constraints, ExecutionConstraints):
            raise TypeError("constraints must be ExecutionConstraints")
        if isinstance(self.required_capabilities, str):
            raise TypeError("required_capabilities must be a sequence of names")
        try:
            required = tuple(self.required_capabilities)
        except TypeError as exc:
            raise TypeError(
                "required_capabilities must be a sequence of names"
            ) from exc
        if any(
            not isinstance(name, str) or name not in EXECUTION_CAPABILITY_NAMES
            for name in required
        ):
            raise ValueError("required_capabilities contains an unknown capability")
        if len(required) != len(set(required)):
            raise ValueError("required_capabilities cannot contain duplicates")
        object.__setattr__(self, "required_capabilities", required)

    @property
    def capability_requirements(self) -> tuple[str, ...]:
        constraint_capability = (
            "read_only" if self.constraints.read_only else "workspace_write"
        )
        return tuple(
            dict.fromkeys((*self.required_capabilities, constraint_capability))
        )


class ExecutionOutcome(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class FailureCause(str, Enum):
    PROCESS_FAILURE = "process_failure"
    PROTOCOL_FAILURE = "protocol_failure"
    SEMANTIC_FAILURE = "semantic_failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    AUTH_UNAVAILABLE = "auth_unavailable"
    HARNESS_UNAVAILABLE = "harness_unavailable"
    UNSUPPORTED_CAPABILITY = "unsupported_capability"
    CAPABILITY_UNVERIFIED = "capability_unverified"
    RESOURCE_LIMIT = "resource_limit"
    STALE_OWNER = "stale_owner"
    LOST_BACKEND = "lost_backend"


class RetryDecision(str, Enum):
    RETRY = "retry"
    DO_NOT_RETRY = "do_not_retry"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ExecutionFailure:
    cause: FailureCause
    retry: RetryDecision
    message: str

    def __post_init__(self) -> None:
        if not isinstance(self.cause, FailureCause):
            raise TypeError("cause must be a FailureCause")
        if not isinstance(self.retry, RetryDecision):
            raise TypeError("retry must be a RetryDecision")
        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("failure message must be non-empty")

    def as_dict(self) -> dict[str, str]:
        return {
            "cause": self.cause.value,
            "retry": self.retry.value,
            "message": self.message,
        }


@dataclass(frozen=True)
class ExecutionResult:
    outcome: ExecutionOutcome
    task_id: str
    attempt_id: str
    harness_id: str
    backend_id: str
    result: Any = None
    artifact_refs: tuple[str, ...] = ()
    external_session_id: str | None = None
    failure: ExecutionFailure | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, ExecutionOutcome):
            raise TypeError("outcome must be an ExecutionOutcome")
        for name in ("task_id", "attempt_id", "harness_id", "backend_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if self.external_session_id is not None and (
            not isinstance(self.external_session_id, str)
            or not self.external_session_id.strip()
        ):
            raise ValueError("external_session_id must be non-empty or null")
        if self.outcome is ExecutionOutcome.SUCCEEDED:
            if self.failure is not None:
                raise ValueError("a successful result cannot contain a failure")
        elif not isinstance(self.failure, ExecutionFailure):
            raise ValueError("a non-successful result requires an ExecutionFailure")
        if isinstance(self.artifact_refs, str):
            raise TypeError("artifact_refs must be a sequence of references")
        try:
            refs = tuple(self.artifact_refs)
        except TypeError as exc:
            raise TypeError("artifact_refs must be a sequence of references") from exc
        if any(not isinstance(ref, str) or not ref.strip() for ref in refs):
            raise ValueError("artifact_refs must contain non-empty strings")
        object.__setattr__(self, "artifact_refs", refs)

    @property
    def status(self) -> str:
        return self.outcome.value

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "task_id": self.task_id,
            "attempt_id": self.attempt_id,
            "harness_id": self.harness_id,
            "backend_id": self.backend_id,
            "result": self.result,
            "artifact_refs": list(self.artifact_refs),
            "external_session_id": self.external_session_id,
            "failure": self.failure.as_dict() if self.failure else None,
        }


class ExecutionBackend(Protocol):
    backend_id: str
    harness_id: str
    capabilities: BackendCapabilities

    def execute(self, request: ExecutionRequest) -> ExecutionResult: ...
