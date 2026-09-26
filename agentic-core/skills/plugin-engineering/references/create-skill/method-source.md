---
name: create-skill
description: "WHAT: Create, repair, review, or validate a self-contained skill package. USE FOR: skill admission, workflow design, templates, references, assets, scripts, and package validation. DO NOT USE FOR: agents, prompts, MCP servers, benchmark optimization, or product implementation."
user-invocable: true
context: fork
compatibility: vscode 1.119.0+, github-copilot 1.119.0+
metadata:
  creation-date: 2026-09-22
  creator: Doodooms
license: MIT
---

<definitions>

- **skill**: A discoverable capability and method family; it is not a persona or deterministic tool.
- **workflow**: An immediate child procedure selected inside one skill; workflows are not globally registered skills.
- **subskill**: A selected package-local specialization declared by a workflow, stored under `references/[subskill-id]/` and not globally discoverable.
- **support file**: Point-of-need reference, reusable asset, or package-local script consumed by a workflow.

</definitions>

<critical_rules>

- MUST preserve the canonical scaffold and exact rejection contract.
- MUST treat skills as packaged workflows, not deterministic tools; use native skill invocation and MUST NOT expose per-skill MCP tools.
- MUST keep each package self-contained. Scripts MUST run without workspace imports; composition MUST pass bounded inputs, explicit return fields, validation, and an exact parent resume point.
- MUST NOT redesign repository architecture while authoring a domain skill.

</critical_rules>

<general_rules>

- `SKILL.md` SHOULD own shared expertise and admission; immediate `workflows/[id].md` files SHOULD own distinct same-domain procedures; references, assets, and scripts support selected steps.
- Workflow IDs MUST be unique lowercase hyphenated names matching immediate Markdown filenames; workflows MUST NOT route to each other or create cycles.
- A workflow MAY declare meaningful `subskills` as Markdown files under `references/[subskill-id]/`; load only those selected by the current procedure, and MUST NOT treat them as separately installed skills.
- Use `MUST` / `MUST NOT` for invariants, `SHOULD` / `SHOULD NOT` for preferences, `MAY` for optional behavior, and `DO` / `DO NOT` for local actions.
- SHOULD route from the parent, load only matching workflows and subskills, and stop disclosure at skill → workflow → subskill/reference/asset/tool.
- Measure `SKILL.md`, selected workflows, selected subskills, and available tool schemas; generic references MUST NOT count. Around 1,000 tokens triggers a disclosure review; above 1,500 requires restructuring or a concise justification. Never drop required behavior to meet a target.
- Keep validation proportional to risk; load support at point of need. Multi-phase work SHOULD use native todos only for meaningful phases and real dependencies.

</general_rules>

<risk_assessment>

Assess impact/blast radius, reversibility, security or data exposure, external contracts, and uncertainty. Use the highest applicable level: **L0** isolated/reversible; **L1** bounded to one component; **L2** cross-component, contract, migration, or material integration; **L3** high-impact, sensitive, destructive, or hard to reverse. Inherit the Orchestrator's level; MUST NOT downgrade it. Scale evidence and validation only, never authorization, authority boundaries, critical rules, or approval gates.

</risk_assessment>

<rules>

- Keep one source of truth per concept and add only support files that reduce repeated context or enable a useful reusable payload or check.
- Multi-phase authoring SHOULD use one todo per meaningful phase; todos are not durable task history.

</rules>

<admission>

## ACCEPT

- Create a new skill package.
- Repair, restructure, normalize, review, or validate an existing skill.
- Update skill templates, references, scripts, workflow metadata, or frontmatter.

## REJECT

- Create or edit an agent → `plugin-engineering`'s `agent-authoring` workflow.
- Create or edit the direct-user Orchestrator → `plugin-engineering`'s `agent-authoring` workflow; its no-Step-0 exception does not make it skill work.
- Create or edit a reusable prompt → `orchestrate` for lightweight routing.
- Implement or repair MCP server code → Implementer with `plugin-engineering`'s `create-mcp` workflow.
- Measure a skill context projection → `context-management`'s `token-optimization` workflow.
- Optimize an existing skill or design its evaluation benchmark → `plugin-engineering`'s `optimize-skill` workflow.
- Define always-on repository guidance → repository instructions.
- Implement general product behavior → the relevant implementation workflow.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"create-skill","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<workflow>

## Step 1 - Select the package procedure.

1. Apply the risk assessment to package impact, reversibility, security/data exposure, contracts, and uncertainty; inherit the Orchestrator's level and never downgrade it. Choose [authoring](./workflows/authoring.md) for a new package or [maintenance](./workflows/maintenance.md) for an existing one, including review- or validate-only requests.

## Step 2 - Apply the selected procedure.

1. Load only that workflow and the assets, references, or scripts needed at its current step; DO NOT scaffold over existing work.

## Step 3 - Validate and return.

1. Use #tool:execute for the selected procedure's package validation and the native skill mechanism to load `context-management`, selecting its `token-optimization` workflow for the expected projection; return the package, evidence, estimate and estimator, excluded references, review status, unresolved decisions, and risks.

</workflow>
