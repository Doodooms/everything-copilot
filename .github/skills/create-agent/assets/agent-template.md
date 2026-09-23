# Agent Template

Use this as a scaffold for one self-contained `.agent.md`, not as a package template. Sibling files may guide authoring, but the generated agent must contain its own routing, workflow, refusal behavior, delegation boundary, invocation semantics, and output contract.

```yaml
---
name: agent-slug               # REQUIRED. Lowercase + hyphens only, 1-64 chars. MUST match the `.agent.md` filename stem exactly.
description: 'WHAT: <one-sentence summary of the unique job this agent owns>. INVOKE FOR: <trigger phrases or scenarios that should route work to this agent>. DO NOT INVOKE FOR: <nearby tasks or situations that this agent must refuse and route elsewhere>.' # REQUIRED. Primary routing surface. Keep all three clauses so the agent exposes both its scope and its refusal boundary before Step 0 runs.
target: vscode                 # REQUIRED for workspace agents in this repository.
tools: [read, search]          # REQUIRED. Keep this list minimal and use real workspace agent-facing tool names only. Confirm live availability via the chat "Configure Tools..." button or the copilot-tool-snapshot workflow before finalizing the list.
# agents: [research]           # OPTIONAL. Add only when this agent delegates. If present, include `agent` in `tools` and list explicit allowed subagents or `*` intentionally.
# argument-hint: "Optional hint shown in the chat input" # OPTIONAL. Use when a short picker hint improves invocation.
# model: GPT-5.6-luna (copilot)     # OPTIONAL. Pin only when the task genuinely requires a specific model.
# user-invocable: false        # OPTIONAL. Set for hidden helper agents that should stay out of the picker.
# disable-model-invocation: true # OPTIONAL. Set only when this agent must never be invoked as a subagent.
---
```

```markdown
<definitions>

<!-- Give definitions that will help the agent understand its role, do NOT give useless definitions that would clutter its understanding and cost tokens.
This section must also help the agent for the STEP 0, try to include definitions useful for the routing surface -->

- **useful definition 1** : a definition useful for the **agent** being invoked
- **useful definition 2** : another definition useful for the **agent** being invoked

</definitions>


## Step 0 - **CONFIRMATION**

1. Check the routing surface to confirm this agent is the right fit for the task.

| Request shape | Invoke? | Why / route |
|---|---:|---|
| Work owned by this agent | Yes | Continue to Step 1 |
| Work owned by another agent, skill, prompt, MCP server, hook, or product implementation | No | Refuse and route |

2. If the task does not match, return: `{"status": "refused", "agent": "agent-slug", "reason": "<specific reason>", "suggested_alternative": "<agent or skill>"}`.
3. If the task matches the routing matrix, continue to Step 1.

```

## Authoring Notes

```text
+------------------+-----------------------------------------+---------------------------------------------+
| Surface          | Write                                   | Avoid                                        |
+------------------+-----------------------------------------+---------------------------------------------+
| File target      | `.github/agents/<slug>.agent.md`        | package-style routing sidecars for new drafts |
| Discovery text   | `WHAT:` + `INVOKE FOR:` + `DO NOT ...`  | vague summaries like `Helpful helper.`       |
| Step 0           | embedded routing matrix + refusal JSON  | continuing when the match is uncertain       |
| Constraints      | forbidden work in `## Constraints`      | mixing refusal rules into random steps       |
| Output contract  | exact result shape in `## Output...`    | generic outputs like `Return a helpful answer.` |
| Delegation       | `agent` only with scoped `agents:`      | default `agents: *`                          |
+------------------+-----------------------------------------+---------------------------------------------+
```

- Use the tool snapshot or the chat "Configure Tools..." button when tool names are unclear.
- If `agents:` is absent, remove `agent` from `tools`.
- If you are normalizing an older package-style agent, fold routing-only content into Step 0 before removing now-redundant sibling files.

## Discovery and routing example

```text
+------+-------------+------------------------------------------------------------------+
| Use  | Surface     | Example                                                          |
+------+-------------+------------------------------------------------------------------+
| Bad  | description | `Helpful helper.`                                                |
| Good | description | `WHAT: ... INVOKE FOR: ... DO NOT INVOKE FOR: ...`              |
+------+-------------+------------------------------------------------------------------+
```

## Step 0 refusal example

```text
+------+---------+---------------------------------------------------------------------------+
| Use  | Surface | Example                                                                   |
+------+---------+---------------------------------------------------------------------------+
| Bad  | Step 0  | flat yes/no bullets with no contrastive matrix                            |
| Good | Step 0  | one ASCII routing matrix plus refusal JSON                                |
+------+---------+---------------------------------------------------------------------------+
```

## Workflow specificity example

```text
+------+---------+----------------------------------------------------------------+
| Use  | Surface | Example                                                        |
+------+---------+----------------------------------------------------------------+
| Bad  | Step 1  | `Read things.`                                                 |
| Good | Step 1  | Name the exact files, checks, inputs, or scope                |
+------+---------+----------------------------------------------------------------+
```

## Delegation boundary example

```text
+------+-------------+----------------------------------------------------------------+
| Use  | Surface     | Example                                                        |
+------+-------------+----------------------------------------------------------------+
| Bad  | frontmatter | `tools: [..., agent]` with `agents: *` by default             |
| Good | frontmatter | Add `agent` only with explicit allowlist or justified `*`     |
+------+-------------+----------------------------------------------------------------+
```

## Output contract example

```text
+------+-----------------+---------------------------------------------------------------+
| Use  | Surface         | Example                                                       |
+------+-----------------+---------------------------------------------------------------+
| Bad  | output contract | `Return a helpful answer.`                                    |
| Good | output contract | Name the exact sections, fields, artifacts, or refusal shape  |
+------+-----------------+---------------------------------------------------------------+
```
