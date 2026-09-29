# Plan r2: TODO and research-input lifecycle

- Task: `todo_lifecycle`
- Base: `662ea3471b9e0a7a0ef34082a1539a8175c668b9`
- Risk: L2 — repository-wide documentation contract for the boundary between research inputs and approved implementation work.
- Scope: inspect existing ledgers and TODO conventions; define the smallest lifecycle; apply it to the six named inputs; add concise canonical documentation and only useful validation.
- Non-goals: workflow engine, custom issue tracker, database, runtime state machine, automatic promotion, changes to active PR #6 or implementation code owned by other lanes.
- Supersedes: plan r1's delivery-task decomposition, after independent review found that the manifest task IDs lacked matching scopes in the plan. The requirements and scope are unchanged.

## Requirements and acceptance

1. `todos/` inputs never authorize implementation by their presence or metadata alone.
2. Review maturity and disposition are independent fields; an approved implementation slice remains represented in the existing task manifest and task-event ledger.
3. Research inputs can be pending, partially adopted, deferred, blocked, superseded, or rejected without pretending the entire source is implemented.
4. The documentation explains intake through evidence, including that `todos/` is not FIFO.
5. The six named inputs retain their business content and receive only accurate lifecycle metadata.
6. Any validator is deterministic, local, and reuses the repository's existing tools; omit it if it would create a competing registry or unnecessary framework.

## Task decomposition and gates

| Task | Owner | Scope and acceptance | Dependency / exit gate |
|---|---|---|---|
| `TASK-TODO-LIFECYCLE-01` | Orchestrator | Audit TODO/task records; define `docs/todo-lifecycle.md`; update `todos/README.md` and the six named frontmatters; add only a small local metadata validator and focused tests if no equivalent exists. Satisfies `AC-TODO-01` through `AC-TODO-05`. | Starts after this plan is approved. Exit when the lifecycle and source metadata are written, source business text is preserved, and focused local checks pass. |
| `TASK-TODO-LIFECYCLE-QA` | Independent Quality Assurance | Read-only falsification of the metadata schema, source preservation, validator behavior, and non-overlap with excluded lanes. Covers `AC-TODO-04` and `AC-TODO-05`. | Depends on `TASK-TODO-LIFECYCLE-01`; exit with a recorded pass or explicit findings and evidence. |
| `TASK-TODO-LIFECYCLE-REVIEW` | Independent Reviewer | Read-only review of scope, authority boundary, lifecycle semantics, provenance, README links, and task evidence. Covers `AC-TODO-01` through `AC-TODO-05`. | Depends on `TASK-TODO-LIFECYCLE-QA`; exit with approve or findings, after QA is recorded. |

## Delivery sequence

1. Audit current TODO directories, task manifests/events, README guidance, and existing metadata/validators.
2. Record the chosen model in `docs/todo-lifecycle.md`; update `todos/README.md` and the six input frontmatters.
3. Run targeted metadata/documentation validation and `git diff --check`; if a validator is added, run its focused tests.
4. Complete `TASK-TODO-LIFECYCLE-QA`, then `TASK-TODO-LIFECYCLE-REVIEW`; resolve findings and re-run affected checks.
5. Commit and push this branch, then open a PR to `develop` titled `docs: define research input lifecycle`.
6. Stop without merging.
