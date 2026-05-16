# Curated VS Code custom-agent notes

Use this file only to confirm host behavior that still matters for local agent authoring.

## Upstream facts that still matter

- Workspace custom agents live under `.github/agents/`.
- Frontmatter discovery is driven mainly by `name`, `description`, `tools`, and optional `agents:`.
- `user-invocable: false` hides an agent from the picker but does **NOT** block subagent use by itself.
- `disable-model-invocation: true` blocks model or subagent invocation and should be used deliberately.
- Delegation requires `agent` in `tools`; precise repos should pair that with an explicit `agents:` allowlist.

## Local authoring rules in this repository

- Default to one self-contained `.agent.md` file at `.github/agents/<slug>.agent.md`.
- Embed Step 0 `### USE FOR` and `### DO **NOT** USE FOR` inside the agent file instead of splitting routing into sibling docs.
- Keep tools minimal and use workspace agent-facing tool names that the local lint core recognizes.
- Prefer `target: vscode` unless the request explicitly targets another Copilot surface.
- Keep support references in the create-agent skill at point of need; do not front-load them into the agent being authored.

## If you still need more detail

- [custom_agent.md](./custom_agent.md) for frontmatter fields, placement, and custom-agent behavior.
- [local_agents.md](./local_agents.md) for picker behavior and interactive VS Code expectations.
- [sub_agent.md](./sub_agent.md) for delegation, `agents:`, and nested subagent behavior.
- [agents.md](./agents.md) for higher-level terminology and product overview.