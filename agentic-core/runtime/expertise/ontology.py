from __future__ import annotations

import hashlib
import json
import re
from enum import Enum
from typing import Any


PACK_SCHEMA_VERSION = 1
AGENT_PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
AGENT_PLUGINS_VERSION = "1.0.0"
SUPPORTED_TARGETS = frozenset({"portable", "copilot", "codex"})
PLUGIN_TYPES = frozenset({"horizontal", "vertical"})

PACK_ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
COMPONENT_ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
CAPABILITY_ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$")
AGENT_PLUGINS_REQUIREMENT_PATTERN = re.compile(
    r"^>=(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:\.(0|[1-9][0-9]*))?$(?![\s\S])"
)
VERSION_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-((?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
RELATIVE_PATH_PATTERN = re.compile(
    r"^(?!/)(?!.*\\)(?!.*(?:^|/)\.{1,2}(?:/|$))"
    r"[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*$"
)


class Target(str, Enum):
    PORTABLE = "portable"
    COPILOT = "copilot"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def parse_version(value: str) -> tuple[int, int, int]:
    match = VERSION_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError(f"invalid semantic version: {value!r}")
    return tuple(int(match.group(index)) for index in range(1, 4))


def parse_agent_plugins_requirement(
    value: str,
) -> tuple[str, tuple[int, int, int]]:
    if not isinstance(value, str) or value != value.strip():
        raise ValueError("Agent Plugins minimum-version constraint must not have whitespace")
    match = AGENT_PLUGINS_REQUIREMENT_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError(f"invalid Agent Plugins minimum-version constraint: {value!r}")
    try:
        major, minor = (int(match.group(index)) for index in (1, 2))
        patch = int(match.group(3) or 0)
    except ValueError as exc:
        raise ValueError("Agent Plugins minimum-version component is too large") from exc
    return f">={major}.{minor}.{patch}", (major, minor, patch)
