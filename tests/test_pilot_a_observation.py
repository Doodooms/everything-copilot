from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness_factory.pilot_a_observation import (
    SkillTelemetryCaptureContract,
    observe_codex_events,
    pilot_a_metrics,
)


def _skill_metric(skill: str, *, status: object = "ok") -> dict[str, object]:
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
                                                {
                                                    "key": "status",
                                                    "value": {"stringValue": status},
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
    assert observed.skill_injections[0].status == "ok"
    assert observed.as_dict()["skill_injections"][0]["status"] == "ok"


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
            },
            {
                "type": "item.started",
                "item": {
                    "type": "collab_tool_call",
                    "tool": "spawn_agent",
                    "sender_thread_id": "thread-parent",
                    "receiver_thread_ids": ["thread-reviewer"],
                    "prompt": "Use the reviewer role.",
                    "status": "in_progress",
                },
            },
        ],
        requested_role="architect",
    )

    assert len(observed.delegations) == 2
    assert observed.delegations[0].confirmed is True
    assert observed.delegations[0].sender_thread_id == "thread-parent"
    assert observed.delegations[0].receiver_thread_ids == (
        "thread-child",
        "thread-helper",
    )
    assert observed.delegations[0].status == "completed"
    assert observed.delegations[0].requested_role == "architect"
    assert observed.delegations[0].observed_role is None
    assert observed.delegations[1].receiver_thread_ids == ("thread-reviewer",)
    assert observed.as_dict()["delegations"][1]["status"] == "in_progress"


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
        capture_complete=None,
    ).as_dict()

    assert record["case_id"] == "case-1"
    assert record["arm"] == "baseline"
    assert record["actual_trigger"] == "unknown"
    assert record["capture_complete"] == "unknown"
    assert record["delegations"] == []
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

    assert observed.actual_trigger is None
    assert observed.actual_route == "architecture"
    assert observed.capture_complete is None


def test_absent_skill_events_stay_unknown_for_a_requested_route():
    observed = observe_codex_events([], requested_route="plugin-engineering")

    assert observed.actual_trigger is None
    assert observed.actual_route is None
    assert observed.capture_complete is None


def test_complete_capture_without_target_is_a_proven_non_invocation():
    observed = observe_codex_events(
        [_skill_metric("architecture")],
        requested_route="plugin-engineering",
        capture_contract=SkillTelemetryCaptureContract(
            capture_id="capture-1",
            status="complete",
            dropped_data_points=0,
            stream_closed=True,
        ),
    )

    assert observed.actual_trigger is False
    assert observed.capture_complete is True


def test_incomplete_capture_without_target_remains_unknown():
    observed = observe_codex_events(
        [_skill_metric("architecture")],
        requested_route="plugin-engineering",
        capture_contract=SkillTelemetryCaptureContract(
            capture_id="capture-2",
            status="partial",
            dropped_data_points=1,
            stream_closed=False,
        ),
    )

    assert observed.actual_trigger is None
    assert observed.capture_complete is False


def test_complete_capture_with_no_skill_event_proves_non_invocation():
    observed = observe_codex_events(
        [],
        requested_route="plugin-engineering",
        capture_contract=SkillTelemetryCaptureContract(
            capture_id="capture-3",
            status="complete",
            dropped_data_points=0,
            stream_closed=True,
        ),
    )

    assert observed.actual_trigger is False
    assert observed.capture_complete is True


def test_case_record_can_store_all_observed_delegations():
    from harness_factory.pilot_a_observation import (
        DelegationObservation,
        PilotACaseObservation,
    )

    record = PilotACaseObservation(
        run_id="run-2",
        case_id="case-2",
        arm="candidate",
        expected_trigger=True,
        actual_trigger=True,
        expected_route="plugin-engineering",
        actual_route="plugin-engineering",
        completion="completed",
        invocation_count=1,
        capture_complete=True,
        delegations=(
            DelegationObservation(
                confirmed=True,
                sender_thread_id="parent",
                receiver_thread_ids=("child-a", "child-b"),
                status="completed",
            ),
            DelegationObservation(
                confirmed=True,
                sender_thread_id="parent",
                receiver_thread_ids=("child-c",),
                status="completed",
            ),
        ),
    ).as_dict()

    assert len(record["delegations"]) == 2
    assert record["capture_complete"] is True
    assert record["delegations"][0]["receiver_thread_ids"] == ["child-a", "child-b"]
    assert record["delegations"][1]["receiver_thread_ids"] == ["child-c"]


def test_failed_skill_injection_remains_an_observed_selection_attempt():
    observed = observe_codex_events(
        [_skill_metric("plugin-engineering", status="error")],
        requested_route="plugin-engineering",
    )

    assert observed.actual_trigger is True
    assert observed.skill_injections[0].status == "error"


def test_missing_or_malformed_skill_injection_status_stays_unknown():
    missing = observe_codex_events(
        [_skill_metric("plugin-engineering", status=None)],
        requested_route="plugin-engineering",
    )
    malformed = observe_codex_events(
        [_skill_metric("plugin-engineering", status="failed")],
        requested_route="plugin-engineering",
    )

    assert missing.actual_trigger is True
    assert missing.skill_injections[0].status is None
    assert malformed.actual_trigger is True
    assert malformed.skill_injections[0].status is None


def test_case_record_preserves_skill_injection_status():
    from harness_factory.pilot_a_observation import (
        PilotACaseObservation,
        SkillInjectionObservation,
    )

    record = PilotACaseObservation(
        run_id="run-3",
        case_id="case-3",
        arm="candidate",
        expected_trigger=True,
        actual_trigger=True,
        expected_route="plugin-engineering",
        actual_route="plugin-engineering",
        completion="completed",
        invocation_count=1,
        skill_injections=(
            SkillInjectionObservation(
                skill="plugin-engineering", invoke_type="explicit", status="error"
            ),
        ),
    ).as_dict()

    assert record["skill_injections"][0] == {
        "skill": "plugin-engineering",
        "invoke_type": "explicit",
        "status": "error",
    }
