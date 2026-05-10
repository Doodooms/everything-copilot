---
name: graphify
description: "What: Build, update, query, and interpret a graphify knowledge graph for this workspace. When to use: mapping an unfamiliar repository, graphify-out is missing or stale, /graphify is invoked, or you need cross-cutting dependency and concept discovery. Do not use for: prompt or skill authoring, or one-off file reads that do not need graph construction."
user-invocable: false
context: fork
compatibility: vscode 1.119.0+, github-copilot 1.119.0+
---

# Graphify Skill

Source: https://github.com/safishamsi/graphify (MIT, Python, VS Code Copilot native)

Purpose: Build and query a knowledge graph over the project to accelerate exploration,
onboarding, and architectural understanding. All code extraction is local (tree-sitter,
no API cost). For markdown-heavy repositories without external API keys, the user-facing [/graphify prompt](../../prompts/graphify.prompt.md) should delegate here and this skill owns the canonical workflow.

## WHEN TO USE

- Starting work on an unfamiliar repository or module
- Before a large refactor (find hidden dependants via god nodes)
- When asked "what does X connect to?" or "show me the architecture"
- Before writing tests (graph reveals untested paths)
- When the workspace `/graphify` prompt is invoked

## WHEN NOT TO USE

- Editing a skill, prompt, agent, or MCP server definition
- Reading a single known file when graphify output would add no value

<definitions>

- **graph state** : The current presence and freshness of `graphify-out/graph.json` and `graphify-out/GRAPH_REPORT.md` for the requested path.
- **Copilot workflow** : The no-key graphify path where GitHub Copilot handles semantic extraction and local `graphifyy` handles detect, AST extraction, build, report, and HTML export.

</definitions>

<workflow>

## Step 1 -- Check existing graph

Check whether `graphify-out/GRAPH_REPORT.md` exists for the requested path.
- EXISTS and the user asked for interpretation or query only: use #tool:read on the existing report and skip to Step 5.
- MISSING or the user explicitly asked to rebuild or update: proceed to Step 2.

## Step 2 -- Bootstrap graphify tooling

If you need repository-specific setup details, use #tool:read on #file:./references/setup-guide.md
Use #tool:execute to verify graphify is available from the repo environment with `uv run python -c "import graphify; print('graphify-ok')"`.
If the import fails, run `uv sync` from the repository root and retry the same import check.

## Step 3 -- Execute the canonical graphify workflow

Use #tool:read on #file:./references/copilot-workflow.md and follow the relevant mode from that file.
Use #tool:read on #file:./assets/semantic-extraction-subagent-prompt.md when dispatching semantic extraction subagents.
Use #tool:execute for the local graphify commands described there.
Use #tool:agent to run the semantic extraction subagents in parallel when the workflow reaches the semantic extraction step.
Use the Copilot workflow as the default for this repository when external backend credentials are not configured.
Use headless `uv run graphify extract ... --backend ...` only when explicit backend credentials are available.

## Step 4 -- Confirm durable outputs

Use #tool:read on #file:./references/output-formats.md if you need the output contract
Ensure the workflow produced the durable outputs `graphify-out/graph.json`, `graphify-out/GRAPH_REPORT.md`, and `graphify-out/graph.html`.
Do not keep temporary chunk files after merge.

## Step 5 -- Read and interpret GRAPH_REPORT.md

Use #tool:read on the generated `graphify-out/GRAPH_REPORT.md`.
Always surface:
1. Top 3 god nodes with their community and degree.
2. Top 2 surprising connections.
3. Any knowledge gaps relevant to the current task.
4. Confidence framing from the report.

## Step 6 -- Mention query and MCP follow-up

If the user wants deeper follow-up, use the graphify query, path, or explain commands from the canonical workflow.
Mention that MCP access is available through [.vscode/mcp.json](../../../.vscode/mcp.json) once `graphify-out/graph.json` exists.

 </workflow>

<rules>

- Never answer architecture questions without first reading GRAPH_REPORT.md.
- Do not rebuild the graph on every run -- check for existing output first.
- The canonical graphify workflow lives in #file:./references/copilot-workflow.md and must not be duplicated in prompts.
- Label all findings with confidence: EXTRACTED or INFERRED.
- When using the graph for refactor scope, always check god nodes for blast radius.
 </rules>
