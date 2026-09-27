---
id: algorithm-selection
description: Choose an algorithm appropriate to input scale, complexity constraints,
  and exactness requirements.
invoke_for:
- compare algorithms with materially different time or memory behavior
- evaluate exact, approximate, batch, incremental, or parallel processing choices
avoid_for:
- ordinary local logic with no scale or complexity constraint
- profiling an existing performance incident
references:
  - ../references/implementation-design/references/algorithmic-complexity.md
  - ../references/implementation-design/references/data-structures.md
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
## Step 1 - Bound the problem.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Identify input size, growth, worst-case constraints, memory limits, determinism, exactness, update frequency, and batch or online requirements.

## Step 2 - Compare candidate methods.

1. Use [complexity guidance](../references/implementation-design/references/algorithmic-complexity.md) and relevant [representation guidance](../references/implementation-design/references/data-structures.md) to compare asymptotic and practical costs.
2. Prefer the clearest correct method when the constraints do not distinguish candidates; MUST NOT optimize hypothetical scale.

## Step 3 - Validate material assumptions.

1. Use #tool:execute to benchmark only when performance is a stated or evidenced constraint; record representative inputs, environment, and limitations, or return to the simpler method.
</workflow>
