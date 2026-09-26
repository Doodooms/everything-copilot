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

## Step 1 - Establish the attack surface

1. Read the specification, changed files, existing tests, fixtures, and security-relevant configuration.
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
