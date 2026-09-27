# Closure plan — task_4, revision 5

- Specification: `SPEC-CORE-ENHANCEMENTS@4`.
- Architecture: `docs/harness-history/task_4/architecture-r3.md`.
- Base revision: `5c6dcd401e9a0d115e79c19f02de96ffed694686`.
- Assigned risk: `L2`.
- Owner: root Orchestrator.
- Status: implementation, focused validation, final read-only review, and plugin sync complete; host-dependent QA and Copilot smoke remain blocked.
- Revision 5 supersedes revision 4 after review found SDD evidence freshness and coverage gaps. The corrections below prevent incomplete evidence from producing a passing state.

## Revision 5 work and evidence

| Task | Result | Evidence |
|---|---|---|
| `TASK-MANIFEST-SDD-CONTRACT-02` | Completed | The versioned manifest schema accepts the typed SDD extension and existing task_3 manifest shapes; segmented stable IDs are accepted. |
| `TASK-PRESERVE-TASK3-01` | Completed | The active task_3 manifest passes the updated exchange envelope; its source and canonical task ledger were not edited by task_4. |
| `TASK-SDD-EVIDENCE-CLOSE-01` | Completed | Passing implementation claims now require current passing evidence that covers their declared acceptance criteria. Blocked/stale evidence no longer contributes to convergence or coverage; completed tasks must have evidence for every declared criterion. |
| `TASK-VALIDATE-CLOSE-02` | Completed | Targeted stale/missing-revision, missing-reference, task-coverage, QA-coverage, schema, SDD-manifest, and exchange-envelope checks passed. Ruff check and format check passed. |
| `TASK-REVIEW-CLOSE-03` | Completed | Final ephemeral, read-only Codex review found no actionable finding in the SDD safeguards. The reviewer could not run its own checks under its read-only sandbox; local regressions supplied execution evidence. |
| `TASK-PLUGIN-SYNC-04` | Completed | Codex and Copilot report `agentic-core` `0.3.3`; both installed trees match source excluding generated Python bytecode. |
| `TASK-TRACK-CLOSE-02` | Completed | Final task index, completion report, and follow-up backlog agree; `todos/in_progress` is absent and contains no files. |

## Superseded records

The earlier `TASK-VALIDATE-CLOSE-01`, `TASK-REVIEW-CLOSE-02`, and `TASK-PLUGIN-SYNC-03` records describe work performed before the SDD fixes or the `0.3.3` refresh. Their SDD task states are stale; the append-only task history retains their original transitions as historical evidence.

## Remaining blockers

- The host did not expose the custom `quality-assurance` agent type. Local checks and Codex review are not represented as an independent QA-agent verdict.
- Copilot reported its monthly quota exhausted before returning a model response. No retry or account change was made.
- Copilot installed successfully from the local path but warned that direct local-path installs are deprecated; a supported marketplace refresh remains a packaging follow-up.
- GitHub MCP still needs host-provided GitHub App environment variables if that server is to be used.

## Constraints

- Preserve the separate active `task_3` / `harness_factory` workstream and its canonical ledger.
- Do not stage, commit, reset, or clean the shared worktree.
- Do not inspect or write provider credentials.
