# Agentic Core

This Agent Plugin bundles the canonical agents, domain skills, and their MCP integrations.

The `multi-harness` skill coordinates bounded Copilot/Codex handoffs. Its two host workflows cross-read each other before communication; see `skills/multi-harness/workflows/`.

The Orchestrator can also use `skills/orchestration/workflows/chatgpt-work-handoff.md` to prepare a verified GitHub PR for a ChatGPT Work event-triggered status report. Codex/Copilot retain implementation and validation ownership; the Work task is read-only and returns a discussion summary.

## Packaged lifecycle CLI

Run `uv run --script /absolute/path/to/agentic-core/runtime/pluginctl_cli.py` from any working directory, passing explicit `--store-root` and (when needed) `--workspace-root` paths. The script declares Python 3.10+ and PyYAML 6.x; a direct `python` invocation works when PyYAML is already installed. The runtime includes the package's canonical `expertise` implementation and does not require the Plugin Factory repository at build or runtime.

## Local Expertise Pack authoring

Scaffold and smoke-test an Expertise Pack directly in its workspace without a Control Plane connection, manifest, or history paths. From the workspace root:

```bash
uv run --no-project --with PyYAML python -c 'from pathlib import Path; from runtime.expertise.cli import main; raise SystemExit(main(["scaffold", "local-workflow-check", "--name", "Local Workflow Check", "--description", "A locally authored Expertise Pack.", "--capability", "local.check", "--skill-id", "local-check", "--skill-description", "Check local authoring.", "--publisher", "Local Workspace", "--source", "Workspace authoring", "--target", "portable"], repo_root=Path.cwd()))'
uv run --no-project --with PyYAML python -c 'from pathlib import Path; from runtime.expertise.cli import main; raise SystemExit(main(["test", "local-workflow-check"], repo_root=Path.cwd()))'
```

The scaffold is written under `expertise/packs/local-workflow-check/`; the test validates and smoke-compiles its declared targets in memory.

## Rebuild agent projections

From the Plugin Factory repository root, regenerate and verify the Copilot, Codex, or Claude projection from the canonical Agentic Core source. These commands write only under the selected output directory; Codex profile installation is a separate explicit operation.

```bash
uv run --no-project --with pyyaml python scripts/project_plugin_agents.py copilot --source-root agentic-core --output-dir agentic-core/com.github.copilot/agents
uv run --no-project --with pyyaml python scripts/project_plugin_agents.py copilot --source-root agentic-core --output-dir agentic-core/com.github.copilot/agents --check
uv run --no-project --with pyyaml python scripts/project_plugin_agents.py codex --source-root agentic-core --output-dir agentic-core/projections/codex
uv run --no-project --with pyyaml python scripts/project_plugin_agents.py claude --source-root agentic-core --output-dir agentic-core/projections/claude
uv run --no-project --with pyyaml python scripts/project_plugin_agents.py claude --source-root agentic-core --output-dir agentic-core/projections/claude --check
```

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
