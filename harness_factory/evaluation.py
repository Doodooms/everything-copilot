"""Budgeted suite execution, durable artifacts, and matched comparisons."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .errors import HarnessFactoryError
from .models import CrossHarnessRequest, HarnessResult, ResultStatus
from .suites import Scenario, ScenarioSuite, SuiteValidationError, validate_suite

ALLOWED_COPILOT_REASONS = frozenset(
    {
        "copilot_specific_behavior",
        "portability_sample",
        "regression_confirmation",
        "host_specific_agent_behavior",
    }
)
_ARTIFACT_SCHEMA_VERSION = 2
_BUDGET_ENFORCEMENT_DIMENSIONS = frozenset(
    {"harness_invocations", "provider_model_calls"}
)
_LEGACY_BUDGET_FIELDS = {
    "max_runs",
    "max_model_calls",
    "max_tokens_if_known",
    "max_failures_before_stop",
}
_RUN_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")
_REVISION_PATTERN = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_PROFILE_FIELDS = {
    "schema_version",
    "profile_id",
    "source_path",
    "source_mode",
    "metadata",
}
_LEGACY_PROFILE_FIELDS = _PROFILE_FIELDS - {"source_mode"}
_ARTIFACT_FIELDS = {
    "schema_version",
    "run_id",
    "suite_id",
    "harness",
    "copilot_reason",
    "model",
    "base_revision",
    "suite",
    "plugin_profile",
    "model_call_limit_enforced",
    "started_at",
    "finished_at",
    "status",
    "budget",
    "scenario_contracts",
    "results",
    "metrics",
    "failures",
    "usage",
    "token_usage",
    "latency_ms",
    "raw_artifact_references",
    "stop_reason",
}


class SystemicEvaluationError(HarnessFactoryError):
    """A materialization, schema, plugin, or routing failure that stops a run."""


@dataclass(frozen=True)
class RunBudget:
    max_runs: int
    max_model_calls: int | None
    max_tokens_if_known: int | None
    max_failures_before_stop: int
    required_enforcement: tuple[str, ...] = ("provider_model_calls",)

    def __post_init__(self) -> None:
        for name in ("max_runs", "max_failures_before_stop"):
            value = getattr(self, name)
            if type(value) is not int or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if self.max_model_calls is not None and (
            type(self.max_model_calls) is not int or self.max_model_calls <= 0
        ):
            raise ValueError("max_model_calls must be a positive integer or null")
        if self.max_tokens_if_known is not None and (
            type(self.max_tokens_if_known) is not int or self.max_tokens_if_known <= 0
        ):
            raise ValueError("max_tokens_if_known must be a positive integer or null")
        if not isinstance(self.required_enforcement, (tuple, list)):
            raise TypeError("required_enforcement must be a sequence of dimensions")
        required = tuple(self.required_enforcement)
        if (
            not required
            or any(
                not isinstance(name, str) or name not in _BUDGET_ENFORCEMENT_DIMENSIONS
                for name in required
            )
            or len(set(required)) != len(required)
        ):
            raise ValueError("required_enforcement contains invalid dimensions")
        if "provider_model_calls" in required and self.max_model_calls is None:
            raise ValueError(
                "max_model_calls is required when provider_model_calls enforcement is required"
            )
        object.__setattr__(self, "required_enforcement", required)

    def as_dict(self) -> dict[str, Any]:
        return {
            "max_runs": self.max_runs,
            "max_model_calls": self.max_model_calls,
            "max_tokens_if_known": self.max_tokens_if_known,
            "max_failures_before_stop": self.max_failures_before_stop,
            "required_enforcement": list(self.required_enforcement),
        }


def _validated_run_budget(value: Mapping[str, Any]) -> RunBudget:
    if not isinstance(value, Mapping) or frozenset(value) not in {
        frozenset(_LEGACY_BUDGET_FIELDS),
        frozenset(_LEGACY_BUDGET_FIELDS | {"required_enforcement"}),
    }:
        raise ValueError("budget fields are invalid")
    return RunBudget(**value)


@dataclass(frozen=True)
class EvaluationProfile:
    """A supplied plugin/profile input, independent of how it was generated."""

    profile_id: str
    source_path: Path
    metadata: Mapping[str, Any] | None = None
    source_mode: str = "external"

    def __post_init__(self) -> None:
        if not isinstance(self.profile_id, str) or not self.profile_id.strip():
            raise ValueError("profile_id must be a non-empty string")
        if not isinstance(self.source_path, Path):
            raise TypeError("source_path must be a Path")
        if not isinstance(self.source_mode, str):
            raise TypeError("source_mode must be a string")
        if self.source_mode not in {"external", "base_revision"}:
            raise ValueError("source_mode must be external or base_revision")
        if self.source_mode == "base_revision" and (
            self.source_path.is_absolute() or ".." in self.source_path.parts
        ):
            raise ValueError(
                "base_revision profile source_path must be workspace-relative"
            )
        values = self.metadata or {}
        if not isinstance(values, Mapping):
            raise TypeError("profile metadata must be an object")
        try:
            json.dumps(values, ensure_ascii=False, sort_keys=True, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError("profile metadata must contain JSON values") from exc
        object.__setattr__(self, "profile_id", self.profile_id.strip())
        object.__setattr__(self, "metadata", MappingProxyType(dict(values)))

    def as_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "source_path": str(self.source_path),
            "source_mode": self.source_mode,
            "metadata": dict(self.metadata or {}),
        }


def load_profile(path: Path) -> EvaluationProfile:
    """Load a profile input without recording or depending on its generator."""

    descriptor = Path(path)
    try:
        raw = json.loads(
            descriptor.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_json_object,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise HarnessFactoryError(f"plugin profile could not be loaded: {exc}") from exc
    if not isinstance(raw, Mapping) or frozenset(raw) not in {
        frozenset(_PROFILE_FIELDS),
        frozenset(_LEGACY_PROFILE_FIELDS),
    }:
        raise HarnessFactoryError("plugin profile has missing or unknown fields")
    if type(raw["schema_version"]) is not int or raw["schema_version"] != 1:
        raise HarnessFactoryError("plugin profile schema_version must be 1")
    if not isinstance(raw["source_path"], str) or not raw["source_path"].strip():
        raise HarnessFactoryError("plugin profile source_path must be non-empty")
    source_mode = raw.get("source_mode", "external")
    if not isinstance(source_mode, str) or source_mode not in {
        "external",
        "base_revision",
    }:
        raise HarnessFactoryError("plugin profile source_mode is unsupported")
    if not isinstance(raw["metadata"], Mapping):
        raise HarnessFactoryError("plugin profile metadata must be an object")
    raw_source = Path(raw["source_path"])
    if source_mode == "base_revision":
        if raw_source.is_absolute() or ".." in raw_source.parts:
            raise HarnessFactoryError(
                "base_revision profile source_path must be workspace-relative"
            )
        if not raw_source.parts:
            raise HarnessFactoryError("base_revision profile source_path is empty")
        source = raw_source
        return EvaluationProfile(
            profile_id=raw["profile_id"],
            source_path=source,
            metadata=raw["metadata"],
            source_mode=source_mode,
        )
    if raw_source.is_absolute():
        source = raw_source
    else:
        source = descriptor.parent / raw_source
    if source.is_symlink():
        raise HarnessFactoryError("plugin profile source must not be a symlink")
    try:
        source = source.resolve(strict=True)
    except OSError as exc:
        raise HarnessFactoryError("plugin profile source is unavailable") from exc
    if not source.is_dir():
        raise HarnessFactoryError("plugin profile source must be a directory")
    return EvaluationProfile(
        profile_id=raw["profile_id"],
        source_path=source,
        metadata=raw["metadata"],
        source_mode=source_mode,
    )


@dataclass(frozen=True)
class CrossHarnessValidationContext:
    """Static policy binding an independent validator to a read-only request."""

    request: CrossHarnessRequest
    validator_id: str
    development_owner_id: str
    recursive_delegation: bool = False
    allowed_mutations: bool = False
    claims_development_ownership: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.request, CrossHarnessRequest):
            raise TypeError("cross-harness context requires a validated request")
        for name in ("validator_id", "development_owner_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        validator_id = self.validator_id.strip()
        development_owner_id = self.development_owner_id.strip()
        object.__setattr__(self, "validator_id", validator_id)
        object.__setattr__(self, "development_owner_id", development_owner_id)
        if validator_id == development_owner_id:
            raise ValueError("cross-harness validator cannot own the development task")
        if any(
            type(value) is not bool
            for value in (
                self.recursive_delegation,
                self.allowed_mutations,
                self.claims_development_ownership,
            )
        ):
            raise TypeError("cross-harness policy flags must be booleans")
        if self.recursive_delegation:
            raise ValueError("cross-harness validator cannot delegate recursively")
        if self.allowed_mutations or self.claims_development_ownership:
            raise ValueError("cross-harness validation is read-only and non-owning")
        if (
            self.request.origin_harness == self.request.target_harness
            or self.request.call_depth != 1
            or self.request.allowed_mutations
            or self.request.requested_by != validator_id
        ):
            raise ValueError(
                "cross-harness request violates isolated validation policy"
            )


def validate_run_target(harness: str, copilot_reason: str | None = None) -> None:
    if not isinstance(harness, str) or harness not in {"codex", "copilot"}:
        raise ValueError("harness must be codex or copilot")
    if harness == "codex" and copilot_reason is not None:
        raise ValueError("Copilot reason is only valid for a Copilot run")
    if harness == "copilot" and (
        not isinstance(copilot_reason, str)
        or copilot_reason not in ALLOWED_COPILOT_REASONS
    ):
        raise ValueError(
            "Copilot run requires one allowed reason: "
            + ", ".join(sorted(ALLOWED_COPILOT_REASONS))
        )


def make_preflight_record(
    suite: ScenarioSuite,
    profile: EvaluationProfile,
    *,
    profile_descriptor: Path,
    run_id: str,
    harness: str,
    copilot_reason: str | None,
    budget: RunBudget,
) -> dict[str, Any]:
    if not isinstance(suite, ScenarioSuite) or not isinstance(
        profile, EvaluationProfile
    ):
        raise TypeError("preflight requires a validated suite and supplied profile")
    if _RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise ValueError("run_id must be a lowercase 32-character UUID")
    if not isinstance(budget, RunBudget):
        raise TypeError("preflight requires an explicit run budget")
    validate_run_target(harness, copilot_reason)
    return {
        "schema_version": 1,
        "run_id": run_id,
        "suite_id": suite.suite_id,
        "harness": harness,
        "copilot_reason": copilot_reason,
        "base_revision": suite.base_revision,
        "profile_id": profile.profile_id,
        "scenario_ids": [scenario.scenario_id for scenario in suite.scenarios],
        "scenario_contracts": {
            scenario.scenario_id: _contract_hash(scenario)
            for scenario in suite.scenarios
        },
        "profile_descriptor": str(profile_descriptor),
        "plugin_profile": profile.as_dict(),
        "budget": budget.as_dict(),
        "model_call_limit_enforced": False,
        "created_at": _utc_now(),
    }


def save_preflight_record(path: Path, record: Mapping[str, Any]) -> None:
    required = {
        "schema_version",
        "run_id",
        "suite_id",
        "harness",
        "copilot_reason",
        "base_revision",
        "profile_id",
        "scenario_ids",
        "scenario_contracts",
        "profile_descriptor",
        "plugin_profile",
        "budget",
        "model_call_limit_enforced",
        "created_at",
    }
    if not isinstance(record, Mapping) or set(record) != required:
        raise HarnessFactoryError("preflight record has missing or unknown fields")
    if type(record["schema_version"]) is not int or record["schema_version"] != 1:
        raise HarnessFactoryError("preflight record schema_version must be 1")
    if record["model_call_limit_enforced"] is not False:
        raise HarnessFactoryError(
            "preflight cannot claim an unproven provider model-call limit"
        )
    if (
        not isinstance(record["scenario_ids"], list)
        or not isinstance(record["scenario_contracts"], Mapping)
        or not isinstance(record["profile_descriptor"], str)
        or not isinstance(record["plugin_profile"], Mapping)
    ):
        raise HarnessFactoryError("preflight record input identities are invalid")
    if (
        not record["profile_descriptor"].strip()
        or any(
            not isinstance(scenario_id, str) or not scenario_id
            for scenario_id in record["scenario_ids"]
        )
        or record["profile_id"] != record["plugin_profile"].get("profile_id")
        or set(record["scenario_ids"]) != set(record["scenario_contracts"])
        or len(record["scenario_ids"]) != len(set(record["scenario_ids"]))
        or any(
            not isinstance(scenario_id, str)
            or not scenario_id
            or not isinstance(digest, str)
            or re.fullmatch(r"[0-9a-f]{64}", digest) is None
            for scenario_id, digest in record["scenario_contracts"].items()
        )
    ):
        raise HarnessFactoryError("preflight record contract identities are invalid")
    validate_run_target(record["harness"], record["copilot_reason"])
    try:
        _validated_run_budget(record["budget"])
    except (TypeError, ValueError) as exc:
        raise HarnessFactoryError("preflight record budget values are invalid") from exc
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        raise HarnessFactoryError(f"preflight record already exists: {destination}")
    _write_json_atomic(destination, record, prefix=".preflight-")


def run_suite(
    suite: ScenarioSuite,
    profile: EvaluationProfile,
    *,
    harness: str,
    copilot_reason: str | None = None,
    model: str = "unknown",
    budget: RunBudget,
    invoke: Callable[[Scenario, EvaluationProfile], HarnessResult],
    artifact_path: Path,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Execute only with every declared required budget dimension enforceable."""

    if not isinstance(suite, ScenarioSuite):
        raise TypeError("suite must be loaded and validated before execution")
    suite = validate_suite(suite.as_dict())
    if not isinstance(profile, EvaluationProfile):
        raise TypeError("evaluation requires a supplied profile")
    if not isinstance(budget, RunBudget):
        raise TypeError("evaluation requires an explicit run budget")
    if not callable(invoke):
        raise TypeError("evaluation requires an invocation boundary")
    validate_run_target(harness, copilot_reason)
    if not isinstance(model, str) or not model.strip():
        raise ValueError("model must be a non-empty identity or 'unknown'")

    selected_run_id = run_id or uuid.uuid4().hex
    if _RUN_ID_PATTERN.fullmatch(selected_run_id) is None:
        raise ValueError("run_id must be a lowercase 32-character UUID")
    started_at = _utc_now()
    model_call_limit_enforced = False
    provider_calls_required = "provider_model_calls" in budget.required_enforcement
    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    raw_artifact_references: list[str] = []
    metric_results: dict[str, dict[str, Any]] = {}
    contract_hashes = {
        scenario.scenario_id: _contract_hash(scenario) for scenario in suite.scenarios
    }
    for scenario in suite.scenarios:
        metric_results[scenario.scenario_id] = {
            name: "unknown" for name in scenario.metrics
        }
    runs = 0
    harness_invocations = 0
    model_calls_total = 0
    model_calls_complete = True
    saw_model_calls = False
    failure_count = 0
    known_tokens = 0
    saw_known_tokens = False
    known_token_total_complete = True
    model_turns_total = 0
    saw_model_turns = False
    model_turns_complete = True
    total_latency = 0
    latency_known = True
    token_totals: dict[str, int] = {}
    token_usage_complete = True
    stop_reason: str | None = None
    status = "completed"

    for scenario_index, scenario in enumerate(suite.scenarios):
        if provider_calls_required and not model_call_limit_enforced:
            stop_reason = (
                "provider model-call limit cannot be enforced by the selected harness"
            )
            status = "blocked"
            break
        if runs >= budget.max_runs:
            stop_reason = "max_runs reached"
            status = "stopped"
            break
        if (
            model_calls_complete
            and saw_model_calls
            and budget.max_model_calls is not None
            and model_calls_total >= budget.max_model_calls
        ):
            stop_reason = "max_model_calls reached"
            status = "stopped"
            break
        if (
            budget.max_tokens_if_known is not None
            and saw_known_tokens
            and known_tokens >= budget.max_tokens_if_known
        ):
            stop_reason = "max_tokens_if_known reached"
            status = "stopped"
            break
        if failure_count >= budget.max_failures_before_stop:
            stop_reason = "max_failures_before_stop reached"
            status = "stopped"
            break

        runs += 1
        harness_invocations += 1
        try:
            result = invoke(scenario, profile)
            if not isinstance(result, HarnessResult):
                raise SystemicEvaluationError(
                    "harness returned an invalid result object"
                )
            if (
                result.harness != harness
                or result.scenario != scenario.scenario_id
                or result.base_revision != scenario.base_revision
            ):
                raise SystemicEvaluationError(
                    "harness result identity does not match the requested scenario"
                )
        except Exception as exc:  # noqa: BLE001 - persist any invocation failure
            failure_count += 1
            token_usage_complete = False
            known_token_total_complete = False
            model_turns_complete = False
            model_calls_complete = False
            latency_known = False
            systemic = isinstance(exc, SystemicEvaluationError)
            failures.append(
                {
                    "scenario_id": scenario.scenario_id,
                    "kind": type(exc).__name__,
                    "message": str(exc),
                    "systemic": systemic,
                }
            )
            results.append(
                {
                    "scenario_id": scenario.scenario_id,
                    "category": scenario.category,
                    "fixture": scenario.fixture,
                    "base_revision": scenario.base_revision,
                    "contract_sha256": contract_hashes[scenario.scenario_id],
                    "harness_run_id": "unknown",
                    "status": "failed",
                    "observations": {},
                    "failures": [str(exc)],
                    "token_usage": "unknown",
                    "latency_ms": "unknown",
                    "model_turns": "unknown",
                    "model_calls": "unknown",
                    "raw_artifact_references": [],
                }
            )
            metric_results[scenario.scenario_id] = {
                name: "unknown" for name in scenario.metrics
            }
            if systemic or failure_count >= budget.max_failures_before_stop:
                stop_reason = (
                    "systemic failure"
                    if systemic
                    else "max_failures_before_stop reached"
                )
                status = "failed"
                break
            if provider_calls_required and not model_calls_complete:
                stop_reason = "provider model-call count unknown; stopped before another invocation"
                status = "stopped"
                break
            continue

        scenario_status = result.status.value
        scenario_metrics = _scenario_metrics(scenario, result)
        result_references = list(result.artifacts)
        raw_artifact_references.extend(result_references)
        results.append(
            {
                "scenario_id": scenario.scenario_id,
                "category": scenario.category,
                "fixture": scenario.fixture,
                "base_revision": scenario.base_revision,
                "contract_sha256": contract_hashes[scenario.scenario_id],
                "harness_run_id": result.run_id,
                "status": scenario_status,
                "observations": _json_value(result.observations),
                "failures": list(result.errors),
                "token_usage": (
                    dict(result.token_usage)
                    if result.token_usage is not None
                    else "unknown"
                ),
                "latency_ms": (
                    result.latency_ms if result.latency_ms is not None else "unknown"
                ),
                "model_turns": (
                    result.model_turns if result.model_turns is not None else "unknown"
                ),
                "model_calls": (
                    result.model_calls if result.model_calls is not None else "unknown"
                ),
                "raw_artifact_references": result_references,
            }
        )
        metric_results[scenario.scenario_id] = scenario_metrics
        if result.token_usage is None:
            token_usage_complete = False
            known_token_total_complete = False
        else:
            saw_known_tokens = True
            token_totals = _add_token_counts(token_totals, result.token_usage)
            scenario_token_total = _total_token_count(result.token_usage)
            if scenario_token_total is None:
                known_token_total_complete = False
            else:
                known_tokens += scenario_token_total
        if result.model_turns is None:
            model_turns_complete = False
        else:
            saw_model_turns = True
            model_turns_total += result.model_turns
        if result.model_calls is None:
            model_calls_complete = False
        else:
            saw_model_calls = True
            model_calls_total += result.model_calls
        if result.latency_ms is None:
            latency_known = False
        else:
            total_latency += result.latency_ms

        if result.status is not ResultStatus.PASSED:
            failure_count += 1
            failures.append(
                {
                    "scenario_id": scenario.scenario_id,
                    "kind": "scenario_failed",
                    "message": "; ".join(result.errors) or "scenario did not pass",
                    "systemic": False,
                }
            )
            if failure_count >= budget.max_failures_before_stop:
                stop_reason = "max_failures_before_stop reached"
                status = "failed"
                break
        if (
            not known_token_total_complete
            and budget.max_tokens_if_known is not None
            and scenario_index + 1 < len(suite.scenarios)
        ):
            stop_reason = "token usage unknown; stopped before another model call"
            status = "stopped"
            break
        if (
            budget.max_tokens_if_known is not None
            and saw_known_tokens
            and known_tokens > budget.max_tokens_if_known
        ):
            stop_reason = "reported token usage exceeded max_tokens_if_known"
            status = "stopped"
            break
        if (
            provider_calls_required
            and result.model_calls is None
            and scenario_index + 1 < len(suite.scenarios)
        ):
            stop_reason = (
                "provider model-call count unknown; stopped before another invocation"
            )
            status = "stopped"
            break
        if (
            model_calls_complete
            and budget.max_model_calls is not None
            and model_calls_total > budget.max_model_calls
        ):
            stop_reason = "reported provider model calls exceeded max_model_calls"
            status = "stopped"
            break
        if harness == "codex" and result.model_turns != 1:
            stop_reason = (
                "Codex turn count unknown; stopped before another invocation"
                if result.model_turns is None
                else "Codex used more or fewer than one turn; stopped before another invocation"
            )
            status = "stopped"
            break

    artifact = {
        "schema_version": _ARTIFACT_SCHEMA_VERSION,
        "run_id": selected_run_id,
        "suite_id": suite.suite_id,
        "harness": harness,
        "copilot_reason": copilot_reason,
        "model": model.strip(),
        "base_revision": suite.base_revision,
        "suite": suite.as_dict(),
        "plugin_profile": profile.as_dict(),
        "model_call_limit_enforced": model_call_limit_enforced,
        "started_at": started_at,
        "finished_at": _utc_now(),
        "status": status,
        "budget": budget.as_dict(),
        "scenario_contracts": contract_hashes,
        "results": results,
        "metrics": metric_results,
        "failures": failures,
        "usage": {
            "runs": runs,
            "harness_invocations": harness_invocations,
            "model_calls": (
                0
                if harness_invocations == 0
                else (
                    model_calls_total
                    if model_calls_complete and saw_model_calls
                    else "unknown"
                )
            ),
            "model_turns": (
                model_turns_total
                if model_turns_complete and saw_model_turns
                else "unknown"
            ),
            "failures": failure_count,
            "known_tokens_total": (
                known_tokens
                if known_token_total_complete and saw_known_tokens
                else "unknown"
            ),
        },
        "token_usage": (
            token_totals if token_usage_complete and saw_known_tokens else "unknown"
        ),
        "latency_ms": total_latency if latency_known and results else "unknown",
        "raw_artifact_references": raw_artifact_references,
        "stop_reason": stop_reason,
    }
    save_run_artifact(Path(artifact_path), artifact)
    return artifact


def save_run_artifact(path: Path, artifact: Mapping[str, Any]) -> None:
    _validate_artifact(artifact)
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        raise HarnessFactoryError(f"evaluation artifact already exists: {destination}")
    _write_json_atomic(destination, artifact, prefix=".evaluation-")


def load_run_artifact(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(
            Path(path).read_text(encoding="utf-8"),
            object_pairs_hook=_unique_json_object,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise HarnessFactoryError(
            f"evaluation artifact could not be loaded: {exc}"
        ) from exc
    _validate_artifact(raw)
    return raw


def compare_run_artifacts(
    left: Path | Mapping[str, Any], right: Path | Mapping[str, Any]
) -> dict[str, Any]:
    left_artifact = _load_artifact_input(left)
    right_artifact = _load_artifact_input(right)
    for field in ("suite_id", "base_revision", "harness"):
        if left_artifact[field] != right_artifact[field]:
            raise ValueError(f"run artifacts are not matched: {field} differs")
    if left_artifact["scenario_contracts"] != right_artifact["scenario_contracts"]:
        raise ValueError(
            "run artifacts are not matched on fixture, prompt, and expected behavior"
        )
    left_profile = left_artifact["plugin_profile"]["profile_id"]
    right_profile = right_artifact["plugin_profile"]["profile_id"]
    if left_artifact["run_id"] == right_artifact["run_id"]:
        raise ValueError("matched comparison requires two distinct run artifacts")
    if left_profile == right_profile:
        raise ValueError("matched comparison requires two distinct profile variants")

    comparisons: dict[str, dict[str, Any]] = {}
    for scenario_id in sorted(left_artifact["scenario_contracts"]):
        left_metrics = left_artifact["metrics"].get(scenario_id, {})
        right_metrics = right_artifact["metrics"].get(scenario_id, {})
        metrics: dict[str, Any] = {}
        for name in sorted(set(left_metrics) | set(right_metrics)):
            left_value = left_metrics.get(name, "unknown")
            right_value = right_metrics.get(name, "unknown")
            if "unknown" in (left_value, right_value):
                delta: Any = "unknown"
            elif (
                isinstance(left_value, (int, float))
                and not isinstance(left_value, bool)
                and isinstance(right_value, (int, float))
                and not isinstance(right_value, bool)
            ):
                delta = right_value - left_value
            else:
                delta = "unchanged" if left_value == right_value else "changed"
            metrics[name] = {
                "left": left_value,
                "right": right_value,
                "delta": delta,
            }
        comparisons[scenario_id] = metrics
    return {
        "schema_version": 1,
        "comparison_id": uuid.uuid4().hex,
        "suite_id": left_artifact["suite_id"],
        "harness": left_artifact["harness"],
        "base_revision": left_artifact["base_revision"],
        "matched": True,
        "left_run_id": left_artifact["run_id"],
        "left_profile_id": left_profile,
        "right_run_id": right_artifact["run_id"],
        "right_profile_id": right_profile,
        "metrics": comparisons,
    }


def _scenario_metrics(scenario: Scenario, result: HarnessResult) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for name in scenario.metrics:
        if name in result.observations:
            output[name] = _json_value(result.observations[name])
        elif name == "correctness":
            output[name] = result.status is ResultStatus.PASSED
        elif name == "latency_ms":
            output[name] = (
                result.latency_ms if result.latency_ms is not None else "unknown"
            )
        elif name == "model_turns":
            output[name] = (
                result.model_turns if result.model_turns is not None else "unknown"
            )
        elif name == "model_calls":
            output[name] = (
                result.model_calls if result.model_calls is not None else "unknown"
            )
        elif name in {"tokens", "total_tokens"}:
            output[name] = (
                _total_token_count(result.token_usage)
                if result.token_usage is not None
                else "unknown"
            )
            if output[name] is None:
                output[name] = "unknown"
        elif name in {"input_tokens", "output_tokens"}:
            output[name] = (
                result.token_usage.get(name, "unknown")
                if result.token_usage is not None
                else "unknown"
            )
        else:
            output[name] = "unknown"
    return output


def _total_token_count(token_usage: Mapping[str, int]) -> int | None:
    for name in ("total_tokens", "total"):
        value = token_usage.get(name)
        if type(value) is int and value >= 0:
            return value
    for input_name, output_name in (
        ("input_tokens", "output_tokens"),
        ("prompt_tokens", "completion_tokens"),
    ):
        input_tokens = token_usage.get(input_name)
        output_tokens = token_usage.get(output_name)
        if (
            type(input_tokens) is int
            and input_tokens >= 0
            and type(output_tokens) is int
            and output_tokens >= 0
        ):
            return input_tokens + output_tokens
    if len(token_usage) == 1:
        value = next(iter(token_usage.values()))
        if type(value) is int and value >= 0:
            return value
    return None


def _contract_hash(scenario: Scenario) -> str:
    encoded = json.dumps(
        scenario.as_dict(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _add_token_counts(
    current: dict[str, int], added: Mapping[str, int]
) -> dict[str, int]:
    combined = dict(current)
    for name, value in added.items():
        combined[name] = combined.get(name, 0) + value
    return combined


def _json_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if value is None:
        return "unknown"
    if isinstance(value, float) and not math.isfinite(value):
        return "unknown"
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _validate_artifact(value: Any) -> None:
    if not isinstance(value, Mapping) or set(value) != _ARTIFACT_FIELDS:
        raise HarnessFactoryError("evaluation artifact has missing or unknown fields")
    try:
        json.dumps(value, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise HarnessFactoryError(
            "evaluation artifact must contain JSON values"
        ) from exc
    if (
        type(value["schema_version"]) is not int
        or value["schema_version"] != _ARTIFACT_SCHEMA_VERSION
    ):
        raise HarnessFactoryError("unsupported evaluation artifact schema_version")
    for name in ("run_id", "suite_id", "harness", "model", "base_revision", "status"):
        if not isinstance(value[name], str) or not value[name].strip():
            raise HarnessFactoryError(f"evaluation artifact {name} must be non-empty")
    if value["harness"] not in {"codex", "copilot"}:
        raise HarnessFactoryError("evaluation artifact harness is unsupported")
    reason = value["copilot_reason"]
    if value["harness"] == "copilot" and (
        not isinstance(reason, str) or reason not in ALLOWED_COPILOT_REASONS
    ):
        raise HarnessFactoryError("Copilot artifact requires an allowed run reason")
    if value["harness"] == "codex" and reason is not None:
        raise HarnessFactoryError("evaluation artifact has an invalid Copilot reason")
    try:
        suite = validate_suite(value["suite"])
    except (SuiteValidationError, TypeError) as exc:
        raise HarnessFactoryError(
            f"evaluation artifact suite is invalid: {exc}"
        ) from exc
    if (
        suite.suite_id != value["suite_id"]
        or suite.base_revision != value["base_revision"]
    ):
        raise HarnessFactoryError(
            "evaluation artifact identity does not match its suite"
        )
    if value["model_call_limit_enforced"] is not False:
        raise HarnessFactoryError(
            "evaluation artifact cannot claim an unproven provider model-call limit"
        )
    if not isinstance(value["plugin_profile"], Mapping) or set(
        value["plugin_profile"]
    ) != {"profile_id", "source_path", "source_mode", "metadata"}:
        raise HarnessFactoryError(
            "evaluation artifact requires a plugin profile identity"
        )
    plugin_profile = value["plugin_profile"]
    if (
        not isinstance(plugin_profile["profile_id"], str)
        or not plugin_profile["profile_id"].strip()
        or not isinstance(plugin_profile["source_path"], str)
        or not plugin_profile["source_path"].strip()
        or not isinstance(plugin_profile["source_mode"], str)
        or plugin_profile["source_mode"] not in {"external", "base_revision"}
        or not isinstance(plugin_profile["metadata"], Mapping)
    ):
        raise HarnessFactoryError(
            "evaluation artifact plugin profile fields are invalid"
        )
    if plugin_profile["source_mode"] == "base_revision":
        source_path = Path(plugin_profile["source_path"])
        if source_path.is_absolute() or ".." in source_path.parts:
            raise HarnessFactoryError(
                "evaluation artifact base_revision source is unsafe"
            )
    if _RUN_ID_PATTERN.fullmatch(value["run_id"]) is None:
        raise HarnessFactoryError("evaluation artifact run_id is invalid")
    if _REVISION_PATTERN.fullmatch(value["base_revision"]) is None:
        raise HarnessFactoryError("evaluation artifact base_revision is invalid")
    if value["status"] not in {"completed", "failed", "stopped", "blocked"}:
        raise HarnessFactoryError("evaluation artifact status is unsupported")
    for name in ("started_at", "finished_at"):
        if not isinstance(value[name], str) or not value[name].strip():
            raise HarnessFactoryError(f"evaluation artifact {name} must be non-empty")
    for name in ("scenario_contracts", "metrics"):
        if not isinstance(value[name], Mapping):
            raise HarnessFactoryError(f"evaluation artifact {name} must be an object")
    expected_contracts = {
        scenario.scenario_id: _contract_hash(scenario) for scenario in suite.scenarios
    }
    if value["scenario_contracts"] != expected_contracts:
        raise HarnessFactoryError("evaluation artifact scenario contracts are invalid")
    scenario_by_id = {scenario.scenario_id: scenario for scenario in suite.scenarios}
    if set(value["metrics"]) != set(scenario_by_id):
        raise HarnessFactoryError("evaluation artifact metrics do not match the suite")
    for scenario_id, scenario_metrics in value["metrics"].items():
        if not isinstance(scenario_metrics, Mapping) or set(scenario_metrics) != set(
            scenario_by_id[scenario_id].metrics
        ):
            raise HarnessFactoryError(
                "evaluation artifact scenario metrics are invalid"
            )
    for name in ("results", "failures", "raw_artifact_references"):
        if not isinstance(value[name], list):
            raise HarnessFactoryError(f"evaluation artifact {name} must be an array")
    result_fields = {
        "scenario_id",
        "category",
        "fixture",
        "base_revision",
        "contract_sha256",
        "harness_run_id",
        "status",
        "observations",
        "failures",
        "token_usage",
        "latency_ms",
        "model_turns",
        "model_calls",
        "raw_artifact_references",
    }
    result_scenarios: set[str] = set()
    result_references: list[str] = []
    for result in value["results"]:
        if not isinstance(result, Mapping) or set(result) != result_fields:
            raise HarnessFactoryError("evaluation artifact result fields are invalid")
        scenario_id = result["scenario_id"]
        if not isinstance(scenario_id, str):
            raise HarnessFactoryError("evaluation artifact result scenario is invalid")
        scenario = scenario_by_id.get(scenario_id)
        if scenario is None or scenario_id in result_scenarios:
            raise HarnessFactoryError("evaluation artifact result scenario is invalid")
        result_scenarios.add(scenario_id)
        if (
            result["category"] != scenario.category
            or result["fixture"] != scenario.fixture
            or result["base_revision"] != scenario.base_revision
            or result["contract_sha256"] != expected_contracts[scenario_id]
            or (
                result["harness_run_id"] != "unknown"
                and (
                    not isinstance(result["harness_run_id"], str)
                    or re.fullmatch(r"[0-9a-f]{32}", result["harness_run_id"]) is None
                )
            )
        ):
            raise HarnessFactoryError(
                "evaluation artifact result contract is mismatched"
            )
        if not isinstance(result["status"], str) or result["status"] not in {
            "passed",
            "failed",
            "blocked",
        }:
            raise HarnessFactoryError("evaluation artifact result status is invalid")
        if not isinstance(result["observations"], Mapping):
            raise HarnessFactoryError(
                "evaluation artifact observations must be an object"
            )
        if not isinstance(result["failures"], list) or any(
            not isinstance(message, str) for message in result["failures"]
        ):
            raise HarnessFactoryError("evaluation artifact result failures are invalid")
        if result["token_usage"] != "unknown" and (
            not isinstance(result["token_usage"], Mapping)
            or any(
                not isinstance(name, str) or type(count) is not int or count < 0
                for name, count in result["token_usage"].items()
            )
        ):
            raise HarnessFactoryError(
                "evaluation artifact result token usage is invalid"
            )
        if result["latency_ms"] != "unknown" and (
            type(result["latency_ms"]) is not int or result["latency_ms"] < 0
        ):
            raise HarnessFactoryError("evaluation artifact result latency is invalid")
        if result["model_turns"] != "unknown" and (
            type(result["model_turns"]) is not int or result["model_turns"] < 0
        ):
            raise HarnessFactoryError("evaluation artifact model turn count is invalid")
        if result["model_calls"] != "unknown" and (
            type(result["model_calls"]) is not int or result["model_calls"] < 0
        ):
            raise HarnessFactoryError(
                "evaluation artifact provider model-call count is invalid"
            )
        if not isinstance(result["raw_artifact_references"], list) or any(
            not isinstance(reference, str)
            for reference in result["raw_artifact_references"]
        ):
            raise HarnessFactoryError(
                "evaluation artifact result references are invalid"
            )
        result_references.extend(result["raw_artifact_references"])
    if result_references != value["raw_artifact_references"]:
        raise HarnessFactoryError("evaluation artifact raw references are inconsistent")
    for failure in value["failures"]:
        if (
            not isinstance(failure, Mapping)
            or set(failure) != {"scenario_id", "kind", "message", "systemic"}
            or not isinstance(failure["scenario_id"], str)
            or failure["scenario_id"] not in scenario_by_id
            or not isinstance(failure["kind"], str)
            or not isinstance(failure["message"], str)
            or type(failure["systemic"]) is not bool
        ):
            raise HarnessFactoryError("evaluation artifact failure records are invalid")
    if not isinstance(value["usage"], Mapping) or not isinstance(
        value["budget"], Mapping
    ):
        raise HarnessFactoryError(
            "evaluation artifact requires budget and usage objects"
        )
    try:
        run_budget = _validated_run_budget(value["budget"])
    except (TypeError, ValueError) as exc:
        raise HarnessFactoryError(
            "evaluation artifact budget values are invalid"
        ) from exc
    if set(value["usage"]) != {
        "runs",
        "harness_invocations",
        "model_calls",
        "model_turns",
        "failures",
        "known_tokens_total",
    }:
        raise HarnessFactoryError("evaluation artifact usage fields are invalid")
    for name in ("runs", "harness_invocations", "failures"):
        if type(value["usage"][name]) is not int or value["usage"][name] < 0:
            raise HarnessFactoryError(f"evaluation artifact usage {name} is invalid")
    if (
        value["usage"]["runs"] != value["usage"]["harness_invocations"]
        or value["usage"]["runs"] != len(value["results"])
        or value["usage"]["failures"] != len(value["failures"])
    ):
        raise HarnessFactoryError("evaluation artifact usage totals are inconsistent")
    model_calls = value["usage"]["model_calls"]
    if model_calls != "unknown" and (type(model_calls) is not int or model_calls < 0):
        raise HarnessFactoryError(
            "evaluation artifact provider model-call total is invalid"
        )
    if (
        value["usage"]["harness_invocations"] > 0
        and "provider_model_calls" in run_budget.required_enforcement
        and not value["model_call_limit_enforced"]
    ):
        raise HarnessFactoryError(
            "evaluation artifact has harness invocations without its required provider model-call limit"
        )
    if value["usage"]["harness_invocations"] == 0 and model_calls != 0:
        raise HarnessFactoryError(
            "evaluation artifact must record zero model calls before any invocation"
        )
    if (
        type(model_calls) is int
        and run_budget.max_model_calls is not None
        and model_calls > run_budget.max_model_calls
    ):
        raise HarnessFactoryError("evaluation artifact exceeds its model-call budget")
    for field in ("model_turns", "known_tokens_total"):
        count = value["usage"][field]
        if count != "unknown" and (type(count) is not int or count < 0):
            raise HarnessFactoryError(f"evaluation artifact usage {field} is invalid")
    if (
        value["usage"]["runs"] > value["budget"]["max_runs"]
        or value["usage"]["failures"] > value["budget"]["max_failures_before_stop"]
    ):
        raise HarnessFactoryError("evaluation artifact exceeds its recorded budget")
    if value["token_usage"] != "unknown" and not isinstance(
        value["token_usage"], Mapping
    ):
        raise HarnessFactoryError("evaluation artifact token_usage is invalid")
    if isinstance(value["token_usage"], Mapping) and any(
        not isinstance(name, str) or type(count) is not int or count < 0
        for name, count in value["token_usage"].items()
    ):
        raise HarnessFactoryError("evaluation artifact token totals are invalid")
    if value["latency_ms"] != "unknown" and (
        type(value["latency_ms"]) is not int or value["latency_ms"] < 0
    ):
        raise HarnessFactoryError("evaluation artifact latency_ms is invalid")
    if value["stop_reason"] is not None and not isinstance(value["stop_reason"], str):
        raise HarnessFactoryError("evaluation artifact stop_reason is invalid")
    if any(
        not isinstance(reference, str) for reference in value["raw_artifact_references"]
    ):
        raise HarnessFactoryError("evaluation artifact raw references must be strings")


def _load_artifact_input(value: Path | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(value, Path):
        return load_run_artifact(value)
    _validate_artifact(value)
    return dict(value)


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _write_json_atomic(
    destination: Path,
    payload: Mapping[str, Any],
    *,
    prefix: str,
) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=prefix, suffix=".tmp", dir=destination.parent
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, destination)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
