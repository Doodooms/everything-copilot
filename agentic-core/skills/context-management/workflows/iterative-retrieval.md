---
id: iterative-retrieval
description: Progressively refine evidence retrieval when initial context is insufficient for a bounded handoff.
invoke_for:
- Multi-agent handoffs with consequential repository evidence gaps
- Context limits or missing-context failures during bounded investigation
- Retrieval pipelines that need a targeted refine-and-stop condition
avoid_for:
- Simple lookups where direct search and read already provide sufficient evidence
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
## Step 1 - Search broadly and locally.

1. DO consume the assigned `risk_level`; define the bounded question and search likely code, docs, tests, and project vocabulary using available local tools.
2. Search independent locations or terms in parallel when the host supports it; retrieve candidates and record why each may matter. Do not preload whole directories or copy complete history.
3. Track each candidate as `available`, `retrieved`, or `expanded`; only `retrieved` evidence may support the current answer, and expand a source only when its relevant summary leaves a decision-critical gap.

## Step 2 - Evaluate and refine.

1. Score candidate relevance from 0 to 1 and state what evidence is still missing: `0.7-1.0` is high, `0.5-<0.7` medium, `0.2-<0.5` low, and `<0.2` negligible. Treat scores as a retrieval aid, not proof that an uninspected source supports a claim.
2. Refine terms, paths, and exclusions from observed evidence for at most three cycles.
3. Stop earlier when at least three high-relevance sources (>= 0.7) cover the critical question with no material gap; otherwise proceed with the best evidence and label remaining uncertainty.

## Step 3 - Return a bounded context packet.

1. Return paths/IDs, retrieval state, relevance score and rationale, useful deltas, unresolved evidence gaps, and the exact handoff or resume point.
2. Do not infer that uninspected files support a claim or turn retrieval into a substitute for the receiving agent's decision.
</workflow>
