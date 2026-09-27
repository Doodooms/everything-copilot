# Implementation plan — task_4, revision 2

- Specification: `SPEC-CORE-ENHANCEMENTS@2` in `todos/in_progress/2026-09-27/agentic-core-enhancements-spec.md`
- Architecture: `docs/harness-history/task_4/architecture-r2.md`
- Base revision: `5c6dcd401e9a0d115e79c19f02de96ffed694686`
- Assigned risk: `L2`
- Plan owner: Orchestrator fallback; host specialist roles are unavailable.

## Phase 1 — Architecture and research

| Task | Scope | Exit evidence |
|---|---|---|
| `TASK-ARCH-ORCH-01` | Reconcile the supplied architecture proposals against current plugin capabilities; record r2 decisions and bounded follow-ups. | Architecture brief and disposition report. |
| `TASK-RESEARCH-CLI-RMCP-01` | Verify official Codex/Copilot status surfaces and current upstream Rust MCP SDK guidance. | Direct official source links, applicability, limitations. |
| `TASK-RESEARCH-CANDIDATES-01` | Assess every in-scope candidate from the supplied repository list; no candidate code imports. | Feasibility report with classification, costs, triggers, and evidence depth. |

## Phase 2 — Plugin implementation

| Task | Owned paths | Objective |
|---|---|---|
| `TASK-IMPLEMENT-MH-01` | `agentic-core/skills/multi-harness/**`; selected `context-management` workflows | Add live-versus-estimated compaction, quota-aware routing, safe boundaries, memory provenance, and retrieval-state distinctions. |
| `TASK-IMPLEMENT-EXCHANGE-01` | Orchestration schemas/helper/docs | Validate handoffs, manifest payload and wrapper, events, transitions, commit identities, and artifact digests. |
| `TASK-IMPLEMENT-MCPRUST-01` | `agentic-core/skills/plugin-engineering/**` | Add the version-pinned Rust MCP authoring workflow to the existing route. |
| `TASK-IMPLEMENT-RESEARCH-01` | `agentic-core/skills/research/SKILL.md`, `workflows/existing-solution-research.md`, orchestration route | Add a bounded prior-art workflow before substantial new abstractions. |

## Phase 3 — Tracking, evidence, and package refresh

| Task | Objective | Exit evidence |
|---|---|---|
| `TASK-TRACK-01` | Add the todo index, disposition report, completed reports, and dated follow-up plan; move reviewed source files only after report creation. | Linked paths resolve; active and completed work are distinct. |
| `TASK-VALIDATE-01` | Validate schemas, positive/negative exchange examples, touched skill routing, and Ruff findings for the validator. | Exact commands/results; no unrelated test suite run. |
| `TASK-REVIEW-01` | Focused local review of path containment, Git/artifact claims, context/quota limits, and Rust guidance. | Findings and residual limitations; no independent gate claim. |
| `TASK-PLUGIN-SYNC-01` | Refresh the already-installed local plugin after source validation. | Installed version, nine-agent inventory, and source/cache comparison. |

## Deferred follow-up

- Add measured skill-load-path, reference-fan-out, and instruction-density reports only after selecting a representative benchmark and defining decision thresholds.
- Define automated memory staleness propagation only when a real provenance/dependency graph and approved memory store can supply the required source revisions.
- Consider external providers or governance runtimes only when a named product requirement and measured integration benefit appear.

## Gates and preservation rules

- The host cannot invoke Architect, Planner, Implementer, QA, or Reviewer roles in this session; Orchestrator fallbacks are recorded honestly.
- Do not run Copilot CLI while its supplied quota observation is exhausted. Do not query private stores or infer another session's usage.
- Do not modify `task_3`, `harness_factory`, its tests, pre-existing dirty agent files, stage files, or make a Git commit.

## Dependency order

```text
SPEC@2 → ARCH@2 / provider research → bounded plugin updates → validation/review → reports and todo index → plugin refresh
```
