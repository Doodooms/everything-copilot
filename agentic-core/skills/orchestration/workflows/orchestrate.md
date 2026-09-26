---
id: orchestrate
description: 'Apply the orchestrate method: multi-agent changes, material feature
  work, migrations, and delivery requiring traceable handoffs.'
invoke_for:
- multi-agent changes, material feature work, migrations, and delivery requiring traceable
  handoffs
avoid_for:
- specialist-only tasks that fit one custom agent or implementation/review work yourself
references: []
---

<workflow>

## Step 1 - Establish scope and the task record.

1. Classify the request, inspect Git/local user state, existing history, repository instructions, available custom agents/tools, and the narrowest relevant files.
2. Normalize requirements and acceptance criteria with the `spec-driven-development` workflow when needed; clarify only material user-owned decisions.
3. Select the smallest specialist sequence, dependency DAG, risk gates, and lifecycle actions. Record the reason for skipped phases.
4. For coordinated work, follow [the manifest schema](../references/orchestrate/references/manifest_schema.md) and its [patch example](../references/orchestrate/assets/example_manifest_patch.yaml) or [full-change example](../references/orchestrate/assets/example_manifest_full_content.yaml); get the next ID with `PYTHONDONTWRITEBYTECODE=1 python scripts/orchestrator.py next-task-id --history-dir <absolute-workspace-harness-history-path>`, initialize the manifest/event files, store the approved plan in planner history, and compile top-level work into native todos and task-status events.
   - Agent Skills resolves packaged script paths relative to this skill's root; see the [official script-path guidance](https://agentskills.io/skill-creation/using-scripts). This does not define a workspace-root environment variable. Obtain absolute workspace history and manifest paths from the caller or approved task packet; if unavailable, ask rather than deriving them from the shell working directory or plugin install location.
   - Use the [plan-index example](../references/orchestrate/assets/plan_index_example.md) and [index helper](../references/orchestrate/scripts/generate_plan_index.py) only when a large plan needs a concise file/section locator; a `plan_index` is optional.
   - Read the [context](../references/orchestrate/references/context.md) or [tool](../references/orchestrate/references/tools.md) reference only when deciding what context or host tools a handoff can use.
5. Before any dispatch, confirm the task state, base revision, scope, and user-required approvals; stop if a required decision or lifecycle prerequisite is blocked.

## Step 2 - Dispatch and reconcile bounded attempts.

1. For each ready task, use #tool:edit to prepare a bounded handoff packet, then #tool:execute with the [task-event helper](../references/orchestrate/scripts/orchestrator.py) once per transition. Supply the absolute workspace task-history path:
   - `PYTHONDONTWRITEBYTECODE=1 python scripts/orchestrator.py append-task-event task_1 TASK-1 queued --attempt-id attempt-1 --agent-id implementer --history-dir <absolute-workspace-tasks-history-path>`
   - Repeat for `running` and later transitions. Update its native todo with #tool:todo before invoking only the assigned custom agent through #tool:agent and resume at the recorded point.
2. Capture the actual agent result and append its terminal/partial/blocked/unknown transition with the same helper and absolute task-history path. Use #tool:execute with `PYTHONDONTWRITEBYTECODE=1 python scripts/orchestrator.py append-harness-event task_1 --event <structured-event-json> --history-dir <absolute-workspace-harness-history-path>` for the specialist return, then update the manifest with `PYTHONDONTWRITEBYTECODE=1 python scripts/orchestrator.py record-manifest --manifest <absolute-workspace-manifest-path> --status <approved-status> --history-dir <absolute-workspace-harness-history-path>`. The helper requires absolute workspace paths and rejects relative/default paths rather than assuming a current directory. Record changed files, validation, commit SHA(s) or the authorized conflict-only no-commit reason, deviation, risks, and next owner.
3. After each agent call, verify output fields and changed-file claims. If the call errors or returns no authoritative result, mark the attempt `failed` or `unknown` from observed evidence; inspect partial changes before a new attempt.
4. Check host status only through a host-provided query when available, and at handoff/phase boundaries. Do not invent a timer, heartbeat, notification, or liveness guarantee.
5. Advance only when dependencies and required gates have current evidence. Route QA failures to the evidenced owner, Reviewer findings to their stated owner, and material scope/specification changes through the Orchestrator before restarting affected gates.

## Step 3 - Reconcile convergence and report.

1. Use the [coordinated-change DAG](../references/orchestrate/references/workflows.md) to reconcile the finite handoff sequence; run SDD convergence for non-trivial work against the current specification, implementation evidence, and selected-gate results, and rerun only gates invalidated by a material change.
2. Verify there are no unresolved blockers, stale required artifacts, missing task owners, or unrecorded modifications; update the manifest, event log, task ledger, and todos from actual evidence.
3. Perform only the branch/worktree/PR/merge/cleanup actions explicitly authorized by the user and required by the selected lifecycle; record each result.
4. Return `success`, `partial`, or `failed` with task/spec/plan identifiers, selected/skipped phases, specialist attempts, changed files/commit SHAs, validation/QA/Reviewer evidence, convergence, unresolved risks, lifecycle state, and exact next action.

</workflow>
