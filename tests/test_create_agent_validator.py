import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).parents[1]
VALIDATOR = ROOT / ".github/skills/create-agent/scripts/validate_agent.py"


class CreateAgentValidatorTests(unittest.TestCase):
    def run_validator(
        self,
        filename: str,
        frontmatter: str,
        body: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        body = body or """
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

    def test_accepts_description_first_agent_without_confirmation_step(self):
        body = """
<definitions>
</definitions>
<workflow>
## Role

<rules>
## Responsibilities
- Keep the role focused.
## Constraints
- Do not exceed the role.
## Output Contract
- Return the scoped result.
</rules>

## Step 1 - Gather context.
## Step 2 - Perform the role.
## Step 3 - Return the result.
</workflow>
"""
        result = self.run_validator(
            "minimal.agent.md",
            "name: minimal\ntarget: vscode\ndescription: 'WHAT: focused work INVOKE FOR: focused requests DO NOT INVOKE FOR: unrelated work'\n",
            body,
        )

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("Step 0", result.stdout)
        self.assertNotIn("refusal", result.stdout.lower())

    def test_rejects_step_one_before_wrapped_role_and_rules(self):
        body = """
<definitions>
</definitions>
<workflow>
## Step 1 - Gather context.

## Role

<rules>
## Responsibilities
- Keep the role focused.
## Constraints
- Do not exceed the role.
## Output Contract
- Return the scoped result.
</rules>

## Step 2 - Perform the role.
## Step 3 - Return the result.
</workflow>
"""
        result = self.run_validator(
            "misplaced.agent.md",
            "name: misplaced\ntarget: vscode\ndescription: 'WHAT: focused work INVOKE FOR: focused requests DO NOT INVOKE FOR: unrelated work'\n",
            body,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Wrapped agents must keep this order", result.stdout)

    def test_rejects_invalid_delegation_contract(self):
        result = self.run_validator(
            "sample.agent.md",
            "name: sample\ntarget: vscode\ndescription: 'WHAT: x INVOKE FOR: x DO NOT INVOKE FOR: y'\nagents: [missing]\n",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("omits the `agent` tool", result.stdout)
        self.assertIn("unknown agent `missing`", result.stdout)

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