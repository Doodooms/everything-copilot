# Original Specification

## Raw intent

Produce grounded architecture decisions and implementation-ready briefs from repository evidence. Assess existing-codebase improvement requests without turning them into speculative refactors or implementation work.

## Normalized requirements

- Preserve Architect ownership of domain semantics, system topology, interfaces, integration, and structural tradeoffs.
- Use module/interface/seam/depth concepts to reason about caller leverage, cohesion, testability, and change locality.
- Use repository evidence such as requirements, code paths, tests, and relevant change history to justify proposals.
- Compose domain modeling only for bounded terminology, context-glossary, or ADR work; validate the child return and resume the parent workflow.

## Constraints and resolved decisions

- Do not implement, create mandatory HTML reports, use fixed parallel-subagent counts, or impose absolute vocabulary bans.
- Preserve the existing Architect/Planner/Implementer ownership boundaries.
- Imported architecture-designing content was treated as source inspiration and rewritten for this workspace; no source template or prose is retained.
- Date: 2026-09-24.
