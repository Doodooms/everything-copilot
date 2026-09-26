# Artifact Lifecycle

## Canonical task-state extension

Extend the existing Orchestrator manifest/state at its established task path. Do not create `.github/sdd/`, a competing plans directory, or a parallel task database. Existing fields such as `id`, `plan_index`, `test_commands`, lifecycle metadata, and audit records remain authoritative for their concepts. The **Optional SDD extension** in the Orchestrator's manifest schema is the single source of truth for field shape; this reference defines lifecycle semantics.

The validator accepts either the task-state wrapper with a `manifest` object or the manifest itself. It is structural validation, not evidence of technical correctness.

`PYTHONDONTWRITEBYTECODE=1 python scripts/validate_sdd_state.py <absolute-task-state-path>` accepts either the task-state wrapper with a `manifest` object or the manifest itself. The validator path is relative to this skill's root, as specified in the [Agent Skills script-path guidance](https://agentskills.io/skill-creation/using-scripts); the task-state path is supplied explicitly and is not inferred from the shell working directory. It is structural validation, not evidence of technical correctness.

## Stable IDs and revisions

- `SPEC-*` identifies one specification across integer `revision` values; `SPEC-001@rev2` is the second immutable view of that specification.
- Use stable `REQ-*`, `AC-*`, `ADR-*`, `TASK-*`, `DEFECT-*`, `QA-RUN-*`, and `REVIEW-*` IDs for traceability.
- Retain an ID only while its meaning remains stable. Materially changed intent gets a new revision and updated affected IDs.
- Every derived artifact records the specification revision and relevant IDs it consumes.
- QA evidence additionally records the implementation revision; Reviewer approval additionally records the exact QA run and implementation revision.
- A reusable validation record SHOULD identify its check/command, subject code revision, relevant environment, result, producer, and scope. Reuse it only while its subject revision, target, and relevant environment remain unchanged.
- The Orchestrator records assigned `risk_level` (`L0`–`L3`) and the selected `required_gates` in the canonical manifest. Specialists consume that level and may escalate from new evidence; they do not reclassify it.

## Dependency-aware invalidation

Material changes flow downstream, not backward:

```text
specification → architecture → plan → tasks → implementation → QA → review
```

The validator's `--invalidate` operation marks downstream artifacts stale on a copy and emits JSON. It does not write the file unless `--write` is explicit. It preserves `architecture.status: not_required` when specification changes do not create an architecture requirement. When exact impact is known to be narrower, invalidate only affected artifacts; when uncertain, use the conservative dependency set.

Examples:

- A changed requirement invalidates affected architecture, plan, tasks, implementation evidence, QA, and review.
- A changed architecture decision invalidates affected plan, task, implementation, QA, and review.
- A sequencing-only plan change can preserve implementation only when the Orchestrator records that no behavior or ownership dependency changed.
- A QA-only test improvement does not invalidate specification, architecture, or plan.
- A semantic-model change is a specification change; use the existing dependency/staleness graph and invalidate only affected downstream artifacts.

## CLI behavior

- Read-only validation returns `0` when state is structurally valid, `1` for validation findings, and `2` for unreadable or malformed input.
- `--coverage` emits a machine-readable REQ → AC → TASK → implementation/QA evidence matrix.
- `--invalidate <source>` emits invalidated JSON without mutating the input. Add `--write` only when the owning Orchestrator intentionally updates the canonical state.
