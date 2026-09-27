from __future__ import annotations

import re
from typing import Any

from ..errors import TargetError
from ..ontology import AGENT_PLUGIN_SCHEMA
from ..validator import validate_mcp_config


_PLUGIN_NAME = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
_AUTHOR_FIELDS = {"name", "email", "url"}
_PLUGIN_FIELDS = {
    "$schema",
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "extensions",
}


def validate_plugin_manifest(manifest: Any) -> None:
    """Validate the fields and constraints emitted by this target against Plugin 1.0."""
    errors: list[str] = []
    if not isinstance(manifest, dict):
        raise TargetError("plugin.json must contain a JSON object")

    unknown = sorted(set(manifest) - _PLUGIN_FIELDS)
    if unknown:
        errors.append(f"unsupported plugin.json fields: {', '.join(unknown)}")
    for required in ("$schema", "name"):
        if required not in manifest:
            errors.append(f"plugin.json is missing required field {required!r}")

    if manifest.get("$schema") != AGENT_PLUGIN_SCHEMA:
        errors.append(f"plugin.json $schema must equal {AGENT_PLUGIN_SCHEMA!r}")
    name = manifest.get("name")
    if (
        not isinstance(name, str)
        or not 1 <= len(name) <= 64
        or _PLUGIN_NAME.fullmatch(name) is None
    ):
        errors.append("plugin.json name must satisfy the Agent Plugins 1.0 name constraint")

    for field in ("version", "description", "homepage", "repository", "license"):
        if field in manifest and not isinstance(manifest[field], str):
            errors.append(f"plugin.json {field} must be a string")

    if "author" in manifest:
        author = manifest["author"]
        if not isinstance(author, dict):
            errors.append("plugin.json author must be an object")
        else:
            unknown_author = sorted(set(author) - _AUTHOR_FIELDS)
            if unknown_author:
                errors.append(
                    "plugin.json author contains unsupported fields: "
                    + ", ".join(unknown_author)
                )
            if any(not isinstance(value, str) for value in author.values()):
                errors.append("plugin.json author values must be strings")

    keywords = manifest.get("keywords")
    if keywords is not None and (
        not isinstance(keywords, list)
        or any(not isinstance(keyword, str) for keyword in keywords)
    ):
        errors.append("plugin.json keywords must be an array of strings")

    extensions = manifest.get("extensions")
    if extensions is not None and (
        not isinstance(extensions, dict)
        or any(not isinstance(value, dict) for value in extensions.values())
    ):
        errors.append("plugin.json extensions must map namespaces to objects")

    if errors:
        raise TargetError("; ".join(sorted(errors)))


def validate_mcp_manifest(manifest: Any) -> None:
    errors: list[str] = []
    validate_mcp_config(manifest, "mcp.json", errors)
    if errors:
        raise TargetError("; ".join(sorted(set(errors))))
