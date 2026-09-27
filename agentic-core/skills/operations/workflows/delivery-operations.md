---
id: delivery-operations
description: 'Apply the delivery-operations method: approved delivery-pipeline or
  operational work in an existing environment.'
invoke_for:
- approved delivery-pipeline or operational work in an existing environment
avoid_for:
- product features, architecture ownership, unapproved production deployment, or generic
  verification-only requests
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
## Step 1 - Establish the operational boundary.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Use #tool:read to inspect the approved task, repository CI/release/deployment files, environment configuration, applicable runbooks, and existing validation commands.
2. Use #tool:todo to create native todos for distinct phases only; mark deployment as blocked until authorization and required environment evidence are available.
3. Identify affected environments, permissions, secrets, data/state risk, rollback path, and non-goals.

## Step 2 - Apply and validate the operational change.

1. Use #tool:edit to make the smallest change in the owning workflow/configuration/runbook surface.
2. Use #tool:execute to run syntax, schema, lint, or dry-run checks before any external side effect.
3. Perform deployment or live verification only when explicitly authorized; verify health and rollback signals with actual evidence.
4. Update operational documentation only to reflect verified behavior.

## Step 3 - Return operational evidence.

1. Report changed files, exact commands/results, environments actually exercised, unverified assumptions, risks, and blockers.
2. State rollout/rollback/monitoring guidance and the next owner.
3. Use #tool:todo to mark todos complete only after the corresponding evidence is recorded; never infer deployment success from configuration validity.
</workflow>
