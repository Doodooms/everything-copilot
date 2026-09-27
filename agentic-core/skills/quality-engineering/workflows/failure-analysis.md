---
id: failure-analysis
description: 'Apply the failure-analysis method: failing builds or tests, unknown
  runtime defects, swallowed errors, dangerous fallbacks, intermittent failures, or
  measured performance regressions.'
invoke_for:
- failing builds or tests, unknown runtime defects, swallowed errors, dangerous fallbacks,
  intermittent failures, or measured performance regressions
avoid_for:
- implementing a fix, speculative optimization, general review, or feature work
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
## Step 1 - Establish the failure signal.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Use #tool:read to inspect the reported symptom, exact failing command or input, environment, recent relevant changes, logs, and reproduction evidence before theorizing.
2. Use #tool:execute to run the narrowest existing test, command, or harness that reaches the reported behavior; confirm its failure is the one described.
3. If no useful signal exists, use #tool:edit only for a minimal, authorized test-surface probe. Read the [failure-analysis guide](../references/failure-analysis/references/guide.md) when help choosing a loop or reducing a reproduction is needed.

## Step 2 - Isolate the cause.

1. Reduce the reproduction to the smallest failure-preserving input, retaining the original case for comparison.
2. Use #tool:search to trace the failure path through callers, state, configuration, error handling, and fallback behavior; identify where the observed result diverges from the expected contract.
3. Rank plausible causes by evidence and define a probe for each. Change one relevant condition at a time; use targeted debugger or existing logs before adding any instrumentation.
4. For timing-sensitive or intermittent failures, capture repeated outcomes and the conditions that affect them. For performance, compare like-for-like measurements before inferring a regression.

## Step 3 - Return the diagnostic handoff.

1. Return `status: success | partial | blocked`, the reported and observed behavior, reproduction command/environment, minimal inputs, failure chain, root-cause evidence, alternative hypotheses, affected requirements when known, likely owner, and exact next action.
2. State whether a reliable signal was established, which checks were not possible, and any remaining uncertainty. Do not implement or claim that a repair is validated.
</workflow>
