---
id: prototype
description: 'Apply the prototype method: checking a state model, interaction, or
  distinct UI direction before committing to production behavior.'
invoke_for:
- checking a state model, interaction, or distinct UI direction before committing
  to production behavior
avoid_for:
- shipping production code, implementing an approved feature, or replacing required
  tests and review
references: []
---

## Step 1 - Bound the question and artifact.

1. Read the task, relevant domain language, nearby implementation, and existing run conventions; use #tool:search to identify the smallest safe location and relevant interface.
2. Read [prototype shapes](../references/prototype/references/prototype-shapes.md) to choose a state-model demo or UI comparison; if the question is still ambiguous, return the exact missing decision rather than building both.
3. Record the question, expected observation, approved file boundary, non-goals, and disposal/preservation expectation.

## Step 2 - Build the smallest useful prototype.

1. Use #tool:edit to create a clearly named, disposable artifact in the approved scratch scope.
2. Keep state transitions or mock data isolated from real side effects; use the project's existing runtime only when needed to make the question observable.
3. Use #tool:execute for the narrowest start or interaction check; avoid production-quality abstractions and avoid changing unrelated project configuration.

## Step 3 - Present the result and hand off.

1. Return the prototype question, exact location and run instructions, options shown, validation performed, observed result or user decision still needed, assumptions, and changed files.
2. State that the artifact is not production-ready. Route any selected behavior to the approved architecture/implementation workflow; do not migrate the code yourself under this skill.
