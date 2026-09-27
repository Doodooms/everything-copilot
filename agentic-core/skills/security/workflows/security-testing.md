---
id: security-testing
description: 'Apply the security-testing method: testing authentication, authorization,
  input handling, secrets, persistence, abuse paths, and trust-boundary behavior.'
invoke_for:
- testing authentication, authorization, input handling, secrets, persistence, abuse
  paths, and trust-boundary behavior
avoid_for:
- static security review, production fixes, architecture decisions, or final acceptance
references: []
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
## Step 1 - Establish the attack surface

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Read the specification, changed files, existing tests, fixtures, and security-relevant configuration.
   - Identify actors, attacker capabilities, assets, trust boundaries, and security invariants.
   - Reuse the narrowest relevant security scenarios; do not expand into unrelated product testing.

## Step 2 - Execute adversarial checks

1. Use #tool:execute to run the cheapest high-signal tests first, then add focused probes for realistic abuse cases.
   - Cover malformed, boundary, replayed, unauthorized, cross-tenant, injected, oversized, and missing inputs when applicable.
   - Verify both rejection behavior and that failures do not leak secrets, internal data, or unsafe state changes.
   - Add or strengthen QA-only fixtures, harnesses, or regression tests when they create durable evidence.
2. Reproduce and minimize each failure, distinguishing implementation defects from test defects and environment blockers.

## Step 3 - Return the QA security evidence

1. Return a structured handoff with the verdict, scope, attacker model, commands, tests changed, findings, evidence gaps, and residual risk.
   - Include `changed_files` and focused `commit_shas` when QA-only assets were modified.
   - Route confirmed production defects to Implementer and static/design questions to Reviewer through the parent `security` skill.
</workflow>
