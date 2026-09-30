from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tempfile import TemporaryDirectory

from harness_factory.evaluation import EvaluationProfile, RunBudget, run_suite
from harness_factory.pilot_a_observation import (
    PilotABudget,
    execute_pilot_a_schedule,
    make_pilot_a_schedule,
)
from harness_factory.suites import validate_suite

BASE = "a" * 40


def test_existing_provider_call_required_evaluation_blocks_before_any_invocation():
    suite = validate_suite(
        {
            "schema_version": 1,
            "suite_id": "legacy-provider-budget",
            "base_revision": BASE,
            "scenarios": [
                {
                    "id": "case-1",
                    "category": "skill_routing",
                    "fixture": "fixture-1",
                    "base_revision": BASE,
                    "prompt": "route to a skill",
                    "expected_behavior": "select the matching skill",
                    "required": [],
                    "forbidden": [],
                    "optional": [],
                    "metrics": {"route_accuracy": "fraction"},
                }
            ],
        }
    )
    calls: list[str] = []
    with TemporaryDirectory() as directory:
        root = Path(directory)
        profile_dir = root / "profile"
        profile_dir.mkdir()
        result = run_suite(
            suite,
            EvaluationProfile("legacy", profile_dir),
            harness="codex",
            budget=RunBudget(1, 5, None, 1),
            invoke=lambda scenario, _profile: calls.append(scenario.scenario_id),
            artifact_path=root / "artifact.json",
            run_id="1" * 32,
        )

    assert result["status"] == "blocked"
    assert result["usage"]["harness_invocations"] == 0
    assert (
        result["stop_reason"]
        == "provider model-call limit cannot be enforced by the selected harness"
    )
    assert calls == []


def test_pilot_budget_enforces_local_harness_cap_and_allows_unknown_provider_calls():
    budget = PilotABudget(max_harness_invocations=24)
    schedule = make_pilot_a_schedule([f"case-{index}" for index in range(1, 13)])
    called: list[tuple[str, str]] = []
    result = execute_pilot_a_schedule(
        schedule,
        budget=budget,
        case_ids=[f"case-{index}" for index in range(1, 13)],
        invoke=lambda pair: (
            called.append((pair.case_id, pair.arm))
            or {"status": "passed", "provider_model_calls": None}
        ),
    )

    assert len(schedule) == 24
    assert len(called) == 24
    assert len({(item.case_id, item.arm) for item in schedule}) == 24
    assert [item.invocation_number for item in result.invocations] == list(range(1, 25))
    assert all(item.provider_model_calls is None for item in result.invocations)
    assert result.status == "completed"
    assert result.harness_invocations == 24
    assert result.provider_model_calls == "unknown"
    assert budget.required_enforcement == ("harness_invocations",)
    assert budget.provider_model_calls == "unknown"


def test_pilot_schedule_is_sequential_without_retries_and_stops_on_first_failure():
    schedule = make_pilot_a_schedule([f"case-{index}" for index in range(1, 13)])
    calls: list[tuple[str, str]] = []

    def invoke(pair):
        calls.append((pair.case_id, pair.arm))
        return {"status": "failed" if len(calls) == 3 else "passed"}

    result = execute_pilot_a_schedule(
        schedule,
        budget=PilotABudget(max_harness_invocations=24),
        case_ids=[f"case-{index}" for index in range(1, 13)],
        invoke=invoke,
    )

    assert len(calls) == result.harness_invocations == 3
    assert [item.invocation_number for item in result.invocations] == [1, 2, 3]
    assert result.status == "failed"
    assert result.invocations[-1].status == "failed"
    assert result.invocations[-1].retry_count == 0
    assert result.invocations[-1].case_id == "case-2"
    assert result.invocations[-1].arm == "baseline"


def test_pilot_budget_rejects_a_cap_smaller_than_the_frozen_schedule():
    schedule = make_pilot_a_schedule([f"case-{index}" for index in range(1, 13)])
    called: list[object] = []

    result = execute_pilot_a_schedule(
        schedule,
        budget=PilotABudget(max_harness_invocations=23),
        case_ids=[f"case-{index}" for index in range(1, 13)],
        invoke=lambda pair: called.append(pair) or {"status": "passed"},
    )

    assert result.status == "blocked"
    assert result.harness_invocations == 0
    assert (
        result.stop_reason
        == "local harness invocation budget is below the frozen schedule"
    )
    assert called == []


def test_pilot_schedule_rejects_thirteen_case_ids_even_when_pair_count_is_24():
    from harness_factory.pilot_a_observation import CaseArm

    schedule = [
        CaseArm(case_id=f"case-{index}", arm=arm)
        for index in range(1, 12)
        for arm in ("baseline", "candidate")
    ]
    schedule.extend(
        [
            CaseArm(case_id="case-12", arm="baseline"),
            CaseArm(case_id="case-13", arm="baseline"),
        ]
    )

    try:
        execute_pilot_a_schedule(
            schedule,
            budget=PilotABudget(),
            case_ids=[f"case-{index}" for index in range(1, 13)],
            invoke=lambda _pair: {"status": "passed"},
        )
    except ValueError as exc:
        assert "make_pilot_a_schedule" in str(exc)
    else:
        raise AssertionError("13 case IDs must not satisfy the frozen schedule")


def test_pilot_schedule_rejects_noncanonical_arm_order():
    from harness_factory.pilot_a_observation import CaseArm

    schedule = list(make_pilot_a_schedule([f"case-{index}" for index in range(1, 13)]))
    schedule[0], schedule[1] = (
        CaseArm("case-1", "candidate"),
        CaseArm("case-1", "baseline"),
    )

    try:
        execute_pilot_a_schedule(
            schedule,
            budget=PilotABudget(),
            case_ids=[f"case-{index}" for index in range(1, 13)],
            invoke=lambda _pair: {"status": "passed"},
        )
    except ValueError as exc:
        assert "make_pilot_a_schedule" in str(exc)
    else:
        raise AssertionError("noncanonical arm order must not be accepted")


def test_pilot_schedule_rejects_interleaved_case_major_order():
    from harness_factory.pilot_a_observation import CaseArm

    case_ids = [f"case-{index}" for index in range(1, 13)]
    schedule = [CaseArm(case_id=case_id, arm="baseline") for case_id in case_ids]
    schedule.extend(CaseArm(case_id=case_id, arm="candidate") for case_id in case_ids)

    try:
        execute_pilot_a_schedule(
            schedule,
            budget=PilotABudget(),
            case_ids=[f"case-{index}" for index in range(1, 13)],
            invoke=lambda _pair: {"status": "passed"},
        )
    except ValueError as exc:
        assert "make_pilot_a_schedule" in str(exc)
    else:
        raise AssertionError("interleaved arms must not be accepted")


def test_pilot_schedule_rejects_reordered_case_blocks():
    schedule = list(make_pilot_a_schedule([f"case-{index}" for index in range(1, 13)]))
    schedule[0:2], schedule[2:4] = schedule[2:4], schedule[0:2]

    try:
        execute_pilot_a_schedule(
            schedule,
            budget=PilotABudget(),
            case_ids=[f"case-{index}" for index in range(1, 13)],
            invoke=lambda _pair: {"status": "passed"},
        )
    except ValueError as exc:
        assert "make_pilot_a_schedule" in str(exc)
    else:
        raise AssertionError("reordered case blocks must not be accepted")
