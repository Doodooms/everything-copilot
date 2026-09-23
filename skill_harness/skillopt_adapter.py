from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .benchmark import verify_benchmark
from .benchmark_oracle import apply_routing_gate, evaluate_task, load_oracle_manifest
from .scaffold import ScaffoldConfig
from .validator import validate_skill_structure
from .waza_adapter import WazaError, run_waza

try:
    from skillopt.envs.base import EnvAdapter
except ImportError:  # pragma: no cover - exercised only without optional SkillOpt
    class EnvAdapter:  # type: ignore[no-redef]
        def setup(self, cfg: dict) -> None:
            self._cfg = cfg


def normalize_rollout_result(row: dict[str, Any]) -> dict[str, Any]:
    """Normalize Waza or local evidence to SkillOpt 0.2.0's result contract."""
    known = {"id", "hard", "soft"}
    return {
        "id": str(row.get("id", row.get("task_id", ""))),
        "hard": int(bool(row.get("hard", row.get("passed", False)))),
        "soft": float(row.get("soft", row.get("score", 0.0))),
        "extras": {key: value for key, value in row.items() if key not in known},
    }


def _extract_rows(payload: dict[str, Any]) -> list[Any]:
    for key in ("runs", "results", "tasks", "outcomes"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
    return []


def _validate_waza_rows(rows: list[Any], expected_task_ids: set[str]) -> None:
    if not rows:
        raise WazaError("Waza returned no task results")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise WazaError("Waza returned a non-object task result")
        task_id = str(row.get("id", row.get("task_id", "")))
        if task_id in seen:
            raise WazaError(f"Waza returned duplicate task result: {task_id}")
        if task_id not in expected_task_ids:
            raise WazaError(f"Waza returned unknown task result: {task_id}")
        seen.add(task_id)
    missing = sorted(expected_task_ids - seen)
    if missing:
        raise WazaError(f"Waza omitted task results: {', '.join(missing)}")


class WazaSkillOptAdapter(EnvAdapter):
    """SkillOpt EnvAdapter delegating scoring and traces to frozen Waza evals."""

    def __init__(self, eval_root: str, waza_bin: str = ".tools/bin/waza") -> None:
        self.eval_root = Path(eval_root)
        self.waza_bin = Path(waza_bin)
        self._cfg: dict[str, Any] = {}

    def _task_limit(self) -> int | None:
        limits = []
        train_size = self._cfg.get("train_size")
        if train_size is not None and int(train_size) > 0:
            limits.append(int(train_size))
        batch_size = self._cfg.get("batch_size")
        steps_per_epoch = self._cfg.get("steps_per_epoch")
        if batch_size is not None and steps_per_epoch is not None:
            workload = int(batch_size) * int(steps_per_epoch)
            if workload > 0:
                limits.append(workload)
        elif batch_size is not None and int(batch_size) > 0:
            limits.append(int(batch_size))
        elif steps_per_epoch is not None and int(steps_per_epoch) > 0:
            limits.append(int(steps_per_epoch))
        if not limits:
            return None
        return min(limits)

    def _materialize_eval(self, split: str, out_root: str | Path | None) -> Path:
        source_root = self.eval_root / split
        source_eval = source_root / "eval.yaml"
        limit = self._task_limit()
        if limit is None:
            return source_eval
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("PyYAML is required to bound Waza eval tasks") from exc
        payload = yaml.safe_load(source_eval.read_text(encoding="utf-8")) or {}
        task_patterns = payload.get("tasks")
        if not isinstance(task_patterns, list):
            raise ValueError(f"Waza eval tasks must be a list: {source_eval}")
        task_files = []
        for pattern in task_patterns:
            task_files.extend(sorted(source_root.glob(str(pattern))))
        selected = task_files[:limit]
        if out_root is None:
            temporary_root = Path(tempfile.mkdtemp(prefix="waza-eval-"))
        else:
            temporary_root = Path(out_root) / ".waza-evals" / split
            if temporary_root.exists():
                shutil.rmtree(temporary_root)
            temporary_root.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_root, temporary_root, dirs_exist_ok=True)
        payload["tasks"] = [str(path.relative_to(source_root)) for path in selected]
        temporary_eval = temporary_root / "eval.yaml"
        temporary_eval.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
        return temporary_eval

    @staticmethod
    def _expected_task_ids(eval_path: Path) -> set[str]:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("PyYAML is required to read Waza eval tasks") from exc
        payload = yaml.safe_load(eval_path.read_text(encoding="utf-8")) or {}
        task_patterns = payload.get("tasks")
        if not isinstance(task_patterns, list):
            raise ValueError(f"Waza eval tasks must be a list: {eval_path}")
        task_ids = set()
        for pattern in task_patterns:
            task_ids.update(path.stem for path in sorted(eval_path.parent.glob(str(pattern))))
        return task_ids

    def setup(self, cfg: dict) -> None:
        super().setup(cfg)
        self.analyst_workers = int(self._cfg.get("analyst_workers", 1))
        self.failure_only = bool(self._cfg.get("failure_only", False))
        self.minibatch_size = int(self._cfg.get("minibatch_size", 1))
        self.edit_budget = int(self._cfg.get("edit_budget", 4))
        if not self.waza_bin.is_absolute():
            canonical_config = self._cfg.get("canonical_config")
            if canonical_config:
                config_path = Path(canonical_config).expanduser().resolve()
                self.waza_bin = (config_path.parent.parent / self.waza_bin).resolve()
            else:
                self.waza_bin = self.waza_bin.expanduser().resolve()
        lock_path = self.eval_root / "benchmark.lock.json"
        if lock_path.exists():
            verify_benchmark(self.eval_root, lock_path)

    def get_dataloader(self):
        return None

    def build_train_env(self, batch_size: int, seed: int, **kwargs):
        eval_path = self._materialize_eval("train", kwargs.get("out_root"))
        return {
            "eval": eval_path,
            "split": "train",
            "expected_task_ids": self._expected_task_ids(eval_path),
        }

    def build_eval_env(self, env_num: int, split: str, seed: int, **kwargs):
        split_map = {
            "valid_seen": "selection",
            "valid_unseen": "holdout",
            "selection": "selection",
            "holdout": "holdout",
        }
        if split not in split_map:
            raise ValueError(f"unsupported SkillOpt split: {split}")
        actual_split = split_map[split]
        eval_path = self._materialize_eval(actual_split, kwargs.get("out_root"))
        return {
            "eval": eval_path,
            "split": actual_split,
            "expected_task_ids": self._expected_task_ids(eval_path),
        }

    @staticmethod
    def _populate_fixtures(candidate_root: Path, source_root: Path) -> None:
        fixtures_root = candidate_root / "fixtures"
        shutil.copytree(
            source_root,
            fixtures_root,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("eval.yaml", "tasks", "fixtures"),
        )

    def rollout(self, env_manager, skill_content: str, out_dir: str, **kwargs) -> list[dict]:
        eval_path = Path(env_manager["eval"])
        candidate_root = Path(out_dir) / f"candidate-{env_manager['split']}"
        if candidate_root.exists():
            shutil.rmtree(candidate_root)
        shutil.copytree(eval_path.parent, candidate_root, ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy2(eval_path.parent / "adapter_manifest.json", candidate_root / "adapter_manifest.json")
        candidate_skill = candidate_root / ".github" / "skills" / "create-skill" / "SKILL.md"
        candidate_skill.write_text(skill_content, encoding="utf-8")
        top_level_skill = candidate_root / "SKILL.md"
        if top_level_skill.exists():
            top_level_skill.write_text(skill_content, encoding="utf-8")
        self._populate_fixtures(candidate_root, eval_path.parent)
        config_path = self._cfg.get("canonical_config")
        if config_path:
            try:
                validate_skill_structure(candidate_skill.parent, ScaffoldConfig.from_file(Path(config_path)))
            except Exception as exc:
                return [normalize_rollout_result({
                    "id": f"candidate-{env_manager['split']}",
                    "hard": False,
                    "soft": 0.0,
                    "rejected": True,
                    "rejection_reason": str(exc),
                })]
        oracle_manifest = load_oracle_manifest(candidate_root)
        expected_task_ids = set(env_manager.get("expected_task_ids", oracle_manifest))
        oracle_results = {}
        for task_id in sorted(expected_task_ids):
            task_oracle = oracle_manifest.get(task_id)
            if task_oracle is None:
                return [normalize_rollout_result({
                    "id": task_id,
                    "hard": False,
                    "soft": 0.0,
                    "rejected": True,
                    "rejection_reason": "task is missing from adapter oracle manifest",
                })]
            result = evaluate_task(task_id, task_oracle, candidate_root)
            oracle_results[task_id] = result
            if not result.passed:
                return [normalize_rollout_result({
                    "id": task_id,
                    "hard": False,
                    "soft": 0.0,
                    "rejected": True,
                    "rejection_reason": "; ".join(result.failures),
                    "oracle": result.as_dict(),
                })]
        candidate_eval = candidate_root / eval_path.name
        output_path = Path(out_dir) / f"waza-{env_manager['split']}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        run = run_waza(candidate_eval, output_path, waza_bin=self.waza_bin, trials=1)
        rows = _extract_rows(run.payload)
        _validate_waza_rows(rows, expected_task_ids)
        results = []
        for row in rows:
            task_id = str(row.get("id", row.get("task_id", "")))
            metadata = oracle_manifest.get(task_id, {})
            routing_passed, routing_failure = apply_routing_gate(
                row, bool(metadata.get("should_trigger", True))
            )
            if not routing_passed:
                row = {
                    **row,
                    "passed": False,
                    "hard": False,
                    "rejected": True,
                    "rejection_reason": routing_failure,
                }
            row["oracle"] = {
                "checks": oracle_results.get(task_id).checks if task_id in oracle_results else {},
                "support_files_optimized": False,
                "support_files_source": "frozen fixture",
                "downstream_execution": "unavailable; Waza judges package guidance only",
                "routing_gate": "deterministic post-Waza result inspection",
            }
            results.append(normalize_rollout_result(row))
        return results

    def get_task_types(self) -> list[str]:
        return ["waza-task"]


def load_normalized_results(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [normalize_rollout_result(row) for row in _extract_rows(payload)]
