# Data structures

Choose by required operations and semantics, not familiarity.

- List/array: ordered traversal and indexed access; search and middle insertion are linear unless maintained separately.
- Set/map: uniqueness or key lookup; account for ordering, hashing, mutation, and memory.
- Queue/deque: FIFO or two-ended operations; preserve fairness and ordering requirements.
- Heap: repeated priority selection; does not provide full sorted traversal.
- Tree: ordered/range lookup or hierarchical traversal when balancing and update costs are justified.
- Graph: explicit relationships and reachability when the domain is genuinely graph-shaped.
- Composite/indexed form: add only when measured or specified access patterns repay synchronization and consistency cost.
