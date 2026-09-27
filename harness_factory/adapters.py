from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from expertise.validator import load_json_no_duplicate_keys

from .errors import CapabilityUnavailableError, HarnessFactoryError
from .models import (
    CAPABILITY_NAMES,
    COPILOT_MIN_AI_CREDITS,
    CapabilityObservation,
    CapabilityState,
    HarnessCapabilities,
    HarnessResult,
    HarnessScenario,
    ResultStatus,
    RunMode,
    RunStatus,
)
from .runs import HarnessRun, HarnessRunManager
from .validation import materialize_source

_COPILOT_RULES: dict[str, tuple[CapabilityState, tuple[str, ...]]] = {
    "plugin_installation": (
        CapabilityState.HOST_SPECIFIC,
        ("--plugin-dir", "plugin install"),
    ),
    "skills": (CapabilityState.HOST_SPECIFIC, ("skill list", "--plugin-dir")),
    "custom_agents": (
        CapabilityState.HOST_SPECIFIC,
        ("--agent", "--add-dir"),
    ),
    "mcp": (
        CapabilityState.HOST_SPECIFIC,
        ("mcp list", "--additional-mcp-config"),
    ),
    "non_interactive_execution": (
        CapabilityState.SUPPORTED,
        ("--prompt",),
    ),
    "structured_output": (
        CapabilityState.SUPPORTED,
        ("--output-format", "jsonl"),
    ),
    "model_selection": (CapabilityState.SUPPORTED, ("--model",)),
    "sandboxing": (
        CapabilityState.HOST_SPECIFIC,
        ("sandbox",),
    ),
    "token_usage_reporting": (
        CapabilityState.SUPPORTED,
        ("--usage-output-file",),
    ),
}

_CODEX_RULES: dict[str, tuple[CapabilityState, tuple[str, ...]]] = {
    "plugin_installation": (
        CapabilityState.HOST_SPECIFIC,
        ("plugins",),
    ),
    "skills": (CapabilityState.HOST_SPECIFIC, ("skill_search",)),
    "custom_agents": (CapabilityState.HOST_SPECIFIC, ("--agent", "agent file")),
    "mcp": (CapabilityState.HOST_SPECIFIC, ("mcp", "mcp_servers")),
    "non_interactive_execution": (
        CapabilityState.SUPPORTED,
        ("exec", "--prompt"),
    ),
    "structured_output": (
        CapabilityState.SUPPORTED,
        ("--json", "--output-schema"),
    ),
    "model_selection": (CapabilityState.SUPPORTED, ("--model",)),
    "sandboxing": (
        CapabilityState.HOST_SPECIFIC,
        ("--sandbox", "read-only"),
    ),
    "token_usage_reporting": (
        CapabilityState.SUPPORTED,
        ("turn.completed", "token usage reporting"),
    ),
}


class HarnessAdapter(ABC):
    name: str
    executable_name: str

    @abstractmethod
    def detect(self) -> HarnessCapabilities:
        raise NotImplementedError

    def prepare(self, run: HarnessRun, source_relative: Path) -> Path:
        if run.harness != self.name:
            raise HarnessFactoryError("run target does not match this harness adapter")
        if run.status is not RunStatus.PREPARED:
            raise HarnessFactoryError("only a prepared run can materialize its source")
        if run.allowed_mutations != (run.mode is RunMode.DEVELOPMENT):
            raise HarnessFactoryError(
                "run mutation policy is inconsistent with its mode"
            )
        if source_relative.is_absolute() or ".." in source_relative.parts:
            raise HarnessFactoryError(
                "plugin source must be relative to the run workspace"
            )
        source_root = run.workspace / source_relative
        if source_root.is_symlink():
            raise HarnessFactoryError("plugin source root must not be a symlink")
        try:
            resolved_source = source_root.resolve(strict=True)
            resolved_workspace = run.workspace.resolve(strict=True)
            resolved_source.relative_to(resolved_workspace)
        except (OSError, ValueError) as exc:
            raise HarnessFactoryError(
                "plugin source must exist under the pinned run workspace"
            ) from exc
        return self.materialize(run, resolved_source)

    def materialize(self, run: HarnessRun, source_root: Path) -> Path:
        if run.harness != self.name:
            raise HarnessFactoryError("run target does not match this harness adapter")
        if run.status is not RunStatus.PREPARED:
            raise HarnessFactoryError("only a prepared run can materialize its source")
        return materialize_source(
            source_root,
            self.name,
            workspace=run.workspace,
            run_id=run.run_id,
        )

    @abstractmethod
    def run_scenario(
        self,
        run: HarnessRun,
        plugin_path: Path,
        scenario: HarnessScenario,
    ) -> HarnessResult:
        raise NotImplementedError

    def collect_result(
        self,
        *,
        run: HarnessRun,
        scenario: HarnessScenario,
        returncode: int,
        output: str,
        elapsed_ms: int,
        usage_file: Path | None = None,
        errors: tuple[str, ...] = (),
        model_turns: int | None = None,
        model_calls: int | None = None,
        additional_observations: Mapping[str, Any] | None = None,
    ) -> HarnessResult:
        normalized_output = output.strip()
        matched = normalized_output == scenario.expected_output
        required_observations = {
            observation: observation in normalized_output
            for observation in scenario.required_observations
        }
        forbidden_observations = {
            observation: observation in normalized_output
            for observation in scenario.forbidden_observations
        }
        optional_observations = {
            observation: observation in normalized_output
            for observation in scenario.optional_observations
        }
        assertions = [
            {"name": "process-exit-zero", "passed": returncode == 0},
            {"name": "expected-output", "passed": matched},
        ]
        assertions.extend(
            {
                "name": f"required:{observation}",
                "passed": observed,
            }
            for observation, observed in required_observations.items()
        )
        assertions.extend(
            {
                "name": f"forbidden:{observation}",
                "passed": not observed,
            }
            for observation, observed in forbidden_observations.items()
        )
        final_errors = list(errors)
        if returncode != 0:
            final_errors.append(f"harness exited with code {returncode}")
        elif not matched:
            final_errors.append("harness response did not match the expected output")
        if not all(required_observations.values()):
            final_errors.append("one or more required observations were missing")
        if any(forbidden_observations.values()):
            final_errors.append("one or more forbidden observations were present")

        token_usage = _read_token_usage(usage_file) if usage_file is not None else None
        observations: dict[str, Any] = {
            "exit_code": returncode,
            "response_matches": matched,
            "required_observations": required_observations,
            "forbidden_observations": forbidden_observations,
            "optional_observations": optional_observations,
            "response_sha256": hashlib.sha256(
                normalized_output.encode("utf-8")
            ).hexdigest(),
        }
        for name, value in (additional_observations or {}).items():
            if not isinstance(name, str) or not name or name in observations:
                raise HarnessFactoryError(
                    "additional result observation has an invalid name"
                )
            observations[name] = value

        return HarnessResult(
            run_id=run.run_id,
            harness=self.name,
            status=(
                ResultStatus.PASSED
                if returncode == 0 and matched and not final_errors
                else ResultStatus.FAILED
            ),
            scenario=scenario.scenario_id,
            base_revision=run.base_revision,
            observations=observations,
            assertions=tuple(assertions),
            artifacts=(
                (str(usage_file),)
                if usage_file is not None and usage_file.is_file()
                else ()
            ),
            evidence=(f"cli:{self.executable_name}", f"base:{run.base_revision}"),
            token_usage=token_usage,
            latency_ms=elapsed_ms,
            model_turns=model_turns,
            model_calls=model_calls,
            errors=tuple(final_errors),
        )

    def cleanup(
        self,
        manager: HarnessRunManager,
        run_id: str,
        *,
        owner: str,
    ) -> HarnessRun:
        return manager.cleanup(run_id, owner=owner)

    @abstractmethod
    def development_command(
        self, run: HarnessRun, plugin_path: Path
    ) -> tuple[str, ...]:
        raise NotImplementedError


class CliHarnessAdapter(HarnessAdapter):
    def __init__(self, *, probe_timeout_seconds: int = 10):
        self.probe_timeout_seconds = probe_timeout_seconds

    def _detect_cli(
        self,
        *,
        rules: Mapping[str, tuple[CapabilityState, tuple[str, ...]]],
        additional_help_commands: tuple[tuple[str, ...], ...] = (),
    ) -> HarnessCapabilities:
        executable = shutil.which(self.executable_name)
        unknown = {
            name: CapabilityObservation(CapabilityState.UNKNOWN)
            for name in CAPABILITY_NAMES
        }
        if executable is None:
            return HarnessCapabilities(
                harness=self.name,
                cli_installed=False,
                executable=None,
                version=None,
                capabilities=unknown,
                diagnostics=(f"{self.executable_name} executable not found on PATH",),
            )

        diagnostics: list[str] = []
        version = self._probe(executable, ("--version",), diagnostics)
        help_text = self._probe(executable, ("--help",), diagnostics)
        for command in additional_help_commands:
            help_text += "\n" + self._probe(executable, command, diagnostics)
        observations = dict(unknown)
        lowered_help = help_text.casefold()
        for name, (state, signals) in rules.items():
            matched = tuple(
                signal for signal in signals if signal.casefold() in lowered_help
            )
            if matched:
                observations[name] = CapabilityObservation(state, matched)
        return HarnessCapabilities(
            harness=self.name,
            cli_installed=True,
            executable=executable,
            version=version.splitlines()[0].strip() if version else None,
            capabilities=observations,
            diagnostics=tuple(diagnostics),
            observed_options=tuple(
                re.findall(r"--[a-z][a-z0-9-]*", help_text.casefold())
            ),
        )

    def _probe(
        self,
        executable: str,
        arguments: tuple[str, ...],
        diagnostics: list[str],
    ) -> str:
        try:
            completed = subprocess.run(
                [executable, *arguments],
                capture_output=True,
                check=False,
                encoding="utf-8",
                errors="replace",
                env=_probe_environment(),
                timeout=self.probe_timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            diagnostics.append(
                f"{' '.join(arguments)} probe failed: {type(exc).__name__}"
            )
            return ""
        if completed.returncode != 0:
            diagnostics.append(
                f"{' '.join(arguments)} probe exited {completed.returncode}"
            )
        return completed.stdout + "\n" + completed.stderr


class CopilotHarnessAdapter(CliHarnessAdapter):
    name = "copilot"
    executable_name = "copilot"

    def detect(self) -> HarnessCapabilities:
        return self._detect_cli(rules=_COPILOT_RULES)

    def development_command(
        self, run: HarnessRun, plugin_path: Path
    ) -> tuple[str, ...]:
        if run.mode is not RunMode.DEVELOPMENT:
            raise HarnessFactoryError("a development command requires development mode")
        _require_plugin_path(run, plugin_path)
        capabilities = self.detect()
        _require_capability(capabilities, "plugin_installation")
        return (
            self.executable_name,
            "--no-auto-update",
            "-C",
            str(run.workspace),
            "--plugin-dir",
            str(plugin_path),
        )

    def run_scenario(
        self,
        run: HarnessRun,
        plugin_path: Path,
        scenario: HarnessScenario,
    ) -> HarnessResult:
        _require_read_only_validation_run(run, self.name)
        if scenario.max_ai_credits < COPILOT_MIN_AI_CREDITS:
            raise CapabilityUnavailableError(
                f"Copilot CLI requires at least {COPILOT_MIN_AI_CREDITS} AI credits"
            )
        capabilities = self.detect()
        _require_capability(capabilities, "non_interactive_execution")
        _require_capability(capabilities, "plugin_installation")
        if capabilities.executable is None:
            raise CapabilityUnavailableError("Copilot CLI executable is unavailable")
        plugin_path = _require_plugin_path(run, plugin_path)
        _require_options(
            capabilities,
            {
                "--no-auto-update",
                "--plugin-dir",
                "--prompt",
                "--disable-builtin-mcps",
                "--available-tools",
                "--allow-tool",
                "--deny-tool",
                "--max-ai-credits",
                "--silent",
                "--usage-output-file",
                "--no-custom-instructions",
            },
        )

        usage_file = run.state_directory / "usage.json"
        if usage_file.exists() or usage_file.is_symlink():
            raise HarnessFactoryError("usage output path already exists")
        mcp_servers = _plugin_mcp_servers(plugin_path)
        if mcp_servers:
            _require_options(capabilities, {"--disable-mcp-server"})
        command = [
            capabilities.executable,
            "--no-auto-update",
            "-C",
            str(run.workspace),
            "--plugin-dir",
            str(plugin_path),
            "--disable-builtin-mcps",
            "--available-tools=glob,grep,view",
            "--allow-tool=glob",
            "--allow-tool=grep",
            "--allow-tool=view",
            "--deny-tool=write",
            "--deny-tool=shell",
            "--max-ai-credits",
            str(scenario.max_ai_credits),
            "--silent",
            "--usage-output-file",
            str(usage_file),
            "--no-custom-instructions",
        ]
        for server in mcp_servers:
            command.extend(("--disable-mcp-server", server))
        command.extend(("--prompt", scenario.prompt))

        started = time.perf_counter()
        try:
            completed = subprocess.run(
                command,
                cwd=run.workspace,
                capture_output=True,
                check=False,
                encoding="utf-8",
                errors="replace",
                env=_harness_environment(),
                timeout=scenario.timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            elapsed = round((time.perf_counter() - started) * 1000)
            return self.collect_result(
                run=run,
                scenario=scenario,
                returncode=124,
                output="",
                elapsed_ms=elapsed,
                usage_file=usage_file,
                errors=("harness timed out",),
            )
        except OSError as exc:
            elapsed = round((time.perf_counter() - started) * 1000)
            return self.collect_result(
                run=run,
                scenario=scenario,
                returncode=127,
                output="",
                elapsed_ms=elapsed,
                usage_file=usage_file,
                errors=(f"harness could not start: {type(exc).__name__}",),
            )
        elapsed = round((time.perf_counter() - started) * 1000)
        return self.collect_result(
            run=run,
            scenario=scenario,
            returncode=completed.returncode,
            output=completed.stdout,
            elapsed_ms=elapsed,
            usage_file=usage_file,
        )


class CodexHarnessAdapter(CliHarnessAdapter):
    name = "codex"
    executable_name = "codex"

    def detect(self) -> HarnessCapabilities:
        return self._detect_cli(
            rules=_CODEX_RULES,
            additional_help_commands=(
                ("exec", "--help"),
                ("plugin", "--help"),
                ("features", "list"),
            ),
        )

    def development_command(
        self, run: HarnessRun, plugin_path: Path
    ) -> tuple[str, ...]:
        if run.mode is not RunMode.DEVELOPMENT:
            raise HarnessFactoryError("a development command requires development mode")
        _require_plugin_path(run, plugin_path)
        capabilities = self.detect()
        if capabilities.executable is None:
            raise CapabilityUnavailableError("Codex CLI executable is unavailable")
        _require_capability(capabilities, "plugin_installation")
        raise CapabilityUnavailableError(
            "Codex exposes plugins through project/local marketplaces, not a direct "
            "plugin-directory development command"
        )

    def run_scenario(
        self,
        run: HarnessRun,
        plugin_path: Path,
        scenario: HarnessScenario,
    ) -> HarnessResult:
        _require_read_only_validation_run(run, self.name)
        plugin_path = _require_plugin_path(run, plugin_path)
        declared_mcp_servers = _plugin_mcp_servers(plugin_path)
        if declared_mcp_servers:
            raise CapabilityUnavailableError(
                "Codex smoke cannot run plugins that declare MCP servers: "
                + ", ".join(declared_mcp_servers)
            )
        capabilities = self.detect()
        if not capabilities.cli_installed:
            raise CapabilityUnavailableError(
                "Codex CLI is not installed; runtime capabilities remain unknown"
            )
        for capability in (
            "non_interactive_execution",
            "structured_output",
            "sandboxing",
            "plugin_installation",
        ):
            _require_capability(capabilities, capability)
        required_options = {
            "--cd",
            "--json",
            "--ephemeral",
            "--sandbox",
            "--ignore-user-config",
        }
        missing = sorted(required_options - set(capabilities.observed_options))
        sandbox_evidence = capabilities.capabilities["sandboxing"].evidence
        if "read-only" not in sandbox_evidence:
            missing.append("read-only sandbox mode")
        if missing:
            raise CapabilityUnavailableError(
                "Codex CLI help does not evidence safe smoke options: "
                + ", ".join(missing)
            )

        environment = _harness_environment()
        command = [
            capabilities.executable,
            "exec",
            "--cd",
            str(run.workspace),
            "--ignore-user-config",
            "--sandbox",
            "read-only",
            "--ephemeral",
            "--json",
        ]
        command.append(scenario.prompt)

        started = time.perf_counter()
        with _codex_project_plugin(run, plugin_path):
            try:
                completed = subprocess.run(
                    command,
                    cwd=run.workspace,
                    capture_output=True,
                    check=False,
                    encoding="utf-8",
                    errors="replace",
                    env=environment,
                    timeout=scenario.timeout_seconds,
                )
            except subprocess.TimeoutExpired:
                elapsed = round((time.perf_counter() - started) * 1000)
                return self.collect_result(
                    run=run,
                    scenario=scenario,
                    returncode=124,
                    output="",
                    elapsed_ms=elapsed,
                    errors=("harness timed out",),
                )
            except OSError as exc:
                elapsed = round((time.perf_counter() - started) * 1000)
                return self.collect_result(
                    run=run,
                    scenario=scenario,
                    returncode=127,
                    output="",
                    elapsed_ms=elapsed,
                    errors=(f"harness could not start: {type(exc).__name__}",),
                )

        response, usage, parse_error, model_turns = _codex_result(completed.stdout)
        mcp_tool_calls = _codex_mcp_tool_calls(completed.stdout)
        usage_file = None
        if usage is not None:
            usage_file = run.state_directory / "usage.json"
            _write_usage_file(usage_file, usage)
        elapsed = round((time.perf_counter() - started) * 1000)
        return self.collect_result(
            run=run,
            scenario=scenario,
            returncode=completed.returncode,
            output=response,
            elapsed_ms=elapsed,
            usage_file=usage_file,
            errors=(parse_error,) if parse_error else (),
            model_turns=model_turns,
            additional_observations=_codex_mcp_observations(
                declared_mcp_servers,
                mcp_tool_calls,
            ),
        )


def _require_read_only_validation_run(run: HarnessRun, harness: str) -> None:
    if run.harness != harness:
        raise HarnessFactoryError("run target does not match this harness adapter")
    if run.mode is not RunMode.VALIDATION or run.allowed_mutations:
        raise HarnessFactoryError("harness smoke requires a read-only validation run")
    if run.status is not RunStatus.RUNNING:
        raise HarnessFactoryError("harness scenario requires a running run record")
    if run.cross_harness_request is not None:
        request = run.cross_harness_request
        if request.allowed_mutations or request.call_depth != 1:
            raise HarnessFactoryError(
                "cross-harness request violates validation policy"
            )


def _require_plugin_path(run: HarnessRun, plugin_path: Path) -> Path:
    if plugin_path.is_symlink() or not plugin_path.is_dir():
        raise HarnessFactoryError("materialized plugin directory is unavailable")
    try:
        resolved_plugin = plugin_path.resolve(strict=True)
        resolved_workspace = run.workspace.resolve(strict=True)
        resolved_plugin.relative_to(resolved_workspace)
    except (OSError, ValueError) as exc:
        raise HarnessFactoryError(
            "materialized plugin must be inside the pinned run workspace"
        ) from exc
    return resolved_plugin


def _require_capability(capabilities: HarnessCapabilities, name: str) -> None:
    observation = capabilities.capabilities[name]
    if observation.state not in {
        CapabilityState.SUPPORTED,
        CapabilityState.HOST_SPECIFIC,
    }:
        raise CapabilityUnavailableError(
            f"{capabilities.harness} capability {name!r} is {observation.state.value}"
        )
    if not capabilities.cli_installed or capabilities.executable is None:
        raise CapabilityUnavailableError(f"{capabilities.harness} CLI is not installed")


def _require_options(
    capabilities: HarnessCapabilities,
    required_options: set[str],
) -> None:
    missing = sorted(required_options - set(capabilities.observed_options))
    if missing:
        raise CapabilityUnavailableError(
            f"{capabilities.harness} CLI help does not evidence required options: "
            + ", ".join(missing)
        )


def _plugin_mcp_servers(plugin_path: Path) -> tuple[str, ...]:
    manifest_path = plugin_path / "mcp.json"
    if not manifest_path.exists():
        return ()
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise HarnessFactoryError("plugin mcp.json must be a regular file")
    try:
        manifest = load_json_no_duplicate_keys(manifest_path.read_bytes())
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        TypeError,
    ) as exc:
        raise HarnessFactoryError("plugin mcp.json is invalid") from exc
    servers = manifest.get("mcpServers") if isinstance(manifest, dict) else None
    if not isinstance(servers, dict):
        raise HarnessFactoryError("plugin mcp.json must declare mcpServers")
    return tuple(sorted(servers))


def _read_token_usage(path: Path | None) -> dict[str, int] | None:
    if path is None or path.is_symlink() or not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    model_metrics = payload.get("modelMetrics")
    if isinstance(model_metrics, dict):
        usage = _copilot_model_token_usage(model_metrics)
        if usage is not None:
            return usage
    usage = payload.get("token_usage")
    if not isinstance(usage, dict):
        return None
    normalized: dict[str, int] = {}
    for key, value in usage.items():
        if not isinstance(key, str) or type(value) is not int or value < 0:
            return None
        normalized[key] = value
    return normalized or None


def _copilot_model_token_usage(
    model_metrics: Mapping[str, Any],
) -> dict[str, int] | None:
    if not model_metrics:
        return None
    totals = {"input_tokens": 0, "output_tokens": 0}
    optional_fields = {
        "cacheReadTokens": "cache_read_tokens",
        "cacheWriteTokens": "cache_write_tokens",
        "reasoningTokens": "reasoning_tokens",
    }
    optional_totals = {normalized: 0 for normalized in optional_fields.values()}
    optional_complete = {normalized: True for normalized in optional_fields.values()}

    for metrics in model_metrics.values():
        usage = metrics.get("usage") if isinstance(metrics, dict) else None
        if not isinstance(usage, dict):
            return None
        for source, target in (
            ("inputTokens", "input_tokens"),
            ("outputTokens", "output_tokens"),
        ):
            value = usage.get(source)
            if type(value) is not int or value < 0:
                return None
            totals[target] += value
        for source, target in optional_fields.items():
            value = usage.get(source)
            if type(value) is int and value >= 0:
                optional_totals[target] += value
            else:
                optional_complete[target] = False

    totals.update(
        {
            field: value
            for field, value in optional_totals.items()
            if optional_complete[field]
        }
    )
    return totals


def _codex_result(
    output: str,
) -> tuple[str, dict[str, int] | None, str | None, int | None]:
    final_message: str | None = None
    token_usage: dict[str, int] = {}
    saw_usage = False
    usage_complete = True
    turn_failed = False
    turn_count = 0
    saw_turn_event = False
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("type") == "item.completed":
            item = event.get("item")
            if (
                isinstance(item, dict)
                and item.get("type") == "agent_message"
                and isinstance(item.get("text"), str)
            ):
                final_message = item["text"]
        if event.get("type") == "turn.completed":
            turn_count += 1
            saw_turn_event = True
            usage = event.get("usage")
            if isinstance(usage, dict):
                candidate = {
                    key: value
                    for key, value in usage.items()
                    if isinstance(key, str) and type(value) is int and value >= 0
                }
                if candidate and len(candidate) == len(usage):
                    saw_usage = True
                    for name, value in candidate.items():
                        token_usage[name] = token_usage.get(name, 0) + value
                else:
                    usage_complete = False
            else:
                usage_complete = False
        elif event.get("type") == "turn.failed":
            turn_failed = True
            turn_count += 1
            saw_turn_event = True
    model_turns = turn_count if saw_turn_event else None
    if final_message is None:
        return (
            "",
            _known_token_usage(token_usage, saw_usage, usage_complete),
            "Codex JSONL output did not contain a final agent message",
            model_turns,
        )
    if turn_failed:
        return (
            final_message,
            _known_token_usage(token_usage, saw_usage, usage_complete),
            "Codex reported a failed turn",
            model_turns,
        )
    return (
        final_message,
        _known_token_usage(token_usage, saw_usage, usage_complete),
        None,
        model_turns,
    )


def _known_token_usage(
    totals: dict[str, int], saw_usage: bool, usage_complete: bool
) -> dict[str, int] | None:
    if not saw_usage or not usage_complete:
        return None
    return totals


def _codex_mcp_tool_calls(output: str) -> tuple[dict[str, str], ...]:
    calls: dict[tuple[str, str], str] = {}
    event_status = {
        "item.started": "started",
        "item.updated": "started",
        "item.completed": "completed",
    }
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        event_type = event.get("type")
        item = event.get("item")
        if item is None and event_type in {"mcp_tool_call", "mcp_call"}:
            item = event
        if not isinstance(item, dict):
            continue
        item_type = item.get("type")
        if not isinstance(item_type, str) or item_type not in {
            "mcp_tool_call",
            "mcp_call",
        }:
            continue
        server = next(
            (
                item.get(field)
                for field in ("server", "server_name", "server_label")
                if isinstance(item.get(field), str) and item[field].strip()
            ),
            None,
        )
        tool = next(
            (
                item.get(field)
                for field in ("tool", "tool_name", "name")
                if isinstance(item.get(field), str) and item[field].strip()
            ),
            None,
        )
        if server is None or tool is None:
            continue
        status = "failed" if item.get("error") else event_status.get(event_type)
        if status is None:
            candidate_status = item.get("status")
            status = (
                candidate_status
                if isinstance(candidate_status, str)
                and candidate_status in {"started", "completed", "failed"}
                else "unknown"
            )
        key = (server.strip(), tool.strip())
        if key not in calls or status != "started":
            calls[key] = status
    return tuple(
        {"server": server, "tool": tool, "status": status}
        for (server, tool), status in sorted(calls.items())
    )


def _codex_mcp_observations(
    declared_servers: tuple[str, ...], calls: tuple[dict[str, str], ...]
) -> dict[str, Any]:
    return {
        "declared_mcp_servers": list(declared_servers),
        "mcp_tool_calls": list(calls),
        "observed_mcp_servers": sorted({call["server"] for call in calls}),
    }


def _write_usage_file(path: Path, usage: Mapping[str, int]) -> None:
    if path.exists() or path.is_symlink():
        raise HarnessFactoryError("usage output path already exists")
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        json.dump(
            {"token_usage": dict(usage)}, stream, ensure_ascii=False, sort_keys=True
        )
        stream.write("\n")


def _probe_environment() -> dict[str, str]:
    environment = {"PATH": os.environ.get("PATH", "")}
    for key in ("HOME", "SYSTEMROOT", "WINDIR", "LANG", "LC_ALL"):
        if key in os.environ:
            environment[key] = os.environ[key]
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return environment


def _harness_environment() -> dict[str, str]:
    environment = _probe_environment()
    for key in (
        "COPILOT_HOME",
        "CODEX_HOME",
        "XDG_CONFIG_HOME",
        "TMPDIR",
        "TEMP",
        "TMP",
    ):
        if key in os.environ:
            environment[key] = os.environ[key]
    return environment


@contextmanager
def _codex_project_plugin(run: HarnessRun, plugin_path: Path) -> Iterator[None]:
    manifest_path = plugin_path / "plugin.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise HarnessFactoryError("Codex plugin requires a regular plugin.json")
    try:
        manifest = load_json_no_duplicate_keys(manifest_path.read_bytes())
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        TypeError,
    ) as exc:
        raise HarnessFactoryError("Codex plugin.json is invalid") from exc
    if not isinstance(manifest, dict):
        raise HarnessFactoryError("Codex plugin.json must contain an object")
    plugin_name = manifest.get("name")
    if (
        not isinstance(plugin_name, str)
        or re.fullmatch(r"[a-z][a-z0-9.-]*", plugin_name) is None
    ):
        raise HarnessFactoryError("Codex plugin.json has an invalid plugin name")

    relative_plugin = plugin_path.relative_to(run.workspace).as_posix()
    if not relative_plugin or relative_plugin.startswith("../"):
        raise HarnessFactoryError(
            "Codex plugin path must be relative to the run workspace"
        )
    marketplace_name = f"harness-factory-{run.run_id[:8]}"
    marketplace_root = run.workspace / ".agents" / "plugins"
    marketplace_file = marketplace_root / "marketplace.json"
    codex_config_root = run.workspace / ".codex"
    codex_config_file = codex_config_root / "config.toml"
    files = {
        marketplace_file: (
            json.dumps(
                {
                    "name": marketplace_name,
                    "plugins": [
                        {
                            "name": plugin_name,
                            "source": {
                                "source": "local",
                                "path": f"./{relative_plugin}",
                            },
                            "policy": {
                                "installation": "AVAILABLE",
                                "authentication": "ON_INSTALL",
                            },
                            "category": "Validation",
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8"),
        codex_config_file: (
            f'[plugins."{plugin_name}@{marketplace_name}"]\nenabled = true\n'
        ).encode(),
    }
    directories = (
        run.workspace / ".agents",
        marketplace_root,
        codex_config_root,
    )
    for directory in directories:
        if directory.is_symlink():
            raise HarnessFactoryError(
                "Codex project plugin directories must not be symlinks"
            )
        if directory.exists() and not directory.is_dir():
            raise HarnessFactoryError("Codex project plugin path is not a directory")
    for path in files:
        if path.exists() or path.is_symlink():
            raise HarnessFactoryError(
                f"Codex project plugin config already exists: "
                f"{path.relative_to(run.workspace)}"
            )

    created_directories: list[Path] = []
    written: list[tuple[Path, bytes]] = []
    try:
        for directory in directories:
            if not directory.exists():
                directory.mkdir(mode=0o700)
                created_directories.append(directory)
        for path, content in files.items():
            written.append((path, content))
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content)
        yield
    finally:
        for path, content in reversed(written):
            if not path.exists() and not path.is_symlink():
                continue
            if path.is_symlink() or not path.is_file() or path.read_bytes() != content:
                raise HarnessFactoryError(
                    "Codex changed temporary plugin configuration; preserving it: "
                    f"{path}"
                )
            path.unlink()
        for directory in reversed(created_directories):
            if not directory.exists():
                continue
            if directory.is_symlink() or any(directory.iterdir()):
                raise HarnessFactoryError(
                    "Codex left unexpected files in temporary plugin configuration; "
                    f"preserving them: {directory}"
                )
            directory.rmdir()


@contextmanager
def _codex_project_plugin(run: HarnessRun, plugin_path: Path) -> Iterator[None]:
    manifest_path = plugin_path / "plugin.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise HarnessFactoryError("Codex plugin requires a regular plugin.json")
    try:
        manifest = load_json_no_duplicate_keys(manifest_path.read_bytes())
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        TypeError,
    ) as exc:
        raise HarnessFactoryError("Codex plugin.json is invalid") from exc
    if not isinstance(manifest, dict):
        raise HarnessFactoryError("Codex plugin.json must contain an object")
    plugin_name = manifest.get("name")
    if (
        not isinstance(plugin_name, str)
        or re.fullmatch(r"[a-z][a-z0-9.-]*", plugin_name) is None
    ):
        raise HarnessFactoryError("Codex plugin.json has an invalid plugin name")

    relative_plugin = plugin_path.relative_to(run.workspace).as_posix()
    if not relative_plugin or relative_plugin.startswith("../"):
        raise HarnessFactoryError(
            "Codex plugin path must be relative to the run workspace"
        )
    marketplace_name = f"harness-factory-{run.run_id[:8]}"
    marketplace_root = run.workspace / ".agents" / "plugins"
    marketplace_file = marketplace_root / "marketplace.json"
    codex_config_root = run.workspace / ".codex"
    codex_config_file = codex_config_root / "config.toml"
    files = {
        marketplace_file: (
            json.dumps(
                {
                    "name": marketplace_name,
                    "plugins": [
                        {
                            "name": plugin_name,
                            "source": {
                                "source": "local",
                                "path": f"./{relative_plugin}",
                            },
                            "policy": {
                                "installation": "AVAILABLE",
                                "authentication": "ON_INSTALL",
                            },
                            "category": "Validation",
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8"),
        codex_config_file: (
            f'[plugins."{plugin_name}@{marketplace_name}"]\nenabled = true\n'
        ).encode(),
    }
    directories = (
        run.workspace / ".agents",
        marketplace_root,
        codex_config_root,
    )
    created_directories: list[Path] = []
    for directory in directories:
        if directory.is_symlink():
            raise HarnessFactoryError(
                "Codex project plugin directories must not be symlinks"
            )
        if directory.exists():
            if not directory.is_dir():
                raise HarnessFactoryError(
                    "Codex project plugin path is not a directory"
                )
        else:
            directory.mkdir(mode=0o700)
            created_directories.append(directory)

    written: list[tuple[Path, bytes]] = []
    try:
        for path, content in files.items():
            if path.exists() or path.is_symlink():
                raise HarnessFactoryError(
                    f"Codex project plugin config already exists: {path.relative_to(run.workspace)}"
                )
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content)
            written.append((path, content))
        yield
    finally:
        for path, content in reversed(written):
            if path.is_symlink() or not path.is_file() or path.read_bytes() != content:
                raise HarnessFactoryError(
                    "Codex changed temporary plugin configuration; preserving it: "
                    f"{path}"
                )
            path.unlink()
        for directory in reversed(created_directories):
            if directory.exists() and not any(directory.iterdir()):
                directory.rmdir()
