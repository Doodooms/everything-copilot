import subprocess
import sys
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / ".github" / "skills" / "create-skill" / "scripts" / "validate_skill.py"


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
    assert "markdown headings in this order" in result.stdout


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
            "Use #tool:search under #file:../../agents/ to inspect existing agents before drafting."
        ),
    )

    result = _run_validator(skill_dir)

    assert result.returncode == 0, (result.stdout + result.stderr).strip()
    assert "#file reference not found (best-effort): ../../agents/" not in result.stdout
    assert "#file reference appears deep: ../../agents/" not in result.stdout


def test_live_create_agent_skill_directory_validates() -> None:
    result = _run_validator(REPO_ROOT / ".github" / "skills" / "create-agent")

    assert result.returncode == 0, (result.stdout + result.stderr).strip()


def test_live_create_prompt_skill_directory_validates() -> None:
    result = _run_validator(REPO_ROOT / ".github" / "skills" / "create-prompt")

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
) -> None:
    (skill_dir / "assets").mkdir(parents=True, exist_ok=True)
    (skill_dir / "references").mkdir(parents=True, exist_ok=True)
    (skill_dir / "scripts").mkdir(parents=True, exist_ok=True)

    files = {
        skill_dir / "references" / "USEFOR.md": "# WHEN TO USE\n\n- Test fixture.\n",
        skill_dir / "references" / "DONOTUSEFOR.md": "# WHEN NOT TO USE\n\n- Test fixture.\n",
        skill_dir / "references" / "guide.md": "# Guide\n\nPoint-of-need guidance.\n",
        skill_dir / "references" / "validation.md": "# Validation\n\nFix warnings here.\n",
        skill_dir / "assets" / "ask_questions.json": "[]\n",
        skill_dir / "scripts" / "noop.py": "print('ok')\n",
    }
    for asset_name, content in (template_assets or {}).items():
        files[skill_dir / "assets" / asset_name] = content

    for path, content in files.items():
        path.write_text(content, encoding="utf-8")

    template_links = ""
    if template_assets:
        references = ", ".join(
            f"[{asset_name}](./assets/{asset_name})" for asset_name in sorted(template_assets)
        )
        template_links = f"\nAvailable templates: {references}."

    if step_one_body_override is not None:
        step_one_body = step_one_body_override.strip()
    elif front_loaded:
        step_one_body = textwrap.dedent(
            """
            Use #tool:search under `.github/skills` to inspect nearby skills.
            Use #tool:read on #file:./references/guide.md before planning.
            Use #tool:read on #file:./references/validation.md before planning.
            Use #tool:read on #file:./assets/ask_questions.json before planning.
            """
        ).strip()
    else:
        step_one_body = textwrap.dedent(
            """
            Use #tool:search under `.github/skills` to inspect nearby skills.
            Review [guide](./references/guide.md), [validation notes](./references/validation.md), and [question payload](./assets/ask_questions.json) to decide what might be needed later.
            """
        ).strip()

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

        Use #tool:read on #file:./references/guide.md only if the guide is still needed.
        Use #tool:execute on #file:./scripts/noop.py when validating the draft.

        </workflow>
        """
    ).strip() + "\n"

    (skill_dir / "SKILL.md").write_text(skill_text, encoding="utf-8")


def _legacy_agent_template() -> str:
    return textwrap.dedent(
        """
        ```markdown
        ---
        name: legacy-agent
        description: "What: Legacy single-fence example. Use when: tests need a broken template."
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
        description: "What: Reordered sections example. Use when: tests need a structurally broken template."
        target: vscode
        tools: [read]
        ---
        ```

        ```markdown
        <definitions>

        - **focused role** : A single job owned by one agent.

        </definitions>

        # Role

        You are the Reordered agent.

        <workflow>

        ## Workflow

        1. Read the task.
        2. Return the result.

        </workflow>

        ## Responsibilities

        - This section moved to the wrong place.

        ## Constraints

        - Keep this invalid for the test.

        ## Output Contract

        - Return a draft.
        ```

        Notes

        - Preserve the outer wrapper, but not the section order.
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