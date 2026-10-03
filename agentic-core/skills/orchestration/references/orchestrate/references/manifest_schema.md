# Legacy orchestration exchange schema

The Control Plane is the sole owner of durable Task, Attempt, event, artifact, replay, lease, and provenance state. This schema, its examples, and helper support explicitly requested legacy exchange or validation artifacts only; they do not define active local task storage. Agentic Core MUST NOT create these repository-local files as a substitute for Control Plane state. Workflows that do not depend on durable task state proceed with local tools and the active handoff/session.

Do not request absolute paths to these files. Use the schemas only when a concrete task supplies or explicitly asks to validate a legacy artifact.

## File ownership

| Path | Owner | Source of truth |
|---|---|---|
| `docs/harness-history/<task-id>/manifest.json` | Legacy exchange format | Historical specification reference, phase/gate status, lifecycle pointers, and derived-artifact links |
| `docs/harness-history/<task-id>/events.jsonl` | Legacy exchange format | Historical decisions and specialist handoff summaries |
| `docs/planner-history/<task-id>/plan-r<revision>.md` | Legacy exchange format | Historical task definitions, dependency DAG, file scopes, phase checks, and validation plan |
| `docs/tasks-history/<task-id>.jsonl` | Legacy exchange format | Historical task-status and attempt transitions |

For a supplied legacy artifact set, the manifest references its plan revision and task ledger. Do not copy plan/task descriptions into the manifest or duplicate full specification text into event records. These references describe the legacy exchange format only.

When explicitly producing or validating a legacy exchange artifact, validate it against the matching JSON Schema in [`../schemas/`](../schemas/) before passing it to another owner. The schemas define that exchange format; they do not authorize local persistence as active task state. Existing pre-schema history remains historical input and is not silently rewritten.

## Manifest

```json
{
  "id": "task_1",
  "title": "Change summary",
  "description": "Approved objective and bounded scope",
  "status": "in_progress",
  "base_revision": null,
  "specification": {
    "id": "SPEC-1",
    "revision": 1,
    "status": "ready",
    "requirements": ["REQ-1"],
    "acceptance_criteria": ["AC-1"],
    "path": "todos/in_progress/task/spec.md"
  },
  "architecture_ref": null,
  "plan_ref": {
    "path": "docs/planner-history/task_1/plan-r1.md",
    "revision": 1,
    "spec_revision": 1,
    "status": "approved"
  },
  "task_events_ref": "docs/tasks-history/task_1.jsonl",
  "selected_phases": [],
  "skipped_phases": [],
  "open_blockers": [],
  "lifecycle": {
    "branch": null,
    "worktree": null,
    "commit_shas": [],
    "pull_request": null,
    "cleanup": "not_requested",
    "commit_status": "not_applicable",
    "commit_reason": "No commit is part of this task."
  },
  "updated_at": "UTC ISO-8601 timestamp"
}
```

`status` is `planned | in_progress | success | partial | failed | blocked`. `lifecycle.commit_shas` contains Git object IDs only; `lifecycle.commit_status` and `commit_reason` explain why no commit exists. Omit other fields that do not apply; never fabricate a branch, worktree, PR, commit, or validation result. Include detailed SDD requirement objects in the manifest only when required; otherwise reference an approved source document by path/revision. When `base_revision` or lifecycle commits are present, pass the local repository to the validator so those references resolve to commit objects.

For newly proposed branches, the Orchestrator may add `lifecycle.branch_naming` with the accepted semantic category and policy source/version/digest. This provenance is optional and additive; existing manifest branch strings remain valid historical data and are not retroactively checked against current policy.

The persisted `manifest.json` wrapper has its own `manifest-record.schema.json`: `task_id` and `status` must match the enclosed manifest. The validator accepts the wrapper with `--kind manifest` for convenience or `--kind manifest-record` to validate the storage envelope explicitly.

## Orchestration event

Append one JSON object per line to `events.jsonl`. Each event MUST include:

- `task_id`, `timestamp` (UTC ISO-8601), `type`, and observed `status`.
- Relevant `spec_revision`, `plan_revision`, `agent_id`, and unique `attempt_id` inside the schema-defined `data` object.
- Bounded handoff/result references, evidence paths or commands, changed files, and commit SHAs.
- Deviations, blockers, next owner, and exact resume point when applicable.

Store structured specialist return fields needed for audit, not duplicated plan/spec prose or entire tool transcripts.

## Planner plan

Each `plan-rN.md` MUST identify `task_id`, plan revision, consumed spec/architecture revisions, requirement/acceptance/decision IDs, phases, and task DAG. Each task records:

- `TASK-*` ID, objective, owner/custom agent, bounded files/components, and expected output.
- Dependencies and safe parallel group; the dependency graph MUST be acyclic.
- Validation evidence, separate phase exit checks, risk, and next handoff.

Product acceptance remains specification-owned. The plan MUST NOT change or weaken it.

## Task status event

For a supplied legacy task-history artifact, each line is one JSON object. New exchange records include `schema_version` and `event_id` and validate against `task-transition.schema.json`:

```json
{
  "schema_version": "1.0.0",
  "event_id": "00000000-0000-4000-8000-000000000001",
  "parent_task_id": "task_1",
  "task_id": "TASK-1",
  "attempt_id": "attempt-1",
  "agent_id": "implementer",
  "status": "running",
  "timestamp": "UTC ISO-8601 timestamp",
  "evidence": []
}
```

Allowed statuses: `planned`, `queued`, `running`, `completed`, `partial`, `failed`, `blocked`, `unknown`, `cancelled`. An attempt follows observed transitions; terminal failures are retained, and retry starts a new `attempt_id`. Every outcome references actual evidence or the observed reason no result exists. Do not interpret time elapsed alone as proof of crash; when a session resumes and the host cannot establish a `running` attempt's state, append `unknown`.

Native todos support active-session work tracking. Update a todo from observed progress and do not mark completion before evidence exists.

The packaged `orchestrator.py` helper only proposes a repository-approved branch name; it has no task-state persistence commands. For a handoff file explicitly supplied for validation, call the packaged `validate_exchange.py --kind handoff --input <packet.json>` and retain the result with the consuming workflow.

## GitHub and hooks

The official custom-agent schema does not define a `github:` YAML key. Configure GitHub access using tools/MCP servers supported by the selected harness; an enabled GitHub tool does not transfer lifecycle ownership from the Orchestrator.

Hooks are harness- and event-specific. They MAY record a supported event, but MUST NOT be treated as a recurring timer, guaranteed heartbeat, or guaranteed crash notification. Verify hook support and payload against the active harness before authoring one.
