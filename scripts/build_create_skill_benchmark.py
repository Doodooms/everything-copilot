from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import yaml


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


def task_payload(task_id: str, prompt: str, tags: list[str], files: list[str], *, should_trigger: bool = True) -> dict:
    return {
        "id": task_id,
        "name": task_id,
        "description": f"Adversarial create-skill completion task: {task_id}.",
        "tags": tags,
        "inputs": {"prompt": prompt, "files": [{"path": path} for path in files]},
        "expected": {"should_trigger": should_trigger},
    }


def skill_prompt(name: str) -> str:
    return (
        f"Authoring, repairing, restructuring, reviewing, and validating a production-ready skill named {name}. "
        "Create or update deterministic VS Code skill packages from a clear specification. "
        "This includes authoring, repairing, restructuring, reviewing, or validating a skill and its support files. "
        "Define its exact purpose and boundaries, "
        "include concrete acceptance and rejection cases, preserve the canonical inline workflow "
        "and grouped ACCEPT/REJECT architecture, keep provenance, and include only support files "
        "that the workflow truly consumes. Validate the package and report unresolved risks."
    )


def app_prompt(app: dict) -> str:
    return (
        f"Authoring, repairing, restructuring, reviewing, and validating a production-ready skill that guides implementation of a {app['name']}. "
        "Create or update deterministic VS Code skill packages from a clear specification. "
        "This includes authoring, repairing, restructuring, reviewing, or validating a skill and its support files. "
        f"The skill must turn this request into an executable, testable workflow: {app['constraints']} "
        "Define the domain ontology, semantic boundaries, acceptance criteria, failure handling, security and verification gates, and enough downstream guidance for another agent to implement the project coherently. "
        "Use the canonical inline grouped-list architecture and preserve source provenance."
    )


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
    root = args.output
    if root.exists():
        raise SystemExit(f"refusing to overwrite benchmark: {root}")
    root.mkdir(parents=True)
    shutil.copy2(args.manifest, root / "benchmark_manifest.json")
    shutil.copy2(args.source_skill / "SKILL.md", root / "SKILL.md")
    support = root / ".github" / "skills" / "create-skill"
    shutil.copytree(args.source_skill, support, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    seen: set[str] = set()
    for split in ("train", "selection", "holdout"):
        split_root = root / split
        (split_root / "tasks").mkdir(parents=True)
        split_support = split_root / ".github" / "skills" / "create-skill"
        shutil.copy2(args.source_skill / "SKILL.md", split_root / "SKILL.md")
        shutil.copytree(args.source_skill, split_support, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        files = ["SKILL.md", ".github/skills/create-skill/SKILL.md"]
        selected = manifest["splits"][split]
        names = list(dict.fromkeys(manifest["skills"] if selected.get("all_skills") else selected.get("skills", [])))
        for name in names:
            task_id = f"skill-{name}"
            prompt = skill_prompt(name)
            (split_root / "tasks" / f"{task_id}.yaml").write_text(
                yaml.safe_dump(task_payload(task_id, prompt, ["skill-creation", "adversarial", split], files), sort_keys=False),
                encoding="utf-8",
            )
            seen.add(task_id)
        for app in manifest["applications"]:
            if app["id"] not in selected.get("applications", []):
                continue
            task_id = f"app-{app['id']}"
            (split_root / "tasks" / f"{task_id}.yaml").write_text(
                yaml.safe_dump(task_payload(task_id, app_prompt(app), ["application", "llm-judge", split], files), sort_keys=False),
                encoding="utf-8",
            )
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
                yaml.safe_dump(task_payload(task_id, prompt, ["near-miss", "rejection", split], files, should_trigger=False), sort_keys=False),
                encoding="utf-8",
            )
            seen.add(task_id)
        write_eval(root, split, len(list((split_root / "tasks").glob("*.yaml"))))
    (root / "README.md").write_text(
        "# create-skill benchmark\n\n"
        "This benchmark is generated from `benchmark_manifest.json`. It evaluates create-skill as a meta-skill: the primary output is a high-quality skill package, and the application tasks test whether that package would give another agent enough structure to build a coherent project.\n\n"
        "## Benchmark: what it evaluates\n\n"
        "- `skill-*`: authoring quality across domains, including ontology, semantic contract, acceptance criteria, rejection boundaries, canonical topology, provenance, self-contained support files, validation, and user review.\n"
        "- `app-*`: downstream project guidance quality for a bounded application request, including domain modeling, implementation workflow, security, failure handling, acceptance criteria, and verification gates. These tasks inspect the generated skill; they do not yet execute a second project with it.\n"
        "- `reject-*-near-miss`: routing and refusal quality for requests that belong to agents, prompts, MCP servers, hooks, or direct application implementation rather than create-skill.\n"
        "- `train`: broad optimization signal covering all manifest skills plus representative applications.\n"
        "- `selection`: held-in optimization selection signal with representative skills, applications, and near misses.\n"
        "- `holdout`: unseen application domains used only for final generalization checks; it is excluded from SkillOpt configuration.\n\n"
        "The Waza prompt grader scores ontology, semantic contract and boundaries, topology and provenance, executable workflow, self-contained support-file discipline, validation and review evidence, downstream implementation utility, and failure/security/verification coverage. Efficiency remains a secondary bounded-action metric. Freeze this directory before optimization.\n",
        encoding="utf-8",
    )
    print(json.dumps({"output": str(root), "tasks": len(seen)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
