# Graph Patch Hook

The workspace hook lives at [.github/hooks/graph-patch.json](../../../hooks/graph-patch.json).

It runs two commands through the repository Python environment:

- `uv run python scripts/atomic_index.py hook-post-tool-use --db-path .graphify/lbug --graph-json graphify-out/graph.json`
- `uv run python scripts/atomic_index.py hook-stop --db-path .graphify/lbug --graph-json graphify-out/graph.json` at each `SubagentStop`
- `uv run python scripts/atomic_index.py hook-stop --db-path .graphify/lbug --graph-json graphify-out/graph.json`

Behavior boundary:

- Graphify is patched automatically after successful mutating tool calls.
- A final full reconciliation runs again when a subagent stops and when the top-level agent stops.
- GitNexus Claude `PostToolUse` semantics are adapted in `scripts/atomic_index.py`: successful terminal `git commit`, `merge`, `rebase`, `cherry-pick`, and `pull` calls compare `HEAD` against `.gitnexus/meta.json` and inject a stale-index notice into the conversation.
- GitNexus is never mutated unsafely when the installed CLI lacks a safe incremental path; pending drift is tracked instead.
