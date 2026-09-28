from __future__ import annotations

import json
import re
import shutil
import stat
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

import yaml

from ..errors import TargetError

ANTIGRAVITY_PLUGIN_SCHEMA = "https://antigravity.google/schemas/v1/plugin.json"
_ANTIGRAVITY_NAME = re.compile(r"^[a-zA-Z0-9_-]+$")
_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", re.DOTALL)
_SKILL_POLICY = re.compile(
    r"^\s*-\s*(?:MUST|SHOULD|MAY)\s+(?:load|use)\s+`([^`]+)`",
    re.MULTILINE,
)
_PLUGIN_ROOT = "${PLUGIN_ROOT}"

# These identifiers were found in the installed agy 1.2.12 binary and in its
# agent-facing documentation. Unknown target tool IDs are rejected before output.
SUPPORTED_AGENT_TOOLS = frozenset(
    {
        "ask_question",
        "create_file",
        "find_file",
        "grep_search",
        "invoke_subagent",
        "list_directory",
        "run_command",
        "search_directory",
        "view_file",
        "write_to_file",
    }
)

_SOURCE_TOOL_MAP = {
    "read": ("list_directory", "view_file"),
    "search": ("find_file", "grep_search", "search_directory"),
    "search/usages": ("find_file", "grep_search", "search_directory"),
    "edit": ("write_to_file",),
    "execute": ("run_command",),
    "agent": ("invoke_subagent",),
    "vscode/askQuestions": ("ask_question",),
}
_SOURCE_TOOLS_WITHOUT_DIRECT_EQUIVALENT = frozenset({"skill", "todo", "web", "browser"})
_MCP_SOURCE_TOOL_PREFIXES = ("mcp_", "github/")

DOCUMENTED_MAPPING_LOSSES = (
    "Agent Plugins version, author, and keywords are omitted from the stricter Antigravity plugin manifest.",
    "Copilot model IDs and per-agent reasoning-effort are omitted; Antigravity has no exact mapping for them.",
    "Skill user-invocable is omitted because agy 1.2.12 exposes no per-skill equivalent.",
    "Agent user-invocable maps to mainAgent; disable-model-invocation maps to subagent=false, which is approximate.",
    "Copilot edit maps to write_to_file, whose write scope is broader; todo, web, browser, and per-agent MCP tool IDs are omitted.",
)


@dataclass(frozen=True)
class AntigravityProjection:
    files: Mapping[str, bytes]
    executable_files: frozenset[str]
    mapping_losses: tuple[str, ...] = DOCUMENTED_MAPPING_LOSSES

    def __post_init__(self) -> None:
        normalized = _validate_file_map(self.files)
        executable_files = frozenset(self.executable_files)
        if not executable_files <= set(normalized):
            raise TargetError("executable projection paths must name projected files")
        object.__setattr__(self, "files", MappingProxyType(normalized))
        object.__setattr__(self, "executable_files", executable_files)


def _validate_relative_path(path: str) -> None:
    if not isinstance(path, str) or not path or path.startswith("/"):
        raise TargetError(f"projected file path must be relative: {path!r}")
    parts = path.split("/")
    if "\\" in path or ":" in path or any(part in {"", ".", ".."} for part in parts):
        raise TargetError(f"projected file path is unsafe: {path!r}")


def _validate_file_map(files: Mapping[str, bytes]) -> dict[str, bytes]:
    if not isinstance(files, Mapping):
        raise TargetError("projected files must be a mapping")
    normalized: dict[str, bytes] = {}
    for path, content in files.items():
        _validate_relative_path(path)
        if not isinstance(content, bytes):
            raise TargetError(f"projected file content must be bytes: {path}")
        if path in normalized:
            raise TargetError(f"duplicate projected file: {path}")
        normalized[path] = content
    return normalized


def _json_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise TargetError(f"JSON contains duplicate key: {key}")
        result[key] = value
    return result


def _load_json(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_json_object_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TargetError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise TargetError(f"{label} must contain a JSON object")
    return value


def _read_source_file(source_root: Path, path: Path, label: str) -> bytes:
    if path.is_symlink():
        raise TargetError(f"source path must not be a symlink: {label}")
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(source_root)
        if not resolved.is_file():
            raise TargetError(f"source path is not a regular file: {label}")
        return resolved.read_bytes()
    except (OSError, TypeError, ValueError) as exc:
        raise TargetError(
            f"source file is missing or outside its root: {label}"
        ) from exc


def _frontmatter(text: str, label: str) -> tuple[dict[str, Any], str]:
    match = _FRONTMATTER.match(text.replace("\r\n", "\n"))
    if match is None:
        raise TargetError(f"source file is missing YAML frontmatter: {label}")
    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise TargetError(f"source frontmatter is invalid: {label}") from exc
    if not isinstance(metadata, dict):
        raise TargetError(f"source frontmatter must be a mapping: {label}")
    return metadata, match.group(2)


def _render_frontmatter(metadata: Mapping[str, Any], body: str) -> bytes:
    frontmatter = yaml.safe_dump(
        dict(metadata),
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).rstrip()
    return f"---\n{frontmatter}\n---\n{body}".encode()


def render_plugin_manifest(source_manifest: Mapping[str, Any]) -> bytes:
    name = source_manifest.get("name")
    description = source_manifest.get("description")
    if not isinstance(name, str) or _ANTIGRAVITY_NAME.fullmatch(name) is None:
        raise TargetError("source plugin name is not valid for Antigravity")
    if not isinstance(description, str) or not description.strip():
        raise TargetError("source plugin description must be non-empty")
    target_manifest = {
        "$schema": ANTIGRAVITY_PLUGIN_SCHEMA,
        "name": name,
        "description": description,
    }
    return (json.dumps(target_manifest, ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )


def _skill_frontmatter(source_file: Path, skill_id: str) -> bytes:
    try:
        text = source_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise TargetError(
            f"skill entrypoint is not readable UTF-8: {source_file}"
        ) from exc
    metadata, body = _frontmatter(text, source_file.as_posix())
    name = metadata.get("name", skill_id)
    description = metadata.get("description")
    if name != skill_id:
        raise TargetError(f"skill name must match its source directory: {skill_id}")
    if not isinstance(description, str) or not description.strip():
        raise TargetError(f"skill description must be non-empty: {skill_id}")
    return _render_frontmatter({"name": name, "description": description}, body)


def copy_skill_tree(source_skill_root: Path) -> tuple[dict[str, bytes], frozenset[str]]:
    """Copy one canonical skill bundle, translating only its root SKILL.md header."""
    source_skill_root = Path(source_skill_root)
    if source_skill_root.is_symlink() or not source_skill_root.is_dir():
        raise TargetError(f"skill source must be a real directory: {source_skill_root}")
    skill_id = source_skill_root.name
    copied: dict[str, bytes] = {}
    executable: set[str] = set()
    try:
        paths = sorted(source_skill_root.rglob("*"))
    except OSError as exc:
        raise TargetError(
            f"could not enumerate skill files: {source_skill_root}"
        ) from exc
    for path in paths:
        relative = path.relative_to(source_skill_root).as_posix()
        _validate_relative_path(relative)
        if path.is_symlink():
            raise TargetError(f"skill source must not contain symlinks: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise TargetError(f"skill source contains a non-regular file: {path}")
        raw = _read_source_file(source_skill_root.resolve(), path, relative)
        if relative == "SKILL.md":
            raw = _skill_frontmatter(path, skill_id)
        copied[relative] = raw
        try:
            mode = path.stat(follow_symlinks=False).st_mode
        except OSError as exc:
            raise TargetError(f"could not inspect source mode: {path}") from exc
        if mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            executable.add(relative)
    if "SKILL.md" not in copied:
        raise TargetError(f"skill source has no SKILL.md: {source_skill_root}")
    return copied, frozenset(executable)


def _parse_agent_skills(body: str, known_skills: set[str], agent_id: str) -> list[str]:
    policy_match = re.search(r"<agent-skills>(.*?)</agent-skills>", body, re.DOTALL)
    if policy_match is None:
        raise TargetError(f"agent has no <agent-skills> policy: {agent_id}")
    skill_ids = _SKILL_POLICY.findall(policy_match.group(1))
    if not skill_ids:
        raise TargetError(f"agent <agent-skills> policy is empty: {agent_id}")
    missing = sorted(set(skill_ids) - known_skills)
    if missing:
        raise TargetError(
            f"agent references unknown skills: {agent_id}: {', '.join(missing)}"
        )
    return list(dict.fromkeys(f"skills/{skill_id}" for skill_id in skill_ids))


def _mapped_agent_tools(source_tools: Any, agent_id: str) -> list[str]:
    if not isinstance(source_tools, list) or not all(
        isinstance(tool, str) for tool in source_tools
    ):
        raise TargetError(f"agent tools must be a list of strings: {agent_id}")
    target_tools: list[str] = []
    for source_tool in source_tools:
        if source_tool in _SOURCE_TOOL_MAP:
            target_tools.extend(_SOURCE_TOOL_MAP[source_tool])
        elif (
            source_tool in _SOURCE_TOOLS_WITHOUT_DIRECT_EQUIVALENT
            or source_tool.startswith(_MCP_SOURCE_TOOL_PREFIXES)
        ):
            continue
        else:
            raise TargetError(
                f"no explicit Antigravity tool mapping for {source_tool!r} in {agent_id}"
            )
    result = list(dict.fromkeys(target_tools))
    unsupported = sorted(set(result) - SUPPORTED_AGENT_TOOLS)
    if unsupported:
        raise TargetError(
            f"mapped tools are not supported by the local Antigravity catalog: {unsupported}"
        )
    return result


def render_agent(
    agent_id: str,
    content: bytes,
    *,
    known_agents: set[str],
    known_skills: set[str],
    source_name: str,
) -> bytes:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TargetError(f"agent source is not valid UTF-8: {source_name}") from exc
    metadata, body = _frontmatter(text, source_name)
    if metadata.get("name") != agent_id:
        raise TargetError(f"agent name must match its source filename: {agent_id}")
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        raise TargetError(f"agent description must be non-empty: {agent_id}")
    if not body.strip():
        raise TargetError(f"agent instructions must be non-empty: {agent_id}")

    user_invocable = metadata.get("user-invocable", False)
    disable_model_invocation = metadata.get("disable-model-invocation", False)
    if not isinstance(user_invocable, bool) or not isinstance(
        disable_model_invocation, bool
    ):
        raise TargetError(f"agent invocation fields must be booleans: {agent_id}")

    source_agents = metadata.get("agents", [])
    if not isinstance(source_agents, list) or not all(
        isinstance(item, str) for item in source_agents
    ):
        raise TargetError(f"agent dependencies must be a list of names: {agent_id}")
    missing_agents = sorted(set(source_agents) - known_agents)
    if missing_agents:
        raise TargetError(
            f"agent references unknown agents: {agent_id}: {', '.join(missing_agents)}"
        )

    target_metadata: dict[str, Any] = {
        "name": agent_id,
        "description": description,
        "tools": _mapped_agent_tools(metadata.get("tools"), agent_id),
        "mainAgent": user_invocable,
        "subagent": not disable_model_invocation,
        "commandExecutionPolicy": "sandbox",
    }
    if source_agents:
        if "invoke_subagent" not in target_metadata["tools"]:
            raise TargetError(f"agent dependencies require invoke_subagent: {agent_id}")
        target_metadata["agents"] = source_agents
    target_metadata["skills"] = _parse_agent_skills(body, known_skills, agent_id)
    return _render_frontmatter(target_metadata, body)


def render_core_agent(
    agent: Any,
    *,
    known_agents: set[str],
    known_skills: set[str],
) -> bytes:
    """Render the private neutral Core source through Antigravity metadata."""
    profile = agent.projection("antigravity")
    tools = profile.get("tools")
    if not isinstance(tools, list) or not all(
        isinstance(tool, str) and tool in SUPPORTED_AGENT_TOOLS for tool in tools
    ):
        raise TargetError(f"unsupported Antigravity tool allowlist: {agent.name}")
    capability_tools = {
        "agent": {"invoke_subagent"},
        "execute": {"run_command"},
        "question": {"ask_question"},
        "read": {"list_directory", "view_file"},
        "search": {"find_file", "grep_search", "search_directory"},
    }
    for capability in agent.capabilities:
        supported_tools = capability_tools.get(capability)
        if supported_tools is not None and not (set(tools) & supported_tools):
            raise TargetError(
                f"Antigravity tools do not support {capability!r} capability: {agent.name}"
            )
        if capability not in {*capability_tools, "skill", "web", "browser"}:
            raise TargetError(
                f"Antigravity capability has no projection policy: {capability!r}"
            )
    main_agent = profile.get("mainAgent")
    subagent = profile.get("subagent")
    if not isinstance(main_agent, bool) or not isinstance(subagent, bool):
        raise TargetError(f"invalid Antigravity invocation settings: {agent.name}")
    dependencies = profile.get("agents", [])
    if not isinstance(dependencies, list) or not all(
        isinstance(item, str) and item in known_agents for item in dependencies
    ):
        raise TargetError(f"invalid Antigravity agent dependencies: {agent.name}")
    if dependencies and "invoke_subagent" not in tools:
        raise TargetError(f"agent dependencies require invoke_subagent: {agent.name}")
    body = agent.instructions_for("antigravity")
    metadata: dict[str, Any] = {
        "name": agent.name,
        "description": agent.description,
        "tools": tools,
        "mainAgent": main_agent,
        "subagent": subagent,
    }
    if dependencies:
        metadata["agents"] = dependencies
    metadata["skills"] = _parse_agent_skills(body, known_skills, agent.name)
    metadata["commandExecutionPolicy"] = "sandbox"
    return _render_frontmatter(metadata, body)


def _target_cwd(source_cwd: Any, server_id: str) -> str | None:
    if source_cwd is None:
        return None
    if not isinstance(source_cwd, str) or not source_cwd:
        raise TargetError(f"MCP cwd must be a non-empty string: {server_id}")
    if source_cwd == _PLUGIN_ROOT:
        return "."
    if source_cwd.startswith(f"{_PLUGIN_ROOT}/"):
        relative = source_cwd[len(_PLUGIN_ROOT) + 1 :]
        _validate_relative_path(relative)
        return relative
    if source_cwd.startswith("${") or Path(source_cwd).is_absolute():
        raise TargetError(f"MCP cwd is not portable to Antigravity: {server_id}")
    if source_cwd != ".":
        _validate_relative_path(source_cwd)
    return source_cwd


def render_mcp_config(source_manifest: Mapping[str, Any]) -> bytes:
    source_servers = source_manifest.get("mcpServers")
    if not isinstance(source_servers, dict) or not source_servers:
        raise TargetError("source mcp.json must declare at least one server")
    target_servers: dict[str, dict[str, Any]] = {}
    for server_id, source_server in sorted(source_servers.items()):
        if (
            not isinstance(server_id, str)
            or _ANTIGRAVITY_NAME.fullmatch(server_id) is None
        ):
            raise TargetError(f"invalid MCP server name: {server_id!r}")
        if not isinstance(source_server, dict):
            raise TargetError(f"MCP server entry must be an object: {server_id}")
        if source_server.get("type") != "stdio":
            raise TargetError(f"unsupported MCP transport for server: {server_id}")
        if "env" in source_server:
            raise TargetError(
                f"MCP environment values are not copied into the plugin: {server_id}"
            )
        command = source_server.get("command")
        args = source_server.get("args", [])
        if not isinstance(command, str) or not command:
            raise TargetError(f"MCP command must be non-empty: {server_id}")
        if not isinstance(args, list) or not all(
            isinstance(item, str) for item in args
        ):
            raise TargetError(f"MCP args must be a list of strings: {server_id}")
        target_server: dict[str, Any] = {"command": command, "args": args}
        cwd = _target_cwd(source_server.get("cwd"), server_id)
        if cwd is not None:
            target_server["cwd"] = cwd
        target_servers[server_id] = target_server
    return (
        json.dumps({"mcpServers": target_servers}, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")


def _source_plugin_root(source_root: Path) -> Path:
    raw_root = Path(source_root)
    if raw_root.is_symlink():
        raise TargetError("Agentic Core source root must not be a symlink")
    try:
        return raw_root.resolve(strict=True)
    except OSError as exc:
        raise TargetError(
            f"Agentic Core source root is unavailable: {raw_root}"
        ) from exc


def _add_file(files: dict[str, bytes], path: str, content: bytes) -> None:
    _validate_relative_path(path)
    if path in files:
        raise TargetError(f"duplicate Antigravity output path: {path}")
    files[path] = content


def project_core_plugin(source_root: Path) -> AntigravityProjection:
    """Project the canonical Agentic Core plugin into Antigravity's package shape."""
    root = _source_plugin_root(source_root)
    source_manifest_path = root / "plugin.json"
    source_manifest = _load_json(
        _read_source_file(root, source_manifest_path, "plugin.json"), "plugin.json"
    )
    source_mcp_path = root / "mcp.json"
    source_mcp = _load_json(
        _read_source_file(root, source_mcp_path, "mcp.json"), "mcp.json"
    )

    files: dict[str, bytes] = {
        "plugin.json": render_plugin_manifest(source_manifest),
        "mcp_config.json": render_mcp_config(source_mcp),
    }
    executable_files: set[str] = set()

    source_skills = root / "skills"
    if source_skills.is_symlink() or not source_skills.is_dir():
        raise TargetError("Agentic Core skills root must be a real directory")
    skill_ids: set[str] = set()
    for skill_root in sorted(source_skills.iterdir()):
        if skill_root.is_symlink():
            raise TargetError(f"skill directory must not be a symlink: {skill_root}")
        if not skill_root.is_dir():
            continue
        entrypoint = skill_root / "SKILL.md"
        if not entrypoint.exists():
            continue
        copied, executable = copy_skill_tree(skill_root)
        skill_id = skill_root.name
        skill_ids.add(skill_id)
        for relative, content in copied.items():
            output_path = f"skills/{skill_id}/{relative}"
            _add_file(files, output_path, content)
        executable_files.update(f"skills/{skill_id}/{path}" for path in executable)
    if not skill_ids:
        raise TargetError("Agentic Core has no valid domain skills")

    source_agents = root / "agents"
    if source_agents.is_symlink() or not source_agents.is_dir():
        raise TargetError("Agentic Core neutral agent source directory is missing")
    core_source_path = Path(__file__).resolve().parents[2] / "agentic-core"
    if str(core_source_path) not in sys.path:
        sys.path.insert(0, str(core_source_path))
    try:
        from core_agents import load_core_agents, load_core_projection_losses

        agents = load_core_agents(source_agents)
        core_losses = load_core_projection_losses(source_agents)
    except (OSError, ValueError) as exc:
        raise TargetError(
            f"Agentic Core neutral agent source is invalid: {exc}"
        ) from exc
    agent_ids = set(agents)
    reported_losses = " ".join(core_losses["antigravity"]).casefold()
    for agent in agents.values():
        for unsupported in agent.capabilities & {"browser", "web"}:
            if unsupported not in reported_losses:
                raise TargetError(
                    f"Antigravity projection omits {unsupported!r} without a loss record"
                )
    for agent_id, agent in agents.items():
        output_path = f"agents/{agent_id}.md"
        _add_file(
            files,
            output_path,
            render_core_agent(
                agent,
                known_agents=agent_ids,
                known_skills=skill_ids,
            ),
        )

    github_wrapper = root / "runtime" / "mcp" / "github-app-stdio.sh"
    wrapper_relative = "runtime/mcp/github-app-stdio.sh"
    if "github-mcp-server" in source_mcp.get("mcpServers", {}):
        wrapper_content = _read_source_file(root, github_wrapper, wrapper_relative)
        _add_file(files, wrapper_relative, wrapper_content)

    mapping_losses = tuple(
        dict.fromkeys((*DOCUMENTED_MAPPING_LOSSES, *core_losses["antigravity"]))
    )
    projection = AntigravityProjection(
        files, frozenset(executable_files), mapping_losses=mapping_losses
    )
    validate_antigravity_layout(projection)
    return projection


def _load_target_frontmatter(content: bytes, label: str) -> tuple[dict[str, Any], str]:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TargetError(f"projected Markdown is not valid UTF-8: {label}") from exc
    return _frontmatter(text, label)


def validate_antigravity_layout(
    projection: AntigravityProjection | Mapping[str, bytes],
) -> None:
    files = _validate_file_map(
        projection.files
        if isinstance(projection, AntigravityProjection)
        else projection
    )
    if "plugin.json" not in files:
        raise TargetError("Antigravity plugin layout is missing plugin.json")
    manifest = _load_json(files["plugin.json"], "projected plugin.json")
    if set(manifest) - {"$schema", "name", "description"}:
        raise TargetError("projected plugin.json contains unsupported fields")
    if manifest.get("$schema") != ANTIGRAVITY_PLUGIN_SCHEMA:
        raise TargetError("projected plugin.json has the wrong Antigravity schema")
    name = manifest.get("name")
    if not isinstance(name, str) or _ANTIGRAVITY_NAME.fullmatch(name) is None:
        raise TargetError("projected plugin name is invalid")
    if (
        not isinstance(manifest.get("description"), str)
        or not manifest["description"].strip()
    ):
        raise TargetError("projected plugin description must be non-empty")

    root_skills: set[str] = set()
    for path, content in files.items():
        parts = path.split("/")
        if len(parts) == 3 and parts[0] == "skills" and parts[2] == "SKILL.md":
            skill_id = parts[1]
            metadata, _ = _load_target_frontmatter(content, path)
            if set(metadata) != {"name", "description"}:
                raise TargetError(
                    f"projected skill has unsupported frontmatter: {path}"
                )
            if metadata.get("name") != skill_id:
                raise TargetError(
                    f"projected skill name does not match its path: {path}"
                )
            if (
                not isinstance(metadata.get("description"), str)
                or not metadata["description"].strip()
            ):
                raise TargetError(
                    f"projected skill description must be non-empty: {path}"
                )
            root_skills.add(skill_id)
    if not root_skills:
        raise TargetError("Antigravity layout has no domain skill entrypoints")

    agent_ids: set[str] = set()
    agent_metadata: dict[str, dict[str, Any]] = {}
    for path, content in files.items():
        if not path.startswith("agents/") or not path.endswith(".md"):
            continue
        agent_id = Path(path).stem
        metadata, body = _load_target_frontmatter(content, path)
        allowed = {
            "name",
            "description",
            "tools",
            "mainAgent",
            "subagent",
            "agents",
            "skills",
            "commandExecutionPolicy",
        }
        if set(metadata) - allowed:
            raise TargetError(f"agent has unsupported Antigravity frontmatter: {path}")
        if metadata.get("name") != agent_id:
            raise TargetError(f"agent name does not match its path: {path}")
        if (
            not isinstance(metadata.get("description"), str)
            or not metadata["description"].strip()
        ):
            raise TargetError(f"agent description must be non-empty: {path}")
        tools = metadata.get("tools")
        if not isinstance(tools, list) or not all(
            isinstance(tool, str) and tool in SUPPORTED_AGENT_TOOLS for tool in tools
        ):
            raise TargetError(f"agent has an unsupported tool allowlist: {path}")
        for field in ("mainAgent", "subagent"):
            if not isinstance(metadata.get(field), bool):
                raise TargetError(f"agent field {field} must be boolean: {path}")
        if metadata.get("commandExecutionPolicy") != "sandbox":
            raise TargetError(f"agent command policy must be sandboxed: {path}")
        if not body.strip():
            raise TargetError(f"agent has an empty instruction body: {path}")
        dependencies = metadata.get("agents", [])
        if not isinstance(dependencies, list) or not all(
            isinstance(item, str) for item in dependencies
        ):
            raise TargetError(f"agent dependencies must be a list: {path}")
        skills = metadata.get("skills")
        if not isinstance(skills, list) or not skills:
            raise TargetError(f"agent must reference one or more skills: {path}")
        for skill_path in skills:
            if not isinstance(skill_path, str) or not skill_path.startswith("skills/"):
                raise TargetError(
                    f"agent skill references must be plugin-relative: {path}"
                )
            skill_id = skill_path.removeprefix("skills/")
            if skill_id not in root_skills:
                raise TargetError(
                    f"agent references an unknown skill: {path}: {skill_path}"
                )
        agent_ids.add(agent_id)
        agent_metadata[agent_id] = metadata
    if not agent_ids:
        raise TargetError("Antigravity layout has no agents")
    if sum(bool(metadata["mainAgent"]) for metadata in agent_metadata.values()) != 1:
        raise TargetError("Antigravity layout must expose exactly one main agent")
    for agent_id, metadata in agent_metadata.items():
        if set(metadata.get("agents", [])) - agent_ids:
            raise TargetError(f"agent has an unknown dependency: {agent_id}")
        if metadata.get("agents") and "invoke_subagent" not in metadata["tools"]:
            raise TargetError(
                f"agent dependency list requires invoke_subagent: {agent_id}"
            )

    if "mcp_config.json" not in files:
        raise TargetError("Antigravity plugin layout is missing mcp_config.json")
    mcp_manifest = _load_json(files["mcp_config.json"], "projected mcp_config.json")
    if set(mcp_manifest) != {"mcpServers"} or not isinstance(
        mcp_manifest["mcpServers"], dict
    ):
        raise TargetError("projected mcp_config.json has an invalid root shape")
    allowed_mcp_fields = {
        "command",
        "args",
        "cwd",
        "env",
        "serverUrl",
        "headers",
        "authProviderType",
        "oauth",
        "disabled",
        "disabledTools",
    }
    for server_id, server in mcp_manifest["mcpServers"].items():
        if not isinstance(server_id, str) or not isinstance(server, dict):
            raise TargetError("projected MCP server IDs and entries must be valid")
        if set(server) - allowed_mcp_fields or "type" in server:
            raise TargetError(
                f"projected MCP entry contains unsupported fields: {server_id}"
            )
        command = server.get("command")
        if not isinstance(command, str) or not command:
            raise TargetError(f"projected MCP command must be non-empty: {server_id}")
        args = server.get("args", [])
        if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
            raise TargetError(f"projected MCP args must be strings: {server_id}")
        if "env" in server:
            raise TargetError(
                f"projected MCP config must not contain credentials/env: {server_id}"
            )
        cwd = server.get("cwd")
        if cwd is not None and cwd != ".":
            _validate_relative_path(cwd)
        for arg in args:
            if arg.endswith(".sh") and not Path(arg).is_absolute():
                wrapper_path = Path(cwd or ".") / arg
                normalized = wrapper_path.as_posix().removeprefix("./")
                if normalized not in files:
                    raise TargetError(
                        f"projected MCP wrapper is missing from plugin: {server_id}: {arg}"
                    )

    if "hooks.json" in files or any(path.startswith("commands/") for path in files):
        raise TargetError("projection must not invent hooks or command files")


def materialize_projection(
    projection: AntigravityProjection, output_root: Path
) -> Path:
    """Write a new standalone projection directory without overwriting existing data."""
    validate_antigravity_layout(projection)
    raw_output = Path(output_root).expanduser()
    if not raw_output.is_absolute():
        raw_output = Path.cwd() / raw_output
    if raw_output.exists() or raw_output.is_symlink():
        raise TargetError(f"refusing to overwrite projection output: {raw_output}")
    cursor = raw_output.parent
    while cursor != cursor.parent:
        if cursor.is_symlink():
            raise TargetError(
                f"projection output parent must not be a symlink: {cursor}"
            )
        cursor = cursor.parent
    created_output = False
    try:
        raw_output.mkdir(parents=True, exist_ok=False)
        created_output = True
        for relative, content in sorted(projection.files.items()):
            target = raw_output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(content)
            target.chmod(0o755 if relative in projection.executable_files else 0o644)
    except FileExistsError as exc:
        raise TargetError(
            f"refusing to overwrite projection output: {raw_output}"
        ) from exc
    except OSError as exc:
        if created_output:
            shutil.rmtree(raw_output, ignore_errors=True)
        raise TargetError(f"could not write Antigravity projection: {exc}") from exc
    return raw_output


__all__ = [
    "ANTIGRAVITY_PLUGIN_SCHEMA",
    "DOCUMENTED_MAPPING_LOSSES",
    "SUPPORTED_AGENT_TOOLS",
    "AntigravityProjection",
    "copy_skill_tree",
    "materialize_projection",
    "project_core_plugin",
    "render_agent",
    "render_mcp_config",
    "render_plugin_manifest",
    "validate_antigravity_layout",
]
