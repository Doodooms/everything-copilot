from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .routing import (
    RoutingArchitecture,
    load_architecture,
    load_routing_spec,
    render_real_skill_variant,
    render_routing_variant,
)
from .waza_adapter import WazaError, configure_summary_only_discovery


class AblationPreparationError(RuntimeError):
    """Raised when a routing ablation cannot be prepared safely."""


def _write_task(path: Path, case: Any, resource_files: list[str]) -> None:
    try:
        import yaml
    except ImportError as exc:
        raise AblationPreparationError("PyYAML is required to prepare Waza tasks") from exc
    routing_tag = f"route-{case.expected_route}" if case.expected_route else "route-none"
    payload = {
        "id": case.id,
        "name": case.id,
        "description": f"Routing ablation case {case.id}.",
        "tags": [
            "routing-ablation",
            "positive" if case.should_use_skill else "negative",
            f"admission-{case.expected_admission}",
            routing_tag,
        ],
        "inputs": {
            "prompt": case.prompt,
            "files": [{"path": resource_path} for resource_path in resource_files],
        },
        "expected": {"should_trigger": case.should_use_skill},
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _prepare_eval(
    workspace: Path,
    skill_name: str,
    cases: tuple[Any, ...],
    waza_bin: Path,
    model: str | None = None,
) -> Path:
    eval_path = workspace / "eval.yaml"
    completed = subprocess.run(
        [str(waza_bin), "new", "eval", skill_name, "--output", str(eval_path)],
        cwd=workspace,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise WazaError(completed.stderr or completed.stdout or "waza new eval failed")
    tasks_dir = workspace / "tasks"
    for generated in tasks_dir.glob("*.yaml"):
        generated.unlink()
    resource_files = ["SKILL.md"]
    resource_files.extend(
        path.relative_to(workspace).as_posix()
        for path in sorted((workspace / ".github" / "skills").rglob("*"))
        if path.is_file()
    )
    for case in cases:
        _write_task(tasks_dir / f"{case.id}.yaml", case, resource_files)
    configure_summary_only_discovery(eval_path, model=model)
    return eval_path


def prepare_phase_0a(
    specs_dir: Path,
    architectures_dir: Path,
    output_root: Path,
    *,
    waza_bin: Path = Path(".tools/bin/waza"),
    source_skill: Path | None = None,
    catalogue_roots: dict[str, Path] | None = None,
    model: str | None = None,
    allow_admission_variants: bool = False,
) -> dict[str, Any]:
    """Render every fixed fixture and prepare isolated, no-rollout Waza evals."""
    waza_bin = waza_bin.expanduser().resolve()
    specs = [load_routing_spec(path) for path in sorted(specs_dir.glob("*.json"))]
    architectures = [load_architecture(path) for path in sorted(architectures_dir.glob("*.json"))]
    if not specs:
        raise AblationPreparationError(f"no routing specs found in {specs_dir}")
    if not architectures:
        raise AblationPreparationError(f"no architecture candidates found in {architectures_dir}")
    if source_skill and not source_skill.joinpath("SKILL.md").is_file():
        raise AblationPreparationError(f"source skill is missing SKILL.md: {source_skill}")
    if source_skill and any(spec.name != source_skill.name for spec in specs):
        raise AblationPreparationError("real-skill Phase 0A requires specs to target the source skill name")
    for architecture in architectures:
        if not allow_admission_variants and architecture.admission_representation != "grouped_lists":
            raise AblationPreparationError(
                f"Phase 0A candidate {architecture.id} changes admission representation"
            )
    output_root.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "phase": "0A",
        "specs": [spec.id for spec in specs],
        "architectures": [],
        "catalogues": sorted(catalogue_roots or {}),
    }
    for architecture in architectures:
        architecture_root = output_root / architecture.id
        architecture_root.mkdir(exist_ok=True)
        architecture_entry = {"id": architecture.id, "fixtures": []}
        for spec in specs:
            fixture_root = architecture_root / spec.id
            skills_root = fixture_root / ".github" / "skills"
            if source_skill:
                render_result = render_real_skill_variant(source_skill, architecture, skills_root)
            else:
                render_result = render_routing_variant(spec, architecture, skills_root)
            skill_root = fixture_root / ".github" / "skills" / spec.name
            catalogue_items = catalogue_roots.items() if catalogue_roots else (("default", None),)
            for catalogue_id, catalogue_root in catalogue_items:
                if catalogue_root:
                    catalogue_fixture = architecture_root / spec.id / catalogue_id
                    if catalogue_fixture != fixture_root:
                        shutil.copytree(fixture_root, catalogue_fixture, dirs_exist_ok=True)
                    catalogue_skills = catalogue_fixture / ".github" / "skills"
                    shutil.copytree(catalogue_root / ".github" / "skills", catalogue_skills, dirs_exist_ok=True)
                    if source_skill:
                        render_result = render_real_skill_variant(source_skill, architecture, catalogue_skills)
                    skill_root = catalogue_skills / spec.name
                    shutil.copy2(skill_root / "SKILL.md", catalogue_fixture / "SKILL.md")
                    eval_path = _prepare_eval(catalogue_fixture, spec.name, spec.cases, waza_bin, model=model)
                else:
                    catalogue_fixture = fixture_root
                    shutil.copy2(skill_root / "SKILL.md", catalogue_fixture / "SKILL.md")
                    eval_path = _prepare_eval(fixture_root, spec.name, spec.cases, waza_bin, model=model)
                architecture_entry["fixtures"].append({
                    "spec_id": spec.id,
                    "catalogue_id": catalogue_id,
                    "skill": render_result["skill"],
                    "eval": eval_path.as_posix(),
                    "semantic_hash": render_result["semantic_hash"],
                })
                if not skill_root.is_dir():
                    raise AblationPreparationError(f"rendered skill missing: {skill_root}")
        manifest["architectures"].append(architecture_entry)
    manifest_path = output_root / "preparation.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest
