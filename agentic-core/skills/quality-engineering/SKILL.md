---
name: quality-engineering
description: "WHAT: Design, assess, and independently falsify software behavior and its evidence. USE FOR: test design or review, adversarial QA, unknown runtime failures, browser journeys, code review, language-level review, or measurable agent evaluations. DO NOT USE FOR: production repair, architecture decisions, or final delivery acceptance."
user-invocable: false
metadata:
  creation-date: 2026-09-26
  creator: Doodooms
license: MIT
---

<critical_rules>

- MUST derive quality work from current observable contracts and return reproducible evidence for material findings.
- MUST NOT repair production behavior or replace the Reviewer as the final acceptance owner.

</critical_rules>

<general_rules>

- SHOULD prefer the cheapest high-signal procedure that can falsify a plausible defect.

</general_rules>

<risk_assessment>

Consume the Orchestrator-assigned `risk_level`; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases impact, exposure, uncertainty, or irreversibility. Risk scales evidence depth, not authority or approvals.

</risk_assessment>

<rules>

- QA owns runtime diagnosis, independent falsification, and test-surface changes; Reviewer owns final acceptance and static security-design review.
- DO select a procedure by its admission and the current evidence; use the separate `security` domain for security-specific methods.

</rules>

<workflow>

## Step 1 - Assess risk and choose a quality procedure.

1. DO consume the assigned `risk_level`, then select only a matching workflow:
   - [test-design](./workflows/test-design.md) to design behavior tests and their oracle.
   - [test-quality-review](./workflows/test-quality-review.md) to assess regression coverage and test adequacy.
   - [end-to-end](./workflows/end-to-end.md) for browser-visible behavior or complete user journeys.
   - [adversarial-testing](./workflows/adversarial-testing.md) to falsify completed behavior independently.
   - [failure-analysis](./workflows/failure-analysis.md) for an observed unknown runtime failure.
   - [code-review](./workflows/code-review.md) for a bounded completed diff.
   - [language-review](./workflows/language-review.md) for non-trivial language-specific risks.
   - [eval-harness](./workflows/eval-harness.md) when acceptance depends on measurable agent/skill behavior.

## Step 2 - Apply the selected procedure.

1. Follow the selected workflow directly and use the smallest relevant test surface; return confirmed production defects to their owning implementation or operations agent.

## Step 3 - Return evidence.

1. Report scope, methods, exact commands and outcomes, reproducible defects, coverage gaps, and residual risk; distinguish QA verdict from Reviewer approval.

</workflow>
