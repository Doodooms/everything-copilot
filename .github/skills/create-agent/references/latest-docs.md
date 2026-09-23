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
- Agent discovery text uses `WHAT:`, `INVOKE FOR:`, and `DO NOT INVOKE FOR:` in this repository.
- Keep routing concise and description-first. Add body-level routing only when the role needs disambiguation beyond `description`.
- Keep tools minimal and use workspace agent-facing tool names that the local lint core recognizes.
- Prefer `target: vscode` unless the request explicitly targets another Copilot surface.
- Keep support references in the create-agent skill at point of need; do not front-load them into the agent being authored.

## If you still need more detail

- [custom_agent.md](./custom_agent.md) for frontmatter fields, placement, handoffs, and hooks.
- [sub_agent.md](./sub_agent.md) for delegation, `agents:`, nested subagents, and subagent invocation behavior.