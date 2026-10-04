#!/usr/bin/env python3
"""Validate an explicitly supplied SDD task-state exchange artifact.

This validator does not require workflows to create a local manifest or task
history file.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

ID_PATTERNS = {
    "specification": re.compile(r"^SPEC-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "requirement": re.compile(r"^REQ-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "acceptance criterion": re.compile(r"^AC-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "architecture decision": re.compile(r"^ADR-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "task": re.compile(r"^TASK-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "defect": re.compile(r"^DEFECT-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "QA run": re.compile(r"^QA-RUN-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "review": re.compile(r"^REVIEW-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "semantic concept": re.compile(r"^CONCEPT-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "semantic relation": re.compile(r"^REL-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "semantic state": re.compile(r"^STATE-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "semantic event": re.compile(r"^EVENT-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "semantic transition": re.compile(r"^TRANSITION-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "semantic invariant": re.compile(r"^INV-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "semantic contract": re.compile(r"^CONTRACT-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "semantic assumption": re.compile(r"^ASSUMPTION-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "semantic hypothesis": re.compile(r"^HYPOTHESIS-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "semantic unknown": re.compile(r"^UNKNOWN-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
    "validation evidence": re.compile(r"^EVIDENCE-[A-Z0-9]+(?:-[A-Z0-9]+)*$"),
}

SEMANTIC_COLLECTIONS = {
    "terminology": None,
    "concepts": ("semantic concept", "term", "meaning"),
    "relations": ("semantic relation", "predicate", None),
    "states": ("semantic state", "name", None),
    "events": ("semantic event", "name", None),
    "transitions": ("semantic transition", None, None),
    "invariants": ("semantic invariant", "statement", None),
    "contracts": ("semantic contract", "statement", None),
    "assumptions": ("semantic assumption", "statement", "source"),
    "hypotheses": ("semantic hypothesis", "statement", "source"),
    "unknowns": ("semantic unknown", "question", None),
}

REQUIRED_GATES = {"architecture", "plan", "implementation", "qa", "review"}
LEGACY_REQUIRED_GATES = {"plan", "implementation", "qa", "review"}

INVALIDATION_GRAPH = {
    "specification": (
        "architecture",
        "plan",
        "tasks",
        "implementation",
        "qa",
        "review",
    ),
    "architecture": ("plan", "tasks", "implementation", "qa", "review"),
    "plan": ("tasks", "implementation", "qa", "review"),
    "tasks": ("implementation", "qa", "review"),
    "implementation": ("qa", "review"),
    "qa": ("review",),
}


def _manifest(payload: Any) -> tuple[dict[str, Any] | None, str]:
    if not isinstance(payload, dict):
        return None, "state"
    candidate = payload.get("manifest", payload)
    if not isinstance(candidate, dict):
        return None, "manifest"
    return candidate, "manifest" if candidate is not payload else ""


def _path(prefix: str, key: str) -> str:
    return f"{prefix}.{key}" if prefix else key


def _list_of_dicts(
    value: Any, location: str, errors: list[str], *, required: bool = True
) -> list[dict[str, Any]]:
    if value is None and not required:
        return []
    if not isinstance(value, list):
        errors.append(f"{location} must be a list")
        return []
    result = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            errors.append(f"{location}[{index}] must be an object")
        else:
            result.append(item)
    return result


def _string_ids(
    item: dict[str, Any],
    field: str,
    location: str,
    errors: list[str],
    *,
    required: bool = False,
) -> list[str]:
    value = item.get(field)
    if value is None and not required:
        return []
    if not isinstance(value, list) or any(
        not isinstance(entry, str) for entry in value
    ):
        errors.append(f"{location}.{field} must be a list of IDs")
        return []
    if required and not value:
        errors.append(f"{location}.{field} must not be empty")
    return value


def _check_id(
    value: Any,
    kind: str,
    location: str,
    errors: list[str],
    seen: set[str] | None = None,
) -> str | None:
    pattern = ID_PATTERNS[kind]
    if not isinstance(value, str) or not pattern.fullmatch(value):
        errors.append(f"{location} must use the {kind} ID format")
        return None
    if seen is not None:
        if value in seen:
            errors.append(f"{location} has duplicate ID {value}")
        seen.add(value)
    return value


def _status(
    item: Any, field: str, location: str, allowed: set[str], errors: list[str]
) -> str | None:
    if not isinstance(item, dict):
        errors.append(f"{location} must be an object")
        return None
    value = item.get(field)
    if value not in allowed:
        errors.append(f"{location}.{field} must be one of {', '.join(sorted(allowed))}")
        return None
    return value


def _has_required_open_decision(specification: dict[str, Any]) -> bool:
    decisions = specification.get("open_decisions", [])
    if not isinstance(decisions, list):
        return False
    return any(
        isinstance(decision, dict)
        and decision.get("required", True)
        and not decision.get("resolved", False)
        for decision in decisions
    )


def _validate_semantic_model(
    specification: dict[str, Any], location: str, errors: list[str]
) -> set[str]:
    if "semantic_model" not in specification:
        return set()
    model = specification.get("semantic_model")
    if not isinstance(model, dict):
        errors.append(f"{location}.semantic_model must be an object when present")
        return set()

    allowed_fields = {"schema_version", "scope", *SEMANTIC_COLLECTIONS}
    for field in model.keys() - allowed_fields:
        errors.append(f"{location}.semantic_model has unknown field {field!r}")
    if type(model.get("schema_version")) is not int or model.get("schema_version") != 1:
        errors.append(f"{location}.semantic_model.schema_version must be 1")
    if not isinstance(model.get("scope"), str) or not model["scope"].strip():
        errors.append(f"{location}.semantic_model.scope must be non-empty text")

    collections: dict[str, list[dict[str, Any]]] = {}
    semantic_ids: set[str] = set()
    if not any(
        isinstance(model.get(name), list) and model[name]
        for name in SEMANTIC_COLLECTIONS
    ):
        errors.append(
            f"{location}.semantic_model must contain at least one non-empty semantic collection"
        )

    canonical_terms: dict[str, str] = {}
    aliases: dict[str, str] = {}
    for collection, schema in SEMANTIC_COLLECTIONS.items():
        items = _list_of_dicts(
            model.get(collection, []),
            f"{location}.semantic_model.{collection}",
            errors,
            required=False,
        )
        collections[collection] = items
        if collection == "terminology":
            for index, item in enumerate(items):
                item_location = f"{location}.semantic_model.terminology[{index}]"
                term = item.get("term")
                meaning = item.get("meaning")
                if not isinstance(term, str) or not term.strip():
                    errors.append(f"{item_location}.term must be non-empty text")
                    continue
                if not isinstance(meaning, str) or not meaning.strip():
                    errors.append(f"{item_location}.meaning must be non-empty text")
                normalized_term = term.casefold().strip()
                if normalized_term in canonical_terms:
                    errors.append(
                        f"{item_location}.term duplicates canonical terminology"
                    )
                canonical_terms[normalized_term] = term
                raw_aliases = item.get("aliases", [])
                if not isinstance(raw_aliases, list) or any(
                    not isinstance(alias, str) or not alias.strip()
                    for alias in raw_aliases
                ):
                    errors.append(
                        f"{item_location}.aliases must be a list of non-empty strings"
                    )
                    continue
                for alias in raw_aliases:
                    normalized_alias = alias.casefold().strip()
                    previous = aliases.get(normalized_alias)
                    if previous is not None and previous != normalized_term:
                        errors.append(
                            f"{item_location}.aliases contains an alias mapped to multiple canonical terms"
                        )
                    aliases[normalized_alias] = normalized_term
            continue

        if schema is None:
            continue
        id_kind, required_text_field, secondary_text_field = schema
        for index, item in enumerate(items):
            item_location = f"{location}.semantic_model.{collection}[{index}]"
            _check_id(
                item.get("id"),
                id_kind,
                f"{item_location}.id",
                errors,
                semantic_ids,
            )
            for field in (required_text_field, secondary_text_field):
                if field is not None and (
                    not isinstance(item.get(field), str) or not item[field].strip()
                ):
                    errors.append(f"{item_location}.{field} must be non-empty text")
            if collection == "concepts" and (
                not isinstance(item.get("kind"), str) or not item["kind"].strip()
            ):
                errors.append(f"{item_location}.kind must be non-empty text")
            if collection == "relations":
                for field in ("source_concept", "target_concept"):
                    if not isinstance(item.get(field), str) or not item[field].strip():
                        errors.append(f"{item_location}.{field} must be a concept ID")
                if "cardinality" in item and (
                    not isinstance(item["cardinality"], str)
                    or not item["cardinality"].strip()
                ):
                    errors.append(f"{item_location}.cardinality must be non-empty text")
            if collection in {"states", "transitions"} and (
                not isinstance(item.get("concept_id"), str)
                or not item["concept_id"].strip()
            ):
                errors.append(f"{item_location}.concept_id must be a concept ID")
            if collection == "assumptions" and (
                not isinstance(item.get("source"), str) or not item["source"].strip()
            ):
                errors.append(
                    f"{item_location}.source must be non-empty provenance text"
                )
            if (
                collection == "unknowns"
                and "owner" in item
                and (not isinstance(item["owner"], str) or not item["owner"].strip())
            ):
                errors.append(
                    f"{item_location}.owner must be non-empty text when present"
                )

    def check_ref(value: Any, valid: set[str], where: str, expected: str) -> None:
        if isinstance(value, str) and value not in valid:
            errors.append(f"{where} references missing {expected} {value}")

    concept_ids = {
        item.get("id")
        for item in collections["concepts"]
        if isinstance(item.get("id"), str)
    }
    state_ids = {
        item.get("id")
        for item in collections["states"]
        if isinstance(item.get("id"), str)
    }
    event_ids = {
        item.get("id")
        for item in collections["events"]
        if isinstance(item.get("id"), str)
    }
    for index, item in enumerate(collections["relations"]):
        item_location = f"{location}.semantic_model.relations[{index}]"
        check_ref(item.get("source_concept"), concept_ids, item_location, "concept")
        check_ref(item.get("target_concept"), concept_ids, item_location, "concept")
    for index, item in enumerate(collections["states"]):
        check_ref(
            item.get("concept_id"),
            concept_ids,
            f"{location}.semantic_model.states[{index}]",
            "concept",
        )
    for index, item in enumerate(collections["events"]):
        item_location = f"{location}.semantic_model.events[{index}]"
        for concept_id in _string_ids(item, "concept_ids", item_location, errors):
            check_ref(concept_id, concept_ids, item_location, "concept")
    for collection in ("invariants", "contracts"):
        for index, item in enumerate(collections[collection]):
            item_location = f"{location}.semantic_model.{collection}[{index}]"
            for concept_id in _string_ids(item, "concept_ids", item_location, errors):
                check_ref(concept_id, concept_ids, item_location, "concept")
    for index, item in enumerate(collections["transitions"]):
        item_location = f"{location}.semantic_model.transitions[{index}]"
        check_ref(item.get("concept_id"), concept_ids, item_location, "concept")
        check_ref(item.get("from_state_id"), state_ids, item_location, "state")
        check_ref(item.get("to_state_id"), state_ids, item_location, "state")
        check_ref(item.get("event_id"), event_ids, item_location, "event")
        for field in ("from_state_id", "to_state_id"):
            state_id = item.get(field)
            state = next(
                (
                    candidate
                    for candidate in collections["states"]
                    if candidate.get("id") == state_id
                ),
                None,
            )
            if (
                state is not None
                and isinstance(item.get("concept_id"), str)
                and state.get("concept_id") != item.get("concept_id")
            ):
                errors.append(f"{item_location}.{field} belongs to a different concept")

    for alias, canonical in aliases.items():
        if alias in canonical_terms and alias != canonical:
            errors.append(
                f"{location}.semantic_model.terminology declares an alias that conflicts with canonical term {canonical_terms[alias]}"
            )
    return semantic_ids


def _validate_validation_evidence(
    state: dict[str, Any],
    prefix: str,
    revision: Any,
    errors: list[str],
) -> tuple[set[str], dict[str, dict[str, Any]]]:
    location = _path(prefix, "validation_evidence")
    records = _list_of_dicts(
        state.get("validation_evidence", []), location, errors, required=False
    )
    evidence_ids: set[str] = set()
    by_id: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        record_location = f"{location}[{index}]"
        identifier = _check_id(
            record.get("id"),
            "validation evidence",
            f"{record_location}.id",
            errors,
            evidence_ids,
        )
        for field in ("check", "subject_revision", "environment", "producer"):
            if not isinstance(record.get(field), str) or not record[field].strip():
                errors.append(f"{record_location}.{field} must be non-empty text")
        if record.get("result") not in {"pass", "fail", "partial", "blocked"}:
            errors.append(
                f"{record_location}.result must be pass, fail, partial, or blocked"
            )
        if "command" in record and (
            not isinstance(record["command"], str) or not record["command"].strip()
        ):
            errors.append(
                f"{record_location}.command must be non-empty text when present"
            )
        if "spec_revision" in record and record["spec_revision"] != revision:
            errors.append(f"{record_location} records a stale specification revision")
        if identifier is not None:
            by_id[identifier] = record
    return evidence_ids, by_id


def _validate_evidence_references(
    item: dict[str, Any],
    location: str,
    evidence_ids: set[str],
    evidence_by_id: dict[str, dict[str, Any]],
    specification_revision: Any,
    implementation_revision: Any,
    claimed_criteria: set[str],
    require_passing_claim: bool,
    errors: list[str],
) -> None:
    references = _string_ids(item, "validation_evidence_refs", location, errors)
    if require_passing_claim and not references:
        errors.append(f"{location} makes a passing claim without validation evidence")
    implementation_revision_known = isinstance(implementation_revision, str) and bool(
        implementation_revision.strip()
    )
    if require_passing_claim and not implementation_revision_known:
        errors.append(
            f"{location} makes a passing claim without a current implementation revision"
        )

    covered_criteria: set[str] = set()
    for evidence_id in references:
        record = evidence_by_id.get(evidence_id)
        if evidence_id not in evidence_ids:
            errors.append(
                f"{location}.validation_evidence_refs references missing evidence {evidence_id}"
            )
            continue
        if record is None:
            continue
        if require_passing_claim and (
            not implementation_revision_known
            or record.get("subject_revision") != implementation_revision
        ):
            errors.append(
                f"{location}.validation_evidence_refs references evidence for a stale implementation revision"
            )
            continue
        if (
            require_passing_claim
            and record.get("spec_revision") != specification_revision
        ):
            errors.append(
                f"{location}.validation_evidence_refs references evidence for a stale specification revision"
            )
            continue
        if require_passing_claim and record.get("result") != "pass":
            errors.append(
                f"{location}.validation_evidence_refs must reference passing evidence for a passing claim"
            )
            continue
        if require_passing_claim:
            record_criteria = record.get("acceptance_criteria", [])
            if isinstance(record_criteria, list):
                covered_criteria.update(record_criteria)

    if require_passing_claim:
        uncovered = claimed_criteria - covered_criteria
        if uncovered:
            errors.append(
                f"{location}.validation_evidence_refs do not cover passing criteria: "
                + ", ".join(sorted(uncovered))
            )


def _required_gates(state: dict[str, Any], prefix: str, errors: list[str]) -> set[str]:
    if "required_gates" not in state:
        return set(LEGACY_REQUIRED_GATES)
    gates = state.get("required_gates")
    if not isinstance(gates, list) or any(not isinstance(gate, str) for gate in gates):
        errors.append(f"{_path(prefix, 'required_gates')} must be a list of gate names")
        return set(LEGACY_REQUIRED_GATES)
    selected = set(gates)
    if len(selected) != len(gates):
        errors.append(f"{_path(prefix, 'required_gates')} must not contain duplicates")
    unknown = selected - REQUIRED_GATES
    if unknown:
        errors.append(
            f"{_path(prefix, 'required_gates')} contains unknown gates: {', '.join(sorted(unknown))}"
        )
    if "implementation" not in selected:
        errors.append(
            f"{_path(prefix, 'required_gates')} must retain the implementation gate for SDD convergence"
        )
        selected.add("implementation")
    if "review" in selected and "qa" not in selected:
        errors.append(
            f"{_path(prefix, 'required_gates')} must include QA when Reviewer acceptance is required"
        )
    return selected


def _blocking_findings(state: dict[str, Any]) -> list[str]:
    findings = state.get("open_findings", [])
    if not isinstance(findings, list):
        return ["open_findings must be a list"]
    return [
        str(finding.get("id", "unnamed finding"))
        for finding in findings
        if isinstance(finding, dict)
        and (
            finding.get("blocking") is True
            or finding.get("status") in {"open", "blocked"}
        )
    ]


def _validate_task_dependency_cycles(
    tasks: list[dict[str, Any]], task_ids: set[str], prefix: str, errors: list[str]
) -> None:
    dependencies: dict[str, list[str]] = {}
    for index, task in enumerate(tasks):
        task_id = task.get("id")
        if not isinstance(task_id, str):
            continue
        location = f"{prefix}.tasks[{index}]"
        dependencies[task_id] = _string_ids(task, "depends_on", location, errors)
        for dependency in dependencies[task_id]:
            if dependency not in task_ids:
                errors.append(
                    f"{location}.depends_on references missing task {dependency}"
                )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            errors.append(
                f"{prefix}.tasks dependency graph contains a cycle at {task_id}"
            )
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in dependencies.get(task_id, []):
            if dependency in dependencies:
                visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in task_ids:
        visit(task_id)


def validate_state(payload: Any) -> list[str]:
    """Return deterministic structural and evidence errors for a task or manifest."""
    state, wrapper = _manifest(payload)
    if state is None:
        return [f"{wrapper} must be an object"]
    prefix = wrapper
    errors: list[str] = []
    required_gates = _required_gates(state, prefix, errors)
    risk_level = state.get("risk_level")
    if "risk_level" in state and risk_level not in {"L0", "L1", "L2", "L3"}:
        errors.append(f"{_path(prefix, 'risk_level')} must be L0, L1, L2, or L3")
    if ("risk_level" in state) != ("required_gates" in state):
        errors.append(
            "risk_level and required_gates must be recorded together in the task manifest"
        )

    specification = state.get("specification")
    if not isinstance(specification, dict):
        return [f"{_path(prefix, 'specification')} must be an object"]
    spec_location = _path(prefix, "specification")
    spec_id = _check_id(
        specification.get("id"), "specification", f"{spec_location}.id", errors
    )
    revision = specification.get("revision")
    if type(revision) is not int or revision < 1:
        errors.append(f"{spec_location}.revision must be a positive integer")
        revision = None
    spec_status = _status(
        specification,
        "status",
        spec_location,
        {"draft", "ready", "blocked"},
        errors,
    )
    if spec_status == "ready" and (
        not isinstance(specification.get("objective"), str)
        or not specification["objective"].strip()
    ):
        errors.append(f"{spec_location}.objective must be non-empty text when ready")
    semantic_ids = _validate_semantic_model(specification, spec_location, errors)
    validation_evidence_ids, validation_evidence_by_id = _validate_validation_evidence(
        state, prefix, revision, errors
    )

    requirements = _list_of_dicts(
        specification.get("requirements"),
        f"{spec_location}.requirements",
        errors,
    )
    if spec_status == "ready" and not requirements:
        errors.append(f"{spec_location}.requirements must not be empty when ready")
    requirement_ids: set[str] = set()
    for index, requirement in enumerate(requirements):
        location = f"{spec_location}.requirements[{index}]"
        identifier = _check_id(
            requirement.get("id"),
            "requirement",
            f"{location}.id",
            errors,
            requirement_ids,
        )
        if (
            not isinstance(requirement.get("statement"), str)
            or not requirement["statement"].strip()
        ):
            errors.append(f"{location}.statement must be non-empty text")
        for semantic_id in _string_ids(requirement, "semantic_refs", location, errors):
            if semantic_id not in semantic_ids:
                errors.append(
                    f"{location}.semantic_refs references missing semantic item {semantic_id}"
                )
        if identifier is None:
            continue

    criteria = _list_of_dicts(
        specification.get("acceptance_criteria"),
        f"{spec_location}.acceptance_criteria",
        errors,
    )
    if spec_status == "ready" and not criteria:
        errors.append(
            f"{spec_location}.acceptance_criteria must not be empty when ready"
        )
    criterion_ids: set[str] = set()
    criterion_requirements: dict[str, list[str]] = {}
    for index, criterion in enumerate(criteria):
        location = f"{spec_location}.acceptance_criteria[{index}]"
        identifier = _check_id(
            criterion.get("id"),
            "acceptance criterion",
            f"{location}.id",
            errors,
            criterion_ids,
        )
        if (
            not isinstance(criterion.get("statement"), str)
            or not criterion["statement"].strip()
        ):
            errors.append(f"{location}.statement must be non-empty text")
        references = _string_ids(
            criterion, "requirements", location, errors, required=True
        )
        semantic_refs = _string_ids(criterion, "semantic_refs", location, errors)
        if identifier is not None:
            criterion_requirements[identifier] = references
        for semantic_id in semantic_refs:
            if semantic_id not in semantic_ids:
                errors.append(
                    f"{location}.semantic_refs references missing semantic item {semantic_id}"
                )
        for requirement_id in references:
            if requirement_id not in requirement_ids:
                errors.append(
                    f"{location}.requirements references missing requirement {requirement_id}"
                )
    for index, record in enumerate(
        state.get("validation_evidence", [])
        if isinstance(state.get("validation_evidence", []), list)
        else []
    ):
        if not isinstance(record, dict):
            continue
        location = f"{_path(prefix, 'validation_evidence')}[{index}]"
        for criterion_id in _string_ids(
            record, "acceptance_criteria", location, errors
        ):
            if criterion_id not in criterion_ids:
                errors.append(
                    f"{location}.acceptance_criteria references missing criterion {criterion_id}"
                )

    _list_of_dicts(
        specification.get("open_decisions", []),
        f"{spec_location}.open_decisions",
        errors,
    )
    if spec_status == "ready" and _has_required_open_decision(specification):
        errors.append(
            f"{spec_location} is ready with unresolved required open decisions"
        )
    if spec_status == "ready":
        covered_by_criteria = {
            requirement_id
            for references in criterion_requirements.values()
            for requirement_id in references
        }
        for requirement_id in requirement_ids - covered_by_criteria:
            errors.append(
                f"{spec_location} has no acceptance criterion linked to {requirement_id}"
            )

    architecture = state.get("architecture")
    architecture_status = _status(
        architecture,
        "status",
        _path(prefix, "architecture"),
        {"not_required", "pending", "ready", "stale", "blocked"},
        errors,
    )
    architecture_ids: set[str] = set()
    if isinstance(architecture, dict):
        decisions = _list_of_dicts(
            architecture.get("decisions", []),
            f"{_path(prefix, 'architecture')}.decisions",
            errors,
        )
        for index, decision in enumerate(decisions):
            location = f"{_path(prefix, 'architecture')}.decisions[{index}]"
            identifier = _check_id(
                decision.get("id"),
                "architecture decision",
                f"{location}.id",
                errors,
                architecture_ids,
            )
            if identifier is None:
                continue
            for requirement_id in _string_ids(
                decision, "requirements", location, errors
            ):
                if requirement_id not in requirement_ids:
                    errors.append(
                        f"{location}.requirements references missing requirement {requirement_id}"
                    )
        if (
            architecture_status == "ready"
            and architecture.get("spec_revision") != revision
        ):
            errors.append(
                f"{_path(prefix, 'architecture')} consumes a stale specification revision"
            )
        architecture_revision = architecture.get("revision")
        if architecture_status == "ready" and (
            type(architecture_revision) is not int or architecture_revision < 1
        ):
            errors.append(
                f"{_path(prefix, 'architecture')}.revision must be a positive integer"
            )

    plan = state.get("plan")
    plan_status = _status(
        plan,
        "status",
        _path(prefix, "plan"),
        {"not_required", "pending", "ready", "stale", "blocked"},
        errors,
    )
    if (
        isinstance(plan, dict)
        and plan_status == "ready"
        and plan.get("spec_revision") != revision
    ):
        errors.append(
            f"{_path(prefix, 'plan')} consumes a stale specification revision"
        )
    if (
        isinstance(plan, dict)
        and plan_status == "ready"
        and (type(plan.get("revision")) is not int or plan["revision"] < 1)
    ):
        errors.append(f"{_path(prefix, 'plan')}.revision must be a positive integer")

    tasks = _list_of_dicts(state.get("tasks"), _path(prefix, "tasks"), errors)
    task_ids: set[str] = set()
    for index, task in enumerate(tasks):
        location = f"{_path(prefix, 'tasks')}[{index}]"
        _check_id(task.get("id"), "task", f"{location}.id", errors, task_ids)
        if task.get("status") not in {
            "planned",
            "in_progress",
            "complete",
            "completed",
            "done",
            "blocked",
            "stale",
        }:
            errors.append(
                f"{location}.status has unknown status {task.get('status')!r}"
            )
        requirements_for_task = _string_ids(
            task, "requirements", location, errors, required=True
        )
        criteria_for_task = _string_ids(
            task, "acceptance_criteria", location, errors, required=True
        )
        decisions_for_task = _string_ids(
            task, "architecture_decisions", location, errors
        )
        for requirement_id in requirements_for_task:
            if requirement_id not in requirement_ids:
                errors.append(
                    f"{location} references missing requirement {requirement_id}"
                )
        for criterion_id in criteria_for_task:
            if criterion_id not in criterion_ids:
                errors.append(
                    f"{location} references missing acceptance criterion {criterion_id}"
                )
        for decision_id in decisions_for_task:
            if decision_id not in architecture_ids:
                errors.append(
                    f"{location} references missing architecture decision {decision_id}"
                )
    _validate_task_dependency_cycles(tasks, task_ids, prefix, errors)

    implementation = state.get("implementation")
    implementation_status = _status(
        implementation,
        "status",
        _path(prefix, "implementation"),
        {"pending", "in_progress", "complete", "blocked", "stale"},
        errors,
    )
    implementation_revision = (
        implementation.get("revision") if isinstance(implementation, dict) else None
    )
    if implementation_status == "complete" and (
        not isinstance(implementation_revision, str)
        or not implementation_revision.strip()
    ):
        errors.append(
            f"{_path(prefix, 'implementation')}.revision must be non-empty text when complete"
        )
    implementation_evidence = _list_of_dicts(
        implementation.get("evidence") if isinstance(implementation, dict) else None,
        f"{_path(prefix, 'implementation')}.evidence",
        errors,
    )
    evidence_by_task: dict[str, list[dict[str, Any]]] = {}
    evidence_criteria: set[str] = set()
    for index, evidence in enumerate(implementation_evidence):
        location = f"{_path(prefix, 'implementation')}.evidence[{index}]"
        task_id = evidence.get("task_id")
        if task_id is not None and task_id not in task_ids:
            errors.append(f"{location}.task_id references missing task {task_id}")
        elif task_id is None and evidence.get("source") not in {"existing", "direct"}:
            errors.append(
                f"{location} without task_id must identify source: existing or direct"
            )
        if task_id is not None:
            evidence_by_task.setdefault(str(task_id), []).append(evidence)
        if evidence.get("spec_revision") != revision:
            errors.append(f"{location} records a stale specification revision")
        if (
            implementation_revision
            and evidence.get("implementation_revision") != implementation_revision
        ):
            errors.append(f"{location} records a stale implementation revision")
        evidence_status = evidence.get("status")
        if evidence_status not in {"pass", "partial", "fail", "blocked"}:
            errors.append(f"{location}.status must be pass, partial, fail, or blocked")
        refs = _string_ids(evidence, "acceptance_criteria", location, errors)
        is_current_passing_evidence = (
            evidence_status == "pass"
            and isinstance(implementation_revision, str)
            and bool(implementation_revision.strip())
            and evidence.get("spec_revision") == revision
            and evidence.get("implementation_revision") == implementation_revision
        )
        if is_current_passing_evidence:
            evidence_criteria.update(refs)
        for criterion_id in refs:
            if criterion_id not in criterion_ids:
                errors.append(
                    f"{location} references missing acceptance criterion {criterion_id}"
                )
        _validate_evidence_references(
            evidence,
            location,
            validation_evidence_ids,
            validation_evidence_by_id,
            revision,
            implementation_revision,
            set(refs),
            evidence_status == "pass",
            errors,
        )

    for index, task in enumerate(tasks):
        if task.get("status") in {"complete", "completed", "done"}:
            task_id = task.get("id")
            current_evidence = [
                entry
                for entry in evidence_by_task.get(str(task_id), [])
                if entry.get("status") == "pass"
                and entry.get("spec_revision") == revision
                and isinstance(implementation_revision, str)
                and bool(implementation_revision.strip())
                and entry.get("implementation_revision") == implementation_revision
            ]
            if not current_evidence:
                errors.append(
                    f"{_path(prefix, 'tasks')}[{index}] {task_id} is complete without current passing implementation evidence"
                )
                continue
            task_criteria = set(task.get("acceptance_criteria", []))
            covered_criteria = {
                criterion_id
                for entry in current_evidence
                for criterion_id in entry.get("acceptance_criteria", [])
            }
            uncovered_criteria = task_criteria - covered_criteria
            if uncovered_criteria:
                errors.append(
                    f"{_path(prefix, 'tasks')}[{index}] {task_id} has no passing implementation evidence for criteria: "
                    + ", ".join(sorted(uncovered_criteria))
                )

    qa = state.get("qa")
    qa_status = _status(
        qa,
        "status",
        _path(prefix, "qa"),
        {"not_required", "pending", "pass", "fail", "blocked", "stale"},
        errors,
    )
    qa_run_id = None
    qa_criteria: set[str] = set()
    if isinstance(qa, dict):
        if qa_status == "pass":
            qa_run_id = _check_id(
                qa.get("qa_run_id"),
                "QA run",
                f"{_path(prefix, 'qa')}.qa_run_id",
                errors,
            )
            if qa.get("spec_revision") != revision:
                errors.append(
                    f"{_path(prefix, 'qa')} records a stale specification revision"
                )
            if qa.get("implementation_revision") != implementation_revision:
                errors.append(
                    f"{_path(prefix, 'qa')} records a stale implementation revision"
                )
        qa_refs = _string_ids(qa, "acceptance_criteria", _path(prefix, "qa"), errors)
        qa_criteria.update(qa_refs)
        for criterion_id in qa_refs:
            if criterion_id not in criterion_ids:
                errors.append(
                    f"{_path(prefix, 'qa')} references missing acceptance criterion {criterion_id}"
                )
        _validate_evidence_references(
            qa,
            _path(prefix, "qa"),
            validation_evidence_ids,
            validation_evidence_by_id,
            revision,
            implementation_revision,
            set(qa_refs),
            qa_status == "pass",
            errors,
        )

    review = state.get("review")
    review_status = _status(
        review,
        "status",
        _path(prefix, "review"),
        {"not_required", "pending", "approve", "reject", "blocked", "stale"},
        errors,
    )
    if isinstance(review, dict):
        review_criteria = _string_ids(
            review, "acceptance_criteria", _path(prefix, "review"), errors
        )
        for criterion_id in review_criteria:
            if criterion_id not in criterion_ids:
                errors.append(
                    f"{_path(prefix, 'review')} references missing acceptance criterion {criterion_id}"
                )
        _validate_evidence_references(
            review,
            _path(prefix, "review"),
            validation_evidence_ids,
            validation_evidence_by_id,
            revision,
            implementation_revision,
            set(review_criteria),
            review_status == "approve",
            errors,
        )
    if isinstance(review, dict) and review_status == "approve":
        _check_id(
            review.get("review_id"),
            "review",
            f"{_path(prefix, 'review')}.review_id",
            errors,
        )
        if review.get("spec_revision") != revision:
            errors.append(
                f"{_path(prefix, 'review')} records a stale specification revision"
            )
        if review.get("implementation_revision") != implementation_revision:
            errors.append(
                f"{_path(prefix, 'review')} records a stale implementation revision"
            )
        if review.get("qa_run_id") != qa_run_id or qa_status != "pass":
            errors.append(
                f"{_path(prefix, 'review')} references a stale or non-passing QA run"
            )

    stale_artifacts = state.get("stale_artifacts", [])
    if not isinstance(stale_artifacts, list) or any(
        not isinstance(item, str) for item in stale_artifacts
    ):
        errors.append(
            f"{_path(prefix, 'stale_artifacts')} must be a list of artifact names"
        )
        stale_artifacts = []
    findings = state.get("open_findings", [])
    if not isinstance(findings, list):
        errors.append(f"{_path(prefix, 'open_findings')} must be a list")
    else:
        finding_ids: set[str] = set()
        for index, finding in enumerate(findings):
            if not isinstance(finding, dict) or "id" not in finding:
                continue
            _check_id(
                finding.get("id"),
                "defect",
                f"{_path(prefix, 'open_findings')}[{index}].id",
                errors,
                finding_ids,
            )

    convergence = state.get("convergence")
    convergence_status = _status(
        convergence,
        "status",
        _path(prefix, "convergence"),
        {"pending", "gaps_found", "converged"},
        errors,
    )
    if convergence_status == "converged":
        if spec_status != "ready":
            errors.append(
                "convergence cannot be converged unless the specification is ready"
            )
        if "architecture" in required_gates and architecture_status != "ready":
            errors.append("convergence requires the selected current architecture gate")
        if (
            "architecture" not in required_gates
            and architecture_status != "not_required"
        ):
            errors.append(
                "convergence requires unselected architecture to be not_required"
            )
        if "plan" in required_gates and plan_status != "ready":
            errors.append("convergence requires the selected current planning gate")
        if "plan" not in required_gates and plan_status != "not_required":
            errors.append("convergence requires unselected planning to be not_required")
        if "plan" in required_gates and any(
            task.get("status") not in {"complete", "completed", "done"}
            for task in tasks
        ):
            errors.append("convergence requires every task to be complete")
        if implementation_status != "complete":
            errors.append("convergence requires complete implementation")
        if "qa" in required_gates and qa_status != "pass":
            errors.append("convergence requires a passing QA run")
        if "qa" not in required_gates and qa_status != "not_required":
            errors.append("convergence requires unselected QA to be not_required")
        if "review" in required_gates and review_status != "approve":
            errors.append("convergence requires Reviewer approval")
        if "review" not in required_gates and review_status != "not_required":
            errors.append("convergence requires unselected Review to be not_required")
        if stale_artifacts:
            errors.append(
                f"convergence cannot include stale artifacts: {', '.join(stale_artifacts)}"
            )
        if _has_required_open_decision(specification):
            errors.append(
                "convergence cannot include unresolved required open decisions"
            )
        blockers = _blocking_findings(state)
        if blockers:
            errors.append(
                f"convergence cannot include blocking findings: {', '.join(blockers)}"
            )
        unrequested = state.get("unrequested_material_changes", [])
        if unrequested:
            errors.append("convergence cannot include unrequested material changes")
        covered_requirements = {
            requirement_id
            for refs in criterion_requirements.values()
            for requirement_id in refs
        }
        for requirement_id in requirement_ids - covered_requirements:
            errors.append(
                f"convergence has no acceptance criterion for {requirement_id}"
            )
        planned_criteria = {
            criterion_id
            for task in tasks
            for criterion_id in task.get("acceptance_criteria", [])
        }
        existing_criteria = {
            criterion.get("id")
            for criterion in criteria
            if criterion.get("existing_behavior") is True
            and isinstance(criterion.get("existing_evidence"), str)
            and criterion["existing_evidence"].strip()
        }
        if "plan" in required_gates:
            for criterion_id in criterion_ids - planned_criteria - existing_criteria:
                errors.append(
                    f"convergence has no planned task or existing-behavior evidence for {criterion_id}"
                )
        for criterion_id in existing_criteria:
            if criterion_id not in evidence_criteria:
                errors.append(
                    f"convergence has no implementation evidence for existing behavior {criterion_id}"
                )
        for criterion_id in criterion_ids - evidence_criteria:
            errors.append(
                f"convergence has no implementation evidence for {criterion_id}"
            )
        if "qa" in required_gates:
            for criterion_id in criterion_ids - qa_criteria:
                errors.append(f"convergence has no QA evidence for {criterion_id}")

    if spec_id is None:
        return errors
    return errors


def propagate_staleness(payload: Any, changed_artifact: str) -> dict[str, Any]:
    """Return a copy with every downstream artifact marked stale."""
    if changed_artifact not in INVALIDATION_GRAPH:
        choices = ", ".join(sorted(INVALIDATION_GRAPH))
        raise ValueError(f"changed_artifact must be one of: {choices}")
    if not isinstance(payload, dict):
        raise TypeError("state must be an object")
    updated = copy.deepcopy(payload)
    state, _ = _manifest(updated)
    if state is None:
        raise ValueError("manifest must be an object")

    stale = state.get("stale_artifacts", [])
    if not isinstance(stale, list) or any(not isinstance(item, str) for item in stale):
        raise ValueError("stale_artifacts must be a list of artifact names")
    for artifact in INVALIDATION_GRAPH[changed_artifact]:
        if (
            artifact == "architecture"
            and isinstance(state.get(artifact), dict)
            and state[artifact].get("status") == "not_required"
        ):
            continue
        value = state.get(artifact)
        if artifact == "tasks" and isinstance(value, list):
            for task in value:
                if isinstance(task, dict):
                    task["status"] = "stale"
        elif isinstance(value, dict):
            value["status"] = "stale"
        else:
            state[artifact] = {"status": "stale"} if artifact != "tasks" else []
        if artifact not in stale:
            stale.append(artifact)
    state["stale_artifacts"] = sorted(set(stale))
    if isinstance(state.get("convergence"), dict):
        state["convergence"]["status"] = "pending"
    return updated


def coverage_matrix(payload: Any) -> dict[str, Any]:
    """Build requirement-to-acceptance/task/implementation/QA coverage."""
    errors = validate_state(payload)
    if errors:
        raise ValueError(
            "cannot build coverage from invalid SDD state: " + "; ".join(errors)
        )
    state, _ = _manifest(payload)
    if state is None:
        raise ValueError("state must be an object or contain an object manifest")
    specification = state.get("specification", {})
    requirements = (
        specification.get("requirements", []) if isinstance(specification, dict) else []
    )
    criteria = (
        specification.get("acceptance_criteria", [])
        if isinstance(specification, dict)
        else []
    )
    tasks = state.get("tasks", [])
    implementation = state.get("implementation", {})
    implementation_evidence = (
        implementation.get("evidence", []) if isinstance(implementation, dict) else []
    )
    qa = state.get("qa", {})
    if not isinstance(qa, dict):
        qa = {}
    review = state.get("review", {})
    if not isinstance(review, dict):
        review = {}
    qa_criteria = (
        set(qa.get("acceptance_criteria", [])) if isinstance(qa, dict) else set()
    )

    criterion_to_tasks: dict[str, set[str]] = {}
    for task in tasks if isinstance(tasks, list) else []:
        if not isinstance(task, dict):
            continue
        for criterion_id in task.get("acceptance_criteria", []):
            criterion_to_tasks.setdefault(criterion_id, set()).add(task.get("id", ""))

    implementation_revision = (
        implementation.get("revision") if isinstance(implementation, dict) else None
    )
    specification_revision = (
        specification.get("revision") if isinstance(specification, dict) else None
    )
    implementation_criteria = {
        criterion_id
        for evidence in implementation_evidence
        if isinstance(evidence, dict)
        and evidence.get("status") == "pass"
        and evidence.get("spec_revision") == specification_revision
        and isinstance(implementation_revision, str)
        and bool(implementation_revision.strip())
        and evidence.get("implementation_revision") == implementation_revision
        for criterion_id in evidence.get("acceptance_criteria", [])
    }

    matrix: dict[str, Any] = {}
    for requirement in requirements if isinstance(requirements, list) else []:
        if not isinstance(requirement, dict):
            continue
        requirement_id = requirement.get("id")
        related_criteria = [
            criterion
            for criterion in criteria
            if isinstance(criterion, dict)
            and requirement_id in criterion.get("requirements", [])
        ]
        criterion_ids = [criterion.get("id") for criterion in related_criteria]
        related_tasks = sorted(
            {
                task_id
                for criterion_id in criterion_ids
                for task_id in criterion_to_tasks.get(criterion_id, set())
                if task_id
            }
        )
        matrix[requirement_id] = {
            "acceptance_criteria": criterion_ids,
            "tasks": related_tasks,
            "implementation_evidence": sorted(
                set(criterion_ids) & implementation_criteria
            ),
            "qa_status": (
                "pass"
                if criterion_ids
                and set(criterion_ids).issubset(qa_criteria)
                and qa.get("status") == "pass"
                else "uncovered"
                if qa.get("status") == "pass"
                else qa.get("status", "pending")
            ),
            "qa_run_id": qa.get("qa_run_id"),
            "review_status": review.get("status", "pending"),
            "review_id": review.get("review_id"),
            "existing_behavior": all(
                criterion.get("existing_behavior") is True
                for criterion in related_criteria
            ),
        }
    return {
        "specification_id": specification.get("id"),
        "specification_revision": specification.get("revision"),
        "risk_level": state.get("risk_level"),
        "required_gates": sorted(state.get("required_gates", LEGACY_REQUIRED_GATES)),
        "review_status": review.get("status", "pending"),
        "review_id": review.get("review_id"),
        "requirements": matrix,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a supplied SDD task-state exchange artifact without modifying it."
    )
    parser.add_argument(
        "state_file", type=Path, help="supplied task-state or manifest JSON artifact"
    )
    parser.add_argument(
        "--invalidate",
        choices=sorted(INVALIDATION_GRAPH),
        help="return a copy with artifacts downstream of this source marked stale",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="emit the requirement-to-evidence coverage matrix",
    )
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.state_file.read_text(encoding="utf-8"))
        if args.invalidate:
            payload = propagate_staleness(payload, args.invalidate)
            rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
            sys.stdout.write(rendered)
            return 0
        errors = validate_state(payload)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        if args.coverage:
            print(json.dumps(coverage_matrix(payload), indent=2, sort_keys=True))
        else:
            print("SDD state valid")
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
