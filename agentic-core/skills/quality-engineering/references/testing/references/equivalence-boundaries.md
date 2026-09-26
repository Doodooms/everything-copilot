# Equivalence and boundaries

Partition inputs by behavior, then choose representatives at meaningful transitions.

- Include lower/upper bounds, empty and singleton cases, invalid values, and overflow or saturation only when the contract permits them.
- Cover state transitions and failure paths that can change observable behavior.
- For broad input spaces, express a stable invariant as a property when the repository's existing test tooling supports it.
- For concurrent behavior, assert the allowed outcomes and shared invariants rather than assuming a particular scheduler order.
- Include negative cases when rejection or absence is a current contract, not merely because a removed implementation once existed.
- Avoid redundant examples from the same equivalence class unless they exercise a distinct risk.
