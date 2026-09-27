---
id: concurrency-design
description: Select synchronization and ownership semantics for shared or concurrently
  accessed state.
invoke_for:
- shared mutable state or concurrent writers
- ordering-sensitive operations or consistency guarantees
- choose between locking, atomics, queues, transactions, or ownership transfer
avoid_for:
- sequential code without a concurrency contract
- runtime race diagnosis or performance profiling
references:
  - ../references/implementation-design/references/concurrency-primitives.md
  - ../references/implementation-design/references/state-machines.md
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
## Step 1 - State the concurrency contract.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Identify shared state, concurrent actors, allowed interleavings, required ordering/visibility, consistency, and failure behavior.

## Step 2 - Select ownership and synchronization.

1. Use [concurrency guidance](../references/implementation-design/references/concurrency-primitives.md) to choose the simplest ownership, synchronization, queueing, or transactional model that preserves the contract.
2. Consult [state-model guidance](../references/implementation-design/references/state-machines.md) when operations change lifecycle state; keep critical sections and shared mutation narrow.

## Step 3 - Make risks explicit.

1. State the invariant, synchronization boundary, deadlock or contention risks, and required concurrency validation; MUST NOT claim race-freedom from inspection alone.
</workflow>
