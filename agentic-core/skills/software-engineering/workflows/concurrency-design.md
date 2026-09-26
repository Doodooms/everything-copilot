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

## Step 1 - State the concurrency contract.

1. Identify shared state, concurrent actors, allowed interleavings, required ordering/visibility, consistency, and failure behavior.

## Step 2 - Select ownership and synchronization.

1. Use [concurrency guidance](../references/implementation-design/references/concurrency-primitives.md) to choose the simplest ownership, synchronization, queueing, or transactional model that preserves the contract.
2. Consult [state-model guidance](../references/implementation-design/references/state-machines.md) when operations change lifecycle state; keep critical sections and shared mutation narrow.

## Step 3 - Make risks explicit.

1. State the invariant, synchronization boundary, deadlock or contention risks, and required concurrency validation; MUST NOT claim race-freedom from inspection alone.
