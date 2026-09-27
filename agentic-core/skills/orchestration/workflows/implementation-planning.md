---
id: implementation-planning
description: 'Apply the implementation-planning method: decomposing requirements into
  phases, task ownership, file scope, sequencing, and validation.'
invoke_for:
- decomposing requirements into phases, task ownership, file scope, sequencing, and
  validation
avoid_for:
- product decisions, architecture ownership, implementation, QA execution, or final
  acceptance
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
## Step 1 - Establish planning inputs.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Use #tool:read to inspect the approved specification, architecture decisions, repository constraints, existing plan, and requested delivery scope.
2. Use #tool:todo to create or update native todos for the three major planning steps; do not dispatch implementation or invent missing acceptance criteria.
3. Stop and return a blocker if required approval, specification revision, or architecture decisions are missing or stale.

## Step 2 - Build the executable task graph.

1. Use #tool:search to map each in-scope requirement and acceptance criterion to the smallest coherent tasks and relevant implementation surfaces.
2. For each task, define ID, objective, owner, allowed files/components, inputs, dependencies, expected output, validation, and phase exit criteria.
3. Sequence prerequisite work first, identify safe parallel groups, and expose the critical path and cross-component integration risks.
4. Keep migrations, compatibility, rollout, rollback, and documentation obligations explicit when relevant.

## Step 3 - Return the plan.

1. Return specification/architecture revisions, task graph, phases, dependency edges, file ownership, validation commands, risks, assumptions, skipped work with rationale, and the next owner.
2. Confirm all acceptance criteria have an owning task or are explicitly marked existing behavior/not applicable with evidence.
3. Use #tool:todo to update planning todos from the returned evidence; leave implementation state to the Orchestrator and task ledger.
</workflow>
