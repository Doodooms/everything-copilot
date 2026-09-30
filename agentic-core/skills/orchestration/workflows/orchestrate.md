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
<critical_rules>
- MUST keep work within this subskill’s declared scope and its specific safety or authority constraints.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
</critical_rules>

<general_rules>
- SHOULD load listed references only at the procedure step that needs them.
- MAY report unavailable evidence or unresolved decisions as unknown.
</general_rules>

<risk_assessment>
Consume the Orchestrator-assigned `risk_level` through the parent domain skill; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases risk. Scale evidence depth, not authority or approvals.
</risk_assessment>

<rules>
- MUST follow this selected subskill only within its declared procedure and scope.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Establish scope and the task record.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Classify the request, inspect Git/local user state, existing history, repository instructions, available custom agents/tools, and the narrowest relevant files.
2. Normalize requirements and acceptance criteria with the `spec-driven-development` workflow when needed; clarify only material user-owned decisions.
3. Select the smallest specialist sequence, dependency DAG, risk gates, and lifecycle actions. Record the reason for skipped phases.
   - Before approving a substantial new framework, subsystem, service, or infrastructure capability, load Research's `existing-solution-research` workflow when a compatible standard or existing project could change the build-versus-reuse decision. Skip it for routine local changes.
4. For coordinated work, follow [the manifest schema](../references/orchestrate/references/manifest_schema.md) and its [patch example](../references/orchestrate/assets/example_manifest_patch.yaml) or [full-change example](../references/orchestrate/assets/example_manifest_full_content.yaml); get the next ID with `uv run --script <absolute-path-to-orchestrator.py> next-task-id --history-dir <absolute-workspace-harness-history-path>`, initialize the manifest/event files, store the approved plan in planner history, and compile top-level work into native todos and task-status events.
   - Agent Skills resolves packaged script paths relative to this skill's root; see the [official script-path guidance](https://agentskills.io/skill-creation/using-scripts). This does not define a workspace-root environment variable. Obtain absolute workspace history and manifest paths from the caller or approved task packet; if unavailable, ask rather than deriving them from the shell working directory or plugin install location.
   - Use the [plan-index example](../references/orchestrate/assets/plan_index_example.md) and [index helper](../references/orchestrate/scripts/generate_plan_index.py) only when a large plan needs a concise file/section locator; a `plan_index` is optional.
   - Read the [context](../references/orchestrate/references/context.md) or [tool](../references/orchestrate/references/tools.md) reference only when deciding what context or host tools a handoff can use.
5. Before any dispatch, confirm the task state, base revision, scope, and user-required approvals; stop if a required decision or lifecycle prerequisite is blocked.
6. Before creating a new branch or worktree:
   1. Determine the primary repository effect (`feature`, `bugfix`, `refactor`, `test`, `docs`, or `maintenance`; `release`/`hotfix` only for those explicit lifecycles).
   2. Run `uv run --script <orchestrator.py> propose-branch --repo-root <absolute-repository-path> --title <task-title> --primary-effect <effect>`. For a release, include `--special-name vMAJOR.MINOR.PATCH`.
   3. Use only the positively validated proposal; ignore and recompute host suggestions. Record returned policy provenance in `lifecycle.branch_naming`. Stop if the policy file is malformed or the proposal is rejected. Historical manifest branch values remain readable and are not checked against current policy.

## Step 2 - Dispatch and reconcile bounded attempts.

1. Route bounded evidence work to Researcher when answering one or more questions locally would require substantial browsing, repository archaeology, versioned-document investigation, inspection of large source surfaces, or material consumption of the caller's context. Large-source isolation can justify delegation even when the final question is concise; keep trivial lookups local. Keep tightly coupled evidence questions together, and parallelize only questions that are genuinely orthogonal and independently useful. Each Researcher handoff MUST name `requested_by`, the artifact and revision it supports, the needed source class, and an explicit stop condition. Ask for compact sourced facts, uncertainty, and decision implications; Researcher supplies evidence but does not take the caller's decision authority. Do not impose a quota or minimum invocation rate.
2. For each ready task, use #tool:edit to prepare a bounded handoff packet, then #tool:execute with the [task-event helper](../references/orchestrate/scripts/orchestrator.py) once per transition. Supply the absolute workspace task-history path:
   - `uv run --script <absolute-path-to-orchestrator.py> append-task-event task_1 TASK-1 queued --attempt-id attempt-1 --agent-id implementer --history-dir <absolute-workspace-tasks-history-path>`
   - Repeat for `running` and later transitions. Update its native todo with #tool:todo before invoking only the assigned custom agent through #tool:agent and resume at the recorded point.
3. Capture the actual agent result and append its terminal/partial/blocked/unknown transition with the same helper and absolute task-history path. Use #tool:execute with `uv run --script <absolute-path-to-orchestrator.py> append-harness-event task_1 --event <structured-event-json> --history-dir <absolute-workspace-harness-history-path>` for the specialist return, then update the manifest with `uv run --script <absolute-path-to-orchestrator.py> record-manifest --manifest <absolute-workspace-manifest-path> --status <approved-status> --history-dir <absolute-workspace-harness-history-path> --repo <absolute-repository-path>`. Validate any outgoing/received packet with [validate_exchange.py](../references/orchestrate/scripts/validate_exchange.py) before advancing it; include `--repo` for commit or artifact checks. The helper requires absolute workspace paths and rejects relative/default paths rather than assuming a current directory. Record changed files, validation, Git commit IDs or explicit no-commit reason, artifact SHA-256 digests, deviations, risks, and next owner.
4. After each agent call, verify output fields and changed-file claims. If the call errors or returns no authoritative result, mark the attempt `failed` or `unknown` from observed evidence; inspect partial changes before a new attempt.
5. Check host status only through a host-provided query when available, and at handoff/phase boundaries. Do not invent a timer, heartbeat, notification, or liveness guarantee.
6. Advance only when dependencies and required gates have current evidence. Route QA failures to the evidenced owner, Reviewer findings to their stated owner, and material scope/specification changes through the Orchestrator before restarting affected gates.

## Step 3 - Reconcile convergence and report.

1. Use the [coordinated-change DAG](../references/orchestrate/references/workflows.md) to reconcile the finite handoff sequence; run SDD convergence for non-trivial work against the current specification, implementation evidence, and selected-gate results, and rerun only gates invalidated by a material change.
2. Verify there are no unresolved blockers, stale required artifacts, missing task owners, or unrecorded modifications; update the manifest, event log, task ledger, and todos from actual evidence.
3. Perform only the branch/worktree/PR/merge/cleanup actions explicitly authorized by the user and required by the selected lifecycle; record each result.
4. Return `success`, `partial`, or `failed` with task/spec/plan identifiers, selected/skipped phases, specialist attempts, changed files/commit SHAs, validation/QA/Reviewer evidence, convergence, unresolved risks, lifecycle state, and exact next action.
</workflow>
