---
id: test-design
description: Design a small, strong test surface for a concrete behavior contract.
invoke_for:
- create or materially change behavior tests
- choose test levels, assertions, cases, or test doubles
- use a property or invariant over a large input space
avoid_for:
- review-only assessment of an existing suite
- independent QA falsification
references:
  - ../references/testing/references/test-oracles.md
  - ../references/testing/references/equivalence-boundaries.md
  - ../references/testing/references/test-levels.md
  - ../references/testing/references/test-doubles.md
---

## Step 1 - Define the contract and oracle.

1. Identify the observable behavior, input/output or state transition, and a plausible defect; consult [test oracles](../references/testing/references/test-oracles.md) when the expected result is not obvious.
2. Partition meaningful inputs and failure modes with [boundary guidance](../references/testing/references/equivalence-boundaries.md); avoid enumerating cases that cannot distinguish behavior.

## Step 2 - Choose the smallest faithful test.

1. Select the lowest test level that observes the real contract using [test-level guidance](../references/testing/references/test-levels.md).
2. Use [test-double guidance](../references/testing/references/test-doubles.md) only when a boundary must be controlled; MUST NOT mock a project-owned behavior that the test is meant to prove.
3. Add the minimum cases that cover normal behavior, important boundaries, and meaningful failures; omit implementation-only assertions. Do not add tombstone tests whose only purpose is to assert that removed code, routes, fields, or features remain absent; negative tests are appropriate when absence is itself a current API, security, or persistence contract.
   - Use property-based checks when a stable invariant and broad input space make hand-picked examples weak; MUST NOT add a new generator dependency without need.
   - For shared mutable state or concurrent writers, state the invariant independently of implementation, use deterministic barriers/latches to force overlap, assert the result after the interleaving, and treat stress runs or race detectors as supplemental evidence; do not use sleeps or random stress alone to create a race.

## Step 3 - Check the evidence.

1. Verify assertions distinguish the intended result from the plausible defect and that the test is deterministic in the repository's established pattern.
2. When used inside TDD, return the designed test target to `tdd`; that skill owns the RED/GREEN sequence.
3. Consult the [original specification](../references/testing/references/original-spec.md) only when maintaining this package's scope or provenance.
