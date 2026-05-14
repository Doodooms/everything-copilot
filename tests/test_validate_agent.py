import subprocess
import sys
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / ".github" / "skills" / "create-agent" / "scripts" / "validate_agent.py"


def test_validator_accepts_canonical_agent_structure(tmp_path: Path) -> None:
    agent_file = _write_agent(tmp_path, _canonical_agent_body())

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 0, (result.stdout + result.stderr).strip()


def test_validator_accepts_heading_only_agent_without_xml_wrappers(tmp_path: Path) -> None:
    agent_file = _write_agent(tmp_path, _legacy_agent_body())

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 0, (result.stdout + result.stderr).strip()


def test_validator_rejects_agent_missing_core_sections(tmp_path: Path) -> None:
    agent_file = _write_agent(tmp_path, _agent_body_missing_output_contract())

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1, (result.stdout + result.stderr).strip()
    assert "## Output Contract" in result.stdout


def test_validator_rejects_wrong_layer_tool_name(tmp_path: Path) -> None:
    agent_file = _write_agent(
        tmp_path,
        _canonical_agent_body(tools_line="tools: [vscode_askQuestions]"),
    )

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1, (result.stdout + result.stderr).strip()
    assert "workspace tool catalog" in result.stdout
    assert "vscode/askQuestions" in result.stdout


def test_validator_rejects_unknown_allowed_subagent(tmp_path: Path) -> None:
    agent_file = _write_agent(
        tmp_path,
        _canonical_agent_body(
            tools_line="tools: [read, agent]",
            extra_frontmatter="agents: [missing-helper]",
        ),
    )

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1, (result.stdout + result.stderr).strip()
    assert "unknown workspace agent" in result.stdout
    assert "missing-helper" in result.stdout


def test_validator_warns_on_broad_agent_tool_without_allowlist(tmp_path: Path) -> None:
    agent_file = _write_agent(
        tmp_path,
        _canonical_agent_body(tools_line="tools: [read, agent]"),
    )

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 0, (result.stdout + result.stderr).strip()
    assert "broad without an `agents` allowlist" in result.stdout


def _run_validator(cwd: Path, agent_file: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), "--agent-file", str(agent_file)],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _write_agent(root: Path, body: str) -> Path:
    agent_dir = root / ".github" / "agents"
    agent_dir.mkdir(parents=True, exist_ok=True)
    agent_file = agent_dir / "structured-agent.agent.md"
    agent_file.write_text(body, encoding="utf-8")
    return agent_file


def _canonical_agent_body(
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


def _legacy_agent_body() -> str:
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


def _agent_body_missing_output_contract() -> str:
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