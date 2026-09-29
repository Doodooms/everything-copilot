# Plan r1: TODO and research-input lifecycle

- Task: `todo_lifecycle`
- Base: `662ea3471b9e0a7a0ef34082a1539a8175c668b9`
- Risk: L2 — repository-wide documentation contract for the boundary between research inputs and approved implementation work.
- Scope: inspect existing ledgers and TODO conventions; define the smallest lifecycle; apply it to the six named inputs; add concise canonical documentation and only useful validation.
- Non-goals: workflow engine, custom issue tracker, database, runtime state machine, automatic promotion, changes to active PR #6 or implementation code owned by other lanes.

## Requirements and acceptance

1. `todos/` inputs never authorize implementation by their presence or metadata alone.
2. Review maturity and disposition are independent fields; an approved implementation slice remains represented in the existing task manifest and task-event ledger.
3. Research inputs can be pending, partially adopted, deferred, blocked, superseded, or rejected without pretending the entire source is implemented.
4. The documentation explains intake through evidence, including that `todos/` is not FIFO.
5. The six named inputs retain their business content and receive only accurate lifecycle metadata.
6. Any validator is deterministic, local, and reuses the repository's existing tools; omit it if it would create a competing registry or unnecessary framework.

## Delivery and gates

1. Audit current TODO directories, task manifests/events, README guidance, and existing metadata/validators.
2. Record the chosen model in `docs/todo-lifecycle.md`; update `todos/README.md` and the six input frontmatters.
3. Run targeted metadata/documentation validation and `git diff --check`; if a validator is added, run its focused tests.
4. Obtain independent read-only QA/review of the resulting diff, fix any findings, commit and push this branch, and open a PR to `develop`.
5. Stop without merging.
