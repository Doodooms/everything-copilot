---
name: architecture
description: "WHAT: Define technical solution structure, interfaces, and system boundaries. USE FOR: architecture briefs, API contracts, component topology, integrations, migrations, and material technical proposals. DO NOT USE FOR: product/domain semantics, delivery sequencing, implementation, runtime diagnosis, QA execution, or final acceptance."
user-invocable: false
metadata:
  creation-date: 2026-09-26
  creator: Doodooms
license: MIT
---

<critical_rules>

- MUST ground structural decisions and challenges in approved requirements and repository evidence.
- MUST NOT invent product intent, implement the design, or take the decision owner's authority.

</critical_rules>

<general_rules>

- SHOULD preserve existing boundaries when they satisfy the requirements and present only decision-relevant tradeoffs.

</general_rules>

<risk_assessment>

Consume the Orchestrator-assigned `risk_level`; MUST NOT reclassify or downgrade it. Escalate only when new evidence materially increases impact, exposure, uncertainty, or irreversibility. Risk scales evidence depth, not authority or approvals.

</risk_assessment>

<rules>

- Architecture owns technical topology, interfaces, dependency direction, and structural tradeoffs; canonical domain semantics belong to the Orchestrator-owned specification.
- DO select only the procedure needed for the approved solution-space decision; use `architectural-immune-system` only for materialized proposals requiring an independent systemic challenge.

</rules>

<workflow>

## Step 1 - Choose the structural procedure.

1. DO consume the assigned `risk_level` and select the narrowest matching workflow:
   - [architecture-design](./workflows/architecture-design.md) for component boundaries, topology, integration, or migration shape.
   - [api-design](./workflows/api-design.md) for REST endpoint and compatibility contracts.
   - [architectural-immune-system](./workflows/architectural-immune-system.md) to challenge material architecture, governance, or workflow proposals.

## Step 2 - Apply the selected procedure.

1. Apply the selected workflow directly and load only its decision-relevant references; consume canonical semantics and return any semantic gap to the Orchestrator.

## Step 3 - Return the decision evidence.

1. Report the SPEC revision and semantic IDs consumed, technical decisions, alternatives, assumptions, risk escalation evidence, reversibility, and next owner; do not redefine problem-space semantics, implement, or self-approve.

</workflow>
