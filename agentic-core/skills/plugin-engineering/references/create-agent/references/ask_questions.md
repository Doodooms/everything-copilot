# askQuestions guidance

Use [ask_questions.json](../assets/ask_questions.json) only when the conversation does not already contain a usable agent contract.

## Ask only for missing fields

```text
+--------------------------------------+---------------------------------------------+
| If still unclear                     | Ask for                                     |
+--------------------------------------+---------------------------------------------+
| File target or naming                | Agent slug                                  |
| Job or routing scope                 | Focused role, routing triggers, exclusions  |
| Tool or refusal boundary             | Required tools, forbidden work              |
| Picker or delegation behavior        | Invocation mode, allowed subagents          |
| Return shape                         | Output contract                             |
+--------------------------------------+---------------------------------------------+
```

## Map each answer once

```text
+--------------------+---------------------------------------------------------------+
| Answer             | Write to                                                      |
+--------------------+---------------------------------------------------------------+
| Agent slug         | filename + frontmatter `name`                                 |
| Focused role       | `description` WHAT                                            |
| Routing triggers   | `description` INVOKE FOR                               |
| Routing exclusions | `description` DO NOT INVOKE FOR                        |
| Required tools     | frontmatter `tools`                                           |
| Forbidden work     | `## Constraints`                                              |
| Invocation mode    | `user-invocable` + `disable-model-invocation`                 |
| Allowed subagents  | `agents:` + `agent` tool only when delegation is real         |
| Output contract    | `## Output Contract`                                          |
+--------------------+---------------------------------------------------------------+
```

- Skip the questionnaire when the conversation already fixes the role, routing, tools, delegation boundary, and output contract.
- Ask about local ACCEPT/REJECT owners only when the conversation and existing role boundaries do not establish them.
- Load [delegation and invocation guidance](./delegation_and_invocation.md) only when picker visibility or subagent behavior is still unclear.