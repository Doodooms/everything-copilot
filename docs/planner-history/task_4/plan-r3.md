# Closure plan — task_4, revision 3

- Specification: `SPEC-CORE-ENHANCEMENTS@3` in `todos/done/2026-09-27/agentic-core-enhancements-spec.md` at closure.
- Architecture: `docs/harness-history/task_4/architecture-r2.md` (unchanged; this continuation closes validation and tracking).
- Base revision: `5c6dcd401e9a0d115e79c19f02de96ffed694686`.
- Assigned risk: `L2`.
- Owner: root Orchestrator.
- User change: finish the current enhancement phase and leave no files in `todos/in_progress`.

## Closure tasks

| Task | Scope | Exit evidence |
|---|---|---|
| `TASK-STATUS-OBS-02` | Query supported Copilot and Codex CLI status surfaces without exposing secrets or resuming the other session. | Fresh host-reported observations; any denied cross-harness call is marked blocked before contact. |
| `TASK-PLUGIN-SYNC-02` | Reinstall the approved local `agentic-core` source in Copilot CLI alongside Codex. | Both CLIs report enabled `0.3.0`; both installed copies match the source; new Copilot session discovers nine agents and the packaged skills. |
| `TASK-QA-CLOSE-01` | Independently falsify the exchange validator and relevant package behavior without editing production files. | Reproducible focused findings and commands. |
| `TASK-REVIEW-CLOSE-01` | Independently review the delivered contracts, workflows, package sync, and residual limits. | Reviewer verdict against SPEC-CORE-ENHANCEMENTS@3. |
| `TASK-TRACK-CLOSE-01` | Move completed task records to `done`, reclassify unrelated unassigned/blocked records to `backlog`, refresh the index, and empty `todos/in_progress`. | No files remain under `todos/in_progress`; unfinished backlog is explicitly not called done; task_3 records and source remain untouched. |
| `TASK-VALIDATE-CLOSE-01` | Re-run only the focused schema, package, cache-parity, and tracking checks needed for closure. | Exact commands/results; no repository-wide or task_3 test run. |

## Completion interpretation

- The source implementation and plugin packaging are complete once QA/Reviewer pass and the two installed hosts match the source.
- A Copilot answer cannot be required while its provider reports exhausted quota. Record the live denial and do not retry, switch accounts, or imply that an independent Codex response came from the other active task_3 session.
- Host credentials are never fabricated or copied into plugin files. The existing GitHub App MCP server remains unavailable in hosts where its required App environment variables are absent; that host setup is outside this phase.
- Unrelated 2026-09-26 task briefs formerly stored under `in_progress` are preserved in `todos/backlog/2026-09-26` as unassigned work, not marked complete.

## Preservation and lifecycle

- Do not edit or move `task_3`, `harness_factory`, its tests, or its canonical ledgers.
- Do not stage, commit, reset, or clean the shared repository.
- Reinstall only the already-approved local `agentic-core` source; do not alter provider credentials or add a remote marketplace.
