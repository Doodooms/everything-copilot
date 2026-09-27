# Implementation plan — task_5, revision 4

> **SUPERSEDED by plan r10 and architecture r6.** Historical record only; the current structure is 11 domain `SKILL.md` entrypoints with complete subskills under their owning `workflows/` directories. Do not implement peer skill packages from any earlier plan.

- Specification: `SPEC-AGENTIC-CORE-NORMALIZATION@1`.
- Architecture: `docs/harness-history/task_5/architecture-skill-topology.md` (revision 1; `ADR-ACN-001`, `ADR-ACN-002`).
- Base revision: `5c6dcd401e9a0d115e79c19f02de96ffed694686`.
- Assigned risk: `L2`.
- Owner: root Orchestrator.
- Status: approved for implementation.
- Supersedes: `plan-r3.md` task sequence and resume point; it does not change specification scope or acceptance criteria.
- Planner handoff: `planner-handoff-r1.md`; source/destination inventory reconciled by the Orchestrator in `workflow-skill-source-map.md`.

## Task DAG

| Task | Owner | Dependencies | State | Scope and exit check |
|---|---|---|---|---|
| `TASK-5-01` Codex agent projection and installation | Orchestrator using operations | — | Complete | Nine canonical roles installed under `CODEX_HOME/agents`; fresh process loaded `quality-assurance`. |
| `TASK-5-02` Skill-topology architecture | Architect; adopted by Orchestrator | — | Complete | Domain and method skill packages are peers at `skills/` root; domain → selected method remains progressive disclosure. |
| `TASK-5-03A` Create 57 peer method packages | Implementer | `TASK-5-02` | Ready | Convert every entry in `workflow-skill-source-map.md` into a complete `skills/<id>/SKILL.md`; preserve procedure text and only move support resources after tracing consumers. All package-relative support links resolve. |
| `TASK-5-03B` Update routers and skill references | Implementer | `TASK-5-03A` | Ready | Update domain routers and affected agent references to select stable peer-skill IDs; no route points to an obsolete workflow path. |
| `TASK-5-03C` Update package validation and authoring contract | Implementer | `TASK-5-03A`, `TASK-5-03B` | Ready | Update canonical skill linter, folder template, validation guidance, package materializer assumptions if applicable, and source tests. The checks prove package completeness, ID uniqueness, route coverage, and package-local references. |
| `TASK-5-04` Verified plugin scratch cleanup | Orchestrator using operations | — | Complete | Removed 10 unconsumed `.workflow-routes.tmp` files and 3 plugin-local generated `__pycache__` directories; no unrelated caches changed. |
| `TASK-5-05` MCP authoring skill composition | Orchestrator | `TASK-5-03A` | In progress | Parent task for the architecture decision and Implementer work below. |
| `TASK-5-05A` MCP guidance composition design | Architect | `TASK-5-02` | Ready | Decide how both full peer skills reference one canonical common transport/security guide without escaping package rules or duplicating procedure; preserve Rust/`rmcp` specialization. |
| `TASK-5-05B` Implement MCP authoring skills | Implementer | `TASK-5-03A`, `TASK-5-05A` | Planned | `create-mcp` and `create-mcp-rust` are complete complementary skills; shared transport/security procedure is authored once and referenced, while Rust/`rmcp` constraints stay Rust-specific. |
| `TASK-5-06` Same-harness session coordination skill | Implementer | `TASK-5-03A` | Planned | Add a new peer method package in the `multi-harness` domain; it distinguishes observed status, explicit contact authorization, queue acceptance, consumption/reply, and bounded handoff/resume. It does not contact sessions. |
| `TASK-5-03D` Independent QA and Reviewer | Quality Assurance, then Reviewer | `TASK-5-03B`, `TASK-5-03C`, `TASK-5-05B`, `TASK-5-06` | Planned | Independently falsify package inventory, routers, links, MCP composition, and session safety; Reviewer checks acceptance mapping, architecture adherence, and open risks. |
| `TASK-5-07` Package refresh and dual-host verification | DevOps | `TASK-5-03D`, `TASK-5-04` | Planned | Bump local version, reinstall through each configured host lifecycle, compare source/cache, verify all 69 domain+method skills and nine Codex agent TOMLs, and verify GitHub MCP starts read-only with user-provided runtime configuration. |
| `TASK-5-08` Todo audit and convergence | Orchestrator | `TASK-5-07` | Planned | Reconcile all `done/`, `in_progress/`, and backlog files with task ledgers/reports; keep `task_3`, `harness_factory/`, and `cost-eval-opt` separate and unchanged. |

## Planner reconciliation

The plugin's `planner` role was invoked in a fresh, read-only Codex process and followed the installed `orchestration/implementation-planning` workflow. It found 57 non-empty stable method IDs and correctly identified the old router/linter/test assumptions, MCP overlap, and session-safety distinctions. Its handoff enumerated every ID by domain but not every source path, so the Orchestrator independently generated and checked `workflow-skill-source-map.md` before implementation. `TASK-5-06` adds one new peer skill from `todos/harness/codex-session-communication.md`; final inventory is 58 method skills plus 11 domain skills. The remaining MCP reference-composition boundary is delegated to the Architect before implementation. No accepted topology decision is reopened.

## Validation and gates

- Run the canonical create-skill package validator across all 69 domain and method packages.
- Run focused source/router/materializer tests, including `uv run pytest tests/test_agentic_core_sources.py` and any directly affected linter tests.
- Run Ruff check/format on modified Python files; use Semgrep on changed implementation scripts where relevant.
- Quality Assurance validates package/route/link inventories and adversarially checks method discoverability and the session-contact boundary.
- Reviewer evaluates AC-1 through AC-6 against the final evidence. DevOps performs cache and host-inventory checks only after QA/Review.
- Keep test and host validation independent of `task_3` evaluation runs; do not start costly behavioral benchmarks here.

## Constraints and blockers

- Preserve all unrelated dirty worktree state; do not stage, commit, reset, or clean it.
- Do not modify `docs/harness-history/task_3/`, `docs/tasks-history/task_3.jsonl`, or `harness_factory/`.
- Do not send or queue messages to another Codex session.
- Do not inspect or manufacture GitHub App credentials. The user supplied runtime IDs and a local PEM path on 2026-09-27; DevOps will verify only that the path is readable and run the plugin MCP server in read-only mode in a fresh process. Never print or read the PEM contents.
- Retain existing workflow source/support files until package references and route checks pass; remove obsolete copies only when the target package is verified and provenance/consumers are understood.
- Use the plugin's existing Codex projection adapter; do not add a competing converter.
