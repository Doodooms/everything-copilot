from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import yaml

from expertise.parser import parse_pack
from expertise.targets import compile_target
from scripts.generate_migration_readiness_waza import generate_waza

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PACK_ROOT = REPOSITORY_ROOT / "expertise/packs/migration-readiness"
SPEC_PATH = REPOSITORY_ROOT / "experiments/routing/specs/migration-readiness.json"
EXPECTED_ROLES = {
    "schema-expand-contract-compatibility": {
        "schema-compatibility-reviewer",
        "rollout-readiness-reviewer",
    },
    "rolling-client-column-removal": {
        "schema-compatibility-reviewer",
        "rollout-readiness-reviewer",
    },
    "backfill-invariant-readiness": {
        "data-integrity-reviewer",
        "rollout-readiness-reviewer",
    },
    "dual-write-cutover-plan": {
        "schema-compatibility-reviewer",
        "data-integrity-reviewer",
        "rollout-readiness-reviewer",
    },
    "foreign-key-rollout-readiness": {
        "schema-compatibility-reviewer",
        "data-integrity-reviewer",
        "rollout-readiness-reviewer",
    },
    "migration-recovery-evidence": {
        "data-integrity-reviewer",
        "rollout-readiness-reviewer",
    },
}


class MigrationReadinessPackTests(unittest.TestCase):
    def test_pack_validates_and_compiles_to_codex_without_external_capabilities(self):
        source = parse_pack(PACK_ROOT)

        self.assertEqual(source.ir.id, "migration-readiness")
        self.assertEqual(source.ir.compatibility.targets, ("codex", "portable"))
        self.assertEqual(
            {contribution.id for contribution in source.ir.agents.contributions},
            {
                "migration-readiness-coordinator",
                "schema-compatibility-reviewer",
                "data-integrity-reviewer",
                "rollout-readiness-reviewer",
            },
        )
        self.assertIsNone(source.ir.mcp_config)
        self.assertEqual(source.ir.mcp_servers, ())
        self.assertEqual(source.ir.dependencies, ())

        artifact = compile_target(source, "codex")
        files = artifact.file_map()
        self.assertEqual(
            {path for path in files if path.startswith("codex-agents/")},
            {
                "codex-agents/migration-readiness-coordinator.toml",
                "codex-agents/schema-compatibility-reviewer.toml",
                "codex-agents/data-integrity-reviewer.toml",
                "codex-agents/rollout-readiness-reviewer.toml",
            },
        )
        self.assertIn("skills/migration-readiness/SKILL.md", files)
        self.assertFalse(any("mcp" in path.casefold() for path in files))

    def test_canonical_corpus_has_exact_balanced_routes_and_digest(self):
        raw = SPEC_PATH.read_bytes()
        corpus = json.loads(raw.decode("utf-8"))
        cases = corpus["cases"]

        self.assertEqual(len(cases), 12)
        self.assertEqual(len({case["id"] for case in cases}), 12)
        positive = [case for case in cases if case["polarity"] == "positive"]
        negative = [case for case in cases if case["polarity"] == "negative"]
        self.assertEqual(len(positive), 6)
        self.assertEqual(len(negative), 6)
        self.assertTrue(
            all(case["expected_route"] == "migration-readiness" for case in positive)
        )
        self.assertTrue(all("expected_route" not in case for case in negative))
        self.assertEqual(
            {case["id"]: set(case["expected_specialist_roles"]) for case in positive},
            EXPECTED_ROLES,
        )
        self.assertTrue(
            all("expected_specialist_roles" not in case for case in negative)
        )
        canonical_cases = json.dumps(
            cases, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(
            hashlib.sha256(canonical_cases).hexdigest(),
            corpus["metadata"]["cases_sha256"],
        )

    def test_generated_waza_view_is_deterministic_and_derived_from_corpus(self):
        with (
            tempfile.TemporaryDirectory() as first_dir,
            tempfile.TemporaryDirectory() as second_dir,
        ):
            first = generate_waza(SPEC_PATH, Path(first_dir))
            second = generate_waza(SPEC_PATH, Path(second_dir))

            self.assertEqual(first, second)
            self.assertEqual(first["case_count"], 12)
            self.assertEqual(
                first["cases_sha256"],
                json.loads(SPEC_PATH.read_text(encoding="utf-8"))["metadata"][
                    "cases_sha256"
                ],
            )
            output = Path(first_dir)
            eval_text = (output / "eval.yaml").read_text(encoding="utf-8")
            self.assertIn(
                "GENERATED FROM experiments/routing/specs/migration-readiness.json",
                eval_text,
            )
            eval_data = yaml.safe_load(eval_text)
            self.assertEqual(eval_data["tasks"], ["tasks/*.yaml"])
            tasks = sorted((output / "tasks").glob("*.yaml"))
            self.assertEqual(len(tasks), 12)
            waza_cases = {
                yaml.safe_load(path.read_text(encoding="utf-8"))["id"]: yaml.safe_load(
                    path.read_text(encoding="utf-8")
                )
                for path in tasks
            }
            canonical = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
            for case in canonical["cases"]:
                task = waza_cases[case["id"]]
                self.assertEqual(task["inputs"]["prompt"], case["prompt"])
                self.assertEqual(
                    task["expected"]["should_trigger"], case["polarity"] == "positive"
                )
                self.assertIn(f"source-case:{case['id']}", task["tags"])
                self.assertEqual(
                    any(tag.startswith("expected-route:") for tag in task["tags"]),
                    "expected_route" in case,
                )
                self.assertEqual(
                    {
                        tag.removeprefix("expected-specialist-role:")
                        for tag in task["tags"]
                        if tag.startswith("expected-specialist-role:")
                    },
                    set(case.get("expected_specialist_roles", [])),
                )


if __name__ == "__main__":
    unittest.main()
