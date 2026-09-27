# Skill topology correction — 2026-09-27

> The initial correction below restored nested workflows but underspecified their content shape. The user's later clarification and architecture r6 control implementation.

## Authority

The user's clarification is authoritative: each domain expertise skill contains subdomain expertise procedures under `workflows/`. Those procedures have the same completeness and stepwise structure expected of a skill, but are not independently registered Agent Skills and must not become peer `skills/<id>/SKILL.md` packages. The progressive-disclosure path remains domain skill → one selected workflow subskill.

## Repository evidence

- `agentic-core/skills/plugin-engineering/references/create-skill/assets/workflow-template.md` defines workflow frontmatter (`id`, `description`, `invoke_for`, `avoid_for`, `references`) and a complete, stepwise procedure directly under `workflows/`; it explicitly says this is part of the parent skill package, not an independent skill.
- `agentic-core/skills/plugin-engineering/references/create-skill/scripts/skill_lint_core.py` validates those workflow files separately from the domain `SKILL.md` contract and resolves references within the owning domain package.
- The current source tree and refreshed Codex cache each have exactly 11 domain `SKILL.md` entrypoints and 59 workflow subskills; neither contains workflow peer `SKILL.md` packages. An earlier cache snapshot had 57 nested workflow files, not 57 discoverable skills; the two missing current workflow files were installed from the approved local source.
- The 57 direct-child peer-package copies produced during the mistaken attempt are quarantined outside the plugin source tree under `/tmp/agentic-core-erroneous-peer-skills-20260927`. They are not installed routes. The same number in the historical source map refers to old procedure IDs; neither count defines the current skill catalog.

## Supersession

- Architecture revisions 1–4 and plan revisions 1–8 remain as history; r4/r8's peer-package model is superseded.
- `qa-03a-preflight-summary.md` tested the erroneous peer copies with the wrong validator contract. It is not evidence that the original nested workflow files fail.
- The old peer destination map is retained as historical provenance. `workflow-subskill-inventory.md` is the current source inventory.
- Reassess copied relationship tables, shared-support allowlists, and package-local paths against the original nested sources. Do not carry over r4's peer-package `ADR-ACN-005`/`ADR-ACN-006` requirements without fresh evidence.

## Completed validation

The 11 domain routers link to their 59 immediate workflow subskills; all 11 domain validators and the focused source tests pass. The Codex cache was reinstalled from the local source and independently counted at 11 domain `SKILL.md` files, 59 workflow subskills, and zero peer workflow packages. Nine custom-agent projections also pass the installer check. A fresh Codex process loaded the installed orchestration domain skill. The user's workspace GitHub MCP is configured by `.vscode/mcp.json` and is reported as running normally; a separate smoke launched from `/tmp` did not use that workspace MCP configuration. Independent QA and Reviewer handoffs remain unavailable in this host context.

## Clarification — keep the canonical skill body structure in nested subskills

The user clarified that each `workflows/<id>.md` is a subdomain expertise subskill and must follow the same canonical body structure as a skill: `<critical_rules>`, `<general_rules>`, `<risk_assessment>`, `<rules>`, and `<workflow>`. This is a content-shape requirement only. A subskill remains nested inside its domain package, uses workflow metadata, and is not a peer Agent Skill package or a separately routed global skill. The parent domain remains the first-stage router; the selected subskill is loaded as the second disclosure stage. See architecture r6 and plan r10.
