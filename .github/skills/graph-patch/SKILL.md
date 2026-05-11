---
name: graph-patch
description: "What: Inspect, reconcile, and repair the automatic Graphify and GitNexus patch workflow for this workspace. When to use: Graphify Ladybug state is missing or stale, the graph patch hook needs verification, you need to force a full patch reconciliation after edits, or you need to inspect pending or stale GitNexus drift after git mutations. Do not use for: ordinary repository exploration, the /graphify semantic extraction workflow, or general hook authoring."
user-invocable: false
compatibility: vscode 1.119.0+, github-copilot 1.119.0+
---

# Graph Patch

## WHEN TO USE

- Checking whether the automatic graph patch hook is active and current
- Repairing Graphify after edits when the hook did not run or the DB is missing
- Inspecting whether GitNexus is stale after git mutations or because incremental patching is unsupported
- Forcing a full graph patch reconciliation without rebuilding Graphify from scratch

## WHEN NOT TO USE

- Building or refreshing the semantic graph from scratch with `/graphify .`
- General repository exploration or MCP querying
- Editing hook policy files themselves

<definitions>

- **graph patch hook** : The workspace hook described in [hook behavior](./references/hook-behavior.md) that runs after successful tool calls and again when the agent stops.
- **GitNexus drift** : Files changed since the last known GitNexus graph state, or a stale `.gitnexus/meta.json` commit marker after a successful terminal `git commit`, `merge`, `rebase`, `cherry-pick`, or `pull`.

</definitions>

<workflow>

## Step 1 - Inspect automatic patch status

Use #tool:execute to run `uv run python scripts/atomic_index.py graph-patch-status` from the repository root.
If `graphify_db_exists=false` and `graphify_json_exists=true`, continue to Step 2.
If `gitnexus_pending_files` is non-zero or `gitnexus_stale=true`, continue to Step 3.
If `last_hook_errors` is non-zero, use #tool:read on #file:./references/hook-behavior.md before Step 3 so you can confirm the workspace hook wiring.

## Step 2 - Bootstrap Graphify patch state

Use #tool:execute to run `uv run python scripts/atomic_index.py migrate-graphify --force` only when the Ladybug DB is missing and the compatibility mirror still exists.
If both the Ladybug DB and `graphify-out/graph.json` are missing, stop and tell the user to run `/graphify .` first.

## Step 3 - Reconcile graphs without a full rebuild

Use #tool:execute to run `uv run python scripts/atomic_index.py reconcile-graphs` from the repository root.
Treat Graphify as reconciled only if the command exits successfully.
Treat any non-zero `gitnexus_pending_files` count or `gitnexus_stale=true` afterwards as an honest signal that GitNexus still needs `analyze`; do not claim GitNexus is current when the CLI cannot patch it safely.

## Step 4 - Summarize the boundary clearly

Report whether the workspace hook is present, whether Graphify is current, and whether GitNexus has pending drift or a stale commit marker.
If GitNexus pending drift or stale state remains, explain that the hook is adapting GitNexus's upstream `PostToolUse` stale-index detection while refusing to mutate `.gitnexus/lbug` unsafely.

</workflow>

<rules>

- The hook, not the skill, is the enforcement surface for automatic graph patching.
- Never trigger a full GitNexus rebuild implicitly.
- Never describe GitNexus as current when `gitnexus_pending_files` is non-zero or `gitnexus_stale=true`.
- Use `reconcile-graphs` before proposing manual per-file Graphify patch commands.

</rules>
