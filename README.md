# Plugin Factory

Plugin Factory is the current repository name for the Plugin Platform. `factory/` owns deterministic, content-neutral plugin tooling; `agentic-core/` is the canonical self-hosted Agent Plugin, including `plugin-engineering`. See [Plugin Platform ownership](./docs/architecture/PLUGIN_PLATFORM_BOUNDARIES.md).

## Repository milestones

- `v0.0.0` preserves the previous remote `main` baseline before the plugin-factory transition.
- `v1.0.0` marks the new plugin-factory baseline on `main`.
- These baselines have separate Git histories. The old history remains inspectable with `git log v0.0.0`; the new history with `git log v1.0.0`. The tags version the repository milestone; `agentic-core/plugin.json` has its own package version.

## Layout

- `factory/projection/`: explicit-source Codex, Copilot, and Claude Agent Plugin projectors and projection provenance.
- `expertise/`: the distinct Expertise Pack parser, PackIR, validators, and target compilers.
- `harness_factory/`: isolated harness capability detection, static validation, and bounded run adapters.
- `agentic-core/plugin.json`, `mcp.json`: installable Core plugin and its bundled MCP servers.
- `agentic-core/agents/*.md`: canonical portable Agentic Core agent sources.
- `agentic-core/com.github.copilot/agents/`: generated Copilot-compatible outputs; do not edit as source.
- `agentic-core/README.md`: GitHub App MCP Docker setup and agent access boundaries.
- `agentic-core/com.github.copilot/agents/`: Copilot agent definitions.
- `agentic-core/skills/`: discoverable domain skills, internal workflows, references, assets, and validation tools.
- `agentic-core/runtime/pluginctl/`: workspace plugin/profile lifecycle and materialization commands.
- `harness_factory/`: isolated Copilot/Codex capability detection, static validation, and bounded run adapters.
- `.github/copilot-instructions.md`: workspace-wide agent invariants and risk policy.

Additional vertical Expertise Packs remain separate from the Core package. Pack compilation remains separate from full-plugin projection.

## Codex custom agents

The canonical Core agents are portable Markdown in `agentic-core/agents/`. Factory generates target-specific Copilot and Codex agent files from that explicit plugin source. The packaged Core Codex command remains available for standalone runtime compatibility; its presence does not make packaged projection code the canonical Factory implementation. No runtime installation occurs during projection.

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
