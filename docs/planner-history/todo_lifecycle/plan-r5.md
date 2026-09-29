# Plan r5: keep adoption disposition separate from output provenance

- Task: `todo_lifecycle`
- Base: `662ea3471b9e0a7a0ef34082a1539a8175c668b9`
- Risk: L2 — repository-wide documentation contract for the boundary between research inputs and approved implementation work.
- Scope: resolve Reviewer-03's metadata example/provenance finding without inventing derived-work links or overriding the user-supplied disposition for the two Plugin Factory inputs; rerun current-revision QA and review.
- Requirements and acceptance criteria: unchanged from specification revision 1. `disposition` records the known handling decision; `derived_work` lists only outputs with a directly evidenced link.
- Non-goals: workflow engine, custom issue tracker, database, runtime state machine, automatic promotion, changes to active PR #6 or other implementation lanes, and merging PR #8.
- Supersedes: plan r4's follow-up sequence after Reviewer-03 found the example and `partially_adopted` provenance wording ambiguous.

## Task decomposition and gates

| Task | Owner | Scope and acceptance | Dependency / exit gate |
|---|---|---|---|
| `TASK-TODO-LIFECYCLE-CLARIFY-03` | Orchestrator | Define `partially_adopted` as the user/review-level disposition that some source proposals informed work while others did not; state that `derived_work` contains only directly traceable outputs and an empty list means no direct output link is established. Use a different disposition in the empty-list metadata example. | Starts from `FINDING-PARTIAL-ADOPTION-PROVENANCE`; exit when the user-supplied `partially_adopted` status is preserved without fabricated paths and the example is unambiguous. |
| `TASK-TODO-LIFECYCLE-QA-05` | Independent Quality Assurance | Reassess all five acceptance criteria and the six input metadata records on the corrected snapshot; rerun focused validation, tests, Ruff, source preservation, and diff checks. | Depends on `TASK-TODO-LIFECYCLE-CLARIFY-03`; exit with current-revision PASS or findings. |
| `TASK-TODO-LIFECYCLE-REVIEW-04` | Independent Reviewer | Review the final diff, provenance semantics, user-supplied dispositions, task evidence, and excluded-lane boundaries. | Depends on `TASK-TODO-LIFECYCLE-QA-05`; exit with current-revision approval or findings. |

## Delivery sequence

1. Clarify the distinction between a source disposition and links to proven outputs; do not infer provenance from thematic similarity.
2. Run the metadata validator and whitespace check.
3. Complete independent QA; resolve findings and rerun affected checks.
4. Complete independent Reviewer after QA passes.
5. Reconcile the manifest, append-only ledgers, current-revision evidence, and SDD convergence.
6. Commit the final follow-up normally, push it as a fast-forward to `docs/todo-lifecycle`, update PR #8's summary, and stop without merging.
