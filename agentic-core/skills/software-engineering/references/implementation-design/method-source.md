---
name: implementation-design
description: "WHAT: Choose a simple local representation and implementation structure that satisfies explicit constraints. USE FOR: non-trivial data structures, algorithmic choices, state models, or synchronization decisions. DO NOT USE FOR: system architecture, product-domain semantics, API contracts, routine glue code, or performance diagnosis."
user-invocable: false
metadata:
  creation-date: 2026-09-26
  creator: Doodooms
license: MIT
---

<definitions>

- **local design choice**: A representation, algorithm, state model, or synchronization structure inside an approved implementation boundary.
- **invariant**: A property that every valid operation or state transition must preserve.

</definitions>

When authoring or materially repairing this method, consult the [preserved specification](./references/original-spec.md) as provenance only.

<rules>

- Start from constraints, invariants, required operations, access patterns, and scale; MUST NOT start from a named design pattern.
- Choose the simplest structure that satisfies the contract. Explain relevant time, memory, ordering, mutation, and maintainability tradeoffs.
- Optimize only against explicit constraints or measured evidence; MUST NOT create abstraction or concurrency for hypothetical future needs.
- Stay within the approved local implementation boundary. Product semantics and system boundaries remain owned by their specification and architecture owners.

</rules>

<admission>

## ACCEPT

- Choose between materially different local data representations or algorithmic strategies.
- Model a non-trivial lifecycle, state transition, or synchronization contract.
- Review a local design choice whose complexity, ordering, or maintainability materially affects correctness.

## REJECT

- Choose service, module, deployment, or system boundaries → `architect` using `architecture-design`.
- Define product-domain meaning or business invariants → `orchestrator` / `architect` using `domain-modeling`.
- Design an external API contract → `architect` using `api-design`.
- Diagnose measured runtime performance → `performance-profiling`.
- Drive test-first implementation → `tdd`.

</admission>

<workflow>

## Step 1 - Establish the local constraints.

1. Use #tool:read and #tool:search to inspect the approved behavior, existing representation, required operations, mutation and access patterns, expected scale, and repository conventions.
2. Identify invariants and ordering or lifecycle requirements; return unresolved product semantics or architecture boundaries to their owner.

## Step 2 - Select the matching design procedure.

1. Use [representation selection](./workflows/representation-selection.md) for data structure choices, [algorithm selection](./workflows/algorithm-selection.md) for complexity-sensitive operations, [state modeling](./workflows/state-modeling.md) for lifecycle transitions, or [concurrency design](./workflows/concurrency-design.md) for shared-state ordering and synchronization.
2. DO load only procedures and point-of-need references justified by the constraints.

## Step 3 - Explain and validate the choice.

1. State the chosen structure, rejected alternatives, invariants preserved, and material tradeoffs; use #tool:execute for a benchmark only when scale or performance constraints require measured evidence.
2. Consult the [original specification](./references/original-spec.md) only when maintaining this package's scope or provenance.

</workflow>
