#!/usr/bin/env python3
"""Measure local, target-aware agent context without network access or file writes."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any


TOKENIZER_NAME = "local-regex-estimate-v1"
TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]", flags=re.UNICODE)


def _read_projection_file(root: Path, relative_path: Any, *, label: str) -> str:
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise ValueError(f"{label} must be a non-empty relative file path")

    path = Path(relative_path)
    if path.is_absolute():
        raise ValueError(f"{label} must be relative to the manifest root")

    root = root.resolve(strict=True)
    try:
        resolved = (root / path).resolve(strict=False)
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"{label} could not be resolved: {relative_path}") from exc

    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{label} resolves outside the manifest root: {relative_path}") from exc

    if not resolved.is_file():
        raise ValueError(f"{label} is not a file: {relative_path}")
    try:
        return resolved.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"{label} could not be read as UTF-8: {relative_path}") from exc


def _token_count(text: str) -> int:
    return len(TOKEN_PATTERN.findall(text))


def measure_file(file_path: Path) -> dict[str, Any]:
    try:
        resolved = file_path.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"file could not be read: {file_path}") from exc
    if not resolved.is_file():
        raise ValueError(f"file is not a regular file: {file_path}")
    try:
        text = resolved.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"file could not be read as UTF-8: {file_path}") from exc
    return {
        "tokenizer": TOKENIZER_NAME,
        "approximate": True,
        "file": str(file_path),
        "tokens": _token_count(text),
    }


def _path_list(value: Any, *, label: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{label} must be an array of relative file paths")
    return value


def _projection_paths(
    value: Any,
    *,
    label: str,
    kind: str,
) -> list[str]:
    paths = _path_list(value, label=label)
    for relative_path in paths:
        path = PurePosixPath(relative_path)
        if (
            not relative_path
            or relative_path != relative_path.strip()
            or "\\" in relative_path
            or path.is_absolute()
            or any(part in {"", ".", ".."} for part in path.parts)
        ):
            raise ValueError(f"{label} must contain safe, non-empty relative paths")
        if kind == "skill" and path.name != "SKILL.md":
            raise ValueError(f"{label} entries must point to a skill package's SKILL.md")
        if kind == "workflow":
            workflow_indices = [
                index for index, part in enumerate(path.parts) if part == "workflows"
            ]
            if (
                len(workflow_indices) != 1
                or workflow_indices[0] != len(path.parts) - 2
                or "references" in path.parts[: workflow_indices[0]]
                or path.suffix.lower() != ".md"
            ):
                raise ValueError(
                    f"{label} entries must point to immediate Markdown procedures under a package workflows/ directory"
                )
    return paths


def measure_projection(manifest_path: Path) -> dict[str, Any]:
    try:
        manifest_path = manifest_path.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"projection manifest could not be read: {manifest_path}") from exc
    if not manifest_path.is_file():
        raise ValueError(f"projection manifest is not a file: {manifest_path}")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"projection manifest is not readable JSON: {manifest_path}") from exc
    if not isinstance(manifest, dict):
        raise ValueError("projection manifest must be a JSON object")

    agents = manifest.get("agents")
    if not isinstance(agents, dict) or not agents:
        raise ValueError("projection manifest must contain a non-empty agents object")

    budget = manifest.get("warning_budget_tokens")
    if budget is not None and (type(budget) is not int or budget < 1):
        raise ValueError("warning_budget_tokens must be a positive integer or null")

    root = manifest_path.parent
    reports: dict[str, dict[str, int]] = {}
    warnings: list[str] = []
    for agent_id, projection in sorted(agents.items()):
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("agent IDs must be non-empty strings")
        if not isinstance(projection, dict):
            raise ValueError(f"projection for {agent_id} must be an object")
        if "subskills" in projection:
            raise ValueError(
                f"{agent_id} subskills are unsupported; project selected procedures under workflows"
            )

        definition_text = _read_projection_file(
            root,
            projection.get("definition"),
            label=f"{agent_id} definition",
        )
        skill_paths = _projection_paths(
            projection.get("skills", []),
            label=f"{agent_id} skills",
            kind="skill",
        )
        workflow_paths = _projection_paths(
            projection.get("workflows", []),
            label=f"{agent_id} workflows",
            kind="workflow",
        )
        reference_paths = _projection_paths(
            projection.get("references", []),
            label=f"{agent_id} references",
            kind="reference",
        )
        tool_paths = _path_list(projection.get("tools", []), label=f"{agent_id} tools")
        skill_tokens = sum(
            _token_count(_read_projection_file(root, path, label=f"{agent_id} skill"))
            for path in skill_paths
        )
        workflow_tokens = sum(
            _token_count(
                _read_projection_file(root, path, label=f"{agent_id} workflow")
            )
            for path in workflow_paths
        )
        tool_tokens = sum(
            _token_count(_read_projection_file(root, path, label=f"{agent_id} tool schema"))
            for path in tool_paths
        )
        definition_tokens = _token_count(definition_text)
        total_tokens = (
            definition_tokens + skill_tokens + workflow_tokens + tool_tokens
        )
        reports[agent_id] = {
            "definition": projection["definition"],
            "skills": skill_paths,
            "workflows": workflow_paths,
            "references_excluded": reference_paths,
            "tools": tool_paths,
            "definition_tokens": definition_tokens,
            "skill_tokens": skill_tokens,
            "workflow_tokens": workflow_tokens,
            "tool_tokens": tool_tokens,
            "total_tokens": total_tokens,
        }
        if budget is not None and total_tokens > budget:
            warnings.append(
                f"{agent_id} has {total_tokens} estimated local tokens, above the advisory "
                f"budget of {budget}; this is not a rejection or release gate."
            )

    return {
        "tokenizer": TOKENIZER_NAME,
        "approximate": True,
        "agents": reports,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure local agent, skill, and tool-schema projections or one text file."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--manifest", type=Path)
    source.add_argument(
        "--file",
        type=Path,
        help="count one local text file without a projection manifest",
    )
    args = parser.parse_args()

    try:
        report = (
            measure_file(args.file)
            if args.file is not None
            else measure_projection(args.manifest)
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
