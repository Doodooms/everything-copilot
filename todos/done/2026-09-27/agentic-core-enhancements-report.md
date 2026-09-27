# Completed work report — agentic-core enhancements

Date: 2026-09-27. Task: `task_4`, specification `SPEC-CORE-ENHANCEMENTS@4`, plan revision 5, risk `L2`.

Implementation status: complete. Overall task status remains `partial` because a successful Copilot cross-harness response could not be obtained while its monthly quota was exhausted. That blocked smoke is recorded in the [follow-up backlog](../../backlog/2026-09-27/agentic-core-enhancements-followups.md). No files remain under `todos/in_progress`.

## Delivered

- Added `multi-harness` workflows for safe context compaction and provider-aware work distribution. Exact host telemetry, local estimates, and unavailable values remain distinct; quota snapshots require source and observation time.
- Extended `context-management` with separate lifetimes for raw history, active context, and durable memory, plus retrieval states and provenance/staleness rules.
- Added versioned JSON Schema contracts and `validate_exchange.py` for handoffs, manifests, persisted wrappers, orchestration events, and task transitions. The validator checks schema shape, exact Git commit objects, declared changed paths, artifact digests, and repository-contained paths.
- Fixed merge commit verification to compare with the first parent, documented the resulting `changed_paths` policy, and made `commit_shas` mandatory when an event says a commit was created.
- Changed the Orchestrator persistence helper to validate the fully built event before writing the manifest. A malformed specialist return now leaves the prior manifest and event ledger untouched.
- Aligned the manifest JSON Schema with the optional SDD extension and the record shapes already in use. The active `task_3` manifest passes the updated outer schema without any change to its files; SDD stable-ID rules now accept segmented IDs used by the task ledger.
- Tightened SDD evidence validation after read-only review found gaps: blocked or stale implementation evidence no longer counts toward convergence or coverage; passing claims require current passing evidence that covers their criteria; completed tasks require evidence for every declared criterion; and QA coverage reports `uncovered` when a passing QA run omits a requirement's criteria. Added the schema's missing `existing_evidence` field.
- Required a fresh budget snapshot for the destination harness before either paired Copilot/Codex workflow contacts its CLI.
- Integrated the `rmcp` Rust workflow into the existing MCP authoring route, linked a focused existing-solution research workflow, and assessed the supplied integration candidates without importing external code.
- Corrected the architecture disposition: `agent_architect_ideas.md` is a review protocol, not a set of prioritized implementation proposals. The bounded conclusion is to keep the plugin and host-adapter architecture and apply the local contract fixes above.
- Reorganized tracking so active `task_3` remains in its canonical ledger, old unassigned records remain in backlog, and `todos/in_progress` is empty.

## Validation and review evidence

- `uvx ruff check` and format checks passed for `orchestrator.py`, `validate_exchange.py`, and the SDD state validator.
- Focused isolated checks passed for merge, ordinary commit, schema, and persistence behavior: merge changed paths resolve to the first-parent delta; ordinary commit paths remain correct; `commit_status: created` without `commit_shas` is rejected; and an invalid specialist return does not alter an existing manifest or create an event.
- Targeted SDD regressions passed for blocked evidence, missing implementation revisions, missing validation references, completed-task criterion coverage, partial QA coverage, and the `existing_evidence` schema field.
- All five exchange schemas pass Draft 2020-12 meta-validation. Both `task_3` and `task_4` manifests pass the updated exchange envelope; the canonical task_4 SDD manifest passes its ID, traceability, revision, and pending-gate checks. Changed skill packages pass their package validators; existing optional-reference/tool-marker warnings remain.
- A final ephemeral, read-only Codex CLI review found no actionable finding in the SDD safeguards. The reviewer could not run its checks under its read-only sandbox; the targeted local regressions above supplied execution evidence. This was not a response from the other active `task_3` session.
- The Copilot CLI prompt attempt returned its monthly quota limit before a model response. No retry or account change was made. A successful cross-harness answer therefore remains unverified.
- A custom `quality-assurance` agent could not be spawned in this host. Focused checks above are recorded as local evidence, not as an independent QA-agent verdict.
- No repository-wide suite or `task_3` tests were run. The separate task and its source/ledger were left untouched.

## Plugin update

The source version is `agentic-core` `0.3.3`, installed and enabled in Codex and Copilot. Copilot reported 11 installed skills; the source contains 11 skills with `SKILL.md` and 9 agent definitions. Both installed trees match the source, excluding generated Python bytecode. A new Copilot model session could not be used to verify skill discovery because its monthly quota was exhausted. Copilot also warned that direct local-path installs are deprecated; that future packaging migration is recorded in the [follow-up backlog](../../backlog/2026-09-27/agentic-core-enhancements-followups.md). The source plugin manifest is [`agentic-core/plugin.json`](../../../agentic-core/plugin.json).

The `result.md` path supplied earlier was absent from the workspace, so this report does not rely on it. The GitHub MCP server also needs GitHub App environment variables provided by the host; they were absent in this shell. No credential values were read, created, or changed.

## Remaining work

Only host-dependent or trigger-dependent items remain, listed in the [backlog follow-ups](../../backlog/2026-09-27/agentic-core-enhancements-followups.md). The implementation phase itself is complete; the overall task remains `partial` while those independent observations are blocked. No files remain under `todos/in_progress`.

The final closure plan is [plan r5](../../../docs/planner-history/task_4/plan-r5.md). The canonical task state and evidence are in [`docs/harness-history/task_4/manifest.json`](../../../docs/harness-history/task_4/manifest.json); append-only transitions are in [`docs/tasks-history/task_4.jsonl`](../../../docs/tasks-history/task_4.jsonl).
