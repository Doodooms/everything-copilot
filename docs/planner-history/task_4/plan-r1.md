# Implementation plan — task_4, revision 1

- Specification: `SPEC-CORE-ENHANCEMENTS@1` in `todos/in_progress/2026-09-27/agentic-core-enhancements-spec.md`
- Architecture: `docs/harness-history/task_4/architecture-r1.md`
- Base revision: `5c6dcd401e9a0d115e79c19f02de96ffed694686`
- Assigned risk: `L2` (Orchestrator-owned; no specialist may lower it)
- Worktree constraint: preserve the existing dirty tree and the separate `task_3` harness-evaluation changes; no stage/commit/reset/clean.
- Plan owner: Orchestrator fallback. The host rejected `agent_type=planner` as unavailable; no Planner agent ran.

## Phase 1 — Research and architecture

| Task | Owner | Objective and scope | Dependency | Exit evidence |
|---|---|---|---|---|
| `TASK-ARCH-ORCH-01` | Orchestrator | Define the semantic distinctions and boundaries in architecture-r1; scope only context usage, harness budgets, exchange validation, Rust MCP authoring, and todo tracking. | SPEC rev 1 | Architecture brief; no `task_3` paths changed. |
| `TASK-RESEARCH-CLI-RMCP-01` | Orchestrator | Verify official Codex/Copilot context and usage surfaces and current upstream Rust MCP SDK/API guidance. | SPEC rev 1 | Official source URLs, applicable command/API evidence, explicit limits. |
| `TASK-RESEARCH-CANDIDATES-01` | Orchestrator | Evaluate all prioritized and lower-priority candidates in the supplied repo list; omit its prohibited subjects/content. Focus on fit, license/maturity evidence, integration surface, cost, and triggers. | SPEC rev 1 | `todos/done/2026-09-27/integration-feasibility.md`; no third-party code added. |

## Phase 2 — Parallel plugin implementation

These work packages have disjoint source ownership and may run in parallel. Since host specialist roles are unavailable, the Orchestrator will implement them under the named plugin workflows and report that limitation.

| Task | Owner | Allowed files/components | Objective and output | Depends on |
|---|---|---|---|---|
| `TASK-IMPLEMENT-MH-01` | Orchestrator fallback to Implementer | `agentic-core/skills/multi-harness/{SKILL.md,workflows/smart-compact.md,workflows/harness-distribution.md,references/original-spec.md}`; relevant `agentic-core/skills/context-management/{SKILL.md,workflows/strategic-compact.md,workflows/token-optimization.md}` | Add live context/status, budget-aware routing, non-timer check points, safe compaction decisions, and cross-links while preserving Copilot/Codex session-contact constraints. | Architecture + official CLI evidence |
| `TASK-IMPLEMENT-EXCHANGE-01` | Orchestrator fallback to Implementer | `agentic-core/skills/orchestration/references/orchestrate/schemas/**`, `.../scripts/{validate_exchange.py,orchestrator.py}`, `.../references/manifest_schema.md`, `agentic-core/skills/orchestration/references/spec-driven-development/references/handoff-contracts.md`, `agentic-core/skills/orchestration/workflows/orchestrate.md`, and clean Copilot agent output contracts only if needed. Do not edit the already-dirty Orchestrator/Researcher agent files. | Add versioned language-neutral schemas for handoff/manifest/events/transitions; local structural/digest/commit validation; require a validated envelope before advancing. | Architecture |
| `TASK-IMPLEMENT-MCPRUST-01` | Orchestrator fallback to Implementer | `agentic-core/skills/plugin-engineering/SKILL.md`, `agentic-core/skills/plugin-engineering/workflows/{create-mcp.md,create-mcp-rust.md}` and only the necessary Rust MCP reference links | Route Rust MCP requests to a focused `rmcp` workflow; remove outdated all-in-one guidance from the active route and keep the intake source as provenance until completion. | Official rmcp evidence |

## Phase 3 — Tracking, validation, and plugin refresh

| Task | Owner | Objective and scope | Dependency | Exit evidence |
|---|---|---|---|---|
| `TASK-TRACK-01` | Orchestrator | Add `todos/README.md`, record the three source dispositions, write a dated completed report, and move reviewed source files to dated `done` only when their review is complete. Put deferred candidates/triggers in the dated `in_progress` follow-up plan. | Research + implementation | Index links resolve; no source is lost. |
| `TASK-VALIDATE-01` | Orchestrator | Run the relevant plugin skill validators, validate good/bad schema examples locally, lint touched Python through `uv`/Ruff, inspect diffs and task state. Do not touch or run the separate `task_3` test suite. | All implementation tasks | Recorded exact commands/results; no claim of independent QA. |
| `TASK-REVIEW-01` | Orchestrator | Perform focused static/security review of schema handling, digest/path resolution, quota/context claims, and `rmcp` guidance. The Reviewer and QA host roles were unavailable; record that independent gates could not run. | Validation | Findings, fixes or explicit residual risks. |
| `TASK-PLUGIN-SYNC-01` | Orchestrator | Use the plugin's update workflow to refresh the already-installed local cache after source validation; preserve package identity and the phase-1 worktree. No marketplace or account/configuration change. | Validation + review | Source/cache file manifest and digest comparison; no harness/model call. |

## Acceptance mapping

- AC-1/AC-2: `TASK-IMPLEMENT-MH-01` and `TASK-VALIDATE-01`.
- AC-3: `TASK-IMPLEMENT-EXCHANGE-01` and `TASK-VALIDATE-01`.
- AC-4: `TASK-RESEARCH-CLI-RMCP-01`, `TASK-IMPLEMENT-MCPRUST-01`, and `TASK-VALIDATE-01`.
- AC-5: `TASK-RESEARCH-CANDIDATES-01` and `TASK-TRACK-01`.
- AC-6: `TASK-TRACK-01` and the evidence-based disposition report.
- AC-7: `TASK-TRACK-01`.
- AC-8: a scope guard across all tasks, checked again during review.

## Skipped gates and risks

- Specialist Planner, Architect, Implementer, QA, and Reviewer roles are not callable in the current host; the Orchestrator will do local, bounded fallback work and must not claim specialist/independent results.
- No Copilot CLI call, Codex CLI session query, or other-harness resume: the prior Copilot quota is exhausted and the active-session surfaces are unavailable from this tool context.
- No end-to-end MCP server build: this task authors a skill, not a production MCP server. The workflow examples will be grounded in upstream docs; no server source is being introduced.
- No repository-wide tests, full audit, stage, or commit. Only focused package/schema/static validation is in scope.

## DAG

```text
SPEC-CORE-ENHANCEMENTS@1
  ├─ TASK-ARCH-ORCH-01 ─┬─ TASK-IMPLEMENT-MH-01 ─┐
  ├─ TASK-RESEARCH-CLI-RMCP-01 ─ TASK-IMPLEMENT-MCPRUST-01 ─┤
  ├─ TASK-RESEARCH-CANDIDATES-01 ──────────────────────────┤
  └────────────────────── TASK-IMPLEMENT-EXCHANGE-01 ─────┤
                                                          ├─ TASK-TRACK-01
                                                          ├─ TASK-VALIDATE-01
                                                          ├─ TASK-REVIEW-01
                                                          └─ TASK-PLUGIN-SYNC-01
```
