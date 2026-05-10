# Graphify Copilot Workflow

This file is the canonical build, update, and query workflow for graphify in this repository.

Run all commands from the repository root and always use `uv run` so the repository-managed `graphifyy` installation is used.

## Input handling

- If no argument is provided, use `.`.
- If the argument starts with `query `, `path `, or `explain `, treat it as query mode and do not rebuild unless the graph is missing.
- Otherwise treat the argument as the target path to build or update.

## Query mode

1. Check that `graphify-out/graph.json` exists.
2. If the graph is missing, switch to build mode on `.` first.
3. Run the matching command with `uv run graphify ...`.
4. Summarize the result directly in chat.

Examples:

```bash
uv run graphify query "what connects skills to prompts?"
uv run graphify path "create-skill" "orchestrator"
uv run graphify explain "graphify"
```

## Build or update mode

### Step 1 - Ensure graphify is available

```bash
uv run python -c "import graphify; print('graphify-ok')"
```

If the import fails:

```bash
uv sync
```

Then retry the import check.

### Step 2 - Detect the corpus

```bash
uv run python -c "import json; from pathlib import Path; from graphify.detect import detect; root=Path('TARGET_PATH'); out=Path('graphify-out'); out.mkdir(exist_ok=True); result=detect(root); (out / '.graphify_detect.json').write_text(json.dumps(result, indent=2), encoding='utf-8'); total=result.get('total_files', 0); words=result.get('total_words', 0); print(f'Corpus: {total} files, ~{words} words'); [print(f'  {ftype}: {len(files)} files') for ftype, files in result.get('files', {}).items() if files]"
```

Replace `TARGET_PATH` with the actual requested path.

If important repository content lives under hidden directories such as `.github/` or `.vscode/`, allowlist those directories in `.graphifyinclude` before you run detection. `graphify.detect()` prunes hidden directories by default.

If no supported files are found, stop and say so.

### Step 3 - Structural extraction

```bash
uv run python -c "import json; from pathlib import Path; from graphify.extract import collect_files, extract; detect=json.loads(Path('graphify-out/.graphify_detect.json').read_text(encoding='utf-8')); code_files=[]; [code_files.extend(collect_files(p) if p.is_dir() else [p]) for f in detect.get('files', {}).get('code', []) for p in [Path(f)]]; result=extract(code_files) if code_files else {'nodes': [], 'edges': [], 'input_tokens': 0, 'output_tokens': 0}; Path('graphify-out/.graphify_ast.json').write_text(json.dumps(result, indent=2), encoding='utf-8'); print(f'AST: {len(result.get(\"nodes\", []))} nodes, {len(result.get(\"edges\", []))} edges')"
```

### Step 4 - Semantic cache check

```bash
uv run python -c "import json; from pathlib import Path; from graphify.cache import check_semantic_cache; detect=json.loads(Path('graphify-out/.graphify_detect.json').read_text(encoding='utf-8')); all_files=[f for files in detect.get('files', {}).values() for f in files]; cached_nodes, cached_edges, cached_hyperedges, uncached = check_semantic_cache(all_files); cached={'nodes': cached_nodes, 'edges': cached_edges, 'hyperedges': cached_hyperedges}; Path('graphify-out/.graphify_cached.json').write_text(json.dumps(cached, indent=2), encoding='utf-8'); Path('graphify-out/.graphify_uncached.txt').write_text('\n'.join(uncached), encoding='utf-8'); print(f'Cache: {len(all_files)-len(uncached)} hit, {len(uncached)} need extraction')"
```

If `uncached` is empty, skip to merge.

### Step 5 - Semantic extraction with Copilot subagents

Split uncached files into related chunks of roughly 10-20 files. Keep files from the same directory together when practical.

Dispatch all chunk subagents in parallel. Each subagent must:

1. Read only its assigned files.
2. Return only valid JSON with this schema:

```json
{"nodes": [], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
```

3. Apply these rules:
   - `EXTRACTED` for explicit relationships.
   - `INFERRED` for reasonable but indirect relationships.
   - `AMBIGUOUS` for uncertain relationships that should remain visible.
   - Code files should add semantic relationships AST extraction cannot provide and should not duplicate plain imports or calls already captured structurally.

Use the prompt template from [semantic-extraction-subagent-prompt.md](../assets/semantic-extraction-subagent-prompt.md), substituting `FILE_LIST`.

Collect all subagent JSON fragments in memory for merge. Do not ask the user to paste them.

### Step 6 - Merge extraction fragments

```bash
uv run python -c "import json; from pathlib import Path; ast=json.loads(Path('graphify-out/.graphify_ast.json').read_text(encoding='utf-8')); cached=json.loads(Path('graphify-out/.graphify_cached.json').read_text(encoding='utf-8')); chunks=CHUNK_JSON_LIST; nodes=list(ast.get('nodes', [])) + list(cached.get('nodes', [])); edges=list(ast.get('edges', [])) + list(cached.get('edges', [])); hyperedges=list(cached.get('hyperedges', [])); [nodes.extend(chunk.get('nodes', [])) or edges.extend(chunk.get('edges', [])) or hyperedges.extend(chunk.get('hyperedges', [])) for chunk in chunks]; merged={'nodes': nodes, 'edges': edges, 'hyperedges': hyperedges, 'input_tokens': sum(chunk.get('input_tokens', 0) for chunk in chunks), 'output_tokens': sum(chunk.get('output_tokens', 0) for chunk in chunks)}; Path('graphify-out/.graphify_extract.json').write_text(json.dumps(merged, indent=2), encoding='utf-8'); print(f'Merged: {len(nodes)} nodes, {len(edges)} edges')"
```

Replace `CHUNK_JSON_LIST` with the actual JSON list built from the subagent responses.

### Step 7 - Build graph and report

```bash
uv run python -c "import json; from pathlib import Path; from graphify.build import build_from_json; from graphify.cluster import cluster; from graphify.analyze import god_nodes, surprising_connections; from graphify.report import generate; from graphify.export import to_html; from networkx.readwrite import json_graph; extraction=json.loads(Path('graphify-out/.graphify_extract.json').read_text(encoding='utf-8')); G=build_from_json(extraction); communities=cluster(G); gods=god_nodes(G); surprises=surprising_connections(G, communities); Path('graphify-out/graph.json').write_text(json.dumps(json_graph.node_link_data(G), indent=2), encoding='utf-8'); report=generate(G, communities, {}, {}, gods, surprises, extraction); Path('graphify-out/GRAPH_REPORT.md').write_text(report, encoding='utf-8'); to_html(G, communities, 'graphify-out/graph.html'); print(f'Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities')"
```

### Step 8 - Surface the result

Read `graphify-out/GRAPH_REPORT.md` and report:

1. The top god nodes.
2. The top surprising connections.
3. Any knowledge gaps relevant to the user request.
4. Confidence framing from the report.

Also tell the user that MCP access is available through `.vscode/mcp.json`.