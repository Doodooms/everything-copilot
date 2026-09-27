---
id: refactor-cleanup
description: 'Apply the refactor-cleanup method: safe cleanup after implementation,
  duplicate removal, dead-code elimination, and behavior-preserving refactors.'
invoke_for:
- safe cleanup after implementation, duplicate removal, dead-code elimination, and
  behavior-preserving refactors
avoid_for:
- feature delivery, speculative rewrites, or optimization without evidence
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
- Preserve intended behavior while cleaning structure.
- Prefer small, reviewable cleanup slices over broad rewrites.
- Reference support files only at the point of need.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Identify the cleanup candidate and its current behavior.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Use #tool:read on the target files, nearby tests, and existing behavior anchor.
2. Use #tool:search to locate duplicate logic, dead branches, unused helpers, or repeated patterns.
3. Use #tool:read on #file:../references/refactor-cleanup/references/guide.md ([cleanup guide](../references/refactor-cleanup/references/guide.md)) only if the cleanup checklist is still needed.

## Step 2 - Apply the smallest behavior-preserving cleanup plan.

1. Decide which code is truly dead, duplicated, or unnecessarily complex.
2. Keep the refactor local and avoid mixing it with new behavior.
3. Preserve or improve the surrounding test safety net.

## Step 3 - Validate the cleanup result.

1. Use #tool:execute on the narrowest test or build check that proves the behavior is unchanged.
2. Return the cleanup scope, preserved behavior, and any follow-up slices that should stay separate.
</workflow>
