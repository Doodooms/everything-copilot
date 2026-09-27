---
id: code-review
description: 'Apply the code-review method: static review of a bounded diff and its
  consequential call sites.'
invoke_for:
- static review of a bounded diff and its consequential call sites
avoid_for:
- implementation, runtime diagnosis, adversarial test execution, dedicated security
  review, or final acceptance
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
## Step 1 - Establish the review contract.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Use #tool:read to inspect the approved requirements, review target, changed-file list, and author/QA evidence.
2. Use #tool:todo to create native todos for major review phases only when the review is multi-phase; do not split each file or finding into a separate todo.
3. Identify review boundaries and required specialist evidence before analyzing implementation details.

## Step 2 - Inspect for material defects.

1. Use #tool:search to trace changed behavior through relevant callers, data boundaries, error handling, and compatibility surfaces.
2. Check correctness, regressions, unsafe fallbacks, maintainability, test evidence, and documentation/operational impact within scope.
3. Route dedicated security, database, performance, or language-specific questions to their corresponding evidence workflow rather than duplicating it.

## Step 3 - Return findings.

1. Order findings by severity and confidence; include exact file/line, concrete impact, evidence, and suggested owner.
2. Separate blockers from optional improvements and state residual risks, examined scope, and missing evidence.
3. Return a concise review handoff; do not claim final approval or modify the change. Use #tool:todo to update todos before returning.
</workflow>
