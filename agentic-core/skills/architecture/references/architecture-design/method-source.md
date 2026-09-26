---
name: architecture-design
description: "WHAT: Produce evidence-grounded technical architecture decisions and implementation-ready design briefs. USE FOR: system boundaries, module interfaces, technology choices, migrations, scalability, or evidence-led architecture improvement. DO NOT USE FOR: problem-space semantics, raw requirements, delivery sequencing, implementation, runtime diagnosis, or final review."
user-invocable: false
metadata:
  creation-date: 2026-09-24
  creator: Doodooms
---

<definitions>

- **architecture brief**: A decision-ready description of structure, responsibilities, interfaces, dependencies, tradeoffs, risks, assumptions, and non-goals.
- **module**: A cohesive unit of behavior presented through an interface; its scale may be a function, package, or larger system.
- **interface / seam**: The observable contract callers depend on, and the point at which an implementation can be changed without rewriting those callers.
- **depth / locality**: Depth is useful behavior behind a comprehensible interface; locality is the degree to which related change and verification stay together.
- **architecture improvement candidate**: A proposed structural change supported by observed friction, repeated change, defects, or difficult verification rather than hypothetical future needs.

</definitions>

<admission>

## ACCEPT

- Design or compare technical structure, responsibilities, interfaces, dependencies, technology choices, migration shape, or scalability for an approved objective.
- Assess a requested codebase-architecture improvement using repository evidence and return a bounded set of actionable candidates.

## REJECT

- Unresolved product intent or requirement ownership -> `orchestrator`.
- Delivery sequencing, tasks, or validation planning -> `planner`.
- Code or test changes -> `implementer`.
- Runtime diagnosis or adversarial verification -> `quality-assurance`.
- Final technical acceptance -> `reviewer`.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"architecture-design","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<rules>

- MUST ground decisions in approved requirements, current repository structure, existing interfaces, and relevant decisions.
- MUST consume approved problem-space semantics; return semantic ambiguity to the Orchestrator rather than redefining it.
- MUST distinguish domain invariants owned by the specification from technical invariants owned by architecture.
- MUST identify the behavior and responsibility behind a proposed interface, the callers it simplifies, and the behavior that tests should observe through it.
- SHOULD deepen a module when a cohesive responsibility can hide complexity behind a smaller stable interface; assess whether a new seam concentrates change or merely adds indirection.
- MUST NOT add abstractions, adapters, or layers only for hypothetical variation, test convenience, or vocabulary purity.
- For codebase-improvement requests, MUST use evidence such as repeated changes, concrete call-path friction, duplicated decisions, defects, or hard-to-exercise behavior; do not infer architecture debt from size or style alone.
- SHOULD prioritize a small number of consequential candidates over an exhaustive repository survey. Compare current and proposed responsibility, interface, caller impact, verification boundary, and tradeoffs.
- MUST NOT implement the design, open files in external viewers, require HTML/CDN output, or spawn a fixed number of parallel agents.
- SHOULD record an ADR only when the decision is costly to reverse, surprising without context, and chosen among material alternatives.
- When domain terms, a project glossary, or ADR recording need their own bounded treatment, select the `domain-modeling` workflow in this `architecture` domain and validate its return before resuming.

</rules>

<workflow>

## Step 1 - Establish structural evidence.

1. Read the approved objective, current architecture notes, relevant domain terms, owning interfaces, data models, integration points, tests, and affected paths.
2. Use #tool:search to trace the current execution or dependency path; inspect repository history only when repeated changes or churn help prioritize an architecture-improvement request.
3. Read the [architecture guide](./references/guide.md) only when its focused decision checklist is needed.

## Step 2 - Model or compare the design.

1. State the responsibility, semantic contracts consumed, proposed interface, dependencies, trust or failure boundaries, and testable outcomes.
2. For a requested architecture-improvement scan, select candidates from observed change or verification friction, then compare current behavior spread with the proposed responsibility and interface; do not produce speculative refactors.
3. When resolving domain terminology, updating a project context glossary, or deciding whether an ADR is warranted, read the [composition contract](./references/composition.md), keep the bounded child context in the conversation, and select the [domain-modeling workflow](../../workflows/domain-modeling.md) from this package:
   - `objective`: the bounded domain terms, glossary update, or ADR question.
   - `inputs`: relevant requirements, current glossary/ADR paths, and code evidence.
   - `constraints`: preserve approved intent; do not design implementation or invent unresolved domain facts.
   - `expected_output`: status, resolved terms, evidence, proposed documentation changes, ADR candidacy, and unresolved decisions.
   - `resume_point`: this skill's Step 2, action 4, to incorporate validated domain output into the architecture brief.
   - After return, verify required fields; resume only on success and otherwise report the gap.
4. Compare alternatives only on decision-relevant criteria. State reversibility, compatibility, operational impact, assumptions, and rejected options where these change the recommendation.

## Step 3 - Return the architecture brief.

1. Return the selected structure, responsibilities, interfaces, dependencies, affected files or modules, implementation constraints, tradeoffs, risks, assumptions, non-goals, and open decisions.
2. For architecture-improvement work, rank only evidenced candidates and identify the strongest next decision; do not turn the scan into implementation or a delivery plan.

</workflow>

Source provenance: [original specification](./references/original-spec.md).
