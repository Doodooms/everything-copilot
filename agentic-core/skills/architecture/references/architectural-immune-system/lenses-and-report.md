# Architectural Immune System: lens and report guide

This reference supports the `architectural-immune-system` workflow. It defines the focused questions for each analysis perspective and the final report format; the workflow remains the complete procedure.

## Six analysis modes

Apply each mode to the same proposal and evidence:

- **Failure analysis:** identify systemic failure vectors, not only immediate defects.
- **Entropy accumulation:** trace how local exceptions, conceptual overload, or compatibility debt compound over time.
- **Governance erosion:** find how enforcement, ownership, and review practices may weaken under pressure.
- **Scale transition:** identify assumptions that stop holding as users, components, data, or coordination grow.
- **Identity drift:** detect responsibility expansion, boundary blur, and transformation into a broader system than intended.
- **Long-horizon systemic stress:** trace gradual loss of coherence, determinism, maintainability, or boundary integrity.

## Seven adversarial perspectives

Use these as independent prompts when specialist dispatch is available, or as separate analysis passes:

| Perspective | Look for |
|---|---|
| Semantic purity | Transport leakage, provider vocabulary, backend assumptions, runtime-specific abstractions, or infrastructure terms inside semantic layers. |
| Determinism | Wall-clock dependencies, mutable globals, hidden state, non-replayable side effects, ordering instability, or implicit concurrency assumptions. |
| Governance erosion | Temporary exceptions, convenience helpers, compatibility shortcuts, emergency paths, review fatigue, or undocumented coupling becoming normal. |
| Scale transition | Registry overload, orchestration bottlenecks, graph growth, cognitive scaling limits, coordination complexity, or governance that cannot scale. |
| Coupling | Bidirectional dependencies, implicit orchestration, semantic/runtime fusion, kernel inflation, dependency cycles, or ownership collapse. |
| Identity drift | Responsibility accumulation, boundary expansion, subsystem absorption, orchestration creep, or conceptual dilution. |
| Long-horizon entropy | Normalized compromises, weakening invariants, growing semantic ambiguity, governance fatigue, or abstraction erosion over 18–36 months. |

Each perspective returns a concise failure narrative, root assumption, entropy vector, normalization path, early warning signals, and concrete hardening strategy. Distinguish observed evidence from inference.

## Mandatory synthesis sections

- Most likely corruption vector.
- Most dangerous long-horizon failure.
- Hidden architectural assumption.
- Governance weak point.
- Scale inflection point.
- Identity drift trajectory.
- Architectural hardening plan, with each recommendation mapped to a specific failure vector.
- Permanent immune responses, such as architecture tests, invariant enforcement, semantic linting, governance gates, replay verification, coupling scans, deterministic execution audits, or ownership-boundary checks.

## HTML report presentation

Present a systems control room with a dark theme, high signal density, and scannable architecture structure. Use severity indicators, governance risk indicators, a collapse timeline, perspective cards, and systemic heatmaps when the findings support them. Keep these report sections visible: executive synthesis, collapse timeline, entropy vectors, perspective findings, governance weaknesses, scale-transition risks, identity drift, hardening plan, and immune responses.

## Writing style and closing principle

Be precise, adversarial, systemic, architecture-first, long-horizon, and governance-aware. Avoid motivational language, vague risk statements, generic startup advice, surface-level critique, and performative pessimism. The goal is structural clarity: technical failure may be survivable; gradual conceptual corruption can destroy the system's identity and coherence.
