from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Any

from .adapters import CodexHarnessAdapter, CopilotHarnessAdapter, HarnessAdapter
from .errors import CapabilityUnavailableError, HarnessFactoryError
from .evaluation import (
    ALLOWED_COPILOT_REASONS,
    CrossHarnessValidationContext,
    EvaluationProfile,
    RunBudget,
    SystemicEvaluationError,
    compare_run_artifacts,
    load_profile,
    make_preflight_record,
    run_suite,
    save_preflight_record,
    validate_run_target,
)
from .models import (
    COPILOT_MIN_AI_CREDITS,
    HARNESS_NAMES,
    CrossHarnessRequest,
    HarnessScenario,
    Purpose,
    ResultStatus,
    RunMode,
    RunStatus,
)
from .runs import HarnessRunManager
from .suites import load_suite
from .validation import validate_source


def _adapters() -> dict[str, HarnessAdapter]:
    return {
        "copilot": CopilotHarnessAdapter(),
        "codex": CodexHarnessAdapter(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="harness-factory")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser(
        "detect", help="detect installed harnesses and evidenced capabilities"
    )

    validate = commands.add_parser(
        "validate", help="statically validate one plugin or Expertise Pack projection"
    )
    validate.add_argument("--target", choices=HARNESS_NAMES, required=True)
    validate.add_argument("--source-root", type=Path, required=True)

    prepare = commands.add_parser(
        "prepare", help="create an isolated development or validation worktree"
    )
    _add_run_arguments(prepare)
    prepare.add_argument("--origin-harness", choices=HARNESS_NAMES)
    prepare.add_argument("--purpose", choices=[purpose.value for purpose in Purpose])
    prepare.add_argument("--expected-output")
    prepare.add_argument("--budget")
    prepare.add_argument("--validator-id")
    prepare.add_argument("--development-owner-id")

    smoke = commands.add_parser(
        "smoke", help="run one bounded read-only Level 1 harness invocation"
    )
    smoke.add_argument("--harness", choices=HARNESS_NAMES, required=True)
    smoke.add_argument("--repo-root", type=Path, required=True)
    smoke.add_argument("--state-root", type=Path, required=True)
    smoke.add_argument("--base-revision", required=True)
    smoke.add_argument("--source", type=Path, required=True)
    smoke.add_argument("--owner", required=True)
    smoke.add_argument(
        "--copilot-reason",
        choices=sorted(ALLOWED_COPILOT_REASONS),
    )
    smoke.add_argument("--timeout-seconds", type=int, default=90)
    smoke.add_argument(
        "--max-ai-credits",
        type=int,
        default=COPILOT_MIN_AI_CREDITS,
    )

    runs = commands.add_parser("runs", help="list persisted harness run records")
    runs.add_argument("--repo-root", type=Path, required=True)
    runs.add_argument("--state-root", type=Path, required=True)

    begin = commands.add_parser(
        "begin", help="mark a prepared external harness run active"
    )
    _add_record_arguments(begin)

    finish = commands.add_parser("finish", help="record an external harness run result")
    _add_record_arguments(finish)
    finish.add_argument(
        "--status",
        choices=(RunStatus.COMPLETED.value, RunStatus.FAILED.value),
        required=True,
    )

    cleanup = commands.add_parser(
        "cleanup", help="explicitly remove a clean, factory-owned run worktree"
    )
    _add_record_arguments(cleanup)

    suite_validate = commands.add_parser(
        "suite-validate", help="locally validate a harness-neutral evaluation suite"
    )
    suite_validate.add_argument("--suite", type=Path, required=True)

    suite_run = commands.add_parser(
        "suite-run", help="run a suite against one supplied plugin/profile variant"
    )
    suite_run.add_argument("--suite", type=Path, required=True)
    suite_run.add_argument("--profile", type=Path, required=True)
    suite_run.add_argument("--harness", choices=HARNESS_NAMES, required=True)
    suite_run.add_argument(
        "--copilot-reason",
        choices=sorted(ALLOWED_COPILOT_REASONS),
    )
    suite_run.add_argument("--repo-root", type=Path, required=True)
    suite_run.add_argument("--state-root", type=Path, required=True)
    suite_run.add_argument("--owner", required=True)
    suite_run.add_argument("--artifact", type=Path, required=True)
    suite_run.add_argument("--preflight-artifact", type=Path, required=True)
    suite_run.add_argument("--run-id")
    suite_run.add_argument("--timeout-seconds", type=int, default=90)
    suite_run.add_argument("--max-ai-credits", type=int, default=COPILOT_MIN_AI_CREDITS)
    suite_run.add_argument("--max-runs", type=int, required=True)
    suite_run.add_argument("--max-model-calls", type=int, required=True)
    suite_run.add_argument("--max-tokens-if-known", type=int, required=True)
    suite_run.add_argument("--max-failures-before-stop", type=int, required=True)

    compare = commands.add_parser(
        "compare", help="compare two durable runs over identical scenario contracts"
    )
    compare.add_argument("--left", type=Path, required=True)
    compare.add_argument("--right", type=Path, required=True)
    compare.add_argument("--artifact", type=Path)
    return parser


def _add_run_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--harness", choices=HARNESS_NAMES, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--base-revision", required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument(
        "--mode", choices=[mode.value for mode in RunMode], required=True
    )


def _add_record_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--owner", required=True)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    adapters = _adapters()

    try:
        if args.command == "detect":
            _emit(
                {
                    "status": "detected",
                    "harnesses": {
                        name: adapters[name].detect().as_dict()
                        for name in HARNESS_NAMES
                    },
                }
            )
            return 0

        if args.command == "validate":
            result = validate_source(args.source_root, args.target)
            _emit(result.as_dict())
            return 0

        if args.command == "suite-validate":
            suite = load_suite(args.suite)
            _emit(
                {
                    "status": "valid",
                    "suite_id": suite.suite_id,
                    "base_revision": suite.base_revision,
                    "scenario_count": len(suite.scenarios),
                    "scenarios": [
                        {"id": item.scenario_id, "category": item.category}
                        for item in suite.scenarios
                    ],
                }
            )
            return 0

        if args.command == "suite-run":
            return _suite_run(args, adapters[args.harness])

        if args.command == "compare":
            comparison = compare_run_artifacts(args.left, args.right)
            if args.artifact is not None:
                _write_json_artifact(args.artifact, comparison)
            _emit(comparison)
            return 0

        if args.command == "prepare":
            return _prepare(args, adapters[args.harness])

        if args.command == "smoke":
            validate_run_target(args.harness, args.copilot_reason)
            return _smoke(args, adapters[args.harness])

        manager = HarnessRunManager(args.repo_root, args.state_root)
        if args.command == "runs":
            _emit(
                {
                    "status": "listed",
                    "runs": [record.as_dict() for record in manager.list_runs()],
                }
            )
            return 0

        if args.command == "begin":
            record = manager.transition(
                args.run_id,
                owner=args.owner,
                status=RunStatus.RUNNING,
            )
            _emit({"status": "running", "run": record.as_dict()})
            return 0

        if args.command == "finish":
            record = manager.transition(
                args.run_id,
                owner=args.owner,
                status=RunStatus(args.status),
            )
            _emit({"status": record.status.value, "run": record.as_dict()})
            return 0

        if args.command == "cleanup":
            record = manager.cleanup(args.run_id, owner=args.owner)
            _emit({"status": "cleaned", "run": record.as_dict()})
            return 0

        raise HarnessFactoryError(f"unsupported command: {args.command}")
    except (HarnessFactoryError, OSError, ValueError) as exc:
        _emit(
            {
                "status": "error",
                "error": type(exc).__name__,
                "message": str(exc),
            }
        )
        return 2


def _prepare(args: argparse.Namespace, adapter: HarnessAdapter) -> int:
    manager = HarnessRunManager(args.repo_root, args.state_root)
    mode = RunMode(args.mode)
    resolved_revision = manager.resolve_revision(args.base_revision)
    request = _cross_harness_request(args, resolved_revision)
    if request is not None:
        validator_id = getattr(args, "validator_id", None)
        development_owner_id = getattr(args, "development_owner_id", None)
        if validator_id != args.owner:
            raise HarnessFactoryError(
                "cross-harness validator-id must match the run owner"
            )
        CrossHarnessValidationContext(
            request=request,
            validator_id=validator_id,
            development_owner_id=development_owner_id,
        )
    elif getattr(args, "validator_id", None) or getattr(
        args, "development_owner_id", None
    ):
        raise HarnessFactoryError(
            "validator and development-owner identities require a cross-harness request"
        )
    capabilities = adapter.detect()
    if not capabilities.cli_installed:
        raise CapabilityUnavailableError(
            f"{adapter.name} CLI is not installed; no run workspace was created"
        )
    record = manager.create_run(
        harness=adapter.name,
        base_revision=resolved_revision,
        mode=mode,
        owner=args.owner,
        run_id=request.run_id if request is not None else None,
        cross_harness_request=request,
    )
    try:
        plugin_path = adapter.prepare(record, args.source)
        command = (
            adapter.development_command(record, plugin_path)
            if mode is RunMode.DEVELOPMENT
            else ()
        )
    except (HarnessFactoryError, OSError, ValueError) as exc:
        failed = manager.transition(
            record.run_id,
            owner=record.owner,
            status=RunStatus.FAILED,
        )
        _emit(
            {
                "status": "failed",
                "error": type(exc).__name__,
                "message": str(exc),
                "run": failed.as_dict(),
            }
        )
        return 3

    _emit(
        {
            "status": "prepared",
            "run": record.as_dict(),
            "plugin_path": str(plugin_path),
            "development_command": list(command) if command else "not applicable",
            "capabilities": capabilities.as_dict(),
        }
    )
    return 0


def _suite_run(args: argparse.Namespace, adapter: HarnessAdapter) -> int:
    suite = load_suite(args.suite)
    profile = load_profile(args.profile)
    validate_run_target(args.harness, args.copilot_reason)
    budget = RunBudget(
        max_runs=args.max_runs,
        max_model_calls=args.max_model_calls,
        max_tokens_if_known=args.max_tokens_if_known,
        max_failures_before_stop=args.max_failures_before_stop,
    )
    run_id = args.run_id or uuid.uuid4().hex
    if type(args.timeout_seconds) is not int or args.timeout_seconds <= 0:
        raise HarnessFactoryError("timeout-seconds must be positive")
    if type(args.max_ai_credits) is not int or args.max_ai_credits <= 0:
        raise HarnessFactoryError("max-ai-credits must be positive")

    if profile.source_mode == "external":
        validate_source(profile.source_path, args.harness)
    if args.preflight_artifact == args.artifact:
        raise HarnessFactoryError("preflight and run artifact paths must differ")
    preflight = make_preflight_record(
        suite,
        profile,
        profile_descriptor=args.profile,
        run_id=run_id,
        harness=args.harness,
        copilot_reason=args.copilot_reason,
        budget=budget,
    )
    save_preflight_record(args.preflight_artifact, preflight)
    capabilities = adapter.detect()
    if not capabilities.cli_installed:
        raise CapabilityUnavailableError(
            f"{args.harness} CLI is unavailable; no evaluation run was launched"
        )

    manager = HarnessRunManager(args.repo_root, args.state_root)
    resolved_revision = manager.resolve_revision(suite.base_revision)
    if resolved_revision != suite.base_revision:
        raise HarnessFactoryError(
            "suite base_revision does not resolve to its pinned SHA"
        )

    def invoke(scenario: Any, selected_profile: EvaluationProfile):
        try:
            record = manager.create_run(
                harness=args.harness,
                base_revision=suite.base_revision,
                mode=RunMode.VALIDATION,
                owner=args.owner,
            )
        except (HarnessFactoryError, OSError, ValueError) as exc:
            raise SystemicEvaluationError(
                f"isolated harness workspace could not be created: {exc}"
            ) from exc
        if selected_profile.source_mode == "base_revision":
            source_relative = selected_profile.source_path
        else:
            source_relative = Path(".evaluation-profile-input")
        profile_input = record.workspace / source_relative
        try:
            if selected_profile.source_mode == "external":
                if profile_input.exists() or profile_input.is_symlink():
                    raise HarnessFactoryError(
                        "evaluation profile input path already exists"
                    )
                shutil.copytree(
                    selected_profile.source_path,
                    profile_input,
                    symlinks=True,
                )
            plugin_path = adapter.prepare(record, source_relative)
            running = manager.transition(
                record.run_id,
                owner=record.owner,
                status=RunStatus.RUNNING,
            )
            result = adapter.run_scenario(
                running,
                plugin_path,
                HarnessScenario(
                    scenario_id=scenario.scenario_id,
                    prompt=scenario.prompt,
                    expected_output=scenario.expected_behavior,
                    timeout_seconds=args.timeout_seconds,
                    max_ai_credits=args.max_ai_credits,
                    required_observations=scenario.required,
                    forbidden_observations=scenario.forbidden,
                    optional_observations=scenario.optional,
                ),
            )
            final_status = (
                RunStatus.COMPLETED
                if result.status is ResultStatus.PASSED
                else RunStatus.FAILED
            )
            manager.transition(
                record.run_id,
                owner=record.owner,
                status=final_status,
            )
            return result
        except (HarnessFactoryError, OSError, ValueError) as exc:
            try:
                current = manager.get_run(record.run_id)
                if current.status in {RunStatus.PREPARED, RunStatus.RUNNING}:
                    manager.transition(
                        record.run_id,
                        owner=record.owner,
                        status=RunStatus.FAILED,
                    )
            except HarnessFactoryError:
                pass
            raise SystemicEvaluationError(
                f"scenario materialization, plugin loading, or routing failed: {exc}"
            ) from exc

    artifact = run_suite(
        suite,
        profile,
        harness=args.harness,
        copilot_reason=args.copilot_reason,
        model="unknown",
        budget=budget,
        invoke=invoke,
        artifact_path=args.artifact,
        run_id=run_id,
    )
    _emit(artifact)
    return 0 if artifact["status"] == "completed" else 3


def _smoke(args: argparse.Namespace, adapter: HarnessAdapter) -> int:
    scenario = HarnessScenario(
        scenario_id="plugin-smoke",
        prompt=(
            "Reply with exactly AGENT_PLUGIN_SMOKE_OK. Do not call tools, "
            "inspect files, or make changes."
        ),
        expected_output="AGENT_PLUGIN_SMOKE_OK",
        timeout_seconds=args.timeout_seconds,
        max_ai_credits=args.max_ai_credits,
    )
    capabilities = adapter.detect()
    if not capabilities.cli_installed:
        _emit(
            {
                "status": "blocked",
                "harness": adapter.name,
                "reason": "CLI unavailable; runtime capabilities remain unknown",
                "capabilities": capabilities.as_dict(),
            }
        )
        return 3

    if adapter.name == "copilot" and scenario.max_ai_credits < COPILOT_MIN_AI_CREDITS:
        _emit(
            {
                "status": "blocked",
                "harness": adapter.name,
                "reason": (
                    "Copilot CLI requires --max-ai-credits to be at least "
                    f"{COPILOT_MIN_AI_CREDITS}"
                ),
            }
        )
        return 3

    manager = HarnessRunManager(args.repo_root, args.state_root)
    resolved_revision = manager.resolve_revision(args.base_revision)
    record = manager.create_run(
        harness=adapter.name,
        base_revision=resolved_revision,
        mode=RunMode.VALIDATION,
        owner=args.owner,
    )
    try:
        plugin_path = adapter.prepare(record, args.source)
        scenario = HarnessScenario(
            scenario_id="plugin-smoke",
            prompt=_smoke_prompt(adapter, plugin_path),
            expected_output="AGENT_PLUGIN_SMOKE_OK",
            timeout_seconds=args.timeout_seconds,
            max_ai_credits=args.max_ai_credits,
        )
        running = manager.transition(
            record.run_id,
            owner=record.owner,
            status=RunStatus.RUNNING,
        )
        result = adapter.run_scenario(running, plugin_path, scenario)
        _write_json_artifact(
            record.state_directory / "result.json",
            result.as_dict(),
        )
        final_status = (
            RunStatus.COMPLETED
            if result.status is ResultStatus.PASSED
            else RunStatus.FAILED
        )
        finished = manager.transition(
            record.run_id,
            owner=record.owner,
            status=final_status,
        )
        _emit(
            {
                "status": result.status.value,
                "run": finished.as_dict(),
                "result": result.as_dict(),
                "cleanup": (
                    "explicitly run the cleanup command after inspecting the run"
                ),
            }
        )
        return 0 if result.status is ResultStatus.PASSED else 3
    except (HarnessFactoryError, OSError, ValueError) as exc:
        current = manager.get_run(record.run_id)
        failed = (
            manager.transition(
                record.run_id,
                owner=record.owner,
                status=RunStatus.FAILED,
            )
            if current.status in {RunStatus.PREPARED, RunStatus.RUNNING}
            else current
        )
        _emit(
            {
                "status": "failed",
                "error": type(exc).__name__,
                "message": str(exc),
                "run": failed.as_dict(),
                "cleanup": (
                    "workspace was preserved; inspect the run before explicit cleanup"
                ),
            }
        )
        return 3


def _smoke_prompt(adapter: HarnessAdapter, plugin_path: Path) -> str:
    if adapter.name == "codex":
        skills = sorted((plugin_path / "skills").glob("*/SKILL.md"))
        if skills:
            return (
                f"${skills[0].parent.name} Reply with exactly "
                "AGENT_PLUGIN_SMOKE_OK. Do not call tools."
            )
    return (
        "Reply with exactly AGENT_PLUGIN_SMOKE_OK. Do not call tools, "
        "inspect files, or make changes."
    )


def _cross_harness_request(
    args: argparse.Namespace,
    resolved_revision: str,
) -> CrossHarnessRequest | None:
    origin = getattr(args, "origin_harness", None)
    if origin is None:
        return None
    if args.mode != RunMode.VALIDATION.value:
        raise HarnessFactoryError("cross-harness requests are validation-only")
    purpose_value = getattr(args, "purpose", None)
    if purpose_value is None:
        raise HarnessFactoryError("cross-harness validation requires --purpose")
    run_id = uuid.uuid4().hex
    budget = getattr(args, "budget", None)
    expected_output = getattr(args, "expected_output", None)
    return CrossHarnessRequest(
        run_id=run_id,
        requested_by=args.owner,
        target_harness=args.harness,
        purpose=Purpose(purpose_value),
        artifact_under_test=str(args.source),
        base_revision=resolved_revision,
        allowed_mutations=False,
        timeout_or_budget=budget,
        expected_output=expected_output,
        origin_harness=origin,
        call_depth=1,
    )


def _write_json_artifact(path: Path, payload: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise HarnessFactoryError(f"result artifact already exists: {path}")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".result-",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
