# Task history

Store append-only task status events in `docs/tasks-history/<task-id>.jsonl`; the latest valid event for a task ID determines its current status. Keep task definitions and dependency/acceptance mapping in the approved Planner plan, and keep orchestration decisions in the harness manifest/events.

Each transition records `task_id`, `attempt_id`, `agent_id`, `status`, UTC `timestamp`, evidence/result reference, and any blocker or next owner. The Orchestrator is the single writer. Native session todos are a live UI mirror compiled from the current plan, not a durable source of truth; create one todo per major task/phase and update it when the corresponding evidence is recorded.

On resume, reconcile every task still marked `running` with the host's available result/state. If no authoritative state is available, record `unknown`; do not infer completion, wait for an unsupported timer, or silently leave a zombie-looking task as running. Retry only as a new attempt after checking for partial writes and preserving prior events.
