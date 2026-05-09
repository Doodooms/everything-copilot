---
name: gitnexus
description: "Architecture impact analysis for AI agents. Use when: making changes to shared symbols, reviewing blast radius before a refactor, getting a 360-degree view of a component, or navigating unfamiliar code. Provides MCP tools: impact (blast-radius), context (360 view), detect_changes (git-diff impact). Requires GitNexus CLI (npx gitnexus). License: PolyForm Noncommercial."
user-invocable: false
---

# GitNexus Skill

Source: https://github.com/abhigyanpatwari/GitNexus (PolyForm Noncommercial, TypeScript)

Purpose: Give agents precomputed relational intelligence so no dependency is missed.
GitNexus indexes the full codebase into a graph DB (LadybugDB/KuzuDB) and exposes
16 MCP tools. The flagship tools are `impact` (blast-radius analysis) and `context`
(360-degree symbol view).

**License note**: PolyForm Noncommercial -- free for personal/research use;
commercial use requires a paid license from akonlabs.com.

# When to Invoke

- Before editing any shared symbol (function, class, API route)
- Before a refactor: understand what will break
- When exploring an unfamiliar codebase component
- When generating architecture documentation
- Pre-commit validation via `detect_changes`

# Workflow

## Step 1 -- Check index status

Check whether `.gitnexus/` exists in the repo root.
- EXISTS: skip to Step 3.
- MISSING: proceed to Step 2.

## Step 2 -- Bootstrap GitNexus

```
# Install and index (creates .gitnexus/ in repo, writes AGENTS.md):
npx gitnexus analyze

# Skip auto-written AGENTS.md if you have custom copilot-instructions.md:
npx gitnexus analyze --skip-agents-md

# Serve MCP server (for VS Code MCP client):
npx gitnexus mcp
```

The MCP server config is in `.vscode/mcp.json` (gitnexus entry). See
[MCP server setup](./references/mcp-setup.md).

## Step 3 -- Use the flagship MCP tools

All queries use the MCP tools defined in #file:./references/mcp-tools.md.

### Before any edit: `context`
Get a 360-degree view of the target symbol:
- Incoming calls (what depends on it)
- Outgoing calls (what it depends on)
- Processes it participates in (execution flows with step indices)
- Community cluster membership

### Before any refactor: `impact`
Get blast-radius analysis with depth grouping:
- `WILL BREAK`: direct callers/consumers (depth 1)
- `LIKELY AFFECTED`: indirect consumers (depth 2+)
- `confidence` score per affected node
Use `minConfidence` param to filter noise (recommend >= 0.7).

### Pre-commit: `detect_changes`
Map git diff to affected symbols and processes.
Returns `risk_level: low|medium|high` and a list of impacted processes.
Always run this before committing changes to shared modules.

### Architecture documentation: `generate_map` prompt
Generates Mermaid diagrams of the codebase architecture.
Invoke via the MCP prompt `generate_map` and embed output in docs.

## Step 4 -- Act on findings

After running `impact` or `context`:
1. List all WILL BREAK symbols -- these require test updates.
2. List LIKELY AFFECTED symbols -- review manually or add to test scope.
3. For high risk_level: escalate to Orchestrator before proceeding.
4. For rename operations: use the `rename` tool (multi-file, graph-aware).

## Step 5 -- Refresh after significant changes

```
# Incremental reindex (fast):
npx gitnexus analyze --incremental

# Full reindex:
npx gitnexus analyze
```

The index goes stale after commits. Refresh before each analysis session.

# Generated Skills Integration

GitNexus auto-generates skill files per community cluster under `.claude/skills/generated/`.
These are plain Markdown and should be ported to `.github/skills/<cluster-name>/SKILL.md`
with VS Code Copilot frontmatter. Each generated skill describes:
- Key files in the cluster
- Entry points and execution flows
- Cross-area connections

Run `npx gitnexus analyze --skills` then port generated skills to `.github/skills/`.

# Rules

- Always run `context` before editing a shared symbol.
- Always run `impact` before a refactor touching shared modules.
- Always run `detect_changes` before committing.
- Never ship high risk_level changes without Orchestrator review.
- Respect the PolyForm Noncommercial license for production/commercial use.

# References

- [MCP tools reference](./references/mcp-tools.md)
- [MCP server setup for VS Code](./references/mcp-setup.md)
