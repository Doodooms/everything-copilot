# Agentic Core skill topology

> **Superseded for the subskill content contract by revision 6.** Retain this revision for the original 11-domain / nested-workflow topology decision; revision 6 clarifies that nested subskills also use the canonical skill body structure.

- Revision: 5; supersedes the mistaken peer-package topology in r4.
- Specification: `SPEC-AGENTIC-CORE-NORMALIZATION@2`.
- Requirements: `REQ-1`.
- Acceptance criteria: `AC-1`.
- Risk: `L2`.
- Decision authority: the user's clarification, recorded by the root Orchestrator; source contract corroborated by the current workflow template and linter.
- Status: adopted for current implementation.

## ADR-ACN-001 — Keep domain skills and workflow subskills nested

Keep 11 domain expertise packages as the only top-level Agent Skill packages under `agentic-core/skills/<domain>/SKILL.md`. Each domain package owns its subdomain expertise procedures as `agentic-core/skills/<domain>/workflows/<id>.md`.

Each workflow subskill is a complete procedure with its own workflow metadata (`id`, `description`, `invoke_for`, `avoid_for`, and `references`) and full stepwise instructions. It stays inside the owning domain package; it is not an independent skill package and has no peer `skills/<id>/SKILL.md` directory. The domain skill remains the discoverable entrypoint and routes to only the relevant workflow file. This preserves two-stage progressive disclosure: domain → selected subskill.

Do not create a third taxonomy level, promote workflows to top-level skills, or replace the parent router with a flat list of all 58 methods.

## Evidence and implementation constraints

- `agentic-core/skills/plugin-engineering/references/create-skill/assets/workflow-template.md` defines the nested workflow metadata and complete stepwise procedure and says it is part of its parent skill package, not a wrapper or independent skill.
- `agentic-core/skills/plugin-engineering/references/create-skill/scripts/skill_lint_core.py` separately validates a domain `SKILL.md` and its immediate `workflows/*.md`; workflow references resolve inside the owning domain package.
- The current inventory is 11 domain entrypoints and 58 nested workflows: 57 entries in the earlier migration source map plus `orchestration/workflows/chatgpt-work-handoff.md`, which was added separately. Verify both inventories from source and installed plugin metadata; do not count workflow files as independent discoverable skills.
- Keep workflow-specific references in the domain package. Re-evaluate any shared-support declarations against original nested source paths; do not carry forward peer-package allowlists that were derived from copied packages.
- MCP language specialization stays as sibling workflows `create-mcp` and `create-mcp-rust` under `plugin-engineering/workflows/`; the shared domain reference remains under `plugin-engineering/references/` if both workflows use it.
- Preserve existing procedure content while auditing host-specific markers. The prior r4 host-neutral marker directive is superseded as a blanket migration rule; decide any required changes from current host behavior and evidence.

## Supersession and limits

This revision corrects the topology only. It does not establish that every current workflow is complete or valid, that host-specific tool markers work in Codex, or that the Codex and Copilot runtimes load workflow links identically. These require the focused implementation, QA, and host checks in plan r9.

The 57 peer packages created under the mistaken r8 interpretation were moved to `/tmp/agentic-core-erroneous-peer-skills-20260927` and are no longer part of the plugin source tree. Their QA report is historical evidence about those copies, not the nested source workflows.
