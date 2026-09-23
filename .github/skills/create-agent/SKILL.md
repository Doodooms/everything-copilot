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

- **agent** : A single `.agent.md` persona selected by its `description` and governed by a bounded role, tool surface, invocation mode, delegation policy, workflow, and output contract.
- **skill** : A reusable capability and workflow that an agent loads for repeatable work; it does not define a specialist persona or agent invocation contract.
- **agent contract** : The combination of frontmatter and body text that determines how the agent is routed, what it may do, and what it must return.
- **routing surface** : The frontmatter `description`, which alone determines agent selection and admission before the body is loaded.
- **tool boundary** : The line between tools the agent genuinely needs and tools that only widen its permissions.
- **delegation boundary** : The line between work the agent performs directly and work it should hand off through `agent`, `agents:`, or `handoffs`.
- **invocation mode** : The frontmatter combination of `user-invocable` and `disable-model-invocation` that controls picker visibility and subagent eligibility.
- **subagent-only agent** : An agent hidden from the picker with `user-invocable: false` but still callable by other agents unless `disable-model-invocation: true` also blocks it.
- **self-contained agent** : A single `.agent.md` file whose routing description, role, workflow, and output contract all live inside that file without sibling runtime documents.
- **primitive choice** : The decision between an agent, skill, prompt, MCP server, hook, or product implementation before authoring begins.

</definitions>

<rules>

- This is the default skill for agent work in this workspace. Use it before improvising agent edits or loading stale external agent-customization guidance.
- Choose an agent for a bounded persona whose description, tools, invocation mode, delegation, workflow, or output contract matter. Choose a skill for repeatable capability guidance and package workflows.
- Default to a single self-contained agent file at `.github/agents/<slug>.agent.md`.
- Keep routing rules inside the `.agent.md` file itself. Do **NOT** require sibling routing docs for new agents.
- Sibling support docs may guide authoring, but the generated agent must not depend on them for runtime routing or workflow.
- The generated body uses optional non-empty `<definitions>`, followed by `<rules>` containing `## Role`, `## Responsibilities`, `## Constraints`, and `## Output Contract`, then a separate `<workflow>` containing Steps 1-3. Do **NOT** invent extra XML-style tags.
- Keep the tool list minimal. Every extra tool widens the agent's blast radius and weakens routing precision.
- If the agent declares `agents:`, it **MUST** also include the `agent` tool.
- If the draft does **NOT** delegate, omit `agents:` and remove `agent` from `tools`.
- Prefer `user-invocable` and `disable-model-invocation` for invocation control. Do **NOT** introduce deprecated `infer`.
- When a direct-user orchestrator is the sole user-facing entry point, set `user-invocable: false` on specialist agents so the picker routes users through the orchestrator. Keep `disable-model-invocation: false` unless the agent must also be unavailable to other agents.
- The dedicated direct-user Orchestrator is the sole exception: set `user-invocable: true` and `disable-model-invocation: true`. Do **NOT** generalize this exception to specialists or any other agents.
- The frontmatter `description` is the sole agent routing and admission surface. It **MUST** use `WHAT:`, `INVOKE FOR:`, and `DO NOT INVOKE FOR:`. Do not add a Step 0 or a body-level admission matrix; body content governs execution only after selection.
- Keep the runtime contract in the agent file: role, minimal tools, optional delegation, invocation mode, workflow, constraints, and output contract. Use a role-specific hand-off or refusal only when needed; do not require a refusal JSON contract.
- There **MUST** be one source of truth per concept. If a matrix, mapping, or checklist already exists in one support file, later steps **MUST** point to it instead of restating it.
- Keep primitive comparisons in this skill's support guidance, not in generated agent bodies. Do **NOT** split the same selection boundary across multiple files.
- If selection still feels ambiguous after drafting, produce one example prompt and verify that the `description` clearly covers it.
- Add a user-review pause only when the agent's role requires user-owned confirmation; otherwise return the defined handoff directly.
- Reference support files only on the workflow step that consumes them. Support markdown files must stay free of active `#tool:` and `#file:` markers.
- Keep procedural workflow in ordered `1.` actions with `-` bullets only for narrow sub-checks, exceptions, or examples.
- Choose the primitive early. Use `create-agent` for a persona with a tool boundary, invocation mode, or delegation contract; use a skill for a reusable capability/package workflow.

</rules>

<admission>

## ACCEPT

- Create, repair, migrate, review, or validate a custom workspace `.agent.md` file.
- Update agent-specific templates, references, lint rules, or validation tests.

## REJECT

- Create or repair a skill -> `create-skill`.
- Create or repair a prompt -> `create-prompt`.
- Create or repair an MCP server -> `create-mcp`.
- Create a hook or general product behavior -> use the corresponding authoring or implementation surface.

For rejected work, state the reason and route it to the matching surface; do not draft an agent as a substitute.

</admission>

<workflow>

## Step 1 - Establish the agent contract

1. Inspect the workspace agent surface before drafting.
   - If the name, scope, or overlap is unclear, use #tool:search in the workspace `.github/agents/` directory to avoid duplicates and naming collisions.
   - If the target agent already exists and you know the exact file path, use #tool:read on its current `.agent.md` file first.
   - If the agent-vs-other-primitive choice remains ambiguous, review the [primitive selection matrix](./references/primitive-selection.md) only for that choice.
2. Confirm current host requirements only when they matter for this draft.
   - Use #tool:read on #file:./references/latest-docs.md only when you need to confirm current VS Code custom-agent frontmatter, location, picker behavior, or subagent behavior.
   - Review [custom agent docs](./references/custom_agent.md) and [subagent docs](./references/sub_agent.md) only for the specific ambiguity that still remains after [latest-docs](./references/latest-docs.md).
3. Confirm the canonical body shape before drafting: omit `<definitions>` unless useful role terms need clarification; when present, keep definitions non-empty. Follow them with `<rules>` containing `## Role`, `## Responsibilities`, `## Constraints`, and `## Output Contract`, then a separate `<workflow>` with ordered Steps 1-3.
   - Use the current [agent template](./assets/agent-template.md) as the canonical draft scaffold when you need to confirm the expected body shape.

## Step 2 - Capture the missing agent contract

1. Reuse the contract already present in the conversation when it is complete.
   - If the conversation already establishes the persona, tools, constraints, and output shape, extract them directly and do not ask redundant questions.
2. Load guidance only when behavior-changing details are missing.
   - Review [askQuestions guidance](./references/ask_questions.md) only when the agent contract is still incomplete.
   - If invocation mode or delegation is still unclear, also review [delegation and invocation guidance](./references/delegation_and_invocation.md).
3. Load the structured questionnaire only when the conversation still leaves missing fields.
   - Use #tool:read on #file:./assets/ask_questions.json and then use #tool:vscode/askQuestions to collect only the missing structured answers from the [question payload](./assets/ask_questions.json).
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
   - Keep drafts agent-shaped with optional non-empty `<definitions>` before a `<rules>` block containing `## Role`, `## Responsibilities`, `## Constraints`, and `## Output Contract`, followed by a separate `<workflow>` block containing `## Step 1 - ...`, `## Step 2 - ...`, and `## Step 3 - ...`.
   - Inside the workflow, prefer ordered `1. 2. 3.` lists when actions must happen in sequence and keep sub-checks, exceptions, or examples under those actions as `-` bullets.
   - Keep routing, workflow, delegation boundaries, and output requirements inside the `.agent.md` file itself instead of splitting runtime behavior into sibling support files.
7. Use the template wrappers as scaffolding for new drafts.
   - Existing legacy agents may keep their older shape unless the task explicitly rewrites them.

## Step 4 - Review before validation

1. Re-read the generated `.agent.md` file before validation.
   - Use #tool:read on the finished draft so you validate the actual file rather than memory.
2. Confirm only the high-risk contract surfaces before validation.
   - Ensure the agent stays a single `.agent.md` file under `.github/agents/`.
   - Ensure the description, tools, invocation mode, delegation, workflow, constraints, and output contract agree with the intended role.
   - Ensure `description`, `tools`, `agents:`, `user-invocable`, and `disable-model-invocation` all agree with the intended role.
   - If you used the template wrappers for a new draft, keep optional `<definitions>` before `<rules>`, `<rules>` around `## Role`, `## Responsibilities`, `## Constraints`, and `## Output Contract`, and a separate `<workflow>` around the ordered Steps 1-3.

## Step 5 - Validate

1. Run the agent validator.
   - Use #tool:execute to run the [agent validator](./scripts/validate_agent.py) with the repository interpreter: `./.venv/bin/python .github/skills/create-agent/scripts/validate_agent.py --agent-file <agent_file>`.
   - The validator and its lint core both live under this skill's own `scripts/` directory. Repo-level wrappers may call them, but they are not the source of truth.
2. Refresh the repository environment if validation prerequisites are missing.
   - If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root before validating.
3. Load the fix guide only when the output needs interpretation.
   - If validation reports errors or warnings you need help interpreting, use #tool:read on #file:./references/validation.md and apply the matching fix in the [validation guide](./references/validation.md).
   - If the validator behavior itself needs inspection, review [agent lint core](./scripts/agent_lint_core.py) at this step.
4. Run the final local audit after script validation.
   - Use #tool:read on #file:./references/final-checklist.md and resolve every unchecked item in the [final checklist](./references/final-checklist.md) or state why it does not apply.
5. Fix the full validation surface instead of weakening the contract.
   - If validation flags unknown tools, broad delegation, a malformed description or body, or missing subagents, fix the agent contract instead of weakening the validator.
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
