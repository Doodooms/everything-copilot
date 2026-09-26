import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD_PATH = (
    ROOT
    / "agentic-core/skills/plugin-engineering/references/create-skill/scripts/scaffold.py"
)
SPEC = importlib.util.spec_from_file_location("create_skill_scaffold_test", SCAFFOLD_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load create-skill scaffolder at {SCAFFOLD_PATH}")
SCAFFOLD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SCAFFOLD
SPEC.loader.exec_module(SCAFFOLD)


class CreateSkillScaffoldTests(unittest.TestCase):
    def test_canonical_configuration_creates_the_declared_provenance_and_definition(self):
        package = ROOT / "agentic-core/skills/plugin-engineering/references/create-skill"
        config = SCAFFOLD.ScaffoldConfig.from_file(
            package / "assets/skill-scaffold.json"
        )

        self.assertEqual(config.architecture_id, "skill-package-v2")
        self.assertEqual(
            config.required_files,
            ("SKILL.md", "references/original-spec.md"),
        )

        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "sample-skill"
            provenance = destination / "references/original-spec.md"
            provenance.parent.mkdir(parents=True)
            provenance.write_text("Approved source intent.\n", encoding="utf-8")

            summary = SCAFFOLD.scaffold_skill(
                destination, config, provenance.read_text(encoding="utf-8")
            )
            SCAFFOLD.validate_scaffold(destination, config)

        self.assertEqual(summary["architecture_id"], "skill-package-v2")
        self.assertEqual(
            summary["created_files"],
            ["SKILL.md", "references/original-spec.md"],
        )
