from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import yaml


FAMILIES = {
    "authoring-contract": {
        "description": "Skill authoring semantics, ontology, contract, canonical topology, and provenance.",
        "hard_gates": ["package_validity", "provenance"],
        "judge_dimensions": ["ontology clarity", "semantic contract and boundaries", "canonical topology and provenance"],
    },
    "support-file-discipline": {
        "description": "Consumption of assets and references without inventing or front-loading unused support files.",
        "hard_gates": ["package_validity", "self_containment", "provenance"],
        "judge_dimensions": ["self-contained support-file discipline"],
    },
    "review-and-checklist": {
        "description": "Point-of-need references, user review, unresolved choices, and final checklist behavior.",
        "hard_gates": ["package_validity", "provenance"],
        "judge_dimensions": ["structural validation and user-review evidence"],
    },
    "scripts-validation": {
        "description": "Self-contained scripts, executable validation, and repair after validation failures.",
        "hard_gates": ["package_validity", "self_containment"],
        "judge_dimensions": ["executable workflow", "structural validation and user-review evidence"],
    },
    "repair-recovery": {
        "description": "Malformed or stale package repair and validation recovery without weakening invariants.",
        "hard_gates": ["package_validity", "self_containment", "provenance"],
        "judge_dimensions": ["failure/security/verification coverage"],
    },
    "routing-near-miss": {
        "description": "Correct rejection and routing of requests owned by neighboring primitives.",
        "hard_gates": ["routing_correctness"],
        "judge_dimensions": ["semantic contract and boundaries"],
    },
    "downstream-guidance": {
        "description": "Guidance quality for downstream project implementation, acceptance, failure handling, and verification.",
        "hard_gates": ["package_validity", "self_containment", "provenance"],
        "judge_dimensions": ["downstream implementation utility", "failure/security/verification coverage"],
    },
}

FAMILY_PROBES = {
    "support-file-discipline": "Exercise asset consumption and support-file discipline: use assets, references, and scripts only at the point of need, keep them self-contained, and do not claim frozen support files were optimized.",
    "review-and-checklist": "Exercise point-of-need references and user-review behavior: expose the resulting package, unresolved choices, and final checklist evidence before treating the package as ready.",
    "scripts-validation": "Exercise scripts self-containment and executable validation/repair: run package-local checks, recover from a failed validation, and preserve the canonical scaffold.",
    "repair-recovery": "Exercise malformed/stale package repair and validation recovery: identify structural drift, repair it without weakening hard gates, and re-run deterministic validation.",
}


JUDGE_RUBRIC = """Judge the generated skill package against the requested skill or application.
Score 0-4 for each dimension: ontology clarity, semantic contract and boundaries,
canonical topology and provenance, executable workflow, self-contained support-file
discipline, structural validation and user-review evidence, downstream implementation
utility, and failure/security/verification coverage. For application tasks, downstream
utility means that another agent could use the produced skill to build a coherent
project with explicit requirements, acceptance criteria, failure handling, and
verification gates; judge the skill's guidance, not an imagined implementation.
Penalize invented architecture, vague discovery text, missing provenance, unsafe or
unverifiable actions, external workspace imports, unnecessary tables, duplicated
guidance, and treating an unreviewed draft as complete. Reject near-miss requests
that belong to another skill. Return JSON with keys score (0-32), hard_pass (boolean),
failures (array), and rationale (string)."""


def task_payload(
    task_id: str,
    prompt: str,
    tags: list[str],
    files: list[str],
    *,
    family: str,
    support_files: list[str],
    should_trigger: bool = True,
) -> dict:
    family_spec = FAMILIES[family]
    return {
        "id": task_id,
        "name": f"{task_id}: {prompt}",
        "description": (
            f"{family_spec['description']} {prompt} "
            "DO NOT USE FOR: agents, prompts, MCP servers, hooks, benchmark optimization, "
            "or general application implementation."
        ),
        "tags": tags + [f"family:{family}"],
        "inputs": {"prompt": prompt, "files": [{"path": path} for path in files]},
        "expected": {"should_trigger": should_trigger},
    }


def oracle_metadata(
    task_id: str,
    *,
    family: str,
    files: list[str],
    support_files: list[str],
    should_trigger: bool,
) -> dict:
    family_spec = FAMILIES[family]
    return {
        "task_id": task_id,
        "family": family,
        "should_trigger": should_trigger,
        "required_paths": files,
        "required_support_files": support_files,
        "provenance_path": ".github/skills/create-skill/references/original-spec.md",
        "support_files_optimized": False,
        "hard_gates": family_spec["hard_gates"],
        "judge_dimensions": family_spec["judge_dimensions"],
    }


def skill_prompt(name: str) -> str:
    return (
        f"Authoring, repairing, restructuring, reviewing, and validating a production-ready skill named {name}. "
        "Create or update deterministic VS Code skill packages from a clear specification. "
        "This includes authoring, repairing, restructuring, reviewing, or validating a skill and its support files. "
        "Define its exact purpose and boundaries, "
        "include concrete acceptance and rejection cases, preserve the canonical inline workflow "
        "and grouped ACCEPT/REJECT architecture, keep provenance, and include only support files "
        "that the workflow truly consumes. Do not create agents, prompts, MCP servers, or hooks; "
        "do not perform general application implementation or benchmark optimization. Validate the "
        "package and report unresolved risks."
    )


def app_prompt(app: dict) -> str:
    return (
        f"Authoring, repairing, restructuring, reviewing, and validating a production-ready skill that guides implementation of a {app['name']}. "
        "Create or update deterministic VS Code skill packages from a clear specification. "
        "This includes authoring, repairing, restructuring, reviewing, or validating a skill and its support files. "
        f"The skill must turn this request into an executable, testable workflow: {app['constraints']} "
        "Define the domain ontology, semantic boundaries, acceptance criteria, failure handling, security and verification gates, and enough downstream guidance for another agent to implement the project coherently. "
        "Use the canonical inline grouped-list architecture, preserve source provenance, and reject requests to create agents, prompts, MCP servers, hooks, general application implementations, or benchmark optimizations."
    )


def validate_manifest(manifest: dict) -> None:
    missing = sorted(set(FAMILIES) - set(manifest.get("families", {})))
    if missing:
        raise ValueError(f"manifest is missing benchmark families: {', '.join(missing)}")
    applications = {app["id"] for app in manifest.get("applications", [])}
    split_apps = {
        split: set(config.get("applications", []))
        for split, config in manifest.get("splits", {}).items()
    }
    unknown = sorted(set().union(*split_apps.values()) - applications)
    if unknown:
        raise ValueError(f"manifest references unknown applications: {', '.join(unknown)}")
    train_and_holdout = split_apps.get("train", set()) & split_apps.get("holdout", set())
    if train_and_holdout:
        raise ValueError(f"holdout applications leak from train: {', '.join(sorted(train_and_holdout))}")


def write_eval(root: Path, split: str, task_count: int) -> None:
    payload = {
        "name": f"create-skill-{split}",
        "description": f"Frozen adversarial {split} benchmark for create-skill.",
        "skill": "create-skill",
        "version": "1.0",
        "config": {
            "trials_per_task": 1,
            "timeout_seconds": 600,
            "parallel": False,
            "executor": "copilot-sdk",
            "model": "gpt-5.6-luna",
            "inject_skill_body": False,
        },
        "metrics": [
            {"name": "llm_quality", "weight": 0.8, "threshold": 0.75, "description": JUDGE_RUBRIC},
            {"name": "efficiency", "weight": 0.2, "threshold": 0.5, "description": "Stay within the task timeout and avoid unnecessary actions."},
        ],
        "graders": [
            {"type": "prompt", "name": "llm-quality", "config": {"rubric": JUDGE_RUBRIC}},
            {"type": "behavior", "name": "bounded-actions", "config": {"max_tokens": 6000}},
        ],
        "tasks": ["tasks/*.yaml"],
    }
    (root / split / "eval.yaml").write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-skill", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    root = args.output
    if root.exists():
        raise SystemExit(f"refusing to overwrite benchmark: {root}")
    root.mkdir(parents=True)
    shutil.copy2(args.manifest, root / "benchmark_manifest.json")
    shutil.copy2(args.source_skill / "SKILL.md", root / "SKILL.md")
    support = root / ".github" / "skills" / "create-skill"
    shutil.copytree(args.source_skill, support, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    support_files = sorted(
        path.relative_to(support).as_posix()
        for path in support.rglob("*")
        if path.is_file() and path.name != "SKILL.md"
    )
    package_files = ["SKILL.md", ".github/skills/create-skill/SKILL.md"] + [
        f".github/skills/create-skill/{path}" for path in support_files
    ]
    seen: set[str] = set()
    for split in ("train", "selection", "holdout"):
        split_root = root / split
        (split_root / "tasks").mkdir(parents=True)
        split_support = split_root / ".github" / "skills" / "create-skill"
        shutil.copy2(args.source_skill / "SKILL.md", split_root / "SKILL.md")
        shutil.copytree(args.source_skill, split_support, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        files = package_files
        adapter_tasks = {}
        selected = manifest["splits"][split]
        names = list(dict.fromkeys(manifest["skills"] if selected.get("all_skills") else selected.get("skills", [])))
        for name in names:
            task_id = f"skill-{name}"
            prompt = skill_prompt(name)
            (split_root / "tasks" / f"{task_id}.yaml").write_text(
                yaml.safe_dump(task_payload(task_id, prompt, ["skill-creation", "adversarial", split], files, family="authoring-contract", support_files=support_files), sort_keys=False),
                encoding="utf-8",
            )
            adapter_tasks[task_id] = oracle_metadata(task_id, family="authoring-contract", files=files, support_files=support_files, should_trigger=True)
            seen.add(task_id)
        for app in manifest["applications"]:
            if app["id"] not in selected.get("applications", []):
                continue
            task_id = f"app-{app['id']}"
            (split_root / "tasks" / f"{task_id}.yaml").write_text(
                yaml.safe_dump(task_payload(task_id, app_prompt(app), ["application", "llm-judge", split], files, family="downstream-guidance", support_files=support_files), sort_keys=False),
                encoding="utf-8",
            )
            adapter_tasks[task_id] = oracle_metadata(task_id, family="downstream-guidance", files=files, support_files=support_files, should_trigger=True)
            seen.add(task_id)
        for family, probe in FAMILY_PROBES.items():
            task_id = f"probe-{family}"
            prompt = skill_prompt("create-skill") + " " + probe
            (split_root / "tasks" / f"{task_id}.yaml").write_text(
                yaml.safe_dump(task_payload(task_id, prompt, ["probe", split], files, family=family, support_files=support_files), sort_keys=False),
                encoding="utf-8",
            )
            adapter_tasks[task_id] = oracle_metadata(task_id, family=family, files=files, support_files=support_files, should_trigger=True)
            seen.add(task_id)
        rejected = {
            "reject-agent": "Create agents for reviewers that delegate implementation work.",
            "reject-prompt": "Create prompts for release notes.",
            "reject-mcp": "Create MCP servers that expose repository search.",
            "reject-hooks": "Create hooks that run on every commit.",
            "reject-application": "Implement a general application implementation for a calendar product.",
            "reject-benchmark": "Perform benchmark optimization for create-skill and run SkillOpt experiments.",
        }
        for suffix, prompt in rejected.items():
            task_id = f"{suffix}-near-miss"
            (split_root / "tasks" / f"{task_id}.yaml").write_text(
                yaml.safe_dump(task_payload(task_id, prompt, ["near-miss", "rejection", split], files, family="routing-near-miss", support_files=support_files, should_trigger=False), sort_keys=False),
                encoding="utf-8",
            )
            adapter_tasks[task_id] = oracle_metadata(task_id, family="routing-near-miss", files=files, support_files=support_files, should_trigger=False)
            seen.add(task_id)
        (split_root / "adapter_manifest.json").write_text(
            json.dumps({"version": 1, "tasks": adapter_tasks}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        write_eval(root, split, len(list((split_root / "tasks").glob("*.yaml"))))
    (root / "README.md").write_text(
        "# create-skill benchmark\n\n"
        "This benchmark is generated from `benchmark_manifest.json`. It evaluates create-skill as a meta-skill: the primary output is a high-quality skill package, and the application tasks test whether that package would give another agent enough structure to build a coherent project.\n\n"
        "## Benchmark: what it evaluates\n\n"
        "- `skill-*` (`authoring-contract`): authoring semantics, ontology, contract, canonical grouped-list topology, and original-spec provenance.\n"
        "- `probe-support-file-discipline`, `probe-review-and-checklist`, `probe-scripts-validation`, and `probe-repair-recovery`: explicit support-file, point-of-need review, executable repair, and stale-package recovery families.\n"
        "- `app-*` (`downstream-guidance`): downstream project guidance quality for bounded application requests, including domain modeling, implementation workflow, security, failure handling, acceptance criteria, and verification gates. These tasks judge the generated skill; current adapters do not execute a second downstream project.\n"
        "- `reject-*-near-miss` (`routing-near-miss`): routing and refusal quality for requests owned by agents, prompts, MCP servers, hooks, direct application implementation, or benchmark optimization.\n"
        "- `train`: broad optimization signal covering all manifest skills plus representative applications.\n"
        "- `selection`: held-in optimization selection signal with representative skills, applications, and near misses.\n"
        "- `holdout`: unseen application domains used only for final generalization checks; it is excluded from SkillOpt configuration.\n\n"
        "Waza task files use the standard task schema. Adapter-only contract metadata is stored in each split's `adapter_manifest.json` and is executed by the local SkillOpt/Waza adapter before Waza runs: package shape, declared frozen support files, provenance, script self-containment, and routing metadata are deterministic hard gates. `support_files_optimized: false` explicitly records that SkillOpt changes only SKILL.md; assets, references, and scripts remain frozen fixtures. Near-miss result text receives a deterministic post-Waza routing gate. Application tasks judge package guidance only; downstream project execution is unavailable. Freeze this directory before optimization.\n",
        encoding="utf-8",
    )
    print(json.dumps({"output": str(root), "tasks": len(seen)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
