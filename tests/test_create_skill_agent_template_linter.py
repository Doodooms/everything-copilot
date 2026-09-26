import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
PLUGIN_SKILL_ROOT = ROOT / "agentic-core/skills/plugin-engineering"
CREATE_AGENT_ROOT = PLUGIN_SKILL_ROOT / "references/create-agent"
CREATE_SKILL_ROOT = PLUGIN_SKILL_ROOT / "references/create-skill"
LINTER_PATH = (
    CREATE_SKILL_ROOT / "scripts/skill_lint_core.py"
)
SPEC = importlib.util.spec_from_file_location("create_skill_lint_core_test", LINTER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load create-skill linter at {LINTER_PATH}")
LINTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = LINTER
SPEC.loader.exec_module(LINTER)


class EmbeddedAgentTemplateLinterTests(unittest.TestCase):
    ROUTING_BLOCK = """
<routing>
## ACCEPT
- Focused work in the agent's domain.
## REJECT
- Work outside the domain → `orchestrator`.
</routing>
"""
    CONTRACT_BLOCKS = """
<critical_rules>
- MUST preserve approved scope and role boundaries.
</critical_rules>
<general_rules>
- SHOULD prefer the smallest sufficient method.
</general_rules>
<risk_assessment>
Consume the assigned `risk_level`; MUST NOT downgrade it. SHOULD escalate only when new evidence warrants it.
</risk_assessment>
"""

    def validate_agent_body(
        self,
        body: str,
        *,
        include_routing: bool = True,
        include_contract_sections: bool = True,
    ):
        if include_routing and "<routing>" not in body and "<rules>" in body:
            body = body.replace("<rules>", self.ROUTING_BLOCK + "<rules>", 1)
        if include_contract_sections and "<critical_rules>" not in body and "<rules>" in body:
            body = body.replace("<rules>", self.CONTRACT_BLOCKS + "<rules>", 1)
        if include_contract_sections and "<workflow>" in body:
            body = body.replace(
                "## Step 1 - Gather context.",
                "## Step 1 - Gather context.\n1. Consume the assigned `risk_level`.",
                1,
            )
        return LINTER.validate_agent_template_markdown_block(body)

    def test_create_skill_admission_and_rejection_contract_remain_intact(self):
        skill_text = (
            PLUGIN_SKILL_ROOT / "workflows/skill-authoring.md"
        ).read_text(encoding="utf-8")
        domain_text = (PLUGIN_SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertLess(skill_text.index("<admission>"), skill_text.index("## Step 0"))
        self.assertIn("## ACCEPT", skill_text)
        self.assertIn("## REJECT", skill_text)
        self.assertIn("For REJECT, return exactly:", skill_text)
        self.assertIn(
            '{"status":"rejected","skill":"create-skill","reason":"<concise reason>","routing":"<route or null>"}',
            skill_text,
        )
        self.assertIn("[skill-authoring](./workflows/skill-authoring.md)", domain_text)
        self.assertIn("[skill-maintenance](./workflows/skill-maintenance.md)", domain_text)

    def test_authoring_skills_route_to_distinct_immediate_workflows(self):
        workflow_ids = (
            "agent-authoring",
            "agent-validation",
            "skill-authoring",
            "skill-maintenance",
            "plugin-creation",
            "plugin-update",
        )
        domain_text = (PLUGIN_SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        workflow_result = LINTER.validate_skill_workflows(PLUGIN_SKILL_ROOT)
        self.assertEqual([], workflow_result.errors)

        for workflow_id in workflow_ids:
            route_path = PLUGIN_SKILL_ROOT / "workflows" / f"{workflow_id}.md"
            route_text = route_path.read_text(encoding="utf-8")
            metadata, _ = LINTER.split_frontmatter(route_text)

            self.assertIn(f"./workflows/{workflow_id}.md", domain_text)
            self.assertEqual(workflow_id, metadata["id"])
            self.assertNotIn("subskills", metadata)
            self.assertTrue(route_path.is_file())

    def test_create_skill_workflows_use_the_supported_scaffold_and_validator_cli(self):
        authoring = (PLUGIN_SKILL_ROOT / "workflows/skill-authoring.md").read_text(
            encoding="utf-8"
        )
        maintenance = (PLUGIN_SKILL_ROOT / "workflows/skill-maintenance.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("scaffold.py", authoring)
        self.assertIn("skill-scaffold.json", authoring)
        self.assertIn(
            "[skill-scaffold.json](../references/create-skill/assets/skill-scaffold.json)",
            authoring,
        )
        self.assertIn("--original-spec [spec_file]", authoring)
        self.assertIn("--original-spec [spec_file] --validate", authoring)
        self.assertIn("the scaffold copies it into the package", authoring)
        self.assertIn("validate.py", authoring)
        self.assertIn("--skill-dir [skill_dir]", authoring)
        self.assertIn("--skill-dir [skill-dir]", maintenance)

    def test_authoring_templates_mark_fillable_fields_and_agent_skills(self):
        agent_template = (CREATE_AGENT_ROOT / "assets/agent-template.md").read_text(
            encoding="utf-8"
        )
        skill_template = (CREATE_SKILL_ROOT / "assets/skill-template.md").read_text(
            encoding="utf-8"
        )
        agent_workflow_fragment = (
            CREATE_AGENT_ROOT / "assets/workflow.md"
        ).read_text(encoding="utf-8")
        agent_validation = (
            CREATE_AGENT_ROOT / "references/validation.md"
        ).read_text(encoding="utf-8")

        self.assertIn('name: "[agent-slug]"', agent_template)
        self.assertIn("<agent-skills>", agent_template)
        self.assertIn("[skill name]", agent_template)
        self.assertIn("Optional:", agent_template)
        self.assertIn("decision-relevant term", agent_template)
        self.assertIn("omit this block", agent_template)
        self.assertIn("L0 isolated/reversible", agent_template)
        self.assertIn("consume the assigned `risk_level`", agent_workflow_fragment)
        self.assertIn("specialist's block consumes the assigned `risk_level`", agent_validation)
        for section in ("<critical_rules>", "<general_rules>", "<risk_assessment>"):
            self.assertIn(section, agent_template)
            self.assertIn(section, skill_template)
        self.assertIn("Optional:", skill_template)
        self.assertIn("decision-relevant term", skill_template)
        self.assertIn("omit this block", skill_template)
        self.assertIn('name: "[skill-name]"', skill_template)
        self.assertIn("[inspect or prepare]", skill_template)
        self.assertIn(
            "square-bracketed value",
            (PLUGIN_SKILL_ROOT / "workflows/skill-authoring.md").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "authoring patterns",
            (PLUGIN_SKILL_ROOT / "workflows/agent-authoring.md").read_text(encoding="utf-8"),
        )
        fences, _, _ = LINTER.split_leading_code_fences(agent_template)
        self.assertEqual(
            [], LINTER.validate_agent_template_yaml_block(fences[0][1])
        )

    def test_create_skill_has_separate_priority_and_risk_contracts(self):
        skill_text = (PLUGIN_SKILL_ROOT / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertLess(skill_text.index("<critical_rules>"), skill_text.index("<general_rules>"))
        self.assertLess(skill_text.index("<general_rules>"), skill_text.index("<risk_assessment>"))
        self.assertLess(skill_text.index("<risk_assessment>"), skill_text.index("<rules>"))
        self.assertEqual([], LINTER.validate_skill_contract_sections(skill_text))

    def test_composed_skill_guidance_preserves_context_and_parent_control(self):
        authoring_workflow_text = (PLUGIN_SKILL_ROOT / "workflows/skill-authoring.md").read_text(
            encoding="utf-8"
        )
        composition = CREATE_SKILL_ROOT / "references/skill-composition.md"
        template = (CREATE_SKILL_ROOT / "assets/skill-template.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("skill-composition", authoring_workflow_text)
        self.assertTrue(composition.is_file())
        composition_text = composition.read_text(encoding="utf-8")
        for term in ("DAG", "resume", "inputs", "return contract", "use_case"):
            self.assertIn(term, composition_text)
        self.assertIn("For a distinct installed domain skill", template)
        self.assertIn("immediate workflow", template)
        self.assertIn("[resume point]", template)

    def test_accepts_canonical_agent_without_definitions_or_step_zero(self):
        body = """
<rules>
## Role
The agent owns one focused role.
## Responsibilities
- Perform that role.
## Constraints
- Stay within scope.
## Output Contract
- Return the defined handoff.
</rules>
<agent-skills>
- [skill name] - [context for using it]
</agent-skills>
<workflow>
## Step 1 - Gather context.
1. Inspect the assigned work.
## Step 2 - Perform the role.
1. Complete the scoped method.
## Step 3 - Return the result.
1. Provide the promised handoff.
</workflow>
"""

        self.assertEqual([], self.validate_agent_body(body))

    def test_accepts_canonical_agent_with_nonempty_optional_definitions(self):
        body = """
<definitions>
- **defect packet** : a minimal reproduction and evidence for the repair owner
</definitions>
<rules>
## Role
The agent owns one focused role.
## Responsibilities
- Perform that role.
## Constraints
- Stay within scope.
## Output Contract
- Return the defined handoff.
</rules>
<agent-skills>
- [skill name] - [context for using it]
</agent-skills>
<workflow>
## Step 1 - Gather context.
1. Inspect the assigned work.
## Step 2 - Perform the role.
1. Complete the scoped method.
## Step 3 - Return the result.
1. Provide the promised handoff.
</workflow>
"""

        self.assertEqual([], self.validate_agent_body(body))

    def test_rejects_empty_optional_definitions(self):
        body = """
<definitions>
</definitions>
<rules>
## Role
The agent owns one focused role.
## Responsibilities
- Perform that role.
## Constraints
- Stay within scope.
## Output Contract
- Return the defined handoff.
</rules>
<agent-skills>
- [skill name] - [context for using it]
</agent-skills>
<workflow>
## Step 1 - Gather context.
1. Inspect the assigned work.
## Step 2 - Perform the role.
1. Complete the scoped method.
## Step 3 - Return the result.
1. Provide the promised handoff.
</workflow>
"""

        errors = self.validate_agent_body(body)
        self.assertTrue(any("non-empty" in error for error in errors), errors)

    def test_rejects_step_zero_outside_workflow(self):
        body = """
<rules>
## Role
The agent owns one focused role.
## Responsibilities
- Perform that role.
## Constraints
- Stay within scope.
## Output Contract
- Return the defined handoff.
</rules>
<agent-skills>
- [skill name] - [context for using it]
</agent-skills>
## Step 0 - Confirmation.
1. Ask a question.
<workflow>
## Step 1 - Gather context.
1. Inspect the assigned work.
## Step 2 - Perform the role.
1. Complete the scoped method.
## Step 3 - Return the result.
1. Provide the promised handoff.
</workflow>
"""

        errors = self.validate_agent_body(body)
        self.assertTrue(any("exactly ## Step 1" in error for error in errors), errors)

    def test_rejects_body_level_admission_matrix_and_refusal_json(self):
        body = """
<rules>
## Role
The agent owns one focused role.
## Responsibilities
- Perform that role.
| REQUEST SHAPE | INVOKE? |
| matching work | YES |
| unrelated work | NO |
- Return `{"status":"refused","agent":"sample","reason":"out of scope","suggested_alternative":"owner"}` for unrelated work.
## Constraints
- Stay within scope.
## Output Contract
- Return the defined handoff.
</rules>
<agent-skills>
- [skill name] - [context for using it]
</agent-skills>
<workflow>
## Step 1 - Gather context.
1. Inspect the assigned work.
## Step 2 - Perform the role.
1. Complete the scoped method.
## Step 3 - Return the result.
1. Provide the promised handoff.
</workflow>
"""

        errors = self.validate_agent_body(body)
        self.assertTrue(any("admission matrix" in error.lower() for error in errors), errors)
        self.assertTrue(any("refusal JSON" in error for error in errors), errors)

    def test_rejects_nested_rules_inside_workflow(self):
        body = """
<workflow>
<rules>
## Role
The agent owns one focused role.
## Responsibilities
- Perform that role.
## Constraints
- Stay within scope.
## Output Contract
- Return the defined handoff.
</rules>
<agent-skills>
- [skill name] - [context for using it]
</agent-skills>
## Step 1 - Gather context.
1. Inspect the assigned work.
## Step 2 - Perform the role.
1. Complete the scoped method.
## Step 3 - Return the result.
1. Provide the promised handoff.
</workflow>
"""

        errors = self.validate_agent_body(body)
        self.assertTrue(any("order" in error and "<workflow>" in error for error in errors), errors)

    def test_rejects_missing_agent_skills_section(self):
        body = """
<rules>
## Role
The agent owns one focused role.
## Responsibilities
- Perform that role.
## Constraints
- Stay within scope.
## Output Contract
- Return the defined handoff.
</rules>
<workflow>
## Step 1 - Gather context.
1. Inspect the assigned work.
## Step 2 - Perform the role.
1. Complete the scoped method.
## Step 3 - Return the result.
1. Provide the promised handoff.
</workflow>
"""

        errors = self.validate_agent_body(body)
        self.assertTrue(any("<agent-skills>" in error for error in errors), errors)

    def test_rejects_missing_routing_block(self):
        body = """
<rules>
## Role
The agent owns one focused role.
## Responsibilities
- Perform that role.
## Constraints
- Stay within scope.
## Output Contract
- Return the defined handoff.
</rules>
<agent-skills>
- [skill name] - [context]
</agent-skills>
<workflow>
## Step 1 - Gather context.
1. Inspect the assigned work.
## Step 2 - Perform the role.
1. Complete the scoped method.
## Step 3 - Return the result.
1. Provide the promised handoff.
</workflow>
"""

        errors = self.validate_agent_body(body, include_routing=False)
        self.assertTrue(any("<routing>" in error for error in errors), errors)

    def test_rejects_step_one_that_skips_risk_assessment(self):
        body = """
<routing>
## ACCEPT
- Focused work in the agent's domain.
## REJECT
- Work outside the domain → `orchestrator`.
</routing>
<critical_rules>
- MUST preserve approved scope and role boundaries.
</critical_rules>
<general_rules>
- SHOULD prefer the smallest sufficient method.
</general_rules>
<risk_assessment>
Consume the assigned `risk_level`; MUST NOT downgrade it. SHOULD escalate only when new evidence warrants it.
</risk_assessment>
<rules>
## Role
The agent owns one focused role.
## Responsibilities
- Perform that role.
## Constraints
- Stay within scope.
## Output Contract
- Return the defined handoff.
</rules>
<agent-skills>
- [skill name] - [context]
</agent-skills>
<workflow>
## Step 1 - Gather context.
1. Read the assigned work.
## Step 2 - Perform the role.
1. Complete the scoped method.
## Step 3 - Return the result.
1. Provide the promised handoff.
</workflow>
"""

        errors = self.validate_agent_body(
            body, include_contract_sections=False
        )
        self.assertTrue(
            any("Step 1 must apply" in error for error in errors), errors
        )


if __name__ == "__main__":
    unittest.main()
