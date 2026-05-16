# Agent Validation Guide

Purpose

- Explains what `scripts/validate_agent.py` checks and how to fix its output.
- The validator and its lint core both live in this skill's own `scripts/` directory.
- Use [agent-template.md](../assets/agent-template.md) for the canonical self-contained agent example.

When to use this file

- Read it after validation fails or when you need to understand what the validator enforces.
- In this repository, run the validator with `./.venv/bin/python .github/skills/create-agent/scripts/validate_agent.py --agent-file <agent_file>`.
- If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root before running the validator.

Automatic checks

- YAML frontmatter parses and the body is not empty.
- `description` warnings cover missing `WHAT:`, `USE FOR:`, or `DO NOT USE FOR:` clauses.
- Tool names are checked against the workspace agent-facing tool catalog embedded in this skill's own lint core.
- Wrong-layer raw tool names such as `run_in_terminal` or `vscode_askQuestions` are rejected with local alias suggestions.
- `agents:` must be a valid list, must include only known workspace agents, and must be paired with the `agent` tool.
- Broad `agent` usage without an explicit `agents:` allowlist is warned.
- The canonical wrapped agent shape keeps `<definitions>`, `<workflow>`, `## Step 0 - **CONFIRMATION**`, `## Role`, `<rules>`, `## Responsibilities`, `## Constraints`, `## Output Contract`, `## Step 1 - ...`, `## Step 2 - ...`, and `## Step 3 - ...` in order.
- Canonical self-contained Step 0 agents embed `### USE FOR` and `### DO **NOT** USE FOR` inside the `.agent.md` file.
- Canonical agents keep a refusal payload with `status: refused`, `agent`, `reason`, and `suggested_alternative`.
- Legacy routing-file agents are still recognized, but they warn and must keep valid sibling routing files if they still use that older mode.

What still needs the final checklist

- Whether the role is narrow enough to justify an agent instead of a skill, prompt, or other primitive.
- Whether the example prompt in the final summary truly matches the `description` and Step 0 routing surface.
- Whether invocation mode is deliberate even when the validator would allow omitted fields.

Use [final-checklist.md](./final-checklist.md) after script validation to catch those remaining judgment calls.

Fix patterns

- Missing embedded routing sections -> add `### USE FOR` and `### DO **NOT** USE FOR` under Step 0.
- Old sibling routing references in a new draft -> move the routing bullets into Step 0 and remove the file reads.
- Missing refusal JSON -> add the structured refusal payload in Step 0 or `## Output Contract`.
- Wrong-layer tool name -> replace it with the workspace alias or namespaced tool the validator suggests.
- Broad delegation -> either remove `agent` or add an explicit `agents:` allowlist.
- Unknown allowed subagent -> fix the agent name or create that agent first.

Fast fix map

```text
+--------------------------------------+---------------------------------------------+----------------------------------------------+
| Validator output                      | First place to look                         | Typical repair                               |
+--------------------------------------+---------------------------------------------+----------------------------------------------+
| Missing wrapped sections              | [agent-template](../assets/agent-template.md) | Restore the canonical body shape           |
| Missing embedded routing              | Step 0 in the `.agent.md` file               | Add `### USE FOR` and `### DO **NOT** USE FOR` |
| Missing refusal JSON                  | Step 0 or `## Output Contract`               | Add the structured refusal payload           |
| Wrong-layer tool name                 | Frontmatter `tools`                          | Replace it with the suggested workspace alias |
| Unknown allowed subagent              | Frontmatter `agents:`                        | Fix the name or create that agent first      |
| Broad `agent` warning                 | Frontmatter `tools` and `agents:`            | Remove `agent` or add an explicit allowlist  |
+--------------------------------------+---------------------------------------------+----------------------------------------------+
```

Status codes

- ERROR: must fix before publishing the agent.
- WARNING: the agent will run, but the contract is still broader, older, or less precise than the workspace standard.