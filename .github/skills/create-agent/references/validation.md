# Agent validation guide

## Purpose

- Explains what `scripts/validate_agent.py` checks and how to fix its output.
- Use [agent-template.md](../assets/agent-template.md) as the canonical starting point when validation points to structural problems.

## When to use this file

- Read it after generated `.agent.md` validation fails.
- In this repository, run the validator with `./.venv/bin/python .github/skills/create-agent/scripts/validate_agent.py --agent-file <agent_file>`.
- If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root before validating.

## Automatic checks

- The file ends with `.agent.md`.
- YAML frontmatter parses and the body is not empty.
- `description` exists and is a non-empty string.
- `description` is checked for both `What:` and `Use when:` guidance because routing weakens when either part is missing.
- The body contains the core agent sections `# Role`, `## Responsibilities`, `## Workflow` or `## Approach`, `## Constraints`, and `## Output Contract` in canonical order.
- `tools` are checked against the workspace tool catalog, with suggestions for wrong-layer names such as `vscode_askQuestions`.
- `tools`, `agents`, `handoffs`, `hooks`, and `model` use the expected shapes.
- `agents:` requires the `agent` tool.
- `agents:` entries must not reference the current agent and must resolve to existing workspace agent names unless `*` is used intentionally.
- `handoffs[*].agent` targets must resolve to existing workspace agent names and must not point back to the current agent.
- `agent` in `tools` without an `agents:` allowlist is reported as a warning because it grants broad delegation.
- Deprecated `infer` is reported as a warning.
- Descriptions that omit `Use when:` are reported as a warning because routing becomes weaker.
- Duplicate tools and overly broad tool lists are reported as warnings.
- Files outside `.github/agents/` are reported as warnings because this repository defaults to workspace agents there.

## Fix patterns

- Missing frontmatter -> add the YAML header before the body.
- Empty `description` -> write a concise sentence that states what the agent does and when it should be chosen.
- Missing `What:` or `Use when:` -> rewrite `description` so it clearly states the job and the routing triggers.
- Missing core sections -> restore the agent-specific contract from [agent-template.md](../assets/agent-template.md): role, responsibilities, workflow or approach, constraints, and output contract.
- Workflow sections out of order -> restore the canonical agent section order from [agent-template.md](../assets/agent-template.md) instead of improvising a new layout.
- Unknown or wrong-layer tool name -> replace it with a workspace agent-facing tool name accepted by the validator.
- `agent` without `agents:` -> add an explicit allowlist or remove `agent` from `tools`.
- `agents:` without `agent` in `tools` -> add `agent` to `tools` or remove `agents:`.
- Unknown subagent or handoff target -> point it to an existing `.github/agents/<slug>.agent.md` name or remove the reference.
- Self-referencing `agents:` or `handoffs` target -> remove the self-reference and route to another existing agent instead.
- Deprecated `infer` -> replace it with `user-invocable` and `disable-model-invocation`.
- Warning about routing text -> add `Use when:` phrases to `description`.
- Warning about broad tools -> remove tools the agent does not need.
- Warning about file location -> move the file to `.github/agents/` unless a different scope was explicitly requested.

## Status codes

- **ERROR**: must fix before the agent is ready.
- **WARNING**: quality or routing issue that should usually be corrected.