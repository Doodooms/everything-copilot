---
name: security-testing
description: "WHAT: Design and execute dynamic, adversarial security tests for a completed implementation. USE FOR: testing authentication, authorization, input handling, secrets, persistence, abuse paths, and trust-boundary behavior. DO NOT USE FOR: static security review, production fixes, architecture decisions, or final acceptance."
user-invocable: false
context: fork
compatibility: vscode 1.119.0+, github-copilot 1.119.0+
metadata:
  creation-date: 2026-09-23
  creator: Doodooms
license: MIT
---

<definitions>

- **security test surface**: The implementation paths, fixtures, harnesses, and runtime boundaries that can expose a security failure.
- **abuse case**: A realistic way an untrusted actor can violate confidentiality, integrity, availability, authorization, or accountability.
- **security test finding**: A reproducible security failure with affected surface, attack input or sequence, observed impact, and evidence.
- **security test verdict**: `pass | fail | blocked`; it reports the result of dynamic or adversarial testing, not final acceptance.

</definitions>

<rules>

- Work inside QA ownership: test and falsify security behavior without editing production implementation.
- Derive tests from the specification, trust boundaries, changed files, and existing security controls.
- Prefer reproducible tests with explicit attacker capability, input, state, expected control, and observed result.
- Separate confirmed findings from hypotheses, environment limitations, and missing evidence.
- Preserve secrets and personal data; use safe test values and redact sensitive output.
- Route static or design-oriented security review to the [security-review workflow](../../workflows/security-review.md) and production fixes to the Implementer.

</rules>

<admission>

## ACCEPT

- Design or execute adversarial security tests for a completed implementation.
- Test authentication, authorization, input validation, secret handling, injection, data isolation, persistence, rate limits, or trust-boundary behavior.
- Strengthen security fixtures, harnesses, or regression tests without changing production code.

## REJECT

- Static or design-oriented security review without runtime testing.
- Fix production code, configuration, or infrastructure.
- Make architecture or threat-model decisions without an implementation test surface.
- Make the final technical acceptance decision.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"security-testing","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<workflow>

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
   - Route confirmed production defects to the Implementer and static/design questions to the Reviewer using the [security-review workflow](../../workflows/security-review.md).

</workflow>
