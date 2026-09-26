---
id: architecture-design
description: 'Apply the architecture-design method: system boundaries, domain semantics,
  module interfaces, technology choices, migrations, scalability, or evidence-led
  architecture improvement.'
invoke_for:
- system boundaries, domain semantics, module interfaces, technology choices, migrations,
  scalability, or evidence-led architecture improvement
avoid_for:
- raw requirements, delivery sequencing, implementation, runtime diagnosis, or final
  review
references:
  - ../references/architecture-design/references/ADR-FORMAT.md
---

## Step 1 - Establish structural evidence.

1. Read the approved objective, current architecture notes, relevant domain terms, owning interfaces, data models, integration points, tests, and affected paths.
2. Use #tool:search to trace the current execution or dependency path; inspect repository history only when repeated changes or churn help prioritize an architecture-improvement request.
3. Read the [architecture guide](../references/architecture-design/references/guide.md) only when its focused decision checklist is needed.

## Step 2 - Model or compare the design.

1. State the responsibility, semantic contracts consumed, proposed interface, dependencies, trust or failure boundaries, and testable outcomes.
2. For a requested architecture-improvement scan, select candidates from observed change or verification friction, then compare current behavior spread with the proposed responsibility and interface; do not produce speculative refactors.
3. For unresolved product terminology or domain meaning, return the gap to the Orchestrator for the canonical specification or `semantic-modeling`; MUST NOT assign product meaning as an architecture decision.
4. Compare alternatives only on decision-relevant criteria. State reversibility, compatibility, operational impact, assumptions, and rejected options where these change the recommendation.

## Step 3 - Return the architecture brief.

1. If the handoff authorizes recording an approved architecture choice that is costly to reverse, surprising without context, and selected over a material alternative, use the [ADR format](../references/architecture-design/references/ADR-FORMAT.md); otherwise return the decision in the brief without creating an ADR.
2. Return the selected structure, responsibilities, interfaces, dependencies, affected files or modules, implementation constraints, tradeoffs, risks, assumptions, non-goals, and open decisions.
3. For architecture-improvement work, rank only evidenced candidates and identify the strongest next decision; do not turn the scan into implementation or a delivery plan.
