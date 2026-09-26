---
name: prototype
description: "WHAT: Build a disposable, runnable artifact to answer one concrete product or design question. USE FOR: checking a state model, interaction, or distinct UI direction before committing to production behavior. DO NOT USE FOR: shipping production code, implementing an approved feature, or replacing required tests and review."
user-invocable: false
metadata:
  creation-date: 2026-09-24
  creator: Doodooms
---

<definitions>

- **prototype question**: One named uncertainty about product behavior, state transitions, interaction, or visual hierarchy that the artifact is intended to resolve.
- **disposable artifact**: A clearly marked scratch deliverable isolated from production code and data, with no presumption that its implementation will ship.
- **validated insight**: The user-visible observation or choice that answers the prototype question, separate from the prototype's implementation.

</definitions>

<admission>

## ACCEPT

- An approved design question whose answer benefits from a runnable or interactive sketch.
- A bounded state-model, interaction, or UI comparison with an explicit disposable-prototype deliverable.

## REJECT

- Production feature implementation or repair -> `implementer` using `tdd`.
- Structural architecture or domain decision -> `architect`.
- Unresolved product intent, scope, or data-safety decision -> `orchestrator`.
- A request that lacks a concrete question or safe artifact boundary -> `orchestrator`.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"prototype","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<rules>

- MUST state one concrete question before creating files; keep the prototype no larger than needed to answer it.
- MUST clearly label the artifact as a prototype and distinguish observed feedback from assumptions or production recommendations.
- MUST use fake or in-memory state by default. MUST NOT perform real user-data mutations, require secrets, or depend on production credentials.
- MUST keep disposable code out of production paths by default. Modifying an existing page, route, adapter, or shared component requires an approved scope and a development-only guard where applicable.
- MAY use a focused smoke check to establish that the artifact runs and demonstrates its question; a prototype does not replace tests, security checks, or review for production code.
- MUST NOT promote prototype code directly into production. Transfer only the validated behavior or design decision; production implementation follows its own approved scope, tests, and review.
- MUST NOT independently start a branch/worktree or perform cleanup. Follow the owning agent's approved lifecycle contract for staging or a focused commit; a prototype artifact MUST remain clearly labeled and MUST NOT be represented as production implementation.
- MUST preserve user state; do not delete or overwrite existing files to make a prototype easier to run.

</rules>

<workflow>

## Step 1 - Bound the question and artifact.

1. Read the task, relevant domain language, nearby implementation, and existing run conventions; use #tool:search to identify the smallest safe location and relevant interface.
2. Read [prototype shapes](./references/prototype-shapes.md) to choose a state-model demo or UI comparison; if the question is still ambiguous, return the exact missing decision rather than building both.
3. Record the question, expected observation, approved file boundary, non-goals, and disposal/preservation expectation.

## Step 2 - Build the smallest useful prototype.

1. Use #tool:edit to create a clearly named, disposable artifact in the approved scratch scope.
2. Keep state transitions or mock data isolated from real side effects; use the project's existing runtime only when needed to make the question observable.
3. Use #tool:execute for the narrowest start or interaction check; avoid production-quality abstractions and avoid changing unrelated project configuration.

## Step 3 - Present the result and hand off.

1. Return the prototype question, exact location and run instructions, options shown, validation performed, observed result or user decision still needed, assumptions, and changed files.
2. State that the artifact is not production-ready. Route any selected behavior to the approved architecture/implementation workflow; do not migrate the code yourself under this skill.

</workflow>

Source provenance: [original specification](./references/original-spec.md).
