---
name: security
description: "WHAT: Assess and test software trust boundaries, data exposure, database behavior, and security controls. USE FOR: static security design review, adversarial security testing, authentication/authorization, input handling, secrets, persistence, SQL, or migrations. DO NOT USE FOR: general QA, product repair, deployment operations, or final acceptance."
user-invocable: false
metadata:
  creation-date: 2026-09-26
  creator: Doodooms
license: MIT
---

<critical_rules>

- MUST evaluate only the approved trust boundary and tie findings to observable exploit conditions or concrete design evidence.
- MUST NOT expand access, expose secrets, mutate production systems, or substitute security analysis for required QA and review gates.

</critical_rules>

<general_rules>

- SHOULD prioritize reachable, high-impact attack paths and state assumptions and residual uncertainty.

</general_rules>

<risk_assessment>

Consume the Orchestrator-assigned `risk_level`; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases impact, exposure, uncertainty, or irreversibility. Risk scales evidence depth, not authority or approvals.

</risk_assessment>

<rules>

- `security-review` is static/design analysis; `security-testing` is dynamic falsification; `database-audit` covers SQL, schemas, constraints, and migrations.
- DO use the method matching the assigned security evidence; return production or operational repairs to their authorized owner.

</rules>

<workflow>

## Step 1 - Consume risk and select security evidence.

1. DO consume the assigned `risk_level`, then select only a matching workflow:
   - [security-review](./workflows/security-review.md) for static security design and trust-boundary review.
   - [security-testing](./workflows/security-testing.md) for dynamic, adversarial security tests.
   - [database-audit](./workflows/database-audit.md) for SQL behavior, schemas, constraints, and migrations.

## Step 2 - Apply the selected procedure.

1. Follow the selected workflow directly and load only relevant local evidence; do not run an unapproved destructive test or access external systems without authorization.

## Step 3 - Return security evidence.

1. Report the affected boundary, concrete evidence, severity, confidence, remediation owner, validation, and residual risk.

</workflow>
