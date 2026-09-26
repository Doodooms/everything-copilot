---
id: tdd
description: 'Apply the tdd method: implementing features, fixing bugs, refactoring
  code, or adding tests when the acceptance criterion can be tested.'
invoke_for:
- implementing features, fixing bugs, refactoring code, or adding tests when the acceptance
  criterion can be tested
avoid_for:
- architecture-only planning, documentation-only edits, deployment operations, or
  tasks with no executable behavior
references: []
---

## Step 0 - Establish the test target

1. Inspect the target repository's existing test commands, test layout, and language tooling before editing with #tool:read
   - Use [test templates](../references/tdd/assets/test-templates.md) only when the repository lacks a clear local pattern.
   - Use #tool:execute with [test project verification](../references/tdd/scripts/verify_tdd_project.py) when the repository's test tooling or layout is unclear.
2. State the acceptance criterion as observable behavior and identify the narrowest test target that can prove it.

## Step 1 - RED: write and run the failing test

1. Write the smallest test or reproducer for the acceptance criterion before changing production code.
   - Use `quality-engineering`'s `test-design` workflow for oracle and test-surface design; keep this step responsible for establishing a valid RED result.
   - Use [test templates](../references/tdd/assets/test-templates.md) only for framework syntax when the repository lacks an established pattern.
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
   - Use [coverage configuration guidance](../references/tdd/assets/coverage-config.md) only when a useful local command is not already established.
   - Use coverage to locate untested behavior or branches; MUST NOT treat a percentage alone as proof or impose a universal threshold not required by the project.
3. Add a focused test when evidence identifies a meaningful untested behavior; do not add assertions solely to raise a metric.
4. If the repository uses Git, create an optional checkpoint after refactoring:
   ```text
   refactor: clean up after <feature or bug> implementation
   ```

## Step 4 - Final quality gate

1. Run the project's normal test, lint, type-check, and security commands with #tool:execute when they apply to the changed code.
2. Verify the test files follow the repository's convention; otherwise use the [test layout guidance](../references/tdd/assets/test-templates.md).
3. Stop and report evidence if RED was never proven, the focused test is not executed, a required coverage gate cannot be measured, or another required quality gate fails.
