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

- Default to workspace-shared agent packages under `.github/agents/<slug>/<slug>.agent.md` so the agent can keep sibling routing docs in `references/USEFOR.md` and `references/DONOTUSEFOR.md`.
- For new drafts, use `<definitions>`, `<workflow>`, and `<rules>` as the canonical wrapper vocabulary. Do **NOT** invent extra XML-style tags.
- Keep the tool list minimal. Every extra tool widens the agent's blast radius and weakens routing precision.
- If the agent declares `agents:`, it **MUST** also include the `agent` tool.
- If the draft does **NOT** delegate, omit `agents:` and remove `agent` from `tools`.
- Prefer `user-invocable` and `disable-model-invocation` for invocation control. Do **NOT** introduce deprecated `infer`.
- `description` is the primary routing surface. It **MUST** use `WHAT:`, `USE FOR:`, and `DO NOT USE FOR:` so the agent advertises both scope and refusal boundary before Step 0 runs.
- Every new agent **MUST** include a Step 0 confirmation that reads `references/USEFOR.md` and `references/DONOTUSEFOR.md` and refuses mismatches with a structured JSON payload.
- If routing still feels ambiguous after drafting, produce one example prompt that should route to the agent and verify that the `description` clearly covers that prompt.
- Reference support files only on the workflow step that consumes them. Support markdown files must stay free of active `#tool:` and `#file:` markers.

</rules>

## Step 1 - Inspect the current agent surface

1. Inspect the workspace agent surface before drafting.
   - If the name, scope, or overlap is unclear, use #tool:search under #file:../../agents/ to inspect the workspace `.github/agents/` directory and avoid duplicates and naming collisions.
   - If the target agent already exists and you know the exact file path, use #tool:read on its current `.agent.md` file first.
2. Confirm the canonical body shape before you draft.
   - Use the current [agent template](./assets/agent-template.md) as the canonical draft scaffold when you need to confirm the expected body shape.
3. Confirm current host requirements only when they matter for this draft.
   - Use #tool:read on #file:./references/latest-docs.md before drafting when you need to confirm current VS Code custom-agent frontmatter, location, or subagent behavior.

## Step 2 - Capture the missing agent contract

1. Reuse the contract already present in the conversation when it is complete.
   - If the conversation already establishes the persona, tools, constraints, and output shape, extract them directly and do not ask redundant questions.
2. Load guidance and the structured questionnaire only when details are missing.
   - **Otherwise**, review [askQuestions guidance](./references/ask_questions.md).
   - If invocation mode or delegation is still unclear, also review [delegation and invocation guidance](./references/delegation_and_invocation.md).
   - If structured questions are still needed, use #tool:read on #file:./assets/ask_questions.json and then use #tool:vscode/askQuestions to collect only the missing structured answers.
3. Ask only for behavior-changing fields.
   - Agent slug.
   - Unique job.
   - Routing triggers.
   - Routing exclusions.
   - Required tools.
   - Forbidden tools.
   - Invocation mode.
   - Delegation needs.
   - Output contract.
4. Keep optional fields out unless the task explicitly needs them.
   - Do **NOT** ask for `model`, `handoffs`, or `hooks` unless the task explicitly needs them.

## Step 3 - Draft the agent file

1. Load the canonical drafting scaffold and create the package files.
   - Use #tool:read on #file:./assets/agent-template.md when writing the target file.
   - Use #tool:edit to create or update `.github/agents/<slug>/<slug>.agent.md`.
   - Use #tool:edit to create or update `.github/agents/<slug>/references/USEFOR.md` and `.github/agents/<slug>/references/DONOTUSEFOR.md`.
2. Set frontmatter deliberately before expanding the body.
   - Set `description` so it clearly states what the agent does and includes explicit `USE FOR:` and `DO NOT USE FOR:` routing clauses.
   - Prefer `target: vscode` for workspace agents unless the user explicitly targets another Copilot surface.
   - Add only the tools the agent genuinely needs. Omit `tools` entirely when the default is acceptable; use `tools: []` only when a tool-free agent is intentional.
   - If the agent delegates, include `agent` in `tools` and list only the allowed subagents in `agents:`. Use `*` only when broad delegation is intentional.
   - Use `user-invocable: false` for helper agents that should stay out of the picker. Use `disable-model-invocation: true` only when the agent must never be invoked as a subagent.
   - Add `handoffs` or `hooks` only when the workflow truly benefits and the task calls for them.
3. Confirm live tool names before finalizing frontmatter when needed.
   - If tool names are unclear, use #tool:read on #file:../../../tools/copilot-tool-snapshot/README.md and then use the Command Palette commands `Agentic Workflow: Export Copilot Tool Snapshot` or `Agentic Workflow: Check Copilot Tool Name`.
   - The chat `Configure Tools...` button exposes the same live availability from the UI side.
4. Map captured answers directly into the draft.
   - slug -> package directory, filename, and frontmatter `name`
   - unique job + routing triggers + routing exclusions -> frontmatter `description` with `WHAT:`, `USE FOR:`, and `DO NOT USE FOR:`
   - routing triggers -> `references/USEFOR.md`
   - routing exclusions -> `references/DONOTUSEFOR.md`
   - required tools -> frontmatter `tools`
   - forbidden work -> `<rules>` -> `## Constraints`
   - invocation mode -> `user-invocable` and `disable-model-invocation`
   - allowed subagents -> `agents:` and the `agent` tool only when delegation is genuinely required
   - output contract -> `<rules>` -> `## Output Contract`
5. Resolve tricky delegation or invocation decisions before finalizing the draft.
   - If invocation mode or delegation still feels tricky while drafting, review [delegation and invocation guidance](./references/delegation_and_invocation.md) before setting `agent`, `agents:`, `user-invocable`, or `disable-model-invocation`.
6. Keep the generated body aligned with the canonical structure.
   - Keep the draft agent-shaped with `<definitions>`, then a `<workflow>` wrapper containing `## Step 0 - **CONFIRMATION**`, `## Role`, a `<rules>` block with `## Responsibilities`, `## Constraints`, and `## Output Contract`, then `## Step 1 - ...`, `## Step 2 - ...`, and `## Step 3 - ...`.
   - Inside the workflow, prefer ordered `1. 2. 3.` lists when actions must happen in sequence.
   - Keep those instructions runtime-facing.
7. Use the template wrappers as scaffolding for new drafts.
   - Existing legacy agents may keep their older shape unless the task explicitly rewrites them.

## Step 4 - Review before validation

1. Re-read the generated `.agent.md` file before validation.
   - Use #tool:read on the finished draft so you validate the actual file rather than memory.
2. Confirm the package structure is complete.
   - Ensure the agent lives in a dedicated package directory.
   - Ensure `references/USEFOR.md` plus `references/DONOTUSEFOR.md` exist beside it.
3. Confirm the body shape matches the canonical contract.
   - Ensure the body keeps the canonical step-based contract: `## Step 0 - **CONFIRMATION**`, `## Role`, `<rules>` with `## Responsibilities`, `## Constraints`, and `## Output Contract`, then `## Step 1 - ...`, `## Step 2 - ...`, and `## Step 3 - ...`.
4. Confirm the refusal path is machine-actionable.
   - Ensure Step 0 refuses mismatches with a JSON payload containing `status: refused`, `agent`, `reason`, and `suggested_alternative`.
5. Confirm the routing surface is explicit.
   - Ensure `description` includes `WHAT:`, `USE FOR:`, and `DO NOT USE FOR:`.
   - Ensure one concrete example prompt would actually route to this agent.
6. Confirm delegation is intentionally scoped.
   - If `agent` appears in `tools`, confirm `agents:` is explicit or that broad delegation is truly intentional.
7. Preserve wrappers when you used the canonical scaffold.
   - If you used the template wrappers for a new draft, keep `<workflow>` around the full runtime contract and `<rules>` around `## Responsibilities`, `## Constraints`, plus `## Output Contract`.

## Step 5 - Validate

1. Run the agent validator.
   - Use #tool:execute to run #file:./scripts/validate_agent.py with the repository interpreter: `./.venv/bin/python .github/skills/create-agent/scripts/validate_agent.py --agent-file <agent_file>`.
2. Refresh the repository environment if validation prerequisites are missing.
   - If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root before validating.
3. Load the fix guide only when the output needs interpretation.
   - If validation reports errors or warnings you need help interpreting, use #tool:read on #file:./references/validation.md and apply the matching fix.
4. Fix the full validation surface instead of weakening the contract.
   - If validation flags unknown tools, broad delegation, or missing subagents, fix the frontmatter or referenced agent names instead of weakening the validator.
   - When tool names are the issue, use the `copilot-tool-snapshot` workflow or the chat `Configure Tools...` button before you guess.
   - Fix **ALL** ERRORs before proceeding.
   - Address WARNINGs when they point to ambiguous routing, deprecated fields, or overly broad tool access.

## Step 6 - Finalize

1. Summarize the finished agent package.
   - State what the agent does.
   - State where the file lives.
   - State which tools and subagents it exposes.
   - Give one example prompt that should route to it.
   - Add one short sentence explaining why the `description` matches that prompt.

</workflow>
