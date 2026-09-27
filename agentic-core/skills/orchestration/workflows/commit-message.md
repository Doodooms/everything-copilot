---
id: commit-message
description: 'Apply the commit-message method: finalizing commit text after implementation
  and validation are complete, summarizing the actual diff, and recording change scope
  without speculation.'
invoke_for:
- finalizing commit text after implementation and validation are complete, summarizing
  the actual diff, and recording change scope without speculation
avoid_for:
- planning work, writing code, validating logic, or inventing changes that are not
  present
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
- Describe only validated changes.
- Do not invent intent or future work.
- Reference support files only at the point of need.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Inspect the validated change surface.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Use #tool:read on the validated summary, changed files, and relevant diff context.
2. Use #tool:search only if you need to confirm module or symbol names mentioned in the change.
3. Use #tool:read on #file:../references/commit-message/references/guide.md ([commit guide](../references/commit-message/references/guide.md)) only if the commit checklist is still needed.

## Step 2 - Draft the commit summary from confirmed facts.

1. Write a concise imperative subject that matches the actual change.
2. Add bullets for the concrete files, behaviors, or operational surfaces changed.
3. Note limitations or risks only when they were explicitly observed during validation.

## Step 3 - Check that the message stays factual.

1. Use #tool:read on the draft and compare it against the validated change summary.
2. Return only the final commit message content.
</workflow>
