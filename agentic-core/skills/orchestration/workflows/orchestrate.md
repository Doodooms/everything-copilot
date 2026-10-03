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
## Step 1 - Establish scope and determine whether durable task state is needed.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Classify the request, inspect Git/local user state, existing history, repository instructions, available custom agents/tools, and the narrowest relevant files.
2. Normalize requirements and acceptance criteria with the `spec-driven-development` workflow when needed; clarify only material user-owned decisions.
3. Select the smallest specialist sequence, dependency DAG, risk gates, and lifecycle actions. Record the reason for skipped phases.
   - Before approving a substantial new framework, subsystem, service, or infrastructure capability, load Research's `existing-solution-research` workflow when a compatible standard or existing project could change the build-versus-reuse decision. Skip it for routine local changes.
4. Decide whether the concrete workflow depends on durable Control Plane state. Task, Attempt, event, artifact, replay, lease, and provenance records belong to the Control Plane. When connected and needed, use its task state and operations; do not create repository-local manifests or history files as a substitute.
   - Workspace-local plugin, skill, and agent authoring, builds, tests, and other tasks that do not depend on durable Control Plane state proceed normally when it is unavailable. Use the repository and its local tools directly. Do not ask for a manifest, harness-history path, planner-history path, task-history path, or arbitrary allowed absolute paths.
   - If a concrete workflow truly requires durable Control Plane state and no Control Plane is connected, explain that dependency and stop only that workflow. Never ask the user to create local history files to satisfy it.
   - Consult the manifest schemas and examples only for an explicitly requested legacy exchange or validation task, not as instructions to persist active task state locally.
   - Use native todos for useful session tracking. Use the [plan-index example](../references/orchestrate/assets/plan_index_example.md) and [index helper](../references/orchestrate/scripts/generate_plan_index.py) only when a large plan needs a concise file/section locator; a `plan_index` is optional.
   - Read the [context](../references/orchestrate/references/context.md) or [tool](../references/orchestrate/references/tools.md) reference only when deciding what context or host tools a handoff can use.
5. Before any dispatch, confirm the available task context, base revision, scope, and user-required approvals; stop if a required decision or lifecycle prerequisite is blocked. A local workflow does not require a task manifest.
6. Before creating a new branch or worktree:
   1. Determine the primary repository effect (`feature`, `bugfix`, `refactor`, `test`, `docs`, or `maintenance`; `release`/`hotfix` only for those explicit lifecycles).
   2. Run `uv run --script <orchestrator.py> propose-branch --repo-root <absolute-repository-path> --title <task-title> --primary-effect <effect>`. For a release, include `--special-name vMAJOR.MINOR.PATCH`.
   3. Use only the positively validated proposal; ignore and recompute host suggestions. Record returned policy provenance in the Control Plane when connected and required, otherwise include it in the active handoff. Stop if the policy file is malformed or the proposal is rejected. Historical manifest branch values remain readable and are not checked against current policy.

## Step 2 - Dispatch and reconcile bounded attempts.

1. Route bounded evidence work to Researcher when answering one or more questions locally would require substantial browsing, repository archaeology, versioned-document investigation, inspection of large source surfaces, or material consumption of the caller's context. Large-source isolation can justify delegation even when the final question is concise; keep trivial lookups local. Keep tightly coupled evidence questions together, and parallelize only questions that are genuinely orthogonal and independently useful. Each Researcher handoff MUST name `requested_by`, the artifact and revision it supports, the needed source class, and an explicit stop condition. Ask for compact sourced facts, uncertainty, and decision implications; Researcher supplies evidence but does not take the caller's decision authority. Do not impose a quota or minimum invocation rate.
2. For each ready task, use #tool:edit to prepare a bounded handoff packet and update its native todo when useful, then invoke only the assigned custom agent through #tool:agent and resume from the returned handoff. When the workflow depends on connected Control Plane state, consume its allocated Attempt ID and persist Task/Attempt transitions and events there. Standalone dispatch uses only available live host status and the current handoff/session outcome; do not invent Attempt IDs/timestamps, create durable transitions/events, or create local event files.
3. Capture the actual agent result and reconcile its terminal/partial/blocked/unknown outcome. Validate an exchange packet with [validate_exchange.py](../references/orchestrate/scripts/validate_exchange.py) only when the concrete handoff uses that packet format. Record changed files, validation, Git commit IDs or explicit no-commit reason, artifact digests, deviations, risks, and next owner in the Control Plane when connected and required; otherwise report the evidence in the active session handoff.
4. After each agent call, verify output fields and changed-file claims. If the call errors or returns no authoritative result, record `failed`/`unknown` only as a Control Plane transition for a connected, required Attempt. Otherwise report the observed error or uncertainty in the active handoff/session and inspect partial changes before retrying; do not create a local lifecycle entry.
5. Check host status only through a host-provided query when available, and at handoff/phase boundaries. Do not invent a timer, heartbeat, notification, or liveness guarantee.
6. Advance only when dependencies and required gates have current evidence. Route QA failures to the evidenced owner, Reviewer findings to their stated owner, and material scope/specification changes through the Orchestrator before restarting affected gates.

## Step 3 - Reconcile convergence and report.

1. Use the [coordinated-change DAG](../references/orchestrate/references/workflows.md) to reconcile the finite handoff sequence; run SDD convergence for non-trivial work against the current specification, implementation evidence, and selected-gate results, and rerun only gates invalidated by a material change.
2. Verify there are no unresolved blockers, stale required artifacts, missing task owners, or unrecorded modifications. Reconcile durable state in the Control Plane when the workflow depends on it; otherwise reconcile from the active session and local evidence without creating repository history files.
3. Perform only the branch/worktree/PR/merge/cleanup actions explicitly authorized by the user and required by the selected lifecycle; record each result.
4. Return `success`, `partial`, or `failed` with supplied task/spec/plan identifiers when available, selected/skipped phases, specialist handoff outcomes, changed files/commit SHAs, validation/QA/Reviewer evidence, convergence, unresolved risks, Control Plane lifecycle state when used, and exact next action.
</workflow>
