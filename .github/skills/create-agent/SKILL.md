---
name: create-agent
description: "WHAT: Create or update deterministic VS Code custom agent definitions with precise frontmatter, minimal tool access, and clear delegation boundaries. USE FOR: authoring a new `.agent.md`, repairing stale agent metadata, tightening tool or subagent restrictions, or converting an implicit chat persona into a reusable workspace agent. DO NOT USE FOR: creating skills, prompts, MCP servers, or general coding changes unrelated to agent definitions."
user-invocable: false
context: fork
compatibility: vscode 1.119.0+, github-copilot 1.119.0+
metadata:
   creation-date: 2026-05-12
   creator: Doodooms
license: MIT
---

<definitions>

- **custom agent** : A reusable `.agent.md` file that defines a specific persona, its tools, optional subagents, and its operating instructions.
- **agent contract** : The combination of frontmatter and body text that determines how the agent is routed, what it may do, and what it must return.
- **routing surface** : The part of the agent that drives selection: mainly `description`, plus any supporting body wording that clarifies the role after the agent is loaded.
- **tool boundary** : The line between tools the agent genuinely needs and tools that only widen its permissions.
- **delegation boundary** : The line between work the agent performs directly and work it should hand off through `agent`, `agents:`, or `handoffs`.
- **invocation mode** : The frontmatter combination of `user-invocable` and `disable-model-invocation` that controls picker visibility and subagent eligibility.
- **subagent-only agent** : An agent hidden from the picker with `user-invocable: false` but still callable by other agents unless `disable-model-invocation: true` also blocks it.

</definitions>

<workflow>

## Step 0 - **CONFIRMATION**

1. USE #tool:read **IMMEDIATELY** on #file:./references/USEFOR.md and **IMMEDIATELY** on #file:./references/DONOTUSEFOR.md to confirm with certainty if this skill should be used.
2. Now read the following rules and workflow steps to understand how the skill works and what it requires for execution.

<rules>

- Default to workspace-shared agent files under `.github/agents/<slug>.agent.md` unless the user explicitly asks for a different supported scope.
- Keep the tool list minimal. Every extra tool widens the agent's blast radius and weakens routing precision.
- If the agent declares `agents:`, it **MUST** also include the `agent` tool.
- If the draft does **NOT** delegate, omit `agents:` and remove `agent` from `tools`.
- Prefer `user-invocable` and `disable-model-invocation` for invocation control. Do **NOT** introduce deprecated `infer`.
- `description` is the primary routing surface. It **MUST** describe what the agent does and when to select it.
- If routing still feels ambiguous after drafting, produce one example prompt that should route to the agent and verify that the `description` clearly covers that prompt.
- Reference support files only on the workflow step that consumes them. Support markdown files must stay free of active `#tool:` and `#file:` markers.

</rules>

## Step 1 - Inspect the current agent surface

If the name, scope, or overlap is unclear, use #tool:search under #file:../../agents/ to inspect the workspace `.github/agents/` directory and avoid duplicates and naming collisions.
If the target agent already exists and you know the exact file path, use #tool:read on its current `.agent.md` file first.
Use the current [agent template](./assets/agent-template.md) as the canonical draft scaffold when you need to confirm the expected body shape.

## Step 2 - Capture the missing agent contract

If the conversation already establishes the persona, tools, constraints, and output shape, extract them directly and do not ask redundant questions.
**Otherwise**, review [askQuestions guidance](./references/ask_questions.md). If invocation mode or delegation is still unclear, also review [delegation and invocation guidance](./references/delegation_and_invocation.md). If structured questions are still needed, use #tool:read on #file:./assets/ask_questions.json and then use #tool:vscode/askQuestions to collect only the missing structured answers.
Ask only for the fields that change behavior: agent slug, unique job, routing triggers, required tools, forbidden tools, invocation mode, delegation needs, and output contract.
Do **NOT** ask for `model`, `handoffs`, or `hooks` unless the task explicitly needs them.

## Step 3 - Draft the agent file

Use #tool:read on #file:./assets/agent-template.md when writing the target file.
Use #tool:edit to create or update `.github/agents/<slug>.agent.md`.
Set `description` so it clearly states what the agent does and includes `Use when:` trigger phrases.
Prefer `target: vscode` for workspace agents unless the user explicitly targets another Copilot surface.
Add only the tools the agent genuinely needs. Omit `tools` entirely when the default is acceptable; use `tools: []` only when a tool-free agent is intentional.
If the agent delegates, include `agent` in `tools` and list only the allowed subagents in `agents:`. Use `*` only when broad delegation is intentional.
Use `user-invocable: false` for helper agents that should stay out of the picker. Use `disable-model-invocation: true` only when the agent must never be invoked as a subagent.
Add `handoffs` or `hooks` only when the workflow truly benefits and the task calls for them.
Map captured answers directly into the draft:
- slug -> filename and frontmatter `name`
- unique job + routing triggers -> frontmatter `description` with `What:` and `Use when:`
- required tools -> frontmatter `tools`
- forbidden work -> `## Constraints`
- invocation mode -> `user-invocable` and `disable-model-invocation`
- allowed subagents -> `agents:` and the `agent` tool only when delegation is genuinely required
- output contract -> `## Output Contract`
If invocation mode or delegation still feels tricky while drafting, review [delegation and invocation guidance](./references/delegation_and_invocation.md) before setting `agent`, `agents:`, `user-invocable`, or `disable-model-invocation`.
Keep the draft agent-shaped: `# Role`, `## Responsibilities`, `## Workflow` or `## Approach`, `## Constraints`, and `## Output Contract`.
Use the XML wrappers shown in the template only as scaffolding for new drafts. Do **NOT** force an existing agent into a skill-shaped body just to mirror the template asset.

## Step 4 - Review before validation

Re-read the generated `.agent.md` file with #tool:read before validation.
Ensure the body keeps a clear agent contract: `# Role`, `## Responsibilities`, `## Workflow` or `## Approach`, `## Constraints`, and `## Output Contract`.
Ensure `description` includes both `What:` and `Use when:` and that one concrete example prompt would actually route to this agent.
If `agent` appears in `tools`, confirm `agents:` is explicit or that broad delegation is truly intentional.
If you used the template's XML wrappers for a new draft, keep them coherent around the human-facing sections instead of copying skill-specific blocks blindly.

## Step 5 - Validate

Use #tool:execute to run #file:./scripts/validate_agent.py with the repository interpreter: `./.venv/bin/python .github/skills/create-agent/scripts/validate_agent.py --agent-file <agent_file>`.
If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root before validating.
If validation reports errors or warnings you need help interpreting, use #tool:read on #file:./references/validation.md and apply the matching fix.
If validation flags unknown tools, broad delegation, or missing subagents, fix the frontmatter or referenced agent names instead of weakening the validator.
Fix **ALL** ERRORs before proceeding. Address WARNINGs when they point to ambiguous routing, deprecated fields, or overly broad tool access.

## Step 6 - Finalize

Summarize what the agent does, where the file lives, which tools and subagents it exposes, one example prompt that should route to it, and one short sentence explaining why the `description` matches that prompt.

</workflow>
