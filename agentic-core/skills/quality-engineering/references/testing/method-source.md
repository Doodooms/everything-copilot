---
name: testing
description: "WHAT: Design and assess tests that provide strong evidence for software behavior. USE FOR: creating or materially changing tests, selecting test levels, and evaluating test adequacy across unit, property-based, integration, stateful, concurrent, browser, or end-to-end behavior. DO NOT USE FOR: the RED-GREEN-REFACTOR lifecycle, independent post-implementation falsification, runtime diagnosis, or security-only testing."
user-invocable: false
metadata:
  creation-date: 2026-09-26
  creator: Doodooms
license: MIT
---

<definitions>

- **test oracle**: An independent expected result that distinguishes correct behavior from a plausible defect.
- **test surface**: The smallest set of tests that exercises the contract, important boundaries, and relevant failure paths.

</definitions>

<rules>

- Start from the observable contract and test oracle, not from implementation structure or line coverage.
- Prefer the lowest test level that faithfully observes the contract; use real deterministic boundaries when they matter and are inexpensive.
- Every test SHOULD have a plausible defect that makes it fail. Assertions MUST prove outcomes, not merely execution.
- Cover dangerous boundaries, negative space, invalid states, and error paths in proportion to risk. MUST NOT add tombstone tests unless absence is itself a current API, security, or persistence contract.
- Treat quantitative coverage as secondary evidence; MUST NOT treat it as test adequacy by itself.
- Keep responsibilities distinct: `tdd` owns the RED-GREEN-REFACTOR lifecycle; `adversarial-testing` independently falsifies completed behavior; this skill owns test design and test-surface review.

</rules>

<admission>

## ACCEPT

- Design, add, or materially change tests for observable software behavior.
- Assess whether an existing test surface detects plausible regressions.
- Select test methods for integration, stateful, concurrent, or user-facing behavior.

## REJECT

- Drive a test-first implementation lifecycle → `tdd`.
- Independently falsify completed behavior for QA → `adversarial-testing`.
- Diagnose an unknown runtime failure → `failure-analysis`.
- Conduct security-specific testing → `security-testing`.
- Diagnose measured performance → `performance-profiling`.

</admission>

<workflow>

## Step 1 - Select the test procedure.

1. Use #tool:read and #tool:search to locate the behavior contract and existing test surface; select [test design](./workflows/test-design.md) for new or materially changed tests, [end-to-end testing](./workflows/end-to-end.md) for browser or full user journeys, and [test-quality review](./workflows/test-quality-review.md) to assess an existing test surface.
2. A task MAY need more than one procedure; load only those matching its contract.

## Step 2 - Apply the selected procedure.

1. Use the selected workflow to define the oracle, choose the smallest faithful test surface, and identify evidence gaps without freezing implementation details.

## Step 3 - Return test evidence.

1. Use #tool:execute when running tests, then report the contract, selected method and level, commands and outcomes, material gaps, and residual risk; MUST NOT claim the TDD or QA gate unless that work was performed.

</workflow>
