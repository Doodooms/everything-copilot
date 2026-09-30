"""Install-local workspace binding for the canonical Foam MCP configuration."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from .errors import TargetError

FOAM_WORKSPACE_PLACEHOLDER = "__FOAM_WORKSPACE__"


def bind_foam_workspace(
    files: Mapping[str, bytes], workspace: Path
) -> dict[str, bytes]:
    """Bind a compiled Foam package without changing its canonical Pack source."""
    raw_workspace = Path(workspace)
    if not raw_workspace.is_absolute():
        raise TargetError("Foam workspace path must be absolute")
    if raw_workspace.is_symlink() or not raw_workspace.is_dir():
        raise TargetError("Foam workspace must be an existing real directory")
    resolved_workspace = raw_workspace.resolve(strict=True)
    if resolved_workspace.parent == resolved_workspace:
        raise TargetError("filesystem root cannot be used as a Foam workspace")

    try:
        mcp = json.loads(files["mcp.json"].decode("utf-8"))
    except (KeyError, UnicodeError, json.JSONDecodeError) as exc:
        raise TargetError("compiled Foam package has no valid mcp.json") from exc
    if not isinstance(mcp, dict) or not isinstance(mcp.get("mcpServers"), dict):
        raise TargetError("Foam mcp.json must contain an mcpServers object")
    servers = mcp["mcpServers"]
    if set(servers) != {"foam"}:
        raise TargetError("Foam package must configure exactly the foam MCP server")
    server = servers["foam"]
    if not isinstance(server, dict) or server.get("type") != "stdio":
        raise TargetError("Foam server must use direct stdio MCP transport")
    if server.get("command") != "foam":
        raise TargetError("Foam server command must be the installed foam CLI")
    args = server.get("args")
    expected = ["mcp", "--workspace", FOAM_WORKSPACE_PLACEHOLDER, "--allow-writes"]
    if args != expected:
        raise TargetError(
            "Foam MCP arguments do not match the canonical binding contract"
        )

    server["args"] = ["mcp", "--workspace", str(resolved_workspace), "--allow-writes"]
    bound = dict(files)
    bound["mcp.json"] = (
        json.dumps(mcp, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    return bound
