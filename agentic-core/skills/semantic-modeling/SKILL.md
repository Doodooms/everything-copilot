---
name: semantic-modeling
description: "WHAT: Establish a sparse, evidence-grounded model of the problem space. USE FOR: material domain changes involving concepts, terminology, identity, relationships, lifecycle, invariants, contracts, assumptions, or unknowns. DO NOT USE FOR: product decisions, technical architecture, implementation, or mandatory modeling of trivial work."
user-invocable: false
metadata:
  creation-date: 2026-09-26
  creator: Doodooms
license: MIT
---

<critical_rules>

- MUST keep approved product intent and canonical terminology in the Orchestrator-owned specification.
- MUST NOT invent product facts, decide unresolved user tradeoffs, or model distinctions that cannot affect downstream reasoning.

</critical_rules>

<general_rules>

- SHOULD model only distinctions whose loss could affect behavior, validation, architecture, testing, or future change.
- MAY propose durable glossary or ADR updates when the approved task assigns them.
- MUST propose an ADR only when changing the choice later would be materially costly, future readers would not infer the decision, and a real alternative was selected for a reason; an ADR remains a supporting view of the approved specification.
- Create context/ADR directories only for an approved entry that is ready to record, and follow the repository's established naming and document structure.

</general_rules>

<risk_assessment>

Consume the Orchestrator-assigned `risk_level`; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases impact, exposure, uncertainty, or irreversibility. Risk scales modeling and evidence depth, not authority or approvals.

</risk_assessment>

<rules>

- The current SDD `SPEC.semantic_model` is the only canonical project problem-space model; this skill MUST NOT create a parallel ontology or task store.
- Distinguish problem-space semantics from technical topology; unresolved product meaning returns to the Orchestrator, and solution structure belongs to Architect.
- DO select the [problem-space workflow](./workflows/problem-space.md) only when a material semantic distinction is needed.

</rules>

<admission>

## ACCEPT

- Establish or revise project semantics needed to make a material requirement, acceptance criterion, or invariant precise.
- Reconcile terminology, identity, relationships, lifecycle, contracts, assumptions, or unknowns against current project evidence.

## REJECT

- Unresolved product intent or user-owned tradeoff -> `orchestrator`.
- Technical boundaries, interfaces, persistence, or technology choices -> `architect`.
- Delivery decomposition -> `planner`.
- Implementation -> `implementer`.

</admission>

<workflow>

## Step 1 - Establish the semantic boundary.

1. Consume the approved objective, current SPEC revision, assigned `risk_level`, and existing semantic/context artifacts; inspect only evidence relevant to the proposed distinctions.
2. Separate observed facts, approved decisions, assumptions, hypotheses, and unknowns. Return unresolved user-owned decisions to the Orchestrator.

## Step 2 - Model only decision-relevant distinctions.

1. Use the [semantic foundations](./references/semantic-foundations.md) when a distinction affects the task.
2. Propose only the needed concepts, identity, relationships, states, events, transitions, invariants, contracts, terminology, assumptions, and unknowns in the existing `SPEC.semantic_model`.
3. Treat use cases and diagrams as views of the model, not competing sources of truth. Do not require a model for trivial or non-semantic work.

## Step 3 - Return a specification-ready delta.

1. Return stable semantic IDs, definitions, evidence/provenance, linked REQ/AC IDs where material, unresolved questions, and the smallest next decision.
2. The Orchestrator owns approval and writes the result into the canonical specification. Update `CONTEXT.md` or an ADR only when the current handoff authorizes that documentation.

</workflow>
