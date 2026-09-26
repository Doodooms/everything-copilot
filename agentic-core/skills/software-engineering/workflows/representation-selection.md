---
id: representation-selection
description: Select a local data representation from the operations and access patterns
  it must support.
invoke_for:
- choose among list, map, set, queue, tree, graph, index, or composite representations
- improve local lookup, ordering, mutation, or iteration structure
avoid_for:
- routine storage with no material alternative
- system or persistence architecture decisions
references:
  - ../references/implementation-design/references/data-structures.md
  - ../references/implementation-design/references/design-patterns.md
---

## Step 1 - Describe the workload.

1. List required operations, their frequency, ordering, duplicate, mutation, and identity semantics; note realistic size and memory constraints.

## Step 2 - Compare viable representations.

1. Use [data-structure guidance](../references/implementation-design/references/data-structures.md) to compare lookup, insertion, removal, traversal, and ordering costs.
2. Consult [pattern guidance](../references/implementation-design/references/design-patterns.md) only if variation or extension is an explicit current force; DO NOT wrap a simple choice in an abstraction.

## Step 3 - Select and explain.

1. Choose the simplest representation that preserves the invariants and workload; report material tradeoffs and any assumptions requiring confirmation.
