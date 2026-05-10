---
name: "graphify"
description: "Entry prompt: run the graphify skill to build, update, or query the workspace knowledge graph without duplicating graphify workflow logic in the prompt."
argument-hint: "[path] | query <question> | path <node-a> <node-b> | explain <node>"
agent: "agent"
model: "GPT-5.4 (copilot)"
---
Use the [graphify skill](../skills/graphify/SKILL.md) as the single source of truth for build, update, query, and reporting behavior.

Pass the prompt argument through unchanged.

- If no argument is provided, treat it as `.`.
- If the argument starts with `query `, `path `, or `explain `, keep that mode intact.
- Do not re-implement graphify workflow in this prompt.