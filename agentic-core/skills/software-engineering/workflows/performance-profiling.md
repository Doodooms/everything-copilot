---
id: performance-profiling
description: 'Apply the performance-profiling method: profiling slow behavior, bundle
  analysis, render hot spots, query performance review, and memory or resource leak
  investigation.'
invoke_for:
- profiling slow behavior, bundle analysis, render hot spots, query performance review,
  and memory or resource leak investigation
avoid_for:
- speculative micro-optimization, general feature work, or unrelated code cleanup
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
- Measure or observe the hotspot before proposing optimization.
- Prefer the narrowest optimization that changes the identified bottleneck.
- Reference support files only at the point of need.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Inspect the measured or observed performance problem.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Use #tool:read on the profiling output, metrics, traces, or performance complaint that anchors the task.
2. Use #tool:search to locate the hot path, heavy dependency, render loop, or query path involved.
3. Use #tool:read on #file:../references/performance-profiling/references/guide.md ([profiling guide](../references/performance-profiling/references/guide.md)) only if the profiling checklist is still needed.

## Step 2 - Identify the optimization path.

1. Use #tool:execute on the narrowest profiler, benchmark, or performance check available for the target slice.
2. Classify the hotspot as algorithmic, rendering, bundle, query, or resource-management related.
3. Choose the smallest optimization that addresses the measured cause.

## Step 3 - Return the performance recommendation or validation.

1. Use #tool:read to verify the referenced hotspot locations and optimization claims.
2. Return the hotspot, evidence, optimization path, and any residual measurement gaps.
</workflow>
