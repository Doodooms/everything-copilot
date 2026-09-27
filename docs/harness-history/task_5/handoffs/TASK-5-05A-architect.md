# Architect handoff — TASK-5-05A

> **SUPERSEDED by plan r10 for execution.** Preserve this design handoff as history; implement MCP authoring as sibling workflows under `plugin-engineering`.

- Parent task: `task_5`
- Task: `TASK-5-05A`
- Attempt: `mcp-skill-composition-architect-1`
- Assigned role: plugin `architect`
- Risk: `L2` (already assigned; do not downgrade)
- Specification: `SPEC-AGENTIC-CORE-NORMALIZATION@1`, revision 1
- Existing architecture: `ADR-ACN-001`, `ADR-ACN-002`; preserve peer skill layout and two-step domain → method disclosure.
- Implementation plan: `docs/planner-history/task_5/plan-r4.md`, revision 4

## Decision request

Read-only architecture decision for `TASK-5-05A`: choose how `create-mcp` and `create-mcp-rust`, after conversion into separate complete peer skill packages, share common transport/security authoring guidance from one canonical source without duplicating procedures, routing to another method skill, or allowing arbitrary path escapes.

Inspect the current MCP workflows, support tree, package linter/reference policy, plugin materializer, and user requirement. Assess practical options such as a domain-owned shared reference that both peer skills load by an explicitly allowed plugin-internal path, a plugin-root shared reference, or another structure consistent with the approved architecture. Preserve Rust/`rmcp`-specific requirements in the Rust skill.

## Constraints

- Do not change files or settle product scope.
- Do not change `ADR-ACN-001`/`ADR-ACN-002` or nest peer skills.
- Do not duplicate common procedures in both method skills.
- Do not invoke an external app, contact another session, inspect credentials, run tests, or perform Git lifecycle actions.

## Return

Return `success | partial | failed`, the selected structure, relevant options/tradeoffs, source evidence, affected file surfaces, risks/assumptions, validation implications, `changed_files: []`, and the next owner. If plugin-internal cross-skill references are unsupported by the relevant host/package contract, cite the evidence and return the issue for a bounded resolution.
