from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence



class WazaError(RuntimeError):
    """Raised when a Waza command fails or emits invalid results."""


def configure_summary_only_discovery(eval_path: Path, *, model: str | None = None) -> None:
    """Disable Waza skill-body injection using its supported eval config field."""
    try:
        import yaml
    except ImportError as exc:
        raise WazaError("PyYAML is required to edit Waza eval YAML") from exc
    try:
        payload = yaml.safe_load(eval_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise WazaError(f"invalid Waza eval: {eval_path}") from exc
    config = payload.setdefault("config", {})
    if not isinstance(config, dict):
        raise WazaError("Waza eval config must be a mapping")
    config["inject_skill_body"] = False
    if model:
        config["model"] = model
    eval_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


@dataclass(frozen=True)
class WazaRun:
    eval_path: Path
    output_path: Path
    trials: int
    payload: dict[str, Any]
    metadata: dict[str, Any] | None = None


def run_waza(
    eval_path: Path,
    output_path: Path,
    *,
    waza_bin: Path = Path(".tools/bin/waza"),
    trials: int = 1,
    context_dir: Path | None = None,
    transcript_dir: Path | None = None,
    extra_args: Sequence[str] = (),
) -> WazaRun:
    if trials < 1:
        raise WazaError("trials must be >= 1")
    command = [str(waza_bin), "run", str(eval_path), "--output", str(output_path), "--trials", str(trials)]
    if context_dir:
        command.extend(["--context-dir", str(context_dir)])
    if transcript_dir:
        command.extend(["--transcript-dir", str(transcript_dir)])
    command.extend(extra_args)
    completed = subprocess.run(
        command,
        cwd=eval_path.parent,
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        payload = json.loads(output_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        if completed.returncode != 0:
            raise WazaError(completed.stderr or completed.stdout or f"Waza exited {completed.returncode}") from exc
        raise WazaError(f"Waza did not produce valid JSON: {output_path}") from exc
    metadata = {
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    return WazaRun(eval_path, output_path, trials, payload, metadata)


def scaffold_waza_eval(
    skill_name: str,
    output_path: Path,
    *,
    waza_bin: Path = Path(".tools/bin/waza"),
) -> None:
    """Delegate eval-file scaffolding to the installed Waza version."""
    command = [str(waza_bin), "new", "eval", skill_name, "--output", str(output_path)]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise WazaError(completed.stderr or completed.stdout or f"Waza exited {completed.returncode}")


def verify_waza_spec(
    skill_path: Path,
    eval_path: Path,
    *,
    waza_bin: Path = Path(".tools/bin/waza"),
    fail: bool = True,
) -> dict[str, Any]:
    command = [str(waza_bin), "spec", "verify", "--skill", str(skill_path), "--eval", str(eval_path), "--format", "json"]
    if fail:
        command.append("--fail")
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if not completed.stdout.strip():
        raise WazaError(completed.stderr or f"Waza spec verify exited {completed.returncode}")
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise WazaError("Waza spec verify did not emit JSON") from exc
    if completed.returncode and fail:
        raise WazaError(json.dumps(result, sort_keys=True))
    return result
