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
<critical_rules>
- MUST keep work within this subskill’s declared scope and its specific safety or authority constraints.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
</critical_rules>

<general_rules>
- SHOULD load listed references only at the procedure step that needs them.
- MAY report unavailable evidence or unresolved decisions as unknown.
</general_rules>

<risk_assessment>
Consume the Orchestrator-assigned `risk_level` through the parent domain skill; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases risk. Scale evidence depth, not authority or approvals.
</risk_assessment>

<rules>
- MUST follow this selected subskill only within its declared procedure and scope.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Describe the workload.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then List required operations, their frequency, ordering, duplicate, mutation, and identity semantics; note realistic size and memory constraints.

## Step 2 - Compare viable representations.

1. Use [data-structure guidance](../references/implementation-design/references/data-structures.md) to compare lookup, insertion, removal, traversal, and ordering costs.
2. Consult [pattern guidance](../references/implementation-design/references/design-patterns.md) only if variation or extension is an explicit current force; DO NOT wrap a simple choice in an abstraction.

## Step 3 - Select and explain.

1. Choose the simplest representation that preserves the invariants and workload; report material tradeoffs and any assumptions requiring confirmation.
</workflow>
