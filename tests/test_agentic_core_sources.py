import json
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "agentic-core"

CANONICAL_AGENTS = {
    "architect.agent.md",
    "challenger.agent.md",
    "devops.agent.md",
    "implementer.agent.md",
    "orchestrator.agent.md",
    "planner.agent.md",
    "quality-assurance.agent.md",
    "researcher.agent.md",
    "reviewer.agent.md",
}

DOMAIN_SKILLS = {
    "architecture",
    "context-management",
    "operations",
    "orchestration",
    "plugin-engineering",
    "quality-engineering",
    "research",
    "semantic-modeling",
    "security",
    "software-engineering",
}

PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"


class AgenticCoreSourceTests(unittest.TestCase):
    def test_core_is_a_standalone_agent_plugin(self):
        manifest_path = CORE / "plugin.json"
        self.assertTrue(manifest_path.is_file(), "agentic-core needs a root plugin.json")

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["$schema"], PLUGIN_SCHEMA)
        self.assertEqual(manifest["name"], "agentic-core")
        self.assertTrue(manifest["description"])
        self.assertRegex(manifest["version"], re.compile(r"^\d+\.\d+\.\d+$"))
        self.assertEqual(manifest["author"]["name"], "Doodooms")
        self.assertTrue((CORE / "skills").is_dir())
        self.assertTrue((CORE / "com.github.copilot/agents").is_dir())

    def test_all_nine_agents_have_only_the_plugin_source(self):
        plugin_agents = CORE / "com.github.copilot/agents"
        self.assertEqual(
            {path.name for path in plugin_agents.glob("*.agent.md")},
            CANONICAL_AGENTS,
        )
        for filename in CANONICAL_AGENTS:
            self.assertFalse(
                (ROOT / ".github/agents" / filename).is_file(),
                f"{filename} must not have an editable workspace duplicate",
            )

        self.assertTrue(
            (ROOT / ".github/copilot-instructions.md").is_file(),
            "workspace-owned Copilot instructions must stay in place",
        )
        instructions = (ROOT / ".github/copilot-instructions.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("agentic-core", instructions)
        self.assertIn(".github/agents/", instructions)
        self.assertIn(".github/skills/", instructions)

    def test_agent_skill_policies_resolve_locally_and_reference_installed_skills(self):
        agents = CORE / "com.github.copilot/agents"
        for agent_path in sorted(agents.glob("*.agent.md")):
            text = agent_path.read_text(encoding="utf-8")
            frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
            self.assertIsNotNone(frontmatter_match, agent_path.name)
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
            skill_block = re.search(
                r"<agent-skills>(.*?)</agent-skills>", text, re.DOTALL
            )
            self.assertIsNotNone(skill_block, agent_path.name)
            skill_names = re.findall(
                r"^\s*-\s*(?:MUST|SHOULD|MAY)\s+(?:load|use)\s+`([^`]+)`",
                skill_block.group(1),
                re.MULTILINE,
            )
            self.assertTrue(skill_names, f"{agent_path.name} has no explicit skill policy")
            self.assertEqual(
                len(skill_names),
                len(set(skill_names)),
                f"{agent_path.name} repeats a skill policy entry",
            )
            for skill_name in skill_names:
                self.assertTrue(
                    (CORE / "skills" / skill_name / "SKILL.md").is_file(),
                    f"{agent_path.name} references missing skill `{skill_name}`",
                )
            self.assertIn(
                "skill",
                frontmatter.get("tools", []),
                f"{agent_path.name} has skill policy but lacks the native skill tool",
            )
            step_one = re.search(
                r"## Step 1\b(.*?)(?=^## Step 2\b)",
                text,
                re.DOTALL | re.MULTILINE,
            )
            self.assertIsNotNone(step_one, agent_path.name)
            self.assertIn(
                "resolve this agent's `<agent-skills>` policy",
                step_one.group(1),
                f"{agent_path.name} does not resolve skill policy before work",
            )

    def test_mcp_servers_are_pinned_and_exposed_to_the_intended_agents(self):
        manifest = json.loads((CORE / "mcp.json").read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["$schema"],
            "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
        )
        servers = manifest["mcpServers"]
        self.assertEqual(set(servers), {"context7", "semgrep"})
        self.assertIn("@upstash/context7-mcp@4.1.1", servers["context7"]["args"])
        self.assertIn("semgrep==1.177.0", servers["semgrep"]["args"])
        self.assertTrue(all("env" not in server for server in servers.values()))

        agent_tools = {}
        for agent_name in ("orchestrator", "researcher", "reviewer"):
            text = (
                CORE
                / "com.github.copilot"
                / "agents"
                / f"{agent_name}.agent.md"
            ).read_text(encoding="utf-8")
            frontmatter = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
            self.assertIsNotNone(frontmatter)
            agent_tools[agent_name] = set(yaml.safe_load(frontmatter.group(1)).get("tools", []))

        self.assertTrue(
            {"mcp_context7_resolve_library_id", "mcp_context7_query_docs"}
            <= agent_tools["researcher"]
        )
        self.assertTrue(
            {"mcp_semgrep_semgrep_scan"} <= agent_tools["reviewer"]
        )
        for agent_name in ("orchestrator", "reviewer"):
            self.assertNotIn("mcp_context7_query_docs", agent_tools[agent_name])
        for agent_name in ("orchestrator", "researcher"):
            self.assertNotIn("mcp_semgrep_semgrep_scan", agent_tools[agent_name])

    def test_orchestrator_has_an_explicit_default_deny_agent_allowlist(self):
        path = CORE / "com.github.copilot/agents/orchestrator.agent.md"
        text = path.read_text(encoding="utf-8")
        frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(frontmatter_match)
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
        authoring_contract = (
            CORE / "skills/plugin-engineering/workflows/agent-authoring.md"
        ).read_text(
            encoding="utf-8"
        )
        expected_recipients = {
            name.removesuffix(".agent.md")
            for name in CANONICAL_AGENTS
            if name != "orchestrator.agent.md"
        }

        self.assertEqual(set(frontmatter.get("agents", [])), expected_recipients)
        self.assertNotIn("*", frontmatter.get("agents", []))
        self.assertIn("skill", frontmatter.get("tools", []))
        self.assertIn("MUST NOT use wildcard recipients", authoring_contract)

    def test_only_domain_skills_are_discoverable_and_workflows_are_immediate(self):
        plugin_skills = CORE / "skills"
        actual_skills = {
            path.parent.name
            for path in plugin_skills.glob("*/SKILL.md")
            if path.is_file()
        }
        self.assertEqual(actual_skills, DOMAIN_SKILLS)
        self.assertEqual(
            {path.parent.name for path in plugin_skills.rglob("SKILL.md")},
            DOMAIN_SKILLS,
            "nested method sources must not be discovered as standalone skills",
        )

        for skill_name in DOMAIN_SKILLS:
            self.assertFalse(
                (ROOT / ".github/skills" / skill_name / "SKILL.md").is_file(),
                f"{skill_name} must not have an editable workspace duplicate",
            )

        for domain in DOMAIN_SKILLS:
            domain_root = plugin_skills / domain
            for workflow in sorted((domain_root / "workflows").glob("*.md")):
                workflow_metadata = yaml.safe_load(
                    re.match(
                        r"\A---\n(.*?)\n---\n",
                        workflow.read_text(encoding="utf-8"),
                        re.DOTALL,
                    ).group(1)
                )
                self.assertNotIn(
                    "subskills",
                    workflow_metadata,
                    f"{workflow} still declares a nested procedure",
                )
                for relative_path in workflow_metadata.get("references", []):
                    resolved = (workflow.parent / relative_path).resolve()
                    self.assertTrue(
                        resolved.is_relative_to(domain_root.resolve()),
                        f"{workflow} declares an out-of-package reference",
                    )
                    self.assertNotEqual(
                        resolved.name,
                        "method-source.md",
                        f"{workflow} loads an archived procedure as runtime guidance",
                    )
                    self.assertFalse(
                        "workflows" in resolved.relative_to(domain_root.resolve()).parts,
                        f"{workflow} references a nested workflow",
                    )

    def test_p7_agent_tool_and_handoff_corrections_are_present(self):
        agents = CORE / "com.github.copilot/agents"
        paths = {
            name: agents / f"{name}.agent.md"
            for name in ("implementer", "planner", "devops", "reviewer")
        }
        for path in paths.values():
            self.assertTrue(path.is_file(), f"missing plugin agent source: {path}")

        implementer = paths["implementer"].read_text(encoding="utf-8")
        planner = paths["planner"].read_text(encoding="utf-8")
        devops = paths["devops"].read_text(encoding="utf-8")
        reviewer = paths["reviewer"].read_text(encoding="utf-8")

        self.assertIn("suggested next owner: normally `quality-assurance`", implementer)
        self.assertNotIn("suggested next owner: normally `qa`", implementer)
        self.assertIn("acceptance-criteria mapping", planner)
        self.assertIn("Own MCP hosting/configuration/deployment only", devops)
        self.assertNotIn("SHOULD load `create-mcp`", devops)
        self.assertIn(
            "`execute` MAY be used only for non-mutating, review-scoped inspection or static analysis",
            reviewer,
        )
        self.assertIn("MUST NOT be used to repair artifacts or substitute for QA", reviewer)

    def test_new_skills_preserve_the_approved_workflow_boundaries(self):
        skills = CORE / "skills"
        token_optimization = (
            skills / "context-management/workflows/token-optimization.md"
        ).read_text(encoding="utf-8")
        install_plugin = (
            skills / "operations/workflows/install-agent-plugin.md"
        ).read_text(encoding="utf-8")
        create_plugin = (
            skills / "plugin-engineering/workflows/plugin-creation.md"
        ).read_text(encoding="utf-8")
        pack_contract = (
            skills / "plugin-engineering/references/create-plugin/references/plugin-contract.md"
        ).read_text(encoding="utf-8")

        self.assertIn("local-regex-estimate-v1", token_optimization)
        self.assertIn("The script does not write source files or make network requests", token_optimization)
        self.assertIn("advisory only", token_optimization.lower())
        self.assertIn("warning_budget_tokens", token_optimization)
        self.assertIn("pluginctl", install_plugin)
        self.assertIn("trusted source", install_plugin.lower())
        self.assertIn("the caller must identify and approve", install_plugin.lower())
        self.assertIn("canonical CLI", create_plugin)
        self.assertIn("MUST NOT hand-write a substitute", create_plugin)
        self.assertIn("codex", pack_contract.lower())
        self.assertIn("skills remain packaged workflows", pack_contract)

    def test_qa_routes_hidden_end_to_end_specialty_through_testing(self):
        qa = (
            CORE / "com.github.copilot/agents/quality-assurance.agent.md"
        ).read_text(encoding="utf-8")
        testing = (CORE / "skills/quality-engineering/SKILL.md").read_text(encoding="utf-8")
        workflow = CORE / "skills/quality-engineering/workflows/end-to-end.md"
        workflow_text = workflow.read_text(encoding="utf-8")

        self.assertIn("load `quality-engineering`", qa)
        self.assertIn("`end-to-end`", qa)
        self.assertIn("[end-to-end]", testing)
        self.assertIn("complete user journeys", workflow_text)

    def test_implementer_routes_hidden_concurrency_specialty_through_workflows(self):
        implementer = (
            CORE / "com.github.copilot/agents/implementer.agent.md"
        ).read_text(encoding="utf-8")
        test_design = (
            CORE / "skills/quality-engineering/workflows/test-design.md"
        ).read_text(encoding="utf-8")
        boundaries = (
            CORE
            / "skills/quality-engineering/references/testing/references/equivalence-boundaries.md"
        ).read_text(encoding="utf-8")
        concurrency_design = (
            CORE
            / "skills/software-engineering/workflows/concurrency-design.md"
        ).read_text(encoding="utf-8")
        implementation = (
            CORE / "skills/software-engineering/SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("load `software-engineering`", implementer)
        self.assertIn("MUST load `quality-engineering` when designing or materially changing tests", implementer)
        self.assertIn("MUST load `software-engineering` for testable behavior changes", implementer)
        self.assertIn("For concurrent behavior", boundaries)
        self.assertIn("../references/testing/references/equivalence-boundaries.md", test_design)
        self.assertIn("deterministic barriers", test_design)
        self.assertIn("[concurrency-design]", implementation)
        self.assertIn("allowed interleavings", concurrency_design)

    def test_testing_and_implementation_design_keep_distinct_method_owners(self):
        implementer = (
            CORE / "com.github.copilot/agents/implementer.agent.md"
        ).read_text(encoding="utf-8")
        reviewer = (
            CORE / "com.github.copilot/agents/reviewer.agent.md"
        ).read_text(encoding="utf-8")
        architect = (
            CORE / "com.github.copilot/agents/architect.agent.md"
        ).read_text(encoding="utf-8")
        testing = (
            CORE / "skills/quality-engineering/workflows/test-design.md"
        ).read_text(encoding="utf-8")
        tdd = (
            CORE / "skills/software-engineering/workflows/tdd.md"
        ).read_text(encoding="utf-8")
        design = (
            CORE / "skills/software-engineering/workflows/representation-selection.md"
        ).read_text(encoding="utf-8")

        self.assertIn("MUST load `software-engineering` for testable behavior changes", implementer)
        self.assertIn("SHOULD load `software-engineering` when a non-trivial local", reviewer)
        self.assertNotIn("software-engineering", architect)
        self.assertIn("that skill owns the RED/GREEN sequence", testing)
        self.assertIn("## Step 0 - Establish the test target", tdd)
        self.assertIn("## Step 1 - RED", tdd)
        self.assertIn("## Step 2 - GREEN", tdd)
        self.assertIn("DO NOT wrap a simple choice in an abstraction", design)

    def test_orchestrator_keeps_github_selector_exclusive(self):
        agents = CORE / "com.github.copilot/agents"
        for agent_path in sorted(agents.glob("*.agent.md")):
            text = agent_path.read_text(encoding="utf-8")
            frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
            self.assertIsNotNone(frontmatter_match, agent_path.name)
            tools = yaml.safe_load(frontmatter_match.group(1)).get("tools", [])
            if agent_path.name == "orchestrator.agent.md":
                self.assertIn("github/*", tools)
            else:
                self.assertNotIn("github/*", tools)

    def test_installed_skill_script_docs_use_skill_relative_paths_and_explicit_workspace_paths(self):
        orchestrate_path = (
            CORE / "skills/orchestration/workflows/orchestrate.md"
        )
        sdd_path = (
            CORE / "skills/orchestration/workflows/spec-driven-development.md"
        )
        artifact_path = (
            CORE
            / "skills/orchestration/references/spec-driven-development/references/artifact-lifecycle.md"
        )

        for path in (orchestrate_path, sdd_path, artifact_path):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("agentic-core/skills/", text, str(path))
            self.assertNotIn("./.venv", text, str(path))

        for path in (orchestrate_path, artifact_path):
            text = path.read_text(encoding="utf-8")
            self.assertIn("agentskills.io/skill-creation/using-scripts", text)

        orchestrate = orchestrate_path.read_text(encoding="utf-8")
        sdd = sdd_path.read_text(encoding="utf-8")
        self.assertIn("scripts/orchestrator.py", orchestrate)
        self.assertIn("--history-dir", orchestrate)
        self.assertIn("agentskills.io/skill-creation/using-scripts", orchestrate)
        self.assertIn("scripts/validate_sdd_state.py", sdd)
        self.assertIn("absolute-task-state-path", sdd)
        self.assertIn("absolute", sdd.lower())


if __name__ == "__main__":
    unittest.main()
