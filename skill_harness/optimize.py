from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .benchmark import verify_benchmark
from .scaffold import ScaffoldConfig
from .validator import validate_skill_structure


class OptimizationError(RuntimeError):
    """Raised when an optimization precondition fails."""


@dataclass(frozen=True)
class CandidateWorkspace:
    name: str
    path: Path


def clone_skill_workspace(source: Path, destination: Path, name: str) -> CandidateWorkspace:
    if destination.exists():
        raise OptimizationError(f"candidate workspace already exists: {destination}")
    shutil.copytree(source, destination)
    return CandidateWorkspace(name, destination)


def validate_candidate_before_waza(
    candidate: CandidateWorkspace,
    config: ScaffoldConfig,
    benchmark_root: Path,
    benchmark_lock: Path,
) -> None:
    validate_skill_structure(candidate.path, config)
    try:
        verify_benchmark(benchmark_root, benchmark_lock)
    except Exception as exc:
        raise OptimizationError("frozen benchmark verification failed") from exc


def skillopt_train_command(
    config_path: Path,
    *,
    executable: Path = Path(".venv/bin/skillopt-train"),
    extra_args: Sequence[str] = (),
) -> list[str]:
    return [str(executable), "--config", str(config_path), *extra_args]


def run_skillopt_train(
    config_path: Path,
    *,
    executable: Path = Path(".venv/bin/skillopt-train"),
    extra_args: Sequence[str] = (),
) -> subprocess.CompletedProcess[str]:
    command = skillopt_train_command(config_path, executable=executable, extra_args=extra_args)
    return subprocess.run(command, text=True, capture_output=True, check=False)
