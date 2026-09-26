# Semantic foundations

Use these distinctions only when losing one could change reasoning, behavior, validation, or future change:

| Distinction | Keep separate |
|---|---|
| Model / world | A model is a purposeful, incomplete representation. |
| Problem / solution space | Domain meaning and expected behavior differ from software structure and implementation. |
| Ontology / schema | Kinds of things and their meaning differ from storage shape; data is not complete knowledge of reality. |
| Identity / state | What remains the same differs from its current condition. |
| Entity / value | Independent identity differs from interchangeable value. |
| State / event / transition | A condition differs from an occurrence and the change between conditions. |
| `is-a` / `part-of` | Taxonomic classification differs from composition; model either as typed relations when material. |
| Fact / assumption / hypothesis / unknown / decision | Evidence, provisional belief, testable proposition, missing knowledge, and authorized choice are distinct; do not silently promote one into another. |
| World state / system knowledge | What is true differs from what the system knows about it. |
| False / unknown | A negative fact differs from missing knowledge; make open-world or closed-world assumptions explicit when they affect behavior. |
| Semantic / technical topology | Domain relationships differ from software dependencies. |
| Precedence / causality / requirement | A happening before another differs from causing it or being required for it. |
| Actual / possible / required / forbidden | An observed state differs from an allowed possibility or a normative constraint. |
| Timeless / temporal fact | A fact may depend on valid time, observation time, or an interval. |
| Context-bound reference | Resolve material terms such as `current`, `active`, or `owner` to their time, actor, scope, or referent. |
| Syntax / semantics | Valid form differs from intended meaning. |
| Consistency / completeness | No contradiction does not imply sufficient coverage. |

The canonical `SPEC.semantic_model` is sparse and purpose-driven. Model a distinction only when losing it could affect reasoning, behavior, validation, or future change; do not require UML or expand it into a formal ontology. Use stable IDs for concepts, relations, states, events, transitions, invariants, contracts, assumptions, hypotheses, and unknowns. Keep provenance and fact-versus-inference status where they affect a decision; user-owned decisions remain in the canonical specification.

Domain use cases and diagrams are views of the semantic model, not alternate sources of truth. Keep the project/domain model separate from the Agentic Workflow system ontology.
