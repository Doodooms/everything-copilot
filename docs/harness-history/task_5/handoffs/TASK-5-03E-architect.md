# Architect handoff — TASK-5-03E

> **SUPERSEDED by plan r10 and architecture r6.** This handoff asks for peer-skill composition and uses the mistaken standalone-package topology. Keep it as history only; reassess any useful workflow composition from the original nested sources during `TASK-5-03A`.

- Parent task: `task_5`
- Task: `TASK-5-03E`
- Attempt: `peer-skill-composition-architect-1`
- Assigned role: plugin `architect`
- Risk: `L2` (already assigned; do not downgrade)
- Specification: `SPEC-AGENTIC-CORE-NORMALIZATION@1`, revision 1
- Current architecture: ADR-ACN-001/002 in `architecture-skill-topology-r2.md`; ADR-ACN-003 covers the exact shared MCP support reference.
- Current plan: `docs/planner-history/task_5/plan-r6.md`, revision 6.

## Decision request

Read-only review of the method composition rule before implementing the 57 workflow-to-skill conversions.

The current ADR-ACN-001 says a peer method skill does not route onward to another method. However, the existing `plugin-engineering/workflows/create-mcp.md` explicitly selects `create-mcp-rust` when Rust is required, and both are in the user-requested conversion. The user's requirement is that each routed workflow becomes a complete skill package and that domain taxonomy provides organization and two-stage disclosure (domain router → selected method skill).

Assess whether preserving deliberate skill composition (including this existing generic-to-Rust specialization) is compatible with complete peer skill packages and two-stage taxonomy. Define a narrow composition rule and linter/route-graph implications that preserve existing behavior, avoid creating nested taxonomy, and maintain package/path safety. Inspect any other existing workflow-to-workflow composition evidence before deciding. Do not remove behavior or simply restate the current prohibition.

## Constraints

- Do not edit files.
- Do not change the user's two-stage domain → method discovery intent or peer package topology.
- Do not reopen `ADR-ACN-003` MCP shared-reference placement unless composition findings directly require it.
- Do not use host operations, contact sessions, inspect credentials, or perform Git lifecycle actions.

## Return

Return `success | partial | failed`, a concrete adopted-rule recommendation, source evidence, allowed composition forms, route graph/linter implications, risks, assumptions, `changed_files: []`, and the next owner. Identify any requirement conflict explicitly rather than silently preserving the architecture wording.
