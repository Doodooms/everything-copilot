from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
import tomllib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _run(tmp_path: Path):
    from harness_factory.models import RunMode, RunStatus
    from harness_factory.runs import HarnessRun

    workspace = tmp_path / "workspace"
    state = tmp_path / "state"
    workspace.mkdir()
    state.mkdir()
    run = HarnessRun(
        run_id=uuid.uuid4().hex,
        harness="codex",
        base_revision="a" * 40,
        workspace=workspace,
        state_directory=state,
        mode=RunMode.VALIDATION,
        owner="pilot-a-test",
        status=RunStatus.RUNNING,
        created_at="2026-09-30T00:00:00Z",
        updated_at="2026-09-30T00:00:00Z",
        allowed_mutations=False,
    )
    plugin = workspace / "plugin"
    plugin.mkdir()
    (plugin / "plugin.json").write_text(
        json.dumps({"name": "pilot-a-test", "version": "1.0.0"}),
        encoding="utf-8",
    )
    codex_agents = workspace / ".codex" / "agents"
    codex_agents.mkdir(parents=True)
    (codex_agents / "existing.toml").write_text('name = "existing"\n', encoding="utf-8")
    return run, plugin


def _capabilities():
    from harness_factory.models import (
        CAPABILITY_NAMES,
        CapabilityObservation,
        CapabilityState,
        HarnessCapabilities,
    )

    options = (
        "--cd",
        "--json",
        "--ephemeral",
        "--sandbox",
        "--ignore-user-config",
    )
    return HarnessCapabilities(
        harness="codex",
        cli_installed=True,
        executable="/usr/bin/codex",
        version="codex-cli 0.158.0",
        capabilities={
            name: CapabilityObservation(
                CapabilityState.SUPPORTED,
                ("read-only",) if name == "sandboxing" else (),
            )
            for name in CAPABILITY_NAMES
        },
        observed_options=options,
    )


def _scenario():
    from harness_factory.models import HarnessScenario

    return HarnessScenario("pilot-a-case", "Reply exactly OK", "OK")


def _otlp_payload():
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
                                                    "value": {
                                                        "stringValue": "migration-readiness"
                                                    },
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


def test_opt_in_run_persists_exact_stdout_and_local_otlp_payload(tmp_path):
    from harness_factory.adapters import CodexHarnessAdapter

    run, plugin = _run(tmp_path)
    output = (
        b'{"type":"item.completed","item":{"type":"agent_message","text":"OK"}}\n'
        b'{"type":"turn.completed","usage":{"input_tokens":4,"output_tokens":1}}\n'
    )
    posted_payloads: list[dict[str, object]] = []
    raw_bodies: list[bytes] = []

    def fake_codex(command, **kwargs):
        assert kwargs["encoding"] is None
        config = tomllib.loads(
            (run.workspace / ".codex" / "config.toml").read_text(encoding="utf-8")
        )
        exporter = config["otel"]["metrics_exporter"]["otlp-http"]
        assert set(config["otel"]) == {"metrics_exporter"}
        assert exporter["protocol"] == "json"
        assert exporter["endpoint"].startswith("http://127.0.0.1:")
        assert "127.0.0.1" in exporter["endpoint"]
        assert exporter["headers"]["Authorization"].startswith("Bearer ")
        payload = _otlp_payload()
        body = json.dumps(payload, indent=2).encode("utf-8")
        request = urllib.request.Request(
            exporter["endpoint"],
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": exporter["headers"]["Authorization"],
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=2) as response:
            assert response.status == 200
        posted_payloads.append(payload)
        raw_bodies.append(body)
        return subprocess.CompletedProcess(command, 0, output, b"")

    adapter = CodexHarnessAdapter()
    with (
        patch.object(adapter, "detect", return_value=_capabilities()),
        patch("harness_factory.adapters.subprocess.run", side_effect=fake_codex),
    ):
        result = adapter.run_scenario(
            run, plugin, _scenario(), capture_skill_telemetry=True
        )

    stdout_refs = [
        Path(item) for item in result.artifacts if item.endswith("codex-stdout.jsonl")
    ]
    metrics_refs = [
        Path(item)
        for item in result.artifacts
        if Path(item).name.startswith("codex-metrics-")
        and Path(item).name != "codex-metrics-capture.json"
    ]
    assert len(stdout_refs) == 1
    assert stdout_refs[0].read_bytes() == output
    assert len(metrics_refs) == 1
    assert metrics_refs[0].read_bytes() == raw_bodies[0]
    assert [json.loads(path.read_bytes()) for path in metrics_refs] == posted_payloads
    from harness_factory.pilot_a_codex_capture import read_codex_metrics_evidence

    assert read_codex_metrics_evidence(tuple(metrics_refs)) == posted_payloads
    assert result.status.value == "passed"
    assert result.token_usage == {"input_tokens": 4, "output_tokens": 1}
    capture_state = json.loads(
        (run.state_directory / "codex-metrics-capture.json").read_text(encoding="utf-8")
    )
    assert capture_state["capture_contract"] == {
        "capture_id": capture_state["capture_id"],
        "status": "unknown",
        "dropped_data_points": None,
        "stream_closed": True,
    }
    assert capture_state["accepted_payloads"] == 1
    assert capture_state["raw_references"] == [str(metrics_refs[0])]
    assert str(run.state_directory / "codex-metrics-capture.json") in result.artifacts
    assert (run.workspace / ".codex" / "agents" / "existing.toml").read_text(
        encoding="utf-8"
    ) == 'name = "existing"\n'
    assert not (run.workspace / ".codex" / "config.toml").exists()


def test_metrics_receiver_rejects_bad_path_auth_and_payload(tmp_path):
    from harness_factory.pilot_a_codex_capture import PilotACodexMetricsCapture

    state = tmp_path / "state"
    state.mkdir()
    with PilotACodexMetricsCapture(state) as capture:
        valid_body = json.dumps(_otlp_payload()).encode("utf-8")

        def request(path, body, *, token=None, content_type="application/json"):
            headers = {"Content-Type": content_type}
            if token is not None:
                headers["Authorization"] = f"Bearer {token}"
            req = urllib.request.Request(
                capture.endpoint.replace("/v1/metrics", path),
                data=body,
                headers=headers,
                method="POST",
            )
            try:
                urllib.request.urlopen(req, timeout=2)
            except urllib.error.HTTPError as error:
                return error.code
            return 200

        assert request("/wrong", valid_body, token=capture.token) == 404
        assert request("/v1/metrics", valid_body, token="wrong") == 401
        assert request("/v1/metrics", b"not json", token=capture.token) == 400
        assert (
            request(
                "/v1/metrics",
                b'{"resourceMetrics":{}}',
                token=capture.token,
            )
            == 400
        )
        assert (
            request(
                "/v1/metrics",
                valid_body,
                token=capture.token,
                content_type="text/plain",
            )
            == 415
        )
        assert capture.evidence_paths == ()
    rejected_state = json.loads(capture.metadata_path.read_text(encoding="utf-8"))
    assert rejected_state["capture_contract"]["status"] == "partial"
    assert rejected_state["capture_contract"]["dropped_data_points"] is None
    assert rejected_state["rejected_payloads"] == 3


def test_metrics_receiver_refuses_symlinked_evidence_path(tmp_path):
    from harness_factory.errors import HarnessFactoryError
    from harness_factory.pilot_a_codex_capture import PilotACodexMetricsCapture

    state = tmp_path / "state"
    state.mkdir()
    target = tmp_path / "target"
    target.write_text("keep", encoding="utf-8")
    (state / "codex-metrics-0001.json").symlink_to(target)
    with pytest.raises(HarnessFactoryError, match="evidence path"):
        PilotACodexMetricsCapture(state).__enter__()
    assert target.read_text(encoding="utf-8") == "keep"


def test_codex_stdout_is_not_saved_without_opt_in_capture(tmp_path):
    from harness_factory.adapters import CodexHarnessAdapter

    run, plugin = _run(tmp_path)
    output = b'{"type":"item.completed","item":{"type":"agent_message","text":"OK"}}\n'
    adapter = CodexHarnessAdapter()

    def fake_codex(command, **kwargs):
        assert kwargs["encoding"] == "utf-8"
        assert "[otel]" not in (run.workspace / ".codex" / "config.toml").read_text(
            encoding="utf-8"
        )
        return subprocess.CompletedProcess(command, 0, output, b"")

    with (
        patch.object(adapter, "detect", return_value=_capabilities()),
        patch("harness_factory.adapters.subprocess.run", side_effect=fake_codex),
    ):
        result = adapter.run_scenario(run, plugin, _scenario())

    assert not any(item.endswith("codex-stdout.jsonl") for item in result.artifacts)
    assert not (run.state_directory / "codex-stdout.jsonl").exists()
    assert not list(run.state_directory.glob("codex-metrics-*"))
    assert result.status.value == "passed"


def test_codex_timeout_saves_partial_stdout(tmp_path):
    from harness_factory.adapters import CodexHarnessAdapter

    run, plugin = _run(tmp_path)
    partial = b'{"type":"item.started"}\n'
    adapter = CodexHarnessAdapter()

    def fake_codex(command, **kwargs):
        raise subprocess.TimeoutExpired(command, 1, output=partial)

    with (
        patch.object(adapter, "detect", return_value=_capabilities()),
        patch("harness_factory.adapters.subprocess.run", side_effect=fake_codex),
    ):
        result = adapter.run_scenario(
            run, plugin, _scenario(), capture_skill_telemetry=True
        )

    stdout_refs = [
        Path(item) for item in result.artifacts if item.endswith("codex-stdout.jsonl")
    ]
    assert len(stdout_refs) == 1
    assert stdout_refs[0].read_bytes() == partial
    assert result.status.value == "failed"
