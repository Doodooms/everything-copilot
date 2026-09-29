from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

import yaml

from .errors import PackValidationError
from .ontology import (
    CAPABILITY_ID_PATTERN,
    COMPONENT_ID_PATTERN,
    PACK_ID_PATTERN,
    RELATIVE_PATH_PATTERN,
    SHA256_PATTERN,
    SUPPORTED_TARGETS,
    VERSION_PATTERN,
    parse_agent_plugins_requirement,
)

MAX_DIAGNOSTICS = 50
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
PACK_SCHEMA_PATH = Path(__file__).resolve().parent / "schemas" / "pack.schema.json"


@dataclass(frozen=True)
class PackValidationReport:
    diagnostics: tuple[str, ...]
    source_files: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.diagnostics


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


class DuplicateJSONKeyError(ValueError):
    def __init__(self, key: str):
        self.key = key
        super().__init__(f"duplicate JSON key {key!r}")


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "mapping keys must be hashable",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _construct_unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for key, value in pairs:
        if key in mapping:
            raise DuplicateJSONKeyError(key)
        mapping[key] = value
    return mapping


def load_json_no_duplicate_keys(content: bytes | str) -> Any:
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    if not isinstance(content, str):
        raise TypeError("JSON source must be UTF-8 bytes or text")
    return json.loads(content, object_pairs_hook=_construct_unique_json_object)


def load_pack_yaml_bytes(content: bytes, *, source_name: str = "pack.yaml") -> Any:
    try:
        text = content.decode("utf-8")
        return yaml.load(text, Loader=_UniqueKeyLoader)
    except (UnicodeError, yaml.YAMLError) as exc:
        raise PackValidationError(
            (f"{source_name}: cannot parse source manifest: {exc}",)
        ) from exc


def load_pack_yaml(path: Path) -> Any:
    try:
        content = path.read_bytes()
    except OSError as exc:
        raise PackValidationError(
            (f"pack.yaml: cannot parse source manifest: {exc}",)
        ) from exc
    return load_pack_yaml_bytes(content)


def load_pack_schema() -> Mapping[str, Any]:
    try:
        schema = json.loads(PACK_SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PackValidationError(
            (f"pack schema is unavailable or malformed: {PACK_SCHEMA_PATH}",)
        ) from exc
    if not isinstance(schema, dict) or not isinstance(schema.get("properties"), dict):
        raise PackValidationError(
            (f"pack schema has an invalid root: {PACK_SCHEMA_PATH}",)
        )
    if not isinstance(schema.get("required"), list):
        raise PackValidationError(
            (f"pack schema has no required-field list: {PACK_SCHEMA_PATH}",)
        )
    return schema


def _diagnostic(errors: list[str], location: str, message: str) -> None:
    if len(errors) < MAX_DIAGNOSTICS:
        errors.append(f"{location}: {message}")


def _mapping(
    value: Any,
    location: str,
    errors: list[str],
    *,
    required: set[str] | None = None,
    allowed: set[str] | None = None,
) -> Mapping[str, Any]:
    if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
        _diagnostic(errors, location, "must be an object with string keys")
        return {}
    if required:
        for key in sorted(required - set(value)):
            _diagnostic(errors, location, f"missing required field {key!r}")
    if allowed:
        for key in sorted(set(value) - allowed):
            _diagnostic(errors, location, f"unknown field {key!r}")
    return value


def _string(value: Any, location: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value.strip():
        _diagnostic(errors, location, "must be a non-empty string")
        return None
    return value


def _unique_list(
    value: Any,
    location: str,
    errors: list[str],
    *,
    minimum: int = 0,
) -> tuple[str, ...]:
    if not isinstance(value, list):
        _diagnostic(errors, location, "must be an array of strings")
        return ()
    items: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        item_path = f"{location}[{index}]"
        normalized = _string(item, item_path, errors)
        if normalized is None:
            continue
        if normalized in seen:
            _diagnostic(errors, item_path, f"duplicate value {normalized!r}")
        else:
            seen.add(normalized)
            items.append(normalized)
    if len(items) < minimum:
        _diagnostic(errors, location, f"must contain at least {minimum} item(s)")
    return tuple(sorted(items))


def _id(
    value: Any,
    location: str,
    errors: list[str],
    pattern: re.Pattern[str],
) -> str | None:
    normalized = _string(value, location, errors)
    if normalized is not None and pattern.fullmatch(normalized) is None:
        _diagnostic(errors, location, f"invalid identifier {normalized!r}")
        return None
    return normalized


def _pack_id(value: Any, location: str, errors: list[str]) -> str | None:
    normalized = _id(value, location, errors, PACK_ID_PATTERN)
    if normalized is not None and len(normalized) > 64:
        _diagnostic(errors, location, "must be at most 64 characters")
        return None
    return normalized


def _safe_relative_path(
    root: Path,
    raw_path: Any,
    location: str,
    errors: list[str],
    *,
    expected: str,
    source_files: set[str],
) -> Path | None:
    normalized = _string(raw_path, location, errors)
    if normalized is None:
        return None
    if "\\" in normalized or RELATIVE_PATH_PATTERN.fullmatch(normalized) is None:
        _diagnostic(errors, location, "must be a safe pack-root-relative path")
        return None

    relative = PurePosixPath(normalized)
    if relative.is_absolute() or any(
        part in {"", ".", ".."} for part in normalized.split("/")
    ):
        _diagnostic(errors, location, "must not escape the pack root")
        return None

    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            _diagnostic(errors, location, "path contains a symlink")
            return None
    try:
        resolved = current.resolve(strict=False)
        resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError):
        _diagnostic(errors, location, "path escapes the pack root")
        return None

    if expected == "file" and not resolved.is_file():
        _diagnostic(errors, location, f"missing regular file {normalized!r}")
        return None
    if expected == "directory" and not resolved.is_dir():
        _diagnostic(errors, location, f"missing directory {normalized!r}")
        return None
    if expected == "file":
        source_files.add(normalized)
    return resolved


def _is_bounded_plugin_cwd(value: Any) -> bool:
    if not isinstance(value, str) or "\\" in value:
        return False
    supported_root = (
        value.startswith("./")
        or value == "${PLUGIN_ROOT}"
        or value.startswith("${PLUGIN_ROOT}/")
        or value == "${PLUGIN_DATA}"
        or value.startswith("${PLUGIN_DATA}/")
    )
    if not supported_root:
        return False
    for index, component in enumerate(value.split("/")):
        if index == 0 and component == "." and value.startswith("./"):
            continue
        normalized = component.rstrip(" .")
        if component and not normalized:
            return False
        if normalized in {".", ".."}:
            return False
    return True


def _directory_files(
    root: Path,
    directory: Path,
    source_prefix: str,
    location: str,
    errors: list[str],
    source_files: set[str],
) -> None:
    for entry in sorted(directory.rglob("*"), key=lambda item: item.as_posix()):
        if entry.is_symlink():
            _diagnostic(errors, location, f"package contains symlink {entry.name!r}")
            continue
        try:
            entry.resolve(strict=False).relative_to(root)
        except (OSError, RuntimeError, ValueError):
            _diagnostic(
                errors, location, f"package path escapes the pack root: {entry}"
            )
            continue
        if entry.is_file():
            if "__pycache__" in entry.parts or entry.suffix in {".pyc", ".pyo"}:
                _diagnostic(
                    errors,
                    location,
                    f"generated cache file is not pack source: {entry.name}",
                )
                continue
            relative = f"{source_prefix}/{entry.relative_to(directory).as_posix()}"
            source_files.add(relative)
        elif not entry.is_dir():
            _diagnostic(
                errors, location, f"unsupported non-file package entry: {entry.name}"
            )


def _load_skill_metadata(
    skill_file: Path | None,
    location: str,
    skill_id: str,
    errors: list[str],
    *,
    content: bytes | None = None,
) -> None:
    if content is None:
        if skill_file is None:
            _diagnostic(errors, location, "SKILL.md is absent from the source snapshot")
            return
        try:
            content = skill_file.read_bytes()
        except OSError:
            _diagnostic(errors, location, "SKILL.md could not be read")
            return
    try:
        text = content.decode("utf-8")
    except UnicodeError:
        _diagnostic(errors, location, "SKILL.md must be valid UTF-8")
        return
    match = re.match(r"\A---\n(.*?)\n---\n?", text, re.DOTALL)
    if match is None:
        _diagnostic(errors, location, "SKILL.md must begin with YAML frontmatter")
        return
    try:
        metadata = yaml.load(match.group(1), Loader=_UniqueKeyLoader)
    except yaml.YAMLError as exc:
        _diagnostic(errors, location, f"invalid SKILL.md frontmatter: {exc}")
        return
    if not isinstance(metadata, dict):
        _diagnostic(errors, location, "SKILL.md frontmatter must be a mapping")
        return
    if metadata.get("name") != skill_id:
        _diagnostic(errors, location, f"frontmatter name must match {skill_id!r}")
    if (
        not isinstance(metadata.get("description"), str)
        or not metadata["description"].strip()
    ):
        _diagnostic(
            errors, location, "frontmatter description must be a non-empty string"
        )


def _validate_mcp_config(data: Any, location: str, errors: list[str]) -> set[str]:
    allowed_root = {"$schema", "mcpServers"}
    config = _mapping(
        data, location, errors, required=allowed_root, allowed=allowed_root
    )
    if (
        config.get("$schema")
        != "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
    ):
        _diagnostic(
            errors, f"{location}.$schema", "must use the Agent Plugins 1.0 MCP schema"
        )
    servers = config.get("mcpServers")
    if not isinstance(servers, dict):
        _diagnostic(errors, f"{location}.mcpServers", "must be an object")
        return set()

    for server_id, server in sorted(servers.items(), key=lambda item: str(item[0])):
        server_path = f"{location}.mcpServers.{server_id}"
        if not isinstance(server_id, str) or not server_id:
            _diagnostic(
                errors, f"{location}.mcpServers", "server IDs must be non-empty strings"
            )
            continue
        if not isinstance(server, dict):
            _diagnostic(errors, server_path, "must be an object")
            continue
        server_type = server.get("type")
        if server_type == "stdio":
            allowed = {"type", "command", "args", "env", "cwd"}
            required = {"type", "command"}
            server = _mapping(
                server, server_path, errors, required=required, allowed=allowed
            )
            if (
                not isinstance(server.get("command"), str)
                or not server.get("command", "").strip()
            ):
                _diagnostic(
                    errors, f"{server_path}.command", "must be a non-empty string"
                )
            if "args" in server and (
                not isinstance(server["args"], list)
                or any(not isinstance(item, str) for item in server["args"])
            ):
                _diagnostic(
                    errors, f"{server_path}.args", "must be an array of strings"
                )
            if "env" in server:
                env = server["env"]
                if not isinstance(env, dict) or any(
                    not isinstance(key, str) or not isinstance(value, str)
                    for key, value in env.items()
                ):
                    _diagnostic(
                        errors, f"{server_path}.env", "must map strings to strings"
                    )
                elif {"PLUGIN_ROOT", "PLUGIN_DATA"} & set(env):
                    _diagnostic(
                        errors,
                        f"{server_path}.env",
                        "must not override reserved plugin variables",
                    )
            if "cwd" in server:
                if not _is_bounded_plugin_cwd(server["cwd"]):
                    _diagnostic(
                        errors,
                        f"{server_path}.cwd",
                        "must be a bounded plugin-relative or supported-root path",
                    )
        elif server_type in {"streamable-http", "sse"}:
            allowed = {"type", "url", "headers"}
            server = _mapping(
                server,
                server_path,
                errors,
                required={"type", "url"},
                allowed=allowed,
            )
            if (
                not isinstance(server.get("url"), str)
                or not server.get("url", "").strip()
            ):
                _diagnostic(errors, f"{server_path}.url", "must be a non-empty string")
            if "headers" in server:
                headers = server["headers"]
                if not isinstance(headers, dict) or any(
                    not isinstance(key, str) or not isinstance(value, str)
                    for key, value in headers.items()
                ):
                    _diagnostic(
                        errors, f"{server_path}.headers", "must map strings to strings"
                    )
        else:
            _diagnostic(
                errors,
                f"{server_path}.type",
                "must be stdio, streamable-http, or sse",
            )
    return set(servers)


def validate_pack_document(
    document: Any,
    root: Path,
    *,
    known_agents: set[str] | frozenset[str] = frozenset(),
    source_snapshot: Mapping[str, bytes] | None = None,
    discover_only: bool = False,
    manifest_path: str = "pack.yaml",
    initial_source_files: tuple[str, ...] = (),
) -> PackValidationReport:
    errors: list[str] = []
    source_files: set[str] = set(initial_source_files)
    source_files.add(manifest_path)
    root = root.resolve(strict=True)
    schema = load_pack_schema()
    allowed_fields = set(schema["properties"])
    required_fields = set(schema["required"])
    top = _mapping(
        document,
        manifest_path,
        errors,
        required=required_fields,
        allowed=allowed_fields,
    )
    if not top:
        return PackValidationReport(tuple(errors), tuple(sorted(source_files)))

    if type(top.get("schema_version")) is not int or top.get("schema_version") != 1:
        _diagnostic(errors, "schema_version", "must be integer 1")
    _pack_id(top.get("id"), "id", errors)
    pack_type = top.get("type")
    if not isinstance(pack_type, str) or pack_type not in {"vertical", "horizontal"}:
        _diagnostic(errors, "type", "must be horizontal or vertical")
    _string(top.get("name"), "name", errors)
    _string(top.get("description"), "description", errors)
    version = _string(top.get("version"), "version", errors)
    if version and VERSION_PATTERN.fullmatch(version) is None:
        _diagnostic(errors, "version", "must be a semantic version")

    compatibility = _mapping(
        top.get("compatibility"),
        "compatibility",
        errors,
        required={"targets", "agent_plugins"},
        allowed={"targets", "agent_plugins"},
    )
    targets = _unique_list(
        compatibility.get("targets"), "compatibility.targets", errors, minimum=1
    )
    for target in targets:
        if target not in SUPPORTED_TARGETS:
            _diagnostic(
                errors, "compatibility.targets", f"unsupported target {target!r}"
            )
    plugin_requirement = _string(
        compatibility.get("agent_plugins"),
        "compatibility.agent_plugins",
        errors,
    )
    if plugin_requirement:
        try:
            parse_agent_plugins_requirement(plugin_requirement)
        except ValueError:
            _diagnostic(
                errors,
                "compatibility.agent_plugins",
                "must be a lower-bound constraint such as '>=1.0' or '>=1.0.0'",
            )

    trust = _mapping(
        top.get("trust"),
        "trust",
        errors,
        required={"publisher", "source", "approval_required"},
        allowed={"publisher", "source", "approval_required", "digest"},
    )
    _string(trust.get("publisher"), "trust.publisher", errors)
    _string(trust.get("source"), "trust.source", errors)
    if trust.get("approval_required") is not True:
        _diagnostic(errors, "trust.approval_required", "must be true")
    digest = trust.get("digest")
    if digest is not None and (
        not isinstance(digest, str) or SHA256_PATTERN.fullmatch(digest) is None
    ):
        _diagnostic(errors, "trust.digest", "must be a lowercase sha256 digest")

    capabilities_raw = top.get("capabilities")
    if not isinstance(capabilities_raw, list) or not capabilities_raw:
        _diagnostic(errors, "capabilities", "must be a non-empty array")
        capabilities_raw = []
    capability_ids: set[str] = set()
    for index, item in enumerate(capabilities_raw):
        location = f"capabilities[{index}]"
        capability = _mapping(
            item,
            location,
            errors,
            required={"id", "description"},
            allowed={"id", "description"},
        )
        capability_id = _id(
            capability.get("id"),
            f"{location}.id",
            errors,
            CAPABILITY_ID_PATTERN,
        )
        _string(capability.get("description"), f"{location}.description", errors)
        if capability_id:
            if capability_id in capability_ids:
                _diagnostic(
                    errors, f"{location}.id", f"duplicate capability {capability_id!r}"
                )
            capability_ids.add(capability_id)

    dependencies_raw = top.get("dependencies")
    dependencies: list[tuple[str, str | None, str | None]] = []
    if not isinstance(dependencies_raw, list):
        _diagnostic(errors, "dependencies", "must be an array")
        dependencies_raw = []
    for index, item in enumerate(dependencies_raw):
        location = f"dependencies[{index}]"
        dependency = _mapping(
            item,
            location,
            errors,
            required={"capability"},
            allowed={"capability", "pack_id", "minimum_version"},
        )
        capability = _id(
            dependency.get("capability"),
            f"{location}.capability",
            errors,
            CAPABILITY_ID_PATTERN,
        )
        provider_pack = dependency.get("pack_id")
        if provider_pack is not None:
            provider_pack = _pack_id(provider_pack, f"{location}.pack_id", errors)
        minimum_version = dependency.get("minimum_version")
        if minimum_version is not None:
            minimum_version = _string(
                minimum_version, f"{location}.minimum_version", errors
            )
            if minimum_version and VERSION_PATTERN.fullmatch(minimum_version) is None:
                _diagnostic(
                    errors, f"{location}.minimum_version", "must be a semantic version"
                )
        if capability:
            dependency_key = (capability, provider_pack, minimum_version)
            if dependency_key in dependencies:
                _diagnostic(errors, location, f"duplicate dependency {capability!r}")
            dependencies.append(dependency_key)

    agents = _mapping(
        top.get("agents"),
        "agents",
        errors,
        required={"contributions", "extensions"},
        allowed={"contributions", "extensions"},
    )
    catalog = set(known_agents)
    contributions_raw = agents.get("contributions")
    extensions_raw = agents.get("extensions")
    if not isinstance(contributions_raw, list):
        _diagnostic(errors, "agents.contributions", "must be an array")
        contributions_raw = []
    if not isinstance(extensions_raw, list):
        _diagnostic(errors, "agents.extensions", "must be an array")
        extensions_raw = []
    contribution_ids: set[str] = set()
    extension_ids: set[str] = set()
    provider_capabilities: set[str] = set()
    for index, item in enumerate(contributions_raw):
        location = f"agents.contributions[{index}]"
        contribution = _mapping(
            item,
            location,
            errors,
            required={"id", "source", "capabilities"},
            allowed={"id", "source", "capabilities"},
        )
        agent_id = _id(
            contribution.get("id"), f"{location}.id", errors, COMPONENT_ID_PATTERN
        )
        if agent_id:
            if agent_id in contribution_ids:
                _diagnostic(
                    errors,
                    f"{location}.id",
                    f"duplicate agent contribution {agent_id!r}",
                )
            if agent_id in catalog:
                _diagnostic(
                    errors,
                    f"{location}.id",
                    f"contribution duplicates known agent {agent_id!r}",
                )
            contribution_ids.add(agent_id)
        source = _safe_relative_path(
            root,
            contribution.get("source"),
            f"{location}.source",
            errors,
            expected="file",
            source_files=source_files,
        )
        if source is not None and agent_id is not None:
            if source.name != f"{agent_id}.agent.md":
                _diagnostic(
                    errors, f"{location}.source", "filename must match the agent ID"
                )
        provider_capabilities.update(
            _validate_reference_list(
                contribution.get("capabilities"),
                f"{location}.capabilities",
                capability_ids,
                errors,
                minimum=1,
            )
        )

    for index, item in enumerate(extensions_raw):
        location = f"agents.extensions[{index}]"
        extension = _mapping(
            item,
            location,
            errors,
            required={"agent_id", "capabilities"},
            allowed={"agent_id", "capabilities"},
        )
        agent_id = _id(
            extension.get("agent_id"),
            f"{location}.agent_id",
            errors,
            COMPONENT_ID_PATTERN,
        )
        if agent_id:
            if agent_id not in catalog and agent_id not in contribution_ids:
                _diagnostic(
                    errors, f"{location}.agent_id", f"unknown agent {agent_id!r}"
                )
            if agent_id in extension_ids:
                _diagnostic(
                    errors,
                    f"{location}.agent_id",
                    f"duplicate agent extension {agent_id!r}",
                )
            extension_ids.add(agent_id)
        provider_capabilities.update(
            _validate_reference_list(
                extension.get("capabilities"),
                f"{location}.capabilities",
                capability_ids,
                errors,
                minimum=1,
            )
        )

    skills_raw = top.get("skills")
    if not isinstance(skills_raw, list):
        _diagnostic(errors, "skills", "must be an array")
        skills_raw = []
    skill_ids: set[str] = set()
    skill_capabilities: dict[str, tuple[str, ...]] = {}
    for index, item in enumerate(skills_raw):
        location = f"skills[{index}]"
        skill = _mapping(
            item,
            location,
            errors,
            required={"id", "path", "capabilities"},
            allowed={"id", "path", "capabilities"},
        )
        skill_id = _id(skill.get("id"), f"{location}.id", errors, COMPONENT_ID_PATTERN)
        if skill_id:
            if skill_id in skill_ids:
                _diagnostic(errors, f"{location}.id", f"duplicate skill {skill_id!r}")
            skill_ids.add(skill_id)
        skill_dir = _safe_relative_path(
            root,
            skill.get("path"),
            f"{location}.path",
            errors,
            expected="directory",
            source_files=source_files,
        )
        component_capabilities = _validate_reference_list(
            skill.get("capabilities"),
            f"{location}.capabilities",
            capability_ids,
            errors,
        )
        if skill_id is not None:
            skill_capabilities[skill_id] = component_capabilities
        provider_capabilities.update(component_capabilities)
        if skill_dir is not None and skill_id is not None:
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.is_file() or skill_file.is_symlink():
                _diagnostic(
                    errors,
                    f"{location}.path",
                    "package must contain a regular SKILL.md",
                )
            else:
                skill_source = f"{skill.get('path')}/SKILL.md"
                source_files.add(skill_source)
                if not discover_only:
                    if source_snapshot is None:
                        _load_skill_metadata(
                            skill_file,
                            f"{location}.path/SKILL.md",
                            skill_id,
                            errors,
                        )
                    else:
                        skill_content = source_snapshot.get(skill_source)
                        if skill_content is None:
                            _diagnostic(
                                errors,
                                f"{location}.path/SKILL.md",
                                "is absent from the captured source snapshot",
                            )
                        else:
                            _load_skill_metadata(
                                None,
                                f"{location}.path/SKILL.md",
                                skill_id,
                                errors,
                                content=skill_content,
                            )
                _directory_files(
                    root,
                    skill_dir,
                    str(skill.get("path")),
                    location,
                    errors,
                    source_files,
                )

    mcp_config_raw = top.get("mcp_config")
    mcp_servers_raw = top.get("mcp_servers")
    if not isinstance(mcp_servers_raw, list):
        _diagnostic(errors, "mcp_servers", "must be an array")
        mcp_servers_raw = []
    mcp_server_ids: set[str] = set()
    mcp_capabilities: dict[str, tuple[str, ...]] = {}
    for index, item in enumerate(mcp_servers_raw):
        location = f"mcp_servers[{index}]"
        server = _mapping(
            item,
            location,
            errors,
            required={"id", "capabilities", "permissions"},
            allowed={"id", "capabilities", "permissions", "tools"},
        )
        server_id = _id(
            server.get("id"), f"{location}.id", errors, COMPONENT_ID_PATTERN
        )
        if server_id:
            if server_id in mcp_server_ids:
                _diagnostic(
                    errors, f"{location}.id", f"duplicate MCP server {server_id!r}"
                )
            mcp_server_ids.add(server_id)
        component_capabilities = _validate_reference_list(
            server.get("capabilities"),
            f"{location}.capabilities",
            capability_ids,
            errors,
            minimum=1,
        )
        if server_id is not None:
            mcp_capabilities[server_id] = component_capabilities
        provider_capabilities.update(component_capabilities)
        _unique_list(server.get("permissions"), f"{location}.permissions", errors)
        tool_names = _unique_list(server.get("tools", []), f"{location}.tools", errors)
        for tool_name in tool_names:
            if "/" in tool_name or any(character.isspace() for character in tool_name):
                _diagnostic(
                    errors,
                    f"{location}.tools",
                    "tool names must be exact MCP names without `/` or whitespace",
                )

    mcp_config_path: Path | None = None
    if mcp_servers_raw and mcp_config_raw is None:
        _diagnostic(errors, "mcp_config", "is required when MCP servers are declared")
    elif not mcp_servers_raw and mcp_config_raw is not None:
        _diagnostic(
            errors, "mcp_config", "must be null when no MCP servers are declared"
        )
    elif mcp_config_raw is not None:
        mcp_config_path = _safe_relative_path(
            root,
            mcp_config_raw,
            "mcp_config",
            errors,
            expected="file",
            source_files=source_files,
        )
        if mcp_config_path is not None and not discover_only:
            try:
                if source_snapshot is None:
                    mcp_content = mcp_config_path.read_bytes()
                else:
                    mcp_content = source_snapshot.get(mcp_config_raw)
                    if mcp_content is None:
                        _diagnostic(
                            errors,
                            "mcp_config",
                            "is absent from the captured source snapshot",
                        )
                if mcp_content is None:
                    mcp_data = None
                else:
                    mcp_data = load_json_no_duplicate_keys(mcp_content)
            except DuplicateJSONKeyError as exc:
                _diagnostic(
                    errors,
                    "mcp_config",
                    f"duplicate JSON key {exc.key!r}",
                )
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                _diagnostic(
                    errors, "mcp_config", f"cannot parse MCP configuration: {exc}"
                )
            else:
                if mcp_data is not None:
                    mcp_ids = validate_mcp_config(mcp_data, "mcp_config", errors)
                    if mcp_ids != mcp_server_ids:
                        _diagnostic(
                            errors,
                            "mcp_servers",
                            "declared server IDs must exactly match the source mcp.json entries",
                        )

    projections_raw = top.get("projections")
    if not isinstance(projections_raw, list):
        _diagnostic(errors, "projections", "must be an array")
        projections_raw = []
    projection_ids: set[str] = set()
    known_agent_ids = catalog | contribution_ids
    for index, item in enumerate(projections_raw):
        location = f"projections[{index}]"
        projection = _mapping(
            item,
            location,
            errors,
            required={"agent_id", "capabilities", "skills", "mcp_servers"},
            allowed={"agent_id", "capabilities", "skills", "mcp_servers"},
        )
        agent_id = _id(
            projection.get("agent_id"),
            f"{location}.agent_id",
            errors,
            COMPONENT_ID_PATTERN,
        )
        if agent_id:
            if agent_id not in known_agent_ids:
                _diagnostic(
                    errors, f"{location}.agent_id", f"unknown agent {agent_id!r}"
                )
            if agent_id in projection_ids:
                _diagnostic(
                    errors, f"{location}.agent_id", f"duplicate projection {agent_id!r}"
                )
            projection_ids.add(agent_id)
        granted_capabilities = set(
            _validate_reference_list(
                projection.get("capabilities"),
                f"{location}.capabilities",
                capability_ids,
                errors,
            )
        )
        granted_skills = set(
            _validate_identifier_list(
                projection.get("skills"), f"{location}.skills", errors
            )
        )
        granted_servers = set(
            _validate_identifier_list(
                projection.get("mcp_servers"), f"{location}.mcp_servers", errors
            )
        )
        for skill_id in granted_skills:
            if skill_id not in skill_ids:
                _diagnostic(errors, f"{location}.skills", f"unknown skill {skill_id!r}")
            elif not set(skill_capabilities.get(skill_id, ())) <= granted_capabilities:
                _diagnostic(
                    errors,
                    f"{location}.skills",
                    f"skill {skill_id!r} exposes capabilities outside this projection",
                )
        for server_id in granted_servers:
            if server_id not in mcp_server_ids:
                _diagnostic(
                    errors, f"{location}.mcp_servers", f"unknown server {server_id!r}"
                )
            elif not set(mcp_capabilities.get(server_id, ())) <= granted_capabilities:
                _diagnostic(
                    errors,
                    f"{location}.mcp_servers",
                    f"server {server_id!r} exposes capabilities outside this projection",
                )

    for capability_id in sorted(capability_ids - provider_capabilities):
        _diagnostic(
            errors,
            "capabilities",
            f"capability {capability_id!r} has no declared provider",
        )

    return PackValidationReport(
        diagnostics=tuple(sorted(set(errors))[:MAX_DIAGNOSTICS]),
        source_files=tuple(sorted(source_files)),
    )


def _validate_identifier_list(
    value: Any,
    location: str,
    errors: list[str],
    *,
    pattern: re.Pattern[str] = COMPONENT_ID_PATTERN,
) -> tuple[str, ...]:
    if not isinstance(value, list):
        _diagnostic(errors, location, "must be an array of identifiers")
        return ()
    identifiers: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        identifier = _id(item, f"{location}[{index}]", errors, pattern)
        if identifier is not None:
            if identifier in seen:
                _diagnostic(
                    errors,
                    f"{location}[{index}]",
                    f"duplicate identifier {identifier!r}",
                )
            seen.add(identifier)
            identifiers.append(identifier)
    return tuple(sorted(identifiers))


def _validate_reference_list(
    value: Any,
    location: str,
    known_ids: set[str],
    errors: list[str],
    *,
    minimum: int = 0,
) -> tuple[str, ...]:
    references = _validate_identifier_list(
        value, location, errors, pattern=CAPABILITY_ID_PATTERN
    )
    if len(references) < minimum:
        _diagnostic(errors, location, f"must contain at least {minimum} reference(s)")
    for reference in references:
        if reference not in known_ids:
            _diagnostic(errors, location, f"unknown capability {reference!r}")
    return references


def validate_mcp_config(data: Any, location: str, errors: list[str]) -> set[str]:
    allowed_root = {"$schema", "mcpServers"}
    if not isinstance(data, dict):
        _diagnostic(errors, location, "must be an object")
        return set()
    for key in sorted(set(data) - allowed_root):
        _diagnostic(errors, location, f"unknown MCP configuration field {key!r}")
    if data.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json":
        _diagnostic(
            errors, f"{location}.$schema", "must use the Agent Plugins 1.0 MCP schema"
        )
    servers = data.get("mcpServers")
    if not isinstance(servers, dict):
        _diagnostic(errors, f"{location}.mcpServers", "must be an object")
        return set()
    server_ids: set[str] = set()
    for server_id, server in sorted(servers.items()):
        if not isinstance(server_id, str) or not server_id:
            _diagnostic(
                errors, f"{location}.mcpServers", "server IDs must be non-empty strings"
            )
            continue
        server_ids.add(server_id)
        server_path = f"{location}.mcpServers.{server_id}"
        if not isinstance(server, dict):
            _diagnostic(errors, server_path, "must be an object")
            continue
        server_type = server.get("type")
        if server_type == "stdio":
            allowed = {"type", "command", "args", "env", "cwd"}
            required = {"type", "command"}
            if set(server) - allowed:
                _diagnostic(
                    errors, server_path, "contains unsupported stdio server fields"
                )
            if not required <= set(server):
                _diagnostic(
                    errors, server_path, "stdio server requires type and command"
                )
            if (
                not isinstance(server.get("command"), str)
                or not server.get("command", "").strip()
            ):
                _diagnostic(
                    errors, f"{server_path}.command", "must be a non-empty string"
                )
            if "args" in server and (
                not isinstance(server["args"], list)
                or any(not isinstance(item, str) for item in server["args"])
            ):
                _diagnostic(
                    errors, f"{server_path}.args", "must be an array of strings"
                )
            if "env" in server:
                env = server["env"]
                if not isinstance(env, dict) or any(
                    not isinstance(key, str) or not isinstance(value, str)
                    for key, value in env.items()
                ):
                    _diagnostic(
                        errors, f"{server_path}.env", "must map strings to strings"
                    )
                elif {"PLUGIN_ROOT", "PLUGIN_DATA"} & set(env):
                    _diagnostic(
                        errors,
                        f"{server_path}.env",
                        "must not override reserved plugin variables",
                    )
            if "cwd" in server:
                if not _is_bounded_plugin_cwd(server["cwd"]):
                    _diagnostic(
                        errors,
                        f"{server_path}.cwd",
                        "must be a bounded plugin-relative or supported-root path",
                    )
        elif server_type in {"streamable-http", "sse"}:
            allowed = {"type", "url", "headers"}
            if set(server) - allowed:
                _diagnostic(
                    errors, server_path, "contains unsupported HTTP server fields"
                )
            if (
                not isinstance(server.get("url"), str)
                or not server.get("url", "").strip()
            ):
                _diagnostic(errors, f"{server_path}.url", "must be a non-empty string")
            if "headers" in server:
                headers = server["headers"]
                if not isinstance(headers, dict) or any(
                    not isinstance(key, str) or not isinstance(value, str)
                    for key, value in headers.items()
                ):
                    _diagnostic(
                        errors, f"{server_path}.headers", "must map strings to strings"
                    )
        else:
            _diagnostic(
                errors,
                f"{server_path}.type",
                "must be stdio, streamable-http, or sse",
            )
    return server_ids
