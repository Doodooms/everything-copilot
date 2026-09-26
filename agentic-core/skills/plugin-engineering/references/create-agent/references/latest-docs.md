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
- Keep global selection concise and description-first; use the canonical body `<routing>` block for local ownership only.
- Keep tools minimal and use workspace agent-facing tool names that the local lint core recognizes.
- Skills remain packaged workflows: core packages live in an installed Agent Plugin's `skills/`, while project-specific workspace packages live under `.github/skills/`. They are not converted into per-skill MCP tools. When an agent needs to load these methods, use the host's native `skill` tool and allowlist that tool in the agent's `tools`.
- List a skill's package name and admission context in `<agent-skills>`. The agent follows its workflow in the current role and then resumes the parent workflow; a skill is not a deterministic tool call or a separate agent.
- Prefer `target: vscode` unless the request explicitly targets another Copilot surface.
- Keep support references in the create-agent skill at point of need; do not front-load them into the agent being authored.
- The current official custom-agent frontmatter property table does not define a top-level `github` key. Authors MUST NOT add an undocumented `github:` block; use the selected harness's supported GitHub tools/MCP configuration and explicit `tools` allowlist instead. Recheck the official schema before relying on a future addition.

## If you still need more detail

- [custom_agent.md](./custom_agent.md) for frontmatter fields, placement, handoffs, and hooks.
- [sub_agent.md](./sub_agent.md) for delegation, `agents:`, nested subagents, and subagent invocation behavior.