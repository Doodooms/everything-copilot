# Implementation plan — task_5, revision 3

> **SUPERSEDED by plan r10 and architecture r6.** Historical record only; the current structure is 11 domain `SKILL.md` entrypoints with complete subskills under their owning `workflows/` directories. Do not implement peer skill packages from any earlier plan.

- Specification: `SPEC-AGENTIC-CORE-NORMALIZATION@1`.
- Architecture: `docs/harness-history/task_5/architecture-skill-topology.md` (revision 1).
- Base revision: `5c6dcd401e9a0d115e79c19f02de96ffed694686`.
- Assigned risk: `L2`.
- Owner: root Orchestrator.
- Status: in progress.
- Supersedes: plan r2 task decomposition; specification scope and acceptance criteria are unchanged.

## Task DAG

| Task | Owner | Depends on | State | Output and exit check |
|---|---|---|---|---|
| `TASK-5-01` Codex agent projection and installation | Orchestrator using `operations` and the existing Codex renderer | — | Complete | Idempotent installer projects all nine core roles to `CODEX_HOME/agents`; fresh Codex child loaded `quality-assurance`. |
| `TASK-5-02` Skill-topology architecture | Architect | — | Complete | Decision record adopts peer skill packages at the plugin `skills/` root, preserving domain-router → method-skill disclosure. |
| `TASK-5-03` Routed workflow skill migration | Planner, then Implementer | `TASK-5-02` | Running | Convert the 57 methods into full peer `SKILL.md` packages; update domain routers, canonical skill linter, source tests, and package projections without duplicate editable trees. |
| `TASK-5-04` Verified plugin scratch cleanup | Orchestrator using `operations` | — | Complete | Removed 10 unconsumed `.workflow-routes.tmp` files and 3 generated `__pycache__` directories inside `agentic-core`; unrelated workspace caches were retained. |
| `TASK-5-05` MCP authoring skill composition | Planner, then Implementer | `TASK-5-03` | Planned | `create-mcp` and `create-mcp-rust` remain complete complementary skills, share common transport/security guidance once, and retain Rust-specific `rmcp` constraints. |
| `TASK-5-06` Same-harness session coordination | Planner, then Implementer | `TASK-5-03` | Planned | Document read-only session status, explicit contact authorization, queue versus consumption/reply, and bounded handoff/resume without messaging another session. |
| `TASK-5-07` Package refresh and dual-host verification | Operations | `TASK-5-03`, `TASK-5-04`, `TASK-5-05`, `TASK-5-06` | Planned | Bump the local plugin version, reinstall through both configured host lifecycles, compare source/cache, and verify all peer skill IDs plus custom-agent inventories in Codex and Copilot. |
| `TASK-5-08` Todo audit and convergence | Orchestrator | `TASK-5-07` | Planned | Reconcile every `done/`, `in_progress/`, and backlog item to actual reports/ledgers; preserve task_3 ownership and leave unresolved work partial or blocked. |

## Current gates and evidence

- `TASK-5-01`: installer `scripts/install_codex_agents.py` reuses `expertise.targets.codex.render_codex_agent`; default install and `--check` are idempotent and refuse conflicting files unless explicitly forced. Ruff and Semgrep pass. A fresh Codex 0.157.1 child rollout records `agent_role=quality-assurance`.
- Host inventories currently report `agentic-core` enabled at 0.3.3 in Codex and Copilot CLI 1.0.88. Each reports 11 plugin skills because the 57 routed workflows are still Markdown methods, not peer packages. Refresh both caches after the migration and version bump.
- The Copilot CLI confirms the package manifest and current skill inventory; full post-migration interactive `/skills list`/agent use remains a separate host smoke if non-interactive inventory cannot prove it.
- The plugin GitHub App MCP server remains blocked: `GITHUB_APP_ID`, `GITHUB_APP_INSTALLATION_ID`, and `GITHUB_APP_PRIVATE_KEY_PATH` are absent from the Codex process environment; Docker is available. Do not inspect or manufacture those values.
- Required implementation, independent QA, and Reviewer gates remain open for the remaining tasks. Do not mark `task_5` complete while the environment blocker or any selected gate remains unresolved.

## Constraints and lifecycle

- Do not modify `docs/harness-history/task_3/`, `docs/tasks-history/task_3.jsonl`, or `harness_factory/`.
- Do not send or queue a message to another Codex session.
- Do not inspect credentials, stage, commit, reset, or clean unrelated worktree state.
- Preserve the user's semantics: domain taxonomy only organizes the skills and provides progressive disclosure; each routed method is itself a full skill.
- Use the existing Codex renderer; do not add a second skill or agent-format converter.
- `TASK-5-04` cleanup completed: `EVIDENCE-PLUGIN-SCRATCH-CLEANUP` records removal of 10 unconsumed route scratch files and 3 generated plugin-local bytecode directories.
- Next action: ask the plugin Planner role for a bounded implementation plan for `TASK-5-03`, including its package/linter/test projection surfaces and the dependent MCP/session skill cleanup.
