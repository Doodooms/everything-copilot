"""Harness-neutral behavioral suite contracts and deterministic validation."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .errors import HarnessFactoryError

SUITE_SCHEMA_VERSION = 1
SCENARIO_CATEGORIES = frozenset(
    {
        "skill_discovery",
        "skill_routing",
        "workflow_routing",
        "agent_routing",
        "plugin_loading",
        "mcp_exposure",
        "risk_proportional_routing",
        "evidence_reuse",
        "cross_harness_materialization",
    }
)
_REVISION_PATTERN = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_SUITE_FIELDS = {"schema_version", "suite_id", "base_revision", "scenarios"}
_SCENARIO_FIELDS = {
    "id",
    "category",
    "fixture",
    "base_revision",
    "prompt",
    "expected_behavior",
    "required",
    "forbidden",
    "optional",
    "metrics",
}


class SuiteValidationError(HarnessFactoryError):
    """Raised when a suite document does not satisfy the versioned contract."""

    def __init__(self, errors: list[str] | tuple[str, ...]):
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    category: str
    fixture: str
    base_revision: str
    prompt: str
    expected_behavior: str
    required: tuple[str, ...]
    forbidden: tuple[str, ...]
    optional: tuple[str, ...]
    metrics: Mapping[str, str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.scenario_id,
            "category": self.category,
            "fixture": self.fixture,
            "base_revision": self.base_revision,
            "prompt": self.prompt,
            "expected_behavior": self.expected_behavior,
            "required": list(self.required),
            "forbidden": list(self.forbidden),
            "optional": list(self.optional),
            "metrics": dict(self.metrics),
        }


@dataclass(frozen=True)
class ScenarioSuite:
    suite_id: str
    base_revision: str
    scenarios: tuple[Scenario, ...]
    schema_version: int = SUITE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != SUITE_SCHEMA_VERSION:
            raise SuiteValidationError(("unsupported suite schema_version",))

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "suite_id": self.suite_id,
            "base_revision": self.base_revision,
            "scenarios": [scenario.as_dict() for scenario in self.scenarios],
        }


def validate_suite(raw: Any) -> ScenarioSuite:
    """Validate suite data locally; this function never imports a harness adapter."""

    errors: list[str] = []
    if not isinstance(raw, Mapping):
        raise SuiteValidationError(("suite must be a JSON object",))

    actual_fields = set(raw)
    missing = sorted(_SUITE_FIELDS - actual_fields)
    extra = sorted(actual_fields - _SUITE_FIELDS)
    if missing:
        errors.append(f"suite is missing fields: {', '.join(missing)}")
    if extra:
        errors.append(
            f"suite has unknown fields: {', '.join(str(item) for item in extra)}"
        )

    schema_version = raw.get("schema_version")
    if type(schema_version) is not int or schema_version != SUITE_SCHEMA_VERSION:
        errors.append(f"schema_version must be {SUITE_SCHEMA_VERSION}")

    suite_id = _required_text(raw.get("suite_id"), "suite_id", errors)
    if suite_id and _ID_PATTERN.fullmatch(suite_id) is None:
        errors.append("suite_id must be a lowercase stable identifier")
    base_revision = _required_revision(
        raw.get("base_revision"), "base_revision", errors
    )
    raw_scenarios = raw.get("scenarios")
    if not isinstance(raw_scenarios, list) or not raw_scenarios:
        errors.append("scenarios must be a non-empty array")
        raw_scenarios = []

    scenarios: list[Scenario] = []
    seen_ids: set[str] = set()
    for index, value in enumerate(raw_scenarios):
        scenario_value = _validate_scenario(value, index, base_revision, errors)
        if scenario_value is None:
            continue
        if scenario_value.scenario_id in seen_ids:
            errors.append(
                f"scenarios[{index}].id duplicates {scenario_value.scenario_id!r}"
            )
        seen_ids.add(scenario_value.scenario_id)
        scenarios.append(scenario_value)

    if errors:
        raise SuiteValidationError(errors)
    return ScenarioSuite(
        suite_id=suite_id,
        base_revision=base_revision,
        scenarios=tuple(scenarios),
        schema_version=schema_version,
    )


def load_suite(path: Path) -> ScenarioSuite:
    """Load and validate a UTF-8 JSON suite, rejecting duplicate object keys."""

    try:
        raw = json.loads(
            Path(path).read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SuiteValidationError((f"suite could not be loaded: {exc}",)) from exc
    return validate_suite(raw)


def _validate_scenario(
    raw: Any,
    index: int,
    suite_revision: str,
    errors: list[str],
) -> Scenario | None:
    label = f"scenarios[{index}]"
    if not isinstance(raw, Mapping):
        errors.append(f"{label} must be a JSON object")
        return None

    fields = set(raw)
    missing = sorted(_SCENARIO_FIELDS - fields)
    extra = sorted(fields - _SCENARIO_FIELDS)
    if missing:
        errors.append(f"{label} is missing fields: {', '.join(missing)}")
    if extra:
        errors.append(
            f"{label} has unknown fields: {', '.join(str(item) for item in extra)}"
        )

    scenario_id = _required_text(raw.get("id"), f"{label}.id", errors)
    if scenario_id and _ID_PATTERN.fullmatch(scenario_id) is None:
        errors.append(f"{label}.id must be a lowercase stable identifier")
    category = raw.get("category")
    if not isinstance(category, str) or category not in SCENARIO_CATEGORIES:
        errors.append(
            f"{label}.category must be one of: {', '.join(sorted(SCENARIO_CATEGORIES))}"
        )
        category = ""
    fixture = _required_text(raw.get("fixture"), f"{label}.fixture", errors)
    revision = _required_revision(
        raw.get("base_revision"), f"{label}.base_revision", errors
    )
    if revision and suite_revision and revision != suite_revision:
        errors.append(f"{label}.base_revision is incompatible with suite base_revision")
    prompt = _required_text(raw.get("prompt"), f"{label}.prompt", errors)
    expected = _required_text(
        raw.get("expected_behavior"), f"{label}.expected_behavior", errors
    )
    required = _observation_list(raw.get("required"), f"{label}.required", errors)
    forbidden = _observation_list(raw.get("forbidden"), f"{label}.forbidden", errors)
    optional = _observation_list(raw.get("optional"), f"{label}.optional", errors)
    conflict = sorted(set(required) & set(forbidden))
    if conflict:
        errors.append(
            f"{label} observations cannot be both required and forbidden: "
            + ", ".join(conflict)
        )
    metrics = _metrics(raw.get("metrics"), f"{label}.metrics", errors)
    if not all((scenario_id, category, fixture, revision, prompt, expected)):
        return None
    return Scenario(
        scenario_id=scenario_id,
        category=category,
        fixture=fixture,
        base_revision=revision,
        prompt=prompt,
        expected_behavior=expected,
        required=required,
        forbidden=forbidden,
        optional=optional,
        metrics=MappingProxyType(metrics),
    )


def _required_text(value: Any, label: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")
        return ""
    return value.strip()


def _required_revision(value: Any, label: str, errors: list[str]) -> str:
    if not isinstance(value, str) or _REVISION_PATTERN.fullmatch(value) is None:
        errors.append(f"{label} must be a resolved lowercase commit SHA")
        return ""
    return value


def _observation_list(value: Any, label: str, errors: list[str]) -> tuple[str, ...]:
    if not isinstance(value, list):
        errors.append(f"{label} must be an array of non-empty strings")
        return ()
    observations: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{label}[{index}] must be a non-empty string")
            continue
        observations.append(item.strip())
    if len(observations) != len(set(observations)):
        errors.append(f"{label} cannot contain duplicates")
    return tuple(observations)


def _metrics(value: Any, label: str, errors: list[str]) -> dict[str, str]:
    if not isinstance(value, Mapping) or not value:
        errors.append(f"{label} must be a non-empty mapping of metric names to units")
        return {}
    result: dict[str, str] = {}
    seen_names: set[str] = set()
    for name, unit in value.items():
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{label} contains an empty or non-string metric name")
            continue
        if not isinstance(unit, str) or not unit.strip():
            errors.append(f"{label}.{name} must be a non-empty unit string")
            continue
        normalized_name = name.strip()
        if normalized_name in seen_names:
            errors.append(f"{label} contains duplicate normalized metric names")
            continue
        seen_names.add(normalized_name)
        result[normalized_name] = unit.strip()
    return result


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result
