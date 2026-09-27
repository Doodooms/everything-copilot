# Harness history

One directory per task ID: `<task-id>/manifest.json` is the current orchestration state; `<task-id>/events.jsonl` is the append-only orchestration/handoff audit.

The manifest owns approved intent, selected phases, current artifact references, and lifecycle pointers. Each event records a timestamp, event type, attempt/agent IDs where applicable, explicit status, evidence references, changed files/commit SHAs, deviations, and next action. Update the manifest atomically and append events rather than overwriting prior decisions.

This directory is the orchestration record, not a second planner or task-state store. Plans live in `docs/planner-history/`; task status transitions live in `docs/tasks-history/`. The manifest references their current revision/path.
