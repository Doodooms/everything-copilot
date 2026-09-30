"""Single-process Pilot A execution and Codex evidence normalization."""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from expertise.validator import load_json_no_duplicate_keys

from .errors import HarnessFactoryError
from .evaluation import EvaluationProfile
from .models import HarnessResult, ResultStatus
from .pilot_a_codex_capture import read_codex_metrics_evidence
from .pilot_a_observation import (
    CaseArm,
    PilotABudget,
    PilotACaseObservation,
    SkillTelemetryCaptureContract,
    execute_pilot_a_schedule,
    make_pilot_a_schedule,
    observe_codex_events,
    pilot_a_metrics,
)

_CASE_SPEC_ID = "migration-readiness"
_CANONICAL_CASES_SHA256 = (
    "8581b32eb37d09114dd63ba4da0a0ed4c57f1847a5920aaf195735528af84df7"
)
_EXPECTED_OUTPUT_MISMATCH = "harness response did not match the expected output"
_REVISION_PATTERN = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def read_codex_stdout_evidence(path: Path) -> list[dict[str, Any]]:
    """Decode JSONL events one line at a time, rejecting unsafe or malformed rows."""

    evidence_path = Path(path)
    if evidence_path.is_symlink() or not evidence_path.is_file():
        raise HarnessFactoryError("Codex stdout evidence path must be a regular file")
    events: list[dict[str, Any]] = []
    try:
        with evidence_path.open("rb") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                try:
                    value = load_json_no_duplicate_keys(line)
                except (ValueError, TypeError, UnicodeDecodeError) as exc:
                    raise ValueError(
                        f"Codex stdout JSONL line {line_number} is invalid"
                    ) from exc
                if not isinstance(value, Mapping):
                    raise TypeError(
                        f"Codex stdout JSONL line {line_number} must be a mapping"
                    )
                events.append(dict(value))
    except OSError as exc:
        raise HarnessFactoryError("Codex stdout evidence could not be read") from exc
    return events


def run_pilot_a_experiment(
    case_spec_path: Path,
    *,
    state_root: Path,
    profiles: Mapping[str, EvaluationProfile],
    profile_digests: Mapping[str, str],
    budget: PilotABudget,
    canonical_revision: str,
    invoke: Callable[[CaseArm, Mapping[str, Any], EvaluationProfile], HarnessResult],
) -> dict[str, Any]:
    """Run the frozen 12 x 2 schedule and retain per-case native evidence."""

    spec_bytes = Path(case_spec_path).read_bytes()
    spec = _load_case_spec(spec_bytes)
    cases_sha256 = spec["metadata"]["cases_sha256"]
    if not isinstance(budget, PilotABudget):
        raise TypeError("Pilot A requires a validated PilotABudget")
    if not isinstance(profiles, Mapping) or set(profiles) != {
        "baseline",
        "candidate",
    }:
        raise ValueError("Pilot A requires baseline and candidate profiles")
    if any(not isinstance(profile, EvaluationProfile) for profile in profiles.values()):
        raise TypeError("Pilot A profiles must be validated EvaluationProfile values")
    if not isinstance(profile_digests, Mapping) or set(profile_digests) != {
        "baseline",
        "candidate",
    }:
        raise ValueError("Pilot A requires a digest for each profile arm")
    if any(
        not isinstance(digest, str) or _DIGEST_PATTERN.fullmatch(digest) is None
        for digest in profile_digests.values()
    ):
        raise ValueError("Pilot A profile digests must be SHA-256 hex values")
    if canonical_revision != "unknown" and (
        not isinstance(canonical_revision, str)
        or _REVISION_PATTERN.fullmatch(canonical_revision) is None
    ):
        raise ValueError("canonical_revision must be a full Git SHA or unknown")
    if not callable(invoke):
        raise TypeError("invoke must be callable")

    cases = {case["id"]: case for case in spec["cases"]}
    case_ids = tuple(case["id"] for case in spec["cases"])
    schedule = make_pilot_a_schedule(case_ids)
    if budget.max_harness_invocations != len(schedule):
        raise HarnessFactoryError(
            f"Pilot A requires a budget for all {len(schedule)} scheduled invocations"
        )

    reservation_path = _reserve_schedule(
        state_root,
        cases_sha256=cases_sha256,
        profile_digests=profile_digests,
        canonical_revision=canonical_revision,
    )

    invocation_rows: list[dict[str, Any]] = []

    def invoke_pair(pair: CaseArm) -> Mapping[str, Any]:
        case = cases[pair.case_id]
        profile = profiles[pair.arm]
        try:
            result = invoke(pair, case, profile)
            if not isinstance(result, HarnessResult):
                raise TypeError("Codex runner must return a HarnessResult")
            if result.harness != "codex" or result.scenario != pair.case_id:
                raise ValueError("Codex result identity does not match its case")
            row = _observe_result(
                result,
                case=case,
                pair=pair,
                profile=profile,
                profile_digest=profile_digests[pair.arm],
                canonical_revision=canonical_revision,
            )
        except Exception as exc:  # noqa: BLE001 - preserve one failure and stop
            error = f"{type(exc).__name__}: {exc}"
            invocation_rows.append(
                {
                    "invocation_number": len(invocation_rows) + 1,
                    "case_id": pair.case_id,
                    "arm": pair.arm,
                    "profile_id": profile.profile_id,
                    "package_digest": profile_digests[pair.arm],
                    "expected_specialist_roles": list(
                        case.get("expected_specialist_roles", [])
                    ),
                    "run_id": "unknown",
                    "adapter_status": "unknown",
                    "invocation_status": "failed",
                    "route_status": "unknown",
                    "error": error,
                    "retry_count": 0,
                    "measurement": "unknown",
                    "raw_artifact_references": [],
                    "artifact_digests": [],
                }
            )
            return {"status": "failed", "error": error}

        invocation_rows.append(row)
        return {
            "status": row["invocation_status"],
            "provider_model_calls": None,
            "model_turns": result.model_turns,
            "error": row["error"],
        }

    schedule_result = execute_pilot_a_schedule(
        schedule,
        case_ids=case_ids,
        budget=budget,
        invoke=invoke_pair,
    )
    _set_reservation_status(
        reservation_path,
        "completed" if schedule_result.status == "completed" else "stopped",
    )
    for row, scheduled in zip(invocation_rows, schedule_result.invocations):
        row["invocation_number"] = scheduled.invocation_number
        row["retry_count"] = scheduled.retry_count

    return {
        "schema_version": 1,
        "experiment_id": spec["id"],
        "harness": "codex",
        "backend": "codex_exec",
        "status": schedule_result.status,
        "harness_invocations": schedule_result.harness_invocations,
        "provider_model_calls": schedule_result.provider_model_calls,
        "model_turns": schedule_result.model_turns,
        "canonical_revision": canonical_revision,
        "cases_sha256": cases_sha256,
        "budget": budget.as_dict(),
        "schedule": schedule_result.as_dict(),
        "profiles": {
            arm: {
                **profile.as_dict(),
                "package_digest": profile_digests[arm],
            }
            for arm, profile in profiles.items()
        },
        "route_policy": {
            "route_mismatches_stop_schedule": False,
            "unknown_route_stops_schedule": False,
            "invocation_or_evidence_errors_stop_schedule": True,
            "exact_response_matching": "not_applicable",
            "actual_agent_role": "unknown unless provided by native Codex evidence",
        },
        "invocations": invocation_rows,
        "metrics": pilot_a_metrics(
            [
                row["measurement"]
                for row in invocation_rows
                if isinstance(row["measurement"], Mapping)
            ]
        ),
        "stop_reason": schedule_result.stop_reason or "unknown",
    }


def _reserve_schedule(
    state_root: Path,
    *,
    cases_sha256: str,
    profile_digests: Mapping[str, str],
    canonical_revision: str,
) -> Path:
    identity = {
        "cases_sha256": cases_sha256,
        "profile_digests": {
            arm: profile_digests[arm] for arm in ("baseline", "candidate")
        },
        "canonical_revision": canonical_revision,
    }
    identity_bytes = json.dumps(
        identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    reservation_id = hashlib.sha256(identity_bytes).hexdigest()
    state_path = Path(state_root)
    if state_path.is_symlink():
        raise HarnessFactoryError("Pilot A state root must not be a symlink")
    try:
        state_path.mkdir(parents=True, exist_ok=True)
        reservation_directory = state_path / "pilot-a-reservations"
        if reservation_directory.is_symlink():
            raise HarnessFactoryError(
                "Pilot A reservation directory must not be a symlink"
            )
        reservation_directory.mkdir(mode=0o700, exist_ok=True)
    except OSError as exc:
        raise HarnessFactoryError(
            "Pilot A state reservation could not be prepared"
        ) from exc
    reservation_path = reservation_directory / f"{reservation_id}.json"
    payload = {
        "schema_version": 1,
        "reservation_id": reservation_id,
        "identity": identity,
        "status": "in_progress",
    }
    try:
        descriptor = os.open(
            reservation_path,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            0o600,
        )
    except FileExistsError as exc:
        raise HarnessFactoryError(
            "Pilot A experiment identity is already reserved; relaunch is blocked"
        ) from exc
    except OSError as exc:
        raise HarnessFactoryError(
            "Pilot A schedule reservation could not be created"
        ) from exc
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
    except OSError as exc:
        raise HarnessFactoryError(
            "Pilot A schedule reservation could not be recorded"
        ) from exc
    return reservation_path


def _set_reservation_status(path: Path, status: str) -> None:
    try:
        payload = load_json_no_duplicate_keys(path.read_bytes())
        if not isinstance(payload, dict):
            raise TypeError("reservation is not an object")
        payload["status"] = status
        path.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError, TypeError, UnicodeDecodeError) as exc:
        raise HarnessFactoryError(
            "Pilot A reservation state could not be updated"
        ) from exc


def _load_case_spec(raw: bytes) -> dict[str, Any]:
    try:
        value = load_json_no_duplicate_keys(raw)
    except (ValueError, TypeError, UnicodeDecodeError) as exc:
        raise HarnessFactoryError("Pilot A case specification is invalid JSON") from exc
    if not isinstance(value, dict) or set(value) != {
        "schema_version",
        "id",
        "skill",
        "description",
        "cases",
        "metadata",
    }:
        raise HarnessFactoryError("Pilot A case specification fields are invalid")
    if (
        type(value["schema_version"]) is not int
        or value["schema_version"] != 1
        or value["id"] != _CASE_SPEC_ID
        or value["skill"] != _CASE_SPEC_ID
        or not isinstance(value["cases"], list)
        or not isinstance(value["metadata"], Mapping)
    ):
        raise HarnessFactoryError("Pilot A case specification identity is invalid")
    if len(value["cases"]) != 12:
        raise HarnessFactoryError("Pilot A case specification must contain 12 cases")
    case_ids: list[str] = []
    for case in value["cases"]:
        if not isinstance(case, Mapping):
            raise HarnessFactoryError("Pilot A case must be an object")
        case_id = case.get("id")
        polarity = case.get("polarity")
        if (
            not isinstance(case_id, str)
            or not case_id.strip()
            or polarity not in {"positive", "negative"}
            or not isinstance(case.get("prompt"), str)
            or not case["prompt"].strip()
        ):
            raise HarnessFactoryError("Pilot A case identity or prompt is invalid")
        if polarity == "positive" and case.get("expected_route") != _CASE_SPEC_ID:
            raise HarnessFactoryError(
                "positive Pilot A cases require the canonical route"
            )
        if polarity == "negative" and "expected_route" in case:
            raise HarnessFactoryError(
                "negative Pilot A cases must not require the route"
            )
        roles = case.get("expected_specialist_roles", [])
        if (
            not isinstance(roles, list)
            or any(not isinstance(role, str) or not role.strip() for role in roles)
            or len(roles) != len(set(roles))
        ):
            raise HarnessFactoryError("Pilot A expected specialist roles are invalid")
        case_ids.append(case_id)
    if len(set(case_ids)) != len(case_ids):
        raise HarnessFactoryError("Pilot A case IDs must be unique")
    if (
        sum(case["polarity"] == "positive" for case in value["cases"]) != 6
        or sum(case["polarity"] == "negative" for case in value["cases"]) != 6
    ):
        raise HarnessFactoryError(
            "Pilot A case specification requires six cases per polarity"
        )
    metadata_digest = value["metadata"].get("cases_sha256")
    computed_digest = hashlib.sha256(
        json.dumps(
            value["cases"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    if metadata_digest != computed_digest:
        raise HarnessFactoryError("Pilot A canonical case digest does not match")
    if computed_digest != _CANONICAL_CASES_SHA256:
        raise HarnessFactoryError(
            "Pilot A case corpus differs from the accepted canonical digest"
        )
    return value


def _observe_result(
    result: HarnessResult,
    *,
    case: Mapping[str, Any],
    pair: CaseArm,
    profile: EvaluationProfile,
    profile_digest: str,
    canonical_revision: str,
) -> dict[str, Any]:
    references = list(result.artifacts)
    paths = [Path(reference) for reference in references]
    evidence_failures: list[str] = []
    artifact_digests: list[dict[str, str]] = []
    for reference, path in zip(references, paths):
        try:
            artifact_digests.append({"path": reference, "sha256": _file_sha256(path)})
        except HarnessFactoryError as exc:
            evidence_failures.append(str(exc))
    stdout_paths = [path for path in paths if path.name == "codex-stdout.jsonl"]
    metric_paths = [
        path
        for path in paths
        if path.name.startswith("codex-metrics-")
        and path.name.endswith(".json")
        and path.name != "codex-metrics-capture.json"
    ]
    metadata_paths = [
        path for path in paths if path.name == "codex-metrics-capture.json"
    ]
    events: list[Mapping[str, Any]] = []
    if len(stdout_paths) != 1:
        evidence_failures.append(
            "Codex JSONL stdout evidence reference is missing or ambiguous"
        )
    else:
        try:
            events.extend(read_codex_stdout_evidence(stdout_paths[0]))
        except (HarnessFactoryError, ValueError) as exc:
            evidence_failures.append(str(exc))
    try:
        events.extend(read_codex_metrics_evidence(metric_paths))
    except HarnessFactoryError as exc:
        evidence_failures.append(str(exc))
    capture_contract = None
    if len(metadata_paths) > 1:
        evidence_failures.append("Codex capture metadata reference is ambiguous")
    elif metadata_paths:
        try:
            capture_contract = _load_capture_contract(metadata_paths[0])
        except HarnessFactoryError as exc:
            evidence_failures.append(str(exc))

    expected_route = case.get("expected_route")
    expected_trigger = case["polarity"] == "positive"
    observed = observe_codex_events(
        events,
        requested_route=_CASE_SPEC_ID,
        capture_contract=capture_contract,
    )
    route_status = _route_status(
        expected_trigger,
        observed.actual_trigger,
        expected_route,
        observed.actual_route,
    )
    exit_code = result.observations.get("exit_code")
    invocation_status, error = pilot_a_invocation_status(result, evidence_failures)
    completion = "completed" if invocation_status == "passed" else invocation_status
    record = PilotACaseObservation(
        run_id=result.run_id,
        case_id=pair.case_id,
        arm=pair.arm,
        expected_trigger=expected_trigger,
        actual_trigger=observed.actual_trigger,
        expected_route=expected_route,
        actual_route=observed.actual_route,
        completion=completion,
        invocation_count=1,
        provider_model_calls=None,
        model_turns=result.model_turns,
        tokens=result.token_usage,
        latency_ms=result.latency_ms,
        delegations=observed.delegations,
        skill_injections=observed.skill_injections,
        validation_failures=tuple(evidence_failures),
        package_digest=profile_digest,
        canonical_revision=canonical_revision,
        raw_reference=",".join(references) if references else "unknown",
        completion_checks=(
            {
                "id": "codex_process_exit",
                "status": "pass" if exit_code == 0 else "unknown",
            },
            {"id": "exact_response_check", "status": "not_applicable"},
            {
                "id": "codex_evidence_parse",
                "status": "fail" if evidence_failures else "pass",
            },
        ),
        capture_complete=observed.capture_complete,
    ).as_dict()
    return {
        "invocation_number": 0,
        "case_id": pair.case_id,
        "arm": pair.arm,
        "profile_id": profile.profile_id,
        "package_digest": profile_digest,
        "expected_specialist_roles": list(case.get("expected_specialist_roles", [])),
        "run_id": result.run_id,
        "adapter_status": result.status.value,
        "invocation_status": invocation_status,
        "route_status": route_status,
        "error": error or "unknown",
        "adapter_errors": list(result.errors),
        "retry_count": 0,
        "measurement": record,
        "raw_artifact_references": references,
        "artifact_digests": artifact_digests,
    }


def pilot_a_invocation_status(
    result: HarnessResult, evidence_failures: Sequence[str]
) -> tuple[str, str | None]:
    if evidence_failures:
        return "failed", "; ".join(evidence_failures)
    exit_code = result.observations.get("exit_code")
    if result.status is ResultStatus.BLOCKED:
        return "blocked", "; ".join(result.errors) or "Codex invocation blocked"
    if exit_code != 0:
        return "failed", "; ".join(
            result.errors
        ) or "Codex process did not exit successfully"
    if result.status is ResultStatus.PASSED and not result.errors:
        return "passed", None
    if (
        result.status is ResultStatus.FAILED
        and result.observations.get("response_matches") is False
        and result.errors == (_EXPECTED_OUTPUT_MISMATCH,)
    ):
        return "passed", None
    return "failed", "; ".join(result.errors) or "Codex invocation result is invalid"


def _route_status(
    expected_trigger: bool,
    actual_trigger: bool | None,
    expected_route: str | None,
    actual_route: str | None,
) -> str:
    if actual_trigger is None:
        return "unknown"
    if actual_trigger is not expected_trigger:
        return "incorrect"
    if expected_trigger:
        if actual_route is None:
            return "unknown"
        if actual_route != expected_route:
            return "incorrect"
    return "correct"


def _load_capture_contract(path: Path) -> SkillTelemetryCaptureContract | None:
    if path.is_symlink() or not path.is_file():
        raise HarnessFactoryError("Codex capture metadata path must be a regular file")
    try:
        value = load_json_no_duplicate_keys(path.read_bytes())
    except (OSError, ValueError, TypeError, UnicodeDecodeError) as exc:
        raise HarnessFactoryError("Codex capture metadata is invalid") from exc
    contract = value.get("capture_contract") if isinstance(value, Mapping) else None
    if not isinstance(contract, Mapping):
        raise HarnessFactoryError("Codex capture metadata has no contract")
    if contract.get("status") == "unknown":
        return None
    try:
        return SkillTelemetryCaptureContract(
            capture_id=contract["capture_id"],
            status=contract["status"],
            dropped_data_points=contract["dropped_data_points"],
            stream_closed=contract["stream_closed"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise HarnessFactoryError("Codex capture contract fields are invalid") from exc


def _file_sha256(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise HarnessFactoryError("Pilot A artifact must be a regular file")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(64 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
