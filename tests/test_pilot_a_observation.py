from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness_factory.pilot_a_observation import (
    observe_codex_events,
    pilot_a_metrics,
)


def _skill_metric(skill: str) -> dict[str, object]:
    return {
        "resourceMetrics": [
            {
                "scopeMetrics": [
                    {
                        "metrics": [
                            {
                                "name": "codex.skill.injected",
                                "sum": {
                                    "dataPoints": [
                                        {
                                            "attributes": [
                                                {
                                                    "key": "skill",
                                                    "value": {"stringValue": skill},
                                                },
                                                {
                                                    "key": "invoke_type",
                                                    "value": {
                                                        "stringValue": "explicit"
                                                    },
                                                },
                                            ]
                                        }
                                    ]
                                },
                            }
                        ]
                    }
                ]
            }
        ]
    }


def test_route_observer_uses_only_native_skill_metric_not_final_prose():
    observed = observe_codex_events(
        [_skill_metric("plugin-engineering"), {"final_output": "route: create-skill"}],
        requested_route="plugin-engineering",
    )

    assert observed.actual_trigger is True
    assert observed.actual_route == "plugin-engineering"
    assert observed.capture_complete is None
    assert observed.requested_route == "plugin-engineering"
    assert observed.invoke_types == ("explicit",)


def test_route_observer_keeps_missing_or_unrecognized_telemetry_unknown():
    missing = observe_codex_events([], requested_route="plugin-engineering")
    malformed = observe_codex_events(
        [
            {
                "type": "item.completed",
                "item": {"type": "agent_message", "text": "plugin-engineering"},
            }
        ],
        requested_route="plugin-engineering",
    )

    assert missing.actual_trigger is None
    assert missing.actual_route is None
    assert missing.capture_complete is None
    assert malformed.actual_trigger is None
    assert malformed.actual_route is None


def test_spawn_agent_event_confirms_thread_delegation_but_role_stays_unknown():
    observed = observe_codex_events(
        [
            {
                "type": "item.completed",
                "item": {
                    "type": "collab_tool_call",
                    "tool": "spawn_agent",
                    "sender_thread_id": "thread-parent",
                    "receiver_thread_ids": ["thread-child", "thread-helper"],
                    "prompt": "Use the architect role.",
                    "status": "completed",
                },
            }
        ],
        requested_role="architect",
    )

    assert observed.delegation.confirmed is True
    assert observed.delegation.sender_thread_id == "thread-parent"
    assert observed.delegation.receiver_thread_ids == (
        "thread-child",
        "thread-helper",
    )
    assert observed.delegation.status == "completed"
    assert observed.delegation.requested_role == "architect"
    assert observed.delegation.observed_role is None


def test_pilot_metrics_separate_standard_false_positive_rate_from_legacy_discovery_rate():
    metrics = pilot_a_metrics(
        [
            {"expected_trigger": False, "actual_trigger": True},  # false positive
            {"expected_trigger": False, "actual_trigger": False},  # true negative
            {"expected_trigger": True, "actual_trigger": True},
        ]
    )

    assert metrics["trigger_false_positive_rate"] == 0.5
    assert metrics["legacy_discovery_false_positive_rate"] == 1 / 3


def test_case_observation_serializes_identity_measurements_and_unknowns():
    from harness_factory.pilot_a_observation import PilotACaseObservation

    record = PilotACaseObservation(
        run_id="run-1",
        case_id="case-1",
        arm="baseline",
        expected_trigger=False,
        actual_trigger=None,
        expected_route=None,
        actual_route=None,
        completion="completed",
        invocation_count=1,
        package_digest="sha256:package",
        canonical_revision="a" * 40,
        raw_reference="artifacts/run-1.jsonl",
        completion_checks=({"id": "AC-PA-ROUTING", "status": "pass"},),
    ).as_dict()

    assert record["case_id"] == "case-1"
    assert record["arm"] == "baseline"
    assert record["actual_trigger"] == "unknown"
    assert record["expected_route"] == "unknown"
    assert record["provider_model_calls"] == "unknown"
    assert record["model_turns"] == "unknown"
    assert record["tokens"] == "unknown"
    assert record["latency_ms"] == "unknown"
    assert record["package_digest"] == "sha256:package"
    assert record["canonical_revision"] == "a" * 40
    assert record["raw_reference"] == "artifacts/run-1.jsonl"
    assert record["completion"] == "completed"
    assert record["completion_checks"] == [{"id": "AC-PA-ROUTING", "status": "pass"}]


def test_recognized_other_skill_is_not_a_trigger_for_the_requested_route():
    observed = observe_codex_events(
        [_skill_metric("architecture")],
        requested_route="plugin-engineering",
    )

    assert observed.actual_trigger is False
    assert observed.actual_route == "architecture"
    assert observed.capture_complete is None


def test_absent_skill_events_stay_unknown_for_a_requested_route():
    observed = observe_codex_events([], requested_route="plugin-engineering")

    assert observed.actual_trigger is None
    assert observed.actual_route is None
    assert observed.capture_complete is None
