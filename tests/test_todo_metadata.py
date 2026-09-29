from __future__ import annotations

import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from validate_todo_metadata import parse_frontmatter, validate_metadata


class TodoMetadataTests(unittest.TestCase):
    def test_accepts_current_metadata_contract(self) -> None:
        metadata = parse_frontmatter(
            "---\n"
            "kind: design_input\n"
            "status: researched\n"
            "disposition: partially_adopted\n"
            "derived_work: []\n"
            "---\n"
            "# Source\n"
        )

        self.assertEqual(validate_metadata(metadata), [])

    def test_accepts_crlf_frontmatter(self) -> None:
        metadata = parse_frontmatter(
            "---\r\n"
            "kind: design_input\r\n"
            "status: researched\r\n"
            "disposition: partially_adopted\r\n"
            "derived_work: []\r\n"
            "---\r\n"
            "# Source\r\n"
        )

        self.assertEqual(validate_metadata(metadata), [])

    def test_rejects_duplicate_frontmatter_keys(self) -> None:
        with self.assertRaisesRegex(yaml.YAMLError, "duplicate key 'status'"):
            parse_frontmatter(
                "---\n"
                "kind: design_input\n"
                "status: invalid\n"
                "status: triaged\n"
                "disposition: research_required\n"
                "derived_work: []\n"
                "---\n"
            )

    def test_rejects_unknown_status_and_extra_authority_field(self) -> None:
        metadata = {
            "kind": "design_input",
            "status": "implemented",
            "disposition": "adopted",
            "derived_work": [],
            "implementation_authorized": True,
        }

        errors = validate_metadata(metadata)

        self.assertTrue(any("status must be one of" in error for error in errors))
        self.assertTrue(any("unexpected fields" in error for error in errors))

    def test_rejects_malformed_frontmatter(self) -> None:
        with self.assertRaisesRegex(ValueError, "closing YAML"):
            parse_frontmatter("---\nkind: design_input\n# no closing marker\n")

    def test_rejects_non_mapping_frontmatter(self) -> None:
        with self.assertRaisesRegex(TypeError, "must be a YAML mapping"):
            parse_frontmatter("---\n- design_input\n---\n")

    def test_reports_missing_required_fields(self) -> None:
        self.assertEqual(
            validate_metadata({"kind": "design_input"}),
            ["missing fields: derived_work, disposition, status"],
        )

    def test_rejects_non_string_enum_values(self) -> None:
        metadata = {
            "kind": ["design_input"],
            "status": 1,
            "disposition": None,
            "derived_work": [],
        }

        errors = validate_metadata(metadata)

        self.assertTrue(
            any(error.startswith("kind must be one of") for error in errors)
        )
        self.assertTrue(
            any(error.startswith("status must be one of") for error in errors)
        )
        self.assertTrue(
            any(error.startswith("disposition must be one of") for error in errors)
        )

    def test_rejects_non_string_derived_work(self) -> None:
        metadata = {
            "kind": "research_input",
            "status": "triaged",
            "disposition": "research_required",
            "derived_work": ["docs/task.md", 12],
        }

        self.assertIn(
            "derived_work must be a list of non-empty strings",
            validate_metadata(metadata),
        )


if __name__ == "__main__":
    unittest.main()
