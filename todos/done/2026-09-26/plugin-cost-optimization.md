# Plugin cost optimization

**Date:** 2026-09-26  
**Status:** done

## Objective

Reduce unnecessary context and routing cost in the self-contained `agentic-core` plugin while preserving role ownership and correctness.

## Scope

- Support one-level, package-local skill workflows with point-of-need references.
- Measure projected agent context as definition + top-level `SKILL.md` + selected workflows + known tool schemas; exclude references.
- Make local skill selection and risk-proportional escalation explicit in authoring guidance.
- Reject MCP tool names unless the exact tool is declared and projected.
- Check Codex output structure against its documentation and whether the host supports a parent-context reference.

## Constraints

- Preserve existing user changes; do not stage, commit, branch, create a worktree, or open a PR.
- Do not run Codex runtime tests or migrate unrelated skills/agents.
- Keep all source/context measurements local; token estimates remain advisory.

## Outcome

- Added one-level `workflows/` subprocedures to the skill package contract, with point-of-need references, deterministic scaffolding, and linter checks for metadata, paths, route targets, nesting, and workflow-to-workflow links.
- Updated context measurement to count the agent definition, loaded `SKILL.md` files, selected workflows, and available local tool schemas. References are reported as excluded paths and never opened or counted.
- Required local `<agent-skills>` policies and native `skill` access where needed; encoded risk-proportional escalation and exact MCP tool catalogs in authoring and validation.
- Added `mcp_servers[].tools` to pack schema/IR validation and require a tool to be both exactly cataloged and projected to the agent.
- Removed the Orchestrator's unvalidated `github/*` tool selector. It retains `execute` for authorized `gh` CLI lifecycle work.
- Documented that subagents do not receive a readable parent-conversation handle; handoffs must carry bounded context and durable artifact references.

## Verification

- Focused unit tests: 98 passed across context measurement, agent validation, embedded templates, scaffold, workflow linting, Expertise Pack validation/compilation, and core plugin sources.
- `create-skill` validator passed on both `create-skill` and `create-agent`.
- `create-agent` validator passed on all 9 retained core agents.
- Expertise Pack tests confirmed workflow files survive portable, Copilot, and Codex static compilation. No Codex runtime test was run.
- Tests and direct validators used `PYTHONDONTWRITEBYTECODE=1`. No changes were staged or committed.

## Residual cost evidence

The local `local-regex-estimate-v1` estimator reports these top-level `SKILL.md` counts (references, selected workflows, and tool schemas are not included in these single-file measurements):

- `create-agent`: 4,446
- `create-skill`: 2,495
- `create-agent-plugin`: 2,147
- `orchestrate`: 2,658
- `spec-driven-development`: 2,123
- `tdd`: 1,868
- `token-optimization`: 1,168

These are approximate local counts, not model-token counts. The measured authoring and orchestration skills remain above the advisory 1,500-token restructuring signal; this pass establishes and validates the progressive workflow and measurement foundation, but does not compress every existing skill. A follow-up should prioritize separating genuinely distinct creation, repair, and review paths, then measure representative agent+skill+workflow projections with the actual host schemas available. Codex's emitted MCP configuration remains plugin-wide, so per-agent isolation is not claimed.
