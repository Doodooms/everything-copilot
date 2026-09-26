---
name: failure-analysis
description: "WHAT: Reproduce an observed failure, isolate its cause, and return an evidence-backed next action. USE FOR: failing builds or tests, unknown runtime defects, swallowed errors, dangerous fallbacks, intermittent failures, or measured performance regressions. DO NOT USE FOR: implementing a fix, speculative optimization, general review, or feature work."
user-invocable: false
metadata:
  creation-date: 2026-09-24
  creator: Doodooms
---

<definitions>

- **failure signal**: A focused observation that distinguishes the reported failure from success at the relevant execution boundary.
- **minimal reproduction**: The smallest reliable inputs, environment, and steps that preserve the reported failure mechanism.
- **failure chain**: The evidence-backed path from trigger through symptom and handling to the likely cause.
- **discriminating probe**: A safe check whose possible outcomes distinguish between explicit causal hypotheses.

</definitions>

<admission>

## ACCEPT

- An observed build, test, runtime, reliability, or performance failure whose cause must be isolated.

## REJECT

- Production or operational repair -> `implementer` or `devops`.
- Completed-change adversarial verification without a reported failure -> `quality-assurance` using `adversarial-testing`.
- Static code review or final acceptance -> `reviewer`.
- Architecture or product-intent decisions -> `architect` or `orchestrator`.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"failure-analysis","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<rules>

- MUST establish the observed symptom and a runnable failure signal before claiming a root cause. If the environment or inputs prevent reproduction, report `partial` or `blocked` and state what evidence is missing.
- SHOULD spend more effort sharpening a fast, deterministic signal than reading unrelated code or adding broad logs.
- MUST minimize inputs and execution steps only while the reported failure remains observable; retain the original reproduction for later comparison.
- For intermittent failures, MUST report reproduction frequency and conditions. MAY repeat or stress the narrow trigger when it adds evidence; MUST NOT run unbounded loops.
- MUST state testable hypotheses and vary one decision-relevant condition at a time. Separate demonstrated cause from plausible alternatives.
- MUST redact secrets and personal data from commands, logs, traces, screenshots, and artifacts before returning evidence.
- MUST NOT edit production code, runtime configuration, or infrastructure. A needed code change routes to Implementer or DevOps; test-surface ownership remains with QA.
- MUST NOT add unapproved production instrumentation or delete artifacts not created by this investigation. Use existing observability or an approved test-surface probe; remove only explicitly created temporary probes.
- For performance regressions, capture a comparable baseline before proposing optimization; do not infer a performance cause from subjective slowness alone.
- MUST preserve the user's working state; do not stage, commit, reset, abort, switch branches, or clean up repository data.

</rules>

<workflow>

## Step 1 - Establish the failure signal.

1. Use #tool:read to inspect the reported symptom, exact failing command or input, environment, recent relevant changes, logs, and reproduction evidence before theorizing.
2. Use #tool:execute to run the narrowest existing test, command, or harness that reaches the reported behavior; confirm its failure is the one described.
3. If no useful signal exists, use #tool:edit only for a minimal, authorized test-surface probe. Read the [failure-analysis guide](./references/guide.md) when help choosing a loop or reducing a reproduction is needed.

## Step 2 - Isolate the cause.

1. Reduce the reproduction to the smallest failure-preserving input, retaining the original case for comparison.
2. Use #tool:search to trace the failure path through callers, state, configuration, error handling, and fallback behavior; identify where the observed result diverges from the expected contract.
3. Rank plausible causes by evidence and define a probe for each. Change one relevant condition at a time; use targeted debugger or existing logs before adding any instrumentation.
4. For timing-sensitive or intermittent failures, capture repeated outcomes and the conditions that affect them. For performance, compare like-for-like measurements before inferring a regression.

## Step 3 - Return the diagnostic handoff.

1. Return `status: success | partial | blocked`, the reported and observed behavior, reproduction command/environment, minimal inputs, failure chain, root-cause evidence, alternative hypotheses, affected requirements when known, likely owner, and exact next action.
2. State whether a reliable signal was established, which checks were not possible, and any remaining uncertainty. Do not implement or claim that a repair is validated.

</workflow>

Source provenance: [original specification](./references/original-spec.md).
