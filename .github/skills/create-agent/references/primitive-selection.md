# Primitive selection matrix

Use this file only when the agent-vs-other-primitive choice remains unresolved.

```text
+------------------+-----------------------------------------------+----------------------------------------------+
| Primitive        | Choose when                                   | Route away when                              |
+------------------+-----------------------------------------------+----------------------------------------------+
| Agent            | Persona, tool boundary, or delegation matters | A plain repeatable workflow is enough        |
| Skill            | Repeatable workflow with support files        | You need a specialist persona                |
| Prompt           | One focused reusable task or input pattern    | You need validation or orchestration         |
| MCP server       | New tools or resources must be executable     | Repo-local guidance is enough                |
| Hook             | Policy must run automatically                 | Guidance alone is enough                     |
| File instruction | Rule is path-scoped and always-on             | The behavior is task-shaped                  |
+------------------+-----------------------------------------------+----------------------------------------------+
```

- Prefer the narrowest primitive that satisfies the request.
- If the matrix points away from agents, route to the matching create surface instead of stretching `create-agent`.