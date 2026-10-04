# Artifact Lifecycle

## Control Plane task state and artifact lifecycle

The Control Plane owns durable Task, Attempt, events, artifacts, replay, leases, and provenance. Use its task state and artifact lifecycle when connected and when the concrete workflow depends on durable coordination. Agentic Core provides instruction and projection content; it MUST NOT create local files as a substitute durable store. For workflows that do not depend on durable task state, carry the specification and evidence in the active handoff/session and proceed with local repository tools.

The packaged validator remains available for an explicitly supplied task-state artifact in its supported format. It accepts either the task-state wrapper with a `manifest` object or the manifest itself. It is structural validation, not evidence of technical correctness, and it is not a requirement to create a local manifest.

`PYTHONDONTWRITEBYTECODE=1 python scripts/validate_sdd_state.py <supplied-state-artifact>` accepts either the task-state wrapper with a `manifest` object or the manifest itself. The validator path is relative to this skill's root, as specified in the [Agent Skills script-path guidance](https://agentskills.io/skill-creation/using-scripts). Run it only when such an artifact is part of the concrete workflow; do not request an absolute local state path to satisfy the validator.

## Stable IDs and revisions

- When a Control Plane specification exists, `SPEC-*` identifies it across integer `revision` values; `SPEC-001@rev2` is the second immutable view. Standalone local workflows may carry their request and evidence in the active handoff/session and must not invent durable specification, requirement, acceptance, task, QA, or review IDs.
- Use stable trace IDs for artifacts that exist; consume Control Plane `TASK-*` IDs when supplied and do not invent them for standalone local work.
- Retain an ID only while its meaning remains stable. Materially changed intent gets a new revision and updated affected IDs.
- Every derived durable artifact records the specification revision and relevant IDs it consumes when those Control Plane artifacts exist. Local handoffs state the concrete scope and evidence without fabricating IDs.
- QA evidence additionally records the implementation revision; durable Reviewer approval additionally records the exact QA run and implementation revision when those Control Plane artifacts exist.
- A reusable validation record SHOULD identify its check/command, subject code revision, relevant environment, result, producer, and scope. Reuse it only while its subject revision, target, and relevant environment remain unchanged.
- The Orchestrator records assigned `risk_level` (`L0`–`L3`) and selected `required_gates` in Control Plane task state when connected. Specialists consume that level and may escalate from new evidence; they do not reclassify it.

## Dependency-aware invalidation

Material changes flow downstream, not backward:

```text
specification → architecture → plan → tasks → implementation → QA → review
```

The validator's `--invalidate` operation marks downstream artifacts stale on a copy and emits JSON; it never writes the supplied artifact. It preserves `architecture.status: not_required` when specification changes do not create an architecture requirement. When exact impact is known to be narrower, invalidate only affected artifacts; when uncertain, use the conservative dependency set.

Examples:

- A changed requirement invalidates affected architecture, plan, tasks, implementation evidence, QA, and review.
- A changed architecture decision invalidates affected plan, task, implementation, QA, and review.
- A sequencing-only plan change can preserve implementation only when the Orchestrator records that no behavior or ownership dependency changed.
- A QA-only test improvement does not invalidate specification, architecture, or plan.
- A semantic-model change is a specification change; use the existing dependency/staleness graph and invalidate only affected downstream artifacts.

## CLI behavior

- Read-only validation returns `0` when state is structurally valid, `1` for validation findings, and `2` for unreadable or malformed input.
- `--coverage` emits a machine-readable REQ → AC → TASK → implementation/QA evidence matrix.
- `--invalidate <source>` emits invalidated JSON without mutating the input. The packaged validator has no write mode; durable state changes belong to the Control Plane.
