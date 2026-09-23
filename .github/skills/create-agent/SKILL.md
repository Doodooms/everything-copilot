---
name: create-agent
description: "WHAT: Create, repair, migrate, review, or validate a custom VS Code `.agent.md` file. INVOKE FOR: agent frontmatter, persona, routing, delegation, invocation mode, workflow, output contracts, templates, and agent validators. DO NOT INVOKE FOR: skills, prompts, MCP servers, hooks, or product implementations."
user-invocable: false
context: fork
compatibility: vscode 1.119.0+, github-copilot 1.119.0+
metadata:
   creation-date: 2026-09-23
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
- **self-contained agent** : A single `.agent.md` file whose Step 0 routing rules, refusal boundary, workflow, and output contract all live inside that file without sibling routing documents.
- **skill** : A reusable capability or package workflow; it is not a specialist persona and does not require an agent's delegation or invocation contract.
- **primitive choice** : The decision between an agent, skill, prompt, MCP server, hook, or product implementation before authoring begins.

</definitions>

<workflow>

## Step 0 - **CONFIRMATION**

1. Confirm that the request needs a custom agent rather than another primitive.

| Request shape | Invoke? | Route |
|---|---:|---|
| Create, repair, migrate, review, or validate one `.agent.md` | Yes | Continue with `create-agent` |
| Create or repair a reusable skill | No | `create-skill` |
| Create or repair a reusable prompt | No | `create-prompt` |
| Create or repair an MCP server | No | `create-mcp` |
| Create or repair a hook | No | `create-hook` |
| Implement general product behavior | No | Relevant implementation skill |

2. If the request does not match, stop and return exactly one concise routing object:

```json
{"status":"rejected","agent":"create-agent","reason":"The request is for a different primitive or product implementation, not a custom agent.","routing":"Route to create-skill, create-prompt, create-mcp, create-hook, or the relevant implementation skill."}
```

3. If the request matches, continue to Step 1.

<rules>

- This is the default skill for agent work in this workspace. Use it before improvising agent edits or loading stale external agent-customization guidance.
- An agent is one `.agent.md` with persona or role, routing, tool boundary, optional delegation, invocation mode, workflow, and exact output contract. A skill is a reusable capability/package; do not require skill topology or a skill ACCEPT/REJECT contract here.
- Default to a single self-contained agent file at `.github/agents/<slug>.agent.md`.
- Keep routing rules inside the `.agent.md` file itself. Do **NOT** require sibling routing docs for new agents.
- Sibling support docs may guide authoring, but the generated agent must not depend on them for runtime routing or workflow.
- For new drafts, use `<definitions>`, `<workflow>`, and `<rules>` as the canonical wrapper vocabulary. Do **NOT** invent extra XML-style tags.
- Keep the tool list minimal. Every extra tool widens the agent's blast radius and weakens routing precision.
- If the agent declares `agents:`, it **MUST** also include the `agent` tool.
- If the draft does **NOT** delegate, omit `agents:` and remove `agent` from `tools`.
- Prefer `user-invocable` and `disable-model-invocation` for invocation control. Do **NOT** introduce deprecated `infer`.
- When a direct-user orchestrator is the sole user-facing entry point, set `user-invocable: false` on specialist agents so the picker routes users through the orchestrator. Keep `disable-model-invocation: false` unless the agent must also be unavailable to other agents.
- `description` is the primary routing surface. It **MUST** use `WHAT:`, `INVOKE FOR:`, and `DO NOT INVOKE FOR:` so the agent advertises both scope and refusal boundary before Step 0 runs.
- Every ordinary agent **MUST** include a Step 0 confirmation with one dense routing decision matrix and a structured refusal path. The only exception is a direct-user orchestrator with `user-invocable: true` and `disable-model-invocation: true`; that agent may omit Step 0 because it is blocked from model or subagent invocation, but it must retain the canonical workflow, role, rules, and output contract.
- There **MUST** be one source of truth per concept. If a matrix, mapping, or checklist already exists in one support file, later steps **MUST** point to it instead of restating it.
- If extra routing help is still needed before the workflow loads, keep it in one dense support surface. Do **NOT** split the same yes or no boundary across multiple files.
- If routing still feels ambiguous after drafting, produce one example prompt that should route to the agent and verify that the `description` clearly covers that prompt.
- Add a user-review pause only when the agent's role requires user-owned confirmation; otherwise return the defined handoff directly.
- Reference support files only on the workflow step that consumes them. Support markdown files must stay free of active `#tool:` and `#file:` markers.
- Keep contrastive choices in dense ASCII matrices and keep procedural workflow in ordered `1.` actions with `-` bullets only for narrow sub-checks, exceptions, or examples.
- Reject skill, prompt, MCP, hook, and product-implementation requests at the primitive gate instead of stretching the agent primitive.

</rules>

## Step 1 - Establish the agent contract

1. Inspect the workspace agent surface before drafting.
   - If the name, scope, or overlap is unclear, use #tool:search in the workspace `.github/agents/` directory to avoid duplicates and naming collisions.
   - If the target agent already exists and you know the exact file path, use #tool:read on its current `.agent.md` file first.
   - If the request is still ambiguous after Step 0 confirmation, review the [primitive selection matrix](./references/primitive-selection.md) only for the remaining agent-vs-other-primitive choice.
2. Confirm current host requirements only when they matter for this draft.
   - Use #tool:read on #file:./references/latest-docs.md only when you need to confirm current VS Code custom-agent frontmatter, location, picker behavior, or subagent behavior.
   - Review [custom agent docs](./references/custom_agent.md) and [subagent docs](./references/sub_agent.md) only for the specific ambiguity that still remains after [latest-docs](./references/latest-docs.md).
3. Confirm the canonical body shape before you draft: `<definitions>`, `<workflow>`, Step 0 for ordinary agents, `## Role`, `<rules>` with Responsibilities, Constraints, and Output Contract, then ordered Steps 1-3. The direct-user orchestrator exception is allowed only with `user-invocable: true` and `disable-model-invocation: true`.
   - Use the current [agent template](./assets/agent-template.md) as the canonical draft scaffold when you need to confirm the expected body shape.

## Step 2 - Capture the missing agent contract

1. Reuse the contract already present in the conversation when it is complete.
   - If the conversation already establishes the persona, tools, constraints, and output shape, extract them directly and do not ask redundant questions.
2. Load guidance only when behavior-changing details are missing.
   - Review [askQuestions guidance](./references/ask_questions.md) only when the agent contract is still incomplete.
   - If invocation mode or delegation is still unclear, also review [delegation and invocation guidance](./references/delegation_and_invocation.md).
3. Load the structured questionnaire only when the conversation still leaves missing fields.
   - Use #tool:read on #file:./assets/ask_questions.json and then use #tool:vscode/askQuestions to collect only the missing structured answers.
4. Keep optional fields out unless the task explicitly needs them.
   - Do **NOT** ask for `model`, `handoffs`, or `hooks` unless the task explicitly needs them.

## Step 3 - Draft the self-contained agent file

1. Load the canonical drafting scaffold and create the target file.
   - Use #tool:read on #file:./assets/agent-template.md when writing the target file.
   - Use #tool:edit to create or update `.github/agents/<slug>.agent.md`.
2. Set frontmatter deliberately before expanding the body.
   - Set `description` so it clearly states what the agent does and includes explicit `INVOKE FOR:` and `DO NOT INVOKE FOR:` routing clauses.
   - Set `target: vscode` for workspace agents.
   - Add only the tools the agent genuinely needs. Omit `tools` entirely when the default is acceptable; use `tools: []` only when a tool-free agent is intentional.
   - If the agent delegates, include `agent` in `tools` and list only the allowed subagents in `agents:`. Use `*` only when broad delegation is intentional.
   - Use `user-invocable: false` for helper agents that should stay out of the picker. Use `disable-model-invocation: true` only when the agent must never be invoked as a subagent.
   - Add `handoffs` or `hooks` only when the workflow truly benefits and the task calls for them.
3. Confirm live tool names before finalizing frontmatter when needed.
   - If tool names are unclear, review the `tools/copilot-tool-snapshot` workflow README and then use the Command Palette commands `Agentic Workflow: Export Copilot Tool Snapshot` or `Agentic Workflow: Check Copilot Tool Name`.
   - The chat `Configure Tools...` button exposes the same live availability from the UI side.
4. Map captured answers directly into the draft.
   - Use the mapping matrix in [askQuestions guidance](./references/ask_questions.md) instead of inventing new field destinations.
5. Resolve tricky delegation or invocation decisions before finalizing the draft.
   - If invocation mode or delegation still feels tricky while drafting, review [delegation and invocation guidance](./references/delegation_and_invocation.md) before setting `agent`, `agents:`, `user-invocable`, or `disable-model-invocation`.
6. Keep the generated body aligned with the canonical structure.
   - Keep ordinary drafts agent-shaped with `<definitions>`, then a `<workflow>` wrapper containing `## Step 0 - **CONFIRMATION**`, one dense routing decision matrix, `## Role`, a `<rules>` block with `## Responsibilities`, `## Constraints`, and `## Output Contract`, then `## Step 1 - ...`, `## Step 2 - ...`, and `## Step 3 - ...`. The direct-user orchestrator exception may omit Step 0 only under the invocation flags documented above.
   - Inside the workflow, prefer ordered `1. 2. 3.` lists when actions must happen in sequence and keep sub-checks, exceptions, or examples under those actions as `-` bullets.
   - Keep routing, refusal, workflow, delegation boundaries, and output requirements inside the `.agent.md` file itself instead of splitting them into sibling support files.
7. Use the template wrappers as scaffolding for new drafts.
   - Existing legacy agents may keep their older shape unless the task explicitly rewrites them.

## Step 4 - Review before validation

1. Re-read the generated `.agent.md` file before validation.
   - Use #tool:read on the finished draft so you validate the actual file rather than memory.
2. Confirm only the high-risk contract surfaces before validation.
   - Ensure the agent stays a single `.agent.md` file under `.github/agents/`.
   - Ensure Step 0 embeds one dense routing decision matrix and the refusal JSON inside that file.
   - Ensure `description`, `tools`, `agents:`, `user-invocable`, and `disable-model-invocation` all agree with the intended role.
   - If you used the template wrappers for a new draft, keep `<workflow>` around the full runtime contract and `<rules>` around `## Responsibilities`, `## Constraints`, plus `## Output Contract`.

## Step 5 - Validate

1. Run the agent validator.
   - Use #tool:execute to run #file:./scripts/validate_agent.py with the repository interpreter: `./.venv/bin/python .github/skills/create-agent/scripts/validate_agent.py --agent-file <agent_file>`.
   - The validator and its lint core both live under this skill's own `scripts/` directory. Repo-level wrappers may call them, but they are not the source of truth.
2. Refresh the repository environment if validation prerequisites are missing.
   - If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root before validating.
3. Load the fix guide only when the output needs interpretation.
   - If validation reports errors or warnings you need help interpreting, use #tool:read on #file:./references/validation.md and apply the matching fix.
   - If the validator behavior itself needs inspection, review [agent lint core](./scripts/agent_lint_core.py) at this step.
4. Run the final local audit after script validation.
   - Use #tool:read on #file:./references/final-checklist.md and resolve every unchecked item or state why it does not apply.
5. Fix the full validation surface instead of weakening the contract.
   - If validation flags unknown tools, broad delegation, missing embedded routing sections, or missing subagents, fix the agent contract instead of weakening the validator.
   - When tool names are the issue, use the `copilot-tool-snapshot` workflow or the chat `Configure Tools...` button before you guess.
   - Fix **ALL** ERRORs before proceeding.
   - Address WARNINGs when they point to ambiguous routing, deprecated fields, broad delegation, or legacy routing-file mode.

## Step 6 - Finalize

1. Summarize the finished agent package.
   - State what the agent does.
   - State where the file lives.
   - State which tools and subagents it exposes.
   - Give one example prompt that should route to it.
   - Add one short sentence explaining why the `description` matches that prompt.

</workflow>
