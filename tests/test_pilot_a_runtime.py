from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_pilot_a_runtime_cli_declares_a_single_process_schedule_entrypoint():
    from harness_factory.cli import build_parser

    args = build_parser().parse_args(
        [
            "pilot-a-run",
            "--cases",
            "cases.json",
            "--baseline-profile",
            "baseline.json",
            "--candidate-profile",
            "candidate.json",
            "--repo-root",
            "scratch",
            "--base-revision",
            "a" * 40,
            "--state-root",
            "state",
            "--owner",
            "pilot-a-test",
            "--artifact",
            "pilot-a.json",
        ]
    )

    assert args.command == "pilot-a-run"
    assert args.max_harness_invocations == 24
    assert args.capture_skill_telemetry is True


def test_pilot_a_case_spec_rejects_modified_prompt_with_recomputed_metadata(tmp_path):
    from harness_factory.errors import HarnessFactoryError
    from harness_factory.pilot_a_runtime import _load_case_spec

    path = _case_spec(tmp_path)
    spec = json.loads(path.read_text(encoding="utf-8"))
    spec["cases"][0]["prompt"] += " Add an unapproved instruction."
    spec["metadata"]["cases_sha256"] = hashlib.sha256(
        json.dumps(
            spec["cases"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()

    with pytest.raises(HarnessFactoryError, match="accepted canonical digest"):
        _load_case_spec(json.dumps(spec).encode("utf-8"))


@pytest.mark.parametrize("first_attempt", ["completed", "interrupted"])
def test_pilot_a_cli_reserves_schedule_across_relaunches(
    tmp_path, monkeypatch, capsys, first_attempt
):
    from harness_factory import cli
    from harness_factory.models import HarnessResult, ResultStatus, RunStatus

    cases = _case_spec(tmp_path)
    baseline_source = tmp_path / "baseline-source"
    candidate_source = tmp_path / "candidate-source"
    baseline_source.mkdir()
    candidate_source.mkdir()
    (baseline_source / "arm.txt").write_text("baseline", encoding="utf-8")
    (candidate_source / "arm.txt").write_text("candidate", encoding="utf-8")
    baseline_profile = _profile_descriptor(tmp_path, "baseline", baseline_source)
    candidate_profile = _profile_descriptor(tmp_path, "candidate", candidate_source)
    state_root = tmp_path / "state"
    calls: list[tuple[str, str, bool]] = []

    class FakeManager:
        def __init__(self, repo_root, selected_state_root):
            self.repo_root = Path(repo_root)
            self.state_root = Path(selected_state_root)
            self.records = {}

        def resolve_revision(self, revision):
            return revision

        def create_run(self, *, harness, base_revision, mode, owner):
            index = len(calls) + 1
            run_id = f"{index:032x}"
            state_directory = self.state_root / run_id
            workspace = self.state_root / "workspaces" / run_id
            state_directory.mkdir(parents=True)
            workspace.mkdir(parents=True)
            record = SimpleNamespace(
                run_id=run_id,
                harness=harness,
                base_revision=base_revision,
                workspace=workspace,
                state_directory=state_directory,
                mode=mode,
                owner=owner,
                status=RunStatus.PREPARED,
            )
            self.records[run_id] = record
            return record

        def transition(self, run_id, *, owner, status):
            current = self.records[run_id]
            updated = SimpleNamespace(**{**current.__dict__, "status": status})
            self.records[run_id] = updated
            return updated

        def get_run(self, run_id):
            return self.records[run_id]

    class FakeCodexAdapter:
        def detect(self):
            return SimpleNamespace(cli_installed=True)

        def prepare(self, record, source_relative, *, known_agents):
            source = record.workspace / source_relative
            self._active_arm = (source / "arm.txt").read_text(encoding="utf-8")
            plugin = record.workspace / "plugin"
            plugin.mkdir()
            return plugin

        def run_scenario(
            self, record, _plugin_path, scenario, *, capture_skill_telemetry=False
        ):
            calls.append(
                (scenario.scenario_id, self._active_arm, capture_skill_telemetry)
            )
            if first_attempt == "interrupted":
                raise KeyboardInterrupt("simulated abrupt interruption")
            stdout = record.state_directory / "codex-stdout.jsonl"
            stdout.write_text(
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {
                            "type": "collab_tool_call",
                            "tool": "spawn_agent",
                            "sender_thread_id": "parent",
                            "receiver_thread_ids": ["child"],
                            "status": "completed",
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            metrics = record.state_directory / "codex-metrics-0001.json"
            metrics.write_text(
                json.dumps({"resourceMetrics": [{"scopeMetrics": [{"metrics": []}]}]}),
                encoding="utf-8",
            )
            metadata = record.state_directory / "codex-metrics-capture.json"
            metadata.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "capture_contract": {
                            "capture_id": record.run_id,
                            "status": "unknown",
                            "dropped_data_points": None,
                            "stream_closed": True,
                        },
                    }
                ),
                encoding="utf-8",
            )
            return HarnessResult(
                run_id=record.run_id,
                harness="codex",
                status=ResultStatus.FAILED,
                scenario=scenario.scenario_id,
                base_revision=record.base_revision,
                observations={"exit_code": 0, "response_matches": False},
                assertions=(),
                artifacts=(str(stdout), str(metrics), str(metadata)),
                errors=("harness response did not match the expected output",),
            )

    adapter = FakeCodexAdapter()
    monkeypatch.setattr(cli, "_adapters", lambda: {"codex": adapter})
    monkeypatch.setattr(cli, "HarnessRunManager", FakeManager)
    monkeypatch.setattr(
        cli,
        "validate_source",
        lambda source, *_args, **_kwargs: SimpleNamespace(
            source_digest=("b" if Path(source).name == "baseline-source" else "c") * 64
        ),
    )
    artifact_path = tmp_path / "pilot-a.json"

    command = [
        "pilot-a-run",
        "--cases",
        str(cases),
        "--baseline-profile",
        str(baseline_profile),
        "--candidate-profile",
        str(candidate_profile),
        "--repo-root",
        str(tmp_path / "scratch"),
        "--base-revision",
        "a" * 40,
        "--canonical-revision",
        "d" * 40,
        "--state-root",
        str(state_root),
        "--owner",
        "pilot-a-test",
        "--artifact",
        str(artifact_path),
    ]
    if first_attempt == "interrupted":
        with pytest.raises(KeyboardInterrupt, match="simulated abrupt interruption"):
            cli.main(command)
        reservation = next((state_root / "pilot-a-reservations").glob("*.json"))
        assert (
            json.loads(reservation.read_text(encoding="utf-8"))["status"]
            == "in_progress"
        )
    else:
        status = cli.main(command)

    assert cli.main(command[:-1] + [str(tmp_path / "different-artifact.json")]) == 2
    assert len(calls) == (24 if first_attempt == "completed" else 1)
    assert capsys.readouterr().out

    if first_attempt == "interrupted":
        return

    reservation = next((state_root / "pilot-a-reservations").glob("*.json"))
    assert json.loads(reservation.read_text(encoding="utf-8"))["status"] == "completed"
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert status == 0
    assert len(calls) == 24
    assert calls[:4] == [
        ("schema-expand-contract-compatibility", "baseline", True),
        ("schema-expand-contract-compatibility", "candidate", True),
        ("rolling-client-column-removal", "baseline", True),
        ("rolling-client-column-removal", "candidate", True),
    ]
    assert payload["harness_invocations"] == 24
    assert payload["provider_model_calls"] == "unknown"
    assert all(row["invocation_status"] == "passed" for row in payload["invocations"])
    assert "exact_response_check" in {
        check["id"]
        for check in payload["invocations"][0]["measurement"]["completion_checks"]
    }
    assert "route_status" in payload["invocations"][0]
    assert "observed_role" not in payload["invocations"][0]
    assert (
        payload["invocations"][0]["measurement"]["delegations"][0]["observed_role"]
        == "unknown"
    )


def test_pilot_a_cli_rejects_existing_artifact_before_invocation_or_schedule_lock(
    tmp_path, monkeypatch, capsys
):
    from harness_factory import cli

    cases = _case_spec(tmp_path)
    baseline_source = tmp_path / "baseline-source"
    candidate_source = tmp_path / "candidate-source"
    baseline_source.mkdir()
    candidate_source.mkdir()
    baseline_profile = _profile_descriptor(tmp_path, "baseline", baseline_source)
    candidate_profile = _profile_descriptor(tmp_path, "candidate", candidate_source)
    artifact = tmp_path / "already-exists.json"
    artifact.write_text("preserve", encoding="utf-8")
    state_root = tmp_path / "state"
    adapter_calls = []

    class FakeManager:
        def __init__(self, *_args):
            pass

        def resolve_revision(self, revision):
            return revision

    class FakeAdapter:
        def detect(self):
            return SimpleNamespace(cli_installed=True)

        def prepare(self, *_args, **_kwargs):
            raise AssertionError("artifact rejection must precede adapter preparation")

        def run_scenario(self, *_args, **_kwargs):
            adapter_calls.append("invoked")
            raise AssertionError("artifact rejection must precede Codex invocation")

    adapter = FakeAdapter()
    monkeypatch.setattr(cli, "_adapters", lambda: {"codex": adapter})
    monkeypatch.setattr(cli, "HarnessRunManager", FakeManager)
    monkeypatch.setattr(
        cli,
        "validate_source",
        lambda *_args, **_kwargs: SimpleNamespace(source_digest="b" * 64),
    )

    status = cli.main(
        [
            "pilot-a-run",
            "--cases",
            str(cases),
            "--baseline-profile",
            str(baseline_profile),
            "--candidate-profile",
            str(candidate_profile),
            "--repo-root",
            str(tmp_path / "scratch"),
            "--base-revision",
            "a" * 40,
            "--state-root",
            str(state_root),
            "--owner",
            "pilot-a-test",
            "--artifact",
            str(artifact),
        ]
    )

    assert status == 2
    assert artifact.read_text(encoding="utf-8") == "preserve"
    assert adapter_calls == []
    assert not (state_root / "pilot-a-reservations").exists()
    assert "already in use" in capsys.readouterr().out


def test_pilot_a_schedule_runner_connects_profiles_budget_and_native_evidence(
    tmp_path,
):
    from harness_factory.evaluation import EvaluationProfile
    from harness_factory.pilot_a_observation import PilotABudget
    from harness_factory.pilot_a_runtime import run_pilot_a_experiment

    case_spec_path = _case_spec(tmp_path)
    baseline = EvaluationProfile("baseline", tmp_path / "baseline")
    candidate = EvaluationProfile("candidate", tmp_path / "candidate")
    profiles = {"baseline": baseline, "candidate": candidate}
    digests = {"baseline": "b" * 64, "candidate": "c" * 64}
    calls: list[tuple[str, str, str]] = []
    artifacts = tmp_path / "captured"
    artifacts.mkdir()

    def invoke(pair, case, profile):
        calls.append((pair.case_id, pair.arm, profile.profile_id))
        return _harness_result(
            artifacts,
            run_id=f"{len(calls):032x}",
            case_id=pair.case_id,
            include_skill=case["polarity"] == "positive",
        )

    result = run_pilot_a_experiment(
        case_spec_path,
        state_root=tmp_path / "state",
        profiles=profiles,
        profile_digests=digests,
        budget=PilotABudget(),
        canonical_revision="a" * 40,
        invoke=invoke,
    )

    assert len(calls) == 24
    assert calls[:4] == [
        ("schema-expand-contract-compatibility", "baseline", "baseline"),
        ("schema-expand-contract-compatibility", "candidate", "candidate"),
        ("rolling-client-column-removal", "baseline", "baseline"),
        ("rolling-client-column-removal", "candidate", "candidate"),
    ]
    assert result["status"] == "completed"
    assert result["budget"]["max_harness_invocations"] == 24
    assert result["provider_model_calls"] == "unknown"
    assert len(result["invocations"]) == 24
    first = result["invocations"][0]
    assert first["case_id"] == "schema-expand-contract-compatibility"
    assert first["arm"] == "baseline"
    assert first["run_id"] == f"{1:032x}"
    assert first["invocation_status"] == "passed"
    assert first["adapter_status"] == "failed"
    assert first["route_status"] == "correct"
    assert first["measurement"]["provider_model_calls"] == "unknown"
    assert first["measurement"]["actual_route"] == "migration-readiness"
    assert first["measurement"]["raw_reference"]
    assert first["artifact_digests"]
    assert first["measurement"]["delegations"][0]["observed_role"] == "unknown"
    negative = next(
        item
        for item in result["invocations"]
        if item["case_id"] == "explain-select-query"
    )
    assert negative["route_status"] == "unknown"
    assert negative["measurement"]["actual_trigger"] == "unknown"


def test_pilot_a_rejects_partial_budget_before_reservation_then_allows_full_budget(
    tmp_path,
):
    from harness_factory.errors import HarnessFactoryError
    from harness_factory.evaluation import EvaluationProfile
    from harness_factory.pilot_a_observation import PilotABudget
    from harness_factory.pilot_a_runtime import run_pilot_a_experiment

    case_spec_path = _case_spec(tmp_path)
    state_root = tmp_path / "state"
    profiles = {
        arm: EvaluationProfile(arm, tmp_path / arm) for arm in ("baseline", "candidate")
    }
    profile_digests = {"baseline": "b" * 64, "candidate": "c" * 64}
    captured = tmp_path / "captured"
    captured.mkdir()
    calls = []

    def invoke(pair, case, _profile):
        calls.append((pair.case_id, pair.arm))
        return _harness_result(
            captured,
            run_id=f"{len(calls):032x}",
            case_id=pair.case_id,
            include_skill=case["polarity"] == "positive",
        )

    with pytest.raises(HarnessFactoryError, match="requires a budget for all 24"):
        run_pilot_a_experiment(
            case_spec_path,
            state_root=state_root,
            profiles=profiles,
            profile_digests=profile_digests,
            budget=PilotABudget(max_harness_invocations=23),
            canonical_revision="a" * 40,
            invoke=invoke,
        )

    assert calls == []
    assert not (state_root / "pilot-a-reservations").exists()
    result = run_pilot_a_experiment(
        case_spec_path,
        state_root=state_root,
        profiles=profiles,
        profile_digests=profile_digests,
        budget=PilotABudget(max_harness_invocations=24),
        canonical_revision="a" * 40,
        invoke=invoke,
    )
    assert result["status"] == "completed"
    assert len(calls) == 24
    assert result["cases_sha256"] == (
        "8581b32eb37d09114dd63ba4da0a0ed4c57f1847a5920aaf195735528af84df7"
    )

    formatted_spec = json.loads(case_spec_path.read_text(encoding="utf-8"))
    case_spec_path.write_text(
        json.dumps(formatted_spec, ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(HarnessFactoryError, match="identity is already reserved"):
        run_pilot_a_experiment(
            case_spec_path,
            state_root=state_root,
            profiles=profiles,
            profile_digests=profile_digests,
            budget=PilotABudget(max_harness_invocations=24),
            canonical_revision="a" * 40,
            invoke=invoke,
        )
    assert len(calls) == 24


def test_pilot_a_route_mismatch_is_reported_but_does_not_stop_the_schedule(tmp_path):
    from harness_factory.evaluation import EvaluationProfile
    from harness_factory.pilot_a_observation import PilotABudget
    from harness_factory.pilot_a_runtime import run_pilot_a_experiment

    case_spec_path = _case_spec(tmp_path)
    profiles = {
        arm: EvaluationProfile(arm, tmp_path / arm) for arm in ("baseline", "candidate")
    }
    captured = tmp_path / "captured"
    captured.mkdir()
    calls: list[str] = []

    def invoke(pair, _case, _profile):
        calls.append(pair.case_id)
        return _harness_result(
            captured,
            run_id=f"{len(calls):032x}",
            case_id=pair.case_id,
            include_skill=pair.case_id == "explain-select-query",
        )

    result = run_pilot_a_experiment(
        case_spec_path,
        state_root=tmp_path / "state",
        profiles=profiles,
        profile_digests={"baseline": "b" * 64, "candidate": "c" * 64},
        budget=PilotABudget(),
        canonical_revision="a" * 40,
        invoke=invoke,
    )

    false_positive = next(
        item
        for item in result["invocations"]
        if item["case_id"] == "explain-select-query"
    )
    assert result["status"] == "completed"
    assert len(calls) == 24
    assert false_positive["route_status"] == "incorrect"
    assert false_positive["measurement"]["actual_trigger"] is True


def test_pilot_a_runner_stops_on_execution_failure_without_retry(tmp_path):
    from harness_factory.evaluation import EvaluationProfile
    from harness_factory.models import HarnessResult, ResultStatus
    from harness_factory.pilot_a_observation import PilotABudget
    from harness_factory.pilot_a_runtime import run_pilot_a_experiment

    case_spec_path = _case_spec(tmp_path)
    profiles = {
        arm: EvaluationProfile(arm, tmp_path / arm) for arm in ("baseline", "candidate")
    }
    captured = tmp_path / "captured"
    captured.mkdir()
    calls: list[str] = []

    def invoke(pair, _case, _profile):
        calls.append(pair.case_id)
        if len(calls) == 2:
            return HarnessResult(
                run_id="2" * 32,
                harness="codex",
                status=ResultStatus.FAILED,
                scenario=pair.case_id,
                base_revision="a" * 40,
                observations={"exit_code": 7, "response_matches": False},
                assertions=(),
                errors=("harness exited with code 7",),
            )
        return _harness_result(
            captured, run_id="1" * 32, case_id=pair.case_id, include_skill=True
        )

    result = run_pilot_a_experiment(
        case_spec_path,
        state_root=tmp_path / "state",
        profiles=profiles,
        profile_digests={"baseline": "b" * 64, "candidate": "c" * 64},
        budget=PilotABudget(),
        canonical_revision="a" * 40,
        invoke=invoke,
    )

    assert result["status"] == "failed"
    assert len(calls) == 2
    assert len(result["invocations"]) == 2
    assert result["invocations"][-1]["invocation_status"] == "failed"
    assert result["invocations"][-1]["retry_count"] == 0


def test_codex_jsonl_reader_rejects_duplicate_keys_and_non_object_lines(tmp_path):
    from harness_factory.pilot_a_runtime import read_codex_stdout_evidence

    evidence = tmp_path / "codex-stdout.jsonl"
    evidence.write_text('{"type":"a","type":"b"}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="line 1"):
        read_codex_stdout_evidence(evidence)

    evidence.write_text('["not", "an", "event"]\n', encoding="utf-8")
    with pytest.raises(TypeError, match="mapping"):
        read_codex_stdout_evidence(evidence)


def _case_spec(tmp_path: Path) -> Path:
    path = tmp_path / "cases.json"
    canonical_spec = ROOT / "experiments/routing/specs/migration-readiness.json"
    path.write_bytes(canonical_spec.read_bytes())
    return path


def _profile_descriptor(tmp_path: Path, profile_id: str, source: Path) -> Path:
    path = tmp_path / f"{profile_id}.profile.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_id": profile_id,
                "source_path": str(source),
                "source_mode": "external",
                "metadata": {},
            }
        ),
        encoding="utf-8",
    )
    return path


def _harness_result(
    directory: Path,
    *,
    run_id: str,
    case_id: str,
    include_skill: bool,
):
    from harness_factory.models import HarnessResult, ResultStatus

    run_directory = directory / run_id
    run_directory.mkdir()
    stdout = run_directory / "codex-stdout.jsonl"
    stdout.write_text(
        json.dumps(
            {
                "type": "item.completed",
                "item": {
                    "type": "collab_tool_call",
                    "tool": "spawn_agent",
                    "sender_thread_id": "thread-parent",
                    "receiver_thread_ids": ["thread-child"],
                    "prompt": "The role text is evidence-free metadata.",
                    "status": "completed",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    metric = run_directory / "codex-metrics-0001.json"
    skill_metrics = (
        [
            {
                "name": "codex.skill.injected",
                "sum": {
                    "dataPoints": [
                        {
                            "attributes": [
                                {
                                    "key": "skill",
                                    "value": {"stringValue": "migration-readiness"},
                                },
                                {
                                    "key": "invoke_type",
                                    "value": {"stringValue": "explicit"},
                                },
                            ]
                        }
                    ]
                },
            }
        ]
        if include_skill
        else []
    )
    metric.write_text(
        json.dumps(
            {"resourceMetrics": [{"scopeMetrics": [{"metrics": skill_metrics}]}]}
        ),
        encoding="utf-8",
    )
    metadata = run_directory / "codex-metrics-capture.json"
    metadata.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "capture_id": run_id,
                "capture_contract": {
                    "capture_id": run_id,
                    "status": "unknown",
                    "dropped_data_points": None,
                    "stream_closed": True,
                },
            }
        ),
        encoding="utf-8",
    )
    return HarnessResult(
        run_id=run_id,
        harness="codex",
        status=ResultStatus.FAILED,
        scenario=case_id,
        base_revision="a" * 40,
        observations={"exit_code": 0, "response_matches": False},
        assertions=(
            {"name": "process-exit-zero", "passed": True},
            {"name": "expected-output", "passed": False},
        ),
        artifacts=(str(stdout), str(metric), str(metadata)),
        errors=("harness response did not match the expected output",),
    )
