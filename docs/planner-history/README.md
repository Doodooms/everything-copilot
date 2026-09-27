# Planner history

Store each approved plan as `docs/planner-history/<task-id>/plan-r<revision>.md`. A plan records its source specification/architecture revisions, requirement and acceptance IDs, task IDs, file/component scope, dependencies, phase exit checks, validation commands, risks, and handoffs.

The Planner owns the plan content and MUST NOT redefine product acceptance. A new plan revision supersedes only the earlier plan; it does not rewrite historical task events or the Orchestrator manifest. The current manifest references the approved plan revision.
