---
name: context-management
description: "WHAT: Retrieve, preserve, and measure only task-relevant agent context. USE FOR: evidence gaps in multi-agent work, durable context management, phase-boundary compaction, or local context/token projection reviews. DO NOT USE FOR: creating a competing specification/task store, hosted token counting, or reducing required safety and product behavior."
user-invocable: false
metadata:
  creation-date: 2026-09-26
  creator: Doodooms
license: MIT
---

<definitions>

- **raw history**: A prior transcript or event log; its presence does not mean it is active context or durable memory.
- **active context**: Material actually retrieved into the current harness context for this task.
- **durable memory**: An approved, provenance-bearing note retained across sessions.
- **retrieval state**: `available`, `retrieved`, and `expanded` are distinct; a reference can be available without being read, and a retrieved summary does not mean its full source was expanded.

</definitions>

<critical_rules>

- MUST preserve canonical task/specification state and keep private source text local during measurement.
- MUST NOT optimize context by removing required behavior, authority, evidence, or safety constraints.

</critical_rules>

<general_rules>

- SHOULD use references, bounded packets, and selected procedures rather than copying full histories or preloading all context.

</general_rules>

<risk_assessment>

Consume the Orchestrator-assigned `risk_level`; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases impact, exposure, uncertainty, or irreversibility. Risk scales evidence depth, not authority or approvals.

</risk_assessment>

<rules>

- This domain curates retrieval, memory, session boundaries, and approximate local context measurements; it does not own canonical product or task state.
- MUST distinguish what is available, what was retrieved, and what was expanded; never claim that an unread source informed a decision.
- SHOULD verify a durable note's source revision or observation date before relying on it; mark it stale when a dependency changed and keep the current source authoritative.
- A local token projection estimates selected files that may be loaded; it cannot measure an active host conversation or provider quota. Use the `multi-harness` host-observation workflows for those values and label missing observations `unknown`.
- DO load only the workflow matching the current gap; generic references are excluded from context totals, while selected workflows are counted.

</rules>

<workflow>

## Step 1 - Identify the context problem.

1. DO consume the assigned `risk_level`, then select only a matching workflow:
   - [iterative-retrieval](./workflows/iterative-retrieval.md) for consequential evidence gaps or bounded multi-agent retrieval.
   - [memory](./workflows/memory.md) for approved durable context orientation, retrieval, or persistence.
   - [strategic-compact](./workflows/strategic-compact.md) at logical phase boundaries or when context limits threaten task quality.
   - [token-optimization](./workflows/token-optimization.md) for local agent, skill, workflow, or tool-schema estimates.

## Step 2 - Apply the selected context method.

1. Follow the selected workflow directly; keep inputs local, load only point-of-need material, and maintain the canonical source of truth rather than creating a parallel store.

## Step 3 - Return a bounded context handoff.

1. Report the relevant references/deltas, estimator and limitations when measured, excluded generic references, unresolved gaps, and exact resume point.

</workflow>
