# Concurrency primitives

Decide required ordering and ownership semantics before choosing a primitive.

- Mutex: exclusive access to a small invariant-preserving critical section; define acquisition order and release paths.
- Read/write lock: only when concurrent reads materially coexist with serialized writes and fairness is understood.
- Atomic: only for operations supported by the memory model; an atomic field does not make a multi-field invariant atomic.
- Queue or message passing: useful when one owner can serialize state mutation and callers can accept the resulting ordering.
- Transaction: use when a storage boundary already supplies atomicity for the relevant invariant.
- Ownership transfer: prefer single-owner designs when they remove shared mutation without violating required concurrency.
- Name ordering, visibility, deadlock, contention, cancellation, and failure risks explicitly.
