import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).parents[1]
VALIDATOR = ROOT / ".github/skills/create-agent/scripts/validate_agent.py"


class CreateAgentValidatorTests(unittest.TestCase):
    def run_validator(self, filename: str, frontmatter: str) -> subprocess.CompletedProcess[str]:
        body = """
# Role

## Responsibilities

- Keep the role focused.

## Workflow

1. Inspect the assigned work.

## Constraints

- Do not exceed the role.

## Output Contract

- Return the scoped result.
"""
        with TemporaryDirectory() as directory:
            agent_file = Path(directory) / filename
            agent_file.write_text(f"---\n{frontmatter}---\n{body}", encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), "--agent-file", str(agent_file)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

    def test_rejects_filename_name_drift(self):
        result = self.run_validator(
            "sample.agent.md",
            "name: different\ntarget: vscode\ndescription: 'WHAT: x INVOKE FOR: x DO NOT INVOKE FOR: y'\n",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must match the `.agent.md` filename stem", result.stdout)

    def test_rejects_missing_vscode_target_and_deprecated_infer(self):
        result = self.run_validator(
            "sample.agent.md",
            "name: sample\ninfer: true\ndescription: 'WHAT: x INVOKE FOR: x DO NOT INVOKE FOR: y'\n",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("target: vscode", result.stdout)
        self.assertIn("`infer` is deprecated", result.stdout)


if __name__ == "__main__":
    unittest.main()