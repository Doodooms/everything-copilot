---
name: resolving-merge-conflicts
description: "WHAT: Reconcile authorized file-level conflicts during an already active Git merge or rebase. USE FOR: bounded source, test, or configuration conflicts where both sides' intent must be preserved and validated. DO NOT USE FOR: starting, aborting, continuing, or completing Git lifecycle operations, unrelated edits, or resolving a conflict whose intended behavior is unknown."
user-invocable: false
metadata:
  creation-date: 2026-09-24
  creator: Doodooms
---

<definitions>

- **conflict state**: An active merge or rebase reported by Git with one or more unmerged paths.
- **conflict intent**: The approved behavior and independent purpose represented by each conflicting change.
- **resolved file**: A conflict file whose content has been deliberately reconciled and whose conflict markers are removed, without assuming the merge/rebase is complete.

</definitions>

<admission>

## ACCEPT

- Resolve specified file-level conflicts in an already active merge or rebase, within an approved task and file-ownership boundary.

## REJECT

- No active merge/rebase or unresolved file conflict -> `orchestrator`.
- Unknown or unapproved product behavior needed to choose between changes -> `orchestrator` or `architect`.
- Conflict in CI, packaging, deployment, or runtime configuration outside the assigned implementation scope -> `devops`.
- Validation or final acceptance -> `quality-assurance` or `reviewer`.
- Starting, aborting, continuing, committing, or otherwise owning the Git lifecycle -> `orchestrator`.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"resolving-merge-conflicts","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<rules>

- MUST verify an active merge/rebase and list its unmerged paths before editing; preserve every unrelated user change.
- MUST inspect the common context, both conflicting versions, relevant commits, approved requirements, and nearby tests before choosing content.
- SHOULD preserve both intentions when compatible. When they conflict semantically, do not guess: return a blocker to the Orchestrator or Architect for the missing decision.
- MUST resolve only files inside the explicit handoff and ownership boundary; do not use whole-file `ours`/`theirs` replacement without review of all changed intent.
- MUST NOT start or abort a merge/rebase, reset files, stage, commit, continue, switch branches, alter worktrees, or clean repository state.
- MUST run the narrowest applicable tests or validation after resolving content; a conflict-free status alone is not proof of correctness.
- MUST leave Git lifecycle completion to the Orchestrator and report any remaining unmerged paths explicitly.

</rules>

<workflow>

## Step 1 - Confirm the conflict boundary.

1. Use #tool:execute to inspect `git status --short` and confirm the active merge/rebase state and exact unmerged paths.
2. Use #tool:read and #tool:search to read the scoped handoff, requirements, relevant source files, tests, and repository instructions; preserve all unrelated modifications.

## Step 2 - Reconcile both intents.

1. Use #tool:execute and #tool:read to inspect the conflict's base and both sides, plus the relevant commit or task context; distinguish code overlap from incompatible behavior.
2. Use #tool:edit to resolve each authorized file with the smallest content change that preserves compatible intent and satisfies the approved contract.
3. If the sources imply incompatible behavior or missing requirements, stop on that conflict and return the exact decision needed; do not invent a compromise.

## Step 3 - Validate and hand off.

1. Review the resolved diff and confirm that no conflict markers or intended changes were lost.
2. Run the narrowest relevant tests or validators; do not stage, commit, continue, or abort the Git operation.
3. Return the resolved and unresolved paths, source intents preserved, validation results, residual risk, `changed_files`, `commit_shas: []`, and the Orchestrator as the lifecycle owner.

</workflow>

Source provenance: [original specification](./references/original-spec.md).
