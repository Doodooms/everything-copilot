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

## Step 1 - Bound the problem.

1. Identify input size, growth, worst-case constraints, memory limits, determinism, exactness, update frequency, and batch or online requirements.

## Step 2 - Compare candidate methods.

1. Use [complexity guidance](../references/implementation-design/references/algorithmic-complexity.md) and relevant [representation guidance](../references/implementation-design/references/data-structures.md) to compare asymptotic and practical costs.
2. Prefer the clearest correct method when the constraints do not distinguish candidates; MUST NOT optimize hypothetical scale.

## Step 3 - Validate material assumptions.

1. Use #tool:execute to benchmark only when performance is a stated or evidenced constraint; record representative inputs, environment, and limitations, or return to the simpler method.
