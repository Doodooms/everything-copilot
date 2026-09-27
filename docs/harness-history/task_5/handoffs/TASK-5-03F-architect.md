# Architect handoff — TASK-5-03F

> **SUPERSEDED.** The package-topology direction in this handoff is incorrect; do not implement peer method packages. See `../topology-correction-2026-09-27.md`, architecture r6, and plan r10.

- Parent task: `task_5`
- Task: `TASK-5-03F` — reconcile peer-skill package and shared-support contract
- Attempt: `peer-skill-contract-architect-1`
- Assigned role: installed plugin `architect`
- Risk: `L2`
- Specification: `SPEC-AGENTIC-CORE-NORMALIZATION@1`, revision 1 (canonical spec file not present in the prior QA packet; use user statement and supplied architecture as authority)
- Base revision: `5c6dcd401e9a0d115e79c19f02de96ffed694686` on `main`
- Prior architecture: `docs/harness-history/task_5/architecture-skill-topology-r3.md`, revision 3 (`ADR-ACN-001`–`ADR-ACN-004`)
- Approved implementation plan: `docs/planner-history/task_5/plan-r7.md`, revision 7
- Evidence: `docs/harness-history/task_5/qa-03a-preflight-summary.md`, QA run `QA-RUN-TASK-5-03A-20260927-01`

## User-authoritative requirement

The user clarified: workflows inside a skill are skills in their own right and must use the same skill structure; the topology/taxonomy exists only for two-stage progressive disclosure and better organization inside the harness. Preserve a domain router → directly selected method `SKILL.md`. Do not restore nested `skills/<domain>/workflows/<method>.md` as the method surface or add a taxonomy layer under a method.

Current `main` is the active branch; local `master` is its ancestor (`git merge-base master main` equals `master`). The canonical `skill-template.md` was added on `main` after `master`. There is no merge conflict. The existing validator's nested-workflow placement assumption is stale for peer methods, but the current skill-authoring template's standard skill package/body contract may still apply. Do not equate a stale validator route with the user's skill requirement.

## Questions for the Architect

1. **Complete skill contract.** Given the user requirement and current `agentic-core/skills/plugin-engineering/references/create-skill/assets/skill-template.md`, define the minimum canonical structure for a method skill: standard frontmatter, body sections/risk contract, and where its complete procedure lives. Account for Codex's native skill parser and GitHub Copilot Agent Plugins without adding custom frontmatter route schemas. Reconcile this with ADR-ACN-001/004 and the old validator errors. Keep the method procedure directly inside that peer package's `SKILL.md`.
2. **Shared support.** QA found 32 unresolved support declarations for 16 unique shared reference files used by 12 method packages across agent authoring/validation, plugin creation/update, skill authoring/maintenance, test design/quality review, and implementation design. The sources still exist under their domain packages. ADR-ACN-003 presently authorizes exactly one MCP shared reference pair. Recommend a deterministic, portable source/materialization policy for these additional files that avoids arbitrary traversal, preserves one source of truth where practical, and can be checked in TASK-5-03C and host validation. Identify whether there is a safe, bounded expansion of an explicit allowlist or whether method-local copies are required; state exact implications for source tree and plugin materialization.
3. **Execution cycle.** QA found `token-optimization → smart-compact → token-optimization` in declared `compose` edges. Read both source methods and targets; recommend which edge is a real bounded skill invocation and whether the other is context-only (`read`) or should be removed/rephrased. Do not propose recursive execution. Preserve the user's two-stage taxonomy; distinguish taxonomy depth from deliberate bounded method composition.
4. **Host directives.** QA found 150 `#tool:` / `#file:` markers across 36 packages, including `#tool:vscode/askQuestions` in `create-mcp`. `expertise/targets/codex.py` converts Expertise Pack agent contributions; it has no skill body/tool-marker adapter. The native plugin materializer copies `SKILL.md` content. Recommend a host-neutral skill-body rule, including how tools supplied by each harness and stable support links should be referenced, without dropping actual procedure behavior. Do not claim a runtime compatibility result.

## Return contract

Provide a concise architecture decision with exact ADR language or a proposed revision, evidence paths, options considered, consequences, and checks TASK-5-03C/QA must enforce. Read-only only: do not edit source, plans, ledgers, todos, or contact sessions. Do not inspect credentials, run Copilot, or change branch/worktree state. The Orchestrator adopts or revises the plan after the handoff; the Architect does not implement.
