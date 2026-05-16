# Primitive Selection Matrix

Purpose

- Helps decide whether a request should become a custom agent or should route to a different customization primitive instead.
- Use it only when the request is still ambiguous after the Step 0 confirmation matrix and the local agent surface.
- Do **NOT** use it to repeat the same yes or no routing boundary already covered by Step 0.

Decision matrix

```text
| Primitive        | Use When                                                | Do Not Use When                                      |
|-----------------|---------------------------------------------------------|------------------------------------------------------|
| Agent           | You need a specialized persona with explicit tools, routing, or optional subagents. | You only need a reusable procedure with no persona boundary. |
| Skill           | You need a reusable multi-step workflow with support files or validation steps. | You need a specialist persona or tool boundary instead. |
| Prompt          | You need one focused reusable task or input pattern.    | You need deterministic orchestration or validation.  |
| MCP Server      | You need tools, resources, or prompts backed by an external system or protocol service. | Local repository guidance is enough.                 |
| Hook            | You need deterministic lifecycle enforcement such as blocking, formatting, or automatic checks. | Guidance alone is sufficient and shell enforcement is unnecessary. |
| File Instruction| You need persistent guidance scoped to specific files or paths. | The behavior is task-shaped rather than file-shaped. |
```

Selection notes

- Prefer the narrowest primitive that satisfies the request.
- If the request is mainly about who should act and which tools they may use, prefer an agent.
- If the request is mainly about how to execute a repeatable workflow, prefer a skill.
- If the matrix points away from agents, route to the corresponding canonical workflow such as `create-skill`, `create-prompt`, or `create-mcp` instead of stretching `create-agent`.