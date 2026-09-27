# Agentic Workflow

This repository packages a reusable agent workflow as an Agent Plugin and provides the tooling to manage Expertise Packs. The current direction is plugin-first: reusable agents and skills belong to `agentic-core`; project-specific customizations remain workspace-local.

## Repository milestones

- `v0.0.0` preserves the previous remote `main` baseline before the plugin-factory transition.
- `v1.0.0` marks the new plugin-factory baseline on `main`.
- These baselines have separate Git histories. The old history remains inspectable with `git log v0.0.0`; the new history with `git log v1.0.0`. The tags version the repository milestone; `agentic-core/plugin.json` has its own package version.

## Layout

- `agentic-core/plugin.json`, `mcp.json`: installable Core plugin and its bundled MCP servers.
- `agentic-core/README.md`: GitHub App MCP Docker setup and agent access boundaries.
- `agentic-core/com.github.copilot/agents/`: Copilot agent definitions.
- `agentic-core/skills/`: discoverable domain skills, internal workflows, references, assets, and validation tools.
- `agentic-core/runtime/pluginctl/`: workspace plugin/profile lifecycle and materialization commands.
- `harness_factory/`: isolated Copilot/Codex capability detection, static validation, and bounded run adapters.
- `.github/copilot-instructions.md`: workspace-wide agent invariants and risk policy.

`agentic-core` is the current packaged baseline. Additional vertical Expertise Packs remain separate from the Core package.

## Codex custom agents

The Core plugin's canonical agent definitions use Copilot frontmatter. Run `uv run --no-project --with pyyaml python scripts/install_codex_agents.py` to validate and render those nine definitions through `expertise/targets/codex.py` into `~/.codex/agents/*.toml`. The adapter preserves descriptions and instructions, maps the Codex model and reasoning fields, and omits Copilot-only tool and invocation metadata. Codex loads custom agent files for spawned sessions, so open a new session after installation.

The Core plugin launches the official GitHub App MCP server in a dedicated Docker container over stdio. Host environment prerequisites and the read-only private-key mount are documented in [`agentic-core/README.md`](./agentic-core/README.md).

## Harness factory

Run the harness CLI from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m harness_factory detect
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m harness_factory validate \
  --target copilot --source-root agentic-core
```

`prepare` creates a detached worktree at an explicit commit and prints a local development command. `smoke` performs one read-only, bounded invocation; the factory stores only normalized results, never response text. Host-native session persistence remains controlled by each CLI. Use a dedicated `--state-root` outside the repository; each run records its owner and must be explicitly cleaned with `cleanup`. Dirty or running worktrees are never removed.

Copilot smoke is limited to the read-only `glob`, `grep`, and `view` tools, disables built-in and plugin MCP servers, and uses a 30-credit cap (the installed CLI's minimum accepted limit). Codex smoke uses a project-local plugin marketplace, ignores global user config/MCPs, and runs with `--ephemeral` plus the read-only sandbox. Codex has no CLI cost-cap flag in the inspected version, so token usage is reported when present and dollar cost remains unknown. Codex plugins that declare MCP servers are refused rather than launched without a per-plugin disable control. Missing CLI or help evidence is reported as blocked/unknown rather than inferred support.
