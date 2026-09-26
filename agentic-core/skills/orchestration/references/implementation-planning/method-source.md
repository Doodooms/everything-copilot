---
name: implementation-planning
description: "WHAT: Convert an approved software change into a dependency-aware implementation plan. USE FOR: decomposing requirements into phases, task ownership, file scope, sequencing, and validation. DO NOT USE FOR: product decisions, architecture ownership, implementation, QA execution, or final acceptance."
user-invocable: false
metadata:
  creation-date: 2026-09-23
  creator: Doodooms
---

<definitions>

- **plan task**: A bounded, independently verifiable unit of work with an owner, scope, dependencies, and completion evidence.
- **phase exit check**: Evidence required before dependent work may begin; it does not redefine specification acceptance.
- **critical path**: The dependency chain that determines the earliest completion of the approved work.

</definitions>

<admission>

Classify the request into exactly one outcome: `ACCEPT` or `REJECT`.

## ACCEPT

- Decompose a current, approved specification and architecture into implementation phases and tasks.
- Identify dependencies, safe parallel work, file/component scope, handoffs, and risk-proportional validation.

## REJECT

- Unresolved or changed product intent -> `orchestrate`.
- Architecture, domain, or technology decisions -> `architect`.
- Code or test implementation -> `implementer`.
- Runtime diagnosis or adversarial execution -> `quality-assurance`.
- Final technical acceptance -> `reviewer`.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"implementation-planning","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<rules>

- Plan only from the current approved specification revision and accepted architecture decisions.
- Every plan task MUST reference applicable `REQ-*`, `AC-*`, and `ADR-*` IDs where provided; the Planner MUST NOT rewrite or weaken product acceptance.
- Every task MUST have a bounded objective, owner, file/component scope, dependencies, and observable completion evidence.
- Dependencies MUST be acyclic. Parallelize only tasks with disjoint write ownership and satisfied prerequisites.
- Validation MUST target the changed behavior and risk; do not add gates without a stated reason.
- The plan MUST record assumptions, blockers, cross-task integration points, and the exact next handoff.
- Use native `todo` items for the major planning phases only; task definitions and dependencies belong in the returned plan, not duplicated as many UI todos.

</rules>

<workflow>

## Step 1 - Establish planning inputs.

1. Use #tool:read to inspect the approved specification, architecture decisions, repository constraints, existing plan, and requested delivery scope.
2. Use #tool:todo to create or update native todos for the three major planning steps; do not dispatch implementation or invent missing acceptance criteria.
3. Stop and return a blocker if required approval, specification revision, or architecture decisions are missing or stale.

## Step 2 - Build the executable task graph.

1. Use #tool:search to map each in-scope requirement and acceptance criterion to the smallest coherent tasks and relevant implementation surfaces.
2. For each task, define ID, objective, owner, allowed files/components, inputs, dependencies, expected output, validation, and phase exit criteria.
3. Sequence prerequisite work first, identify safe parallel groups, and expose the critical path and cross-component integration risks.
4. Keep migrations, compatibility, rollout, rollback, and documentation obligations explicit when relevant.

## Step 3 - Return the plan.

1. Return specification/architecture revisions, task graph, phases, dependency edges, file ownership, validation commands, risks, assumptions, skipped work with rationale, and the next owner.
2. Confirm all acceptance criteria have an owning task or are explicitly marked existing behavior/not applicable with evidence.
3. Use #tool:todo to update planning todos from the returned evidence; leave implementation state to the Orchestrator and task ledger.

</workflow>

Source provenance: [original specification](./references/original-spec.md).