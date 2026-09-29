# Plan r4: separate research maturity from disposition decisions

- Task: `todo_lifecycle`
- Base: `662ea3471b9e0a7a0ef34082a1539a8175c668b9`
- Risk: L2 — repository-wide documentation contract for the boundary between research inputs and approved implementation work.
- Scope: resolve the sole AC-TODO-02 ambiguity found by QA-03, then rerun independent QA and final review against the corrected branch snapshot.
- Requirements and acceptance criteria: unchanged from specification revision 1; `status` describes evidence-review maturity, while `disposition` records handling decisions.
- Non-goals: workflow engine, custom issue tracker, database, runtime state machine, automatic promotion, changes to active PR #6 or other implementation lanes, and merging PR #8.
- Supersedes: plan r3's follow-up sequence after QA-03 found a contradiction between `researched` and `pending`.

## Task decomposition and gates

| Task | Owner | Scope and acceptance | Dependency / exit gate |
|---|---|---|---|
| `TASK-TODO-LIFECYCLE-CLARIFY-02` | Orchestrator | Define `researched` only as reviewing relevant evidence against the questions identified at triage; state explicitly that `status: researched` with `disposition: pending` is valid when no handling decision has been made. Preserve the no-implementation-authority rule. | Starts from QA-03's `FINDING-RESEARCHED-PENDING`. Exit when documentation is internally consistent and targeted local checks pass. |
| `TASK-TODO-LIFECYCLE-QA-04` | Independent Quality Assurance | Reassess all five acceptance criteria on the corrected snapshot, rerun focused metadata tests and validation, check source-body preservation, and confirm no excluded lane changed. | Depends on `TASK-TODO-LIFECYCLE-CLARIFY-02`; exit with current-revision PASS or findings. |
| `TASK-TODO-LIFECYCLE-REVIEW-03` | Independent Reviewer | Review the final branch diff, all five acceptance criteria, task evidence, and excluded-lane boundaries. | Depends on `TASK-TODO-LIFECYCLE-QA-04`; exit with current-revision approval or findings. |

## Delivery sequence

1. Clarify that evidence-review maturity does not imply a disposition decision.
2. Run targeted metadata, focused-test, Ruff, source-preservation, and diff checks.
3. Complete independent QA; resolve any findings and rerun affected checks.
4. Complete independent Reviewer after QA records a current-revision pass.
5. Reconcile the manifest, append-only ledgers, SDD evidence coverage, and convergence.
6. Commit the follow-up normally, push it as a fast-forward to `docs/todo-lifecycle`, update PR #8's summary, and stop without merging.
