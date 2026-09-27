# Planner handoff — TASK-5-03

> **SUPERSEDED by plan r10 and architecture r6.** Historical task instructions only; follow the nested workflow topology and canonical subskill body structure in the current plan.

- Parent task: `task_5`
- Task: `TASK-5-03`
- Attempt: `workflow-skill-plan-1`
- Assigned role: plugin `planner`
- Risk: `L2` (already assigned; do not downgrade)
- Specification: `todos/in_progress/2026-09-27/agentic-core-normalization.md`, `SPEC-AGENTIC-CORE-NORMALIZATION@1`
- Approved architecture: `docs/harness-history/task_5/architecture-skill-topology.md`, revision 1
- Current plan: `docs/planner-history/task_5/plan-r3.md`, revision 3
- Base revision: `5c6dcd401e9a0d115e79c19f02de96ffed694686`

## Request

Planning only; do not edit plugin, test, or task files. Inspect current source and produce an executable bounded plan for the remaining tasks:

1. `TASK-5-03`: migrate all 57 routed workflow methods into complete peer skill packages discoverable under `agentic-core/skills/<skill-id>/SKILL.md`. Preserve the user's requirement that each method itself follows the same skill package contract as a domain skill, while domain taxonomy remains a two-step progressive-disclosure layer. Avoid maintaining duplicate editable copies.
2. `TASK-5-05`: make `create-mcp` and `create-mcp-rust` complementary, validated, and non-duplicative; preserve Rust-specific `rmcp` constraints.
3. `TASK-5-06`: incorporate same-harness session coordination, distinguishing observed status, explicit authorization, queue acceptance, actual consumption/reply, and bounded handoff/resume. The plan must not send or queue a message to another session.

## Required inspection and output

- Map all 57 current routed files to stable IDs and destination skill directories. Identify relative links/assets that need relocation handling.
- Inspect domain routers, `skill_lint_core.py`, source tests/materializers, package metadata, and both-host discoverability assumptions.
- Define small implementation tasks, exact allowed file scopes, dependencies, outputs, validation commands, exit checks, migration rollback/compatibility behavior, and QA/Reviewer ownership.
- Identify shared versus Rust-only MCP guidance and the minimal placement needed to avoid procedure duplication.
- Identify the canonical location and content boundaries for same-harness session coordination.
- Preserve already completed `TASK-5-01`, `TASK-5-02`, and `TASK-5-04`. Do not inspect credentials, use Copilot runtime, modify `task_3`/`harness_factory`, or perform Git lifecycle actions.
- Return findings and a proposed plan as a handoff only. Root Orchestrator will reconcile and approve it before implementation.
