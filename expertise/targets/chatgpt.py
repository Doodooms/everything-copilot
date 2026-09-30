"""Generic ChatGPT package projection for registered MCP app connections."""

from __future__ import annotations

import hashlib
import json
import re
import shlex
from pathlib import Path

from ..errors import TargetError
from ..foam_binding import FOAM_WORKSPACE_PLACEHOLDER, bind_foam_workspace
from ..ir import PackSource
from ..validator import load_json_no_duplicate_keys
from . import compile_target
from .common import validate_target_files
from .validation import validate_mcp_manifest, validate_plugin_manifest

APP_ID_PATTERN = re.compile(
    r"^(?:plugin_)?(?:asdk_app|connector|templated_apps)_[A-Za-z0-9][A-Za-z0-9_-]{0,127}$"
)
TUNNEL_ID_PATTERN = re.compile(r"^tunnel_[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
OPENAI_APPS_PATH = "./.app.json"
CONNECTION_PATH = "com.doodooms.agentic-workflow/chatgpt-connection.md"
PROVENANCE_PATH = "com.doodooms.agentic-workflow/chatgpt-projection.json"


def _connection_guide(
    pack: PackSource,
    mcp_manifest: dict[str, object] | None,
    *,
    tunnel_id: str | None,
    app_registered: bool,
) -> bytes | None:
    if mcp_manifest is None:
        return None
    servers = mcp_manifest.get("mcpServers")
    if not isinstance(servers, dict):
        raise TargetError("ChatGPT projection MCP manifest has invalid servers")
    stdio_servers = [
        (server_id, server)
        for server_id, server in sorted(servers.items())
        if isinstance(server, dict) and server.get("type") == "stdio"
    ]
    if not stdio_servers:
        return None
    if len(stdio_servers) != 1:
        raise TargetError(
            "Secure MCP Tunnel setup currently supports one local stdio server per generated guide"
        )
    server_id, server = stdio_servers[0]
    command = server.get("command")
    args = server.get("args", [])
    if (
        not isinstance(command, str)
        or not isinstance(args, list)
        or any(not isinstance(item, str) for item in args)
    ):
        raise TargetError("stdio command configuration is malformed")
    if FOAM_WORKSPACE_PLACEHOLDER in args:
        raise TargetError("bind the Foam workspace before ChatGPT projection")
    if FOAM_WORKSPACE_PLACEHOLDER in command:
        raise TargetError("MCP command contains an unresolved workspace placeholder")
    mcp_command = shlex.join([command, *args])
    selected_tunnel_id = tunnel_id or "your_tunnel_id"
    selected_profile = f"{pack.ir.id}-{server_id}"
    if app_registered:
        app_step = (
            "The supplied `.app.json` mapping references an app ID already registered in ChatGPT. "
            "Confirm that app is configured to use this running tunnel and review its discovered tools."
        )
    else:
        app_step = (
            "After the tunnel client is healthy, create the ChatGPT developer-mode app and select this tunnel. "
            "Then rerun the ChatGPT projector with the registered app ID in `.app.json`."
        )
    guide = f"""# ChatGPT connection setup

The generated `.app.json` contains only the registered app mappings supplied to the projector; it may be empty before app registration. Package generation does not register the app or establish a connection.

For local stdio server `{server_id}`, run Secure MCP Tunnel in the same environment as that server. Create a tunnel in OpenAI Platform first, then initialize the local profile:

```sh
export CONTROL_PLANE_API_KEY="<runtime-api-key>"
tunnel-client init \\
  --sample sample_mcp_stdio_local \\
  --profile {selected_profile} \\
  --tunnel-id {selected_tunnel_id} \\
  --mcp-command {shlex.quote(mcp_command)}
tunnel-client doctor --profile {selected_profile} --explain
tunnel-client run --profile {selected_profile}
```

Keep the runtime API key outside the package. {app_step} Tunnel readiness, app registration, tool discovery, and runtime invocation are separate from this generated package.
"""
    return guide.encode("utf-8")


def compile_chatgpt(
    source: PackSource,
    app_ids: dict[str, str],
    *,
    workspace: Path | None = None,
    tunnel_id: str | None = None,
) -> tuple[dict[str, bytes], dict[str, object]]:
    """Project any canonical Pack and bind only its generated local MCP config."""
    server_ids = {server.id for server in source.ir.mcp_servers}
    if not set(app_ids).issubset(server_ids):
        raise TargetError("app ID mapping contains an undeclared Pack MCP server ID")
    if app_ids and set(app_ids) != server_ids:
        raise TargetError(
            "app ID mapping must be empty before registration or cover every Pack MCP server ID"
        )
    for server_id, app_id in sorted(app_ids.items()):
        if not isinstance(app_id, str) or APP_ID_PATTERN.fullmatch(app_id) is None:
            raise TargetError(f"invalid registered ChatGPT app ID for {server_id!r}")
    if tunnel_id is not None and TUNNEL_ID_PATTERN.fullmatch(tunnel_id) is None:
        raise TargetError("tunnel ID must be a bounded OpenAI tunnel identifier")

    artifact = compile_target(source, "portable")
    files = dict(artifact.files)
    mcp_manifest: dict[str, object] | None = None
    if "mcp.json" in files:
        try:
            parsed = load_json_no_duplicate_keys(files["mcp.json"])
        except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
            raise TargetError("portable Pack output has invalid mcp.json") from exc
        if not isinstance(parsed, dict):
            raise TargetError("portable MCP manifest must be an object")
        mcp_manifest = parsed
        raw_text = files["mcp.json"].decode("utf-8")
        if FOAM_WORKSPACE_PLACEHOLDER in raw_text:
            if workspace is None:
                raise TargetError(
                    "this Pack requires an install-local workspace binding"
                )
            files = bind_foam_workspace(files, workspace)
            mcp_manifest = json.loads(files["mcp.json"].decode("utf-8"))

    try:
        plugin_manifest = load_json_no_duplicate_keys(files["plugin.json"])
    except (KeyError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise TargetError("portable Pack output has invalid plugin.json") from exc
    if not isinstance(plugin_manifest, dict):
        raise TargetError("portable plugin manifest must contain a JSON object")
    extensions = plugin_manifest.setdefault("extensions", {})
    if not isinstance(extensions, dict):
        raise TargetError("plugin extensions must be an object")
    openai = extensions.setdefault("com.openai", {})
    if not isinstance(openai, dict):
        raise TargetError("OpenAI plugin extension must be an object")
    existing_apps_path = openai.get("apps")
    if existing_apps_path not in (None, OPENAI_APPS_PATH):
        raise TargetError("source plugin points to a different OpenAI apps file")
    openai["apps"] = OPENAI_APPS_PATH

    app_manifest = {
        "apps": {
            server_id: {"id": app_id} for server_id, app_id in sorted(app_ids.items())
        }
    }
    files["plugin.json"] = (
        json.dumps(plugin_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    files[".app.json"] = (
        json.dumps(app_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    guide = _connection_guide(
        source,
        mcp_manifest,
        tunnel_id=tunnel_id,
        app_registered=bool(app_ids),
    )
    if guide is not None:
        files[CONNECTION_PATH] = guide

    validate_plugin_manifest(plugin_manifest)
    if mcp_manifest is not None:
        validate_mcp_manifest(mcp_manifest)
    files = dict(validate_target_files(files))
    provenance: dict[str, object] = {
        "schema_version": 1,
        "target": "chatgpt-package",
        "source_pack": f"{source.ir.id}@{source.ir.version}",
        "source_digest": artifact.source_digest,
        "registered_app_ids": [app_ids[key] for key in sorted(app_ids)],
        "mcp_servers": sorted(server_ids),
        "projected_files_sha256": _files_digest(files),
        "connection_status": "not_connected_by_projection",
    }
    files[PROVENANCE_PATH] = (
        json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    return dict(validate_target_files(files)), provenance


def _files_digest(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for relative, content in sorted(files.items()):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()
