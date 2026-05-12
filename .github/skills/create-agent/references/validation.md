# Agent validation guide

Purpose

- Explains what `scripts/validate_agent.py` checks and how to fix its output.
- Use [agent-template.md](../assets/agent-template.md) as the canonical starting point when validation points to structural problems.

When to use this file

- Read it after generated `.agent.md` validation fails.
- In this repository, run the validator with `./.venv/bin/python .github/skills/create-agent/scripts/validate_agent.py --agent-file <agent_file>`.
- If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root before validating.

Automatic checks

- The file ends with `.agent.md`.
- YAML frontmatter parses and the body is not empty.
- `description` exists and is a non-empty string.
- `tools`, `agents`, `handoffs`, `hooks`, and `model` use the expected shapes.
- `agents:` requires the `agent` tool.
- Deprecated `infer` is reported as a warning.
- Descriptions that omit `Use when:` are reported as a warning because routing becomes weaker.
- Duplicate tools and overly broad tool lists are reported as warnings.
- Files outside `.github/agents/` are reported as warnings because this repository defaults to workspace agents there.

Fix patterns

- Missing frontmatter -> add the YAML header before the body.
- Empty `description` -> write a concise sentence that states what the agent does and when it should be chosen.
- `agents:` without `agent` in `tools` -> add `agent` to `tools` or remove `agents:`.
- Deprecated `infer` -> replace it with `user-invocable` and `disable-model-invocation`.
- Warning about routing text -> add `Use when:` phrases to `description`.
- Warning about broad tools -> remove tools the agent does not need.
- Warning about file location -> move the file to `.github/agents/` unless a different scope was explicitly requested.

Status codes

- ERROR: must fix before the agent is ready.
- WARNING: quality or routing issue that should usually be corrected.