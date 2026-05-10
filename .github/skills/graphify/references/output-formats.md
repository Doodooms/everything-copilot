# Graphify Output Formats

`graphifyy` produces a small set of durable outputs under `graphify-out/`.

## Primary outputs

- `graph.json` -- node-link JSON representation of the knowledge graph. This is the file served by the graphify MCP server.
- `GRAPH_REPORT.md` -- plain-language architecture report with god nodes, surprising connections, communities, and confidence framing.
- `graph.html` -- interactive visualization for manual inspection.

## Intermediate outputs

- `.graphify_detect.json` -- corpus detection summary used during build and update runs.
- `.graphify_ast.json` -- structural extraction output from local AST analysis.
- `.graphify_cached.json` -- semantic fragments restored from graphify cache.
- `.graphify_extract.json` -- merged extraction payload used to build the final graph.
- `.graphify_uncached.txt` -- files that still need semantic extraction.

## Usually ignored

- `manifest.json` -- local change tracking for incremental runs.
- `cost.json` -- token and cost accounting when external backends are used.
- `cache/` -- graphify semantic cache.

Commit the primary outputs when you want a prebuilt graph available to future agents. Ignore the cache and bookkeeping files unless you are actively debugging the graphify pipeline.