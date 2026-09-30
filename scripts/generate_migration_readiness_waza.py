from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC = REPOSITORY_ROOT / "experiments/routing/specs/migration-readiness.json"
DEFAULT_OUTPUT = REPOSITORY_ROOT / "experiments/routing/waza/migration-readiness"
EXPECTED_CASES = 12
SPECIALIST_ROLES = {
    "schema-compatibility-reviewer",
    "data-integrity-reviewer",
    "rollout-readiness-reviewer",
}


def _canonical_cases_digest(cases: list[dict[str, Any]]) -> str:
    payload = json.dumps(
        cases, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _load_spec(spec_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    try:
        document = json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"cannot read routing spec as UTF-8 JSON: {spec_path}"
        ) from exc
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise ValueError("routing spec must be a schema_version 1 object")
    if (
        document.get("id") != "migration-readiness"
        or document.get("skill") != "migration-readiness"
    ):
        raise ValueError("routing spec id and skill must be migration-readiness")
    cases = document.get("cases")
    if not isinstance(cases, list) or len(cases) != EXPECTED_CASES:
        raise ValueError(f"routing spec must contain exactly {EXPECTED_CASES} cases")
    ids: set[str] = set()
    positives = negatives = 0
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise TypeError(f"case at index {index} must be an object")
        if set(case) - {
            "id",
            "polarity",
            "prompt",
            "expected_route",
            "expected_specialist_roles",
        }:
            raise ValueError(f"case at index {index} contains unsupported fields")
        case_id = case.get("id")
        prompt = case.get("prompt")
        polarity = case.get("polarity")
        if not isinstance(case_id, str) or not case_id or case_id in ids:
            raise ValueError(f"case at index {index} has an empty or duplicate id")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(f"case {case_id} must have a non-empty prompt")
        ids.add(case_id)
        if polarity == "positive":
            positives += 1
            if case.get("expected_route") != "migration-readiness":
                raise ValueError(
                    f"positive case {case_id} must route to migration-readiness"
                )
            roles = case.get("expected_specialist_roles")
            if (
                not isinstance(roles, list)
                or not roles
                or any(
                    not isinstance(role, str) or role not in SPECIALIST_ROLES
                    for role in roles
                )
                or len(set(roles)) != len(roles)
            ):
                raise ValueError(
                    f"positive case {case_id} must declare unique Pack specialist roles"
                )
        elif polarity == "negative":
            negatives += 1
            if "expected_route" in case or "expected_specialist_roles" in case:
                raise ValueError(
                    f"negative case {case_id} must not invent destination or role expectations"
                )
        else:
            raise ValueError(f"case {case_id} polarity must be positive or negative")
    if positives != 6 or negatives != 6:
        raise ValueError(
            "routing spec must contain exactly six positive and six negative cases"
        )

    digest = _canonical_cases_digest(cases)
    metadata = document.get("metadata")
    if not isinstance(metadata, dict) or metadata.get("cases_sha256") != digest:
        raise ValueError(
            "routing spec metadata cases_sha256 does not match canonical cases"
        )
    return document, cases, digest


def _yaml_bytes(value: dict[str, Any], *, digest: str) -> bytes:
    content = yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=1000)
    header = f"# GENERATED FROM experiments/routing/specs/migration-readiness.json\n# cases-sha256: {digest}\n"
    return (header + content).encode("utf-8")


def generate_waza(
    spec_path: Path = DEFAULT_SPEC, output_dir: Path = DEFAULT_OUTPUT
) -> dict[str, Any]:
    document, cases, digest = _load_spec(spec_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    tasks_dir = output_dir / "tasks"
    tasks_dir.mkdir(exist_ok=True)

    eval_payload = {
        "name": "migration-readiness-static-stage-0",
        "description": "Generated Waza view of the frozen Pilot A migration-readiness routing corpus; no model evaluation is implied.",
        "skill": document["skill"],
        "version": "1.0",
        "config": {
            "trials_per_task": 1,
            "timeout_seconds": 600,
            "parallel": False,
            "inject_skill_body": False,
        },
        "metrics": [
            {
                "name": "routing_decision",
                "weight": 1.0,
                "threshold": 1.0,
                "description": "Compare skill invocation with each task's should_trigger expectation. This generated static oracle is not a runtime result.",
            }
        ],
        "graders": [],
        "tasks": ["tasks/*.yaml"],
    }
    (output_dir / "eval.yaml").write_bytes(_yaml_bytes(eval_payload, digest=digest))

    expected_names: set[str] = set()
    for case in cases:
        case_id = case["id"]
        expected_names.add(f"{case_id}.yaml")
        polarity = case["polarity"]
        task_payload = {
            "id": case_id,
            "name": f"{case_id}: {case['prompt']}",
            "description": f"Frozen {polarity} routing case for migration-readiness.",
            "tags": [
                "pilot-a",
                polarity,
                f"source-case:{case_id}",
                "family:migration-readiness-routing",
                f"cases-sha256:{digest}",
                *(
                    [f"expected-route:{case['expected_route']}"]
                    if "expected_route" in case
                    else []
                ),
                *(
                    [
                        f"expected-specialist-role:{role}"
                        for role in case["expected_specialist_roles"]
                    ]
                    if "expected_specialist_roles" in case
                    else []
                ),
            ],
            "inputs": {"prompt": case["prompt"]},
            "expected": {"should_trigger": polarity == "positive"},
        }
        (tasks_dir / f"{case_id}.yaml").write_bytes(
            _yaml_bytes(task_payload, digest=digest)
        )

    for path in tasks_dir.glob("*.yaml"):
        if path.name not in expected_names:
            path.unlink()

    generated_files = sorted(path for path in output_dir.rglob("*") if path.is_file())
    return {
        "case_count": len(cases),
        "cases_sha256": digest,
        "generated_file_sha256": {
            path.relative_to(output_dir).as_posix(): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in generated_files
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Waza files from the canonical migration-readiness corpus."
    )
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = generate_waza(args.spec, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
