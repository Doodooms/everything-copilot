# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML>=6.0,<7"]
# ///
"""Validate explicit lifecycle metadata on selected TODO source documents."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

ALLOWED_FIELDS = {"kind", "status", "disposition", "derived_work"}
ALLOWED_KINDS = {"design_input", "research_input", "work_brief"}
ALLOWED_STATUSES = {"raw", "triaged", "researched"}
ALLOWED_DISPOSITIONS = {
    "pending",
    "research_required",
    "adopted",
    "partially_adopted",
    "deferred",
    "blocked",
    "superseded",
    "rejected",
}


class UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects ambiguous duplicate mapping keys."""

    def construct_mapping(
        self, node: yaml.MappingNode, deep: bool = False
    ) -> dict[Any, Any]:
        self.flatten_mapping(node)
        mapping: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in mapping
            except TypeError as exc:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    "found an unhashable mapping key",
                    key_node.start_mark,
                ) from exc
            if duplicate:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key {key!r}",
                    key_node.start_mark,
                )
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


def parse_frontmatter(text: str) -> dict[str, Any]:
    """Read a YAML mapping from a Markdown document's leading frontmatter."""
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        raise ValueError("missing leading YAML frontmatter")
    try:
        frontmatter, _body = text[4:].split("\n---\n", maxsplit=1)
    except ValueError as exc:
        raise ValueError("missing closing YAML frontmatter delimiter") from exc
    metadata = yaml.load(frontmatter, Loader=UniqueKeySafeLoader)
    if not isinstance(metadata, dict):
        raise TypeError("frontmatter must be a YAML mapping")
    return metadata


def validate_metadata(metadata: dict[str, Any]) -> list[str]:
    """Return contract violations for the deliberately small metadata schema."""
    errors: list[str] = []
    missing = ALLOWED_FIELDS - metadata.keys()
    unexpected = metadata.keys() - ALLOWED_FIELDS
    if missing:
        errors.append(f"missing fields: {', '.join(sorted(missing))}")
    if unexpected:
        errors.append(f"unexpected fields: {', '.join(sorted(unexpected))}")

    if "kind" in metadata and (
        not isinstance(metadata["kind"], str) or metadata["kind"] not in ALLOWED_KINDS
    ):
        errors.append(f"kind must be one of: {', '.join(sorted(ALLOWED_KINDS))}")
    if "status" in metadata and (
        not isinstance(metadata["status"], str)
        or metadata["status"] not in ALLOWED_STATUSES
    ):
        errors.append(f"status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}")
    if "disposition" in metadata and (
        not isinstance(metadata["disposition"], str)
        or metadata["disposition"] not in ALLOWED_DISPOSITIONS
    ):
        errors.append(
            "disposition must be one of: " + ", ".join(sorted(ALLOWED_DISPOSITIONS))
        )
    if "derived_work" in metadata:
        derived_work = metadata["derived_work"]
        if not isinstance(derived_work, list) or any(
            not isinstance(item, str) or not item.strip() for item in derived_work
        ):
            errors.append("derived_work must be a list of non-empty strings")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="Markdown input files")
    args = parser.parse_args(argv)

    failed = False
    for path in args.files:
        try:
            metadata = parse_frontmatter(path.read_text(encoding="utf-8"))
            errors = validate_metadata(metadata)
        except (OSError, UnicodeError, TypeError, ValueError, yaml.YAMLError) as exc:
            errors = [str(exc)]
        if errors:
            failed = True
            for error in errors:
                print(f"ERROR {path}: {error}")
        else:
            print(f"OK {path}")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
