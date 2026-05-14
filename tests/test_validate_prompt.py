import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / ".github" / "skills" / "create-prompt" / "scripts" / "validate_prompt.py"


class ValidatePromptTest(unittest.TestCase):
    def test_validator_accepts_structured_prompt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="prompt-validator-") as temp_dir:
            temp_root = Path(temp_dir)
            prompt_file = self._write_prompt(temp_root, self._structured_prompt_body())

            result = self._run_validator(temp_root, prompt_file)

        self.assertEqual(result.returncode, 0, msg=(result.stdout + result.stderr).strip())

    def test_validator_rejects_prompt_missing_top_level_heading(self) -> None:
        with tempfile.TemporaryDirectory(prefix="prompt-validator-") as temp_dir:
            temp_root = Path(temp_dir)
            prompt_file = self._write_prompt(temp_root, self._prompt_body_missing_h1())

            result = self._run_validator(temp_root, prompt_file)

        self.assertEqual(result.returncode, 1, msg=(result.stdout + result.stderr).strip())
        self.assertIn("top-level `#` heading", result.stdout)

    def test_validator_warns_on_flat_long_prompt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="prompt-validator-") as temp_dir:
            temp_root = Path(temp_dir)
            prompt_file = self._write_prompt(temp_root, self._flat_prompt_body())

            result = self._run_validator(temp_root, prompt_file)

        self.assertEqual(result.returncode, 0, msg=(result.stdout + result.stderr).strip())
        self.assertIn("Longer prompt bodies should use short `##` sections", result.stdout)

    def test_live_init_prompt_validates(self) -> None:
        prompt_file = REPO_ROOT / ".github" / "prompts" / "init.prompt.md"

        result = self._run_validator(REPO_ROOT, prompt_file)

        self.assertEqual(result.returncode, 0, msg=(result.stdout + result.stderr).strip())

    def _run_validator(self, cwd: Path, prompt_file: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), "--prompt-file", str(prompt_file)],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )

    def _write_prompt(self, root: Path, body: str) -> Path:
        prompt_dir = root / ".github" / "prompts"
        prompt_dir.mkdir(parents=True, exist_ok=True)
        prompt_file = prompt_dir / "structured.prompt.md"
        prompt_file.write_text(body, encoding="utf-8")
        return prompt_file

    def _structured_prompt_body(self) -> str:
        return textwrap.dedent(
            """
            ---
            description: "What: Generate a deterministic summary. Use when: the user wants a concise synthesis from selected inputs."
            agent: agent
            tools: [read, search]
            ---

            # Task

            Produce a concise summary from the provided materials.

            ## Inputs

            - Use the selected files or pasted text.

            ## Constraints

            - Keep the summary factual and scoped to the provided material.

            ## Output Contract

            - Return a short summary followed by explicit open questions if anything is missing.
            """
        ).strip() + "\n"

    def _prompt_body_missing_h1(self) -> str:
        return textwrap.dedent(
            """
            ---
            description: "What: Exercise prompt validation. Use when: tests need a structurally broken prompt."
            ---

            Produce a concise summary.

            ## Output Contract

            - Return a short summary.
            """
        ).strip() + "\n"

    def _flat_prompt_body(self) -> str:
        return textwrap.dedent(
            """
            ---
            description: "What: Exercise flat prompt warnings. Use when: tests need a long body without section structure."
            ---

            # Task

            Produce a release note summary from the provided context.
            Use the user argument as the release scope.
            Keep the tone factual.
            Mention risks when they are explicit.
            Mention open questions if anything is ambiguous.
            Keep the output concise.
            Avoid inventing features.
            Prefer the repository's own terminology.
            Return the result in Markdown.
            """
        ).strip() + "\n"


if __name__ == "__main__":
    unittest.main()