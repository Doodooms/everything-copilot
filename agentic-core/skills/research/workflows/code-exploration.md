---
id: code-exploration
description: 'Apply the code-exploration method: entry-point tracing, execution-path
  mapping, dependency discovery, and identifying the safest local change surface in
  unfamiliar code.'
invoke_for:
- entry-point tracing, execution-path mapping, dependency discovery, and identifying
  the safest local change surface in unfamiliar code
avoid_for:
- broad architecture design, direct implementation, security auditing, or documentation
  updates
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
- Start from the narrowest concrete anchor available.
- Map only the controlling path needed for the requested work.
- Reference support files only at the point of need.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Find the controlling entry point.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Use #tool:search to locate the concrete trigger, handler, route, command, or failing test closest to the requested behavior.
2. Use #tool:read on the anchor files and immediate neighbors that control the behavior.
3. Use #tool:read on #file:../references/code-exploration/references/guide.md ([exploration guide](../references/code-exploration/references/guide.md)) only if the exploration checklist is still needed.

## Step 2 - Trace the execution path and dependencies.

1. Use #tool:read to follow the control flow from the entry point to the state change or result.
2. Use #tool:search to locate related call sites, shared symbols, and adjacent tests when they affect the path.
3. Distinguish orchestration code from the logic that actually decides behavior.

## Step 3 - Return the execution map.

1. Return the entry point, key files, dependency boundaries, and recommended first edit surface.
2. State traps, hidden side effects, or unresolved branches only when they affect likely changes.
</workflow>
