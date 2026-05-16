# Confirmation matrix

Read this file in Step 0 only. It is intentionally narrow so confirmation stays cheap in tokens.

```text
+-----------------------------------------------+-----+-----------------------------------------------+
| Request shape                                 | Use | Route instead                                  |
+-----------------------------------------------+-----+-----------------------------------------------+
| Create a new skill package                    | Yes | N/A                                           |
| Repair or normalize an existing skill         | Yes | N/A                                           |
| Remove duplicated skill guidance in a skill   | Yes | N/A                                           |
| Tighten point-of-need loading in a skill      | Yes | N/A                                           |
| Update skill templates or skill validation    | Yes | N/A                                           |
| Create or edit a custom agent                 | No  | create-agent                                  |
| Create or edit a reusable prompt              | No  | create-prompt                                 |
| Create or edit an MCP server                  | No  | create-mcp                                    |
| General coding or debugging work              | No  | Do the implementation or use a domain skill   |
| Repo policy with no repeatable skill workflow | No  | Instructions or hooks                         |
+-----------------------------------------------+-----+-----------------------------------------------+
```

If the answer is still unclear after this file, use [decision-matrices](./decision-matrices.md).