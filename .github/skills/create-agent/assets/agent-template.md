```yaml
---
name: agent-slug               # REQUIRED. Lowercase + hyphens only, 1-64 chars. MUST match the `.agent.md` filename stem exactly.
description: 'WHAT: <one-sentence summary of the unique job this agent owns>. INVOKE FOR: <trigger phrases or scenarios that should route work to this agent>. DO NOT INVOKE FOR: <nearby tasks or situations outside this agent boundary>.' # REQUIRED. Primary routing surface.
target: vscode                 # REQUIRED for workspace agents in this repository.
tools: [read, search]          # OPTIONAL. Add only tools the agent genuinely needs; omit when the default is sufficient, or use [] only for an intentional tool-free agent. Confirm live availability before finalizing names.
# model: GPT-6 Luna (copilot) # OPTIONAL. Always check last available version and pin only when necessary.
# reasoning-effort: max # OPTIONAL. Always review official model benchmarks to select the best reasoning-effort for cost-efficiency
# agents: [research]           # OPTIONAL. Add only when this agent delegates. If present, include `agent` in `tools` and list explicit allowed subagents or `*` intentionally.
# argument-hint: "Optional hint shown in the chat input" # OPTIONAL. Use when a short picker hint improves invocation.
# user-invocable: false        # OPTIONAL. Set for hidden helper agents that should stay out of the picker.
# disable-model-invocation: true # OPTIONAL. Set only when this agent must never be invoked as a subagent.
---
```
```markdown
<definitions>

<!-- Optional: omit this entire block when no non-obvious role vocabulary needs clarification.
Give definitions that will help the agent understand its role, do NOT give useless definitions that would clutter its understanding and cost tokens.
Include only definitions that help the agent perform its role. -->

- **useful definition 1** : a definition useful for the **agent** being invoked

</definitions>

<rules>

## Role

State the specific role this agent owns and the work it performs.

## Responsibilities

- Name the primary capability owned by the agent.
- Include only secondary responsibilities that belong to the same role.

## Constraints

- State the work outside this agent's boundary.
- Keep tool and delegation constraints consistent with frontmatter.

## Output Contract

- Name the result, fields, or artifacts the agent must return.

</rules>

<workflow>

## Step 1 - Gather the context needed for the task.

1. <name the inputs, files, or evidence this role must inspect>

## Step 2 - Apply the role-specific method.

1. <describe the main action the agent performs within its role>

## Step 3 - Return the promised result.

1. <describe the concrete handoff or result returned to the caller>

</workflow>

```

Use this as a scaffold for one self-contained `.agent.md`, not as a package template. The frontmatter `description` is the sole routing and admission surface; the body defines the role and execution contract after selection.

## Authoring Notes

```text
+------------------+-----------------------------------------+---------------------------------------------+
| Surface          | Write                                   | Avoid                                        |
+------------------+-----------------------------------------+---------------------------------------------+
| File target      | `.github/agents/<slug>.agent.md`        | package-style routing sidecars for new drafts |
| Discovery text   | `WHAT:` + `INVOKE FOR:` + `DO NOT ...`  | vague summaries like `Helpful helper.`       |
| Routing          | clear description clauses; execution details in the workflow | body-level admission rules or a routing matrix |
| Constraints      | forbidden work in `## Constraints`      | burying constraints in workflow actions       |
| Output contract  | exact result shape in `## Output...`    | generic outputs like `Return a helpful answer.` |
| Delegation       | `agent` only with scoped `agents:`      | default `agents: *`                          |
+------------------+-----------------------------------------+---------------------------------------------+
```

- Use the tool snapshot or the chat "Configure Tools..." button when tool names are unclear.
- If `agents:` is absent, remove `agent` from `tools`.
- The description alone decides whether this agent should be selected. Put any role-specific execution branches in the workflow, not in a body-level admission section.

## Discovery and routing example

```text
+------+-------------+------------------------------------------------------------------+
| Use  | Surface     | Example                                                          |
+------+-------------+------------------------------------------------------------------+
| Bad  | description | `Helpful helper.`                                                |
| Good | description | `WHAT: ... INVOKE FOR: ... DO NOT INVOKE FOR: ...`              |
+------+-------------+------------------------------------------------------------------+
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
| Good | output contract | Name the exact result fields or artifact shape                 |
+------+-----------------+---------------------------------------------------------------+
```
