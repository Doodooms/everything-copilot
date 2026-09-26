# Expertise Pack Contract

## Canonical source and package layout

An Expertise Pack is the canonical source for reusable expertise. Its source lives below `expertise/packs/[pack-id]/` and is compiled into target-specific plugin outputs; generated output is not a second source of truth.

```text
expertise/packs/[pack-id]/
├── pack.yaml
├── mcp.json                         # optional
├── agents/
│   └── [agent-id].agent.md          # optional contributions
└── skills/
    └── [skill-id]/
        ├── SKILL.md
        └── [only-consumed-support-files]
```

`expertise scaffold` creates a valid starter `pack.yaml` and one skill. Add or remove contributions only after deciding which agent or workflow the capability actually needs.

## Manifest responsibilities

`pack.yaml` is validated against `expertise/schemas/pack.schema.json`. Its fields have one job each:

- `id`, `type`, `name`, `version`, and `description` identify the horizontal or vertical pack.
- `compatibility.targets` declares `portable`, `copilot`, and/or `codex`; `agent_plugins` is the minimum compatible Agent Plugins version.
- `trust` identifies the publisher and canonical source and requires approval.
- `capabilities` names the expertise exposed by the pack; `dependencies` declares required capabilities from other packs.
- `agents.contributions` adds a pack-owned agent; `agents.extensions` projects a capability into an existing core agent.
- `skills` registers packaged workflows and their source paths.
- `mcp_config` points to an optional MCP manifest; `mcp_servers` declares each server's capability, permissions, and exact published tool names in `tools`.
- `projections` assigns only the listed capabilities, skills, and MCP servers to each agent.

Use the scaffold-generated manifest as the default. Do not copy a second handwritten schema or add empty agent, dependency, or MCP sections beyond what the schema requires.

## MCP boundary

- MCP servers expose deterministic tools; skills remain packaged workflows.
- Pin executable package versions in `mcp.json`; do not commit credentials or assume environment-variable interpolation that the host does not document.
- For Copilot, project an MCP server only to agents that require its operations. Keep the agent's `tools` list equally narrow.
- A server projection makes its configuration available to the composed profile; it does not automatically amend an agent's `tools` allowlist. A core-agent allowlist change belongs in the canonical core agent source and is validated with the `agent-authoring` workflow.
- Use the host's existing read-only GitHub integration where available. Do not bundle a second authenticated GitHub server merely to duplicate host capability.
- For pack-owned agents, use the exact host-facing `server/tool` name. The linter requires the name in `mcp_servers[].tools` and its server to be projected to that agent; it cannot query arbitrary server processes offline. Populate the catalog from the live `tools/list` response or authoritative registered tool definitions and pin the implementation/version when possible. Update the core catalog only when adding a reusable core/host alias.

## Target outputs

All targets compile from the same validated pack source:

- `portable` emits the standard plugin manifest, skills, optional `mcp.json`, integration manifest, and agent contribution sources.
- `copilot` emits the portable plugin package plus VS Code/Copilot agent files under `com.github.copilot/agents/`.
- `codex` emits the portable plugin package plus `codex-agents/[agent-id].toml` sidecars for pack-owned agents. The current adapter exports only `name`, `description`, and `developer_instructions`; MCP configuration remains at plugin scope.

Codex agent sidecars are generated exports, not active agents merely because they are inside the plugin. Place them in the applicable `.codex/agents/` directory or user-level Codex agents directory separately. Codex's [subagent documentation](https://developers.openai.com/codex/subagents) describes `mcp_servers` in custom-agent files, but the current [role application](https://github.com/openai/codex/blob/main/codex-rs/core/src/agent/role.rs) projects only a bounded set of overrides, and its [regression test](https://github.com/openai/codex/blob/main/codex-rs/core/src/agent/role_tests.rs) confirms that a role cannot change the parent's `mcp_servers`. Therefore the Codex target packages its MCP manifest at plugin scope and every agent inherits access to all packaged MCP servers/tools. Keep Codex MCP servers suitable for this wider audience; do not claim per-agent isolation. Do not claim the build installed agents.

## Authoring and validation commands

Run from the Agentic Workflow repository root with its configured environment:

```sh
PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python -m expertise scaffold [pack-id] [authoring options]
PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python -m expertise validate [pack-id]
PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python -m expertise test [pack-id]
PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python -m expertise build [pack-id] --target portable
PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python -m expertise build [pack-id] --target copilot
PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python -m expertise build [pack-id] --target codex
```

`scaffold` validates the starter against selected targets before publishing it. `validate` checks the canonical source; `test` validates and smoke-compiles every declared target in memory; `build` materializes a chosen target below `dist/`. Do not use built output as input to another build.