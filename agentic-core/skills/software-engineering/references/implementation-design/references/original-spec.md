# Original specification

Create one local implementation-design subdomain for non-trivial representation, algorithm, lifecycle, and synchronization choices. The method begins with constraints, invariants, required operations, access/mutation patterns, and scale, then chooses the simplest structure that satisfies them.

Keep the subdomain below `architecture-design`: it does not own service/module boundaries, product semantics, or API contracts. Keep `tdd` responsible for test-first execution and `performance-profiling` responsible for diagnosis of measured runtime problems.

Use immediate workflows for representation selection, algorithm selection, state modeling, and concurrency design. Load only a matching workflow and its point-of-need reference; MUST NOT introduce standalone data-structure, algorithm, pattern, state-machine, or concurrency skills.
