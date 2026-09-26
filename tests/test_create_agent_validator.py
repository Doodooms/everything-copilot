import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).parents[1]
VALIDATOR = (
    ROOT
    / "agentic-core/skills/plugin-engineering/references/create-agent/scripts/validate_agent.py"
)


class CreateAgentValidatorTests(unittest.TestCase):
    ROUTING_BLOCK = """
<routing>
## ACCEPT
- Focused work in the agent's domain.
## REJECT
- Work outside the domain → `orchestrator`.
</routing>
"""
    CRITICAL_RULES_BLOCK = """
<critical_rules>
- MUST preserve approved scope and role boundaries.
</critical_rules>
"""
    GENERAL_RULES_BLOCK = """
<general_rules>
- SHOULD prefer the smallest sufficient method.
</general_rules>
"""
    RISK_ASSESSMENT_BLOCK = """
<risk_assessment>
Consume the assigned `risk_level`; MUST NOT downgrade it. SHOULD escalate only when new evidence warrants it.
</risk_assessment>
"""

    def run_validator(
        self,
        filename: str,
        frontmatter: str,
        body: str | None = None,
        *,
        include_routing: bool = True,
        include_contract_sections: bool = True,
        pack_manifest: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        body = body or """
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
    Own one focused role.
    ## Responsibilities
    - Keep the role focused.
    ## Constraints
    - Do not exceed the role.
    ## Output Contract
    - Return the scoped result.
    </rules>
    <agent-skills>
    - [skill name] - [context for using it]
    </agent-skills>
    <workflow>
    ## Step 1 - Gather context.
    ## Step 2 - Perform the role.
    ## Step 3 - Return the result.
    </workflow>
    """
        if include_routing and "<routing>" not in body and "<rules>" in body:
            body = body.replace("<rules>", self.ROUTING_BLOCK + "<rules>", 1)
        if include_contract_sections and "<critical_rules>" not in body and "<rules>" in body:
            body = body.replace(
                "<rules>",
                self.CRITICAL_RULES_BLOCK
                + self.GENERAL_RULES_BLOCK
                + self.RISK_ASSESSMENT_BLOCK
                + "<rules>",
                1,
            )
        if include_contract_sections and "<workflow>" in body:
            body = body.replace(
                "## Step 1 - Gather context.",
                "## Step 1 - Gather context.\n1. Consume the assigned `risk_level`.",
                1,
            )
        with TemporaryDirectory() as directory:
            pack_root = Path(directory)
            if pack_manifest is not None:
                (pack_root / "pack.yaml").write_text(pack_manifest, encoding="utf-8")
                agent_directory = pack_root / "agents"
                agent_directory.mkdir()
            else:
                agent_directory = pack_root
            agent_file = agent_directory / filename
            agent_file.write_text(f"---\n{frontmatter}---\n{body}", encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), "--agent-file", str(agent_file)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

    def test_rejects_missing_local_routing_block(self):
        body = """
<rules>
## Role
Own one focused role.
## Responsibilities
- Keep the role focused.
## Constraints
- Do not exceed the role.
## Output Contract
- Return the scoped result.
</rules>
<agent-skills>
- [skill name] - [context]
</agent-skills>
<workflow>
## Step 1 - Gather context.
## Step 2 - Perform the role.
## Step 3 - Return the result.
</workflow>
"""
        result = self.run_validator(
            "missing-routing.agent.md",
            "name: missing-routing\ntarget: vscode\ndescription: 'WHAT: focused work INVOKE FOR: focused requests DO NOT INVOKE FOR: unrelated work'\n",
            body,
            include_routing=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("<routing>", result.stdout)

    def test_rejects_missing_critical_rules_section(self):
        result = self.run_validator(
            "missing-critical.agent.md",
            "name: missing-critical\ntarget: vscode\ndescription: 'WHAT: focused work INVOKE FOR: focused requests DO NOT INVOKE FOR: unrelated work'\n",
            "<routing>\n## ACCEPT\n- scoped work\n## REJECT\n- unrelated → `orchestrator`\n</routing>",
            include_contract_sections=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("<critical_rules>", result.stdout)

    def test_rejects_missing_risk_assessment(self):
        body = self.CRITICAL_RULES_BLOCK + self.GENERAL_RULES_BLOCK + """
<routing>
## ACCEPT
- Focused work in the agent's domain.
## REJECT
- Work outside the domain → `orchestrator`.
</routing>
<rules>
## Role
Own one focused role.
## Responsibilities
- Keep the role focused.
## Constraints
- Do not exceed the role.
## Output Contract
- Return the scoped result.
</rules>
<agent-skills>
- [skill name] - [context]
</agent-skills>
<workflow>
## Step 1 - Gather context.
1. Apply the local risk assessment.
## Step 2 - Perform the role.
## Step 3 - Return the result.
</workflow>
"""
        result = self.run_validator(
            "missing-risk.agent.md",
            "name: missing-risk\ntarget: vscode\ndescription: 'WHAT: focused work INVOKE FOR: focused requests DO NOT INVOKE FOR: unrelated work'\n",
            body,
            include_contract_sections=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("<risk_assessment>", result.stdout)

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
Own one focused role.
## Responsibilities
- Keep the role focused.
## Constraints
- Do not exceed the role.
## Output Contract
- Return the scoped result.
</rules>
<agent-skills>
- [skill name] - [context]
</agent-skills>
<workflow>
## Step 1 - Gather context.
1. Read the assigned work.
## Step 2 - Perform the role.
## Step 3 - Return the result.
</workflow>
"""
        result = self.run_validator(
            "skipped-risk.agent.md",
            "name: skipped-risk\ntarget: vscode\ndescription: 'WHAT: focused work INVOKE FOR: focused requests DO NOT INVOKE FOR: unrelated work'\n",
            body,
            include_contract_sections=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("consume the inherited `risk_level`", result.stdout)

    def test_accepts_canonical_agent_without_definitions_or_confirmation_step(self):
        body = """
<rules>
## Role

## Responsibilities
- Keep the role focused.
## Constraints
- Do not exceed the role.
## Output Contract
- Return the scoped result.
</rules>

<agent-skills>
- [skill name] - [context for using it]
</agent-skills>

<workflow>
## Step 1 - Gather context.
## Step 2 - Perform the role.
## Step 3 - Return the result.
</workflow>
"""
        result = self.run_validator(
            "minimal.agent.md",
            "name: minimal\ntarget: vscode\ndescription: 'WHAT: focused work INVOKE FOR: focused requests DO NOT INVOKE FOR: unrelated work'\n",
            body,
        )

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("Step 0", result.stdout)
        self.assertNotIn("refusal", result.stdout.lower())

    def test_accepts_canonical_agent_with_nonempty_optional_definitions(self):
        body = """
<definitions>
- **defect packet** : a minimal reproduction and evidence for the repair owner
</definitions>
<rules>
## Role
Own one focused role.
## Responsibilities
- Keep the role focused.
## Constraints
- Do not exceed the role.
## Output Contract
- Return the scoped result.
</rules>
<agent-skills>
- [skill name] - [context for using it]
</agent-skills>
<workflow>
## Step 1 - Gather context.
## Step 2 - Perform the role.
## Step 3 - Return the result.
</workflow>
"""
        result = self.run_validator(
            "defined.agent.md",
            "name: defined\ntarget: vscode\ndescription: 'WHAT: focused work INVOKE FOR: focused requests DO NOT INVOKE FOR: unrelated work'\n",
            body,
        )

        self.assertEqual(result.returncode, 0, result.stdout)

    def test_rejects_empty_optional_definitions_block(self):
        body = """
<definitions>
</definitions>
<rules>
## Role
- Own the focused role.
## Responsibilities
- Keep the role focused.
## Constraints
- Do not exceed the role.
## Output Contract
- Return the scoped result.
</rules>
<agent-skills>
- [skill name] - [context for using it]
</agent-skills>
<workflow>
## Step 1 - Gather context.
## Step 2 - Perform the role.
## Step 3 - Return the result.
</workflow>
"""
        result = self.run_validator(
            "empty-definitions.agent.md",
            "name: empty-definitions\ntarget: vscode\ndescription: 'WHAT: focused work INVOKE FOR: focused requests DO NOT INVOKE FOR: unrelated work'\n",
            body,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("at least one non-empty", result.stdout)

    def test_rejects_step_zero_outside_workflow(self):
        body = """
<rules>
## Role
- Own the focused role.
## Responsibilities
- Keep the role focused.
## Constraints
- Do not exceed the role.
## Output Contract
- Return the scoped result.
</rules>

## Step 0 - Confirmation
1. Ask a question.

<workflow>
## Step 1 - Gather context.
## Step 2 - Perform the role.
## Step 3 - Return the result.
</workflow>
"""
        result = self.run_validator(
            "step-zero.agent.md",
            "name: step-zero\ntarget: vscode\ndescription: 'WHAT: focused work INVOKE FOR: focused requests DO NOT INVOKE FOR: unrelated work'\n",
            body,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must not include a Step 0", result.stdout)

    def test_rejects_body_level_admission_matrix_and_refusal_json(self):
        body = """
<rules>
## Role
Own one focused role.
## Responsibilities
- Keep the role focused.
| REQUEST SHAPE | INVOKE? |
| matching work | YES |
| unrelated work | NO |
- Return `{"status":"refused","agent":"sample","reason":"out of scope","suggested_alternative":"owner"}` for unrelated work.
## Constraints
- Do not exceed the role.
## Output Contract
- Return the scoped result.
</rules>

<agent-skills>
- [skill name] - [context for using it]
</agent-skills>

<workflow>
## Step 1 - Gather context.
## Step 2 - Perform the role.
## Step 3 - Return the result.
</workflow>
"""
        result = self.run_validator(
            "admission.agent.md",
            "name: admission\ntarget: vscode\ndescription: 'WHAT: focused work INVOKE FOR: focused requests DO NOT INVOKE FOR: unrelated work'\n",
            body,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("admission matrix", result.stdout.lower())
        self.assertIn("refusal JSON", result.stdout)

    def test_rejects_empty_definitions_in_legacy_wrapper(self):
        body = """
<definitions>
</definitions>
<workflow>
## Role
Own one focused role.
<rules>
## Responsibilities
- Keep the role focused.
## Constraints
- Do not exceed the role.
## Output Contract
- Return the scoped result.
</rules>
## Step 1 - Gather context.
## Step 2 - Perform the role.
## Step 3 - Return the result.
</workflow>
"""
        result = self.run_validator(
            "empty-legacy.agent.md",
            "name: empty-legacy\ntarget: vscode\ndescription: 'WHAT: focused work INVOKE FOR: focused requests DO NOT INVOKE FOR: unrelated work'\n",
            body,
        )

        self.assertNotEqual(result.returncode, 0)

    def test_rejects_legacy_use_for_description(self):
        result = self.run_validator(
            "legacy-routing.agent.md",
            "name: legacy-routing\ntarget: vscode\ndescription: 'WHAT: focused work USE FOR: focused requests DO NOT USE FOR: unrelated work'\n",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("INVOKE FOR", result.stdout)
        self.assertIn("DO NOT INVOKE FOR", result.stdout)

    def test_rejects_missing_agent_skills_section(self):
        body = """
<rules>
## Role
Own one focused role.
## Responsibilities
- Keep the role focused.
## Constraints
- Do not exceed the role.
## Output Contract
- Return the scoped result.
</rules>
<workflow>
## Step 1 - Gather context.
## Step 2 - Perform the role.
## Step 3 - Return the result.
</workflow>
"""
        result = self.run_validator(
            "missing-skills.agent.md",
            "name: missing-skills\ntarget: vscode\ndescription: 'WHAT: focused work INVOKE FOR: focused requests DO NOT INVOKE FOR: unrelated work'\n",
            body,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("<agent-skills>", result.stdout)

    def test_rejects_step_one_before_wrapped_role_and_rules(self):
        body = """
<definitions>
</definitions>
<workflow>
## Step 1 - Gather context.

## Role

<rules>
## Responsibilities
- Keep the role focused.
## Constraints
- Do not exceed the role.
## Output Contract
- Return the scoped result.
</rules>

## Step 2 - Perform the role.
## Step 3 - Return the result.
</workflow>
"""
        result = self.run_validator(
            "misplaced.agent.md",
            "name: misplaced\ntarget: vscode\ndescription: 'WHAT: focused work INVOKE FOR: focused requests DO NOT INVOKE FOR: unrelated work'\n",
            body,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Wrapped agents must keep this order", result.stdout)

    def test_rejects_legacy_nested_workflow_and_rules(self):
        body = """
<definitions>
- **handoff** : evidence sent to the owner of the next action
</definitions>
<workflow>
## Role
Own one focused role.
<rules>
## Responsibilities
- Perform that role.
## Constraints
- Stay within scope.
## Output Contract
- Return the defined handoff.
</rules>
## Step 1 - Gather context.
## Step 2 - Perform the role.
## Step 3 - Return the result.
</workflow>
"""
        result = self.run_validator(
            "legacy.agent.md",
            "name: legacy\ntarget: vscode\ndescription: 'WHAT: focused work INVOKE FOR: focused requests DO NOT INVOKE FOR: unrelated work'\n",
            body,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canonical", result.stdout.lower())

    def test_rejects_legacy_unwrapped_agent_body(self):
        body = """
# Role
Own one focused role.
## Responsibilities
- Perform that role.
## Workflow
1. Complete the scoped method.
## Constraints
- Stay within scope.
## Output Contract
- Return the defined handoff.
"""
        result = self.run_validator(
            "legacy-unwrapped.agent.md",
            "name: legacy-unwrapped\ntarget: vscode\ndescription: 'WHAT: focused work INVOKE FOR: focused requests DO NOT INVOKE FOR: unrelated work'\n",
            body,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canonical", result.stdout.lower())

    def test_rejects_invalid_delegation_contract(self):
        result = self.run_validator(
            "sample.agent.md",
            "name: sample\ntarget: vscode\ndescription: 'WHAT: x INVOKE FOR: x DO NOT INVOKE FOR: y'\nagents: [missing]\n",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("omits the `agent` tool", result.stdout)
        self.assertIn("unknown agent `missing`", result.stdout)

    def test_rejects_wildcard_agent_allowlists(self):
        result = self.run_validator(
            "sample.agent.md",
            "name: sample\ntarget: vscode\ndescription: 'WHAT: x INVOKE FOR: x DO NOT INVOKE FOR: y'\ntools: [agent, skill]\nagents: ['*']\n",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("wildcard", result.stdout.lower())

    def test_rejects_unapproved_agent_recipients(self):
        result = self.run_validator(
            "sample.agent.md",
            "name: sample\ntarget: vscode\ndescription: 'WHAT: x INVOKE FOR: x DO NOT INVOKE FOR: y'\ntools: [agent, skill]\nagents: [not-approved]\n",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown agent `not-approved`", result.stdout)

    def test_rejects_filename_name_drift(self):
        result = self.run_validator(
            "sample.agent.md",
            "name: different\ntarget: vscode\ndescription: 'WHAT: x INVOKE FOR: x DO NOT INVOKE FOR: y'\n",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must match the `.agent.md` filename stem", result.stdout)

    def test_rejects_missing_vscode_target_and_deprecated_infer(self):
        result = self.run_validator(
            "sample.agent.md",
            "name: sample\ninfer: true\ndescription: 'WHAT: x INVOKE FOR: x DO NOT INVOKE FOR: y'\n",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("target: vscode", result.stdout)
        self.assertIn("`infer` is deprecated", result.stdout)

    def test_accepts_native_skill_tool_and_read_only_github_mcp_tools(self):
        result = self.run_validator(
            "researcher.agent.md",
            "name: researcher\ntarget: vscode\ndescription: 'WHAT: research INVOKE FOR: evidence questions DO NOT INVOKE FOR: implementation'\ntools: [read, search, web, browser, skill, mcp_github_mcp_se_search_code, mcp_github_mcp_se_get_file_contents]\n",
        )

        self.assertEqual(result.returncode, 0, result.stdout)

    def test_accepts_configured_read_only_plugin_mcp_tools(self):
        result = self.run_validator(
            "researcher.agent.md",
            "name: researcher\ntarget: vscode\ndescription: 'WHAT: research INVOKE FOR: evidence questions DO NOT INVOKE FOR: implementation'\ntools: [context7/resolve-library-id, context7/query-docs, github-mcp-server/search_code, github-mcp-server/get_file_contents, semgrep/semgrep_scan, mcp_context7_resolve_library_id, mcp_context7_query_docs, mcp_semgrep_semgrep_scan]\n",
        )

        self.assertEqual(result.returncode, 0, result.stdout)

    def test_github_wildcard_is_reserved_for_the_canonical_orchestrator(self):
        result = self.run_validator(
            "researcher.agent.md",
            "name: researcher\ntarget: vscode\ndescription: 'WHAT: research INVOKE FOR: evidence questions DO NOT INVOKE FOR: implementation'\ntools: ['github/*']\n",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reserved for the canonical Orchestrator", result.stdout)

        result = subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--agent-file",
                str(ROOT / "agentic-core/com.github.copilot/agents/orchestrator.agent.md"),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_rejects_skill_wrappers_and_prompt_wrapper_tools(self):
        for tool_name in (
            "capabilityd/skill_load_github_evidence_research",
            "architecture_design",
            "code_review",
            "tdd_perform",
            "challenge_architecture",
        ):
            with self.subTest(tool_name=tool_name):
                result = self.run_validator(
                    "researcher.agent.md",
                    "name: researcher\ntarget: vscode\ndescription: 'WHAT: research INVOKE FOR: evidence questions DO NOT INVOKE FOR: implementation'\ntools: ["
                    + tool_name
                    + "]\n",
                )

                self.assertNotEqual(result.returncode, 0)
                expected_message = (
                    "uses a forbidden internal server"
                    if tool_name.startswith("capabilityd/")
                    else "not recognized by the workspace tool catalog"
                )
                self.assertIn(
                    expected_message, result.stdout
                )

    def test_rejects_unknown_mcp_server_tools(self):
        for tool_name in (
            "unknown-server/search_code",
            "context7/resolve-library-id-extra",
            "capabilityd/skill_load_tdd",
        ):
            with self.subTest(tool_name=tool_name):
                result = self.run_validator(
                    "researcher.agent.md",
                    "name: researcher\ntarget: vscode\ndescription: 'WHAT: research INVOKE FOR: evidence questions DO NOT INVOKE FOR: implementation'\ntools: ["
                    + tool_name
                    + "]\n",
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ERRORS:", result.stdout)

    def test_accepts_pack_mcp_tools_only_when_exact_tool_is_cataloged_and_projected(self):
        manifest = """
mcp_servers:
  - id: docs-api
    capabilities: [documentation]
    permissions: [query]
    tools: [search_docs]
projections:
  - agent_id: plugin-researcher
    mcp_servers: [docs-api]
"""
        result = self.run_validator(
            "plugin-researcher.agent.md",
            "name: plugin-researcher\ntarget: vscode\ndescription: 'WHAT: research INVOKE FOR: evidence questions DO NOT INVOKE FOR: implementation'\ntools: [docs-api/search_docs]\n",
            pack_manifest=manifest,
        )
        self.assertEqual(result.returncode, 0, result.stdout)

        unprojected_manifest = manifest.replace(
            "mcp_servers: [docs-api]", "mcp_servers: []"
        )
        result = self.run_validator(
            "plugin-researcher.agent.md",
            "name: plugin-researcher\ntarget: vscode\ndescription: 'WHAT: research INVOKE FOR: evidence questions DO NOT INVOKE FOR: implementation'\ntools: [docs-api/search_docs]\n",
            pack_manifest=unprojected_manifest,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not in this agent's exact projected", result.stdout)

    def test_rejects_unlisted_pack_mcp_subtools_even_when_server_is_projected(self):
        manifest = """
mcp_servers:
  - id: docs-api
    capabilities: [documentation]
    permissions: [query]
    tools: [search_docs]
projections:
  - agent_id: plugin-researcher
    mcp_servers: [docs-api]
"""
        result = self.run_validator(
            "plugin-researcher.agent.md",
            "name: plugin-researcher\ntarget: vscode\ndescription: 'WHAT: research INVOKE FOR: evidence questions DO NOT INVOKE FOR: implementation'\ntools: [docs-api/delete_all_documents]\n",
            pack_manifest=manifest,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not in this agent's exact projected", result.stdout)

    def test_rejects_mutating_github_mcp_tool_for_read_only_agents(self):
        result = self.run_validator(
            "researcher.agent.md",
            "name: researcher\ntarget: vscode\ndescription: 'WHAT: research INVOKE FOR: evidence questions DO NOT INVOKE FOR: implementation'\ntools: [mcp_github_mcp_se_push_files]\n",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not recognized by the workspace tool catalog", result.stdout)

    def test_rejects_self_delegation(self):
        result = self.run_validator(
            "researcher.agent.md",
            "name: researcher\ntarget: vscode\ndescription: 'WHAT: research INVOKE FOR: evidence questions DO NOT INVOKE FOR: implementation'\ntools: [agent]\nagents: [researcher]\n",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must not list itself", result.stdout)

    def test_accepts_agent_ids_from_the_installed_core_plugin(self):
        result = self.run_validator(
            "sample.agent.md",
            "name: sample\ntarget: vscode\ndescription: 'WHAT: sample INVOKE FOR: scoped requests DO NOT INVOKE FOR: unrelated work'\ntools: [agent]\nagents: [researcher]\n",
        )

        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()