import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_execution_request_represents_one_task_attempt():
    from harness_factory.execution import ExecutionConstraints, ExecutionRequest

    request = ExecutionRequest(
        task_id="TASK-1",
        attempt_id="attempt-1",
        input="Return a structured result.",
        working_directory=Path.cwd(),
        constraints=ExecutionConstraints(timeout_seconds=45),
    )

    assert request.task_id == "TASK-1"
    assert request.attempt_id == "attempt-1"
    assert request.constraints.timeout_seconds == 45


def test_execution_result_keeps_task_attempt_and_backend_identity():
    from harness_factory.execution import ExecutionOutcome, ExecutionResult

    result = ExecutionResult(
        outcome=ExecutionOutcome.SUCCEEDED,
        task_id="TASK-1",
        attempt_id="attempt-2",
        harness_id="codex",
        backend_id="codex_exec",
        result={"answer": 42},
    )

    assert result.task_id == "TASK-1"
    assert result.attempt_id == "attempt-2"
    assert result.harness_id == "codex"
    assert result.backend_id == "codex_exec"
    assert result.external_session_id is None
    assert result.artifact_refs == ()


def test_execution_result_supports_external_session_and_separate_failure_dimensions():
    from harness_factory.execution import (
        ExecutionFailure,
        ExecutionOutcome,
        ExecutionResult,
        FailureCause,
        RetryDecision,
    )

    result = ExecutionResult(
        outcome=ExecutionOutcome.FAILED,
        task_id="TASK-1",
        attempt_id="attempt-3",
        harness_id="codex",
        backend_id="codex_app_server",
        external_session_id="session-123",
        failure=ExecutionFailure(
            cause=FailureCause.LOST_BACKEND,
            retry=RetryDecision.RETRY,
            message="The process connection was lost.",
        ),
    )

    assert result.external_session_id == "session-123"
    assert result.failure.cause is FailureCause.LOST_BACKEND
    assert result.failure.retry is RetryDecision.RETRY


def test_backend_capabilities_distinguish_supported_unsupported_and_unknown():
    from harness_factory.execution import (
        EXECUTION_CAPABILITY_NAMES,
        BackendCapabilities,
    )
    from harness_factory.models import CapabilityObservation, CapabilityState

    observations = {
        name: CapabilityObservation(CapabilityState.UNKNOWN)
        for name in EXECUTION_CAPABILITY_NAMES
    }
    observations["headless"] = CapabilityObservation(CapabilityState.SUPPORTED)
    observations["parallel"] = CapabilityObservation(CapabilityState.UNSUPPORTED)
    capabilities = BackendCapabilities("codex_exec", observations)

    assert capabilities.satisfies(("headless",))
    assert not capabilities.satisfies(("parallel",))
    assert not capabilities.satisfies(("workspace_write",))


def test_codex_exec_uses_stdin_and_normalizes_structured_output(tmp_path):
    from harness_factory.adapters import CodexExecBackend
    from harness_factory.execution import ExecutionOutcome

    adapter = Mock()
    adapter.detect.return_value = _installed_codex_capabilities()
    backend = CodexExecBackend(adapter=adapter)
    request = _execution_request(tmp_path)
    completed = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=_codex_execution_events(
            {
                "task_id": request.task_id,
                "attempt_id": request.attempt_id,
                "result_json": json.dumps({"answer": 42}),
            }
        ),
        stderr="",
    )

    def run_with_schema(command, **kwargs):
        schema_path = Path(command[command.index("--output-schema") + 1])
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        assert schema["properties"]["task_id"]["enum"] == [request.task_id]
        assert schema["properties"]["attempt_id"]["enum"] == [request.attempt_id]
        assert schema["properties"]["result_json"]["type"] == "string"
        assert schema["additionalProperties"] is False
        return completed

    with patch(
        "harness_factory.adapters.subprocess.run", side_effect=run_with_schema
    ) as run:
        result = backend.execute(request)

    command = run.call_args.args[0]
    assert command[:2] == ["/usr/bin/codex", "exec"]
    assert command[-1] == "-"
    assert "--output-schema" in command
    assert (
        "--sandbox" in command
        and command[command.index("--sandbox") + 1] == "read-only"
    )
    assert run.call_args.kwargs["input"] == request.input
    assert result.outcome is ExecutionOutcome.SUCCEEDED
    assert result.result == {"answer": 42}
    assert result.task_id == request.task_id
    assert result.attempt_id == request.attempt_id
    assert result.backend_id == "codex_exec"
    assert result.harness_id == "codex"
    assert result.external_session_id is None


def test_codex_exec_classifies_process_protocol_semantic_and_timeout_failures(tmp_path):
    from harness_factory.adapters import CodexExecBackend
    from harness_factory.execution import (
        ExecutionOutcome,
        FailureCause,
    )

    adapter = Mock()
    adapter.detect.return_value = _installed_codex_capabilities()
    backend = CodexExecBackend(adapter=adapter)
    request = _execution_request(tmp_path)
    correct_payload = {
        "task_id": request.task_id,
        "attempt_id": request.attempt_id,
        "result_json": json.dumps("ok"),
    }

    with patch(
        "harness_factory.adapters.subprocess.run",
        return_value=subprocess.CompletedProcess(
            [], 2, _codex_execution_events(correct_payload), "error"
        ),
    ):
        process_failure = backend.execute(request)
    assert process_failure.outcome is ExecutionOutcome.FAILED
    assert process_failure.failure.cause is FailureCause.PROCESS_FAILURE

    with patch(
        "harness_factory.adapters.subprocess.run",
        return_value=subprocess.CompletedProcess([], 0, "not-json\n", ""),
    ):
        protocol_failure = backend.execute(request)
    assert protocol_failure.failure.cause is FailureCause.PROTOCOL_FAILURE

    for identity_field in ("task_id", "attempt_id"):
        mismatched_payload = dict(correct_payload, **{identity_field: "OTHER-ID"})
        with patch(
            "harness_factory.adapters.subprocess.run",
            return_value=subprocess.CompletedProcess(
                [], 0, _codex_execution_events(mismatched_payload), ""
            ),
        ):
            semantic_failure = backend.execute(request)
        assert semantic_failure.failure.cause is FailureCause.SEMANTIC_FAILURE

    with patch(
        "harness_factory.adapters.subprocess.run",
        side_effect=subprocess.TimeoutExpired("codex exec", 10),
    ):
        timeout = backend.execute(request)
    assert timeout.failure.cause is FailureCause.TIMEOUT


def test_unknown_workspace_write_requirement_blocks_before_invocation(tmp_path):
    from harness_factory.adapters import CodexExecBackend
    from harness_factory.execution import ExecutionConstraints, ExecutionOutcome

    adapter = Mock()
    adapter.detect.return_value = _installed_codex_capabilities()
    backend = CodexExecBackend(adapter=adapter)
    request = _execution_request(
        tmp_path,
        constraints=ExecutionConstraints(read_only=False),
    )

    with patch("harness_factory.adapters.subprocess.run") as run:
        result = backend.execute(request)

    assert result.outcome is ExecutionOutcome.BLOCKED
    assert result.failure.cause.value == "capability_unverified"
    adapter.detect.assert_not_called()
    run.assert_not_called()


def _execution_request(tmp_path, **overrides):
    from harness_factory.execution import ExecutionRequest

    values = {
        "task_id": "TASK-1",
        "attempt_id": "attempt-1",
        "input": "Return the answer as structured output.",
        "working_directory": tmp_path,
    }
    values.update(overrides)
    return ExecutionRequest(**values)


def _installed_codex_capabilities():
    from harness_factory.models import (
        CAPABILITY_NAMES,
        CapabilityObservation,
        CapabilityState,
        HarnessCapabilities,
    )

    observations = {
        name: CapabilityObservation(CapabilityState.SUPPORTED, ("fixture help",))
        for name in CAPABILITY_NAMES
    }
    observations["sandboxing"] = CapabilityObservation(
        CapabilityState.SUPPORTED,
        ("--sandbox", "read-only"),
    )
    return HarnessCapabilities(
        harness="codex",
        cli_installed=True,
        executable="/usr/bin/codex",
        version="fixture",
        capabilities=observations,
        observed_options=(
            "--cd",
            "--ignore-user-config",
            "--sandbox",
            "--ephemeral",
            "--json",
            "--output-schema",
        ),
    )


def _codex_execution_events(payload):
    return (
        "\n".join(
            json.dumps(event)
            for event in (
                {"type": "thread.started", "thread_id": "native-thread"},
                {
                    "type": "item.completed",
                    "item": {"type": "agent_message", "text": json.dumps(payload)},
                },
                {"type": "turn.completed"},
            )
        )
        + "\n"
    )
