# Confirmation matrix

Read this file in Step 0 only. It is intentionally narrow so agent-work confirmation stays cheap in tokens.

```text
+---------------------------------------------------------+-----+------------------------------------------------+
| Request shape                                           | Use | Route instead                                   |
+---------------------------------------------------------+-----+------------------------------------------------+
| Create a new `.agent.md` file                           | Yes | N/A                                            |
| Repair or normalize an existing custom agent            | Yes | N/A                                            |
| Update the agent template or agent validation rules     | Yes | N/A                                            |
| Convert an implicit chat persona into a workspace agent | Yes | N/A                                            |
| Create or repair a skill                                | No  | create-skill                                   |
| Create or repair a prompt                               | No  | create-prompt                                  |
| Create or repair an MCP server                          | No  | create-mcp                                     |
| General coding or debugging work unrelated to agents    | No  | Do the implementation or use a domain skill    |
+---------------------------------------------------------+-----+------------------------------------------------+
```

If the answer is still unclear after this file, use [primitive-selection](./primitive-selection.md) only for the remaining agent-vs-other-primitive choice.