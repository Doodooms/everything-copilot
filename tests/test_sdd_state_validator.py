import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
VALIDATOR_PATH = (
    ROOT
    / "agentic-core/skills/orchestration/references/spec-driven-development/scripts/validate_sdd_state.py"
)


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "sdd_state_validator_test", VALIDATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load SDD validator at {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SddStateValidatorTests(unittest.TestCase):
    def test_validator_is_packaged_as_a_self_contained_script(self):
        self.assertTrue(
            VALIDATOR_PATH.is_file(),
            "spec-driven-development must package its deterministic state validator",
        )

    def test_relative_script_path_works_from_source_and_installed_skill_roots(self):
        with TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            workspace = temporary_root / "workspace"
            workspace.mkdir()
            state_file = workspace / "task-state.json"
            state_file.write_text(json.dumps(self.state), encoding="utf-8")

            source_skill_root = VALIDATOR_PATH.parents[1]
            installed_plugin_root = temporary_root / "installed-plugin"
            installed_plugin_root.mkdir()
            shutil.copy2(ROOT / "agentic-core/plugin.json", installed_plugin_root / "plugin.json")
            installed_skill_root = (
                installed_plugin_root
                / "skills"
                / "orchestration"
                / "references"
                / "spec-driven-development"
            )
            installed_scripts = installed_skill_root / "scripts"
            installed_scripts.mkdir(parents=True)
            shutil.copy2(VALIDATOR_PATH, installed_scripts / "validate_sdd_state.py")
            self.assertNotIn(ROOT, installed_skill_root.parents)

            environment = dict(os.environ)
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            for skill_root in (source_skill_root, installed_skill_root):
                with self.subTest(skill_root=skill_root):
                    result = subprocess.run(
                        [
                            sys.executable,
                            "scripts/validate_sdd_state.py",
                            str(state_file),
                        ],
                        cwd=skill_root,
                        capture_output=True,
                        text=True,
                        check=False,
                        env=environment,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("SDD state valid", result.stdout)

    def setUp(self):
        self.validator = load_validator()
        self.state = {
            "specification": {
                "id": "SPEC-001",
                "revision": 1,
                "status": "ready",
                "objective": "Allow authorized guests to read projects.",
                "requirements": [
                    {"id": "REQ-001", "statement": "Guests can read projects."}
                ],
                "acceptance_criteria": [
                    {
                        "id": "AC-001",
                        "requirements": ["REQ-001"],
                        "statement": "A guest can read an authorized project.",
                    }
                ],
                "constraints": [],
                "non_goals": [],
                "open_decisions": [],
            },
            "architecture": {
                "status": "not_required",
                "revision": None,
                "spec_revision": 1,
                "decisions": [],
            },
            "plan": {"status": "ready", "revision": 1, "spec_revision": 1},
            "tasks": [
                {
                    "id": "TASK-001",
                    "status": "complete",
                    "requirements": ["REQ-001"],
                    "acceptance_criteria": ["AC-001"],
                    "architecture_decisions": [],
                    "depends_on": [],
                }
            ],
            "implementation": {
                "status": "complete",
                "revision": "commit-impl-1",
                "evidence": [
                    {
                        "task_id": "TASK-001",
                        "spec_revision": 1,
                        "implementation_revision": "commit-impl-1",
                        "status": "pass",
                        "acceptance_criteria": ["AC-001"],
                    }
                ],
            },
            "qa": {
                "status": "pass",
                "qa_run_id": "QA-RUN-001",
                "spec_revision": 1,
                "implementation_revision": "commit-impl-1",
                "acceptance_criteria": ["AC-001"],
            },
            "review": {
                "status": "approve",
                "review_id": "REVIEW-001",
                "spec_revision": 1,
                "implementation_revision": "commit-impl-1",
                "qa_run_id": "QA-RUN-001",
            },
            "convergence": {"status": "converged"},
            "open_findings": [],
            "stale_artifacts": [],
        }

    def test_accepts_a_fully_traced_converged_state(self):
        self.assertEqual([], self.validator.validate_state(self.state))

    def test_validates_sparse_semantic_model_and_reusable_evidence(self):
        self.state["specification"]["semantic_model"] = {
            "schema_version": 1,
            "scope": "Project subscription lifecycle",
            "terminology": [
                {
                    "term": "Subscription",
                    "meaning": "A customer's current service agreement.",
                    "aliases": ["plan enrollment"],
                }
            ],
            "concepts": [
                {
                    "id": "CONCEPT-001",
                    "term": "Subscription",
                    "kind": "entity",
                    "meaning": "A customer's service agreement.",
                    "identity": "Stable subscription ID.",
                    "granularity": "One agreement, independent of its billing periods.",
                },
                {
                    "id": "CONCEPT-002",
                    "term": "AnnualSubscription",
                    "kind": "entity",
                    "meaning": "A subscription billed annually.",
                }
            ],
            "relations": [
                {
                    "id": "REL-001",
                    "source_concept": "CONCEPT-002",
                    "predicate": "is-a",
                    "target_concept": "CONCEPT-001",
                    "meaning": "An annual subscription is a kind of subscription.",
                }
            ],
            "states": [
                {
                    "id": "STATE-001",
                    "concept_id": "CONCEPT-001",
                    "name": "active",
                },
                {
                    "id": "STATE-002",
                    "concept_id": "CONCEPT-001",
                    "name": "cancelled",
                },
            ],
            "events": [{"id": "EVENT-001", "name": "cancellation accepted"}],
            "transitions": [
                {
                    "id": "TRANSITION-001",
                    "concept_id": "CONCEPT-001",
                    "from_state_id": "STATE-001",
                    "event_id": "EVENT-001",
                    "to_state_id": "STATE-002",
                }
            ],
            "invariants": [
                {
                    "id": "INV-001",
                    "statement": "A cancelled subscription cannot be active.",
                    "concept_ids": ["CONCEPT-001"],
                }
            ],
            "hypotheses": [
                {
                    "id": "HYPOTHESIS-001",
                    "statement": "Cancellation disables the next renewal.",
                    "source": "Inferred from the requested cancellation behavior.",
                }
            ],
        }
        self.state["specification"]["requirements"][0]["semantic_refs"] = [
            "CONCEPT-001",
            "INV-001",
        ]
        self.state["specification"]["acceptance_criteria"][0]["semantic_refs"] = [
            "TRANSITION-001",
            "HYPOTHESIS-001",
        ]
        self.state["validation_evidence"] = [
            {
                "id": "EVIDENCE-001",
                "check": "targeted permission test",
                "command": "pytest tests/test_permissions.py",
                "subject_revision": "commit-impl-1",
                "environment": "Linux, Python 3.12",
                "result": "pass",
                "producer": "implementer",
                "spec_revision": 1,
                "acceptance_criteria": ["AC-001"],
            }
        ]
        self.state["implementation"]["evidence"][0][
            "validation_evidence_refs"
        ] = ["EVIDENCE-001"]
        self.state["qa"]["validation_evidence_refs"] = ["EVIDENCE-001"]
        self.state["review"]["validation_evidence_refs"] = ["EVIDENCE-001"]

        self.assertEqual([], self.validator.validate_state(self.state))

    def test_rejects_malformed_semantic_hypothesis(self):
        self.state["specification"]["semantic_model"] = {
            "schema_version": 1,
            "scope": "Bounded domain",
            "hypotheses": [
                {
                    "id": "ASSUMPTION-001",
                    "statement": "An unconfirmed semantic proposition.",
                }
            ],
        }

        errors = self.validator.validate_state(self.state)

        self.assertTrue(
            any("semantic hypothesis ID format" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("hypotheses[0].source must be non-empty text" in error for error in errors),
            errors,
        )

    def test_rejects_semantic_alias_conflicts_and_dangling_references(self):
        self.state["specification"]["semantic_model"] = {
            "schema_version": 1,
            "scope": "Bounded domain",
            "terminology": [
                {"term": "Subscription", "meaning": "A service agreement.", "aliases": ["plan"]},
                {"term": "Plan", "meaning": "A billing option.", "aliases": ["subscription"]},
            ],
            "concepts": [
                {
                    "id": "CONCEPT-001",
                    "term": "Subscription",
                    "kind": "entity",
                    "meaning": "A service agreement.",
                }
            ],
            "relations": [
                {
                    "id": "REL-001",
                    "source_concept": "CONCEPT-001",
                    "predicate": "includes",
                    "target_concept": "CONCEPT-999",
                }
            ],
        }
        self.state["specification"]["requirements"][0]["semantic_refs"] = [
            "CONCEPT-404"
        ]

        errors = self.validator.validate_state(self.state)

        self.assertTrue(any("alias" in error.lower() and "conflict" in error.lower() for error in errors), errors)
        self.assertTrue(any("missing concept CONCEPT-999" in error for error in errors), errors)
        self.assertTrue(any("missing semantic item CONCEPT-404" in error for error in errors), errors)

    def test_accepts_l0_convergence_without_unselected_planning_qa_or_review(self):
        self.state.update(
            {
                "risk_level": "L0",
                "required_gates": ["implementation"],
                "architecture": {
                    "status": "not_required",
                    "revision": None,
                    "spec_revision": 1,
                    "decisions": [],
                },
                "plan": {"status": "not_required", "revision": None, "spec_revision": 1},
                "tasks": [],
                "implementation": {
                    "status": "complete",
                    "revision": "commit-impl-1",
                    "evidence": [
                        {
                            "source": "direct",
                            "spec_revision": 1,
                            "implementation_revision": "commit-impl-1",
                            "status": "pass",
                            "acceptance_criteria": ["AC-001"],
                        }
                    ],
                },
                "qa": {"status": "not_required"},
                "review": {"status": "not_required"},
            }
        )

        self.assertEqual([], self.validator.validate_state(self.state))

    def test_rejects_review_without_qa_and_stale_reused_validation_evidence(self):
        self.state["risk_level"] = "L2"
        self.state["required_gates"] = ["implementation", "review"]
        self.state["validation_evidence"] = [
            {
                "id": "EVIDENCE-001",
                "check": "unit tests",
                "subject_revision": "commit-impl-old",
                "environment": "Linux",
                "result": "pass",
                "producer": "implementer",
            }
        ]
        self.state["implementation"]["evidence"][0][
            "validation_evidence_refs"
        ] = ["EVIDENCE-001"]

        errors = self.validator.validate_state(self.state)

        self.assertTrue(
            any("must include QA" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("stale implementation revision" in error for error in errors),
            errors,
        )

    def test_rejects_duplicate_ids_and_dangling_acceptance_references(self):
        self.state["specification"]["requirements"].append(
            {"id": "REQ-001", "statement": "duplicate"}
        )
        self.state["specification"]["acceptance_criteria"][0]["requirements"] = [
            "REQ-999"
        ]

        errors = self.validator.validate_state(self.state)

        self.assertTrue(any("duplicate ID REQ-001" in error for error in errors), errors)
        self.assertTrue(any("REQ-999" in error for error in errors), errors)

    def test_rejects_tasks_with_missing_references_or_dependency_cycles(self):
        self.state["tasks"][0]["requirements"] = ["REQ-404"]
        self.state["tasks"][0]["depends_on"] = ["TASK-002"]
        self.state["tasks"].append(
            {
                "id": "TASK-002",
                "status": "planned",
                "requirements": ["REQ-001"],
                "acceptance_criteria": ["AC-001"],
                "architecture_decisions": [],
                "depends_on": ["TASK-001"],
            }
        )
        self.state["tasks"][0]["depends_on"] = ["TASK-002"]

        errors = self.validator.validate_state(self.state)

        self.assertTrue(any("REQ-404" in error for error in errors), errors)
        self.assertTrue(any("cycle" in error.lower() for error in errors), errors)

    def test_rejects_completed_tasks_without_current_implementation_evidence(self):
        self.state["implementation"]["evidence"] = []

        errors = self.validator.validate_state(self.state)

        self.assertTrue(any("TASK-001" in error and "evidence" in error for error in errors), errors)

    def test_rejects_qa_and_review_evidence_from_stale_revisions(self):
        self.state["qa"]["implementation_revision"] = "commit-impl-old"
        self.state["review"]["qa_run_id"] = "QA-RUN-OLD"

        errors = self.validator.validate_state(self.state)

        self.assertTrue(
            any("qa" in error.lower() and "implementation revision" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("review" in error.lower() and "qa run" in error.lower() for error in errors),
            errors,
        )

    def test_rejects_false_convergence_with_open_blockers_or_stale_artifacts(self):
        self.state["open_findings"] = [{"id": "DEFECT-001", "blocking": True}]
        self.state["stale_artifacts"] = ["plan"]

        errors = self.validator.validate_state(self.state)

        self.assertTrue(any("blocking" in error for error in errors), errors)
        self.assertTrue(any("stale" in error.lower() for error in errors), errors)

    def test_rejects_unresolved_required_decisions_and_unplanned_criteria(self):
        self.state["specification"]["open_decisions"] = [
            {"required": True, "resolved": False}
        ]
        self.state["tasks"][0]["acceptance_criteria"] = []

        errors = self.validator.validate_state(self.state)

        self.assertTrue(
            any("unresolved required open decisions" in error for error in errors),
            errors,
        )
        self.assertTrue(any("no planned task" in error for error in errors), errors)

    def test_rejects_unknown_task_status_and_malformed_stale_artifact_list(self):
        self.state["tasks"][0]["status"] = "probably_done"
        self.state["stale_artifacts"] = "plan"

        errors = self.validator.validate_state(self.state)

        self.assertTrue(any("unknown status" in error.lower() for error in errors), errors)
        self.assertTrue(any("stale_artifacts must be a list" in error for error in errors), errors)

    def test_rejects_ready_specification_without_criteria_for_each_requirement(self):
        self.state["specification"]["acceptance_criteria"] = []

        errors = self.validator.validate_state(self.state)

        self.assertTrue(
            any("acceptance_criteria must not be empty" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("no acceptance criterion linked to REQ-001" in error for error in errors),
            errors,
        )

    def test_accepts_existing_behavior_with_explicit_current_evidence(self):
        self.state["tasks"] = []
        self.state["specification"]["acceptance_criteria"][0].update(
            {"existing_behavior": True, "existing_evidence": "Existing permission check."}
        )
        self.state["implementation"]["evidence"] = [
            {
                "source": "existing",
                "spec_revision": 1,
                "implementation_revision": "commit-impl-1",
                "status": "pass",
                "acceptance_criteria": ["AC-001"],
            }
        ]

        self.assertEqual([], self.validator.validate_state(self.state))

    def test_propagates_spec_revision_staleness_without_mutating_input(self):
        updated = self.validator.propagate_staleness(self.state, "specification")

        self.assertEqual([], self.state["stale_artifacts"])
        self.assertEqual(
            {"plan", "tasks", "implementation", "qa", "review"},
            set(updated["stale_artifacts"]),
        )
        self.assertEqual("stale", updated["plan"]["status"])
        self.assertEqual("stale", updated["qa"]["status"])
        self.assertEqual("not_required", updated["architecture"]["status"])

    def test_coverage_matrix_traces_requirements_through_qa(self):
        matrix = self.validator.coverage_matrix(self.state)

        self.assertEqual(["AC-001"], matrix["requirements"]["REQ-001"]["acceptance_criteria"])
        self.assertEqual(["TASK-001"], matrix["requirements"]["REQ-001"]["tasks"])
        self.assertEqual("pass", matrix["requirements"]["REQ-001"]["qa_status"])
        self.assertEqual("approve", matrix["requirements"]["REQ-001"]["review_status"])

    def test_composed_workflow_mermaid_graphs_are_named_dags(self):
        reference_paths = [
            ROOT
            / "agentic-core/skills/plugin-engineering/references/create-skill/references/skill-composition.md",
            *(
                ROOT
                / "agentic-core/skills/orchestration/references/spec-driven-development/references"
            ).glob("*.md"),
        ]
        graph_count = 0
        for path in reference_paths:
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r"```mermaid\n(.*?)\n```", text, re.DOTALL):
                graph_count += 1
                self.assertRegex(
                    text[: match.start()], r"(?m)^## use_case:\s+[a-z0-9_]+\s*$"
                )
                edges = []
                for line in match.group(1).splitlines():
                    if "-->" not in line:
                        continue
                    parts = line.split("-->")
                    nodes = []
                    for part in parts:
                        part = re.sub(r"^\|[^|]*\|", "", part.strip()).strip()
                        node = re.match(r"([A-Za-z][A-Za-z0-9_]*)", part)
                        self.assertIsNotNone(node, f"unparseable Mermaid edge: {line}")
                        nodes.append(node.group(1))
                    edges.extend(zip(nodes, nodes[1:]))
                adjacency = {}
                for source, target in edges:
                    adjacency.setdefault(source, set()).add(target)
                visiting = set()
                visited = set()

                def visit(node):
                    if node in visiting:
                        return False
                    if node in visited:
                        return True
                    visiting.add(node)
                    if any(not visit(child) for child in adjacency.get(node, ())):
                        return False
                    visiting.remove(node)
                    visited.add(node)
                    return True

                self.assertTrue(
                    all(visit(node) for node in adjacency),
                    f"{path} contains a cyclic execution graph",
                )
        self.assertGreaterEqual(graph_count, 4)

    def test_cli_invalidation_is_non_mutating_without_write_flag(self):
        with TemporaryDirectory() as directory:
            state_file = Path(directory) / "task.json"
            wrapped_state = {"task_id": "task_1", "manifest": self.state}
            original = json.dumps(wrapped_state, sort_keys=True)
            state_file.write_text(original, encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR_PATH),
                    str(state_file),
                    "--invalidate",
                    "specification",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(original, state_file.read_text(encoding="utf-8"))
            invalidated = json.loads(result.stdout)
            self.assertIn("plan", invalidated["manifest"]["stale_artifacts"])
            self.assertEqual(
                "pending", invalidated["manifest"]["convergence"]["status"]
            )


if __name__ == "__main__":
    unittest.main()
