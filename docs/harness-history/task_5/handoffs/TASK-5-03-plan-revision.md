# Planner handoff — plan r8

> **SUPERSEDED.** The request in this handoff encodes the mistaken peer-package interpretation. Plan r10 and architecture r6 preserve workflow subskills beneath their domain package and define their canonical body structure.

- Parent task: `task_5`
- Task: `TASK-5-03G` — reconcile QA findings into an approved plan revision
- Attempt: `peer-skill-plan-r8-1`
- Assigned role: installed plugin `planner`
- Risk: `L2`; preserve assigned level.
- Base revision: `5c6dcd401e9a0d115e79c19f02de96ffed694686` on `main`.
- Current plan: `docs/planner-history/task_5/plan-r7.md`, revision 7.
- Architecture decision to adopt: `docs/harness-history/task_5/architecture-skill-topology-r4.md`, revision 4.
- QA evidence: `docs/harness-history/task_5/qa-03a-preflight-summary.md`.
- Architect return summary: `docs/planner-history/task_5/architect-contract-return.md`.
- User clarification: workflows are complete peer skills using the same skill structure; progressive-disclosure taxonomy is only domain router → selected method skill.

## Request

Revise the implementation plan to revision 8 based on the QA failure and adopted architecture revision 4. Preserve the user's explicit two-stage taxonomy; do not route the 57 methods back under `workflows/`. Require each direct-child method package to meet the current canonical Agentic Core skill structure and keep its complete procedure in its own `<workflow>` body section. Keep `TASK-5-03A` in progress until all 57 package defects are repaired and validated.

Include these implementation requirements in the plan:

1. Repair all 25 unresolved links in 12 methods; replace the 32 unresolved `support` placeholders with the exact 32 consumer/source pairs in ADR-ACN-005; ensure all 16 source files are materialized without arbitrary traversal.
2. Reconcile the 18 below-threshold/line-count-different source conversions against their source procedures; do not use sequence similarity as semantic acceptance.
3. Rewrite `#tool:` and `#file:` markers in all domain and method skill bodies as host-neutral instructions while preserving the procedure. Update the skill template and validator in TASK-5-03C; do not claim runtime tool compatibility before host checks.
4. Fix the `codex`/`copilot` self-read body errors, malformed `harness-distribution` references, and the compact-method compose cycle per ADR-ACN-004 revision 4.
5. Repair the `create-mcp` validator command/path and keep the MCP authoring skills complementary; retain `create-mcp` → `create-mcp-rust` specialization. Implement TASK-5-05B's GitHub App launcher using the user's approved Docker invocation including `stdio --read-only`, runtime env only, read-only PEM mount, and no key disclosure.
6. Add `end-to-end → test-levels.md` to the exact support allowlist. Ensure linter/materializer and focused checks prove all allowlisted targets exist and are included, while rejecting symlinks, undeclared pairs, and other package escapes.
7. Keep the existing top-level DAG and durable task/QA/Reviewer/DevOps/todo gates. Include a bounded implementation attempt followed by independent QA; no parallel mutation of the 57 peer packages.

The next implementer attempt should be `TASK-5-03A` with a new attempt ID and a focused remediation handoff based on the revised plan. Preserve source workflows and all unrelated dirty worktree files until downstream package, route, and support checks pass.

## Return contract

Return a proposed plan r8 with task dependencies, owners, states, acceptance checks, validation gates, risks, and next owner. Use the handoff artifacts above as authoritative; do not modify source skills, the old plan, manifest, task ledgers, tests, plugin cache, or host state. No Git operations or commits. Orchestrator adopts the returned plan and updates canonical state after checking it.
