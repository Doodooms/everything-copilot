---
id: eval-harness
description: Define and run measurable evaluations for AI-assisted workflows or agent behavior.
invoke_for:
- Pass/fail criteria for AI-assisted workflows or agent capabilities
- Reliability, regression, pass@k, or model/version evaluation
- Benchmarks that compare agent or prompt behavior
avoid_for:
- Ordinary deterministic software tests unrelated to agent/skill evaluation
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
## Step 1 - Define a falsifiable evaluation.

1. DO consume the assigned `risk_level`; state the capability or regression target, baseline, environment, representative task set, success criteria, and planned trial count before running.
2. MUST version the evaluation definition, task prompts or fixtures, expected behavior, and matched baselines with the code or immutable source references. Store each run as a durable machine-readable artifact in the repository's established evaluation path; keep private prompt content protected.
3. Separate deterministic code-based checks from model-graded or human-reviewed judgments; make the latter use an explicit rubric.
4. Before any model invocation, set an explicit maximum model-call budget and retry budget, and configure a guard that can stop the invocation before the ceiling is exceeded. If that ceiling cannot be enforced before a call, mark the model evaluation blocked and do not invoke the model; continue only with independent deterministic checks.

## Step 2 - Run the smallest informative evaluation.

1. Prefer deterministic graders; use model graders only for open-ended qualities and human review for consequential judgments.
2. Record each trial's task/eval ID, grader, result, model calls, and relevant revision in the durable machine-readable artifact; report unreported token/call values as `unknown`. Count harness executions separately from model calls, and compare regression results to the matched baseline. Markdown may summarize a run but MUST NOT be its only durable record.
3. Compute `pass@k` (one or more successes in k attempts) or `pass^k` (all k trials succeed) only when the trial design supports that metric.

## Step 3 - Report measured behavior.

1. Return the eval definition, exact commands/configuration, revision, trial counts, raw outcome references, aggregate metrics, failures, and limitations.
2. MUST NOT claim reliability from a single success, substitute model opinion for a declared grader, or treat an unrun evaluation as passed.
</workflow>
