---
name: graphify
description: "Explore any codebase, docs, PDFs, or media as a knowledge graph. Use when: starting a new project, mapping unfamiliar code, finding hidden dependencies, exploring cross-cutting concerns. Produces GRAPH_REPORT.md with god-nodes, surprising connections, and confidence-labeled (EXTRACTED/INFERRED) relationships. Requires graphify CLI (pip install graphifyy)."
user-invocable: false
---

# Graphify Skill

Source: https://github.com/safishamsi/graphify (MIT, Python, VS Code Copilot native)

Purpose: Build and query a knowledge graph over the project to accelerate exploration,
onboarding, and architectural understanding. All code extraction is local (tree-sitter,
no API cost). Docs/PDFs/images use an LLM backend.

# When to Invoke

- Starting work on an unfamiliar repository or module
- Before a large refactor (find hidden dependants via god nodes)
- When asked "what does X connect to?" or "show me the architecture"
- Before writing tests (graph reveals untested paths)

# Workflow

## Step 1 -- Check existing graph

Check whether `graphify-out/GRAPH_REPORT.md` exists.
- EXISTS: read it immediately with #tool:read_file. Skip to Step 3.
- MISSING: proceed to Step 2.

## Step 2 -- Build the graph

Run the appropriate extraction command:

```
# Code-only (fast, no API cost):
graphify extract <path>

# Code + docs (requires LLM backend):
graphify extract <path> --backend openai|claude|gemini

# VS Code Copilot integration (one-time, writes to VS Code user settings):
graphify vscode install
```

Use the official PyPI package `graphifyy` (double-y). The CLI command remains `graphify`.

Add a `.graphifyignore` file to exclude noise (node_modules, build artifacts,
migrations, generated files). See [.graphifyignore guide](./references/setup-guide.md).

Commit `graphify-out/` (excluding `manifest.json` and `cost.json`) so all agents
start with a pre-built map.

## Step 3 -- Read and interpret GRAPH_REPORT.md

Read `graphify-out/GRAPH_REPORT.md`. It contains:
- **God Nodes**: highest-degree nodes. These are the load-bearing concepts.
  Start any investigation here.
- **Surprising Connections**: cross-module links ranked by unexpectedness.
  Surface hidden dependencies.
- **Communities**: Leiden-clustered groups of related nodes with cohesion scores.
  Use as module boundaries for task scoping.
- **Knowledge Gaps**: nodes with missing outbound edges -- likely under-tested or
  undocumented areas.
- **Suggested Questions**: graph-generated onboarding questions. Use as prompts
  for deeper investigation.
- **Confidence stats**: ratio of EXTRACTED (directly found) vs INFERRED (deduced)
  edges. High INFERRED ratio means the graph has less certain areas.

## Step 4 -- Precision queries via MCP (optional)

If `.vscode/mcp.json` includes the graphify server, use MCP tools for precise queries:
- `query_graph`: keyword or semantic search over nodes and edges
- `get_node`: full metadata for a specific node (community, source file, confidence)
- `get_neighbors`: 1-hop neighborhood of a node
- `shortest_path`: dependency path between two nodes

MCP config: #file:../../../.vscode/mcp.json (see graphify entry)

## Step 5 -- Surface findings

Always report:
1. Top 3 god nodes with their community and degree
2. Top 2 surprising connections
3. Any knowledge gaps relevant to the current task
4. Confidence level (EXTRACTED% / INFERRED%)

Reference `graphify-out/GRAPH_REPORT.md` as a `#file:` in Copilot Chat for full context.

# Rules

- Never answer architecture questions without first reading GRAPH_REPORT.md.
- Do not rebuild the graph on every run -- check for existing output first.
- Label all findings with confidence: EXTRACTED or INFERRED.
- When using the graph for refactor scope, always check god nodes for blast radius.

# References

- [Setup guide and .graphifyignore patterns](./references/setup-guide.md)
- [Graph output file formats](./references/output-formats.md)
