import subprocess
import sys
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / ".github" / "skills" / "create-skill" / "scripts" / "validate_skill.py"
LINTER_PATH = REPO_ROOT / "scripts" / "customization_lint.py"


def test_validator_warns_on_front_loaded_support_reads(tmp_path: Path) -> None:
    skill_dir = tmp_path / "front-load-skill"
    _write_skill(skill_dir, front_loaded=True)

    result = _run_validator(skill_dir)

    assert result.returncode == 0, (result.stdout + result.stderr).strip()
    assert "Potential front-loading" in result.stdout


def test_validator_allows_point_of_need_links_without_front_loading_warning(tmp_path: Path) -> None:
    skill_dir = tmp_path / "point-of-need-skill"
    _write_skill(skill_dir, front_loaded=False)

    result = _run_validator(skill_dir)

    assert result.returncode == 0, (result.stdout + result.stderr).strip()
    assert "Potential front-loading" not in result.stdout


def test_validator_rejects_plain_text_workflow_steps(tmp_path: Path) -> None:
    skill_dir = tmp_path / "plain-text-steps"
    _write_skill(
        skill_dir,
        front_loaded=False,
        step_one_body_override=(
            "Inspect nearby skills before drafting.\n"
            "Use #tool:search under `.github/skills` to inspect nearby skills."
        ),
    )

    result = _run_validator(skill_dir)

    assert result.returncode == 3, (result.stdout + result.stderr).strip()
    assert "must start with an ordered `1.` action" in result.stdout


def test_validator_rejects_canonical_create_surface_without_scripts(tmp_path: Path) -> None:
    skill_dir = tmp_path / "create-mcp"
    _write_skill(skill_dir, front_loaded=False, include_scripts=False)

    result = _run_validator(skill_dir)

    assert result.returncode == 3, (result.stdout + result.stderr).strip()
    assert "must include a non-empty `scripts/` directory" in result.stdout


def test_validator_rejects_excessive_post_workflow_reference_sections(tmp_path: Path) -> None:
    skill_dir = tmp_path / "post-workflow-skill"
    _write_skill(
        skill_dir,
        front_loaded=False,
        post_workflow_text=_current_create_mcp_style_reference_appendix(),
    )

    result = _run_validator(skill_dir)

    assert result.returncode == 3, (result.stdout + result.stderr).strip()
    assert "lignes après </workflow>" in result.stdout


def test_validator_warns_on_duplicate_concepts_between_skill_and_support_files(tmp_path: Path) -> None:
    skill_dir = tmp_path / "duplicate-concepts"
    _write_skill(
        skill_dir,
        front_loaded=False,
        post_workflow_text=(
            "## Language Selection\n\n"
            "Review [language selection checklist](./assets/language-selection-checklist.md) before choosing the implementation language.\n"
        ),
        extra_files={
            "assets/language-selection-checklist.md": (
                "# MCP Language Selection Checklist\n\n"
                "Use this checklist before choosing the implementation language.\n"
            )
        },
    )

    result = _run_validator(skill_dir)

    assert result.returncode == 0, (result.stdout + result.stderr).strip()
    assert "Language Selection" in result.stdout
    assert "Gardez une seule source" in result.stdout


def test_validator_rejects_template_assets_without_split_yaml_and_markdown_fences(
    tmp_path: Path,
) -> None:
    skill_dir = tmp_path / "broken-template-skill"
    _write_skill(
        skill_dir,
        front_loaded=False,
        template_assets={"agent-template.md": _legacy_agent_template()},
    )

    result = _run_validator(skill_dir)

    assert result.returncode == 3, (result.stdout + result.stderr).strip()
    assert "./assets/agent-template.md" in result.stdout
    assert "consecutive ```yaml and ```markdown code fences" in result.stdout


def test_validator_rejects_template_assets_with_reordered_canonical_sections(
    tmp_path: Path,
) -> None:
    skill_dir = tmp_path / "reordered-template-skill"
    _write_skill(
        skill_dir,
        front_loaded=False,
        template_assets={"agent-template.md": _reordered_agent_template()},
    )

    result = _run_validator(skill_dir)

    assert result.returncode == 3, (result.stdout + result.stderr).strip()
    assert "./assets/agent-template.md" in result.stdout
    assert "in canonical order" in result.stdout


def test_validator_rejects_agent_template_with_reordered_post_sections(
    tmp_path: Path,
) -> None:
    skill_dir = tmp_path / "reordered-agent-post-template"
    _write_skill(
        skill_dir,
        front_loaded=False,
        template_assets={"agent-template.md": _agent_template_with_reordered_post_sections()},
    )

    result = _run_validator(skill_dir)

    assert result.returncode == 3, (result.stdout + result.stderr).strip()
    assert "./assets/agent-template.md" in result.stdout
    assert "post-template headings in this order" in result.stdout


def test_validator_rejects_skill_template_with_reordered_reference_sections(
    tmp_path: Path,
) -> None:
    skill_dir = tmp_path / "broken-skill-template"
    _write_skill(
        skill_dir,
        front_loaded=False,
        template_assets={"skill-template.md": _reordered_skill_template()},
    )

    result = _run_validator(skill_dir)

    assert result.returncode == 3, (result.stdout + result.stderr).strip()
    assert "./assets/skill-template.md" in result.stdout
    assert "post-template headings in this order" in result.stdout


def test_validator_resolves_parent_relative_file_references(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    skill_dir = workspace_root / ".github" / "skills" / "relative-parent-skill"
    (workspace_root / ".github" / "agents").mkdir(parents=True, exist_ok=True)
    _write_skill(
        skill_dir,
        front_loaded=False,
        step_one_body_override=(
            "1. Inspect existing agents before drafting.\n"
            "   - Use #tool:search under #file:../../agents/ to inspect existing agents before drafting."
        ),
    )

    result = _run_validator(skill_dir)

    assert result.returncode == 0, (result.stdout + result.stderr).strip()
    assert "#file reference not found (best-effort): ../../agents/" not in result.stdout
    assert "#file reference appears deep: ../../agents/" not in result.stdout


def test_live_create_agent_skill_directory_validates() -> None:
    result = _run_validator(REPO_ROOT / ".github" / "skills" / "create-agent")

    assert result.returncode == 0, (result.stdout + result.stderr).strip()


def test_live_create_skill_directory_validates() -> None:
    result = _run_validator(REPO_ROOT / ".github" / "skills" / "create-skill")

    assert result.returncode == 0, (result.stdout + result.stderr).strip()


def test_live_create_prompt_skill_directory_validates() -> None:
    result = _run_validator(REPO_ROOT / ".github" / "skills" / "create-prompt")

    assert result.returncode == 0, (result.stdout + result.stderr).strip()


def test_live_create_mcp_skill_directory_validates() -> None:
    result = _run_validator(REPO_ROOT / ".github" / "skills" / "create-mcp")

    assert result.returncode == 0, (result.stdout + result.stderr).strip()


def test_current_create_mcp_style_reference_appendix_fails_validation(tmp_path: Path) -> None:
    skill_dir = tmp_path / "create-mcp"
    _write_skill(
        skill_dir,
        front_loaded=False,
        post_workflow_text=_current_create_mcp_style_reference_appendix(),
    )

    result = _run_validator(skill_dir)

    assert result.returncode == 3, (result.stdout + result.stderr).strip()
    assert "lignes après </workflow>" in result.stdout


def test_live_create_surface_linter_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(LINTER_PATH), "create-surfaces", "--root", str(REPO_ROOT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (result.stdout + result.stderr).strip()


def _run_validator(skill_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), "--skill-dir", str(skill_dir)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _write_skill(
    skill_dir: Path,
    *,
    front_loaded: bool,
    template_assets: dict[str, str] | None = None,
    step_one_body_override: str | None = None,
    include_scripts: bool = True,
    post_workflow_text: str = "",
    extra_files: dict[str, str] | None = None,
) -> None:
    (skill_dir / "assets").mkdir(parents=True, exist_ok=True)
    (skill_dir / "references").mkdir(parents=True, exist_ok=True)
    if include_scripts:
        (skill_dir / "scripts").mkdir(parents=True, exist_ok=True)

    files = {
        skill_dir / "references" / "USEFOR.md": "# WHEN TO USE\n\n- Test fixture.\n",
        skill_dir / "references" / "DONOTUSEFOR.md": "# WHEN NOT TO USE\n\n- Test fixture.\n",
        skill_dir / "references" / "guide.md": "# Guide\n\nPoint-of-need guidance.\n",
        skill_dir / "references" / "validation.md": "# Validation\n\nFix warnings here.\n",
        skill_dir / "assets" / "ask_questions.json": "[]\n",
    }
    if include_scripts:
        files[skill_dir / "scripts" / "noop.py"] = "print('ok')\n"
    for asset_name, content in (template_assets or {}).items():
        files[skill_dir / "assets" / asset_name] = content
    for relative_path, content in (extra_files or {}).items():
        files[skill_dir / Path(relative_path)] = content

    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    template_links = ""
    if template_assets:
        references = ", ".join(
            f"[{asset_name}](./assets/{asset_name})" for asset_name in sorted(template_assets)
        )
        template_links = (
            "\n3. Review the available templates when they matter for this draft.\n"
            f"   - Available templates: {references}."
        )

    if step_one_body_override is not None:
        step_one_body = step_one_body_override.strip()
    elif front_loaded:
        step_one_body = textwrap.dedent(
            """
            1. Inspect nearby skills before planning.
               - Use #tool:search under `.github/skills` to inspect nearby skills.
            2. Load the candidate support files that this fixture intentionally front-loads.
               - Use #tool:read on #file:./references/guide.md before planning.
               - Use #tool:read on #file:./references/validation.md before planning.
               - Use #tool:read on #file:./assets/ask_questions.json before planning.
            """
        ).strip()
    else:
        step_one_body = textwrap.dedent(
            """
            1. Inspect nearby skills before drafting.
               - Use #tool:search under `.github/skills` to inspect nearby skills.
            2. Review candidate references without front-loading them.
               - Review [guide](./references/guide.md), [validation notes](./references/validation.md), and [question payload](./assets/ask_questions.json) to decide what might be needed later.
            """
        ).strip()

    normalized_post_workflow_text = textwrap.dedent(post_workflow_text).strip()
    post_workflow_block = f"\n\n{normalized_post_workflow_text}" if normalized_post_workflow_text else ""

    skill_text = textwrap.dedent(
        f"""
        ---
        name: {skill_dir.name}
        description: "WHAT: Fixture skill for validator tests. USE FOR: validating front-loading detection. DO NOT USE FOR: production workflows."
        user-invocable: false
        ---

        <workflow>

        ## Step 0 - **CONFIRMATION**

        1. USE #tool:read **IMMEDIATELY** on #file:./references/USEFOR.md and **IMMEDIATELY** on #file:./references/DONOTUSEFOR.md to confirm with certainty if this skill should be used.
        2. Read the workflow and continue.

        <rules>

        - Reference support files only at point of need.

        </rules>

        ## Step 1 - Inspect current state

        {step_one_body}
        {template_links}

        ## Step 2 - Validate

          1. Load the guide only if this validation step still needs it.
              - Use #tool:read on #file:./references/guide.md only if the guide is still needed.
          2. Run the narrow validation command.
              - Use #tool:execute on #file:./scripts/noop.py when validating the draft.

        </workflow>
                {post_workflow_block}
        """
    ).strip() + "\n"

    (skill_dir / "SKILL.md").write_text(skill_text, encoding="utf-8")


def _current_create_mcp_style_reference_appendix() -> str:
    return textwrap.dedent(
        """
        ## Language Selection

        | Primary goal | Recommended language | Why |
        |--------------|----------------------|-----|
        | Reliable default for production | Go | Strong performance, simple deployment, single binary, low operational friction |
        | Maximum performance and safety | Rust | Best control over latency, memory use, and safety-sensitive behavior |
        | Fastest prototype | Python | Smallest time-to-first-server, minimal ceremony, easy experimentation |
        | Existing Node-only stack | Node.js | Use only when the user explicitly requires it |

        ## Transport Selection

        | Client Type | Transport |
        |-------------|-----------|
        | Local (Claude Desktop, VS Code) | `stdio` |
        | Remote (Cursor, cloud) | Streamable HTTP |
        | Backward compatibility | Legacy HTTP/SSE |

        Keep server logic independent of transport.

        ## Core Concepts

        - Tools are model-invokable actions.
        - Resources are read-only context.
        - Prompts are reusable prompt templates.

        ## Server Setup

        Prefer official SDKs and validate the installed version before coding.

        ## Official Resources

        - [Official MCP SDK references](./references/URIs.md)
        - [Language selection checklist](./assets/language-selection-checklist.md)
        """
    ).strip()


def _legacy_agent_template() -> str:
    return textwrap.dedent(
        """
        ```markdown
        ---
        name: legacy-agent
        description: "WHAT: Legacy single-fence example. USE FOR: tests need a broken template. DO NOT USE FOR: production routing."
        target: vscode
        tools: [read]
        ---

        # Role

        You are the Legacy agent.

        ## Responsibilities

        - Keep everything in one fence.

        ## Workflow

        1. Read the task.
        2. Return the result.

        ## Constraints

        - This shape is intentionally wrong.

        ## Output Contract

        - Return a draft.
        ```
        """
    ).strip() + "\n"


def _reordered_agent_template() -> str:
    return textwrap.dedent(
        """
        ```yaml
        ---
        name: reordered-agent
        description: "WHAT: Reordered sections example. USE FOR: tests need a structurally broken template. DO NOT USE FOR: production routing."
        target: vscode
        tools: [read]
        ---
        ```

        ```markdown
        <definitions>

        - **focused role** : A single job owned by one agent.

        </definitions>

        <workflow>

        ## Step 0 - **CONFIRMATION**

        1. Check the routing surface to confirm this agent is the right fit for the task.

        ### USE FOR

        - Requests that match the reordered-agent role.

        ### DO **NOT** USE FOR

        - Implementation work, refactors, or unrelated requests.

        2. If the task does not match, return: `{"status": "refused", "agent": "reordered-agent", "reason": "test fixture", "suggested_alternative": "planner"}`.
        3. If the task matches, continue to Step 1.

        ## Step 1 - Gather only the context needed for the task.

        1. Read the validated inputs named in the task.

        ## Role

        You are the Reordered agent.

        <rules>

        ## Responsibilities

        - This section moved to the wrong place.

        ## Constraints

        - Keep this invalid for the test.

        ## Output Contract

        - If Step 0 rejects the task, return the refusal JSON payload.
        - If Step 0 accepts the task, return the promised artifact.

        </rules>

        ## Step 2 - Apply the role-specific method using the declared tools.

        1. Continue with the role-specific method.

        ## Step 3 - Return the promised result without drifting into adjacent work.

        1. Return the promised artifact.

        </workflow>
        ```

        ## Authoring Notes

        - Preserve the outer wrapper, but not the section order.

        ## Discovery and routing example

        Bad:

        ```yaml
        ---
        name: vague-agent
        description: Helpful agent.
        ---
        ```

        Good:

        ```yaml
        ---
        name: precise-agent
        description: "WHAT: Do one thing. USE FOR: that one thing is needed. DO NOT USE FOR: unrelated work."
        ---
        ```

        ## Step 0 refusal example

        Bad:

        ```markdown
        ## Step 0 - **CONFIRMATION**
        1. Continue if unsure.
        ```

        Good:

        ```markdown
        ## Step 0 - **CONFIRMATION**
        1. Check the routing surface to confirm this agent is the right fit for the task.

        ### USE FOR

        - Summarizing validated release changes for the caller.

        ### DO **NOT** USE FOR

        - Implementation work, code edits, or speculative roadmap design.

        2. If the task does not match, return: `{"status": "refused", "agent": "release-summarizer", "reason": "this request is asking for implementation details, not a release summary", "suggested_alternative": "dev"}`.
        3. If the task matches, continue to Step 1.
        ```

        ## Workflow specificity example

        Bad:

        ```markdown
        ## Step 1 - Gather context
        1. Read things.
        ```

        Good:

        ```markdown
        ## Step 1 - Gather only the context needed for the task.
        1. Read the validated inputs named in the task.
        ```

        ## Delegation boundary example

        Bad:

        ```yaml
        ---
        tools: [read, agent]
        agents: [*]
        ---
        ```

        Good:

        ```yaml
        ---
        tools: [read]
        ---
        ```

        ## Output contract example

        Bad:

        ```markdown
        ## Output Contract
        - Be helpful.
        ```

        Good:

        ```markdown
        ## Output Contract
        - If Step 0 rejects the task, return the refusal JSON payload.
        - If Step 0 accepts the task, return the promised artifact.
        ```
        """
    ).strip() + "\n"


def _reordered_skill_template() -> str:
    return textwrap.dedent(
        """
        ```yaml
        ---
        name: fixture-skill
        description: "WHAT: Exercise validator template checks. USE FOR: testing exact template structure. DO NOT USE FOR: production workflows."
        user-invocable: false
        ---
        ```

        ```markdown
        <definitions>

        - **fixture definition** : Keeps the template shape deterministic.

        </definitions>

        <workflow>

        ## Step 0 - **CONFIRMATION**

        1. Confirm the template still applies.
        2. Continue with the fixed skeleton.

        <rules>

        - Keep the wrapper structure stable.

        </rules>

        ## Step 1 - Inspect
        Use #tool:read on #file:./references/guide.md only if needed.

        ## Step 2 - Ask
        Use #tool:vscode/askQuestions on #file:./assets/questions.json only if needed.

        ## Step 3 - Validate
        Use #tool:execute on #file:./scripts/validate.py only if needed.

        </workflow>
        ```

        ## Discovery and routing example

        Bad:

        ```yaml
        ---
        name: vague-skill
        description: Helpful skill
        user-invocable: false
        ---
        ```

        Good:

        ```yaml
        ---
        name: precise-skill
        description: "WHAT: Provide precise routing. USE FOR: validator tests. DO NOT USE FOR: unrelated work."
        user-invocable: false
        ---
        ```

        ## Authoring Notes

        - The sections above are intentionally reordered.

        ## Duplicate logic example

        Bad:

        ```markdown
        ## Step 4 - Validate
        - Repeat the validator instruction.
        ```

        Good:

        ```markdown
        ## Step 4 - Validate
        Apply the shared validation rules instead.
        ```

        ## Point-of-need reference example

        Bad:

        ```markdown
        ## Runtime Inputs
        - #file:./assets/questions.json
        ```

        Good:

        ```markdown
        ## Step 2 - Ask
        Use #tool:vscode/askQuestions with #file:./assets/questions.json.
        ```

        ## Choosing `#file:` versus markdown links

        Bad:

        ```markdown
        ## Step 1 - Inspect options
        Use #file:./references/guide-a.md to note the canonical guidance.
        ```

        Good:

        ```markdown
        ## Step 1 - Inspect options
        Review [guide A](./references/guide-a.md) before deciding whether it is needed now.
        ```

        ## Early-context front-loading example

        Bad:

        ```markdown
        ## Step 1 - Gather references
        Use #tool:read on #file:./references/guide-a.md before planning.
        Use #tool:read on #file:./references/guide-b.md before planning.
        Use #tool:read on #file:./assets/checklist.md before planning.
        ```

        Good:

        ```markdown
        ## Step 1 - Gather context
        Review [guide A](./references/guide-a.md), [guide B](./references/guide-b.md), and [checklist](./assets/checklist.md) before deciding what matters.
        ```

        ## Support-doc marker example

        Bad:

        ```markdown
        # Validation notes
        Use #tool:read on #file:./references/validation.md.
        ```

        Good:

        ```markdown
        # Validation notes
        See [validation guide](../references/validation.md).
        ```
        """
    ).strip() + "\n"


def _agent_template_with_reordered_post_sections() -> str:
    return textwrap.dedent(
        """
        ```yaml
        ---
        name: precise-agent
        description: "WHAT: Exercise post-template validation. USE FOR: tests need a canonical agent template with bad trailing docs order. DO NOT USE FOR: production routing."
        target: vscode
        tools: [read]
        ---
        ```

        ```markdown
        <definitions>

        - **focused role** : A test role.

        </definitions>

        <workflow>

        ## Step 0 - **CONFIRMATION**

        1. Check the routing surface to confirm this agent is the right fit for the task.

        ### USE FOR

        - Requests that match the precise-agent role.

        ### DO **NOT** USE FOR

        - Implementation work, refactors, or unrelated requests.

        2. If the task does not match, return: `{"status": "refused", "agent": "precise-agent", "reason": "test fixture", "suggested_alternative": "planner"}`.
        3. If the task matches, continue to Step 1.

        ## Role

        You are the Precise agent.

        <rules>

        ## Responsibilities

        - Keep the primary role explicit.

        ## Constraints

        - Stay inside the role.

        ## Output Contract

        - If Step 0 rejects the task, return the refusal JSON payload.
        - If Step 0 accepts the task, return the promised artifact.

        </rules>

        ## Step 1 - Gather only the context needed for the task.

        1. Read the validated inputs named in the task.

        ## Step 2 - Apply the role-specific method using the declared tools.

        1. Return the role-specific result.

        ## Step 3 - Return the promised result without drifting into adjacent work.

        1. Stop at the declared boundary.

        </workflow>
        ```

        ## Step 0 refusal example

        Bad:

        ```markdown
        ## Step 0 - **CONFIRMATION**
        1. Continue if unsure.
        ```

        Good:

        ```markdown
        ## Step 0 - **CONFIRMATION**
        1. Check the routing surface to confirm this agent is the right fit for the task.

        ### USE FOR

        - Summarizing validated release changes for the caller.

        ### DO **NOT** USE FOR

        - Implementation work, code edits, or speculative roadmap design.

        2. If the task does not match, return: `{"status": "refused", "agent": "release-summarizer", "reason": "this request is asking for implementation details, not a release summary", "suggested_alternative": "dev"}`.
        3. If the task matches, continue to Step 1.
        ```

        ## Authoring Notes

        - These headings are intentionally out of order.

        ## Discovery and routing example

        Bad:

        ```yaml
        ---
        name: vague-agent
        description: Helpful agent.
        ---
        ```

        Good:

        ```yaml
        ---
        name: precise-agent
        description: "WHAT: Do one thing. USE FOR: that one thing is needed. DO NOT USE FOR: unrelated work."
        ---
        ```

        ## Workflow specificity example

        Bad:

        ```markdown
        ## Step 1 - Gather context
        1. Do the work.
        ```

        Good:

        ```markdown
        ## Step 1 - Gather only the context needed for the task.
        1. Read the validated inputs named in the task.
        ```

        ## Delegation boundary example

        Bad:

        ```yaml
        ---
        tools: [read, agent]
        agents: [*]
        ---
        ```

        Good:

        ```yaml
        ---
        tools: [read]
        ---
        ```

        ## Output contract example

        Bad:

        ```markdown
        ## Output Contract
        - Be helpful.
        ```

        Good:

        ```markdown
        ## Output Contract
        - If Step 0 rejects the task, return: `{"status": "refused", "agent": "release-summarizer", "reason": "<specific reason>", "suggested_alternative": "<agent or skill>"}`.
        - If Step 0 accepts the task, return a short release summary plus explicit risks and open questions.
        - Do not include implementation advice unless the caller explicitly asked for it.
        ```
        """
    ).strip() + "\n"