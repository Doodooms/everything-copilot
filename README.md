# Everything Copilot

Everything Copilot is not an AI framework. It is the engineering layer for GitHub Copilot agent workflows in VS Code. It adds deterministic structure, mechanical validation, and context-aware dispatch so Copilot agents behave reliably, auditably, and scalably across projects.

This repository is the working reference implementation. It ships the core compiler skills, the validator layer that keeps them honest, the operational AHK and MCP integration, and the graph workflow used to keep the workspace explorable.

Current status: `create-skill`, `create-agent`, `create-mcp`, and their validator surfaces are stable. AHK, Graphify, GitNexus, Docker, and the `/init` entrypoint are operational. Broader memory, graph, and consumer-surface ideas remain under active design.

## What Is Stable Today

| Surface | Status | Role |
|---------|--------|------|
| `create-skill` | Stable | Creates deterministic skills with point-of-need loading and structural validation |
| `create-agent` | Stable | Creates custom agents with precise frontmatter, minimal tool surfaces, and explicit delegation |
| `create-mcp` | Stable | Creates MCP servers and validates their VS Code registration |
| Validator layer | Stable | Enforces structure, routing guardrails, duplicate-guidance control, and MCP config shape |
| AHK integration | Operational | Provides the task ledger, action journal, health gate, and MCP task surface |
| Graphify and GitNexus | Operational | Provide semantic exploration, raw-text retrieval, and blast-radius analysis |

## Why Deterministic Orchestration Matters

Most agent systems mix persona, workflow, and context into a single prompt. That leads to four recurring failures:

- Context pollution from loading too much material too early
- Dispatch drift when an agent responds outside its scope
- Weak recovery because the system relies on heuristics instead of checks
- Monolithic instructions that become impossible to maintain safely

Everything Copilot separates those concerns instead of blending them:

- Skills define how a repeatable workflow executes
- Agents define who executes it and which tools or subagents are allowed
- Prompts remain optional suggestions, not the control plane
- Validators provide mechanical governance instead of wishful prompting

## Design Principles

- Deterministic over heuristic
- Explicit over implicit
- Load late, not early
- Validate mechanically
- Minimize tool blast radius
- One concept, one canonical home

## Core Architecture

### Skills

A skill is a repeatable procedure. In this repository, a skill is a folder with a `SKILL.md` workflow plus support files under `assets/`, `references/`, and `scripts/`.

Key rules:

- A skill defines how to execute work, not a persona
- Support files are loaded only at the point of need
- The frontmatter `description` drives discovery, while the body drives execution

### Agents

An agent is a specialized persona with explicit tools, optional subagents, and invocation rules. It decides when to route to a skill and how to synthesize the result.

Key rules:

- Every new agent includes a Step 0 confirmation that rejects out-of-scope work
- Tool lists stay minimal because every extra tool widens the blast radius
- Delegation is explicit and validated instead of informal

### Prompts

A prompt is reusable guidance that may be included conditionally. Prompts are suggestions, not deterministic orchestration surfaces.

### MCP Servers

MCP servers expose tools, resources, prompts, and related capabilities through a standard interface over stdio or remote transport.

Design rules in this repository:

- Prefer Go or Rust for production-oriented servers
- Use Python for fast prototypes or repo-local tooling
- Allow Node.js only when the ecosystem or task requires it
- Keep transport wiring thin and the validation path explicit

### Validators And Governance

The validators are the core differentiator in this repository. They do not just check formatting; they enforce architectural constraints.

### Memory, Graphs, And External Context

The broader direction is a layered context system:

- Native Copilot memory where the platform provides it
- Repository-local notes under `.memory/`
- Graphify for semantic and raw-text retrieval over the workspace
- GitNexus for code-impact and blast-radius analysis

The long-term graph and memory architecture is still evolving, but the operational surfaces above already exist in this repository.

## Mechanical Validation

The repository ships regression-tested validators for the most important compiler surfaces:

- Invalid or missing frontmatter on skills, agents, prompts, and MCP configuration
- Unsupported tool names or invalid tool aliases
- Missing Step 0 confirmation or malformed agent body structure
- Eager loading and front-loading of support files instead of point-of-need reads
- Duplicate guidance between canonical files and support docs
- Missing or stale support-file references from `SKILL.md`
- Invalid create-surface package layout for skills such as `create-skill`, `create-agent`, and `create-mcp`
- Invalid `.vscode/mcp.json` server shape, including malformed local or remote server entries

These checks are regression-tested in [tests/test_validate_skill.py](tests/test_validate_skill.py), [tests/test_validate_agent.py](tests/test_validate_agent.py), [tests/test_validate_prompt.py](tests/test_validate_prompt.py), and [tests/test_validate_mcp.py](tests/test_validate_mcp.py).

## Why XML For Workflows?

The repository uses XML-style wrapper tags for control surfaces and Markdown for prose.

- XML gives explicit boundaries. A closing tag such as `</workflow>` is unambiguous in a way Markdown headings are not.
- XML is extraction-safe for downstream orchestration and validation.
- XML does not conflict with Markdown prose, code blocks, or heading hierarchies.
- JSON remains the right format for strict payloads and tool-call data.

Repository convention: structural wrapper tags such as `<definitions>`, `<workflow>`, and `<rules>` stay attribute-free. Priority is expressed by ordering and wording such as MUST, ONLY, and NEVER.

## Real Workflow Example

Typical path for an implementation task in this repository:

```text
User request
	|
	v
/init or orchestrator routing
	|
	v
Plan or manifest generation
	|
	v
User review or approval
	|
	v
Implementation agent or builder flow
	|
	v
Validator and review pass
	|
	v
Documentation and close-out
```

When the `ahk` MCP server is connected, the task is also recorded in the operational ledger under `.harness/` while `.github/PLAN.md`, `.github/tasks/`, and `.github/plan_history/` remain the strategic and audit source of truth.

## Repository Layout

```text
everything-copilot/
|-- .github/
|   |-- agents/
|   |-- hooks/
|   |-- instructions/
|   |-- prompts/
|   |-- skills/
|   `-- PLAN.md
|-- .harness/
|-- .memory/
|-- .vscode/
|   `-- mcp.json
|-- scripts/
|-- tests/
|-- tools/
|-- Dockerfile
|-- agent-harness-kit.config.ts
|-- health.sh
`-- README.md
```

## Setup

### Prerequisites

- VS Code with a compatible GitHub Copilot extension
- `uv`
- Python 3.10+
- Node.js 22.5+
- npm 9+

### Quick Start

From the repository root, run:

```bash
uv sync
npm install
```

This creates or updates the local `.venv` from [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock), then installs the pinned local Node-based AHK dependency from [package.json](package.json).

Then open the repository in VS Code and use `/init` in Copilot Chat to enter the workspace orchestration flow.

## Current Operational Surfaces

### AHK

This repository integrates AHK locally through [package.json](package.json), [agent-harness-kit.config.ts](agent-harness-kit.config.ts), and [.harness/feature_list.json](.harness/feature_list.json).

Tracked Copilot-facing AHK runtime surface:

- [agent-harness-kit.config.ts](agent-harness-kit.config.ts)
- [health.sh](health.sh)
- [.harness/feature_list.json](.harness/feature_list.json)
- [.vscode/mcp.json](.vscode/mcp.json)

AHK's role here is operational, not strategic:

- AHK is the shared backlog, action journal, health gate, and MCP task surface
- [.github/PLAN.md](.github/PLAN.md) remains the strategic source of truth
- `.github/tasks/` and `.github/plan_history/` remain the audit trail for orchestrated changes

AHK currently supports `claude-code` and `opencode` providers in its config schema. This workspace keeps `provider: 'claude-code'` only to satisfy the package contract, while GitHub Copilot uses the manual MCP server registration in [.vscode/mcp.json](.vscode/mcp.json). Provider-materialized files from `ahk build` or `ahk init` are intentionally excluded from this repository; [health.sh](health.sh) fails if they appear.

Useful commands from the repository root:

```bash
npm run ahk:health
npm run ahk:sync
npm run ahk:status
npm run ahk:dashboard
npx --no-install ahk serve
```

Focused validation:

```bash
uv run pytest tests/test_ahk_integration.py -q
npm run test:workspace:stability
```

### Graphify And GitNexus

This repository uses `graphifyy` as the semantic graph tool for workspace exploration. It is installed through the root uv project and is intended to map the repository's Markdown-heavy orchestration content, not just its small amount of code.

Preferred mode in this repository: use the workspace `/graphify` prompt in Copilot Chat. That prompt uses GitHub Copilot itself as the semantic extraction backend, so no external API keys are required.

```text
/graphify .
```

That prompt lives in [.github/prompts/graphify.prompt.md](.github/prompts/graphify.prompt.md) and serves as the user-facing entrypoint to the canonical Graphify workflow in [.github/skills/graphify/SKILL.md](.github/skills/graphify/SKILL.md).

Headless build path from the repository root:

```bash
uv run graphify extract . --backend <backend>
```

Use the headless command only when external backend credentials are configured.

This repository keeps Graphify's primary store in Ladybug at `.graphify/lbug`, maintains `graphify-out/graph.json` as a compatibility mirror, and keeps a repo-local SQLite FTS5 index at `.graphify/docs-fts.db` for raw-text retrieval over the same Graphify-tracked files.

Useful commands:

```bash
uv run python scripts/atomic_index.py migrate-graphify --force
scripts/patch-graphify.sh README.md
uv run python scripts/atomic_index.py search-docs "graph patch"
uv run python scripts/atomic_index.py serve-graphify --db-path .graphify/lbug
uv run python scripts/atomic_index.py graph-patch-status
uv run python scripts/atomic_index.py reconcile-graphs
```

Automatic patching is enforced by [.github/hooks/graph-patch.json](.github/hooks/graph-patch.json). The same workflow boundary also tracks GitNexus staleness after mutating Git commands. GitNexus remains the retained blast-radius layer, while Graphify remains the retained semantic and raw-text exploration layer.

Focused validation:

```bash
npm run test:graphify:fts
```

### CodeGraphContext Status

CodeGraphContext is not part of the active workspace integration.

Deep validation against the 0.4.7 release found multiple issues that make it unsafe to expose through the default MCP surface:

- indexing reported success while returning zero extracted functions, classes, and modules
- symbol queries such as `find_code` and `analyze_code_relationships` returned empty results for disposable repositories and the real workspace
- backend-selection behavior was inconsistent across the CLI and MCP server paths during fallback testing

Because of that, the workspace does not register CodeGraphContext in [.vscode/mcp.json](.vscode/mcp.json), the default health gate does not depend on it, and the operational backlog tracks only future revalidation after an upstream fix.

## Daily Usage

1. Open the repository in VS Code.
2. Read [.github/PLAN.md](.github/PLAN.md) for the repository structure and operating model.
3. Read [.github/copilot-instructions.md](.github/copilot-instructions.md) for always-on agent rules.
4. Run `npm run test:workspace:stability` when you want to validate the active workspace tool surface before agent work.
5. Use Copilot Chat with the repository skills, prompts, agents, and MCP servers.

## Running Repository Python Tooling

Prefer `uv run` so commands use the repository environment without manual activation.

Examples:

```bash
uv run python .github/skills/create-skill/scripts/validate_skill.py --skill-dir .github/skills/create-skill
uv run python -c "import typer, yaml, mcp"
```

If you prefer direct interpreter paths after syncing, `./.venv/bin/python` remains valid.

## Docker

This repository includes a Docker build for the active workspace surface.

```bash
npm run docker:build
npm run docker:test:workspace:stability
npm run docker:run
```

The image installs uv, Node.js 24, npm, syncs the Python environment from [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock), installs the pinned AHK dependency from [package.json](package.json), and runs [health.sh](health.sh) during the build.

## Updating Dependencies

Use `uv` to modify the Python manifest, then refresh the lockfile.

```bash
uv add <package>
uv remove <package>
uv lock
uv sync
```

Commit both [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock) when Python dependencies change.

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
- `graphify` is managed by the root uv project in this repository.
- `gitnexus` remains an external prerequisite managed outside the root uv project; the workspace adapts the upstream hook semantics in Python, but does not declare a root PyPI dependency for GitNexus.
- `ahk` is managed as a pinned local Node development dependency and exposed to Copilot through [.vscode/mcp.json](.vscode/mcp.json).
- For Markdown-heavy Graphify runs without external API keys, use the workspace [/graphify prompt](.github/prompts/graphify.prompt.md).