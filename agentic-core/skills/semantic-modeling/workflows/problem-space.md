---
id: problem-space
description: Establish or revise a sparse, canonical model of project meaning before solution structure is chosen.
invoke_for:
  - material behavior changes whose concepts, identity, relationships, lifecycle, or invariants affect requirements
  - semantic ambiguity or contradiction that blocks stable acceptance criteria
avoid_for:
  - trivial changes with known behavior
  - technical architecture or unresolved product decisions
references:
  - ../references/semantic-foundations.md
  - ../references/context-format.md
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
## Step 1 - Inspect the current problem definition.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Read the current specification, relevant project context, and the smallest code or product-evidence slice that can confirm or contradict the terminology.
2. Keep the Orchestrator-assigned `risk_level`; report evidence for escalation without reclassifying the task.
3. Distinguish facts, approved decisions, assumptions, hypotheses, and unknowns. Return a material user-owned ambiguity instead of guessing.

## Step 2 - Build the sparse semantic delta.

1. Add only distinctions needed to reason about the approved behavior: canonical terms, concepts, identity and granularity; typed relations and material cardinalities; relevant states, events, transitions, invariants, and contracts; and material assumptions, hypotheses, or unknowns.
2. Give modeled items stable IDs and concise evidence/provenance. Link semantic IDs to REQ/AC IDs only where the relationship is material.
3. Distinguish `is-a` from `part-of`; represent taxonomy and composition as typed relations. Model preconditions, effects, failure semantics, time, causality, modality, and context only when they change expected behavior.
4. Separate world state from system knowledge; distinguish facts, assumptions, hypotheses, unknowns, and authorized decisions. Do not treat absence as false or an assumption as an invariant.
5. Use a use case to expose actor, goal, preconditions, main/alternate/failure flow, postconditions, affected concepts, events, or invariants when useful; keep the semantic model canonical.
6. Treat UML/Mermaid/PlantUML diagrams as regenerable views. Assign domain-state meaning to the problem-space model and implementation-state structure to Architect.

## Step 3 - Return the current-specification update.

1. Return the proposed `SPEC.semantic_model` delta and any affected REQ/AC IDs, evidence, assumptions, unknowns, contradictions, and open product decisions.
2. Identify any semantic revision that may stale downstream architecture, plan, tasks, implementation, or validation; reuse the existing SDD dependency graph.
3. If the handoff explicitly authorizes recording approved project vocabulary, use the [context format](../references/context-format.md); the current `SPEC.semantic_model` remains canonical and the glossary is only a compact supporting view.
4. If the handoff explicitly authorizes an ADR, record only the already-approved decision in the repository's established ADR location and format. Propose an ADR only when changing the choice later is materially costly, future readers would not infer the decision, and a real alternative was selected for a reason; keep it as a supporting view of `SPEC.semantic_model`.
5. Do not create a second knowledge graph, require exhaustive modeling, or edit the specification unless the handoff explicitly grants that authority.
</workflow>
