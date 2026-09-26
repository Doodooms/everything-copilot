---
id: test-quality-review
description: Evaluate whether existing tests meaningfully detect plausible regressions
  in changed behavior.
invoke_for:
- assess test adequacy after a code change
- review behavioral assertions, boundary coverage, or regression protection
avoid_for:
- raw line-coverage reporting without behavioral assessment
- writing production implementation or independently running a QA campaign
references:
  - ../references/testing/references/test-oracles.md
  - ../references/testing/references/equivalence-boundaries.md
  - ../references/testing/references/test-doubles.md
---

## Step 1 - Inspect the claimed test surface.

1. Read the changed behavior and nearest tests; use search to find related paths, error handling, and tests that cover the same contract.
2. Identify the test oracle and plausible regression using [oracle guidance](../references/testing/references/test-oracles.md).

## Step 2 - Assess sensitivity and gaps.

1. Check whether assertions prove behavior and would fail for a plausible defect; inspect boundaries, error paths, test independence, fixture realism, mocks, and flakiness.
2. Use [boundary guidance](../references/testing/references/equivalence-boundaries.md) and [test-double guidance](../references/testing/references/test-doubles.md) only where a concrete gap is suspected.
3. Treat coverage percentages as supporting evidence, not a proxy for adequacy; report material gaps separately from optional improvements.

## Step 3 - Return the review.

1. Summarize strong evidence, reproducible coverage gaps, affected behavior, and residual risk; MUST NOT modify production code or claim final acceptance.
