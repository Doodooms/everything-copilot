# Agentic Workflow

This repository packages a reusable agent workflow as an Agent Plugin and provides the tooling to manage Expertise Packs. The current direction is plugin-first: reusable agents and skills belong to `agentic-core`; project-specific customizations remain workspace-local.

## Repository milestones

- `v0.0.0` preserves the previous remote `main` baseline before the plugin-factory transition.
- `v1.0.0` marks the new plugin-factory baseline on `main`.
- These baselines have separate Git histories. The old history remains inspectable with `git log v0.0.0`; the new history with `git log v1.0.0`. The tags version the repository milestone; `agentic-core/plugin.json` has its own package version.

## Layout

- `agentic-core/plugin.json`, `mcp.json`: installable Core plugin and its bundled MCP servers.
- `agentic-core/com.github.copilot/agents/`: Copilot agent definitions.
- `agentic-core/skills/`: discoverable domain skills, internal workflows, references, assets, and validation tools.
- `agentic-core/runtime/pluginctl/`: workspace plugin/profile lifecycle and materialization commands.
- `.github/copilot-instructions.md`: workspace-wide agent invariants and risk policy.

`agentic-core` is the current packaged baseline. Additional vertical Expertise Packs and host adapters are separate follow-up work; their presence must not be inferred from the Core package alone.
