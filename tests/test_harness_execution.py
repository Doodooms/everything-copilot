from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_execution_request_represents_one_task_attempt():
    from harness_factory.execution import ExecutionRequest

    request = ExecutionRequest(
        task_id="TASK-1",
        attempt_id="attempt-1",
        input="Return a structured result.",
        working_directory=Path.cwd(),
    )

    assert request.task_id == "TASK-1"
    assert request.attempt_id == "attempt-1"
