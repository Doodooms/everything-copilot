---
name: create-agent
description: "WHAT: Create, repair, review, or validate a custom VS Code `.agent.md` persona. INVOKE FOR: agent role boundaries, routing, tools, skill policy, delegation, invocation, workflow, or output contracts. DO NOT INVOKE FOR: skills, prompts, MCP servers, hooks, or product implementation."
user-invocable: false
context: fork
compatibility: vscode 1.119.0+, github-copilot 1.119.0+
metadata:
  creation-date: 2026-09-23
  creator: Doodooms
license: MIT
---

<definitions>

- **agent**: A self-contained `.agent.md` persona with a bounded role and runtime contract.
- **agent contract**: Frontmatter and body together define routing, tools, invocation, delegation, behavior, and output.
- **workflow**: A selected authoring or validation procedure inside this skill; it is not a runtime document for the generated agent.

</definitions>

<critical_rules>

- MUST keep runtime routing, rules, skill policy, and workflow in one `.agent.md` using the canonical block order.
- MUST NOT add Step 0, duplicate global routing, or refusal JSON; every local REJECT names the exact receiver.
- MUST use exact host/MCP tool names and native skill invocation; skills are workflows, not MCP tools. Only the canonical Orchestrator may use `github/*`.
- If `agents:` is present, MUST include `agent` and explicit known recipients; MUST NOT use wildcard recipients. Omit both when the persona does not delegate.
- MUST use `user-invocable` and `disable-model-invocation`; MUST NOT use deprecated `infer`.

</critical_rules>

<general_rules>

- SHOULD choose an agent for durable role ownership and a skill for reusable methods; default to `.github/agents/[slug].agent.md` unless `create-plugin` supplies an exact pack path.
- MUST place global selection in `description` and local admission in `<routing>`. The body order is optional meaningful `<definitions>`, `<routing>`, `<critical_rules>`, `<general_rules>`, `<risk_assessment>`, `<rules>` with Role / Responsibilities / Constraints / Output Contract, `<agent-skills>`, then a separate three-step `<workflow>`.
- Generated agents MUST use `MUST` / `MUST NOT` for invariants, `SHOULD` / `SHOULD NOT` for preferences, `MAY` for optional behavior, and `DO` / `DO NOT` only for local workflow actions.
- The agent resolves its own skill policy in Step 1: load matching `MUST` skills, consider matching `SHOULD` skills, and skip unmatched methods. Use exact package names.
- Keep tools minimal and tied to actions; use only MCP `server/tool` names declared by the pack and projected to the agent.
- Keep definitions optional and meaningful. Put detailed guidance in point-of-need support files without splitting the runtime contract or duplicating assurance procedures.

</general_rules>

<risk_assessment>

Assess impact/blast radius, reversibility, trust/data exposure, external contracts, and uncertainty. Use the highest applicable level: **L0** isolated/reversible; **L1** bounded to one component; **L2** cross-component/contract/migration; **L3** high-impact, sensitive, destructive, or hard to reverse. Use the Orchestrator's recorded level; specialists MUST NOT downgrade it and SHOULD report escalation evidence. Select only role-owned gates.

</risk_assessment>

<rules>

- Include a user-review pause only when a user-owned confirmation is required; keep validation proportional to risk.

</rules>

<admission>

## ACCEPT

- Create, repair, migrate, review, or validate a custom workspace `.agent.md`.
- Author a pack-owned `.agent.md` contribution from a bounded `create-plugin` handoff naming its exact output path.
- Update agent-specific templates, references, lint rules, or validation tests.

## REJECT

- Create or repair a skill → `plugin-engineering`'s `skill-authoring` workflow.
- Create or repair a reusable prompt → `orchestrator` for lightweight routing.
- Implement or repair MCP server code → Implementer with `plugin-engineering`'s `create-mcp` workflow.
- Create a hook or general product behavior → the corresponding authoring or implementation surface.

For rejected work, state the reason and route it to the matching surface; MUST NOT draft an agent as a substitute.

</admission>

<workflow>

## Step 1 - Select the procedure.

1. After ACCEPT, assess risk using the selected agent contract; choose [agent authoring](./workflows/authoring.md) for creating or repairing a persona, or [agent validation](./workflows/validation.md) for validate-only review.

## Step 2 - Apply the selected procedure.

1. Load only the matching workflow and the support files it calls for; DO NOT preload all templates, references, or checks.

## Step 3 - Return the outcome.

1. Use #tool:execute for the selected procedure's validation, then report the exact agent path, role, tools and delegates, representative routing example, result, and unresolved risks; MUST NOT claim user approval that was not given.

</workflow>
