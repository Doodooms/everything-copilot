import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / ".github" / "skills" / "create-agent" / "scripts" / "validate_agent.py"


class ValidateAgentTest(unittest.TestCase):
    def test_validator_accepts_canonical_agent_structure(self) -> None:
        with tempfile.TemporaryDirectory(prefix="agent-validator-") as temp_dir:
            temp_root = Path(temp_dir)
            agent_file = self._write_agent(temp_root, self._canonical_agent_body())

            result = self._run_validator(temp_root, agent_file)

        self.assertEqual(result.returncode, 0, msg=(result.stdout + result.stderr).strip())

    def test_validator_accepts_heading_only_agent_without_xml_wrappers(self) -> None:
        with tempfile.TemporaryDirectory(prefix="agent-validator-") as temp_dir:
            temp_root = Path(temp_dir)
            agent_file = self._write_agent(temp_root, self._legacy_agent_body())

            result = self._run_validator(temp_root, agent_file)

        self.assertEqual(result.returncode, 0, msg=(result.stdout + result.stderr).strip())

    def test_validator_rejects_agent_missing_core_sections(self) -> None:
        with tempfile.TemporaryDirectory(prefix="agent-validator-") as temp_dir:
            temp_root = Path(temp_dir)
            agent_file = self._write_agent(temp_root, self._agent_body_missing_output_contract())

            result = self._run_validator(temp_root, agent_file)

        self.assertEqual(result.returncode, 1, msg=(result.stdout + result.stderr).strip())
        self.assertIn("## Output Contract", result.stdout)

    def test_validator_rejects_wrong_layer_tool_name(self) -> None:
        with tempfile.TemporaryDirectory(prefix="agent-validator-") as temp_dir:
            temp_root = Path(temp_dir)
            agent_file = self._write_agent(
                temp_root,
                self._canonical_agent_body(tools_line="tools: [vscode_askQuestions]"),
            )

            result = self._run_validator(temp_root, agent_file)

        self.assertEqual(result.returncode, 1, msg=(result.stdout + result.stderr).strip())
        self.assertIn("workspace tool catalog", result.stdout)
        self.assertIn("vscode/askQuestions", result.stdout)

    def test_validator_rejects_unknown_allowed_subagent(self) -> None:
        with tempfile.TemporaryDirectory(prefix="agent-validator-") as temp_dir:
            temp_root = Path(temp_dir)
            agent_file = self._write_agent(
                temp_root,
                self._canonical_agent_body(
                    tools_line="tools: [read, agent]",
                    extra_frontmatter="agents: [missing-helper]",
                ),
            )

            result = self._run_validator(temp_root, agent_file)

        self.assertEqual(result.returncode, 1, msg=(result.stdout + result.stderr).strip())
        self.assertIn("unknown workspace agent", result.stdout)
        self.assertIn("missing-helper", result.stdout)

    def test_validator_warns_on_broad_agent_tool_without_allowlist(self) -> None:
        with tempfile.TemporaryDirectory(prefix="agent-validator-") as temp_dir:
            temp_root = Path(temp_dir)
            agent_file = self._write_agent(
                temp_root,
                self._canonical_agent_body(tools_line="tools: [read, agent]"),
            )

            result = self._run_validator(temp_root, agent_file)

        self.assertEqual(result.returncode, 0, msg=(result.stdout + result.stderr).strip())
        self.assertIn("broad without an `agents` allowlist", result.stdout)

    def _run_validator(self, cwd: Path, agent_file: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), "--agent-file", str(agent_file)],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )

    def _write_agent(self, root: Path, body: str) -> Path:
        agent_dir = root / ".github" / "agents"
        agent_dir.mkdir(parents=True, exist_ok=True)
        agent_file = agent_dir / "structured-agent.agent.md"
        agent_file.write_text(body, encoding="utf-8")
        return agent_file

    def _canonical_agent_body(
        self,
        *,
        description: str = "What: Produce deterministic role-scoped output. Use when: validating the canonical custom agent contract.",
        tools_line: str = "tools: [read, search]",
        extra_frontmatter: str = "",
    ) -> str:
        extra_frontmatter_block = f"{extra_frontmatter}\n" if extra_frontmatter else ""
        return textwrap.dedent(
            f"""
            ---
            name: structured-agent
            description: "{description}"
            target: vscode
            {tools_line}
            {extra_frontmatter_block}---

            <definitions>

            - **focused role** : The single job this agent owns from start to finish.
            - **output contract** : The exact result shape the agent must return to its caller.

            </definitions>

            # Role

            You are the Structured Agent agent. You perform one focused role and stay inside that boundary.

            ## Responsibilities

            - Gather only the context needed for the assigned task.
            - Produce the artifact this role owns without drifting into adjacent work.


            <workflow>

            ## Workflow

            1. Read only the files, symbols, or user inputs required for the task at hand.
            2. Apply the role-specific method using the approved tools and constraints.
            3. Return the final result in the exact shape promised below.

            </workflow>

            ## Constraints

            - Do not exceed the role described above.
            - Escalate or hand off when another specialist is required.

            ## Output Contract

            - Return a concise, role-scoped result for the caller.
            - State blockers or handoff conditions explicitly when needed.
            """
        ).strip() + "\n"

    def _legacy_agent_body(self) -> str:
        return textwrap.dedent(
            """
            ---
            name: legacy-agent
            description: "What: Preserve the old loose structure. Use when: tests need a structurally invalid agent."
            target: vscode
            tools: [read]
            ---

            # Role

            You are the Legacy agent.

            ## Responsibilities

            - Keep the older heading-only layout.

            ## Workflow

            1. Read the task.
            2. Return the result.

            ## Constraints

            - This body intentionally uses only the human-facing headings.

            ## Output Contract

            - Return a draft.
            """
        ).strip() + "\n"

    def _agent_body_missing_output_contract(self) -> str:
        return textwrap.dedent(
            """
            ---
            name: incomplete-agent
            description: "What: Exercise missing core section handling. Use when: tests need a structurally incomplete agent."
            target: vscode
            tools: [read]
            ---

            # Role

            You are the Incomplete agent.

            ## Responsibilities

            - Keep the workflow present while omitting one required section.

            ## Workflow

            1. Read the task.
            2. Perform the assigned work.

            ## Constraints

            - This file is intentionally invalid.
            """
        ).strip() + "\n"


if __name__ == "__main__":
    unittest.main()