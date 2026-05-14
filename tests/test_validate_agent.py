import subprocess
import sys
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = (
    REPO_ROOT / ".github" / "skills" / "create-agent" / "scripts" / "validate_agent.py"
)


def test_validator_accepts_canonical_self_contained_agent_structure(tmp_path: Path) -> None:
    agent_file = _write_agent(tmp_path, _canonical_agent_body())

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Validation passed." in result.stdout


def test_validator_rejects_partial_rules_wrapper(tmp_path: Path) -> None:
    agent_file = _write_agent(tmp_path, _agent_body_with_partial_rules_wrapper())

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1
    assert "either omit `<rules>` entirely or use both `<rules>` and `</rules>`" in result.stdout


def test_validator_rejects_canonical_agent_missing_embedded_routing_sections(tmp_path: Path) -> None:
    agent_file = _write_agent(tmp_path, _agent_body_missing_embedded_routing_sections())

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1
    assert "embed `### USE FOR` plus `### DO **NOT** USE FOR`" in result.stdout


def test_validator_accepts_legacy_routing_file_agent_when_support_files_exist(tmp_path: Path) -> None:
    agent_file = _write_agent(
        tmp_path,
        _canonical_agent_body(use_embedded_routing=False),
        nested=True,
        with_routing_refs=True,
    )

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "legacy sibling routing files" in result.stdout


def test_validator_rejects_legacy_routing_file_agent_without_support_files(tmp_path: Path) -> None:
    agent_file = _write_agent(
        tmp_path,
        _canonical_agent_body(use_embedded_routing=False),
        nested=True,
        with_routing_refs=False,
    )

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1
    assert "legacy routing files must include a sibling routing file" in result.stdout


def test_validator_rejects_malformed_step_heading_contract(tmp_path: Path) -> None:
    agent_file = _write_agent(tmp_path, _agent_body_with_skill_steps())

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1
    assert "must keep headings in this order" in result.stdout


def test_validator_rejects_role_wrapper(tmp_path: Path) -> None:
    agent_file = _write_agent(tmp_path, _agent_body_with_role_wrapper())

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1
    assert "should not wrap content in a `<role>` block" in result.stdout


def test_validator_accepts_heading_only_legacy_agent_without_xml_wrappers(tmp_path: Path) -> None:
    agent_file = _write_agent(tmp_path, _legacy_agent_body())

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Validation passed." in result.stdout


def test_validator_rejects_agent_missing_core_sections(tmp_path: Path) -> None:
    body = textwrap.dedent(
        """
        # Role

        You are the structured-agent. Do the job.

        ## Step 1

        1. Do work.
        """
    ).strip()
    agent_file = _write_agent(tmp_path, body)

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1
    assert "Agent markdown body is missing expected sections" in result.stdout


def test_validator_rejects_wrong_layer_tool_name(tmp_path: Path) -> None:
    agent_file = _write_agent(
        tmp_path,
        _canonical_agent_body(tools_line="tools: [read, run_in_terminal]"),
    )

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1
    assert "Tool `run_in_terminal` is not recognized" in result.stdout
    assert "workspace tool catalog" in result.stdout
    assert "Wrong-layer raw tool name detected" in result.stdout
    assert "execute" in result.stdout


def test_validator_rejects_unknown_allowed_subagent(tmp_path: Path) -> None:
    agent_file = _write_agent(
        tmp_path,
        _canonical_agent_body(
            extra_frontmatter="agents:\n  - implementer\n  - ghost-agent",
        ),
    )

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1
    assert "lists unknown agent `ghost-agent`" in result.stdout


def test_validator_warns_on_broad_agent_tool_without_allowlist(tmp_path: Path) -> None:
    agent_file = _write_agent(
        tmp_path,
        _canonical_agent_body(tools_line="tools: [read, agent]"),
    )

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Tool `agent` is broad" in result.stdout
    assert "declare an `agents:` allowlist" in result.stdout


def test_validator_rejects_canonical_agent_without_json_refusal(tmp_path: Path) -> None:
    agent_file = _write_agent(
        tmp_path,
        _canonical_agent_body(
            refusal_payload="`stop and ask the caller for clarification`",
            output_refusal_payload="`stop and ask the caller for clarification`",
        ),
    )

    result = _run_validator(tmp_path, agent_file)

    assert result.returncode == 1
    assert "must return a refusal JSON object before continuing" in result.stdout


def _run_validator(workspace: Path, agent_file: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), "--agent-file", str(agent_file)],
        cwd=workspace,
        capture_output=True,
        text=True,
        check=False,
    )


def _write_agent(
    workspace: Path,
    body: str,
    *,
    nested: bool = False,
    with_routing_refs: bool = False,
) -> Path:
    if nested:
        agent_dir = workspace / ".github" / "agents" / "structured-agent"
        agent_dir.mkdir(parents=True, exist_ok=True)
        agent_file = agent_dir / "structured-agent.agent.md"
        if with_routing_refs:
            refs_dir = agent_dir / "references"
            refs_dir.mkdir(parents=True, exist_ok=True)
            (refs_dir / "USEFOR.md").write_text("- Legacy routing example.\n", encoding="utf-8")
            (refs_dir / "DONOTUSEFOR.md").write_text("- Legacy refusal example.\n", encoding="utf-8")
    else:
        agent_dir = workspace / ".github" / "agents"
        agent_dir.mkdir(parents=True, exist_ok=True)
        agent_file = agent_dir / "structured-agent.agent.md"

    frontmatter = textwrap.dedent(
        """
        ---
        name: structured-agent
        description: "WHAT: Handle structured work. USE FOR: structured work requests. DO NOT USE FOR: unrelated requests."
        tools: [read]
        ---
        """
    ).strip()
    agent_file.write_text(frontmatter + "\n\n" + body.strip() + "\n", encoding="utf-8")
    return agent_file


def _canonical_agent_body(
    *,
    tools_line: str = "tools: [read]",
    extra_frontmatter: str = "",
    refusal_payload: str | None = None,
    output_refusal_payload: str | None = None,
    use_embedded_routing: bool = True,
) -> str:
    refusal_payload = (
        refusal_payload
        or '`{"status": "refused", "agent": "structured-agent", "reason": "this request is outside the structured-agent role", "suggested_alternative": "implementer"}`'
    )
    output_refusal_payload = output_refusal_payload or refusal_payload

    routing_block = textwrap.dedent(
        f"""
        1. Check the routing surface to confirm this agent is the right fit for the task.

        ### USE FOR

        - Requests that match the structured-agent role.

        ### DO **NOT** USE FOR

        - Implementation work, refactors, or unrelated requests.

        2. If the task does not match, return: {refusal_payload}.
        3. If the task matches, continue to Step 1.
        """
    ).strip()
    if not use_embedded_routing:
        routing_block = textwrap.dedent(
            f"""
            1. Use #tool:read on #file:./references/USEFOR.md and #file:./references/DONOTUSEFOR.md before doing anything else.
            2. If the task does not match, return: {refusal_payload}.
            3. If the task matches, continue to Step 1.
            """
        ).strip()

    frontmatter_lines = [
        "---",
        "name: structured-agent",
        'description: "WHAT: Handle structured work. USE FOR: structured work requests. DO NOT USE FOR: unrelated requests."',
        tools_line,
    ]
    if extra_frontmatter:
        frontmatter_lines.append(extra_frontmatter)
    frontmatter_lines.append("---")
    frontmatter = "\n".join(frontmatter_lines)

    body = textwrap.dedent(
        f"""
        {frontmatter}

        <definitions>

        - **focused role** : Handle structured work for the caller.
        - **routing refusal** : The explicit Step 0 result when this agent should not handle the task.

        </definitions>

        <workflow>

        ## Step 0 - **CONFIRMATION**

        {routing_block}

        ## Role

        You are the structured-agent. Your job is to handle structured work and stop at that boundary.

        <rules>

        ## Responsibilities

        - Gather only the context needed for the request.
        - Return the role-specific result without drifting into adjacent work.

        ## Constraints

        - Do not invent facts.
        - Do not edit files unless that is part of the declared role.

        ## Output Contract

        - If Step 0 rejects the task, return: {output_refusal_payload}.
        - Return the requested structured result and call out blockers explicitly.

        </rules>

        ## Step 1 - Gather only the context needed for the task.

        1. Read only the files and notes needed for the task.
        2. Ignore unrelated surfaces.

        ## Step 2 - Apply the role-specific method using the declared tools.

        1. Produce the role-specific result.
        2. Escalate only when another specialist is required.

        ## Step 3 - Return the promised result without drifting into adjacent work.

        1. Return the answer in the format declared above.
        2. State blockers or the handoff explicitly when needed.

        </workflow>
        """
    ).strip()
    return body


def _legacy_agent_body() -> str:
    return textwrap.dedent(
        """
        # Role

        You are the structured-agent. Handle structured work for the caller.

        ## Responsibilities

        - Gather only the context needed for the task.
        - Produce the structured result the caller requested.

        ## Constraints

        - Do not edit files.
        - Do not invent facts.

        ## Output Contract

        - Return the structured result.
        - State blockers explicitly when needed.

        ## Step 1

        1. Read only the relevant source material.
        2. Ignore unrelated surfaces.

        ## Step 2

        1. Apply the role-specific method.
        2. Keep the response grounded in the reviewed material.

        ## Step 3

        1. Return the requested result.
        2. Note any blockers.
        """
    ).strip()


def _agent_body_with_partial_rules_wrapper() -> str:
    return textwrap.dedent(
        """
        <definitions>

        - **focused role** : Handle structured work.
        - **routing refusal** : The explicit Step 0 refusal.

        </definitions>

        <workflow>

        ## Step 0 - **CONFIRMATION**

        1. Check the routing surface to confirm this agent is the right fit for the task.

        ### USE FOR

        - Requests that match the structured-agent role.

        ### DO **NOT** USE FOR

        - Implementation work, refactors, or unrelated requests.

        2. If the task does not match, return: `{"status": "refused", "agent": "structured-agent", "reason": "outside scope", "suggested_alternative": "implementer"}`.
        3. If the task matches, continue to Step 1.

        ## Role

        You are the structured-agent.

        <rules>

        ## Responsibilities

        - Gather only the context needed for the task.

        ## Constraints

        - Do not invent facts.

        ## Output Contract

        - Return the requested result.

        ## Step 1 - Gather the minimum relevant context.

        1. Read only the relevant source material.

        ## Step 2 - Apply the role-specific method.

        1. Produce the role-specific result.

        ## Step 3 - Return the promised result.

        1. Return the answer.

        </workflow>
        """
    ).strip()


def _agent_body_with_skill_steps() -> str:
    return textwrap.dedent(
        """
        <definitions>

        - **focused role** : Handle structured work.
        - **routing refusal** : The explicit Step 0 refusal.

        </definitions>

        <workflow>

        ## Step 0 - **CONFIRMATION**

        1. Check the routing surface to confirm this agent is the right fit for the task.

        ### USE FOR

        - Requests that match the structured-agent role.

        ### DO **NOT** USE FOR

        - Implementation work, refactors, or unrelated requests.

        2. If the task does not match, return: `{"status": "refused", "agent": "structured-agent", "reason": "outside scope", "suggested_alternative": "implementer"}`.
        3. If the task matches, continue to Step 1.

        ## Role

        You are the structured-agent.

        <rules>

        ## Responsibilities

        - Gather only the context needed for the task.

        ## Constraints

        - Do not invent facts.

        ## Output Contract

        - Return the requested result.

        </rules>

        ## STEP 1

        1. Gather context.

        ## STEP 2

        1. Produce the result.

        ## STEP 3

        1. Return the result.

        </workflow>
        """
    ).strip()


def _agent_body_with_role_wrapper() -> str:
    return textwrap.dedent(
        """
        <role>

        # Role

        You are the structured-agent.

        </role>

        ## Responsibilities

        - Gather only the context needed for the task.

        ## Constraints

        - Do not invent facts.

        ## Output Contract

        - Return the requested result.

        ## Step 1

        1. Gather context.

        ## Step 2

        1. Produce the result.

        ## Step 3

        1. Return the result.
        """
    ).strip()


def _agent_body_missing_embedded_routing_sections() -> str:
    return textwrap.dedent(
        """
        <definitions>

        - **focused role** : Handle structured work.
        - **routing refusal** : The explicit Step 0 refusal.

        </definitions>

        <workflow>

        ## Step 0 - **CONFIRMATION**

        1. Check the routing surface to confirm this agent is the right fit for the task.
        2. If the task does not match, return: `{"status": "refused", "agent": "structured-agent", "reason": "outside scope", "suggested_alternative": "implementer"}`.
        3. If the task matches, continue to Step 1.

        ## Role

        You are the structured-agent.

        <rules>

        ## Responsibilities

        - Gather only the context needed for the task.

        ## Constraints

        - Do not invent facts.

        ## Output Contract

        - Return the requested result.

        </rules>

        ## Step 1 - Gather the minimum relevant context.

        1. Read only the relevant source material.

        ## Step 2 - Apply the role-specific method.

        1. Produce the role-specific result.

        ## Step 3 - Return the promised result.

        1. Return the answer.

        </workflow>
        """
    ).strip()
