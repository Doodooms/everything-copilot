# agentic-workflow

This repository stores a deterministic GitHub Copilot workflow: skills, agents, prompts, instructions, hooks, and MCP configuration that can be reused across projects.

## Prerequisites

- VS Code with a compatible GitHub Copilot extension
- `uv`
- Python 3.10+
- Node.js 22.5+
- npm 9+

## Setup

From the repository root, run:

```bash
uv sync
npm install
```

This creates or updates the local `.venv` from [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock), then installs the pinned local Node-based AHK dependency from [package.json](package.json).

## Recommended Evolution Path

This repository is evolving toward an `everything-copilot` platform in phases. The current recommendation order is:

1. **AHK (`@cardor/agent-harness-kit`) is now integrated** as the orchestration backbone for backlog management, atomic task claiming, action journaling, health gates, and a dashboard.
2. **Re-evaluate CodeGraphContext only after an upstream fix** because the 0.4.7 candidate failed deep symbol-extraction validation and is not part of the active workspace surface.
3. **Keep GitNexus** as the retained code-impact and blast-radius layer.
4. **Keep Graphify on LadybugDB** as the retained documentation and semantic graph layer.
5. **Use the committed Dockerfile** when you want a reproducible packaged environment for the active workspace surface.
6. **Evaluate Bernstein and axiom-graph later** as follow-up additions, not first-wave dependencies.

Current state versus plan:

- Active today: AHK, Graphify, GitNexus, hooks, skills, prompts, instructions, uv-managed Python tooling, and a pinned local Node dependency for AHK.
- Quarantined candidate: CodeGraphContext 0.4.7 was removed from the active MCP surface after deep validation found successful indexing with zero extracted symbols.
- Packaged environment: [Dockerfile](Dockerfile) now builds the active workspace surface with uv, Node.js 24, npm, and the repository health gate.
- Planned next: any later watchlist tools.
- Source of truth: [.github/PLAN.md](.github/PLAN.md).

## AHK

This repository now integrates AHK locally through the pinned dependency in [package.json](package.json), the harness config in [agent-harness-kit.config.ts](agent-harness-kit.config.ts), and the operational backlog in [.harness/feature_list.json](.harness/feature_list.json).

The tracked Copilot-facing AHK runtime surface is:

- [agent-harness-kit.config.ts](agent-harness-kit.config.ts)
- [health.sh](health.sh)
- [.harness/feature_list.json](.harness/feature_list.json)
- [.vscode/mcp.json](.vscode/mcp.json)

AHK's current role in this workspace is operational, not strategic:

- AHK is the shared backlog, action journal, health gate, and MCP task surface.
- [.github/PLAN.md](.github/PLAN.md) remains the strategic source of truth for what exists and what is planned.
- `.github/tasks/` and `.github/plan_history/` remain the audit trail for orchestrated changes.

AHK itself currently supports `claude-code` and `opencode` providers in its config schema. This workspace keeps `provider: 'claude-code'` only to satisfy the package contract, while GitHub Copilot uses the manual MCP server registration in [.vscode/mcp.json](.vscode/mcp.json). Provider-materialized files from `ahk build` or `ahk init` are intentionally excluded from this repository; [health.sh](health.sh) fails if they appear.

Useful AHK commands from the repository root:

```bash
npm run ahk:health
npm run ahk:sync
npm run ahk:status
npm run ahk:dashboard
```

The workspace MCP registration starts AHK locally with:

```bash
npx --no-install ahk serve
```

The focused AHK integration test suite is:

```bash
uv run python -m unittest tests.test_ahk_integration
```

The broader active-tool stability battery is:

```bash
npm run test:workspace:stability
```

The focused Graphify raw-text retrieval battery is:

```bash
npm run test:graphify:fts
```

## CodeGraphContext Candidate

CodeGraphContext is not part of the active workspace integration.

Deep validation against the 0.4.7 release found multiple issues that make it unsafe to expose through the default MCP surface:

- indexing reported success while returning zero extracted functions, classes, and modules
- symbol queries such as `find_code` and `analyze_code_relationships` returned empty results for disposable repositories and the real workspace
- backend-selection behavior was inconsistent across the CLI and MCP server paths during fallback testing

Because of that, the workspace does not register CodeGraphContext in [.vscode/mcp.json](.vscode/mcp.json), the default health gate does not depend on it, and the operational backlog tracks only future revalidation after an upstream fix.

GitNexus remains the retained blast-radius layer, and Graphify remains the retained documentation and semantic knowledge graph layer.

## Graphify

This repository uses `graphifyy` as the semantic graph tool for workspace exploration. It is installed through the root uv project and is intended to map the repository's markdown-heavy orchestration content, not just its small amount of code.

Preferred mode in this repository: use the workspace `/graphify` prompt in Copilot Chat. That prompt uses GitHub Copilot itself as the semantic extraction backend, so no external API keys are required.

Build the graph in Copilot Chat with:

```text
/graphify .
```

That prompt lives in [.github/prompts/graphify.prompt.md](.github/prompts/graphify.prompt.md) and serves as the user-facing entrypoint to the canonical graphify workflow in [.github/skills/graphify/SKILL.md](.github/skills/graphify/SKILL.md).

Build the graph from the repository root:

```bash
uv run graphify extract . --backend <backend>
```

Use the headless command above only when you explicitly have external backend credentials configured. For this repository, most important content lives in `.md` files, so the Copilot-native `/graphify` prompt is the default path.

This repository now keeps Graphify's primary store in Ladybug at `.graphify/lbug`, maintains `graphify-out/graph.json` as a compatibility mirror, and keeps a repo-local SQLite FTS5 index at `.graphify/docs-fts.db` for raw-text retrieval over the same Graphify-tracked files.

Bootstrap or refresh the local Ladybug store from the current JSON graph with:

```bash
uv run python scripts/atomic_index.py migrate-graphify --force
```

Patch a single changed file into the Ladybug store without rebuilding the full Graphify graph with:

```bash
scripts/patch-graphify.sh README.md
```

That patch path updates `.graphify/lbug` first and then rewrites `graphify-out/graph.json` from the DB snapshot so existing JSON-based tooling can keep reading the mirror.

Search the raw-text index directly from the repository root with:

```bash
uv run python scripts/atomic_index.py search-docs "graph patch"
```

Automatic agent-time patching is enforced by the workspace hook at [.github/hooks/graph-patch.json](.github/hooks/graph-patch.json). It runs after successful mutating tool calls, again when each subagent stops, and again when the top-level agent stops, so Graphify stays patched continuously during agent and subagent editing without spawning a second model-driven subagent.

The same `hook-post-tool-use` command now adapts GitNexus's upstream Claude `PostToolUse` staleness check to GitHub Copilot's hook payload. After successful terminal `git commit`, `merge`, `rebase`, `cherry-pick`, or `pull` commands, it compares `HEAD` with `.gitnexus/meta.json` and injects a stale-index notice into the conversation when GitNexus still needs `analyze`.

If you want MCP tool access after the graph exists, the workspace MCP config starts graphify from the local uv environment with:

```bash
uv run python scripts/atomic_index.py serve-graphify --db-path .graphify/lbug
```

That same Graphify MCP server now exposes `search_docs` for FTS-backed raw-text retrieval alongside the existing graph tools.

`scripts/patch-gitnexus.sh` exists for the same workflow boundary, but it intentionally exits instead of mutating `.gitnexus/lbug` when the installed GitNexus CLI does not expose a safe incremental analyze path. It will not trigger a full rebuild implicitly, and the hook records pending or stale GitNexus drift instead.

For manual inspection or repair of the automatic workflow, use `uv run python scripts/atomic_index.py graph-patch-status` or `uv run python scripts/atomic_index.py reconcile-graphs`. `graph-patch-status` now reports both the Ladybug graph state and the SQLite text-index state. The workspace skill [.github/skills/graph-patch/SKILL.md](.github/skills/graph-patch/SKILL.md) documents that repair workflow.

Optional VS Code Copilot Chat integration:

```bash
uv run graphify vscode install
```

That command installs graphify's vendor-managed user-level Copilot skill. It is optional here because the repository already provides a workspace-local `/graphify` prompt.

## Daily usage

1. Open the repository in VS Code.
2. Read [.github/PLAN.md](.github/PLAN.md) for the repository structure and operating model.
3. Read [.github/copilot-instructions.md](.github/copilot-instructions.md) for always-on agent rules.
4. Run `npm run test:workspace:stability` when you want to validate the active workspace tool surface before agent work.
5. Use Copilot Chat with the repository skills, prompts, agents, and MCP servers.

## Running repository Python tooling

Prefer `uv run` so commands use the repository environment without manual activation.

Examples:

```bash
uv run python .github/skills/create-skill/scripts/validate_skill.py --skill-dir .github/skills/create-skill
uv run python -c "import typer, yaml, mcp"
```

If you prefer direct interpreter paths after syncing, `./.venv/bin/python` remains valid.

## Docker

This repository now includes a Docker build for the active workspace surface.

Build the image from the repository root with:

```bash
npm run docker:build
```

Validate the packaged workspace surface inside the built image with:

```bash
npm run docker:test:workspace:stability
```

Start an interactive shell in the packaged workspace with:

```bash
npm run docker:run
```

The image installs uv, Node.js 24, npm, syncs the Python environment from [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock), installs the pinned AHK dependency from [package.json](package.json), and runs [health.sh](health.sh) during the build.

## Updating dependencies

Use `uv` to modify the manifest, then refresh the lockfile.

```bash
uv add <package>
uv remove <package>
uv lock
uv sync
```

Commit both [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock) when dependencies change.

Use `npm` to modify the local AHK dependency surface.

```bash
npm install
npm install --save-dev @cardor/agent-harness-kit@<version>
```

Commit both [package.json](package.json) and `package-lock.json` when Node dependencies change.

Commit [Dockerfile](Dockerfile) and [.dockerignore](.dockerignore) when the packaged environment changes.

## Notes

- This repository is not published as a Python package. The root [pyproject.toml](pyproject.toml) exists to manage local tooling dependencies reproducibly.
- Current local tooling dependencies include `graphifyy`, `ladybug`, `mcp`, `pyyaml`, and `typer`.
- `uv sync` removes packages that are not declared in [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock).
- `npm install` installs the pinned local AHK dependency declared in [package.json](package.json).
- The committed AHK workspace files are [agent-harness-kit.config.ts](agent-harness-kit.config.ts), [health.sh](health.sh), [.harness/feature_list.json](.harness/feature_list.json), and [.vscode/mcp.json](.vscode/mcp.json). Provider-materialized files are intentionally excluded.
- CodeGraphContext is intentionally not registered in [.vscode/mcp.json](.vscode/mcp.json) until a future candidate passes the deep validation battery.
- `graphify` is managed by the root uv project in this repository.
- `gitnexus` remains an external prerequisite managed outside the root uv project; the workspace adapts the upstream hook semantics in Python, but does not declare a root PyPI dependency for GitNexus.
- `ahk` is managed as a pinned local Node development dependency and exposed to Copilot through [.vscode/mcp.json](.vscode/mcp.json).
- For markdown-heavy graphify runs without external API keys, use the workspace [/graphify prompt](.github/prompts/graphify.prompt.md).