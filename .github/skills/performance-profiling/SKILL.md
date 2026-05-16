---
name: performance-profiling
description: "WHAT: Identify performance bottlenecks and choose the narrowest evidence-backed optimization path. USE FOR: profiling slow behavior, bundle analysis, render hot spots, query performance review, and memory or resource leak investigation. DO NOT USE FOR: speculative micro-optimization, general feature work, or unrelated code cleanup."
user-invocable: false
metadata:
  creation-date: 2026-05-14
  creator: Doodooms
---

<definitions>

- **performance hotspot** : A measurable bottleneck in runtime, rendering, bundle size, query execution, or memory usage that materially affects the user or operator experience.

</definitions>

<workflow>

## Step 0 - **CONFIRMATION**

1. USE #tool:read **IMMEDIATELY** on #file:./references/USEFOR.md and **IMMEDIATELY** on #file:./references/DONOTUSEFOR.md to confirm with certainty if this skill should be used.
2. Now read the following rules and workflow steps to understand how the skill works and what it requires for execution.

<rules>

- Measure or observe the hotspot before proposing optimization.
- Prefer the narrowest optimization that changes the identified bottleneck.
- Reference support files only at the point of need.

</rules>

## Step 1 - Inspect the measured or observed performance problem.

1. Use #tool:read on the profiling output, metrics, traces, or performance complaint that anchors the task.
2. Use #tool:search to locate the hot path, heavy dependency, render loop, or query path involved.
3. Use #tool:read on #file:./references/guide.md only if the profiling checklist is still needed.

## Step 2 - Identify the optimization path.

1. Use #tool:execute on the narrowest profiler, benchmark, or performance check available for the target slice.
2. Classify the hotspot as algorithmic, rendering, bundle, query, or resource-management related.
3. Choose the smallest optimization that addresses the measured cause.

## Step 3 - Return the performance recommendation or validation.

1. Use #tool:read to verify the referenced hotspot locations and optimization claims.
2. Return the hotspot, evidence, optimization path, and any residual measurement gaps.

</workflow>