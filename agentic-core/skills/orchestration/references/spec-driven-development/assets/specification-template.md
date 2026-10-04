# Specification: [short objective]

Use durable IDs below only when supplied or allocated by the Control Plane for a workflow that depends on them. For standalone local work, omit ID/revision fields and carry the request, behavior statements, and observable outcomes directly in the active handoff/session. Do not invent SPEC, REQ, or AC IDs.

## Identity

- `id`: [Control Plane allocated SPEC ID; otherwise omit]
- `revision`: [Control Plane revision; otherwise omit]
- `status`: [draft | ready | blocked]
- source request: [user request reference]
- updated at: [timestamp or repository-standard revision metadata]

## Objective and intent

- Objective: [observable outcome]
- User intent / rationale: [why this behavior is required]

## Requirements

- [Requirement; add a `REQ-*` identifier only when supplied or allocated by the Control Plane]
  - Statement: [required behavior/property; WHAT, not implementation]
  - Rationale: [reason]
  - Priority: [must | should | could]

## Acceptance criteria

- [Acceptance criterion; add an `AC-*` identifier and linked `REQ-*` only when supplied or allocated by the Control Plane]
  - Requirements: [linked supplied/allocated IDs, or omit for standalone work]
  - Statement: [falsifiable observation, including relevant boundary/failure behavior]

## Constraints

- [mandatory solution or execution boundary]

## Non-goals

- [explicitly excluded behavior]

## Assumptions

- [evidence-backed assumption and its source]

## Open decisions

- id: [DECISION-001]
  - Decision: [unresolved user-owned choice]
  - Material impact: [behavior, scope, acceptance, architecture, or risk]
  - Required: [true | false]
  - Resolved: [true | false]

## Optional semantic model

Include only for material domain changes where losing a distinction could affect behavior, validation, architecture, testing, or future change. Keep it sparse; omit unused collections.

Use typed `relations` for taxonomy (`is-a`) and composition (`part-of`) rather than duplicating those edges in separate graphs. Keep user-owned decisions in `open_decisions`; include concise per-item provenance where it affects confidence or downstream decisions. Put a claim in `hypotheses` only while it remains a testable, unconfirmed proposition.

```yaml
semantic_model:
  schema_version: 1
  scope: "[bounded problem-space scope]"
  terminology:
    - term: "[canonical term]"
      meaning: "[approved meaning]"
      aliases: []
      provenance: "[evidence or decision]"
  concepts:
    - id: CONCEPT-001
      term: "[name]"
      kind: "[entity | value | actor | resource | other]"
      meaning: "[decision-relevant meaning]"
      identity: "[what makes it the same thing over time, if relevant]"
      granularity: "[level of detail needed for the behavior, if relevant]"
      provenance: "[evidence or decision]"
  relations:
    - id: REL-001
      source_concept: CONCEPT-001
      predicate: "[typed relationship]"
      target_concept: CONCEPT-002
      meaning: "[relationship meaning, when not clear from predicate]"
      cardinality: "[optional, when material]"
  states:
    - id: STATE-001
      concept_id: CONCEPT-001
      name: "[state]"
  events:
    - id: EVENT-001
      name: "[occurrence]"
      concept_ids: [CONCEPT-001]
  transitions:
    - id: TRANSITION-001
      concept_id: CONCEPT-001
      from_state_id: STATE-001
      event_id: EVENT-001
      to_state_id: STATE-002
  invariants:
    - id: INV-001
      statement: "[required truth]"
      concept_ids: [CONCEPT-001]
  contracts:
    - id: CONTRACT-001
      statement: "[domain-visible contract]"
      preconditions: []
      postconditions: []
      failure_semantics: "[relevant failure behavior, if material]"
  assumptions:
    - id: ASSUMPTION-001
      statement: "[provisional belief]"
      source: "[basis and uncertainty]"
  hypotheses:
    - id: HYPOTHESIS-001
      statement: "[testable, unconfirmed proposition]"
      source: "[evidence or inference]"
  unknowns:
    - id: UNKNOWN-001
      question: "[unresolved material question]"
      owner: "[decision owner]"
```

Concepts, relations, events, states, transitions, invariants, and contracts represent the approved model; do not add a separate `facts` collection. Use optional `provenance` on any material item. Semantic assumptions should receive stable IDs only when they need semantic traceability; do not duplicate the same prose already recorded in the specification.

## Change notes

- [material change summary and affected IDs for each later revision]
