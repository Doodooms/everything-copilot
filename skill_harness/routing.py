from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .manifest import ManifestError, canonical_hash

SENTINEL_NAME = "__routing_probe__.md"
SENTINEL_CONTENT = """ROUTING_EVAL_WORKFLOW_ENTRY

This file is an evaluation sentinel.

Reading this file proves that the skill was invoked, the request was ACCEPTED,
and execution crossed the workflow-entry boundary.

STOP IMMEDIATELY.
Do not invoke another tool.
Do not read the real workflow.
Do not modify files.
Do not continue execution.

Return exactly: ROUTING_EVAL_ACCEPTED
"""


@dataclass(frozen=True)
class RoutingCase:
    id: str
    prompt: str
    should_use_skill: bool
    expected_admission: str
    expected_route: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "prompt": self.prompt,
            "should_use_skill": self.should_use_skill,
            "expected_admission": self.expected_admission,
            "expected_route": self.expected_route,
        }


@dataclass(frozen=True)
class RoutingSpec:
    id: str
    name: str
    description: str
    accept_rules: tuple[str, ...]
    reject_rules: tuple[dict[str, str | None], ...]
    workflow_payload: str
    cases: tuple[RoutingCase, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "accept_rules": list(self.accept_rules),
            "reject_rules": list(self.reject_rules),
            "workflow_payload": self.workflow_payload,
            "cases": [case.as_dict() for case in self.cases],
            "metadata": self.metadata,
        }

    @property
    def semantic_hash(self) -> str:
        return canonical_hash(self.as_dict())


@dataclass(frozen=True)
class RoutingArchitecture:
    id: str
    progressive_disclosure: str
    admission_representation: str
    workflow_location: str

    def __post_init__(self) -> None:
        if self.progressive_disclosure not in {"simple_inline", "inline_workflow", "deferred_workflow"}:
            raise ManifestError("unsupported progressive disclosure")
        if self.admission_representation not in {"grouped_lists", "markdown_table", "compact_rules"}:
            raise ManifestError("unsupported admission representation")

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "progressive_disclosure": self.progressive_disclosure,
            "admission_representation": self.admission_representation,
            "workflow_location": self.workflow_location,
        }


def load_routing_spec(path: Path) -> RoutingSpec:
    payload = json.loads(path.read_text(encoding="utf-8"))
    try:
        cases = tuple(RoutingCase(**case) for case in payload["cases"])
        return RoutingSpec(
            id=payload["id"],
            name=payload["name"],
            description=payload["description"],
            accept_rules=tuple(payload["accept_rules"]),
            reject_rules=tuple(payload["reject_rules"]),
            workflow_payload=payload["workflow_payload"],
            cases=cases,
            metadata=dict(payload.get("metadata", {})),
        )
    except (KeyError, TypeError) as exc:
        raise ManifestError(f"invalid routing spec: {path}") from exc


def load_architecture(path: Path) -> RoutingArchitecture:
    try:
        return RoutingArchitecture(**json.loads(path.read_text(encoding="utf-8")))
    except (KeyError, TypeError) as exc:
        raise ManifestError(f"invalid routing architecture: {path}") from exc


def _admission_markdown(spec: RoutingSpec, representation: str) -> str:
    if representation == "grouped_lists":
        accepted = "\n".join(f"- {rule}" for rule in spec.accept_rules)
        rejected = "\n".join(
            f"- {item['case']} -> {item['route'] or 'null'}" for item in spec.reject_rules
        )
        return f"## ACCEPT\n{accepted}\n\n## REJECT\n{rejected}"
    if representation == "markdown_table":
        rows = ["| Request | Decision | Route |", "|---|---|---|"]
        rows.extend(f"| {rule} | ACCEPT | - |" for rule in spec.accept_rules)
        rows.extend(f"| {item['case']} | REJECT | {item['route'] or 'null'} |" for item in spec.reject_rules)
        return "\n".join(rows)
    return "\n".join(["## Admission", *[f"ACCEPT: {rule}" for rule in spec.accept_rules], *[
        f"REJECT: {item['case']} -> {item['route'] or 'null'}" for item in spec.reject_rules
    ]])


def _real_admission_markdown(content: str, representation: str) -> str:
    sections = re.split(r"\n## (ACCEPT|REJECT)\n", content)
    accepted = [line[2:].strip() for line in sections[2].splitlines() if line.startswith("- ")] if len(sections) > 2 else []
    rejected = [line[2:].strip() for line in sections[4].splitlines() if line.startswith("- ")] if len(sections) > 4 else []
    if representation == "markdown_table":
        rows = ["| Request | Decision | Route |", "|---|---|---|"]
        rows.extend(f"| {rule} | ACCEPT | - |" for rule in accepted)
        rows.extend(
            f"| {rule.rsplit(' -> ', 1)[0]} | REJECT | {rule.rsplit(' -> ', 1)[-1]} |"
            for rule in rejected
        )
        return "\n".join(rows)
    return "\n".join([
        "## Admission",
        *[f"ACCEPT: {rule}" for rule in accepted],
        *[f"REJECT: {rule}" for rule in rejected],
    ])


def render_routing_variant(spec: RoutingSpec, architecture: RoutingArchitecture, destination: Path) -> dict[str, str]:
    skill_dir = destination / spec.name
    references = skill_dir / "references"
    references.mkdir(parents=True, exist_ok=True)
    (references / SENTINEL_NAME).write_text(SENTINEL_CONTENT, encoding="utf-8")
    if architecture.progressive_disclosure == "simple_inline":
        body = (
            f"---\nname: {spec.name}\ndescription: {spec.description}\n---\n\n"
            f"# Workflow\n\n"
            f"When this skill is invoked, read references/{SENTINEL_NAME} before any workflow action.\n"
            "The sentinel is terminal for this routing evaluation.\n\n"
            f"{spec.workflow_payload}\n"
        )
    else:
        admission = _admission_markdown(spec, architecture.admission_representation)
        routing = (
            "## Routing contract\n\n"
            "Evaluate the request against the ACCEPT and REJECT rules before doing any workflow action.\n"
            "For REJECT, do not read the sentinel and return exactly this structured result:\n\n"
            '```json\n{"status":"rejected","skill":"<skill-name>","reason":"<concise reason>","routing":"<route or null>"}\n```\n\n'
            f"For ACCEPT, read references/{SENTINEL_NAME} as the first action. The sentinel is terminal for this routing evaluation; do not read the real workflow afterward.\n"
        )
        body = f"---\nname: {spec.name}\ndescription: {spec.description}\n---\n\n# Definitions\n\n{spec.description}\n\n{admission}\n\n## Routing\n\n{routing}"
    if architecture.progressive_disclosure == "inline_workflow":
        body += f"\n## Workflow\n\n{spec.workflow_payload}\n"
    elif architecture.progressive_disclosure == "deferred_workflow":
        body += "\n## Workflow\n\nRead `./references/workflow.md` only after ACCEPT and sentinel read.\n"
        (references / "workflow.md").write_text(spec.workflow_payload + "\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")
    return {"skill": (skill_dir / "SKILL.md").as_posix(), "semantic_hash": spec.semantic_hash}


def render_real_skill_variant(
    source_skill: Path,
    architecture: RoutingArchitecture,
    destination: Path,
) -> dict[str, str]:
    """Render a routing-only copy from the real target skill.

    The source package remains untouched. Only the routing disclosure boundary
    changes; the TDD workflow text is copied verbatim or deferred as a unit.
    """
    source_skill = source_skill.resolve()
    skill_dir = destination / source_skill.name
    shutil.copytree(source_skill, skill_dir, dirs_exist_ok=True)
    references = skill_dir / "references"
    references.mkdir(parents=True, exist_ok=True)
    (references / SENTINEL_NAME).write_text(SENTINEL_CONTENT, encoding="utf-8")
    skill_path = skill_dir / "SKILL.md"
    body = skill_path.read_text(encoding="utf-8")
    if architecture.progressive_disclosure == "simple_inline":
        body = re.sub(r"\n?<admission>.*?</admission>\n?", "\n", body, flags=re.DOTALL)
        body = re.sub(r"\n?<routing>.*?</routing>\n?", "\n", body, flags=re.DOTALL)
    elif architecture.progressive_disclosure == "deferred_workflow":
        workflow_match = re.search(r"<workflow>.*?</workflow>", body, flags=re.DOTALL)
        if not workflow_match:
            raise ManifestError("real skill has no workflow block to defer")
        workflow = workflow_match.group(0)
        workflow_content = workflow[len("<workflow>") : -len("</workflow>")].strip()
        (skill_dir / "references").mkdir(parents=True, exist_ok=True)
        (skill_dir / "references" / "workflow.md").write_text(workflow_content + "\n", encoding="utf-8")
        body = body[: workflow_match.start()] + (
            "<workflow>\n\nRead [the deferred workflow](./references/workflow.md) only after ACCEPT.\n\n</workflow>"
        ) + body[workflow_match.end() :]
    sentinel_ref = f"Read references/{SENTINEL_NAME} as the first routing action."
    if architecture.admission_representation != "grouped_lists":
        admission_match = re.search(r"<admission>(.*?)</admission>", body, flags=re.DOTALL)
        if admission_match:
            admission = _real_admission_markdown(
                admission_match.group(1), architecture.admission_representation
            )
            body = body[: admission_match.start()] + f"<admission>\n\n{admission}\n\n</admission>" + body[admission_match.end() :]
    if sentinel_ref not in body:
        body = body.replace("</routing>", f"\n- If `ACCEPT`, {sentinel_ref}\n\n</routing>")
        body = body.replace("<workflow>", f"<workflow>\n\n{sentinel_ref}", 1)
    skill_path.write_text(body, encoding="utf-8")
    return {"skill": skill_path.as_posix(), "semantic_hash": canonical_hash(body)}
