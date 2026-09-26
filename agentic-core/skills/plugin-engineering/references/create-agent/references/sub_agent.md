# Subagent quick reference

Use this file only when delegation, invocation mode, nesting, or model inheritance is still unclear after [latest-docs](./latest-docs.md).

## Invocation control

```text
+-----------------------------------------------+-------------------------------------------------------+-----------------------------------------------+
| Need                                          | Frontmatter choice                                    | Result                                        |
+-----------------------------------------------+-------------------------------------------------------+-----------------------------------------------+
| Visible in picker and callable as subagent    | omit both flags                                       | default general agent                         |
| Hidden from picker, callable as subagent      | `user-invocable: false`                               | helper agent                                  |
| Visible in picker, blocked from subagents     | `disable-model-invocation: true`                      | user-only agent                               |
| Hidden from picker and blocked from subagents | `user-invocable: false` + `disable-model-invocation: true` | internal-only agent                    |
+-----------------------------------------------+-------------------------------------------------------+-----------------------------------------------+
```

## Delegation scope

```text
+---------------------------------------+------------------------------------------------------+-----------------------------------------------------------+
| Situation                             | Write                                                | Notes                                                     |
+---------------------------------------+------------------------------------------------------+-----------------------------------------------------------+
| No delegation                         | omit `agents:` and remove `agent`                    | narrowest local default                                   |
| Delegate to named helpers             | add `agent` and explicit `agents:` allowlist         | verify each named agent already exists                    |
| Broad delegation is intentional       | add `agent` and `agents: *`                          | use only with explicit justification                      |
| Block all subagents while keeping tool | `agents: []`                                        | host supports this, but local drafts usually omit both    |
+---------------------------------------+------------------------------------------------------+-----------------------------------------------------------+
```

- Explicitly listing an agent in `agents:` can override that target agent's `disable-model-invocation: true` guard.
- MUST NOT list the current agent in `agents:`. Recursive self-delegation is outside this workspace's canonical agent contract.

## Model precedence

```text
+----------+--------------------------------------------------------------+
| Priority | Source                                                       |
+----------+--------------------------------------------------------------+
| 1        | explicit model passed at subagent invocation                 |
| 2        | subagent frontmatter `model`                                 |
| 3        | parent conversation model                                    |
+----------+--------------------------------------------------------------+
```

## Nested delegation

```text
+----------------------+----------------------------------------------------------------+
| Surface              | Rule                                                           |
+----------------------+----------------------------------------------------------------+
| Default              | subagents do not spawn subagents                               |
| Opt-in               | a host setting enables nesting                                 |
| Depth                | the host caps recursion depth                                  |
| Self-reference       | MUST NOT list self in `agents:`                              |
+----------------------+----------------------------------------------------------------+
```

## High-value patterns

```text
+----------------------+---------------------------------------------------------------+
| Pattern              | Use when                                                      |
+----------------------+---------------------------------------------------------------+
| Coordinator/worker   | one agent routes between narrow specialists                   |
| Parallel review      | independent review lenses should not contaminate each other   |
| Isolated research    | exploration would otherwise pollute the main context          |
+----------------------+---------------------------------------------------------------+
```