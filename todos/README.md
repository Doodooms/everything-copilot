# Todo and idea index

Use this index to find raw ideas, active work, completed reports, and deferred follow-ups. The canonical task ledger in `docs/` records active work. Unfinished or unassigned records belong in `backlog/`, never `done/`.

## Active work

`task_3` no longer has an active implementation owner. Its partial checkpoint
and unassigned follow-up gates are recorded below.

## Completed work

| Work | Specification and report | State |
|---|---|---|
| Agentic Core enhancements (`task_4`) | [SPEC-CORE-ENHANCEMENTS@4](./done/2026-09-27/agentic-core-enhancements-spec.md), [completion report](./done/2026-09-27/agentic-core-enhancements-report.md), [plan r5](../docs/planner-history/task_4/plan-r5.md) | Implementation and focused validation complete; task state remains `partial` because custom QA and Copilot cross-harness smoke are blocked. See the follow-up backlog. |
| Agentic Core normalization (`task_5`) | [source brief](./done/2026-09-27/source-inputs/agentic-core-normalization.md), [clarification source](./done/2026-09-27/source-inputs/subskills-fix-source.md), [completion report](./done/2026-09-27/agentic-core-normalization-report.md), [plan r10](../docs/planner-history/task_5/plan-r10.md), [task ledger](../docs/tasks-history/task_5.jsonl) | Implementation and automated validation are recorded; overall state remains `partial` because independent QA and Reviewer were not executed. See the [review-gate backlog](./backlog/2026-09-27/agentic-core-normalization-review-gates.md). |

## Backlog

- [`backlog/2026-09-27/cost-eval-opt-followups.md`](./backlog/2026-09-27/cost-eval-opt-followups.md) — released partial `task_3` checkpoint; remaining budget, baseline, smoke, QA, and Reviewer gates.
- [`backlog/2026-09-27/agentic-core-enhancements-followups.md`](./backlog/2026-09-27/agentic-core-enhancements-followups.md) — blocked host checks and evidence-triggered future work from task_4.
- [`backlog/2026-09-27/agentic-core-normalization-review-gates.md`](./backlog/2026-09-27/agentic-core-normalization-review-gates.md) — independent task_5 QA and Reviewer handoffs unavailable in this host.
- [`backlog/2026-09-26/`](./backlog/2026-09-26/) — earlier unassigned work records, preserved without claiming completion.

## Idea intake

- [`harness/`](./harness/) — harness routing, cost, session communication, and safety inputs. [`cost-eval-opt.md`](./harness/cost-eval-opt.md) is the source brief for the released partial task_3 checkpoint; [`codex-session-communication.md`](./harness/codex-session-communication.md) is a research input for `task_5` and does not authorize contacting another session.
- [`plugins/`](./plugins/) — plugin proposals.
- [`skills/`](./skills/) — skill ideas and optimization.
- [`mcp/`](./mcp/) — MCP authoring and server ideas.
- [`agents/`](./agents/) — agent and architecture inputs.
- [`gh-repos/`](./gh-repos/) — external projects for feasibility review.

Reviewed task_4 inputs are preserved beside their reports:

- [`create-mcp-rust.md`](./done/2026-09-27/create-mcp-rust.md) → Rust MCP authoring workflow in the completion report.
- [`agent_architect_ideas.md`](./done/2026-09-27/agent_architect_ideas.md) → [architecture review disposition](./done/2026-09-27/architecture-ideas-disposition.md). The source is a review brief, not an idea list.
- [`gpt-confirmed.md`](./done/2026-09-27/gpt-confirmed.md) → [integration feasibility report](./done/2026-09-27/integration-feasibility.md).

## Other completed reports

- [`done/2026-09-26/`](./done/2026-09-26/) — earlier completion reports and source inputs.

## Status rule

Moving a source file does not make its requested work complete. A `done/` report states what was implemented, assessed, or blocked. Remaining work is linked from the backlog with its owner or resume condition. Keep `todos/in_progress/` empty when there is no currently assigned implementation slice.
