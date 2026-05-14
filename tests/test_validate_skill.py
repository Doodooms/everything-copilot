import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / ".github" / "skills" / "create-skill" / "scripts" / "validate_skill.py"


class ValidateSkillTest(unittest.TestCase):
    def test_validator_warns_on_front_loaded_support_reads(self) -> None:
        with tempfile.TemporaryDirectory(prefix=".tmp-skill-validator-") as temp_dir:
            skill_dir = Path(temp_dir) / "front-load-skill"
            self._write_skill(skill_dir, front_loaded=True)

            result = self._run_validator(skill_dir)

        self.assertEqual(result.returncode, 0, msg=(result.stdout + result.stderr).strip())
        self.assertIn("Potential front-loading", result.stdout)

    def test_validator_allows_point_of_need_links_without_front_loading_warning(self) -> None:
        with tempfile.TemporaryDirectory(prefix=".tmp-skill-validator-") as temp_dir:
            skill_dir = Path(temp_dir) / "point-of-need-skill"
            self._write_skill(skill_dir, front_loaded=False)

            result = self._run_validator(skill_dir)

        self.assertEqual(result.returncode, 0, msg=(result.stdout + result.stderr).strip())
        self.assertNotIn("Potential front-loading", result.stdout)

    def test_validator_rejects_template_assets_without_split_yaml_and_markdown_fences(self) -> None:
        with tempfile.TemporaryDirectory(prefix=".tmp-skill-validator-") as temp_dir:
            skill_dir = Path(temp_dir) / "broken-template-skill"
            self._write_skill(
                skill_dir,
                front_loaded=False,
                template_assets={"agent-template.md": self._legacy_agent_template()},
            )

            result = self._run_validator(skill_dir)

        self.assertEqual(result.returncode, 3, msg=(result.stdout + result.stderr).strip())
        self.assertIn("./assets/agent-template.md", result.stdout)
        self.assertIn("consecutive ```yaml and ```markdown code fences", result.stdout)

    def test_validator_rejects_template_assets_with_reordered_canonical_sections(self) -> None:
        with tempfile.TemporaryDirectory(prefix=".tmp-skill-validator-") as temp_dir:
            skill_dir = Path(temp_dir) / "reordered-template-skill"
            self._write_skill(
                skill_dir,
                front_loaded=False,
                template_assets={"agent-template.md": self._reordered_agent_template()},
            )

            result = self._run_validator(skill_dir)

        self.assertEqual(result.returncode, 3, msg=(result.stdout + result.stderr).strip())
        self.assertIn("./assets/agent-template.md", result.stdout)
        self.assertIn("markdown headings in this order", result.stdout)

    def test_validator_rejects_skill_template_with_reordered_reference_sections(self) -> None:
        with tempfile.TemporaryDirectory(prefix=".tmp-skill-validator-") as temp_dir:
            skill_dir = Path(temp_dir) / "broken-skill-template"
            self._write_skill(
                skill_dir,
                front_loaded=False,
                template_assets={"skill-template.md": self._reordered_skill_template()},
            )

            result = self._run_validator(skill_dir)

        self.assertEqual(result.returncode, 3, msg=(result.stdout + result.stderr).strip())
        self.assertIn("./assets/skill-template.md", result.stdout)
        self.assertIn("post-template headings in this order", result.stdout)

    def test_validator_resolves_parent_relative_file_references(self) -> None:
        with tempfile.TemporaryDirectory(prefix=".tmp-skill-validator-") as temp_dir:
            workspace_root = Path(temp_dir) / "workspace"
            skill_dir = workspace_root / ".github" / "skills" / "relative-parent-skill"
            (workspace_root / ".github" / "agents").mkdir(parents=True, exist_ok=True)
            self._write_skill(
                skill_dir,
                front_loaded=False,
                step_one_body_override=(
                    "Use #tool:search under #file:../../agents/ to inspect existing agents before drafting."
                ),
            )

            result = self._run_validator(skill_dir)

        self.assertEqual(result.returncode, 0, msg=(result.stdout + result.stderr).strip())
        self.assertNotIn("#file reference not found (best-effort): ../../agents/", result.stdout)
        self.assertNotIn("#file reference appears deep: ../../agents/", result.stdout)

    def test_live_create_agent_skill_directory_validates(self) -> None:
        result = self._run_validator(REPO_ROOT / ".github" / "skills" / "create-agent")

        self.assertEqual(result.returncode, 0, msg=(result.stdout + result.stderr).strip())

    def test_live_create_prompt_skill_directory_validates(self) -> None:
        result = self._run_validator(REPO_ROOT / ".github" / "skills" / "create-prompt")

        self.assertEqual(result.returncode, 0, msg=(result.stdout + result.stderr).strip())

    def _run_validator(self, skill_dir: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), "--skill-dir", str(skill_dir)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def _write_skill(
        self,
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

    def _legacy_agent_template(self) -> str:
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

    def _reordered_agent_template(self) -> str:
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

    def _reordered_skill_template(self) -> str:
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