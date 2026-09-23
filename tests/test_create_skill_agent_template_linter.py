import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
LINTER_PATH = ROOT / ".github/skills/create-skill/scripts/skill_lint_core.py"
SPEC = importlib.util.spec_from_file_location("create_skill_lint_core_test", LINTER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load create-skill linter at {LINTER_PATH}")
LINTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = LINTER
SPEC.loader.exec_module(LINTER)


class EmbeddedAgentTemplateLinterTests(unittest.TestCase):
    def test_accepts_canonical_agent_without_definitions_or_step_zero(self):
        body = """
<rules>
## Role
The agent owns one focused role.
## Responsibilities
- Perform that role.
## Constraints
- Stay within scope.
## Output Contract
- Return the defined handoff.
</rules>
<workflow>
## Step 1 - Gather context.
1. Inspect the assigned work.
## Step 2 - Perform the role.
1. Complete the scoped method.
## Step 3 - Return the result.
1. Provide the promised handoff.
</workflow>
"""

        self.assertEqual([], LINTER.validate_agent_template_markdown_block(body))

    def test_accepts_canonical_agent_with_nonempty_optional_definitions(self):
        body = """
<definitions>
- **defect packet** : a minimal reproduction and evidence for the repair owner
</definitions>
<rules>
## Role
The agent owns one focused role.
## Responsibilities
- Perform that role.
## Constraints
- Stay within scope.
## Output Contract
- Return the defined handoff.
</rules>
<workflow>
## Step 1 - Gather context.
1. Inspect the assigned work.
## Step 2 - Perform the role.
1. Complete the scoped method.
## Step 3 - Return the result.
1. Provide the promised handoff.
</workflow>
"""

        self.assertEqual([], LINTER.validate_agent_template_markdown_block(body))

    def test_rejects_empty_optional_definitions(self):
        body = """
<definitions>
</definitions>
<rules>
## Role
The agent owns one focused role.
## Responsibilities
- Perform that role.
## Constraints
- Stay within scope.
## Output Contract
- Return the defined handoff.
</rules>
<workflow>
## Step 1 - Gather context.
1. Inspect the assigned work.
## Step 2 - Perform the role.
1. Complete the scoped method.
## Step 3 - Return the result.
1. Provide the promised handoff.
</workflow>
"""

        errors = LINTER.validate_agent_template_markdown_block(body)
        self.assertTrue(any("non-empty" in error for error in errors), errors)

    def test_rejects_step_zero_outside_workflow(self):
        body = """
<rules>
## Role
The agent owns one focused role.
## Responsibilities
- Perform that role.
## Constraints
- Stay within scope.
## Output Contract
- Return the defined handoff.
</rules>
## Step 0 - Confirmation.
1. Ask a question.
<workflow>
## Step 1 - Gather context.
1. Inspect the assigned work.
## Step 2 - Perform the role.
1. Complete the scoped method.
## Step 3 - Return the result.
1. Provide the promised handoff.
</workflow>
"""

        errors = LINTER.validate_agent_template_markdown_block(body)
        self.assertTrue(any("exactly ## Step 1" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
