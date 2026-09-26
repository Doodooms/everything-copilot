---
name: create-plugin
description: "WHAT: Create, update, validate, and compile canonical Expertise Packs into Agent Plugin targets. USE FOR: packaging reusable skills, optional agent contributions, capabilities, and projected MCP integrations for portable, Copilot, or Codex. DO NOT USE FOR: standalone skills, agents, MCP implementation, or plugin runtime changes."
user-invocable: true
metadata:
  creation-date: 2026-09-25
  creator: Doodooms
license: MIT
---

<definitions>

- **Expertise Pack**: Canonical source for related capabilities, skills, optional agent contributions, dependencies, and MCP projections.
- **projection**: Explicit assignment of skills, agents, and MCP servers to a pack or core agent.
- **target**: A portable, Copilot, or Codex build derived from the same validated pack source.

</definitions>

<rules>

- `expertise/packs/[pack-id]/pack.yaml` is canonical; MUST NOT hand-edit generated `dist/` output or duplicate the parser/compiler.
- Keep contributions minimal and capability-scoped. MUST use existing `expertise scaffold`, `validate`, `test`, and `build` commands.
- Keep workflows in skills and deterministic operations in MCP tools. MUST NOT turn a workflow skill into an MCP tool or expose a one-tool-per-skill endpoint.
- Project only needed capabilities and servers. For Copilot, MCP availability does not amend an agent's `tools` allowlist; both declarations MUST agree.
- MCP catalogs MUST contain exact published `tools/list` names. An agent may use a pack tool only when its server is declared and projected to that agent.
- Pin runnable MCP versions where possible and include no secrets. Codex agents inherit the plugin's MCP configuration; MUST disclose that tools are not isolated per agent and Codex agent TOML exports are sidecars, not automatically installed agents.
- Any composed authoring handoff MUST carry bounded inputs, required return fields, validation, and an exact parent resume point. Internal workflow IDs are package procedures, not standalone skills or tools; validate each result before resuming.
- Build every declared target before reporting success. MUST NOT install, activate, stage, commit, branch, or open a PR unless explicitly requested.
- Multi-phase authoring SHOULD use one native todo per top-level phase, with real dependencies only.

</rules>

<admission>

## ACCEPT

- Create or update an Expertise Pack from a capability-level request.
- Add and validate required skills, agent contributions, dependencies, or MCP projections inside a pack.
- Compile a validated pack for its declared portable, Copilot, or Codex targets.

## REJECT

- Create or edit a standalone skill → `plugin-engineering`'s `skill-authoring` workflow.
- Create or edit a standalone agent → `plugin-engineering`'s `agent-authoring` workflow.
- Implement or repair MCP server code → Implementer with `plugin-engineering`'s `create-mcp` workflow.
- Install, activate, or manage the runtime Active Set → `operations`' `install-agent-plugin` workflow.
- Implement general product behavior → the relevant implementation workflow.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"create-plugin","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<workflow>

## Step 1 - Select the pack procedure.

1. Choose [create](./workflows/create.md) for a new pack; choose [update](./workflows/update.md) for an existing pack.

## Step 2 - Compose the approved capability.

1. Follow only the selected procedure. Keep the capability, agent ownership, tool surface, and target projections bounded to the request.

## Step 3 - Validate, build, and return.

1. Use #tool:execute from the repository root to run `PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python -m expertise validate [pack-id]`, then `PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python -m expertise test [pack-id]`.
2. Use #tool:execute to run `PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python -m expertise build [pack-id] --target [target]` for each declared target.
3. Inspect diagnostics and output paths; report pack ID/version, source, declared targets, exact build outputs, validation results, changed files, unresolved risks, and next action.

</workflow>
