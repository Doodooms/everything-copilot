# Delegation and invocation matrices

Use this file only when `agent`, `agents:`, `handoffs`, `user-invocable`, or `disable-model-invocation` are still unclear.

## Invocation mode

```text
+-----------------------------------------------+-------------------------------------------------------+-----------------------------------------------+
| Need                                          | Frontmatter choice                                    | Result                                        |
+-----------------------------------------------+-------------------------------------------------------+-----------------------------------------------+
| Visible in picker and usable as subagent      | Omit both flags                                       | Default general agent                         |
| Hidden from picker, callable as subagent      | `user-invocable: false`                               | Helper agent                                  |
| Visible in picker, blocked from subagent use  | `disable-model-invocation: true`                      | User-only agent                               |
| Hidden from picker and blocked from subagents | `user-invocable: false` + `disable-model-invocation: true` | Internal-only agent                    |
+-----------------------------------------------+-------------------------------------------------------+-----------------------------------------------+
```

## Delegation scope

```text
+-------------------------------------------+---------------------------------------------------+---------------------------------------------------+
| Situation                                 | Frontmatter and tools                             | Notes                                             |
+-------------------------------------------+---------------------------------------------------+---------------------------------------------------+
| No delegation                             | Omit `agents:` and remove `agent` from `tools`    | Default and narrowest shape                       |
| Delegation to named helpers               | Add `agent` and set explicit `agents:` allowlist  | Verify each named agent already exists            |
| Broad delegation is intentionally required| Add `agent` and set `agents: *`                   | Use only with explicit justification              |
+-------------------------------------------+---------------------------------------------------+---------------------------------------------------+
```

## Handoffs

```text
+-------------------------------------------+--------------------------------------+----------------------------------------------+
| Need                                      | Use                                  | Avoid when                                   |
+-------------------------------------------+--------------------------------------+----------------------------------------------+
| UI transition to a next specialist        | `handoffs`                           | A plain summary or refusal is enough         |
| No UI transition, just a scoped result    | Output contract only                 | A button would add noise                     |
+-------------------------------------------+--------------------------------------+----------------------------------------------+
```

- Never list the current agent in `agents:`.