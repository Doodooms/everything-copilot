from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
import uuid
from collections.abc import Mapping
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
from .pilot_a_observation import PilotABudget
from .pilot_a_runtime import pilot_a_invocation_status, run_pilot_a_experiment
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
    validate.add_argument(
        "--known-agent",
        action="append",
        default=[],
        help="known agent ID (repeat for each agent available to this pack)",
    )

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
        "--known-agent",
        action="append",
        default=[],
        help="known agent ID (repeat for each agent available to this pack)",
    )
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
    suite_run.add_argument(
        "--known-agent",
        action="append",
        default=[],
        help="known agent ID (repeat for each agent available to this pack)",
    )
    suite_run.add_argument("--run-id")
    suite_run.add_argument("--timeout-seconds", type=int, default=90)
    suite_run.add_argument("--max-ai-credits", type=int, default=COPILOT_MIN_AI_CREDITS)
    suite_run.add_argument(
        "--capture-skill-telemetry",
        action="store_true",
        help="opt in to Codex skill telemetry and JSONL transcript artifacts",
    )
    suite_run.add_argument("--max-runs", type=int, required=True)
    suite_run.add_argument("--max-model-calls", type=int)
    suite_run.add_argument("--max-tokens-if-known", type=int)
    suite_run.add_argument(
        "--required-enforcement",
        action="append",
        choices=("harness_invocations", "provider_model_calls"),
        help=(
            "budget dimension that must be enforceable before execution; "
            "defaults to provider_model_calls for compatibility"
        ),
    )
    suite_run.add_argument("--max-failures-before-stop", type=int, required=True)

    pilot_a_run = commands.add_parser(
        "pilot-a-run",
        help="execute the frozen local Pilot A Codex routing schedule",
    )
    pilot_a_run.add_argument("--cases", type=Path, required=True)
    pilot_a_run.add_argument("--baseline-profile", type=Path, required=True)
    pilot_a_run.add_argument("--candidate-profile", type=Path, required=True)
    pilot_a_run.add_argument("--repo-root", type=Path, required=True)
    pilot_a_run.add_argument("--base-revision", required=True)
    pilot_a_run.add_argument("--canonical-revision", default="unknown")
    pilot_a_run.add_argument("--state-root", type=Path, required=True)
    pilot_a_run.add_argument("--owner", required=True)
    pilot_a_run.add_argument("--artifact", type=Path, required=True)
    pilot_a_run.add_argument("--max-harness-invocations", type=int, default=24)
    pilot_a_run.add_argument("--timeout-seconds", type=int, default=90)
    pilot_a_run.add_argument(
        "--known-agent",
        action="append",
        default=[],
        help="known agent ID (repeat for each agent available to these profiles)",
    )
    pilot_a_run.set_defaults(capture_skill_telemetry=True)

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
        "--known-agent",
        action="append",
        default=[],
        help="known agent ID (repeat for each agent available to this pack)",
    )
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
            result = validate_source(
                args.source_root,
                args.target,
                known_agents=frozenset(args.known_agent),
            )
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

        if args.command == "pilot-a-run":
            return _pilot_a_run(args, adapters["codex"])

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
        plugin_path = adapter.prepare(
            record,
            args.source,
            known_agents=frozenset(args.known_agent),
        )
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
    if args.capture_skill_telemetry and args.harness != "codex":
        raise HarnessFactoryError(
            "skill telemetry capture is currently supported only for Codex"
        )
    budget = RunBudget(
        max_runs=args.max_runs,
        max_model_calls=args.max_model_calls,
        max_tokens_if_known=args.max_tokens_if_known,
        max_failures_before_stop=args.max_failures_before_stop,
        required_enforcement=tuple(
            args.required_enforcement
            if args.required_enforcement is not None
            else ("provider_model_calls",)
        ),
    )
    run_id = args.run_id or uuid.uuid4().hex
    if type(args.timeout_seconds) is not int or args.timeout_seconds <= 0:
        raise HarnessFactoryError("timeout-seconds must be positive")
    if type(args.max_ai_credits) is not int or args.max_ai_credits <= 0:
        raise HarnessFactoryError("max-ai-credits must be positive")

    if profile.source_mode == "external":
        validate_source(
            profile.source_path,
            args.harness,
            known_agents=frozenset(args.known_agent),
        )
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
            plugin_path = adapter.prepare(
                record,
                source_relative,
                known_agents=frozenset(args.known_agent),
            )
            running = manager.transition(
                record.run_id,
                owner=record.owner,
                status=RunStatus.RUNNING,
            )
            result = _run_adapter_scenario(
                adapter,
                args.harness,
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
                capture_skill_telemetry=args.capture_skill_telemetry,
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


def _run_adapter_scenario(
    adapter: HarnessAdapter,
    harness: str,
    run: Any,
    plugin_path: Path,
    scenario: HarnessScenario,
    *,
    capture_skill_telemetry: bool = False,
):
    if capture_skill_telemetry and harness != "codex":
        raise HarnessFactoryError(
            "skill telemetry capture is currently supported only for Codex"
        )
    if harness == "codex":
        return adapter.run_scenario(
            run,
            plugin_path,
            scenario,
            capture_skill_telemetry=capture_skill_telemetry,
        )
    return adapter.run_scenario(run, plugin_path, scenario)


def _pilot_a_run(args: argparse.Namespace, adapter: HarnessAdapter) -> int:
    baseline = load_profile(args.baseline_profile)
    candidate = load_profile(args.candidate_profile)
    profiles = {"baseline": baseline, "candidate": candidate}
    profile_digests = {}
    for arm, profile in profiles.items():
        validation = validate_source(
            profile.source_path,
            "codex",
            known_agents=frozenset(args.known_agent),
        )
        profile_digests[arm] = validation.source_digest
    capabilities = adapter.detect()
    if not capabilities.cli_installed:
        raise CapabilityUnavailableError(
            "Codex CLI is unavailable; no Pilot A invocation was launched"
        )
    if type(args.timeout_seconds) is not int or args.timeout_seconds <= 0:
        raise HarnessFactoryError("timeout-seconds must be positive")
    budget = PilotABudget(max_harness_invocations=args.max_harness_invocations)
    if budget.max_harness_invocations != 24:
        raise HarnessFactoryError("Pilot A requires all 24 scheduled invocations")
    if args.artifact == args.cases or args.artifact in {
        args.baseline_profile,
        args.candidate_profile,
    }:
        raise HarnessFactoryError("Pilot A artifact path must differ from its inputs")
    manager = HarnessRunManager(args.repo_root, args.state_root)
    resolved_revision = manager.resolve_revision(args.base_revision)
    if resolved_revision != args.base_revision:
        raise HarnessFactoryError("Pilot A base_revision is not its pinned SHA")
    artifact_reservation = _reserve_pilot_a_artifact(args.artifact)
    invocation_started = False

    def invoke(pair: Any, case: Mapping[str, Any], profile: EvaluationProfile):
        nonlocal invocation_started
        invocation_started = True
        try:
            record = manager.create_run(
                harness="codex",
                base_revision=resolved_revision,
                mode=RunMode.VALIDATION,
                owner=args.owner,
            )
            if profile.source_mode == "base_revision":
                source_relative = profile.source_path
            else:
                source_relative = Path(".pilot-a-profile-input")
                profile_input = record.workspace / source_relative
                if profile_input.exists() or profile_input.is_symlink():
                    raise HarnessFactoryError(
                        "Pilot A profile input path already exists"
                    )
                shutil.copytree(profile.source_path, profile_input, symlinks=True)
            plugin_path = adapter.prepare(
                record,
                source_relative,
                known_agents=frozenset(args.known_agent),
            )
            running = manager.transition(
                record.run_id,
                owner=record.owner,
                status=RunStatus.RUNNING,
            )
            result = _run_adapter_scenario(
                adapter,
                "codex",
                running,
                plugin_path,
                HarnessScenario(
                    scenario_id=pair.case_id,
                    prompt=case["prompt"],
                    expected_output="__PILOT_A_RESPONSE_MATCHING_NOT_APPLICABLE__",
                    timeout_seconds=args.timeout_seconds,
                ),
                capture_skill_telemetry=True,
            )
            status, _ = pilot_a_invocation_status(result, ())
            manager.transition(
                record.run_id,
                owner=record.owner,
                status=(
                    RunStatus.COMPLETED if status == "passed" else RunStatus.FAILED
                ),
            )
            return result
        except (HarnessFactoryError, OSError, ValueError, TypeError) as exc:
            try:
                current = manager.get_run(record.run_id)
                if current.status in {RunStatus.PREPARED, RunStatus.RUNNING}:
                    manager.transition(
                        record.run_id,
                        owner=record.owner,
                        status=RunStatus.FAILED,
                    )
            except (HarnessFactoryError, UnboundLocalError):
                pass
            raise HarnessFactoryError(
                f"Pilot A Codex invocation failed: {type(exc).__name__}: {exc}"
            ) from exc

    try:
        artifact = run_pilot_a_experiment(
            args.cases,
            state_root=args.state_root,
            profiles=profiles,
            profile_digests=profile_digests,
            budget=budget,
            canonical_revision=args.canonical_revision,
            invoke=invoke,
        )
    except BaseException:
        if invocation_started:
            artifact_reservation.close()
        else:
            artifact_reservation.discard()
        raise
    artifact_reservation.write(artifact)
    _emit(artifact)
    return 0 if artifact["status"] == "completed" else 3


class _PilotAArtifactReservation:
    def __init__(self, path: Path, stream, identity: tuple[int, int]):
        self.path = path
        self.stream = stream
        self.identity = identity

    def write(self, payload: Mapping[str, Any]) -> None:
        self._write_payload(payload, close=True)

    def _write_payload(self, payload: Mapping[str, Any], *, close: bool) -> None:
        self._verify_path()
        try:
            self.stream.seek(0)
            self.stream.truncate()
            json.dump(
                payload, self.stream, ensure_ascii=False, indent=2, sort_keys=True
            )
            self.stream.write("\n")
            self.stream.flush()
            os.fsync(self.stream.fileno())
        finally:
            if close:
                self.stream.close()

    def close(self) -> None:
        if not self.stream.closed:
            self.stream.close()

    def discard(self) -> None:
        self.close()
        try:
            self._verify_path()
        except HarnessFactoryError:
            return
        self.path.unlink()

    def _verify_path(self) -> None:
        try:
            current = self.path.lstat()
        except OSError as exc:
            raise HarnessFactoryError("Pilot A result reservation disappeared") from exc
        if self.path.is_symlink() or (current.st_dev, current.st_ino) != self.identity:
            raise HarnessFactoryError("Pilot A result path changed after reservation")


def _reserve_pilot_a_artifact(path: Path) -> _PilotAArtifactReservation:
    target = Path(path)
    if target.exists() or target.is_symlink():
        raise HarnessFactoryError("Pilot A result artifact path is already in use")
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.parent.is_symlink() or not target.parent.is_dir():
            raise HarnessFactoryError(
                "Pilot A result artifact parent is not a directory"
            )
        flags = os.O_CREAT | os.O_EXCL | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(target, flags, 0o600)
        file_identity = os.fstat(descriptor)
        stream = os.fdopen(descriptor, "r+", encoding="utf-8")
        reservation = _PilotAArtifactReservation(
            target,
            stream,
            (file_identity.st_dev, file_identity.st_ino),
        )
        try:
            reservation._write_payload(
                {"status": "in_progress", "artifact": "Pilot A result reservation"},
                close=False,
            )
        except BaseException:
            reservation.discard()
            raise
        return reservation
    except FileExistsError as exc:
        raise HarnessFactoryError(
            "Pilot A result artifact path is already in use"
        ) from exc
    except OSError as exc:
        raise HarnessFactoryError(
            "Pilot A result artifact path is not writable"
        ) from exc


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
        plugin_path = adapter.prepare(
            record,
            args.source,
            known_agents=frozenset(args.known_agent),
        )
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
