from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))

from test_expertise_framework import (
    read_pack_manifest,
    write_pack,
    write_pack_manifest,
)

from expertise.ontology import AGENT_PLUGIN_SCHEMA
from harness_factory.adapters import (
    CodexHarnessAdapter,
    CopilotHarnessAdapter,
    _codex_result,
    _read_token_usage,
)
from harness_factory.cli import main as harness_factory_main
from harness_factory.errors import (
    CapabilityUnavailableError,
    HarnessFactoryError,
    RunOwnershipError,
)
from harness_factory.evaluation import (
    EvaluationProfile,
    load_run_artifact,
    run_suite,
    validate_run_target,
)
from harness_factory.evaluation import (
    RunBudget as EvaluationRunBudget,
)
from harness_factory.models import (
    CAPABILITY_NAMES,
    CapabilityObservation,
    CapabilityState,
    CrossHarnessRequest,
    HarnessCapabilities,
    HarnessResult,
    HarnessScenario,
    Purpose,
    ResultStatus,
    RunMode,
    RunStatus,
)
from harness_factory.runs import HarnessRun, HarnessRunManager
from harness_factory.suites import SuiteValidationError, load_suite, validate_suite
from harness_factory.validation import (
    _warnings_from_validator,
    materialize_source,
    validate_source,
)


def make_capabilities(
    harness: str,
    *,
    options: tuple[str, ...] = (),
    sandbox_evidence: tuple[str, ...] = (),
) -> HarnessCapabilities:
    observations = {
        name: CapabilityObservation(
            CapabilityState.SUPPORTED,
            ("fixture help output",),
        )
        for name in CAPABILITY_NAMES
    }
    if sandbox_evidence:
        observations["sandboxing"] = CapabilityObservation(
            CapabilityState.HOST_SPECIFIC,
            sandbox_evidence,
        )
    return HarnessCapabilities(
        harness=harness,
        cli_installed=True,
        executable=f"/usr/bin/{harness}",
        version="fixture 1.0",
        capabilities=observations,
        observed_options=options,
    )


def make_run(
    root: Path,
    harness: str,
    *,
    mode: RunMode = RunMode.VALIDATION,
    status: RunStatus = RunStatus.RUNNING,
    cross_harness_request: CrossHarnessRequest | None = None,
) -> HarnessRun:
    workspace = root / "workspace"
    state_directory = root / "state"
    workspace.mkdir(parents=True, exist_ok=True)
    state_directory.mkdir(parents=True, exist_ok=True)
    return HarnessRun(
        run_id=(
            cross_harness_request.run_id
            if cross_harness_request is not None
            else uuid4().hex
        ),
        harness=harness,
        base_revision="a" * 40,
        workspace=workspace,
        state_directory=state_directory,
        mode=mode,
        owner="fixture-owner",
        status=status,
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
        allowed_mutations=mode is RunMode.DEVELOPMENT,
        origin_harness=(
            cross_harness_request.origin_harness
            if cross_harness_request is not None
            else None
        ),
        call_depth=(
            cross_harness_request.call_depth if cross_harness_request is not None else 0
        ),
        cross_harness_request=cross_harness_request,
    )


def write_researcher_pack(root: Path) -> Path:
    source = write_pack(root, include_mcp=False)
    manifest = read_pack_manifest(source)
    manifest["compatibility"]["targets"] = ["portable", "copilot", "codex"]
    write_pack_manifest(source, manifest)
    return source


def init_git_repo(root: Path) -> tuple[Path, str]:
    root.mkdir(parents=True)
    for arguments in (
        ("init", "-q", str(root)),
        ("-C", str(root), "config", "user.name", "Harness Fixture"),
        ("-C", str(root), "config", "user.email", "fixture@example.invalid"),
    ):
        subprocess.run(["git", *arguments], check=True, capture_output=True, text=True)
    (root / "source.txt").write_text("baseline\n", encoding="utf-8")
    (root / ".gitignore").write_text("*.ignored\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(root), "add", "source.txt", ".gitignore"],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "-C", str(root), "commit", "-m", "fixture baseline"],
        check=True,
        capture_output=True,
        text=True,
    )
    revision = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return root, revision


class HarnessFactoryModelTests(unittest.TestCase):
    def test_cross_harness_request_rejects_mutation_recursion_and_bool_depth(self):
        values = {
            "run_id": uuid4().hex,
            "requested_by": "fixture-owner",
            "target_harness": "codex",
            "purpose": Purpose.VALIDATION,
            "artifact_under_test": "agentic-core",
            "base_revision": "a" * 40,
            "origin_harness": "copilot",
        }
        for invalid in (
            {"allowed_mutations": True},
            {"call_depth": 2},
            {"call_depth": True},
            {"target_harness": "copilot"},
            {"timeout_or_budget": ""},
            {"timeout_or_budget": [1]},
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                CrossHarnessRequest(**(values | invalid))

        request = CrossHarnessRequest(**values)
        self.assertEqual(request.call_depth, 1)
        self.assertFalse(request.allowed_mutations)
        self.assertIsNone(request.as_dict()["timeout_or_budget"])
        with self.assertRaises(TypeError):
            CrossHarnessRequest(**(values | {"purpose": "validation"}))
        with self.assertRaises(TypeError):
            CrossHarnessRequest(**(values | {"base_revision": None}))

    def test_run_models_reject_mutation_policy_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            run = make_run(
                Path(directory),
                "copilot",
                mode=RunMode.DEVELOPMENT,
            )
            with self.assertRaisesRegex(ValueError, "mutation permission"):
                HarnessRun(
                    **{
                        **run.__dict__,
                        "allowed_mutations": False,
                    }
                )

    def test_uninstalled_codex_reports_unknown_instead_of_assuming_features(self):
        with patch("harness_factory.adapters.shutil.which", return_value=None):
            capabilities = CodexHarnessAdapter().detect()
        self.assertFalse(capabilities.cli_installed)
        self.assertTrue(
            all(
                observation.state is CapabilityState.UNKNOWN
                for observation in capabilities.capabilities.values()
            )
        )

    def test_codex_detection_uses_observed_help_evidence(self):
        results = (
            subprocess.CompletedProcess([], 0, "codex fixture\n", ""),
            subprocess.CompletedProcess([], 0, "exec --json --sandbox read-only\n", ""),
            subprocess.CompletedProcess(
                [], 0, "--ephemeral --ignore-user-config --cd <DIR>\n", ""
            ),
            subprocess.CompletedProcess([], 0, "Manage Codex plugins\n", ""),
            subprocess.CompletedProcess(
                [], 0, "plugins stable true\nskill_search stable true\n", ""
            ),
        )
        with (
            patch(
                "harness_factory.adapters.shutil.which", return_value="/usr/bin/codex"
            ),
            patch("harness_factory.adapters.subprocess.run", side_effect=results),
        ):
            capabilities = CodexHarnessAdapter().detect()
        self.assertIn("--cd", capabilities.observed_options)
        self.assertEqual(
            capabilities.capabilities["plugin_installation"].state,
            CapabilityState.HOST_SPECIFIC,
        )
        self.assertEqual(
            capabilities.capabilities["skills"].state,
            CapabilityState.HOST_SPECIFIC,
        )
        self.assertEqual(
            capabilities.capabilities["sandboxing"].evidence,
            ("--sandbox", "read-only"),
        )

    def test_result_serialization_does_not_retain_response_text(self):
        result = HarnessResult(
            run_id=uuid4().hex,
            harness="copilot",
            status=ResultStatus.PASSED,
            scenario="fixture",
            base_revision="a" * 40,
            observations={"response_sha256": "0" * 64},
            assertions=({"name": "expected-output", "passed": True},),
        )
        payload = json.dumps(result.as_dict())
        self.assertNotIn("AGENT_PLUGIN_SMOKE_OK", payload)
        self.assertEqual(result.as_dict()["token_usage"], "unknown")
        self.assertEqual(result.as_dict()["latency_ms"], "unknown")


class HarnessRunManagerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repo, self.revision = init_git_repo(self.root / "repo")
        self.state_root = self.root / "factory-state"
        self.manager = HarnessRunManager(self.repo, self.state_root)

    def tearDown(self):
        self.temporary.cleanup()

    def create_run(self, *, harness: str = "copilot", **overrides) -> HarnessRun:
        return self.manager.create_run(
            harness=harness,
            base_revision=self.revision,
            mode=RunMode.VALIDATION,
            owner="fixture-owner",
            **overrides,
        )

    def test_runs_get_unique_detached_worktrees_and_round_trip_records(self):
        first = self.create_run()
        second = self.create_run(harness="codex")
        self.assertNotEqual(first.run_id, second.run_id)
        self.assertNotEqual(first.workspace, second.workspace)
        self.assertEqual(
            (first.workspace / "source.txt").read_text(encoding="utf-8"),
            "baseline\n",
        )
        self.assertEqual(self.manager.get_run(first.run_id), first)
        self.assertEqual(len(self.manager.list_runs()), 2)

    def test_owner_status_and_clean_workspace_are_required_for_cleanup(self):
        record = self.create_run()
        with self.assertRaises(RunOwnershipError):
            self.manager.transition(
                record.run_id,
                owner="different-owner",
                status=RunStatus.RUNNING,
            )
        running = self.manager.transition(
            record.run_id,
            owner=record.owner,
            status=RunStatus.RUNNING,
        )
        with self.assertRaisesRegex(HarnessFactoryError, "running"):
            self.manager.cleanup(record.run_id, owner=record.owner)
        completed = self.manager.transition(
            running.run_id,
            owner=running.owner,
            status=RunStatus.COMPLETED,
        )
        (completed.workspace / "untracked.txt").write_text(
            "preserve\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(HarnessFactoryError, "uncommitted changes"):
            self.manager.cleanup(completed.run_id, owner=completed.owner)
        self.assertTrue(completed.workspace.exists())

    def test_cleanup_refuses_ignored_user_files_and_missing_ownership_marker(self):
        ignored_run = self.create_run()
        ignored_file = ignored_run.workspace / "private.ignored"
        ignored_file.write_text("keep\n", encoding="utf-8")
        with self.assertRaisesRegex(HarnessFactoryError, "uncommitted changes"):
            self.manager.cleanup(ignored_run.run_id, owner=ignored_run.owner)
        self.assertTrue(ignored_file.is_file())

        unmarked_run = self.create_run()
        (unmarked_run.workspace / ".harness-factory-run").unlink()
        with self.assertRaisesRegex(RunOwnershipError, "ownership marker"):
            self.manager.cleanup(unmarked_run.run_id, owner=unmarked_run.owner)

    def test_nonempty_unowned_state_root_is_refused(self):
        state_root = self.root / "user-state"
        state_root.mkdir()
        (state_root / "keep.txt").write_text("untouched\n", encoding="utf-8")
        manager = HarnessRunManager(self.repo, state_root)
        with self.assertRaisesRegex(HarnessFactoryError, "not owned"):
            manager.create_run(
                harness="copilot",
                base_revision=self.revision,
                mode=RunMode.VALIDATION,
                owner="fixture-owner",
            )
        self.assertEqual(
            (state_root / "keep.txt").read_text(encoding="utf-8"), "untouched\n"
        )

    def test_record_id_tampering_cannot_redirect_run_ownership(self):
        record = self.create_run()
        record_path = record.state_directory / "run.json"
        payload = json.loads(record_path.read_text(encoding="utf-8"))
        payload["run_id"] = uuid4().hex
        record_path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(RunOwnershipError):
            self.manager.get_run(record.run_id)

    def test_cross_harness_run_is_read_only_and_exactly_one_hop(self):
        run_id = uuid4().hex
        request = CrossHarnessRequest(
            run_id=run_id,
            requested_by="fixture-owner",
            target_harness="codex",
            purpose=Purpose.VALIDATION,
            artifact_under_test="agentic-core",
            base_revision=self.revision,
            origin_harness="copilot",
            timeout_or_budget="unknown",
        )
        record = self.create_run(
            harness="codex",
            run_id=run_id,
            cross_harness_request=request,
        )
        self.assertEqual(record.call_depth, 1)
        self.assertFalse(record.allowed_mutations)
        self.assertEqual(self.manager.get_run(run_id).cross_harness_request, request)


class HarnessEvaluationTests(unittest.TestCase):
    def test_suite_contract_rejects_missing_behavior_without_harness_call(self):
        suite_payload = json.loads(
            (
                ROOT / "experiments/harness-evals/agentic-core-v0.2.0/suite.json"
            ).read_text(encoding="utf-8")
        )
        del suite_payload["scenarios"][0]["expected_behavior"]

        with self.assertRaisesRegex(
            SuiteValidationError,
            r"scenarios\[0\] is missing fields: expected_behavior",
        ):
            validate_suite(suite_payload)

    def test_target_policy_requires_allowed_copilot_reason(self):
        self.assertIsNone(validate_run_target("codex"))
        self.assertIsNone(validate_run_target("copilot", "portability_sample"))
        with self.assertRaisesRegex(ValueError, "allowed reason"):
            validate_run_target("copilot")
        with self.assertRaisesRegex(ValueError, "allowed reason"):
            validate_run_target("copilot", "routine_run")

    def test_suite_run_persists_fail_closed_artifact_without_invocation(self):
        suite = load_suite(
            ROOT / "experiments/harness-evals/agentic-core-v0.2.0/suite.json"
        )
        profile = EvaluationProfile(
            profile_id="unused-profile",
            source_path=Path("/unavailable/profile"),
        )
        invoke = Mock()
        with tempfile.TemporaryDirectory() as directory:
            artifact_path = Path(directory) / "run.json"
            result = run_suite(
                suite,
                profile,
                harness="codex",
                budget=EvaluationRunBudget(
                    max_runs=1,
                    max_model_calls=1,
                    max_tokens_if_known=25000,
                    max_failures_before_stop=1,
                ),
                invoke=invoke,
                artifact_path=artifact_path,
                run_id="b" * 32,
            )

            invoke.assert_not_called()
            self.assertEqual(result["status"], "blocked")
            self.assertEqual(
                result["stop_reason"],
                "provider model-call limit cannot be enforced by the selected harness",
            )
            self.assertEqual(result["usage"]["runs"], 0)
            self.assertEqual(result["usage"]["harness_invocations"], 0)
            self.assertEqual(result["usage"]["model_calls"], 0)
            persisted = load_run_artifact(artifact_path)
            self.assertEqual(persisted["run_id"], "b" * 32)
            self.assertTrue(
                all(
                    value == "unknown"
                    for values in persisted["metrics"].values()
                    for value in values.values()
                )
            )


class HarnessProviderTests(unittest.TestCase):
    def test_development_commands_pin_plugin_and_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            copilot_run = make_run(
                root / "copilot",
                "copilot",
                mode=RunMode.DEVELOPMENT,
                status=RunStatus.PREPARED,
            )
            copilot_plugin = copilot_run.workspace / "plugin"
            copilot_plugin.mkdir()
            copilot = CopilotHarnessAdapter()
            with patch.object(
                copilot,
                "detect",
                return_value=make_capabilities("copilot"),
            ):
                copilot_command = copilot.development_command(
                    copilot_run,
                    copilot_plugin,
                )
            self.assertIn("-C", copilot_command)
            self.assertIn(str(copilot_run.workspace), copilot_command)
            self.assertIn(str(copilot_plugin), copilot_command)

            codex_run = make_run(
                root / "codex",
                "codex",
                mode=RunMode.DEVELOPMENT,
                status=RunStatus.PREPARED,
            )
            codex_plugin = codex_run.workspace / "plugin"
            codex_plugin.mkdir()
            codex = CodexHarnessAdapter()
            with (
                patch.object(
                    codex,
                    "detect",
                    return_value=make_capabilities(
                        "codex",
                        options=("--cd",),
                    ),
                ),
                self.assertRaisesRegex(
                    CapabilityUnavailableError,
                    "project/local marketplaces",
                ),
            ):
                codex.development_command(codex_run, codex_plugin)

    def test_copilot_smoke_rejects_below_host_minimum_before_running(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = make_run(root, "copilot")
            plugin = run.workspace / "plugin"
            plugin.mkdir()
            adapter = CopilotHarnessAdapter()
            with (
                patch.object(adapter, "detect") as detect,
                patch("harness_factory.adapters.subprocess.run") as run_cli,
                self.assertRaisesRegex(
                    CapabilityUnavailableError,
                    "at least 30 AI credits",
                ),
            ):
                adapter.run_scenario(
                    run,
                    plugin,
                    HarnessScenario(
                        "fixture",
                        "Reply exactly.",
                        "AGENT_PLUGIN_SMOKE_OK",
                        max_ai_credits=1,
                    ),
                )
            detect.assert_not_called()
            run_cli.assert_not_called()

    def test_copilot_usage_output_metrics_are_normalized_without_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            usage_file = Path(directory) / "usage.json"
            usage_file.write_text(
                json.dumps(
                    {
                        "modelMetrics": {
                            "claude-sonnet-5": {
                                "usage": {
                                    "inputTokens": 5284,
                                    "outputTokens": 22,
                                    "cacheReadTokens": 2919,
                                    "cacheWriteTokens": 2285,
                                    "reasoningTokens": 0,
                                }
                            }
                        },
                        "agentMetrics": {
                            "main": {
                                "modelMetrics": {
                                    "claude-sonnet-5": {
                                        "usage": {
                                            "inputTokens": 5284,
                                            "outputTokens": 22,
                                        }
                                    }
                                }
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            self.assertEqual(
                _read_token_usage(usage_file),
                {
                    "input_tokens": 5284,
                    "output_tokens": 22,
                    "cache_read_tokens": 2919,
                    "cache_write_tokens": 2285,
                    "reasoning_tokens": 0,
                },
            )

    def test_copilot_smoke_grants_only_read_tools_and_disables_mcp(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = make_run(root, "copilot")
            plugin = run.workspace / "plugin"
            plugin.mkdir()
            (plugin / "mcp.json").write_text(
                json.dumps({"mcpServers": {"fixture-server": {}}}),
                encoding="utf-8",
            )
            options = (
                "--no-auto-update",
                "--plugin-dir",
                "--prompt",
                "--disable-builtin-mcps",
                "--disable-mcp-server",
                "--available-tools",
                "--allow-tool",
                "--deny-tool",
                "--max-ai-credits",
                "--silent",
                "--usage-output-file",
                "--no-custom-instructions",
            )
            adapter = CopilotHarnessAdapter()

            def fake_copilot_run(command, **kwargs):
                usage_path = Path(command[command.index("--usage-output-file") + 1])
                usage_path.write_text(
                    json.dumps(
                        {"token_usage": {"input_tokens": 10, "output_tokens": 2}}
                    ),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(
                    command,
                    0,
                    "AGENT_PLUGIN_SMOKE_OK\n",
                    "",
                )

            with (
                patch.object(
                    adapter,
                    "detect",
                    return_value=make_capabilities("copilot", options=options),
                ),
                patch(
                    "harness_factory.adapters.subprocess.run",
                    side_effect=fake_copilot_run,
                ) as run_cli,
            ):
                result = adapter.run_scenario(
                    run,
                    plugin,
                    HarnessScenario(
                        "fixture",
                        "Reply with exactly AGENT_PLUGIN_SMOKE_OK.",
                        "AGENT_PLUGIN_SMOKE_OK",
                    ),
                )
            command = run_cli.call_args.args[0]
            self.assertNotIn("--allow-all-tools", command)
            self.assertIn("--available-tools=glob,grep,view", command)
            self.assertIn("--allow-tool=glob", command)
            self.assertIn("--deny-tool=write", command)
            self.assertIn("--deny-tool=shell", command)
            self.assertIn("--disable-builtin-mcps", command)
            self.assertIn("--disable-mcp-server", command)
            self.assertEqual(result.status, ResultStatus.PASSED)
            self.assertEqual(
                result.token_usage, {"input_tokens": 10, "output_tokens": 2}
            )
            self.assertNotIn("AGENT_PLUGIN_SMOKE_OK", json.dumps(result.as_dict()))

    def test_codex_smoke_uses_ephemeral_local_marketplace_and_blocks_mcp(self):
        options = (
            "--cd",
            "--json",
            "--ephemeral",
            "--sandbox",
            "--ignore-user-config",
        )
        capabilities = make_capabilities(
            "codex",
            options=options,
            sandbox_evidence=("--sandbox", "read-only"),
        )
        adapter = CodexHarnessAdapter()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = make_run(root, "codex")
            plugin = run.workspace / "plugin"
            plugin.mkdir()
            (plugin / "plugin.json").write_text(
                json.dumps(
                    {
                        "$schema": AGENT_PLUGIN_SCHEMA,
                        "name": "codex-smoke",
                        "version": "1.0.0",
                        "description": "A local Codex smoke plugin.",
                    }
                ),
                encoding="utf-8",
            )
            scenario = HarnessScenario(
                "fixture",
                "$codex-smoke Reply with exactly AGENT_PLUGIN_SMOKE_OK.",
                "AGENT_PLUGIN_SMOKE_OK",
            )
            output = "\n".join(
                (
                    json.dumps(
                        {
                            "type": "item.completed",
                            "item": {
                                "type": "agent_message",
                                "text": "AGENT_PLUGIN_SMOKE_OK",
                            },
                        }
                    ),
                    json.dumps(
                        {
                            "type": "turn.completed",
                            "usage": {"input_tokens": 7, "output_tokens": 2},
                        }
                    ),
                )
            )

            def fake_codex_run(command, **kwargs):
                marketplace = json.loads(
                    (
                        run.workspace / ".agents" / "plugins" / "marketplace.json"
                    ).read_text(encoding="utf-8")
                )
                config = (run.workspace / ".codex" / "config.toml").read_text(
                    encoding="utf-8"
                )
                self.assertEqual(
                    marketplace["name"], f"harness-factory-{run.run_id[:8]}"
                )
                self.assertEqual(
                    marketplace["plugins"][0]["source"]["path"],
                    "./plugin",
                )
                self.assertIn('[plugins."codex-smoke@', config)
                return subprocess.CompletedProcess(command, 0, output, "")

            with (
                patch.object(adapter, "detect", return_value=capabilities),
                patch(
                    "harness_factory.adapters.subprocess.run",
                    side_effect=fake_codex_run,
                ) as run_cli,
            ):
                result = adapter.run_scenario(run, plugin, scenario)
            command = run_cli.call_args.args[0]
            self.assertIn("exec", command)
            self.assertIn("--cd", command)
            self.assertIn(str(run.workspace), command)
            self.assertNotIn("--plugin-dir", command)
            self.assertIn("read-only", command)
            self.assertIn("--ephemeral", command)
            environment = run_cli.call_args.kwargs["env"]
            self.assertNotEqual(
                environment.get("CODEX_HOME"),
                str(run.state_directory / "codex-home"),
            )
            self.assertNotIn("GH_TOKEN", environment)
            self.assertNotIn("GITHUB_TOKEN", environment)
            self.assertEqual(result.status, ResultStatus.PASSED)
            self.assertEqual(
                result.token_usage, {"input_tokens": 7, "output_tokens": 2}
            )
            self.assertFalse(
                (run.workspace / ".agents" / "plugins" / "marketplace.json").exists()
            )
            self.assertFalse((run.workspace / ".codex" / "config.toml").exists())

    def test_codex_smoke_refuses_declared_mcp_before_detecting_harness(self):
        adapter = CodexHarnessAdapter()
        with tempfile.TemporaryDirectory() as directory:
            run = make_run(Path(directory), "codex")
            plugin = run.workspace / "plugin"
            plugin.mkdir()
            (plugin / "mcp.json").write_text(
                json.dumps({"mcpServers": {"external": {}}}),
                encoding="utf-8",
            )
            with (
                patch.object(adapter, "detect") as detect,
                self.assertRaisesRegex(CapabilityUnavailableError, "MCP servers"),
            ):
                adapter.run_scenario(
                    run,
                    plugin,
                    HarnessScenario("fixture", "Reply exactly.", "OK"),
                )
            detect.assert_not_called()

    def test_plugin_path_outside_run_workspace_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            external_plugin = root / "external"
            external_plugin.mkdir()
            adapter = CopilotHarnessAdapter()
            with self.assertRaisesRegex(HarnessFactoryError, "inside the pinned"):
                adapter.development_command(
                    make_run(root / "dev", "copilot", mode=RunMode.DEVELOPMENT),
                    external_plugin,
                )

    def test_codex_jsonl_result_normalizes_final_message_and_usage(self):
        final, usage, error, model_turns = _codex_result(
            '{"type":"item.completed","item":{"type":"agent_message","text":"ok"}}\n'
            '{"type":"turn.completed","usage":{"input_tokens":4,"output_tokens":1}}\n'
        )
        self.assertEqual(
            (final, usage, error, model_turns),
            ("ok", {"input_tokens": 4, "output_tokens": 1}, None, 1),
        )
        final, usage, error, model_turns = _codex_result("not json\n")
        self.assertEqual(final, "")
        self.assertIsNone(usage)
        self.assertIsNotNone(error)
        self.assertIsNone(model_turns)
        _, _, error, model_turns = _codex_result(
            '{"type":"item.completed","item":{"type":"agent_message","text":"ok"}}\n'
            '{"type":"turn.failed"}\n'
        )
        self.assertEqual(error, "Codex reported a failed turn")
        self.assertEqual(model_turns, 1)

    def test_codex_cli_smoke_when_cli_is_absent_creates_no_run(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = io.StringIO()
            adapter = CodexHarnessAdapter()
            capabilities = HarnessCapabilities(
                harness="codex",
                cli_installed=False,
                executable=None,
                version=None,
                capabilities={
                    name: CapabilityObservation(CapabilityState.UNKNOWN)
                    for name in CAPABILITY_NAMES
                },
            )
            with (
                contextlib.redirect_stdout(output),
                patch.object(adapter, "detect", return_value=capabilities),
                patch(
                    "harness_factory.cli._adapters",
                    return_value={
                        "copilot": CopilotHarnessAdapter(),
                        "codex": adapter,
                    },
                ),
            ):
                status = harness_factory_main(
                    [
                        "smoke",
                        "--harness",
                        "codex",
                        "--repo-root",
                        str(root / "unused-repo"),
                        "--state-root",
                        str(root / "unused-state"),
                        "--base-revision",
                        "HEAD",
                        "--source",
                        "agentic-core",
                        "--owner",
                        "fixture-owner",
                    ]
                )
            result = json.loads(output.getvalue())
            self.assertEqual(status, 3)
            self.assertEqual(result["status"], "blocked")
            self.assertIn("CLI unavailable", result["reason"])
            self.assertFalse((root / "unused-state").exists())


class HarnessValidationTests(unittest.TestCase):
    def test_validate_cli_accepts_repeated_agent_ids_and_rejects_omission(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_researcher_pack(Path(directory) / "source")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = harness_factory_main(
                    [
                        "validate",
                        "--target",
                        "codex",
                        "--source-root",
                        str(source),
                        "--known-agent",
                        "architect",
                        "--known-agent",
                        "researcher",
                    ]
                )

            self.assertEqual(status, 0, output.getvalue())
            self.assertEqual(json.loads(output.getvalue())["status"], "passed")

            omitted_output = io.StringIO()
            with contextlib.redirect_stdout(omitted_output):
                omitted_status = harness_factory_main(
                    [
                        "validate",
                        "--target",
                        "codex",
                        "--source-root",
                        str(source),
                    ]
                )
            self.assertEqual(omitted_status, 2)
            self.assertIn("unknown agent 'researcher'", omitted_output.getvalue())

    def test_suite_run_preflight_uses_explicit_agent_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = write_researcher_pack(root / "source")
            profile_path = root / "profile.json"
            profile_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "profile_id": "fixture-profile",
                        "source_path": str(source),
                        "source_mode": "external",
                        "metadata": {},
                    }
                ),
                encoding="utf-8",
            )
            suite_path = (
                ROOT / "experiments/harness-evals/agentic-core-v0.2.0/suite.json"
            )
            adapter = Mock()
            adapter.detect.return_value = Mock(cli_installed=False)

            def run_suite_cli(preflight: Path, artifact: Path, known_agent: bool):
                arguments = [
                    "suite-run",
                    "--suite",
                    str(suite_path),
                    "--profile",
                    str(profile_path),
                    "--harness",
                    "codex",
                    "--repo-root",
                    str(ROOT),
                    "--state-root",
                    str(root / "state"),
                    "--owner",
                    "fixture-owner",
                    "--artifact",
                    str(artifact),
                    "--preflight-artifact",
                    str(preflight),
                    "--max-runs",
                    "1",
                    "--max-model-calls",
                    "1",
                    "--max-tokens-if-known",
                    "25000",
                    "--max-failures-before-stop",
                    "1",
                ]
                if known_agent:
                    arguments.extend(("--known-agent", "researcher"))
                output = io.StringIO()
                with (
                    contextlib.redirect_stdout(output),
                    patch(
                        "harness_factory.cli._adapters", return_value={"codex": adapter}
                    ),
                ):
                    status = harness_factory_main(arguments)
                return status, json.loads(output.getvalue())

            preflight = root / "preflight.json"
            status, result = run_suite_cli(preflight, root / "artifact.json", True)
            self.assertEqual(status, 2)
            self.assertIn("CLI is unavailable", result["message"])
            self.assertTrue(preflight.is_file())

            omitted_preflight = root / "omitted-preflight.json"
            omitted_status, omitted_result = run_suite_cli(
                omitted_preflight, root / "omitted-artifact.json", False
            )
            self.assertEqual(omitted_status, 2)
            self.assertIn("unknown agent 'researcher'", omitted_result["message"])
            self.assertFalse(omitted_preflight.exists())

    def test_adapter_prepare_uses_explicit_agent_catalog_and_rejects_omission(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = make_run(
                root,
                "codex",
                status=RunStatus.PREPARED,
            )
            write_researcher_pack(run.workspace / "source")
            adapter = CodexHarnessAdapter()

            output = adapter.prepare(
                run,
                Path("source"),
                known_agents=frozenset({"researcher"}),
            )
            self.assertTrue((output / "codex-agents/demo-pack-engineer.toml").is_file())

            omitted_root = root / "omitted"
            omitted_run = make_run(
                omitted_root,
                "codex",
                status=RunStatus.PREPARED,
            )
            write_researcher_pack(omitted_run.workspace / "source")
            with self.assertRaisesRegex(HarnessFactoryError, "unknown agent"):
                adapter.prepare(omitted_run, Path("source"))

    def test_validator_warning_normalization_omits_section_boilerplate(self):
        output = subprocess.CompletedProcess(
            [],
            0,
            "WARNINGS:\n  - meaningful warning\n"
            "Validation passed (warnings may need attention).\n",
            "",
        )
        self.assertEqual(
            _warnings_from_validator(output),
            ["meaningful warning"],
        )

    def test_static_plugin_validation_and_invalid_manifest_diagnostics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plugin = root / "plugin"
            plugin.mkdir()
            (plugin / "plugin.json").write_text(
                json.dumps({"$schema": AGENT_PLUGIN_SCHEMA, "name": "fixture-plugin"}),
                encoding="utf-8",
            )
            for target in ("copilot", "codex"):
                result = validate_source(plugin, target)
                self.assertEqual(result.status, "passed")
                self.assertIn("plugin.json", result.files)

            agent_directory = plugin / "com.github.copilot" / "agents"
            agent_directory.mkdir(parents=True)
            (agent_directory / "fixture.agent.md").write_text(
                "Copilot-only fixture\n",
                encoding="utf-8",
            )
            codex_validation = validate_source(plugin, "codex")
            self.assertTrue(
                any(
                    "Copilot agent definitions" in warning
                    for warning in codex_validation.warnings
                )
            )

            (plugin / "plugin.json").write_text(
                json.dumps({"$schema": AGENT_PLUGIN_SCHEMA, "name": "../unsafe"}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                HarnessFactoryError, "plugin manifest is invalid"
            ):
                validate_source(plugin, "copilot")

    def test_agent_validation_uses_the_pinned_plugin_validator(self):
        with tempfile.TemporaryDirectory() as directory:
            plugin = Path(directory) / "plugin"
            agent_validator = (
                plugin
                / "skills/plugin-engineering/references/create-agent/scripts/validate_agent.py"
            )
            agent_file = plugin / "com.github.copilot/agents/orchestrator.agent.md"
            agent_validator.parent.mkdir(parents=True)
            agent_validator.write_text("pass\n", encoding="utf-8")
            agent_file.parent.mkdir(parents=True)
            agent_file.write_text("fixture agent\n", encoding="utf-8")
            (plugin / "plugin.json").write_text(
                json.dumps({"$schema": AGENT_PLUGIN_SCHEMA, "name": "fixture-plugin"}),
                encoding="utf-8",
            )

            with patch(
                "harness_factory.validation._run_canonical_validator",
                return_value=subprocess.CompletedProcess([], 0, "", ""),
            ) as validator:
                result = validate_source(plugin, "copilot")

            self.assertEqual(result.status, "passed")
            self.assertEqual(validator.call_args.args[0], agent_validator)
            self.assertEqual(
                validator.call_args.args[1],
                ("--agent-file", str(agent_file)),
            )

    def test_expertise_pack_is_validated_and_materialized_inside_run_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspace"
            workspace.mkdir()
            source = write_pack(workspace / "source", include_mcp=False)
            manifest = read_pack_manifest(source)
            manifest["compatibility"]["targets"] = ["portable", "copilot", "codex"]
            write_pack_manifest(source, manifest)

            known_agents = frozenset({"researcher"})
            validation = validate_source(source, "codex", known_agents=known_agents)
            self.assertEqual(validation.source_kind, "expertise-pack")
            self.assertIn("codex-agents/demo-pack-engineer.toml", validation.files)

            output = materialize_source(
                source,
                "codex",
                workspace=workspace,
                run_id=uuid4().hex,
                known_agents=known_agents,
            )
            self.assertTrue(output.is_dir())
            self.assertEqual(output.name, "codex")
            self.assertEqual(output.parent.parent.name, "harness-factory")
            self.assertTrue((output / "codex-agents/demo-pack-engineer.toml").is_file())

    def test_expertise_pack_rejects_agents_outside_the_explicit_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_pack(Path(directory) / "source", include_mcp=False)

            with self.assertRaisesRegex(HarnessFactoryError, "unknown agent"):
                validate_source(source, "codex", known_agents=frozenset())

    def test_materialization_rejects_unsafe_run_id_and_symlinked_plugin_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspace"
            source = workspace / "source"
            source.mkdir(parents=True)
            (source / "pack.yaml").write_text("unused\n", encoding="utf-8")
            with self.assertRaisesRegex(HarnessFactoryError, "run_id"):
                materialize_source(
                    source,
                    "copilot",
                    workspace=workspace,
                    run_id="../outside",
                )

            plugin = root / "plugin"
            plugin.mkdir()
            outside = root / "outside.json"
            outside.write_text(
                json.dumps({"$schema": AGENT_PLUGIN_SCHEMA, "name": "fixture-plugin"}),
                encoding="utf-8",
            )
            (plugin / "plugin.json").symlink_to(outside)
            with self.assertRaisesRegex(HarnessFactoryError, "symlink"):
                validate_source(plugin, "copilot")


if __name__ == "__main__":
    unittest.main()
