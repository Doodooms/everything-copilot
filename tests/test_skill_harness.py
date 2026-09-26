import unittest
import json
import importlib
import shutil
import sys
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch

import yaml

from skill_harness.benchmark import BenchmarkMutationError, freeze_benchmark, verify_benchmark
from skill_harness.benchmark_oracle import apply_routing_gate, evaluate_task, load_oracle_manifest
from skill_harness.ablation import prepare_phase_0a
from skill_harness.manifest import ArchitectureVariant, ManifestError, SemanticManifest
from skill_harness.metrics import RoutingTrial, aggregate_trials
from skill_harness.render import RendererRegistry
from skill_harness.routing import (
    SENTINEL_NAME,
    RoutingArchitecture,
    RoutingCase,
    RoutingSpec,
    render_real_skill_variant,
    render_routing_variant,
)
from skill_harness.scaffold import ScaffoldConfig, scaffold_skill, validate_scaffold
from skill_harness.selection import (
    ArchitectureResult,
    SelectionConstraints,
    select_architecture,
)
from skill_harness.skillopt_adapter import WazaSkillOptAdapter, normalize_rollout_result
from skill_harness.optimize import clone_skill_workspace, validate_candidate_before_waza
from skill_harness.waza_adapter import WazaError, configure_summary_only_discovery, run_waza
from skill_harness.routing_observation import parse_routing_observation
from skill_harness.sentinel import count_sentinels, insert_sentinel, remove_sentinel
from scripts.build_create_skill_benchmark import FAMILIES, JUDGE_RUBRIC, WAZA_RUBRIC, main as build_benchmark, validate_manifest


class BenchmarkGenerationTests(unittest.TestCase):
    repository_root = Path(__file__).parents[1]
    manifest_path = repository_root / "experiments/optimization/create-skill/benchmark/benchmark_manifest.json"
    source_skill = (
        repository_root
        / "agentic-core/skills/plugin-engineering/references/create-skill"
    )

    def test_manifest_families_and_holdout_are_disjoint(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(set(manifest["families"]), set(FAMILIES))
        self.assertTrue(
            set(manifest["splits"]["train"]["applications"]).isdisjoint(
                manifest["splits"]["holdout"]["applications"]
            )
        )
        validate_manifest(manifest)

    def test_generated_tasks_cover_frozen_support_files_and_hard_gates(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        with TemporaryDirectory() as directory:
            output = Path(directory) / "benchmark"
            with patch.object(sys, "argv", [
                "build_create_skill_benchmark",
                "--manifest", str(self.manifest_path),
                "--source-skill", str(self.source_skill),
                "--output", str(output),
            ]):
                self.assertEqual(build_benchmark(), 0)

            source_support = {
                path.relative_to(self.source_skill).as_posix()
                for path in self.source_skill.rglob("*")
                if path.is_file()
                and path.relative_to(self.source_skill).as_posix() != "method-source.md"
                and path.name != "SKILL.md"
                and "__pycache__" not in path.parts
                and path.suffix != ".pyc"
            }
            for split in ("train", "selection", "holdout"):
                manifest = json.loads((output / split / "adapter_manifest.json").read_text(encoding="utf-8"))
                oracle = manifest["tasks"]["probe-support-file-discipline"]
                self.assertFalse(oracle["support_files_optimized"])
                self.assertEqual(set(oracle["required_support_files"]), source_support)
                self.assertIn("self_containment", oracle["hard_gates"])
                for path in oracle["required_support_files"]:
                    self.assertTrue((output / split / ".github/skills/create-skill" / path).is_file())
                projected_skill = output / split / ".github/skills/create-skill"
                self.assertEqual(
                    (projected_skill / "SKILL.md").read_text(encoding="utf-8"),
                    (self.source_skill / "method-source.md").read_text(encoding="utf-8"),
                )
                self.assertFalse((projected_skill / "method-source.md").exists())
                self.assertEqual(
                    {item["path"] for item in yaml.safe_load(
                        (output / split / "tasks" / "probe-support-file-discipline.yaml").read_text(encoding="utf-8")
                    )["inputs"]["files"]},
                    set(oracle["required_paths"]),
                )
                task = yaml.safe_load(
                    (output / split / "tasks" / "probe-support-file-discipline.yaml").read_text(encoding="utf-8")
                )
                self.assertNotIn("oracle", task)
                self.assertNotIn("family", task)
                self.assertNotIn("evaluates", task)

    def test_generated_eval_uses_supported_builtin_waza_rubric(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "benchmark"
            with patch.object(sys, "argv", [
                "build_create_skill_benchmark",
                "--manifest", str(self.manifest_path),
                "--source-skill", str(self.source_skill),
                "--output", str(output),
            ]):
                self.assertEqual(build_benchmark(), 0)

            for split in ("train", "selection", "holdout"):
                evaluation = yaml.safe_load((output / split / "eval.yaml").read_text(encoding="utf-8"))
                prompt_grader = next(grader for grader in evaluation["graders"] if grader["type"] == "prompt")
                self.assertEqual(prompt_grader["config"]["rubric"], WAZA_RUBRIC)
                self.assertNotIn(JUDGE_RUBRIC, prompt_grader["config"].values())
                metric = next(metric for metric in evaluation["metrics"] if metric["name"] == "llm_quality")
                self.assertIn(JUDGE_RUBRIC, metric["description"])
                self.assertIn("supported built-in helpfulness judge", metric["description"])


class ManifestTests(unittest.TestCase):
    def test_user_renderer_must_preserve_semantics(self):
        source = SemanticManifest("demo-skill", "A demo", ({"id": "f1"},), ({"step": 1},))
        registry = RendererRegistry()
        registry.register("identity", lambda manifest, config: manifest)
        result = registry.render(ArchitectureVariant("user-variant", "identity", {}), source)
        self.assertEqual(result.semantic_hash, source.semantic_hash)

        registry.register(
            "drifting", lambda manifest, config: SemanticManifest(
                manifest.name, "changed", manifest.fixtures, manifest.workflow
            )
        )
        with self.assertRaises(ManifestError):
            registry.render(ArchitectureVariant("bad", "drifting", {}), source)


class MetricsTests(unittest.TestCase):
    def test_aggregate_reports_routing_and_cost_metrics(self):
        report = aggregate_trials(
            [
                RoutingTrial("accept", "accept", True, True, True, True, 2, 10),
                RoutingTrial(None, "accept", False, True, False, True, 1, 20),
                RoutingTrial("reject", None, False, False, False, False, 0, 5),
            ]
        )
        self.assertEqual(report["trial_count"], 3)
        self.assertAlmostEqual(report["discovery"]["precision"], 0.5)
        self.assertEqual(report["workflow_entry_after_reject"], 1)
        self.assertEqual(report["tokens"]["median"], 10.0)


class ProtectionTests(unittest.TestCase):
    def test_benchmark_oracle_rejects_support_symlink_to_fixture(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / ".github/skills/create-skill"
            fixture = root / "fixtures/.github/skills/create-skill"
            package.mkdir(parents=True)
            fixture.mkdir(parents=True)
            skill = "See references/original-spec.md\n"
            (package / "SKILL.md").write_text(skill, encoding="utf-8")
            (fixture / "SKILL.md").write_text(skill, encoding="utf-8")
            (fixture / "references").mkdir()
            fixture_spec = fixture / "references/original-spec.md"
            fixture_spec.write_text("spec\n", encoding="utf-8")
            (package / "references").mkdir()
            (package / "references/original-spec.md").symlink_to(fixture_spec)

            result = evaluate_task(
                "probe",
                {
                    "family": "support-file-discipline",
                    "should_trigger": True,
                    "required_paths": [".github/skills/create-skill/references/original-spec.md"],
                    "required_support_files": ["references/original-spec.md"],
                    "provenance_path": ".github/skills/create-skill/references/original-spec.md",
                },
                root,
            )

            self.assertFalse(result.passed)
            self.assertFalse(result.checks["package_shape"])
            self.assertFalse(result.checks["support_files"])

    def test_benchmark_oracle_rejects_missing_and_mutated_frozen_support(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / ".github/skills/create-skill"
            fixture = root / "fixtures/.github/skills/create-skill"
            package.mkdir(parents=True)
            fixture.mkdir(parents=True)
            skill = "---\nname: create-skill\n---\nSee references/original-spec.md\n"
            (package / "SKILL.md").write_text(skill, encoding="utf-8")
            (fixture / "SKILL.md").write_text(skill, encoding="utf-8")
            (package / "references").mkdir()
            (fixture / "references").mkdir()
            (package / "references/original-spec.md").write_text("spec\n", encoding="utf-8")
            (fixture / "references/original-spec.md").write_text("spec\n", encoding="utf-8")
            (package / "references/final-checklist.md").write_text("changed\n", encoding="utf-8")
            (fixture / "references/final-checklist.md").write_text("frozen\n", encoding="utf-8")
            result = evaluate_task(
                "probe",
                {
                    "family": "support-file-discipline",
                    "should_trigger": True,
                    "required_paths": [".github/skills/create-skill/references/final-checklist.md"],
                    "required_support_files": ["references/final-checklist.md"],
                    "provenance_path": ".github/skills/create-skill/references/original-spec.md",
                },
                root,
            )
            self.assertFalse(result.passed)
            self.assertFalse(result.checks["support_files"])
            self.assertIn("support files were mutated", " ".join(result.failures))

    def test_benchmark_oracle_rejects_deleted_frozen_script_and_support_file(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / ".github/skills/create-skill"
            fixture = root / "fixtures/.github/skills/create-skill"
            package.mkdir(parents=True)
            fixture.mkdir(parents=True)
            skill = "See references/original-spec.md\n"
            (package / "SKILL.md").write_text(skill, encoding="utf-8")
            (fixture / "SKILL.md").write_text(skill, encoding="utf-8")
            for relative in ("references/original-spec.md", "references/final-checklist.md", "scripts/validate.py"):
                for base in (package, fixture):
                    target = base / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text("frozen\n", encoding="utf-8")
            (package / "scripts/validate.py").unlink()
            (fixture / "references/final-checklist.md").unlink()

            result = evaluate_task(
                "probe",
                {
                    "family": "scripts-validation",
                    "should_trigger": True,
                    "required_paths": [
                        ".github/skills/create-skill/scripts/validate.py",
                        ".github/skills/create-skill/references/final-checklist.md",
                    ],
                    "required_support_files": [
                        "scripts/validate.py",
                        "references/final-checklist.md",
                        "references/original-spec.md",
                    ],
                    "provenance_path": ".github/skills/create-skill/references/original-spec.md",
                },
                root,
            )

            self.assertFalse(result.passed)
            self.assertFalse(result.checks["package_shape"])
            self.assertFalse(result.checks["support_files"])
            self.assertTrue(any("validate.py" in failure for failure in result.failures))
            self.assertTrue(any("final-checklist.md" in failure for failure in result.failures))

    def test_oracle_manifest_must_match_waza_tasks(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tasks").mkdir()
            (root / "tasks" / "one.yaml").write_text("id: one\n", encoding="utf-8")
            (root / "adapter_manifest.json").write_text(
                json.dumps({"tasks": {"two": {"task_id": "two", "family": "routing-near-miss", "should_trigger": False}}}),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                load_oracle_manifest(root)

    def test_oracle_manifest_rejects_task_id_mismatch(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tasks").mkdir()
            (root / "tasks" / "one.yaml").write_text("id: two\n", encoding="utf-8")
            (root / "adapter_manifest.json").write_text(
                json.dumps({"tasks": {"one": {"task_id": "one", "family": "probe", "should_trigger": True}}}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "task id does not match filename"):
                load_oracle_manifest(root)

    def test_benchmark_oracle_rejects_paths_outside_candidate_root(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / ".github/skills/create-skill"
            fixture = root / "fixtures/.github/skills/create-skill"
            package.mkdir(parents=True)
            fixture.mkdir(parents=True)
            (package / "SKILL.md").write_text("See references/original-spec.md\n", encoding="utf-8")
            (fixture / "SKILL.md").write_text("See references/original-spec.md\n", encoding="utf-8")
            outside = root.parent / "oracle-outside-sentinel.txt"
            outside.write_text("sentinel\n", encoding="utf-8")
            try:
                result = evaluate_task(
                    "probe",
                    {
                        "family": "probe",
                        "should_trigger": True,
                        "required_paths": ["../oracle-outside-sentinel.txt", str(outside)],
                        "required_support_files": ["../../oracle-outside-sentinel.txt"],
                        "provenance_path": ".github/skills/create-skill/SKILL.md",
                    },
                    root,
                )
            finally:
                outside.unlink()
            self.assertFalse(result.passed)
            self.assertFalse(result.checks["package_shape"])
            self.assertFalse(result.checks["support_files"])
            self.assertIn("escape candidate root", " ".join(result.failures))

    def test_script_self_containment_rejects_undeclared_third_party_import(self):
        with TemporaryDirectory() as directory:
            package = Path(directory) / ".github/skills/create-skill"
            script = package / "scripts/check.py"
            script.parent.mkdir(parents=True)
            (package / "scripts/skill_lint_core.py").write_text("def lint(): pass\n", encoding="utf-8")
            for source in (
                "import requests\nfrom skill_lint_core import lint\n",
                "__import__('requests')\n",
                "import importlib\nimportlib.import_module('requests')\n",
                "from importlib import import_module\nimport_module('requests')\n",
                "import importlib as il\nil.import_module('requests')\n",
                "import importlib\nmodule = importlib\nmodule.import_module('requests')\n",
                "import importlib\nloader = importlib.import_module\nloader('requests')\n",
                "import importlib\nloader = getattr(importlib, 'import_module')\nloader('requests')\n",
                "import importlib\ngetattr(importlib, 'import_module')('requests')\n",
                "from builtins import __import__ as load\nload('requests')\n",
                "import builtins as b\nb.__import__('requests')\n",
            ):
                with self.subTest(source=source):
                    script.write_text(source, encoding="utf-8")
                    result = evaluate_task(
                        "probe",
                        {
                            "family": "scripts-validation",
                            "should_trigger": True,
                            "required_paths": [".github/skills/create-skill/SKILL.md"],
                            "required_support_files": ["scripts/check.py"],
                            "provenance_path": ".github/skills/create-skill/SKILL.md",
                        },
                        Path(directory),
                    )
                    self.assertFalse(result.checks["script_self_containment"])
                    self.assertIn("non-self-contained scripts", " ".join(result.failures))

    def test_script_self_containment_allows_normal_local_imports(self):
        with TemporaryDirectory() as directory:
            package = Path(directory) / ".github/skills/create-skill"
            script = package / "scripts/check.py"
            script.parent.mkdir(parents=True)
            script.write_text(
                "import importlib\nfrom importlib import import_module\nimport yaml\n",
                encoding="utf-8",
            )
            result = evaluate_task(
                "probe",
                {
                    "family": "scripts-validation",
                    "should_trigger": True,
                    "required_paths": [".github/skills/create-skill/SKILL.md"],
                    "required_support_files": ["scripts/check.py"],
                    "provenance_path": ".github/skills/create-skill/SKILL.md",
                },
                Path(directory),
            )
            self.assertTrue(result.checks["script_self_containment"])

    def test_near_miss_gate_rejects_unauthorized_create_skill_result(self):
        passed, reason = apply_routing_gate(
            {"final_output": "I created the create-skill package with SKILL.md"}, False
        )
        self.assertFalse(passed)
        self.assertIn("unauthorized", reason)

    def test_skillopt_launcher_registers_create_skill_adapter(self):
        launcher = importlib.import_module("scripts.skillopt_train")
        launcher.register_create_skill()
        self.assertIs(launcher.skillopt_train._ENV_REGISTRY["create-skill"], launcher.WazaSkillOptAdapter)

    def test_skillopt_config_uses_supported_environment_and_excludes_holdout(self):
        from skillopt.config import flatten_config, load_config

        config_path = (
            Path(__file__).parents[1]
            / "experiments"
            / "optimization"
            / "create-skill"
            / "skillopt.yaml"
        )
        config = flatten_config(load_config(str(config_path)))
        self.assertEqual(config["env"], "create-skill")
        self.assertEqual(config["eval_root"], "experiments/optimization/create-skill/benchmark")
        self.assertNotIn("holdout", config["eval_root"])

    def test_sentinel_is_test_only_and_benchmark_mutation_is_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "SKILL.md"
            skill.write_text("body\n", encoding="utf-8")
            insert_sentinel(skill, "trial-1")
            self.assertEqual(count_sentinels(skill), 1)
            remove_sentinel(skill)
            self.assertEqual(skill.read_text(encoding="utf-8"), "body\n")

            fixture = root / "fixture.txt"
            fixture.write_text("frozen\n", encoding="utf-8")
            lock = root / "benchmark.lock.json"
            freeze_benchmark(root, lock)
            verify_benchmark(root, lock)
            fixture.write_text("mutated\n", encoding="utf-8")
            with self.assertRaises(BenchmarkMutationError):
                verify_benchmark(root, lock)

    def test_scaffold_is_deterministic_and_persists_original_spec(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            config = ScaffoldConfig("chosen-by-user", ("SKILL.md", "references/guide.md"), ("semantic",))
            summary = scaffold_skill(root, config, "# Original request\n")
            validate_scaffold(root, config)
            self.assertEqual(summary["architecture_id"], "chosen-by-user")
            self.assertEqual(
                (root / "references" / "original-spec.md").read_text(encoding="utf-8"),
                "# Original request\n",
            )
            self.assertEqual(scaffold_skill(root, config, "# Original request\n"), summary)

    def test_selection_applies_hard_constraints_before_quality_ordering(self):
        constraints = SelectionConstraints(max_false_positive_final_rate=0.0)
        selected, report = select_architecture(
            [
                ArchitectureResult("unsafe-high-score", {
                    "false_positive_final_rate": 1.0,
                    "false_positive_recovery_rate": 1.0,
                    "reject_route_accuracy": 1.0,
                    "unexpected_workflow_entry_rate": 0.0,
                    "post_sentinel_tool_calls": 0,
                    "discovery": {"f1": 1.0},
                    "admission": {"f1": 1.0},
                }),
                ArchitectureResult("safe-lower-score", {
                    "false_positive_final_rate": 0.0,
                    "false_positive_recovery_rate": 1.0,
                    "reject_route_accuracy": 1.0,
                    "unexpected_workflow_entry_rate": 0.0,
                    "post_sentinel_tool_calls": 0,
                    "discovery": {"f1": 0.7},
                    "admission": {"f1": 0.8},
                }),
            ],
            constraints,
        )
        self.assertEqual(selected.architecture_id, "safe-lower-score")
        self.assertEqual(report["rejected"], ["unsafe-high-score"])

    def test_skillopt_result_normalization_preserves_extra_evidence(self):
        result = normalize_rollout_result(
            {"task_id": "t1", "passed": True, "score": 0.75, "tool_events": ["read"]}
        )
        self.assertEqual(result["id"], "t1")
        self.assertEqual(result["hard"], 1)
        self.assertEqual(result["soft"], 0.75)
        self.assertEqual(result["extras"]["tool_events"], ["read"])

    def test_waza_discovery_disables_skill_body_injection(self):
        with TemporaryDirectory() as directory:
            eval_path = Path(directory) / "eval.yaml"
            eval_path.write_text("name: routing\nskill: demo\n", encoding="utf-8")
            configure_summary_only_discovery(eval_path)
            self.assertIn("inject_skill_body: false", eval_path.read_text(encoding="utf-8"))

    def test_skillopt_resolves_waza_before_split_cwd_is_used(self):
        repository_root = Path(__file__).parents[1]
        adapter = WazaSkillOptAdapter(
            "experiments/optimization/create-skill/benchmark",
            ".tools/bin/waza",
        )
        adapter.setup({"canonical_config": "config/canonical-skill-architecture.json"})
        self.assertEqual(adapter.waza_bin, repository_root / ".tools/bin/waza")

        with TemporaryDirectory() as directory:
            split_root = Path(directory) / "selection"
            split_root.mkdir()
            eval_path = split_root / "eval.yaml"
            output_path = split_root / "result.json"
            eval_path.write_text("name: routing\n", encoding="utf-8")

            def fake_run(command, **kwargs):
                self.assertTrue(Path(command[0]).is_absolute())
                self.assertEqual(kwargs["cwd"], eval_path.parent)
                output_path.write_text("{}", encoding="utf-8")
                return type("Completed", (), {"returncode": 0, "stdout": "", "stderr": ""})()

            with patch("skill_harness.waza_adapter.subprocess.run", side_effect=fake_run):
                run_waza(eval_path, output_path, waza_bin=adapter.waza_bin)

    def test_skillopt_setup_initializes_inherited_reflect_configuration(self):
        adapter = WazaSkillOptAdapter(
            "experiments/optimization/create-skill/benchmark",
            ".tools/bin/waza",
        )
        adapter.setup({
            "analyst_workers": 3,
            "failure_only": True,
            "minibatch_size": 2,
            "edit_budget": 5,
        })

        with TemporaryDirectory() as directory, patch(
            "skillopt.gradient.reflect.run_minibatch_reflect",
            return_value=[],
        ) as reflect:
            self.assertEqual(adapter.reflect([], "skill", directory), [])

        arguments = reflect.call_args.kwargs
        self.assertEqual(arguments["workers"], 3)
        self.assertTrue(arguments["failure_only"])
        self.assertEqual(arguments["minibatch_size"], 2)
        self.assertEqual(arguments["edit_budget"], 5)
        self.assertEqual(adapter._cfg["analyst_workers"], 3)

    def test_waza_nonzero_exit_with_valid_output_returns_payload_and_diagnostics(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            eval_path = root / "eval.yaml"
            output_path = root / "result.json"
            output_path.write_text('{"runs": [{"task_id": "failed-task", "passed": false}]}', encoding="utf-8")
            completed = type("Completed", (), {"returncode": 1, "stdout": "task failed\n", "stderr": ""})()

            with patch("skill_harness.waza_adapter.subprocess.run", return_value=completed):
                result = run_waza(eval_path, output_path)

            self.assertEqual(result.payload["runs"][0]["task_id"], "failed-task")
            self.assertEqual(result.metadata["returncode"], 1)
            self.assertEqual(result.metadata["stdout"], "task failed\n")

    def test_waza_nonzero_exit_without_valid_output_raises(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            eval_path = root / "eval.yaml"
            output_path = root / "result.json"
            completed = type("Completed", (), {"returncode": 1, "stdout": "", "stderr": "runner failed"})()

            with patch("skill_harness.waza_adapter.subprocess.run", return_value=completed):
                with self.assertRaises(WazaError):
                    run_waza(eval_path, output_path)

    def test_waza_nonzero_exit_with_invalid_output_raises(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            eval_path = root / "eval.yaml"
            output_path = root / "result.json"
            output_path.write_text("not json", encoding="utf-8")
            completed = type("Completed", (), {"returncode": 1, "stdout": "", "stderr": "runner failed"})()

            with patch("skill_harness.waza_adapter.subprocess.run", return_value=completed):
                with self.assertRaises(WazaError):
                    run_waza(eval_path, output_path)

    def test_skillopt_maps_trainer_splits_without_exposing_holdout_in_config(self):
        adapter = WazaSkillOptAdapter(
            "experiments/optimization/create-skill/benchmark",
            ".tools/bin/waza",
        )
        adapter.setup({})
        selection = adapter.build_eval_env(1, "valid_seen", 42)
        holdout = adapter.build_eval_env(1, "valid_unseen", 42)
        self.assertEqual(selection["split"], "selection")
        self.assertEqual(holdout["split"], "holdout")
        self.assertTrue(str(selection["eval"]).endswith("selection/eval.yaml"))
        self.assertTrue(str(holdout["eval"]).endswith("holdout/eval.yaml"))

    def test_skillopt_bounds_waza_tasks_in_temporary_eval(self):
        import yaml

        adapter = WazaSkillOptAdapter(
            "experiments/optimization/create-skill/benchmark",
            ".tools/bin/waza",
        )
        adapter.setup({"train_size": 1, "batch_size": 2, "steps_per_epoch": 2})
        with TemporaryDirectory() as directory:
            env = adapter.build_eval_env(1, "valid_seen", 42, out_root=directory)
            captured = {}

            def fake_run_waza(eval_path, output_path, **kwargs):
                captured["eval"] = Path(eval_path)
                return type(
                    "Run",
                    (),
                    {
                        "payload": {
                            "runs": [
                                {"task_id": task_id, "passed": True}
                                for task_id in env["expected_task_ids"]
                            ]
                        }
                    },
                )()

            skill = Path(
                "experiments/optimization/create-skill/benchmark/selection"
                "/.github/skills/create-skill/SKILL.md"
            ).read_text(encoding="utf-8")
            with patch("skill_harness.skillopt_adapter.run_waza", side_effect=fake_run_waza):
                adapter.rollout(env, skill, directory)
            payload = yaml.safe_load(captured["eval"].read_text(encoding="utf-8"))
            self.assertEqual(len(payload["tasks"]), 1)
            self.assertNotEqual(captured["eval"].parent, adapter.eval_root / "selection")
            self.assertEqual(len(env["expected_task_ids"]), 1)

    def test_skillopt_requires_exactly_one_waza_result_per_task(self):
        adapter = WazaSkillOptAdapter(
            "experiments/optimization/create-skill/benchmark",
            ".tools/bin/waza",
        )
        adapter._cfg = {}
        env = adapter.build_eval_env(1, "valid_seen", 42)
        skill = Path(
            "experiments/optimization/create-skill/benchmark/selection"
            "/.github/skills/create-skill/SKILL.md"
        ).read_text(encoding="utf-8")
        expected = sorted(path.stem for path in (adapter.eval_root / "selection" / "tasks").glob("*.yaml"))
        cases = {
            "empty": [],
            "unknown": [{"task_id": "unknown", "passed": True}],
            "duplicate": [{"task_id": expected[0], "passed": True}, {"task_id": expected[0], "passed": True}],
            "missing": [{"task_id": task_id, "passed": True} for task_id in expected[:-1]],
        }
        for name, rows in cases.items():
            with self.subTest(case=name), TemporaryDirectory() as directory, patch(
                "skill_harness.skillopt_adapter.run_waza",
                return_value=type("Run", (), {"payload": {"runs": rows}})(),
            ):
                with self.assertRaises(WazaError):
                    adapter.rollout(env, skill, directory)

    def test_skillopt_rejects_non_dictionary_waza_result(self):
        adapter = WazaSkillOptAdapter(
            "experiments/optimization/create-skill/benchmark",
            ".tools/bin/waza",
        )
        adapter._cfg = {}
        env = adapter.build_eval_env(1, "valid_seen", 42)
        skill = Path(
            "experiments/optimization/create-skill/benchmark/selection"
            "/.github/skills/create-skill/SKILL.md"
        ).read_text(encoding="utf-8")
        with TemporaryDirectory() as directory, patch(
            "skill_harness.skillopt_adapter.run_waza",
            return_value=type("Run", (), {"payload": {"runs": [None]}})(),
        ):
            with self.assertRaisesRegex(WazaError, "non-object"):
                adapter.rollout(env, skill, directory)

    def test_skillopt_fixtures_copy_frozen_source_after_candidate_support_mutation(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            candidate = root / "candidate"
            (source / ".github/skills/create-skill/references").mkdir(parents=True)
            (source / ".github/skills/create-skill/SKILL.md").write_text(
                "See references/original-spec.md\n", encoding="utf-8"
            )
            (source / ".github/skills/create-skill/references/original-spec.md").write_text(
                "frozen\n", encoding="utf-8"
            )
            (source / "SKILL.md").write_text("See original-spec.md\n", encoding="utf-8")
            shutil.copytree(source, candidate)
            support = candidate / ".github/skills/create-skill/references/original-spec.md"
            support.write_text("mutated\n", encoding="utf-8")

            WazaSkillOptAdapter._populate_fixtures(candidate, source)

            fixture = candidate / "fixtures/.github/skills/create-skill/references/original-spec.md"
            self.assertEqual(fixture.read_text(encoding="utf-8"), "frozen\n")
            result = evaluate_task(
                "probe",
                {
                    "family": "support-file-discipline",
                    "should_trigger": True,
                    "required_paths": [".github/skills/create-skill/SKILL.md"],
                    "required_support_files": ["references/original-spec.md"],
                    "provenance_path": ".github/skills/create-skill/references/original-spec.md",
                },
                candidate,
            )
            self.assertFalse(result.passed)
            self.assertFalse(result.checks["support_files"])

    def test_skillopt_populates_waza_fixtures_before_run(self):
        adapter = WazaSkillOptAdapter(
            "experiments/optimization/create-skill/benchmark",
            ".tools/bin/waza",
        )
        adapter.setup({})
        env = adapter.build_eval_env(1, "valid_seen", 42)
        with TemporaryDirectory() as directory:
            def fake_run_waza(eval_path, output_path, **kwargs):
                candidate_root = Path(eval_path).parent
                self.assertTrue((candidate_root / "eval.yaml").is_file())
                self.assertTrue((candidate_root / "tasks").is_dir())
                self.assertTrue((candidate_root / "fixtures" / "SKILL.md").is_file())
                self.assertTrue(
                    (candidate_root / "fixtures" / ".github" / "skills" / "create-skill" / "SKILL.md").is_file()
                )
                task_ids = [path.stem for path in (Path(eval_path).parent / "tasks").glob("*.yaml")]
                return type("Run", (), {"payload": {"runs": [{"task_id": task_id} for task_id in task_ids]}})()

            skill = Path(
                "experiments/optimization/create-skill/benchmark/selection"
                "/.github/skills/create-skill/SKILL.md"
            ).read_text(encoding="utf-8")
            with patch("skill_harness.skillopt_adapter.run_waza", side_effect=fake_run_waza):
                adapter.rollout(env, skill, directory)

    def test_structural_candidate_rejection_skips_waza(self):
        adapter = WazaSkillOptAdapter(
            "experiments/optimization/create-skill/benchmark",
            ".tools/bin/waza",
        )
        adapter.setup({"canonical_config": "config/canonical-skill-architecture.json"})
        env = adapter.build_eval_env(1, "valid_seen", 42)
        with TemporaryDirectory() as directory:
            with patch(
                "skill_harness.skillopt_adapter.validate_skill_structure",
                side_effect=ValueError("invalid candidate"),
            ), patch("skill_harness.skillopt_adapter.run_waza") as run:
                results = adapter.rollout(env, "broken", directory)
            run.assert_not_called()
            self.assertEqual(results[0]["hard"], 0)
            self.assertEqual(results[0]["extras"]["rejected"], True)
            self.assertIn("invalid candidate", results[0]["extras"]["rejection_reason"])

    def test_routing_trace_parser_detects_invocation_sentinel_and_post_calls(self):
        trial = parse_routing_observation(
            {
                "output": "ROUTING_EVAL_ACCEPTED",
                "tokens": 12,
                "tool_events": [
                    {"tool_name": "skill_invocation", "skill": "demo"},
                    {"tool_name": "read", "path": "ROUTING_EVAL_WORKFLOW_ENTRY"},
                    {"tool_name": "write", "path": "unexpected"},
                ],
            },
            expected_route=None,
            discovery_expected=True,
            admission_expected=True,
        )
        self.assertTrue(trial.discovery_actual)
        self.assertEqual(trial.sentinel_events, 2)
        self.assertEqual(trial.post_sentinel_tool_calls, 1)

    def test_routing_trace_parser_reads_waza_transcript_events(self):
        trial = parse_routing_observation(
            {
                "transcript": [
                    {"type": "tool.execution_start", "tool_name": "skill", "arguments": {"skill": "tdd"}},
                    {"type": "skill.invoked"},
                    {"type": "tool.execution_start", "tool_name": "view", "arguments": {"path": "references/__routing_probe__.md"}},
                ]
            },
            expected_route=None,
            discovery_expected=True,
            admission_expected=True,
        )
        self.assertTrue(trial.discovery_actual)
        self.assertTrue(trial.admission_actual)
        self.assertEqual(trial.sentinel_events, 1)
        self.assertEqual(trial.tool_calls, 3)

    def test_routing_trace_parser_recognizes_plugin_and_workspace_skill_paths(self):
        for root in ("agentic-core/skills", ".github/skills"):
            with self.subTest(root=root):
                trial = parse_routing_observation(
                    {
                        "transcript": [
                            {
                                "type": "tool.execution_start",
                                "tool_name": "view",
                                "arguments": {
                                    "path": f"/workspace/{root}/tdd/references/__routing_probe__.md"
                                },
                            },
                            {"type": "skill.invoked"},
                            {
                                "type": "tool.execution_start",
                                "tool_name": "view",
                                "arguments": {
                                    "path": f"/workspace/{root}/create-skill/SKILL.md"
                                },
                            },
                        ]
                    },
                    expected_route="create-skill",
                    discovery_expected=True,
                    admission_expected=True,
                )

                self.assertTrue(trial.discovery_actual)
                self.assertTrue(trial.admission_actual)
                self.assertEqual(trial.actual_route, "create-skill")
                self.assertEqual(trial.sentinel_events, 1)
                self.assertEqual(trial.post_sentinel_tool_calls, 1)

    def test_candidate_is_cloned_and_structurally_gated_before_waza(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "SKILL.md").write_text(
                "---\nname: candidate\ndescription: demo\n---\n\nMUTABLE\n", encoding="utf-8"
            )
            (source / "references").mkdir()
            (source / "references" / "original-spec.md").write_text("spec\n", encoding="utf-8")
            config = ScaffoldConfig("canonical", ("SKILL.md",), ("MUTABLE",))
            benchmark = root / "benchmark"
            benchmark.mkdir()
            (benchmark / "task.json").write_text("{}\n", encoding="utf-8")
            lock = root / "benchmark.lock.json"
            freeze_benchmark(benchmark, lock)
            candidate = clone_skill_workspace(source, root / "candidate", "S0")
            validate_candidate_before_waza(candidate, config, benchmark, lock)
            (candidate.path / "SKILL.md").write_text("broken\n", encoding="utf-8")
            with self.assertRaises(Exception):
                validate_candidate_before_waza(candidate, config, benchmark, lock)

    def test_routing_variants_share_semantics_and_isolate_deferred_workflow(self):
        spec = RoutingSpec(
            "s1",
            "routing-demo",
            "A routing demo",
            ("matching requests",),
            ({"case": "other requests", "route": "create-agent"},),
            "Read the sentinel, then do the expensive work.",
            (RoutingCase("positive", "match", True, "accept"),),
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            inline = render_routing_variant(
                spec,
                RoutingArchitecture("inline", "inline_workflow", "grouped_lists", "SKILL.md"),
                root / "inline",
            )
            deferred = render_routing_variant(
                spec,
                RoutingArchitecture("deferred", "deferred_workflow", "grouped_lists", "references/workflow.md"),
                root / "deferred",
            )
            self.assertEqual(inline["semantic_hash"], deferred["semantic_hash"])
            self.assertTrue((root / "inline" / "routing-demo" / "references" / SENTINEL_NAME).is_file())
            self.assertTrue((root / "deferred" / "routing-demo" / "references" / "workflow.md").is_file())

    def test_real_tdd_variants_have_distinct_disclosure_boundaries(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source" / "tdd"
            source.mkdir(parents=True)
            (source / "SKILL.md").write_text(
                "---\nname: tdd\ndescription: tdd\n---\n\n"
                "<definitions>\nA behavior.\n</definitions>\n\n"
                "<admission>\nACCEPT executable change.\n</admission>\n\n"
                "<routing>\nRoute the request.\n</routing>\n\n"
                "<workflow>\n## Step 0\nRun the test.\n</workflow>\n",
                encoding="utf-8",
            )
            variants = {}
            for name, disclosure, location in (
                ("simple", "simple_inline", "SKILL.md"),
                ("inline", "inline_workflow", "SKILL.md"),
                ("deferred", "deferred_workflow", "references/workflow.md"),
            ):
                destination = root / name
                variants[name] = render_real_skill_variant(
                    source,
                    RoutingArchitecture(name, disclosure, "grouped_lists", location),
                    destination,
                )
            simple_body = Path(variants["simple"]["skill"]).read_text(encoding="utf-8")
            inline_body = Path(variants["inline"]["skill"]).read_text(encoding="utf-8")
            deferred_dir = Path(variants["deferred"]["skill"]).parent
            deferred_body = (deferred_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("<admission>", simple_body)
            self.assertNotIn("<routing>", simple_body)
            self.assertIn("<admission>", inline_body)
            self.assertIn("## Step 0", inline_body)
            self.assertIn("<routing>", deferred_body)
            self.assertIn("references/workflow.md", deferred_body)
            self.assertNotIn("## Step 0", deferred_body)
            deferred_workflow = (deferred_dir / "references" / "workflow.md").read_text(encoding="utf-8")
            self.assertIn("## Step 0", deferred_workflow)
            self.assertNotIn("<workflow>", deferred_workflow)

    def test_simple_progressive_disclosure_has_no_admission_block(self):
        spec = RoutingSpec(
            "s1",
            "routing-demo",
            "A routing demo",
            ("matching requests",),
            ("other requests",),
            "Perform the workflow.",
            (RoutingCase("positive", "match", True, "accept"),),
        )
        with TemporaryDirectory() as directory:
            skill_path = Path(directory)
            render_routing_variant(
                spec,
                RoutingArchitecture("simple", "simple_inline", "grouped_lists", "SKILL.md"),
                skill_path,
            )
            body = (skill_path / "routing-demo" / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("## ACCEPT", body)
            self.assertIn("# Workflow", body)
            self.assertIn("The sentinel is terminal", body)

    def test_admission_variants_define_reject_contract_before_sentinel(self):
        spec = RoutingSpec(
            "s1",
            "routing-demo",
            "A routing demo",
            ("matching requests",),
            ({"case": "other requests", "route": "implementation"},),
            "Perform the workflow.",
            (RoutingCase("positive", "match", True, "accept"),),
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            render_routing_variant(
                spec,
                RoutingArchitecture("inline", "inline_workflow", "grouped_lists", "SKILL.md"),
                root / "inline",
            )
            body = (root / "inline" / "routing-demo" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn('"status":"rejected"', body)
            self.assertIn("do not read the sentinel", body)
            self.assertIn("read references/__routing_probe__.md as the first action", body)

    def test_phase_0a_preparation_renders_all_candidates_without_rollout(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            specs = root / "specs"
            architectures = root / "architectures"
            specs.mkdir()
            architectures.mkdir()
            (specs / "s1.json").write_text(
                '{"id":"s1","name":"demo","description":"demo","accept_rules":["match"],'
                '"reject_rules":[{"case":"other","route":"implementation"}],'
                '"workflow_payload":"work","cases":[{"id":"positive","prompt":"match",'
                '"should_use_skill":true,"expected_admission":"accept"}]}\n',
                encoding="utf-8",
            )
            for name, disclosure, location in (
                ("simple", "simple_inline", "SKILL.md"),
                ("inline", "inline_workflow", "SKILL.md"),
                ("deferred", "deferred_workflow", "references/workflow.md"),
            ):
                (architectures / f"{name}.json").write_text(
                    json.dumps({
                        "id": name,
                        "progressive_disclosure": disclosure,
                        "admission_representation": "grouped_lists",
                        "workflow_location": location,
                    }),
                    encoding="utf-8",
                )
            manifest = prepare_phase_0a(
                specs,
                architectures,
                root / "prepared",
                waza_bin=Path.cwd() / ".tools" / "bin" / "waza",
            )
            self.assertEqual(len(manifest["architectures"]), 3)
            self.assertTrue((root / "prepared" / "preparation.json").is_file())
            self.assertTrue((root / "prepared" / "deferred" / "s1" / "eval.yaml").is_file())

    def test_phase_0a_prepares_real_catalogue_sizes(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            specs = root / "specs"
            architectures = root / "architectures"
            source = root / "source" / "tdd"
            one = root / "one"
            five = root / "five"
            for path in (specs, architectures, source, one, five):
                path.mkdir(parents=True)
            (source / "SKILL.md").write_text(
                "---\nname: tdd\ndescription: real tdd\n---\n\n"
                "<admission>\nACCEPT code changes\n</admission>\n"
                "<routing>\nACCEPT then enter workflow\n</routing>\n"
                "<workflow>\n## Step 0 - Run\n1. Test\n</workflow>\n",
                encoding="utf-8",
            )
            for catalogue, names in ((one, ("tdd",)), (five, ("tdd", "create-agent", "create-hook", "code-exploration", "create-skill"))):
                skills = catalogue / ".github" / "skills"
                for name in names:
                    (skills / name).mkdir(parents=True)
                    (skills / name / "SKILL.md").write_text(
                        f"---\nname: {name}\ndescription: {name}\n---\n", encoding="utf-8"
                    )
            (specs / "tdd.json").write_text(
                json.dumps({
                    "id": "tdd",
                    "name": "tdd",
                    "description": "real tdd",
                    "accept_rules": ["code changes"],
                    "reject_rules": [],
                    "workflow_payload": "Test.",
                    "cases": [{"id": "positive", "prompt": "test", "should_use_skill": True, "expected_admission": "accept"}],
                }),
                encoding="utf-8",
            )
            for name, disclosure, location in (
                ("simple", "simple_inline", "SKILL.md"),
                ("inline", "inline_workflow", "SKILL.md"),
                ("deferred", "deferred_workflow", "references/workflow.md"),
            ):
                (architectures / f"{name}.json").write_text(json.dumps({
                    "id": name,
                    "progressive_disclosure": disclosure,
                    "admission_representation": "grouped_lists",
                    "workflow_location": location,
                }), encoding="utf-8")
            manifest = prepare_phase_0a(
                specs,
                architectures,
                root / "prepared",
                waza_bin=Path.cwd() / ".tools" / "bin" / "waza",
                source_skill=source,
                catalogue_roots={"1-skill": one, "5-skills": five},
            )
            self.assertEqual(manifest["catalogues"], ["1-skill", "5-skills"])
            self.assertEqual(len(manifest["architectures"][0]["fixtures"]), 2)
            for fixture in manifest["architectures"][1]["fixtures"]:
                skills = Path(fixture["skill"]).parent.parent
                expected = 1 if fixture["catalogue_id"] == "1-skill" else 5
                self.assertEqual(len([path for path in skills.iterdir() if path.is_dir()]), expected)
                self.assertTrue((skills.parent.parent / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
