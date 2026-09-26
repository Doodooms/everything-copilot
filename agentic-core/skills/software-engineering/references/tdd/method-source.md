---
name: tdd
description: "WHAT: Apply a test-first RED-GREEN-REFACTOR workflow with evidence gates. USE FOR: implementing features, fixing bugs, refactoring code, or adding tests when the acceptance criterion can be tested. DO NOT USE FOR: architecture-only planning, documentation-only edits, deployment operations, or tasks with no executable behavior."
user-invocable: false
compatibility: vscode 1.119.0+, github-copilot 1.119.0+
metadata:
  creation-date: 2026-09-22
  creator: Doodooms
license: MIT
---

<definitions>

- **behavior under change**: The externally observable result, contract, or failure condition that the requested work is intended to add, preserve, or correct.
- **acceptance criterion**: A concrete observable condition that demonstrates the requested behavior is correct, including relevant success, boundary, and failure cases.
- **test target**: The narrowest existing or newly created command, test case, or reproducer that can evaluate the acceptance criterion against the repository.
- **regression**: A previously working behavior that no longer satisfies its established contract after a change.
- **characterization test**: A test that records the current observable behavior of an existing system before a refactor, so unintended changes can be distinguished from the requested change.
- **RED**: The test target collects or compiles successfully, executes, and fails because the intended behavior is missing or broken. A setup error, missing dependency, or unexecuted test is not RED.
- **GREEN**: The same test target executes and passes after the minimum production change, without weakening or rewriting the test.
- **refactor**: A behavior-preserving restructuring performed only after GREEN, with the focused test rerun after each change and no change to the acceptance criterion.
- **coverage evidence**: A report from the repository's coverage command that identifies exercised and unexercised behavior; a percentage without a runnable command or report is not evidence.
- **quality gate**: The applicable final test, lint, type-check, security, and coverage checks required by the repository or change surface.
- **checkpoint**: An optional Git commit recording a validated RED, GREEN, or refactor stage; it is evidence of state, not a substitute for running the test target.

</definitions>

<admission>

Classify the request into exactly one outcome: `ACCEPT` or `REJECT`. Decide from the behavior under change, the requested deliverable, and the evidence needed to establish correctness.

## ACCEPT

- The work changes or verifies executable behavior in the target repository.
- The behavior under change and its acceptance criterion are identifiable from the request or the existing repository contract.
- The work can proceed through a failing test or reproducer, a minimal implementation, and a passing verification target.
- A refactor has an existing behavior to preserve, or a characterization test can establish that behavior before restructuring.

## REJECT

- The work is limited to architecture, planning, comparison, or review without an implementation or executable verification change -> `architecture-design` or the relevant review route.
- The work is limited to documentation or other non-executable artifacts -> the relevant documentation route.
- The work is deployment, CI, packaging, infrastructure, or operations without a code or test behavior change -> the relevant specialist route.
- No behavior under change or acceptance criterion can be established -> request clarification or route to the relevant non-TDD specialist.

The presence of testing vocabulary is supporting context, not the admission decision. The decision rests on whether this workflow is the appropriate way to change or verify repository behavior.

</admission>

<routing>

Apply these checks in order:

1. Identify the behavior under change and the repository boundary where it is observed.
2. Identify the requested deliverable and the acceptance criterion that will establish correctness.
3. Confirm that a test target or executable command can expose the acceptance criterion and distinguish intended behavior from setup failure.
4. Choose `ACCEPT` when the workflow owns that behavior change; otherwise choose `REJECT` and route to the closest specialist.

For `REJECT`, do **not** load the workflow. Return exactly:

```json
{"status":"rejected","skill":"tdd","reason":"<concise mismatch reason>","routing":"<suggested route or null>"}
```

For `ACCEPT`, continue directly to Step 0. Do not require a routing-probe file or run unrelated checks before establishing the target repository's test boundary.

</routing>

<rules>

- Never change production code before a valid RED result.
- Rerun the same focused target for GREEN before refactoring.
- TDD owns the test-first lifecycle; `quality-engineering`'s `test-design` workflow owns test-oracle, test-level, and case-design choices.
- Do not weaken or rewrite a test to make it pass.
- Do not add tombstone tests whose only purpose is to assert that removed code, routes, fields, or features remain absent. Negative tests are appropriate when the failure or absence is itself a current API, security, or persistence contract.
- Report missing evidence instead of claiming a gate passed.

</rules>

<workflow>

## Step 0 - Establish the test target

1. Inspect the target repository's existing test commands, test layout, and language tooling before editing with #tool:read
   - Use [test templates](./assets/test-templates.md) only when the repository lacks a clear local pattern.
   - Use #tool:execute with [test project verification](./scripts/verify_tdd_project.py) when the repository's test tooling or layout is unclear.
2. State the acceptance criterion as observable behavior and identify the narrowest test target that can prove it.

## Step 1 - RED: write and run the failing test

1. Write the smallest test or reproducer for the acceptance criterion before changing production code.
   - Use `quality-engineering`'s `test-design` workflow for oracle and test-surface design; keep this step responsible for establishing a valid RED result.
   - Use [test templates](./assets/test-templates.md) only for framework syntax when the repository lacks an established pattern.
2. Run the exact test target with #tool:execute and verify a valid RED result.
   - The target must compile or collect successfully.
   - The new or changed test must actually execute.
   - The failure must be caused by the intended missing or broken behavior.
3. If the repository uses Git, create a checkpoint after RED is proven:
   ```text
   test: add reproducer for <feature or bug>
   ```

## Step 2 - GREEN: implement the minimum change

1. Implement only what is necessary to make the failing test pass.
   - Do not add untested features or refactor unrelated code.
   - If the test fails for an environmental or test-authoring reason, repair that cause and re-establish RED before production changes.
2. Rerun the same test target with #tool:execute and confirm the previous failure is GREEN.
3. If the repository uses Git, create a checkpoint after GREEN is proven:
   ```text
   fix: <feature or bug>
   ```

## Step 3 - Refactor and inspect coverage when useful

1. Refactor only after GREEN while preserving behavior and keeping the tests green.
   - Remove duplication, improve names, and apply local language idioms.
   - Rerun the focused test target after each refactoring change.
2. Run the repository's coverage command with #tool:execute when its quality policy requires it or when the report can reveal unexercised changed behavior.
   - Use [coverage configuration guidance](./assets/coverage-config.md) only when a useful local command is not already established.
   - Use coverage to locate untested behavior or branches; MUST NOT treat a percentage alone as proof or impose a universal threshold not required by the project.
3. Add a focused test when evidence identifies a meaningful untested behavior; do not add assertions solely to raise a metric.
4. If the repository uses Git, create an optional checkpoint after refactoring:
   ```text
   refactor: clean up after <feature or bug> implementation
   ```

## Step 4 - Final quality gate

1. Run the project's normal test, lint, type-check, and security commands with #tool:execute when they apply to the changed code.
2. Verify the test files follow the repository's convention; otherwise use the [test layout guidance](./assets/test-templates.md).
3. Stop and report evidence if RED was never proven, the focused test is not executed, a required coverage gate cannot be measured, or another required quality gate fails.

</workflow>

Source provenance: [original specification](./references/original-spec.md).
