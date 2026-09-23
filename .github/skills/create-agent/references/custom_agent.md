# Custom agent quick reference

Use this file only when [latest-docs](./latest-docs.md) still leaves a frontmatter, placement, or host-behavior ambiguity.

## Placement

```text
+-----------+----------------------+--------------------------------------+
| Scope     | Default path         | Use when                             |
+-----------+----------------------+--------------------------------------+
| Workspace | `.github/agents/`    | the repo should share the agent      |
| User      | `~/.copilot/agents/` | the agent is personal and cross-repo |
| Claude    | `.claude/agents/`    | Claude-format compatibility matters  |
+-----------+----------------------+--------------------------------------+
```

## Frontmatter fields

```text
+----------------------------+----------------------------------------------+----------------------------------------------+
| Field                      | Keep when                                    | Notes                                        |
+----------------------------+----------------------------------------------+----------------------------------------------+
| `name`                     | the display name must differ from file stem  | otherwise the file name is enough            |
| `description`              | always                                       | local standard: `WHAT:` + `INVOKE FOR:` + `DO NOT INVOKE FOR:` |
| `tools`                    | always deliberate                            | unavailable tools are ignored by the host    |
| `agents`                   | the agent delegates                          | requires `agent` in `tools`                  |
| `target`                   | host must be explicit                        | local default is `vscode`                    |
| `user-invocable`           | hide from the picker                         | does not block subagent use by itself        |
| `disable-model-invocation` | block subagent use                           | explicit allowlists can still override it    |
| `argument-hint`            | a short picker hint reduces bad prompts      | omit when redundant                          |
| `model`                    | the role genuinely needs a specific model    | otherwise inherit the active model           |
| `handoffs`                 | the UI should offer a next-agent button      | not a substitute for the output contract     |
| `hooks`                    | an agent-scoped lifecycle hook is required   | preview surface                              |
| `mcp-servers`              | target is `github-copilot`                   | not used for local `vscode` agents           |
| `infer`                    | never                                        | deprecated                                   |
+----------------------------+----------------------------------------------+----------------------------------------------+
```

## Body facts

```text
+----------------------+---------------------------------------------------------------+
| Surface              | Rule                                                          |
+----------------------+---------------------------------------------------------------+
| Body format          | Markdown instructions loaded when the agent is selected       |
| File references      | Use markdown links for optional file reads                    |
| Tool references      | `#tool:` is valid inside `.agent.md`                          |
| Missing tools        | Host ignores unavailable tools                                |
| New local agents     | Keep routing in `description`; add body guidance only when needed |
+----------------------+---------------------------------------------------------------+
```

## Claude format

```text
+-----------------------+------------------------------------------------------------+
| Surface               | Difference                                                 |
+-----------------------+------------------------------------------------------------+
| `.github/*.agent.md`  | YAML arrays for `tools`, VS Code frontmatter              |
| `.claude/agents/*.md` | plain `.md`, comma-separated `tools` and `disallowedTools` |
+-----------------------+------------------------------------------------------------+
```