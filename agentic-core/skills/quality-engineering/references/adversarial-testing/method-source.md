---
name: adversarial-testing
description: "WHAT: Try to falsify completed software behavior against its approved contract. USE FOR: independent QA, edge cases, integration failures, invalid states, and test-surface weakness. DO NOT USE FOR: production fixes, architecture decisions, routine implementation tests, static security review, or final acceptance."
user-invocable: false
metadata:
  creation-date: 2026-09-23
  creator: Doodooms
---

<definitions>

- **counterexample**: A reproducible observation where actual behavior violates an approved requirement, acceptance criterion, or invariant.
- **test-surface defect**: A missing, weak, misleading, or over-mocked test/harness that cannot detect a material regression.
- **falsification check**: A targeted test or experiment designed to expose a plausible contract violation.

</definitions>

<admission>

Classify the request into exactly one outcome: `ACCEPT` or `REJECT`.

## ACCEPT

- Independently test completed behavior against current approved requirements, acceptance criteria, architecture invariants, and test assumptions.
- Reproduce and minimize a behavior or test-surface failure and return evidence to its owner.

## REJECT

- Production implementation or repair -> `implementer`.
- Unknown runtime failure diagnosis without a completed behavior contract -> `failure-analysis`.
- Architecture or scope decision -> `architect` or `orchestrate`.
- Static security-design review -> `reviewer` using `security-review`.
- Final acceptance -> `reviewer`.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"adversarial-testing","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<rules>

- Test only against the current approved specification and implementation revision; record the IDs/revision exercised.
- Seek high-signal counterexamples, not test volume. Prioritize boundaries, invalid states, ordering, error paths, persistence, concurrency, compatibility, integrations, and abuse cases according to risk.
- Do not add tombstone tests whose only purpose is to assert that removed code, routes, fields, or features remain absent. Negative tests are appropriate when the failure or absence is itself a current API, security, or persistence contract.
- MUST NOT edit production code or change requirements to make a check pass.
- Test-surface edits MUST remain within tests, fixtures, harnesses, and benchmarks; report ownership ambiguity as a blocker.
- Use `security-testing` or `performance-profiling` only when the changed surface and risk warrant them; browser checks SHOULD reuse the repository's established end-to-end test surface.
- A pass means no material falsification was found within the tested scope; it MUST NOT be presented as final acceptance.
- Every failure report MUST contain a reproduction, expected/actual result, command/environment, evidence, affected requirement IDs, likely owner, and residual uncertainty.

</rules>

<workflow>

## Step 1 - Define the falsification surface.

1. Use #tool:read to inspect the current handoff, specification, relevant architecture decisions, changed files, immediate tests, and Implementer evidence.
2. Use #tool:todo to create or update one native todo for each major QA phase; do not create a todo per assertion or test case.
3. Derive plausible contract violations and select the smallest checks capable of exposing them.

## Step 2 - Execute independent checks.

1. Use #tool:execute to run focused boundary and error-path tests before broad suites; inspect assertions and fixtures for false confidence.
2. Exercise sequencing, integration, persistence, concurrency, compatibility, security, or performance only where applicable.
3. Reproduce and minimize each material failure; use #tool:edit to add durable test-surface protection only when authorized and useful.
4. Stop additional exploration when the correct owner has enough evidence to repair, unless directly related checks are cheap.

## Step 3 - Return the verdict and defect packet.

1. Return `pass`, `fail`, or `blocked`, the tested scope/revision, executed commands, outcomes, and untested risks.
2. For each failure, provide expected/actual behavior, reproduction, evidence, affected IDs, suspected owner, and next action.
3. Route product defects to Implementer, operational defects to DevOps, architecture/specification gaps to their owner, and test-surface defects to QA; use #tool:todo to update QA todos before routing.

</workflow>

Source provenance: [original specification](./references/original-spec.md).