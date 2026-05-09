# GitNexus MCP Tools Reference

Source: https://github.com/abhigyanpatwari/GitNexus/blob/main/ARCHITECTURE.md

## 16 MCP Tools

### Core Analysis Tools

#### `context` -- 360-degree symbol view
Input: `{ "symbol": "UserService", "repo": "my-repo" }`
Returns:
- `incoming_calls`: list of symbols that call the target
- `outgoing_calls`: list of symbols the target calls
- `processes`: execution flows the symbol participates in (with step index)
- `community`: cluster membership and cohesion score
- `imports`: what the symbol imports

Use before any edit to understand dependencies.

#### `impact` -- blast-radius analysis
Input: `{ "symbol": "UserService", "repo": "my-repo", "depth": 3, "minConfidence": 0.7 }`
Returns:
- `WILL_BREAK`: depth-1 direct dependants (must update)
- `LIKELY_AFFECTED`: depth 2+ indirect dependants (review required)
- `confidence`: score per affected node

#### `query` -- hybrid search
Input: `{ "q": "authentication token validation", "repo": "my-repo" }`
Returns: process-grouped results (BM25 + semantic + RRF fusion, grouped by execution flow)

#### `detect_changes` -- git-diff impact
Input: `{ "repo": "my-repo" }` (uses current git diff)
Returns:
- `changed_symbols`: list of modified functions/classes
- `affected_processes`: execution flows touching changed symbols
- `risk_level`: `low` | `medium` | `high`

### Rename and Refactor

#### `rename` -- graph-aware multi-file rename
Input: `{ "symbol": "UserService", "new_name": "AccountService", "dry_run": true }`
Returns: list of files that would be changed, then executes if `dry_run: false`

### API and Route Analysis

#### `api_impact` -- pre-change impact for route handlers
Input: `{ "route": "/api/users/:id", "method": "GET" }`
Returns: handler chain, consumers, downstream effects

#### `route_map` -- API route to handler mappings
Input: `{ "repo": "my-repo" }`
Returns: full map of routes -> handlers -> consumers

#### `shape_check` -- response shape validation
Input: `{ "handler": "getUserById" }`
Returns: mismatch between response shape and consumer property accesses

### Multi-repo Group Tools

#### `group_list` / `group_sync` / `group_contracts` / `group_query` / `group_status`
Used for tracking contracts and querying execution flows across multiple repositories.

### Raw Access

#### `cypher` -- raw graph query
Input: `{ "query": "MATCH (f:Function)-[:CALLS]->(g:Function) RETURN f.name, g.name LIMIT 10" }`
Direct Cypher query against LadybugDB (KuzuDB).

### Discovery

#### `list_repos` -- list indexed repositories
Input: `{}`
Returns: all repos registered in the global registry (`~/.gitnexus/registry.json`)

## MCP Resources (read-only, instant)

- `gitnexus://repos` -- all indexed repos
- `gitnexus://repo/{name}/context` -- high-level repo context
- `gitnexus://repo/{name}/clusters` -- functional area overview (community clusters)
- `gitnexus://repo/{name}/processes` -- execution flow list
- `gitnexus://repo/{name}/schema` -- LadybugDB schema for this repo

## MCP Prompts

- `detect_impact` -- guided pre-commit analysis workflow
- `generate_map` -- generates Mermaid architecture diagram from graph
