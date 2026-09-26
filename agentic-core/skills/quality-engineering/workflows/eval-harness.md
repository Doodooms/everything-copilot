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

## Step 1 - Define a falsifiable evaluation.

1. DO consume the assigned `risk_level`; state the capability or regression target, baseline, environment, representative task set, success criteria, and planned trial count before running.
2. Separate deterministic code-based checks from model-graded or human-reviewed judgments; make the latter use an explicit rubric.

## Step 2 - Run the smallest informative evaluation.

1. Prefer deterministic graders; use model graders only for open-ended qualities and human review for consequential judgments.
2. Record each trial's task/eval ID, grader, result, and relevant revision; compare regression results to the baseline and protect private prompt content.
3. Compute `pass@k` (one or more successes in k attempts) or `pass^k` (all k trials succeed) only when the trial design supports that metric.

## Step 3 - Report measured behavior.

1. Return the eval definition, exact commands/configuration, revision, trial counts, raw outcome references, aggregate metrics, failures, and limitations.
2. MUST NOT claim reliability from a single success, substitute model opinion for a declared grader, or treat an unrun evaluation as passed.
