#!/usr/bin/env python3
"""Generate a compact plan_index from an attached plan file.

Heuristics used (best-effort):
- Extract fenced code block labeled `repo-structure` or `repository-structure`.
- Fall back to a header titled 'Repo Structure' / 'Repository structure' and capture following paragraph or list.
- Fall back to a YAML key like `repo_structure:` in the plan.

Usage:
    python generate_plan_index.py path/to/PLAN.md --out plan_index.yaml
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path


def extract_fenced(text: str):
    m = re.search(r"```(?:repo-structure|repository-structure|repo_structure)\n(.*?)\n```", text, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else None


def extract_header_block(text: str):
    m = re.search(r"(?m)^(#{1,6}\s*(Repo(?:sitory)?\s*Structure|Repo-structure|Repository structure)\s*$)\n(.*?)(?:\n#{1,6}\s|\Z)", text, re.IGNORECASE | re.DOTALL)
    return m.group(2).strip() if m else None


def extract_yaml_key(text: str):
    m = re.search(r"(?m)^(repo[-_]structure\s*:\s*\n(?:\s+.+\n)+)", text, re.IGNORECASE)
    return m.group(1) if m else None


def lines_to_paths(block: str):
    paths = []
    for line in block.splitlines():
        line = line.strip().lstrip("-*")
        if not line:
            continue
        # Try to extract a path-like token
        part = line.split('#', 1)[0].strip()
        if part:
            paths.append(part)
    return paths


def build_plan_index(paths):
    return {"repo_structure": [{"path": p} for p in paths]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("plan", type=Path)
    p.add_argument("--out", type=Path, default=Path("plan_index.json"))
    args = p.parse_args()

    text = args.plan.read_text(encoding="utf-8")

    block = extract_fenced(text) or extract_header_block(text) or extract_yaml_key(text)
    if not block:
        print("No repo-structure block found in plan. Please include a 'Repo-structure' section or fenced `repo-structure` block.")
        raise SystemExit(2)

    # Normalize block and extract path lines
    paths = lines_to_paths(block)
    if not paths:
        print("Found block but no path-like lines were detected.")
        raise SystemExit(3)

    plan_index = build_plan_index(paths)
    args.out.write_text(json.dumps(plan_index, indent=2), encoding="utf-8")
    print(f"Wrote plan_index to {args.out}")


if __name__ == "__main__":
    main()
