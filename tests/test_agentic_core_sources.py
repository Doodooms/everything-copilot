import json
import os
import re
import subprocess
import tempfile
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
    "multi-harness",
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
        self.assertTrue(
            manifest_path.is_file(), "agentic-core needs a root plugin.json"
        )

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
            self.assertTrue(
                skill_names, f"{agent_path.name} has no explicit skill policy"
            )
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
        self.assertEqual(
            set(servers),
            {"context7", "github-mcp-server", "semgrep"},
        )
        self.assertIn("@upstash/context7-mcp@4.1.1", servers["context7"]["args"])
        self.assertIn("semgrep==1.177.0", servers["semgrep"]["args"])
        self.assertTrue(all("env" not in server for server in servers.values()))
        self.assertEqual(
            servers["github-mcp-server"],
            {
                "type": "stdio",
                "command": "bash",
                "args": ["runtime/mcp/github-app-stdio.sh"],
                "cwd": "${PLUGIN_ROOT}",
            },
        )
        self.assertTrue((CORE / "runtime/mcp/github-app-stdio.sh").is_file())

        agent_tools = {}
        for agent_name in ("orchestrator", "researcher", "reviewer"):
            text = (
                CORE / "com.github.copilot" / "agents" / f"{agent_name}.agent.md"
            ).read_text(encoding="utf-8")
            frontmatter = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
            self.assertIsNotNone(frontmatter)
            agent_tools[agent_name] = set(
                yaml.safe_load(frontmatter.group(1)).get("tools", [])
            )

        self.assertTrue(
            {"mcp_context7_resolve_library_id", "mcp_context7_query_docs"}
            <= agent_tools["researcher"]
        )
        self.assertIn("github/*", agent_tools["orchestrator"])
        self.assertTrue(
            {
                "mcp_github_mcp_se_search_code",
                "mcp_github_mcp_se_get_file_contents",
                "mcp_github_mcp_se_search_pull_requests",
                "mcp_github_mcp_se_pull_request_read",
            }
            <= agent_tools["researcher"]
        )
        self.assertTrue({"mcp_semgrep_semgrep_scan"} <= agent_tools["reviewer"])
        for agent_name in ("orchestrator", "reviewer"):
            self.assertNotIn("mcp_context7_query_docs", agent_tools[agent_name])
        for agent_name in ("orchestrator", "researcher"):
            self.assertNotIn("mcp_semgrep_semgrep_scan", agent_tools[agent_name])
        self.assertFalse(
            any(
                tool.startswith("mcp_github_mcp_se_")
                for tool in agent_tools["reviewer"]
            )
        )

    def test_github_app_launcher_uses_a_read_only_key_mount_and_pinned_image(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake_docker = root / "docker"
            captured_args = root / "docker-args.txt"
            key_file = root / "fixture-app.pem"
            fake_docker.write_text(
                '#!/usr/bin/env bash\nprintf \'%s\\n\' "$@" > "$DOCKER_ARGS_PATH"\n',
                encoding="utf-8",
            )
            fake_docker.chmod(0o700)
            key_file.write_text("", encoding="utf-8")
            environment = {
                "PATH": f"{root}{os.pathsep}{os.defpath}",
                "DOCKER_ARGS_PATH": str(captured_args),
                "GITHUB_APP_ID": "fixture-app-id",
                "GITHUB_APP_INSTALLATION_ID": "fixture-installation-id",
                "GITHUB_APP_PRIVATE_KEY_PATH": str(key_file),
            }

            completed = subprocess.run(
                ["bash", str(CORE / "runtime/mcp/github-app-stdio.sh")],
                capture_output=True,
                check=False,
                encoding="utf-8",
                env=environment,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            arguments = captured_args.read_text(encoding="utf-8").splitlines()
            self.assertEqual(arguments[:3], ["run", "--rm", "-i"])
            self.assertIn(f"{key_file}:/secrets/github-app.pem:ro", arguments)
            self.assertIn("GITHUB_APP_ID", arguments)
            self.assertIn("GITHUB_APP_INSTALLATION_ID", arguments)
            self.assertIn(
                "GITHUB_APP_PRIVATE_KEY_PATH=/secrets/github-app.pem",
                arguments,
            )
            self.assertNotIn("fixture-app-id", arguments)
            self.assertNotIn("fixture-installation-id", arguments)
            self.assertEqual(
                arguments[-3:],
                [
                    "ghcr.io/github/github-mcp-server:v1.12.2",
                    "stdio",
                    "--read-only",
                ],
            )

    def test_orchestrator_has_an_explicit_default_deny_agent_allowlist(self):
        path = CORE / "com.github.copilot/agents/orchestrator.agent.md"
        text = path.read_text(encoding="utf-8")
        frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(frontmatter_match)
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
        authoring_contract = (
            CORE / "skills/plugin-engineering/workflows/agent-authoring.md"
        ).read_text(encoding="utf-8")
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
        skill_template = (
            plugin_skills
            / "plugin-engineering/references/create-skill/assets/skill-template.md"
        ).read_text(encoding="utf-8")
        workflow_template = (
            plugin_skills
            / "plugin-engineering/references/create-skill/assets/workflow-template.md"
        ).read_text(encoding="utf-8")
        for section in (
            "critical_rules",
            "general_rules",
            "risk_assessment",
            "rules",
            "workflow",
        ):
            self.assertIn(f"<{section}>", skill_template)
            self.assertIn(f"<{section}>", workflow_template)
        self.assertIn("not an independently registered Agent Skill", workflow_template)
        self.assertIn("global route", skill_template)

        skill_maintenance = (
            plugin_skills / "plugin-engineering/workflows/skill-maintenance.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Each immediate subskill keeps its `id`", skill_maintenance)
        self.assertIn("canonical skill body structure", skill_maintenance)
        self.assertIn("peer `SKILL.md` package", skill_maintenance)
        self.assertIn("authoring-patterns.md", skill_maintenance)
        self.assertIn(
            "Preserve useful knowledge, examples, assets, and scripts",
            skill_maintenance,
        )
        self.assertNotIn("Do not add nested workflow metadata", skill_maintenance)

        authoring_patterns = (
            plugin_skills
            / "plugin-engineering/references/create-skill/references/authoring-patterns.md"
        ).read_text(encoding="utf-8")
        skill_authoring = (
            plugin_skills / "plugin-engineering/workflows/skill-authoring.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "Agent → Skill → Workflow → Reference / Asset / Script", authoring_patterns
        )
        self.assertIn(
            "Refactoring a skill into workflows MUST preserve useful domain knowledge",
            authoring_patterns,
        )
        self.assertIn("GOOD/BAD", authoring_patterns)
        self.assertIn(
            "Do not impose example counts, reference counts", authoring_patterns
        )
        self.assertIn("Apply [authoring patterns]", skill_authoring)
        self.assertIn("revalidate versioned material", skill_authoring)

        current_plan = (ROOT / "docs/planner-history/task_5/plan-r10.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "Current authority and historical peer-package artifacts", current_plan
        )
        self.assertIn(
            "do not execute destinations from `workflow-skill-source-map.md`",
            current_plan,
        )
        self.assertIn("`handoffs/TASK-5-03E-architect.md`", current_plan)
        self.assertIn("same canonical body structure as a skill", current_plan)
        composition_handoff = (
            ROOT / "docs/harness-history/task_5/handoffs/TASK-5-03E-architect.md"
        ).read_text(encoding="utf-8")
        self.assertIn("SUPERSEDED by plan r10 and architecture r6", composition_handoff)

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
        workflow_files = sorted(plugin_skills.rglob("workflows/*.md"))
        inventory_path = (
            ROOT / "docs/planner-history/task_5/workflow-subskill-inventory.md"
        )
        inventory_text = inventory_path.read_text(encoding="utf-8")
        inventoried_workflows = {
            path
            for path in re.findall(
                r"`(agentic-core/skills/[^`]+/workflows/[^`]+\.md)`",
                inventory_text,
            )
            if "<" not in path
        }
        self.assertEqual(
            inventoried_workflows,
            {str(path.relative_to(ROOT)) for path in workflow_files},
            "the nested workflows must match the canonical inventory exactly",
        )

        for skill_file in sorted(plugin_skills.glob("*/SKILL.md")):
            router_text = skill_file.read_text(encoding="utf-8")
            linked_workflows = set(
                re.findall(r"\]\(\./workflows/([^)#]+\.md)(?:#[^)]*)?\)", router_text)
            )
            owned_workflows = {
                path.name for path in (skill_file.parent / "workflows").glob("*.md")
            }
            self.assertEqual(
                linked_workflows,
                owned_workflows,
                f"{skill_file} must route to all and only its immediate subskills",
            )

        for skill_name in DOMAIN_SKILLS:
            self.assertFalse(
                (ROOT / ".github/skills" / skill_name / "SKILL.md").is_file(),
                f"{skill_name} must not have an editable workspace duplicate",
            )

        for workflow in workflow_files:
            domain_root = workflow.parent.parent
            workflow_text = workflow.read_text(encoding="utf-8")
            metadata_match = re.match(r"\A---\n(.*?)\n---\n", workflow_text, re.DOTALL)
            self.assertIsNotNone(metadata_match, workflow)
            workflow_metadata = yaml.safe_load(metadata_match.group(1))
            self.assertEqual(workflow_metadata.get("id"), workflow.stem)
            self.assertTrue(workflow_metadata.get("description"), workflow)
            self.assertTrue(workflow_metadata.get("invoke_for"), workflow)
            self.assertIsInstance(workflow_metadata.get("avoid_for"), list)
            self.assertIsInstance(workflow_metadata.get("references"), list)
            workflow_body = workflow_text[metadata_match.end() :]
            structure_lines = []
            inside_code_fence = False
            for line in workflow_body.splitlines():
                if line.startswith("```"):
                    inside_code_fence = not inside_code_fence
                    continue
                if not inside_code_fence:
                    structure_lines.append(line)
            structural_sections = (
                "critical_rules",
                "general_rules",
                "risk_assessment",
                "rules",
                "workflow",
            )
            section_positions = []
            for section in structural_sections:
                self.assertEqual(
                    sum(line.strip() == f"<{section}>" for line in structure_lines),
                    1,
                    f"{workflow} must define one <{section}> block",
                )
                self.assertEqual(
                    sum(line.strip() == f"</{section}>" for line in structure_lines),
                    1,
                    f"{workflow} must close one </{section}> block",
                )
                section_positions.extend(
                    index
                    for index, line in enumerate(structure_lines)
                    if line.strip() in {f"<{section}>", f"</{section}>"}
                )
            self.assertEqual(
                section_positions,
                sorted(section_positions),
                f"{workflow} must match the canonical skill body section order",
            )
            self.assertNotIn(
                "<admission>",
                structure_lines,
                f"{workflow} must leave global admission with its parent domain skill",
            )
            workflow_start = next(
                index
                for index, line in enumerate(structure_lines)
                if line.strip() == "<workflow>"
            )
            workflow_end = next(
                index
                for index, line in enumerate(structure_lines)
                if line.strip() == "</workflow>"
            )
            step_numbers = [
                int(number)
                for number in re.findall(
                    r"(?m)^## Step (\d+)\b",
                    "\n".join(structure_lines[workflow_start + 1 : workflow_end]),
                )
            ]
            self.assertIn(
                step_numbers[0] if step_numbers else None,
                {0, 1},
                f"{workflow} must start with Step 0 or Step 1",
            )
            self.assertEqual(
                step_numbers,
                list(range(step_numbers[0], step_numbers[0] + len(step_numbers)))
                if step_numbers
                else [],
                f"{workflow} must use a complete, ordered step sequence",
            )
            self.assertRegex(workflow_body, r"(?m)^\s*\d+\. ", workflow)
            self.assertNotIn(
                "__routing_probe__.md",
                workflow_text,
                f"{workflow} must not include a benchmark-only routing sentinel",
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
                self.assertTrue(
                    resolved.is_file(),
                    f"{workflow} has missing reference {relative_path}",
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

    def test_mcp_authoring_uses_canonical_rust_contract_and_shared_security(self):
        workflow_dir = CORE / "skills/plugin-engineering/workflows"
        workflow_path = workflow_dir / "create-mcp.md"
        shared_path = (
            CORE
            / "skills/plugin-engineering/references/create-mcp/common-transport-security.md"
        )
        patterns_path = (
            CORE
            / "skills/plugin-engineering/references/create-mcp/rust-server-patterns.md"
        )
        sources_path = (
            CORE / "skills/plugin-engineering/references/create-mcp/references/URIs.md"
        )

        workflow_text = workflow_path.read_text(encoding="utf-8")
        shared_text = shared_path.read_text(encoding="utf-8")
        patterns_text = patterns_path.read_text(encoding="utf-8")
        sources_text = sources_path.read_text(encoding="utf-8")
        general_metadata = yaml.safe_load(
            re.match(r"\A---\n(.*?)\n---\n", workflow_text, re.DOTALL).group(1)
        )
        shared_reference = "../references/create-mcp/common-transport-security.md"
        patterns_reference = "../references/create-mcp/rust-server-patterns.md"
        sources_reference = "../references/create-mcp/references/URIs.md"

        self.assertIn(shared_reference, general_metadata["references"])
        self.assertIn(patterns_reference, general_metadata["references"])
        self.assertIn(sources_reference, general_metadata["references"])
        self.assertIn(
            "MUST implement every new standalone MCP server in Rust", workflow_text
        )
        self.assertIn("official `rmcp` SDK", workflow_text)
        self.assertIn("exact published `rmcp` version", workflow_text)
        self.assertIn("architectural exception", workflow_text)
        self.assertIn("Choose one transport", workflow_text)
        self.assertIn("graceful shutdown", workflow_text)
        self.assertIn("load [Rust server patterns]", workflow_text)
        self.assertIn("reject invalid origins with HTTP 403", shared_text)
        self.assertIn("write protocol frames to stdout", shared_text)
        self.assertIn("write diagnostics to stderr", shared_text)
        self.assertIn("MCP 2026-07-28 transport specification", shared_text)
        self.assertIn("`server/discover` is an optional", shared_text)
        self.assertIn("Do not require `initialize` for every server", shared_text)
        self.assertIn("GOOD", patterns_text)
        self.assertIn("BAD", patterns_text)
        self.assertIn("<PINNED_VERSION>", sources_text)
        self.assertIn("https://docs.rs/rmcp/<PINNED_VERSION>/rmcp/", sources_text)
        domain_router = (CORE / "skills/plugin-engineering/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("[create-mcp](./workflows/create-mcp.md)", domain_router)
        self.assertIn("New standalone MCP servers use Rust", domain_router)

    def test_hook_and_frontend_workflows_keep_host_and_version_boundaries(self):
        hook = (CORE / "skills/plugin-engineering/workflows/create-hook.md").read_text(
            encoding="utf-8"
        )
        frontend = (
            CORE / "skills/software-engineering/workflows/frontend-patterns.md"
        ).read_text(encoding="utf-8")

        self.assertIn("target host's current official hook documentation", hook)
        self.assertIn("do not assume its schema applies to another harness", hook)
        self.assertIn("remote extension host", hook)
        self.assertIn("documented input channel", hook)
        self.assertIn("malformed input when the script accepts input", hook)

        self.assertIn("router (App or Pages)", frontend)
        self.assertIn("App Router", frontend)
        self.assertIn("Pages Router", frontend)
        self.assertIn("Use Context7", frontend)
        self.assertIn("event handlers", frontend)
        self.assertIn("Measure a rendering bottleneck", frontend)

    def test_pack_authoring_workflows_validate_and_build_before_handoff(self):
        workflow_dir = CORE / "skills/plugin-engineering/workflows"
        for filename in ("plugin-creation.md", "plugin-update.md"):
            text = (workflow_dir / filename).read_text(encoding="utf-8")
            self.assertIn("## Step 3 - Validate, build, and return.", text)
            self.assertIn("python -m expertise validate", text)
            self.assertIn("python -m expertise test", text)
            self.assertIn("python -m expertise build", text)

        skill_authoring = (workflow_dir / "skill-authoring.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("<admission>", skill_authoring)

    def test_eval_harness_fails_closed_without_an_enforced_model_call_ceiling(self):
        workflow = (
            CORE / "skills/quality-engineering/workflows/eval-harness.md"
        ).read_text(encoding="utf-8")
        self.assertIn("maximum model-call budget", workflow)
        self.assertIn("stop the invocation before the ceiling is exceeded", workflow)
        self.assertIn("mark the model evaluation blocked", workflow)
        self.assertIn("version the evaluation definition", workflow)
        self.assertIn("durable machine-readable artifact", workflow)
        self.assertIn("MUST NOT be its only durable record", workflow)
        self.assertIn("unknown", workflow)

    def test_multi_harness_workflows_cross_read_each_other(self):
        workflows = CORE / "skills/multi-harness/workflows"
        self.assertTrue(
            {
                "copilot.md",
                "codex.md",
                "same-harness-session-coordination.md",
            }
            <= {path.name for path in workflows.glob("*.md")},
            "paired cross-harness and bounded same-harness procedures must remain present",
        )
        copilot = (workflows / "copilot.md").read_text(encoding="utf-8")
        codex = (workflows / "codex.md").read_text(encoding="utf-8")
        same_harness = (workflows / "same-harness-session-coordination.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("read `./codex.md` first", copilot)
        self.assertIn("read `./copilot.md` first", codex)
        self.assertIn(
            "Read-only status inspection does not authorize a message", same_harness
        )
        self.assertIn("After the user explicitly authorizes contact", same_harness)
        self.assertIn("does not prove the session consumed or answered", same_harness)
        self.assertIn("leave the state `unknown` or `queued`", same_harness)
        self.assertIn("Do not use `codex resume` as a status check", same_harness)
        same_harness = (workflows / "same-harness-session-coordination.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("explicit user authorization", same_harness)
        self.assertIn("codex queue --thread", same_harness)
        self.assertIn("means only `queued`", same_harness)
        self.assertIn("Do not use `codex resume`", same_harness)
        orchestrator = (
            CORE / "com.github.copilot/agents/orchestrator.agent.md"
        ).read_text(encoding="utf-8")
        self.assertIn("load `multi-harness`", orchestrator)
        self.assertIn(
            "bounded same- or cross-harness session coordination", orchestrator
        )
        multi_harness = (CORE / "skills/multi-harness/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("same-harness session coordination", multi_harness)

    def test_context_management_workflows_preserve_bounded_retrieval_and_memory_safety(
        self,
    ):
        context_root = CORE / "skills/context-management"
        retrieval = (context_root / "workflows/iterative-retrieval.md").read_text(
            encoding="utf-8"
        )
        memory_path = context_root / "workflows/memory.md"
        memory = memory_path.read_text(encoding="utf-8")
        memory_metadata = yaml.safe_load(
            re.match(r"\A---\n(.*?)\n---\n", memory, re.DOTALL).group(1)
        )
        compact = (context_root / "workflows/strategic-compact.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("at most three cycles", retrieval)
        self.assertIn("0.7-1.0` is high", retrieval)
        self.assertIn("only `retrieved` evidence may support", retrieval)
        self.assertIn("stop after two hops", memory)
        self.assertIn("user explicitly authorizes the write", memory)
        self.assertEqual(len(memory_metadata["references"]), 2)
        for reference in memory_metadata["references"]:
            self.assertTrue((memory_path.parent / reference).is_file())
        self.assertIn("failed approach that is being abandoned", compact)
        self.assertIn("MUST NOT recommend a reset mid-implementation", compact)
        memory_references = context_root / "references/memory"
        self.assertFalse((memory_references / "method-source.md").exists())
        self.assertFalse(
            (memory_references / "references/karpathy-principles.md").exists()
        )

    def test_api_design_keeps_method_in_workflow_and_patterns_in_reference(self):
        workflow_path = CORE / "skills/architecture/workflows/api-design.md"
        workflow_text = workflow_path.read_text(encoding="utf-8")
        metadata_match = re.match(r"\A---\n(.*?)\n---\n", workflow_text, re.DOTALL)
        self.assertIsNotNone(metadata_match)
        metadata = yaml.safe_load(metadata_match.group(1))
        self.assertEqual(
            metadata["references"],
            ["../references/api-design/api-design-patterns.md"],
        )
        reference_path = (
            CORE / "skills/architecture/references/api-design/api-design-patterns.md"
        )
        reference_text = reference_path.read_text(encoding="utf-8")
        for knowledge_section in (
            "Resource Design",
            "HTTP Methods and Status Codes",
            "Pagination",
            "Filtering, Sorting, and Search",
            "Authentication and Authorization",
            "Rate Limiting",
            "Versioning",
        ):
            self.assertIn(knowledge_section, reference_text)
        self.assertIn("Confirm input validation", workflow_text)
        self.assertNotIn("method-source.md", workflow_text)

    def test_architectural_immune_system_preserves_lenses_and_report_contract(self):
        workflow_path = (
            CORE / "skills/architecture/workflows/architectural-immune-system.md"
        )
        workflow_text = workflow_path.read_text(encoding="utf-8")
        metadata_match = re.match(r"\A---\n(.*?)\n---\n", workflow_text, re.DOTALL)
        self.assertIsNotNone(metadata_match)
        metadata = yaml.safe_load(metadata_match.group(1))
        self.assertEqual(
            metadata["references"],
            ["../references/architectural-immune-system/lenses-and-report.md"],
        )
        guide_path = (
            CORE
            / "skills/architecture/references/architectural-immune-system/lenses-and-report.md"
        )
        guide_text = guide_path.read_text(encoding="utf-8")
        for lens in (
            "Semantic purity",
            "Determinism",
            "Governance erosion",
            "Scale transition",
            "Coupling",
            "Identity drift",
            "Long-horizon entropy",
        ):
            self.assertIn(lens, guide_text)
        self.assertIn("18 months", workflow_text)
        self.assertIn("500 words maximum", workflow_text)
        self.assertIn("ais-report-[timestamp].html", workflow_text)
        self.assertIn("ais-transcript-[timestamp].md", workflow_text)
        self.assertIn("not independent agents", workflow_text)

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
        self.assertIn(
            "MUST NOT be used to repair artifacts or substitute for QA", reviewer
        )

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
            skills
            / "plugin-engineering/references/create-plugin/references/plugin-contract.md"
        ).read_text(encoding="utf-8")

        self.assertIn("local-regex-estimate-v1", token_optimization)
        self.assertIn(
            "The script does not write source files or make network requests",
            token_optimization,
        )
        self.assertIn("advisory only", token_optimization.lower())
        self.assertIn("warning_budget_tokens", token_optimization)
        self.assertIn("pluginctl", install_plugin)
        self.assertIn("trusted source", install_plugin.lower())
        self.assertIn("the caller must identify and approve", install_plugin.lower())
        self.assertIn("canonical CLI", create_plugin)
        self.assertIn("MUST NOT hand-write a substitute", create_plugin)
        self.assertIn("codex", pack_contract.lower())
        self.assertIn("skills remain packaged workflows", pack_contract)

    def test_semantic_modeling_preserves_domain_documentation_boundaries(self):
        semantic_skill = (CORE / "skills/semantic-modeling/SKILL.md").read_text(
            encoding="utf-8"
        )
        semantic_workflow = (
            CORE / "skills/semantic-modeling/workflows/problem-space.md"
        ).read_text(encoding="utf-8")

        self.assertIn("SPEC.semantic_model` is the only canonical", semantic_skill)
        self.assertIn("MAY propose durable glossary or ADR updates", semantic_skill)
        self.assertIn("materially costly", semantic_skill)
        self.assertIn("future readers would not infer", semantic_skill)
        self.assertIn("a real alternative was selected for a reason", semantic_skill)
        self.assertIn("If the handoff explicitly authorizes an ADR", semantic_workflow)
        self.assertIn("established ADR location and format", semantic_workflow)

    def test_security_controls_reference_preserves_review_coverage(self):
        security_controls = (
            CORE / "skills/security/references/security-review/security-controls.md"
        ).read_text(encoding="utf-8")

        for review_area in (
            "## Identity and authorization",
            "## Input, injection, and uploads",
            "## Secrets, data exposure, and errors",
            "## Browser-facing controls",
            "## Outbound requests and SSRF",
            "## Abuse limits and dependency evidence",
            "## Evidence and disposition",
        ):
            with self.subTest(review_area=review_area):
                self.assertIn(review_area, security_controls)

        self.assertIn("specific object and action", security_controls)
        self.assertIn("- XSS:", security_controls)
        self.assertIn("- CSRF:", security_controls)
        self.assertIn("Session cookies", security_controls)
        self.assertIn("Cross-Origin Resource Sharing (CORS)", security_controls)
        self.assertIn("public, non-credentialed access", security_controls)
        self.assertIn("wildcard origin MUST NOT be combined", security_controls)
        self.assertIn("`Vary: Origin`", security_controls)
        self.assertIn("CORS is not authentication or authorization", security_controls)
        self.assertIn(
            "validate the resolved address and every redirect", security_controls
        )
        self.assertIn("not proof that all dependencies are safe", security_controls)

    def test_operations_workflows_preserve_removed_method_source_contracts(self):
        operations_skill = (CORE / "skills/operations/SKILL.md").read_text(
            encoding="utf-8"
        )
        delivery = (
            CORE / "skills/operations/workflows/delivery-operations.md"
        ).read_text(encoding="utf-8")
        documentation = (
            CORE / "skills/operations/workflows/documentation-sync.md"
        ).read_text(encoding="utf-8")
        install = (
            CORE / "skills/operations/workflows/install-agent-plugin.md"
        ).read_text(encoding="utf-8")
        verification = (
            CORE / "skills/operations/workflows/verification-loop.md"
        ).read_text(encoding="utf-8")

        for procedure in (
            "delivery-operations",
            "documentation-sync",
            "install-agent-plugin",
            "verification-loop",
        ):
            self.assertIn(
                f"[{procedure}](./workflows/{procedure}.md)", operations_skill
            )
        self.assertIn("deployment as blocked until authorization", delivery)
        self.assertIn("rollout/rollback/monitoring guidance", delivery)
        self.assertIn("unsupported product claim", documentation)
        self.assertIn("only the assigned documentation sections", documentation)
        self.assertIn(
            "The installation request itself authorizes the requested installation only",
            install,
        )
        self.assertIn("available, installed, active, or loaded", install)
        self.assertIn("READY` only when all applicable gates pass", verification)
        self.assertIn("NOT READY", verification)

    def test_qa_routes_hidden_end_to_end_specialty_through_testing(self):
        qa = (CORE / "com.github.copilot/agents/quality-assurance.agent.md").read_text(
            encoding="utf-8"
        )
        testing = (CORE / "skills/quality-engineering/SKILL.md").read_text(
            encoding="utf-8"
        )
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
            CORE / "skills/software-engineering/workflows/concurrency-design.md"
        ).read_text(encoding="utf-8")
        implementation = (CORE / "skills/software-engineering/SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("load `software-engineering`", implementer)
        self.assertIn(
            "MUST load `quality-engineering` when designing or materially changing tests",
            implementer,
        )
        self.assertIn(
            "MUST load `software-engineering` for testable behavior changes",
            implementer,
        )
        self.assertIn("For concurrent behavior", boundaries)
        self.assertIn(
            "../references/testing/references/equivalence-boundaries.md", test_design
        )
        self.assertIn("deterministic barriers", test_design)
        self.assertIn("[concurrency-design]", implementation)
        self.assertIn("allowed interleavings", concurrency_design)

    def test_testing_and_implementation_design_keep_distinct_method_owners(self):
        implementer = (
            CORE / "com.github.copilot/agents/implementer.agent.md"
        ).read_text(encoding="utf-8")
        reviewer = (CORE / "com.github.copilot/agents/reviewer.agent.md").read_text(
            encoding="utf-8"
        )
        architect = (CORE / "com.github.copilot/agents/architect.agent.md").read_text(
            encoding="utf-8"
        )
        testing = (
            CORE / "skills/quality-engineering/workflows/test-design.md"
        ).read_text(encoding="utf-8")
        tdd = (CORE / "skills/software-engineering/workflows/tdd.md").read_text(
            encoding="utf-8"
        )
        design = (
            CORE / "skills/software-engineering/workflows/representation-selection.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "MUST load `software-engineering` for testable behavior changes",
            implementer,
        )
        self.assertIn(
            "SHOULD load `software-engineering` when a non-trivial local", reviewer
        )
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

    def test_installed_skill_script_docs_use_skill_relative_paths_and_explicit_workspace_paths(
        self,
    ):
        orchestrate_path = CORE / "skills/orchestration/workflows/orchestrate.md"
        sdd_path = CORE / "skills/orchestration/workflows/spec-driven-development.md"
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
