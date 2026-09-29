# Plan r3: clarify TODO metadata meanings and revalidate

- Task: `todo_lifecycle`
- Base: `662ea3471b9e0a7a0ef34082a1539a8175c668b9`
- Risk: L2 — repository-wide documentation contract for the boundary between research inputs and approved implementation work.
- Scope: close the AC-TODO-02 definition gap found during supplemental QA of the published PR branch, then independently revalidate the resulting documentation and task evidence.
- Requirements and acceptance criteria: unchanged from specification revision 1; this follow-up clarifies existing metadata vocabulary and does not expand product scope.
- Non-goals: workflow engine, custom issue tracker, database, runtime state machine, automatic promotion, changes to active PR #6 or other implementation lanes, and merging PR #8.
- Supersedes: plan r2 for the follow-up delivery sequence only; prior completed task history remains intact.

## Task decomposition and gates

| Task | Owner | Scope and acceptance | Dependency / exit gate |
|---|---|---|---|
| `TASK-TODO-LIFECYCLE-CLARIFY-01` | Orchestrator | Clarify the observable meaning of every allowed `status` and `disposition` value in `docs/todo-lifecycle.md`; preserve the no-authorization boundary and existing source metadata. | Starts from the AC-TODO-02 gap reported by supplemental QA. Exit when all allowed values have distinct, concise definitions and local validation passes. |
| `TASK-TODO-LIFECYCLE-QA-03` | Independent Quality Assurance | Read-only assessment of all five acceptance criteria on the clarified branch; rerun focused metadata tests and validation, check source-body preservation, and assess the distinction between status and disposition. | Depends on `TASK-TODO-LIFECYCLE-CLARIFY-01`; exit with current-revision PASS or findings. |
| `TASK-TODO-LIFECYCLE-REVIEW-03` | Independent Reviewer | Read-only review of the final branch diff, all five acceptance criteria, evidence references, and excluded-lane boundaries. | Depends on `TASK-TODO-LIFECYCLE-QA-03`; exit with current-revision approval or findings. |

## Delivery sequence

1. Define each permitted status and disposition value without changing their existing metadata assignments.
2. Run targeted documentation, metadata, focused-test, Ruff, and diff checks.
3. Complete independent QA; resolve any findings and rerun only affected checks.
4. Complete independent Reviewer after QA has recorded a current-revision pass.
5. Reconcile manifest, task events, SDD coverage, and convergence against the final content.
6. Commit the follow-up normally, push it as a fast-forward to `docs/todo-lifecycle`, update the existing PR #8 summary if needed, and stop without merging.
