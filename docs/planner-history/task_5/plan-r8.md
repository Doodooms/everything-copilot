# Implementation plan — task_5, revision 8

> **SUPERSEDED before implementation by plan r10 and architecture r6.** This revision incorrectly turns 57 workflow subskills into top-level `SKILL.md` packages and reverses the intended progressive-disclosure model. Keep r8 as history only; use the current nested subskill and body-structure contract.

- Specification: `SPEC-AGENTIC-CORE-NORMALIZATION@1`, revision 1 at `todos/in_progress/2026-09-27/agentic-core-normalization.md`.
- Architecture: `docs/harness-history/task_5/architecture-skill-topology-r4.md` (revision 4; `ADR-ACN-001`–`ADR-ACN-006`).
- QA evidence: `docs/harness-history/task_5/qa-03a-preflight-summary.md`, `QA-RUN-TASK-5-03A-20260927-01`.
- Planner input/return: `docs/harness-history/task_5/handoffs/TASK-5-03-plan-revision.md`; plugin Planner returned the proposed r8 in-message, no files changed. The Orchestrator reconciled its sequencing sentence against the explicit dependency table and checked the six ACs against the canonical spec.
- Base revision: `5c6dcd401e9a0d115e79c19f02de96ffed694686`.
- Assigned risk: `L2`.
- Owner: root Orchestrator.
- Status: approved for implementation; `TASK-5-03A` remains in progress.
- Supersedes: plan r7 for current task sequencing; does not change user requirements or acceptance criteria.

## User-authoritative package contract

Every routed workflow is itself a complete skill package, with the same canonical Agentic Core skill structure as the domain package: `SKILL.md`, standard frontmatter, and the established critical/general/risk/rules/workflow body sections. Put the complete method procedure in the method skill's own `<workflow>` section. Keep each method as an immediate peer directory under `agentic-core/skills/`.

The only taxonomy and progressive-disclosure path is **domain router → selected method skill**. The old validator assumption that a method procedure must stay in `skills/<domain>/workflows/` is obsolete. Do not move methods back under `workflows/` or add method-level taxonomy directories. Use body tables for typed skill relationships; do not add unsupported custom routing fields to frontmatter. A `compose` edge is an execution relationship, not another taxonomy level.

## Task DAG

| Task | Owner | Dependencies | State | Scope and exit check |
|---|---|---|---|---|
| `TASK-5-01` Codex agent projection and installation | Orchestrator using operations | — | Complete | Nine canonical roles installed under the Codex-supported agents directory; a fresh process loaded `quality-assurance`. |
| `TASK-5-02` Skill-topology architecture | Architect; adopted by Orchestrator | — | Complete | Domain and method skills are immediate peer packages; domain → selected method is the two-stage taxonomy. |
| `TASK-5-03E` Reconcile peer-skill composition policy | Architect; adopted by Orchestrator | `TASK-5-02` | Complete | ADR-ACN-004 defines typed route/compose/read/support relationships without adding a taxonomy level. |
| `TASK-5-03F` Resolve QA-discovered package/support contract | Architect; adopted by Orchestrator | `TASK-5-03A` preflight evidence, `TASK-5-03E` | Complete | Architect returned partial because no native skill-loading tool was exposed; Orchestrator reviewed the source contract and adopted bounded ADR amendments in architecture r4. |
| `TASK-5-03G` Reconcile QA findings into plan r8 | Planner; adopted by Orchestrator | `TASK-5-03F`, QA run `QA-RUN-TASK-5-03A-20260927-01` | Complete | The approved plan incorporates package, source-fidelity, support, relationship, host-portability, QA, and rollout findings. |
| `TASK-5-03A` Repair and complete 57 peer method skills | Implementer; one bounded attempt | `TASK-5-02`, `TASK-5-03E`, `TASK-5-03F`, `TASK-5-03G` | **In progress** | All 57 method packages follow the canonical skill contract; procedure meaning reconciles with sources, including semantic review of the 18 triage outliers; all package links resolve; no active host-only markers remain in skill bodies; typed relationships agree with procedure; the compose graph is acyclic; all 32 shared-support pairs reference the 16 canonical source files. Preserve source methods and unrelated dirty files. |
| `TASK-5-04` Verified plugin scratch cleanup | Orchestrator using operations | — | Complete | Removed 10 unconsumed `.workflow-routes.tmp` files and 3 plugin-local generated `__pycache__` directories; no unrelated caches changed. |
| `TASK-5-05` MCP authoring skill composition | Orchestrator | `TASK-5-03A` | In progress | Parent task for design and implementation of complementary MCP authoring skills. |
| `TASK-5-05A` MCP guidance composition design | Architect | `TASK-5-02` | Complete | ADR-ACN-003 keeps common transport/security guidance canonical and permits its exact MCP references. |
| `TASK-5-05B` Complete MCP authoring skills and read-only GitHub launch | Implementer | `TASK-5-03A`, `TASK-5-03E`, `TASK-5-05A` | Planned | `create-mcp` and `create-mcp-rust` are complete, complementary skills without copied procedures; common guidance remains canonical, Rust/`rmcp` constraints remain local; fix package-local validator invocation. Update the launcher to the user-supplied Docker behavior including `stdio --read-only`, runtime env configuration, and read-only PEM mount; never store or print credentials. |
| `TASK-5-06` Same-harness session coordination skill | Implementer | `TASK-5-03A` | Planned | Add a complete peer skill from `todos/harness/codex-session-communication.md`; distinguish observed status, explicit contact authorization, queue acceptance, actual consumption/reply, and bounded handoff/resume. Do not contact other sessions. |
| `TASK-5-03B` Update routers and skill references | Implementer | `TASK-5-03A` | Ready, blocked on `TASK-5-03A` | Update all domain routers and affected agent references to stable peer IDs; keep two-stage disclosure and remove obsolete source-workflow routes only after links and provenance pass. |
| `TASK-5-03C` Update package validation, authoring contract, and materialization | Implementer | `TASK-5-03A`, `TASK-5-03B`, `TASK-5-05B`, `TASK-5-06` | Planned | Update the canonical template, linter, validation guidance, package materializer, and focused source tests for complete direct-child method skills, body relationship consistency, exact shared-support pairs, package/materialized links, symlink/path containment, and an acyclic compose graph. Reject old nested-workflow-only assumptions and active `#tool:`/`#file:` contracts in skill bodies. |
| `TASK-5-03D` Independent QA, then Reviewer | Quality Assurance, then Reviewer | `TASK-5-03B`, `TASK-5-03C`, `TASK-5-05B`, `TASK-5-06` | Planned | QA independently falsifies inventory, body/source semantics, routers, links, shared files, host-neutral procedures, MCP behavior, and session safety. Reviewer checks AC-1–AC-6 against the canonical spec and remaining risks. |
| `TASK-5-07` Package refresh and dual-host verification | DevOps | `TASK-5-03D`, `TASK-5-04`, `TASK-5-05`, `TASK-5-06` | Planned | Refresh each configured host, compare source/cache, confirm all 69 skills and nine Codex agent TOMLs, and verify the configured GitHub App MCP initializes in read-only mode in a fresh process. |
| `TASK-5-08` Todo audit and convergence | Orchestrator | `TASK-5-07` | Planned | Reconcile done/in-progress/backlog files, reports, and ledgers; put verified completed reports in `todos/done`; keep `cost-eval-opt` separate and resume only after this task converges. |

### Dependency sequencing

Complete `TASK-5-03A` first. After it completes, `TASK-5-03B`, `TASK-5-05B`, and `TASK-5-06` may proceed as independent bounded tasks. `TASK-5-03C` joins their results. `TASK-5-03D` runs QA then Reviewer only after 03B, 03C, 05B, and 06 complete. `TASK-5-07` refreshes hosts only after the required review and cleanup gates. There is no requirement for 03B to finish before 05B or 06 starts.

## Acceptance mapping

- **AC-1 / REQ-1:** `TASK-5-03A`, `TASK-5-03B`, `TASK-5-03C`, `TASK-5-03D`, and `TASK-5-07`.
- **AC-2 / REQ-2:** `TASK-5-05A`, `TASK-5-05B`, `TASK-5-03C`, `TASK-5-03D`, and `TASK-5-07`.
- **AC-3 / REQ-3:** `TASK-5-04`, `TASK-5-03D`, and `TASK-5-07`.
- **AC-4 / REQ-4:** `TASK-5-06` and `TASK-5-03D`.
- **AC-5 / REQ-5:** `TASK-5-01` and `TASK-5-07`.
- **AC-6 / REQ-6:** `TASK-5-08`, after task state, reports, and host inventory converge.

## Validation and gates

- Reconcile all 57 method procedure bodies with their mapped source; do not treat the QA's sequence-similarity threshold as semantic acceptance.
- Validate all 68 current packages and 69 after `TASK-5-06` against the same skill-level structure. The validator must understand direct-child method packages and domain routers; it must not require method procedures under `workflows/`.
- Parse body relationship tables and compare each edge with the actual procedure. Validate all 32 exact shared-support pairs plus ADR-ACN-003's MCP pair; confirm each target resolves under `agentic-core/skills/` and exists in the materialized plugin. Reject missing files, symlinks, undeclared pairs, arbitrary traversal, and non-allowlisted package escapes.
- Confirm no unresolved `support` placeholders remain, no method reads itself by mistake, no malformed peer IDs remain, and the `compose` graph has no cycles. A context-only `read` edge must not execute another procedure.
- Replace host-specific markers in skill instructions with active-harness language and ordinary Markdown links, preserving behavior. Do not claim tool invocation compatibility until a fresh Codex process and Copilot runtime checks exercise the relevant host interfaces.
- Run focused source/materializer/linter tests after 03C. Use `uv` for Python tests and Ruff for any edited Python files; use Semgrep on changed code where relevant. Keep these checks separate from costly behavioral evaluation.
- QA performs independent falsification; Reviewer maps final evidence to all six canonical acceptance criteria. DevOps performs refresh and host inventory after review.

## Constraints

- Preserve all unrelated dirty worktree state; no stage, commit, reset, or clean.
- Do not modify `docs/harness-history/task_3/`, `docs/tasks-history/task_3.jsonl`, or `harness_factory/`.
- Do not send or queue messages to another Codex session.
- The user supplied GitHub App runtime settings on 2026-09-27. Use only env-based runtime configuration, the given read-only launcher behavior, a read-only PEM mount, and fresh-process initialization checks. Never read or print the PEM contents.
- Preserve source workflows and support until their package targets, route edges, and support dependencies pass; remove source copies only after consumers and provenance are reconciled.
- Use the existing `expertise/targets/codex.py` only for its supported Codex agent projection; do not add a competing converter or claim that it rewrites skill-body directives.
- No expensive `cost-eval-opt` runs belong to this cleanup task.

## Planner and Orchestrator reconciliation

The installed plugin Planner returned this graph in a fresh read-only Codex process and did not edit files. The Orchestrator corrected one contradictory critical-path sentence by making the table dependencies explicit. The canonical specification was located and checked after the Planner handoff: `todos/in_progress/2026-09-27/agentic-core-normalization.md` contains all six acceptance criteria and their requirement mapping. QA failed the initial 03A preflight; 57/57 target files exist, but source fidelity, links, relationships, shared support, and host-body instructions remain incomplete. The failed attempt was cancelled because it returned no authoritative handoff. The Architect's partial read-only return and the Orchestrator's adopted bounded decisions are recorded in architecture r4.
