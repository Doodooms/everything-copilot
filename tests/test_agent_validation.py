import unittest
from pathlib import Path

from expertise.agent_validation import validate_agent_semantics
from expertise.errors import TargetError

ROOT = Path(__file__).resolve().parents[1]


class AgentValidationTests(unittest.TestCase):
    def test_canonical_sections_are_accepted_and_crossed_sections_are_rejected(self):
        canonical = (ROOT / "agentic-core/agents/architect.md").read_bytes()
        parsed = validate_agent_semantics(canonical, "architect", "architect.md")
        self.assertEqual(parsed.metadata["name"], "architect")
        self.assertIn("<routing>", parsed.body)

        crossed = canonical.replace(
            b"</routing>\n\n<critical_rules>", b"<critical_rules>", 1
        ).replace(b"</critical_rules>", b"</routing>\n\n</critical_rules>", 1)
        with self.assertRaisesRegex(TargetError, "sections are not in canonical order"):
            validate_agent_semantics(crossed, "architect", "architect.md")


if __name__ == "__main__":
    unittest.main()
