import subprocess
import sys
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / ".github" / "skills" / "create-agent" / "scripts" / "validate_agent.py"


def test_validator_accepts_canonical_agent_structure(tmp_path: Path) -> None:
    agent_file = _write_agent(
        tmp_path,
        _canonical_agent_body(),
        nested=True,
        with_routing_refs=True,
    )

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 0, (result.stdout + result.stderr).strip()


def test_validator_rejects_partial_rules_wrapper(tmp_path: Path) -> None:
    agent_file = _write_agent(tmp_path, _agent_body_with_partial_rules_wrapper())

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1, (result.stdout + result.stderr).strip()
    assert "either omit `<rules>` entirely or use both `<rules>` and `</rules>`" in result.stdout


def test_validator_rejects_canonical_agent_without_package_directory(tmp_path: Path) -> None:
    agent_file = _write_agent(tmp_path, _canonical_agent_body())

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1, (result.stdout + result.stderr).strip()
    assert "must live in a dedicated package directory" in result.stdout


def test_validator_rejects_canonical_agent_missing_routing_support_files(tmp_path: Path) -> None:
    agent_file = _write_agent(tmp_path, _canonical_agent_body(), nested=True)

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1, (result.stdout + result.stderr).strip()
    assert "must include a sibling routing file" in result.stdout


def test_validator_rejects_malformed_step_heading_contract(tmp_path: Path) -> None:
    agent_file = _write_agent(
        tmp_path,
        _agent_body_with_skill_steps(),
        nested=True,
        with_routing_refs=True,
    )

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1, (result.stdout + result.stderr).strip()
    assert "must keep headings in this order" in result.stdout


def test_validator_rejects_role_wrapper(tmp_path: Path) -> None:
    agent_file = _write_agent(tmp_path, _agent_body_with_role_wrapper())

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1, (result.stdout + result.stderr).strip()
    assert "must not use `<role>` wrappers" in result.stdout


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
        nested=True,
        with_routing_refs=True,
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
        nested=True,
        with_routing_refs=True,
    )

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1, (result.stdout + result.stderr).strip()
    assert "unknown workspace agent" in result.stdout
    assert "missing-helper" in result.stdout


def test_validator_warns_on_broad_agent_tool_without_allowlist(tmp_path: Path) -> None:
    agent_file = _write_agent(
        tmp_path,
        _canonical_agent_body(tools_line="tools: [read, agent]"),
        nested=True,
        with_routing_refs=True,
    )

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 0, (result.stdout + result.stderr).strip()
    assert "broad without an `agents` allowlist" in result.stdout


def test_validator_rejects_canonical_agent_without_json_refusal(tmp_path: Path) -> None:
    agent_file = _write_agent(
        tmp_path,
        _canonical_agent_body(use_json_refusal=False),
        nested=True,
        with_routing_refs=True,
    )

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1, (result.stdout + result.stderr).strip()
    assert "JSON refusal response" in result.stdout


def _run_validator(cwd: Path, agent_file: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), "--agent-file", str(agent_file)],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _write_agent(
    root: Path,
    body: str,
    *,
    nested: bool = False,
    with_routing_refs: bool = False,
) -> Path:
    agents_root = root / ".github" / "agents"
    agents_root.mkdir(parents=True, exist_ok=True)
    if nested:
        agent_dir = agents_root / "structured-agent"
        agent_dir.mkdir(parents=True, exist_ok=True)
    else:
        agent_dir = agents_root

    agent_file = agent_dir / "structured-agent.agent.md"
    agent_file.write_text(body, encoding="utf-8")

    if with_routing_refs:
        references_dir = agent_dir / "references"
        references_dir.mkdir(parents=True, exist_ok=True)
        (references_dir / "USEFOR.md").write_text(
            "# WHEN TO USE\n\n- Summarize validated release changes.\n",
            encoding="utf-8",
        )
        (references_dir / "DONOTUSEFOR.md").write_text(
            "# WHEN NOT TO USE\n\n- Implement or refactor code.\n",
            encoding="utf-8",
        )

    return agent_file


def _canonical_agent_body(
    *,
    description: str = "WHAT: Produce deterministic role-scoped output. USE FOR: validating the canonical custom agent contract. DO NOT USE FOR: implementation work, broad repository refactors, or unrelated agent design.",
    tools_line: str = "tools: [read, search]",
    extra_frontmatter: str = "",
    use_json_refusal: bool = True,
) -> str:
    extra_frontmatter_block = f"{extra_frontmatter}\n" if extra_frontmatter else ""
    refusal_payload = (
        '`{"status": "refused", "agent": "Structured Agent", "reason": "this request asks for implementation, not structured summary output.", "suggested_alternative": "dev"}`'
        if use_json_refusal
        else '`Agent Structured Agent cannot handle this task. Reason: this request asks for implementation, not structured summary output. Suggested alternative: dev.`'
    )
    output_contract_refusal = (
        '`{"status": "refused", "agent": "Structured Agent", "reason": "<specific reason>", "suggested_alternative": "<agent or skill>"}`'
        if use_json_refusal
        else '`Agent Structured Agent cannot handle this task. Reason: <specific reason>. Suggested alternative: <agent or skill>.`'
    )
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
        - **routing refusal** : The explicit Step 0 result when this agent should not handle the task.

        </definitions>

        <workflow>

        ## Step 0 - **CONFIRMATION**

        1. USE #tool:read **IMMEDIATELY** on #file:./references/USEFOR.md and **IMMEDIATELY** on #file:./references/DONOTUSEFOR.md to confirm with certainty if this agent should be used.
        2. If the task does not match, return: {refusal_payload}
        3. If the task matches, continue to Step 1.

        ## Role

        You are the Structured Agent agent. You perform one focused role and stay inside that boundary.

        <rules>

        ## Responsibilities

        - Gather only the context needed for the assigned task.
        - Produce the artifact this role owns without drifting into adjacent work.

        ## Constraints

        - Do not exceed the role described above.
        - Escalate or hand off when another specialist is required.

        ## Output Contract

        - If Step 0 rejects the task, return: {output_contract_refusal}
        - Return a concise, role-scoped result for the caller.
        - State blockers or handoff conditions explicitly when needed.

        </rules>

        ## Step 1 - Gather only the context needed for the task.

        1. Read only the validated files and inputs named in the task.
        2. Ignore unrelated repository surfaces that do not affect the requested result.

        ## Step 2 - Apply the role-specific method using the declared tools.

        1. Synthesize the approved source material into the artifact this role owns.
        2. Escalate only if the task requires a different specialist or broader permissions.

        ## Step 3 - Return the promised result without drifting into adjacent work.

        1. Return the requested role-scoped result.
        2. State blockers or the suggested handoff explicitly when needed.

        </workflow>
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


def _agent_body_with_partial_rules_wrapper() -> str:
    return textwrap.dedent(
        """
        ---
        name: partial-rules-agent
        description: "What: Exercise partial rules wrapper handling. Use when: tests need a malformed wrapped agent body."
        target: vscode
        tools: [read]
        ---

        <definitions>

        - **focused role** : A malformed wrapper test agent.

        </definitions>

        # Role

        You are the Partial Rules agent.

        ## Responsibilities

        - Keep the body mostly valid while leaving one wrapper incomplete.

        <workflow>

        ## Workflow

        1. Read the task.
        2. Return the result.

        </workflow>

        <rules>

        ## Constraints

        - This file intentionally omits the closing rules wrapper.

        ## Output Contract

        - Return a draft.
        """
    ).strip() + "\n"


def _agent_body_with_skill_steps() -> str:
    return textwrap.dedent(
        """
        ---
        name: skill-steps-agent
        description: "What: Exercise skill-step leakage handling. Use when: tests need a generated agent with the wrong workflow shape."
        target: vscode
        tools: [read]
        ---

        <definitions>

        - **focused role** : A malformed canonical agent.

        </definitions>

        <workflow>

        ## Step 0 - **CONFIRMATION**

        1. USE #tool:read on #file:./references/USEFOR.md and #file:./references/DONOTUSEFOR.md.

        ## Role

        You are the Skill Steps agent.

        <rules>

        ## Responsibilities

        - Keep the body otherwise valid while using the wrong step heading casing.

        ## Constraints

        - This file intentionally uses invalid step headings.

        ## Output Contract

        - Return a draft.

        </rules>

        ## STEP 1 - Inspect the task

        1. Read the task.

        ## STEP 2 - Apply the role-specific method

        1. Try to continue.

        ## STEP 3 - Return the result

        1. Return a draft.

        </workflow>
        """
    ).strip() + "\n"


def _agent_body_with_role_wrapper() -> str:
    return textwrap.dedent(
        """
        ---
        name: wrapped-role-agent
        description: "What: Exercise forbidden role wrapper handling. Use when: tests need a generated agent with invalid wrapper tags."
        target: vscode
        tools: [read]
        ---

        <role>

        # Role

        You are the Wrapped Role agent.

        </role>

        ## Responsibilities

        - Keep the rest of the structure valid.

        ## Workflow

        1. Read the task.
        2. Return the result.

        ## Constraints

        - This file intentionally wraps the role section.

        ## Output Contract

        - Return a draft.
        """
    ).strip() + "\n"