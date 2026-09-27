# Implementation plan — task_5, revision 2

> **SUPERSEDED by plan r10 and architecture r6.** Historical record only; the current structure is 11 domain `SKILL.md` entrypoints with complete subskills under their owning `workflows/` directories. Do not implement peer skill packages from any earlier plan.

- Specification: `SPEC-AGENTIC-CORE-NORMALIZATION@1`.
- Base revision: `5c6dcd401e9a0d115e79c19f02de96ffed694686`.
- Assigned risk: `L2`.
- Owner: root Orchestrator.
- Status: in progress.
- Supersedes: plan r1 for execution tracking; the approved scope and acceptance criteria are unchanged.

## Task DAG

| Task | Owner | Depends on | State | Output and exit check |
|---|---|---|---|---|
| `TASK-5-01` Codex projection and installation | Orchestrator using the `operations` workflow and existing Codex renderer | — | Complete | Idempotent installer projects all canonical agents into `CODEX_HOME/agents`; Codex CLI loads the `quality-assurance` role in a fresh process. |
| `TASK-5-02` Workflow skill topology | Architect for the bounded topology decision; Implementer for approved code/package changes | `TASK-5-01` | Planned | Every routed workflow follows the complete skill contract and is recursively discoverable/materialized by the declared harness targets. |
| `TASK-5-03` MCP authoring skill composition | Implementer | `TASK-5-02` | Planned | Generic and Rust `rmcp` skills have distinct scopes, one owner for shared rules, and pass package validation. |
| `TASK-5-04` Scratch cleanup and same-harness session coordination | Implementer | `TASK-5-02` | Planned | Remove only verified generated scratch files; document read-only status, explicit contact authorization, queued versus consumed/replied messages, and bounded handoff. |
| `TASK-5-05` Todo crosswalk and convergence | Orchestrator | `TASK-5-02`, `TASK-5-03`, `TASK-5-04` | Planned | Reconcile active/done/backlog files with reports and ledgers; preserve task_3 ownership; leave task_5 partial if any required gate remains blocked. |

## Current evidence and gates

- `TASK-5-01` checks: `uv run --python .venv/bin/python scripts/install_codex_agents.py`; the same command with `--check`; Ruff check and format; Semgrep 1.177.0 scan of the renderer and installer; Codex CLI 0.157.1 fresh-process role-load probe.
- Installation writes only missing or explicitly forced generated role files. It does not prune unrelated roles or overwrite differing files by default.
- The native plugin remains separately installed through the Codex plugin lifecycle. Source and cache report version 0.3.3, with matching `plugin.json` and `mcp.json`, 11 skills, and 9 packaged Copilot agents.
- `github-mcp-server` is configured but its launcher cannot initialize unless `GITHUB_APP_ID`, `GITHUB_APP_INSTALLATION_ID`, and `GITHUB_APP_PRIVATE_KEY_PATH` reach the Codex process. They are currently absent; do not inspect credential values or modify secret configuration. Context7 and Semgrep are available in this session.
- Keep implementation validation, independent QA, and review open for the remaining tasks. Do not advance the task to complete while a required gate or blocker remains.

## Constraints and lifecycle

- Do not modify `docs/harness-history/task_3/`, `docs/tasks-history/task_3.jsonl`, or `harness_factory/`.
- Do not send or queue a message to another Codex session.
- Do not inspect credentials, stage, commit, reset, or clean the shared worktree.
- Keep workflows as complete skill packages; topology is only an organization and progressive-disclosure layer.
- Use the existing Codex projection renderer; do not add a second format converter.
- Next action: route `TASK-5-02` to the plugin Architect for a read-only topology brief, then dispatch the bounded implementation to the custom Implementer role.
