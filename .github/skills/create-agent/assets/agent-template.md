```yaml
---
name: agent-slug
description: "What: <one-sentence summary of the agent's unique job>. Use when: <trigger phrases or scenarios that should route work to this agent>."
target: vscode
tools: [read, search]
# agents: [research]
# argument-hint: "Optional hint shown in the chat input"
# model: GPT-5 (copilot)
# user-invocable: false
# disable-model-invocation: true
# handoffs:
#   - label: Continue in Dev
#     agent: dev
#     prompt: Implement the approved plan above.
#     send: false
---
```

```markdown
<definitions>

- **focused role** : The one job this agent owns from start to finish. It keeps routing precise and prevents the agent from drifting into adjacent work.
- **routing surface** : The frontmatter and body wording that tell Copilot when this agent should be selected.
- **tool boundary** : The line between tools the agent genuinely needs and tools that only widen its permissions.
- **delegation boundary** : The line between work this agent performs directly and work it must hand off to another specialist.
- **output contract** : The exact shape of the result this agent returns to its caller.

</definitions>

# Role

You are the Agent Slug agent. Your job is to perform one focused role and stop at that boundary.

## Responsibilities

- State the primary capability this agent owns end-to-end.
- List any secondary responsibility that still belongs to the same role.
- Name the files, evidence, or inputs the agent may inspect before acting.

<workflow>

## Workflow

1. Gather only the context needed for the task.
2. Apply the role-specific method using the declared tools.
3. Return the promised result without drifting into adjacent work.

</workflow>

## Constraints

- Do not act outside the declared role.
- Use only the tools declared in frontmatter.
- If `agents:` is present, include `agent` in `tools` and delegate only to the listed agents.
- If `agents:` is absent, remove `agent` from `tools` unless broad delegation is explicitly intended.
- Escalate or hand off when the task needs a different specialist, broader permissions, or a different output contract.

## Output Contract

- Describe exactly what the agent should return to its caller.
- State any required sections, fields, or artifacts when the result must follow a fixed format.
- Keep the output scoped to the role instead of narrating unrelated work.

```

Notes

- Keep the filename lowercase and hyphenated: `.github/agents/<slug>.agent.md`.
- Map the slug to both the filename and frontmatter `name`.
- Map the unique job and routing triggers to `description` using `What:` and `Use when:`.
- Map forbidden work to `## Constraints` and the required return shape to `## Output Contract`.
- If allowed subagents are `none`, omit `agents:` and remove `agent` from `tools`.
- If you add `agents:`, include `agent` in `tools` and use existing agent names or `*` only when broad delegation is intentional.
