---
name: code-review
description: "WHAT: Review a completed code change for grounded correctness, regression, maintainability, and compatibility findings. USE FOR: static review of a bounded diff and its consequential call sites. DO NOT USE FOR: implementation, runtime diagnosis, adversarial test execution, dedicated security review, or final acceptance."
user-invocable: false
metadata:
  creation-date: 2026-09-23
  creator: Doodooms
---

<definitions>

- **material finding**: An evidence-backed issue that can change correctness, security, compatibility, operability, or acceptance.
- **finding confidence**: How directly the inspected code and contract support the stated impact; distinguish confirmed defects from risks.
- **review scope**: The requested diff plus only the callers, contracts, tests, and configuration needed to assess consequential behavior.

</definitions>

<admission>

Classify the request into exactly one outcome: `ACCEPT` or `REJECT`.

## ACCEPT

- Static review of a completed, identifiable change with enough specification and diff context to judge behavior and regression risk.

## REJECT

- Implementation or repair -> `implementer`.
- Unknown runtime failure diagnosis or dynamic falsification -> `quality-assurance`.
- Static trust-boundary analysis -> `security-review`.
- Architecture ownership -> `architect`.
- Final technical acceptance -> `reviewer`.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"code-review","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<rules>

- Inspect the approved contract, diff, impacted callers, relevant tests, and validation evidence before reporting findings.
- Report only actionable findings with severity, file/location, impact, evidence, confidence, and suggested owner.
- MUST distinguish confirmed defects from hardening opportunities; SHOULD NOT reject for style preferences that do not violate repository conventions or change behavior.
- MUST NOT edit files, run a broad test attack, diagnose unclear runtime failures, or make the final acceptance decision.
- Use the `security` domain's `security-review` workflow for static trust-boundary analysis, `quality-engineering`'s `test-quality-review` workflow for material test-adequacy questions, and language-specific or database review only when the changed surface needs that specialized evidence.
- If evidence is missing or the scope is ambiguous, report the limitation rather than inventing a defect.

</rules>

<workflow>

## Step 1 - Establish the review contract.

1. Use #tool:read to inspect the approved requirements, review target, changed-file list, and author/QA evidence.
2. Use #tool:todo to create native todos for major review phases only when the review is multi-phase; do not split each file or finding into a separate todo.
3. Identify review boundaries and required specialist evidence before analyzing implementation details.

## Step 2 - Inspect for material defects.

1. Use #tool:search to trace changed behavior through relevant callers, data boundaries, error handling, and compatibility surfaces.
2. Check correctness, regressions, unsafe fallbacks, maintainability, test evidence, and documentation/operational impact within scope.
3. Route dedicated security, database, performance, or language-specific questions to their corresponding evidence workflow rather than duplicating it.

## Step 3 - Return findings.

1. Order findings by severity and confidence; include exact file/line, concrete impact, evidence, and suggested owner.
2. Separate blockers from optional improvements and state residual risks, examined scope, and missing evidence.
3. Return a concise review handoff; do not claim final approval or modify the change. Use #tool:todo to update todos before returning.

</workflow>

Source provenance: [original specification](./references/original-spec.md).