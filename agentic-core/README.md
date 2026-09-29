# Agentic Core

This Agent Plugin bundles the canonical agents, domain skills, and their MCP integrations.

The `multi-harness` skill coordinates bounded Copilot/Codex handoffs. Its two host workflows cross-read each other before communication; see `skills/multi-harness/workflows/`.

The Orchestrator can also use `skills/orchestration/workflows/chatgpt-work-handoff.md` to prepare a verified GitHub PR for a ChatGPT Work event-triggered status report. Codex/Copilot retain implementation and validation ownership; the Work task is read-only and returns a discussion summary.

## Packaged lifecycle CLI

Run `uv run --script /absolute/path/to/agentic-core/runtime/pluginctl_cli.py` from any working directory, passing explicit `--store-root` and (when needed) `--workspace-root` paths. The script declares Python 3.10+ and PyYAML 6.x; a direct `python` invocation works when PyYAML is already installed. The runtime includes the canonical `expertise` package; keep it synchronized with the repository source by running `python scripts/sync_pluginctl_runtime.py --write` after changing `expertise/`.

## GitHub App MCP

The `github-mcp-server` MCP is started by the plugin host as a dedicated Docker container using stdio. GitHub App authentication is supported by the official server in stdio mode; the HTTP mode does not support this authentication flow.

Before starting Copilot or Codex, make these values available in the host process environment:

- `GITHUB_APP_ID`
- `GITHUB_APP_INSTALLATION_ID`
- `GITHUB_APP_PRIVATE_KEY_PATH`: absolute path to the App's PEM file on the host

The launcher requires Docker, passes the App ID and installation ID to the container, and mounts the PEM file read-only at `/secrets/github-app.pem`. It uses the pinned image `ghcr.io/github/github-mcp-server:v1.12.2`. No credential values or private key files belong in this package. Do not use `GITHUB_APP_PRIVATE_KEY` inline.

After setting the environment, start or restart the host/MCP session so it can launch the server. If the server or its tools are unavailable, inspect the host's MCP diagnostics and fix the host configuration; agents must report the GitHub operation as blocked rather than inspect credentials or switch to another GitHub identity.

## Agent access

- Orchestrator uses the GitHub MCP surface for remote GitHub API and lifecycle operations; local `git` remains for local repository and worktree operations.
- Researcher has an explicit read-only GitHub MCP allowlist for repository evidence.
- Other agents do not receive GitHub MCP access by default.
