---
name: software-engineering
description: "WHAT: Select local implementation methods for behavior, data, algorithms, state, synchronization, and user interfaces. USE FOR: testable code changes, non-trivial local design, frontend behavior, measured performance problems, disposable prototypes, or behavior-preserving refactors. DO NOT USE FOR: system architecture, product semantics, independent QA, or operational deployment."
user-invocable: false
metadata:
  creation-date: 2026-09-26
  creator: Doodooms
license: MIT
---

<critical_rules>

- MUST implement only approved behavior and preserve its invariants, error contracts, and architecture boundaries.
- MUST NOT substitute a local design method for architecture ownership, QA, or final acceptance.

</critical_rules>

<general_rules>

- SHOULD choose the simplest faithful implementation and use measured constraints rather than hypothetical scale.

</general_rules>

<risk_assessment>

Consume the Orchestrator-assigned `risk_level`; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases impact, exposure, uncertainty, or irreversibility. Risk scales evidence depth, not authority or approvals.

</risk_assessment>

<rules>

- This domain owns local implementation methods; product intent and system boundaries remain owned by the specification and architecture owners.
- DO load only the workflow matching the behavior, constraints, and evidence in the handoff; use `tdd` for the test-first implementation lifecycle.

</rules>

<workflow>

## Step 1 - Assess risk and route the implementation question.

1. DO consume the assigned `risk_level`, then select only matching procedures:
   - [tdd](./workflows/tdd.md) for testable behavior changes and fixes.
   - [representation-selection](./workflows/representation-selection.md), [algorithm-selection](./workflows/algorithm-selection.md), [state-modeling](./workflows/state-modeling.md), or [concurrency-design](./workflows/concurrency-design.md) for their local design decision.
   - [frontend-patterns](./workflows/frontend-patterns.md) for React/Next.js UI, state, forms, rendering, or accessibility.
   - [performance-profiling](./workflows/performance-profiling.md) for an evidenced performance issue.
   - [prototype](./workflows/prototype.md) only for an explicitly approved disposable artifact.
   - [refactor-cleanup](./workflows/refactor-cleanup.md) for approved behavior-preserving cleanup.

## Step 2 - Apply the selected procedure.

1. Follow the selected workflow directly and load only relevant supporting knowledge; stop and return material specification or architecture changes to their owner.

## Step 3 - Validate and hand off.

1. Report the implementation evidence, tests, deviations, unresolved assumptions, and next owner; do not claim independent QA or review.

</workflow>
