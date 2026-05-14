# Manage MCP Servers in VS Code

## Purpose

- Use this file when the task changes VS Code registration, trust, sandboxing, configuration location, or server lifecycle behavior.
- Do not use this file to choose the implementation language. That belongs in [language-selection-checklist](../assets/language-selection-checklist.md).

## Configuration targets

- **Workspace**: `.vscode/mcp.json` when the server should be shared with the repository.
- **User profile**: personal global `mcp.json` when the server should follow the user across workspaces.
- **Remote user config**: when the server must run on the remote machine rather than locally.
- **Dev Container**: `devcontainer.json` under `customizations.vscode.mcp` when the server belongs inside the containerized environment.
- **CLI add flow**: `code --add-mcp` when the task is explicitly about provisioning a local user-profile server from the command line.

## Local stdio pattern

```json
{
  "servers": {
    "my-server": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "python", "server.py"]
    }
  }
}
```

- VS Code local examples may omit `type` when `command` is present.
- In this repository, explicit `type: stdio` is preferred for readability, and the local validator accepts both shapes.
- Keep `command`, `args`, `cwd`, and `env` minimal and deterministic.

## Remote Streamable HTTP pattern

```json
{
  "servers": {
    "my-remote-server": {
      "type": "streamable-http",
      "url": "https://example.com/mcp"
    }
  }
}
```

- Use remote transport when the server is hosted elsewhere and the client should not spawn a local process.
- Keep secrets out of the URL when the configuration is shared.

## Trust, secrets, and sandboxing

- Review the full server configuration before trusting a new local server. Local servers can execute arbitrary code.
- Prefer environment variables or VS Code input variables over hardcoded tokens.
- On macOS and Linux, local stdio servers can enable `sandboxEnabled` and add a `sandbox` object to restrict filesystem and network access.
- Sandboxing is not available on Windows.
- If the task touches a sensitive server, explain why the chosen trust and sandbox posture is acceptable.

## Lifecycle and debugging

- Use **MCP: Add Server** for guided registration.
- Use **MCP: List Servers** to start, stop, enable, disable, or inspect servers.
- Use **Show Output** from the MCP server actions when the server fails to start or discover tools.
- Use **MCP: Reset Trust** if a trust prompt needs to be re-reviewed.
- Use the chat **Configure Tools** button to confirm the discovered tool surface.
- If configuration changes should auto-restart servers, check the experimental `chat.mcp.autoStart` setting.

## Related docs

- Use [latest docs](./latest-docs.md) when you need the current VS Code or MCP guidance.
- Use [URIs](./URIs.md) when you need the canonical documentation link for the selected SDK or configuration reference.
