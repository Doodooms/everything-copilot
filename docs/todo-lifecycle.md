# TODO and research-input lifecycle

Dropping a design or research document into `todos/` preserves an input for future consideration. It does not authorize implementation.

```text
research/design input != backlog follow-up != approved task slice != active task != implemented behavior
```

## The records mean different things

- **Research or design input** is source material for review. It may contain ideas, vendor claims, options, or a proposed architecture. Its presence, wording, and metadata never grant implementation authority.
- **Backlog follow-up** records unassigned or deferred work in `todos/backlog/`. The directory is a place to find it, not an execution queue or approval signal.
- **Approved task slice** is a bounded scope recorded by the Orchestrator in `docs/harness-history/<task-id>/manifest.json`, with its approved plan in `docs/planner-history/` when planning is needed. The manifest and task ledger, not the source note, are the durable task record.
- **Active task** is shown by the canonical task state and its current task event (`running`), together with the manifest's current ownership and scope.
- **Implemented behavior** is present in repository code or configuration and is backed by the validation/evidence recorded for that task. A source note is not relabeled as wholly implemented when only some proposals were used.

The intended path is:

```text
input → review/research → disposition → optional approved slice → implementation → evidence
```

An input can remain deferred, blocked, superseded, or rejected at any point. One input may inform multiple slices, and one slice may use multiple inputs. Keep source provenance in `derived_work` only when a task, artifact, or PR is directly traceable; leave it empty when the relationship is merely thematic.

## Input metadata

Use YAML frontmatter on durable design/research inputs. Keep this four-field schema:

```yaml
kind: design_input
status: researched
disposition: partially_adopted
derived_work: []
```

- `kind`: `design_input`, `research_input`, or `work_brief` for a source brief that already fed a task.
- `status`: intake/review maturity — `raw`, `triaged`, or `researched`. It does not say whether the proposal was accepted.
- `disposition`: current handling — `pending`, `research_required`, `adopted`, `partially_adopted`, `deferred`, `blocked`, `superseded`, or `rejected`. `adopted` describes a decision about source ideas; it is not permission to implement them.
- `derived_work`: a list of repository paths or PR references for directly traceable outputs; use `[]` when none is known.

Do not add an `owner`, priority score, implementation state, runtime state, or review date. Git history records edits, while task manifests and events record actual ownership and evidence; a manually maintained date or owner would quickly go stale. Do not mark an entire input `implemented` when it contains mixed ideas.

An approved slice must instead appear in the existing task system. Record its bounded specification, scope, and gates in the task manifest/approved plan; record task transitions in `docs/tasks-history/`. An input's disposition alone never creates that slice.

## Ordering

`todos/` is not FIFO. Choose work by dependencies, fit with current architecture, available evidence, cost, risk, and the smallest coherent slice. File age or directory order is not a reason to implement an item first.

## Local validation

Validate only the changed input documents, passing their paths explicitly:

```sh
uv run --script scripts/validate_todo_metadata.py \
  todos/plugins/plugin-factory-refont.md \
  todos/plugins/plugin-factory-helper.md \
  todos/plugins/self-improvement.md \
  todos/harness/security-hardening-input.md \
  todos/gh-repos/core-upgrade.md \
  todos/harness/cost-eval-opt.md
```

This check validates metadata shape and vocabulary. It does not decide whether an idea is sound, approved, implemented, or ready for promotion.
