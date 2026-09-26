import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LINTER_PATH = (
    ROOT
    / "agentic-core/skills/plugin-engineering/references/create-skill/scripts/skill_lint_core.py"
)
SPEC = importlib.util.spec_from_file_location("skill_workflow_lint_core_test", LINTER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load skill linter at {LINTER_PATH}")
LINTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = LINTER
SPEC.loader.exec_module(LINTER)


class SkillWorkflowLinterTests(unittest.TestCase):
    def write_workflow(
        self,
        skill_dir: Path,
        filename: str = "concurrency.md",
        *,
        workflow_id: str = "concurrency",
        references: tuple[str, ...] = ("../references/concurrency-oracle.md",),
        body: str = "[oracle](../references/concurrency-oracle.md)\n",
    ) -> Path:
        workflows_dir = skill_dir / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        workflow = workflows_dir / filename
        workflow.write_text(
            "---\n"
            f"id: {workflow_id}\n"
            "description: Design checks for concurrent state transitions.\n"
            "invoke_for:\n"
            "  - shared mutable state\n"
            "avoid_for:\n"
            "  - purely sequential behavior\n"
            "references:\n"
            + "".join(f"  - {reference}\n" for reference in references)
            + "---\n"
            "## Falsify concurrent behavior\n"
            "1. Derive an observable concurrency contract.\n"
            f"{body}",
            encoding="utf-8",
        )
        return workflow

    def test_requires_separate_critical_general_and_risk_sections(self):
        skill_text = """---
name: demo
description: Demo workflow.
---
<rules>
- Preserve behavior.
</rules>
<workflow>
## Step 1 - Select.
1. Read the request.
## Step 2 - Act.
1. Complete the scoped method.
## Step 3 - Return.
1. Report evidence.
</workflow>
"""
        result = LINTER.lint_skill_markdown(Path("demo"), skill_text)

        self.assertTrue(
            any("`<critical_rules>` and `</critical_rules>`" in error for error in result.errors),
            result.errors,
        )

    def test_risk_section_must_be_applied_by_step_one(self):
        skill_text = """---
name: demo
description: Demo workflow.
---
<critical_rules>
- MUST preserve the approved scope.
</critical_rules>
<general_rules>
- SHOULD use the smallest sufficient method.
</general_rules>
<risk_assessment>
Consume the assigned `risk_level`; MUST NOT downgrade it. SHOULD escalate only when evidence warrants it.
</risk_assessment>
<rules>
- Preserve behavior.
</rules>
<workflow>
## Step 1 - Select.
1. Read the request.
## Step 2 - Act.
1. Complete the scoped method.
## Step 3 - Return.
1. Report evidence.
</workflow>
"""
        result = LINTER.lint_skill_markdown(Path("demo"), skill_text)

        self.assertIn(
            "`<workflow>` Step 1 must consume or assign risk before substantive work.",
            result.errors,
        )

    def test_validates_one_level_workflow_metadata_and_point_of_need_references(self):
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "testing"
            workflow = self.write_workflow(skill_dir)
            (skill_dir / "references").mkdir()
            (skill_dir / "references/concurrency-oracle.md").write_text(
                "An oracle for ordering-sensitive behavior.\n", encoding="utf-8"
            )

            result = LINTER.validate_skill_workflows(skill_dir)
            self.assertTrue(workflow.is_file())

        self.assertEqual(result.errors, [])
        self.assertEqual(
            result.data["workflows"],
            [
                {
                    "path": "workflows/concurrency.md",
                    "references": ["references/concurrency-oracle.md"],
                    "linked_paths": ["references/concurrency-oracle.md"],
                    "markdown_linked_paths": ["references/concurrency-oracle.md"],
                    "file_references": [],
                }
            ],
        )

    def test_rejects_nested_procedure_metadata_and_reference_workflows(self):
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "testing"
            workflow = self.write_workflow(skill_dir)
            workflow_text = workflow.read_text(encoding="utf-8").replace(
                "references:\n  - ../references/concurrency-oracle.md\n",
                "references:\n  - ../references/concurrency-oracle.md\n"
                "subskills:\n  - ../references/create-tdd/method-source.md\n",
            )
            workflow.write_text(workflow_text, encoding="utf-8")
            nested = skill_dir / "references/create-tdd/workflows"
            nested.mkdir(parents=True)
            (nested / "execute.md").write_text(
                "# Execute\nFollow the test-first loop.\n", encoding="utf-8"
            )
            (skill_dir / "references/concurrency-oracle.md").write_text(
                "An oracle for ordering-sensitive behavior.\n", encoding="utf-8"
            )

            result = LINTER.validate_skill_workflows(skill_dir)

        self.assertTrue(
            any("unknown workflow metadata field(s): subskills" in error for error in result.errors),
            result.errors,
        )
        self.assertTrue(
            any("nested workflow directory found" in error for error in result.errors),
            result.errors,
        )

    def test_follows_top_level_workflow_references_transitively(self):
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "testing"
            self.write_workflow(
                skill_dir,
                references=("../references/guidance.md",),
                body="[guidance](../references/guidance.md)\n",
            )
            references_dir = skill_dir / "references"
            references_dir.mkdir()
            (references_dir / "guidance.md").write_text(
                "Consult the [detail](./detail.md) only "
                "when maintaining this package.\n",
                encoding="utf-8",
            )
            (references_dir / "detail.md").write_text(
                "Supporting knowledge.\n",
                encoding="utf-8",
            )
            skill_text = """---
name: testing
description: Test engineering methods.
---
<critical_rules>
- MUST preserve the approved behavior.
</critical_rules>
<general_rules>
- SHOULD use the smallest sufficient method.
</general_rules>
<risk_assessment>
Consume the assigned `risk_level`; MUST NOT downgrade it. SHOULD escalate only when evidence warrants it.
</risk_assessment>
<rules>
- Preserve observable behavior and report actual evidence.
</rules>
<workflow>
## Step 1 - Select.
1. Consume the assigned `risk_level` before choosing a procedure.
2. Route matching work to [concurrency](./workflows/concurrency.md).
## Step 2 - Apply.
1. Follow the selected method.
## Step 3 - Return.
1. Report evidence and residual risk.
</workflow>
"""

            result = LINTER.lint_skill_markdown(skill_dir, skill_text)

        self.assertEqual(result.errors, [], result.errors)
        self.assertFalse(
            any(
                "./references/detail.md" in warning
                for warning in result.warnings
            ),
            result.warnings,
        )

    def test_concurrency_test_design_is_directly_in_the_immediate_workflow(self):
        skill_dir = ROOT / "agentic-core/skills/quality-engineering"
        workflow_path = skill_dir / "workflows/test-design.md"

        result = LINTER.validate_skill_workflows(skill_dir)
        metadata, _ = LINTER.split_frontmatter(
            workflow_path.read_text(encoding="utf-8")
        )
        test_design_method = workflow_path.read_text(encoding="utf-8")

        self.assertEqual(result.errors, [])
        self.assertNotIn("subskills", metadata)
        self.assertIn("shared mutable state or concurrent writers", test_design_method)
        self.assertIn("deterministic barriers", test_design_method)

    def test_follows_reference_metadata_in_transitive_knowledge_files(self):
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "testing"
            workflows = skill_dir / "workflows"
            reference_dir = skill_dir / "references/guides"
            assets = skill_dir / "assets"
            workflows.mkdir(parents=True)
            reference_dir.mkdir(parents=True)
            assets.mkdir(parents=True)

            (workflows / "testing.md").write_text(
                "---\n"
                "id: testing\n"
                "description: Apply a focused test method.\n"
                "invoke_for:\n"
                "  - behavior changes\n"
                "avoid_for:\n"
                "  - pure research\n"
                "references:\n"
                "  - ../references/guides/testing.md\n"
                "---\n"
                "Load [supporting guidance](../references/guides/testing.md).\n",
                encoding="utf-8",
            )
            (reference_dir / "testing.md").write_text(
                "---\n"
                "references:\n"
                "  - ./details.md\n"
                "---\n"
                "Supporting [detail](./details.md) and [configuration](../../assets/config.json).\n",
                encoding="utf-8",
            )
            (reference_dir / "details.md").write_text(
                "Knowledge only; no procedure is routed from this file.\n",
                encoding="utf-8",
            )
            (assets / "config.json").write_text('{"strict":true}\n', encoding="utf-8")
            skill_text = """---
name: testing
description: Test engineering methods.
---
<critical_rules>
- MUST validate selected behavior with evidence.
</critical_rules>
<general_rules>
- SHOULD use the smallest useful test method.
</general_rules>
<risk_assessment>
Consume the assigned `risk_level`; MUST NOT downgrade it. SHOULD escalate only when evidence warrants it.
</risk_assessment>
<rules>
- Preserve observable behavior and report actual test evidence.
</rules>
<workflow>
## Step 1 - Assess and select.
1. Consume the assigned `risk_level` before substantive work.
2. Route behavior changes to [testing](./workflows/testing.md).
## Step 2 - Execute.
1. Apply the selected method and preserve the observed evidence.
## Step 3 - Return.
1. Report evidence, gaps, and residual risk.
</workflow>
"""
            (skill_dir / "SKILL.md").write_text(skill_text, encoding="utf-8")

            result = LINTER.lint_skill_markdown(skill_dir, skill_text)

        self.assertEqual([], result.errors, result.errors)
        self.assertFalse(
            any("Support file is not referenced" in warning for warning in result.warnings),
            result.warnings,
        )

    def test_ignores_file_markers_inside_referenced_code_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "testing"
            (skill_dir / "references/scripts").mkdir(parents=True)
            (skill_dir / "references/concurrency-oracle.md").write_text(
                "An oracle for ordering-sensitive behavior.\n",
                encoding="utf-8",
            )
            (skill_dir / "references/scripts/validator.py").write_text(
                'FILE_PATTERN = r"#file:\\s*([^\\s`]+)"\n',
                encoding="utf-8",
            )
            self.write_workflow(
                skill_dir,
                references=("../references/scripts/validator.py",),
            )
            skill_text = """---
name: testing
description: Test engineering methods.
---
<critical_rules>
- MUST preserve the approved behavior.
</critical_rules>
<general_rules>
- SHOULD use the smallest useful test method.
</general_rules>
<risk_assessment>
Consume the assigned `risk_level`; MUST NOT downgrade it. SHOULD escalate only when evidence warrants it.
</risk_assessment>
<rules>
- Preserve observable behavior and report actual test evidence.
</rules>
<workflow>
## Step 1 - Select.
1. Consume the assigned `risk_level` and route to [concurrency](./workflows/concurrency.md).
## Step 2 - Apply.
1. Follow the selected method.
## Step 3 - Return.
1. Report evidence and residual risk.
</workflow>
"""

            result = LINTER.lint_skill_markdown(skill_dir, skill_text)

        self.assertEqual(result.errors, [], result.errors)

    def test_rejects_duplicate_ids_and_filename_mismatches(self):
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "testing"
            self.write_workflow(skill_dir, "first.md", workflow_id="same")
            self.write_workflow(skill_dir, "second.md", workflow_id="same")

            result = LINTER.validate_skill_workflows(skill_dir)

        self.assertTrue(
            any("duplicate workflow id `same`" in error for error in result.errors),
            result.errors,
        )
        self.assertTrue(
            any("must match the workflow filename stem" in error for error in result.errors),
            result.errors,
        )

    def test_rejects_missing_and_out_of_package_references(self):
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "testing"
            self.write_workflow(
                skill_dir,
                references=(
                    "../references/missing.md",
                    "../../outside.md",
                ),
            )

            result = LINTER.validate_skill_workflows(skill_dir)

        self.assertTrue(
            any("is not a file" in error for error in result.errors),
            result.errors,
        )
        self.assertTrue(
            any("must resolve inside the skill package" in error for error in result.errors),
            result.errors,
        )

    def test_rejects_nested_workflows_and_workflow_to_workflow_links(self):
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "testing"
            self.write_workflow(
                skill_dir,
                "first.md",
                workflow_id="first",
                body="[second](./second.md)\n",
            )
            self.write_workflow(skill_dir, "second.md", workflow_id="second")
            nested = skill_dir / "workflows/nested/deep.md"
            nested.parent.mkdir()
            nested.write_text("nested procedure\n", encoding="utf-8")

            result = LINTER.validate_skill_workflows(skill_dir)

        self.assertTrue(
            any("workflow-to-workflow links are not allowed" in error for error in result.errors),
            result.errors,
        )
        self.assertTrue(
            any("immediate children" in error for error in result.errors),
            result.errors,
        )

    def test_parent_skill_must_route_only_to_existing_workflows(self):
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "testing"
            self.write_workflow(skill_dir)
            (skill_dir / "references").mkdir()
            (skill_dir / "references/concurrency-oracle.md").write_text(
                "An oracle.\n", encoding="utf-8"
            )
            skill_text = """---
name: testing
description: Test design and selected testing procedures.
---
<rules>
- Preserve observable contracts.
</rules>
<workflow>
## Step 1 - Select a method.
1. Use [concurrency](./workflows/concurrency.md) for shared mutable state.
2. Do not load [missing](./workflows/missing.md).
## Step 2 - Apply it.
1. Falsify the selected behavior.
## Step 3 - Return evidence.
1. Report the evidence and residual risk.
</workflow>
"""
            (skill_dir / "SKILL.md").write_text(skill_text, encoding="utf-8")

            result = LINTER.lint_skill_markdown(skill_dir, skill_text)

        self.assertTrue(
            any("existing immediate child of `workflows/`" in error for error in result.errors),
            result.errors,
        )
        self.assertFalse(
            any("Support file is not referenced" in warning for warning in result.warnings),
            result.warnings,
        )

    def test_create_plugin_may_use_the_canonical_expertise_cli_without_local_scripts(self):
        skill_dir = Path("create-plugin")
        skill_text = """---
name: create-plugin
description: Create and validate an Expertise Pack.
user-invocable: true
---
<rules>
- Use the canonical Expertise CLI.
</rules>
<workflow>
## Step 1 - Validate the source.
1. Use #tool:execute to run `python -m expertise validate [pack-id]`.
## Step 2 - Build the target.
1. Use #tool:execute to run `python -m expertise build [pack-id] --target [target]`.
## Step 3 - Return evidence.
1. Report the validation and build results.
</workflow>
"""
        result = LINTER.lint_skill_markdown(skill_dir, skill_text)

        self.assertFalse(
            any("Canonical create-surface skills" in error for error in result.errors),
            result.errors,
        )
