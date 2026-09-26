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

## Step 1 - Search broadly and locally.

1. DO consume the assigned `risk_level`; define the bounded question and search likely code, docs, tests, and project vocabulary using available local tools.
2. Retrieve candidates and record why each may matter; do not preload whole directories or copy complete history.

## Step 2 - Evaluate and refine.

1. Score candidate relevance from 0 to 1 and state what evidence is still missing; load only decision-relevant candidates.
2. Refine terms, paths, and exclusions from observed evidence for at most three cycles.
3. Stop earlier when at least three high-relevance sources (>= 0.7) cover the critical question with no material gap; otherwise proceed with the best evidence and label remaining uncertainty.

## Step 3 - Return a bounded context packet.

1. Return paths/IDs, relevance rationale, useful deltas, unresolved evidence gaps, and the exact handoff or resume point.
2. Do not infer that uninspected files support a claim or turn retrieval into a substitute for the receiving agent's decision.
