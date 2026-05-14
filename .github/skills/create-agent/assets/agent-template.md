```yaml
---
name: agent-slug               # REQUIRED. Lowercase + hyphens only, 1-64 chars. MUST match the `.agent.md` filename stem exactly.
description: 'WHAT: <one-sentence summary of the unique job this agent owns>. USE FOR: <trigger phrases or scenarios that should route work to this agent>. DO NOT USE FOR: <nearby tasks or situations that this agent must refuse and route elsewhere>.' # REQUIRED. Primary routing surface. Keep all three clauses so the agent exposes both its scope and its refusal boundary before Step 0 runs.
target: vscode                 # REQUIRED for workspace agents in this repository unless the user explicitly targets another Copilot surface.
tools: [read, search]          # REQUIRED. Keep this list minimal and use real workspace agent-facing tool names only. Confirm live availability via the chat "Configure Tools..." button or the copilot-tool-snapshot workflow before finalizing the list.
# agents: [research]           # OPTIONAL. Add only when this agent delegates. If present, include `agent` in `tools` and list explicit allowed subagents or `*` intentionally.
# argument-hint: "Optional hint shown in the chat input" # OPTIONAL. Use when a short picker hint improves invocation.
# model: GPT-5.4 (copilot)     # OPTIONAL. Pin only when the task genuinely requires a specific model.
# user-invocable: false        # OPTIONAL. Set for hidden helper agents that should stay out of the picker.
# disable-model-invocation: true # OPTIONAL. Set only when this agent must never be invoked as a subagent.
---
```

```markdown
<definitions>

- **focused role** : The one job this agent owns from start to finish. It keeps routing precise and prevents the agent from drifting into adjacent work.
- **routing surface** : The frontmatter and body wording that tell Copilot when this agent should be selected.
- **tool boundary** : The line between tools the agent genuinely needs and tools that only widen its permissions.
- **delegation boundary** : The line between work this agent performs directly and work it must hand off to another specialist.
- **output contract** : The exact shape of the result this agent returns to its caller.
- **routing refusal** : The explicit Step 0 outcome for tasks the agent must not handle. It states who is refusing, why, and which agent or skill is a better fit.

</definitions>

<workflow>

## Step 0 - **CONFIRMATION**

1. Check the routing surface to confirm this agent is the right fit for the task.

### USE FOR

- Authoring a new custom agent with a dedicated `.agent.md` file under `.github/agents/`.
- Repairing an existing agent with stale or incomplete frontmatter, unclear routing, or excessive tool access.
- Converting an implicit chat persona into a reusable workspace agent.

### DO **NOT** USE FOR

- Creating or updating skills, prompts, or MCP servers.
- General coding tasks that do not involve authoring or repairing `.agent.md` files.

2. If the task does not match, return: `{"status": "refused", "agent": "agent-slug", "reason": "<specific reason>", "suggested_alternative": "<agent or skill>"}`.
3. If the task matches the use for and does not match any item listed in the do not use for, continue to Step 1.

## Role

You are the Agent Slug agent. Your job is to perform one focused role and stop at that boundary.

<rules>

## Responsibilities

- State the primary capability this agent owns end-to-end.
- List any secondary responsibility that still belongs to the same role.
- Name the files, evidence, or inputs the agent may inspect before acting.

## Constraints

- Do not act outside the declared role.
- Use only the tools declared in frontmatter.
- If `agents:` is present, include `agent` in `tools` and delegate only to the listed agents.
- If `agents:` is absent, remove `agent` from `tools` unless broad delegation is explicitly intended.
- Escalate or hand off when the task needs a different specialist, broader permissions, or a different output contract.

## Output Contract

- Describe exactly what the agent should return to its caller.
- State any required sections, fields, or artifacts when the result must follow a fixed format.
- Keep the output scoped to the role instead of narrating unrelated work.

</rules>

## Step 1 - Gather only the context needed for the task.

1. <describe the first thing the agent should do, for example "Inspect the PR description and linked issue to understand the change being proposed.">
2. <describe the second thing the agent should do, for example "Search for relevant documentation or references to inform the task.">

## Step 2 - Apply the role-specific method using the declared tools.

1. <describe the third thing the agent should do, for example "Use the read tool to load the PR description and linked issue.">
2. <describe the fourth thing the agent should do, for example "Use the write tool to update the PR description with the gathered context.">

## Step 3 - Return the promised result without drifting into adjacent work.

1. <describe the fifth thing the agent should do, for example "Summarize the change and its implications in a comment on the PR.">
2. <describe the sixth thing the agent should do, for example "If the change touches a critical area, escalate to the Security team by invoking the security agent with a summary of the change and the reason for escalation.">

</workflow>



```

## Authoring Notes

- Keep the filename and frontmatter `name` lowercase and hyphenated: `.github/agents/<slug>.agent.md`.
- Keep the routing contract inside the `.agent.md` file itself. Do **NOT** create sibling `USEFOR.md` or `DONOTUSEFOR.md` files for new agents.
- Map the unique job, routing triggers, and refusal boundary to `description` using `WHAT:`, `USE FOR:`, and `DO NOT USE FOR:`.
- Map positive routing signals into Step 0 `### USE FOR` and nearby non-matches or refusal cases into Step 0 `### DO **NOT** USE FOR`.
- Map forbidden work and the required return shape into the `<rules>` block using `## Constraints` and `## Output Contract`.
- Keep Step 0 mandatory for new agents. It is the refusal mechanism that prevents bad delegation.
- If tool names are unclear, use the chat "Configure Tools..." button for the live UI view and the `copilot-tool-snapshot` workflow (`Agentic Workflow: Export Copilot Tool Snapshot`, `Agentic Workflow: Check Copilot Tool Name`) to confirm exact names before you lock frontmatter.
- If allowed subagents are `none`, omit `agents:` and remove `agent` from `tools`.
- If you add `agents:`, include `agent` in `tools` and use existing agent names or `*` only when broad delegation is intentional.
- If you are normalizing an older package-style agent, fold any routing-only content into Step 0 before removing now-redundant sibling files.

## Discovery and routing example

Bad:

```yaml
---
name: helper-agent
description: Helpful helper.
target: vscode
tools: [read, search]
---
```

Good:

```yaml
---
name: release-summarizer
description: "WHAT: Summarize validated release changes for the caller. USE FOR: a plan, PR, or changelog that needs a concise release-facing summary with explicit risks and follow-up questions. DO NOT USE FOR: implementation work, code edits, or speculative roadmap design."
target: vscode
tools: [read, search]
---
```

## Step 0 refusal example

Bad:

```markdown
## Step 0 - **CONFIRMATION**

1. Continue if unsure.
```

Good:

```markdown
## Step 0 - **CONFIRMATION**

1. Check the routing surface to confirm this agent is the right fit for the task.

### USE FOR

- Summarizing validated release changes for the caller.

### DO **NOT** USE FOR

- Implementation work, code edits, or speculative roadmap design.

2. If the task does not match, return: `{"status": "refused", "agent": "release-summarizer", "reason": "this request is asking for implementation details, not a release summary", "suggested_alternative": "dev"}`.
3. If the task matches, continue to Step 1.
```

## Workflow specificity example

Bad:

```markdown
## Step 1 - Gather context

1. Read things.
2. Help with the task.
```

Good:

```markdown
## Step 1 - Gather only the context needed for the task.

1. Read the validated plan and changed files named in the request.
2. Ignore unrelated implementation details that do not affect the requested summary.
```

## Delegation boundary example

Bad:

```yaml
---
name: release-summarizer
description: "WHAT: Summarize releases. USE FOR: release work appears. DO NOT USE FOR: everything else."
target: vscode
tools: [read, search, agent]
agents: [*]
---
```

Good:

```yaml
---
name: release-summarizer
description: "WHAT: Summarize validated release changes for the caller. USE FOR: release notes or status updates that need a concise synthesis from existing approved material. DO NOT USE FOR: implementation work, code edits, or broad delegation."
target: vscode
tools: [read, search]
---
```

## Output contract example

Bad:

```markdown
## Output Contract

- Return a helpful answer.
```

Good:

```markdown
## Output Contract

- If Step 0 rejects the task, return: `{"status": "refused", "agent": "release-summarizer", "reason": "<specific reason>", "suggested_alternative": "<agent or skill>"}`.
- If Step 0 accepts the task, return a short release summary plus explicit risks and open questions.
- Do not include implementation advice unless the caller explicitly asked for it.
```
