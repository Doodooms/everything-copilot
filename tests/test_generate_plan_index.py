import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).parents[1]
        / "agentic-core"
        / "skills"
        / "orchestration"
        / "references"
        / "orchestrate"
        / "scripts"
    ),
)

import generate_plan_index


class PlanIndexTests(unittest.TestCase):
    def test_header_extraction_returns_block_content_not_heading_label(self):
        plan = """## Repository structure

- src/api/ # request handlers
- tests/api/ # focused tests

## Delivery phases
"""

        self.assertEqual(
            generate_plan_index.extract_header_block(plan),
            "- src/api/ # request handlers\n- tests/api/ # focused tests",
        )

    def test_optional_index_contains_only_path_entries(self):
        index = generate_plan_index.build_plan_index(["src/api/", "tests/api/"])

        self.assertEqual(
            index,
            {"repo_structure": [{"path": "src/api/"}, {"path": "tests/api/"}]},
        )


if __name__ == "__main__":
    unittest.main()
