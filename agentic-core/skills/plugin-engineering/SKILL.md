---
name: plugin-engineering
description: "WHAT: Author, validate, and evolve packaged agent expertise and its plugin integrations. USE FOR: agent/skill/hook authoring, MCP server implementation guidance, Expertise Pack creation or updates, and skill-package evaluation. DO NOT USE FOR: product implementation, plugin installation/deployment, or general operational configuration."
user-invocable: true
metadata:
  creation-date: 2026-09-26
  creator: Doodooms
license: MIT
---

<critical_rules>

- MUST keep skills as packaged workflows, MCP tools as deterministic capabilities, and each generated target derived from its canonical source.
- MUST use exact published tool names and preserve role, risk, rejection, and validation contracts.

</critical_rules>

<general_rules>

- SHOULD add only the smallest coherent package surface and expose specialized procedures only when their admission matches.

</general_rules>

<risk_assessment>

Consume the Orchestrator-assigned `risk_level`; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases risk. Risk scales package validation depth, not authority or approvals.

</risk_assessment>

<rules>

- This domain owns reusable agent, skill, hook, and Expertise Pack authoring plus MCP server method guidance; Implementer owns MCP server code and `operations` owns host configuration, installation, and deployment.
- Each immediate workflow MUST contain its actual procedure; references are supporting knowledge only. DO route once from this domain skill to the narrowest matching workflow; never expose one MCP tool per skill.

</rules>

<workflow>

## Step 1 - Select a package procedure.

1. DO consume the assigned `risk_level`, then choose only a matching immediate workflow:
   - [agent-authoring](./workflows/agent-authoring.md) or [agent-validation](./workflows/agent-validation.md) for agent definitions.
   - [skill-authoring](./workflows/skill-authoring.md) or [skill-maintenance](./workflows/skill-maintenance.md) for skill packages and internal workflows.
   - [create-mcp](./workflows/create-mcp.md) for new or existing MCP server implementation and repair. New standalone MCP servers use Rust with the official `rmcp` SDK; the workflow documents the narrow architectural exception. MCP server source belongs to Implementer; host configuration and deployment belong to `operations`.
   - [plugin-creation](./workflows/plugin-creation.md) or [plugin-update](./workflows/plugin-update.md) for Expertise Packs.
   - [create-hook](./workflows/create-hook.md) for deterministic lifecycle hooks.
   - [optimize-skill](./workflows/optimize-skill.md) only when an explicit skill-optimization or evaluation task requires it.

## Step 2 - Apply the selected package workflow.

1. Follow the selected workflow directly; load only the references, assets, or scripts needed at their point of use.

## Step 3 - Validate and return.

1. Report source/target paths, exact validation and build results, changed files, risks, and any unverified runtime behavior; do not install or activate the plugin unless authorized.

</workflow>
