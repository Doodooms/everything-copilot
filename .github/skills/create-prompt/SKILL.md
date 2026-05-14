---
name: create-prompt
description: "WHAT: Create or update reusable VS Code prompt files with clear routing text, lightweight Markdown structure, and scoped tool use. USE FOR: creating a new `.prompt.md`, tightening an existing prompt, improving prompt readability, or adding prompt validation guidance. DO NOT USE FOR: skills, custom agents, MCP servers, or general code changes unrelated to prompt authoring."
user-invocable: false
context: fork
compatibility: vscode 1.119.0+, github-copilot 1.119.0+
metadata:
  creation-date: 2026-05-13
  creator: Doodooms
license: MIT
---

<definitions>

- **prompt** : A reusable `.prompt.md` file that captures one focused task and can be run directly from chat.
- **prompt contract** : The combination of frontmatter and body structure that tells Copilot when to surface the prompt and what result shape it should request.
- **argument hint** : Optional frontmatter text shown in the chat input to suggest the missing user argument.
- **tool scope** : The exact `tools` list attached to the prompt. It should stay minimal because prompt tools are merged with the selected agent's tools.

</definitions>

<workflow>

## Step 0 - **CONFIRMATION**

1. USE #tool:read **IMMEDIATELY** on #file:./references/USEFOR.md and **IMMEDIATELY** on #file:./references/DONOTUSEFOR.md to confirm with certainty if this skill should be used.
2. Now read the following rules and workflow steps to understand how the skill works and what it requires for execution.

<rules>

- Default to workspace prompt files under `.github/prompts/<slug>.prompt.md` unless the user explicitly asks for a supported user-profile scope.
- One prompt should own one focused task. If the request mixes planning, implementation, and review, route to a skill or agent instead.
- `description` is the primary discovery surface. It **MUST** say what the prompt does and when it should be used.
- Keep prompt bodies human-readable: use one `#` heading and short `##` sections when the prompt covers distinct concerns such as inputs, constraints, or output shape.
- Add `tools`, `agent`, `model`, or `argument-hint` only when they materially change how the prompt runs.
- Support markdown files in this skill must stay free of active `#tool:` and `#file:` markers. Use markdown links for files and inline tool names there.

</rules>

## Step 1 - Inspect the current prompt surface

1. Inspect the workspace prompt surface before drafting.
  - If the name, scope, or overlap is unclear, use #tool:search under #file:../../prompts/ to inspect the workspace `.github/prompts/` directory and avoid duplicates.
  - If the target prompt already exists and you know its path, use #tool:read on that `.prompt.md` file first.
2. Confirm the canonical prompt shape before you write.
  - Use the current [prompt template](./assets/prompt-template.md) as the canonical scaffold when you need to confirm the expected body shape.

## Step 2 - Capture the missing prompt contract

1. Reuse the prompt contract already present in the conversation when it is complete.
  - If the conversation already establishes the task, inputs, and expected output, extract them directly and do not ask redundant questions.
2. Load the question assets only when details are missing.
  - Otherwise, use #tool:read on #file:./references/ask_questions.md and #file:./assets/ask_questions.json and then use #tool:vscode/askQuestions to collect only the missing structured answers.
3. Ask only for behavior-changing fields.
  - Prompt slug.
  - Unique job.
  - Routing triggers.
  - Required inputs.
  - Required tools.
  - Target agent, if any.
  - Output contract.
4. Keep optional model selection out unless the task explicitly needs it.
  - Do **NOT** ask for `model` unless the user explicitly needs a model preference.

## Step 3 - Draft the prompt file

1. Load the canonical prompt scaffold and create the target file.
  - Use #tool:read on #file:./assets/prompt-template.md when writing the target prompt.
  - Use #tool:edit to create or update `.github/prompts/<slug>.prompt.md`.
2. Set frontmatter deliberately before expanding the body.
  - Set `description` so it clearly states the prompt's job and includes `Use when:` trigger phrases.
  - Set `argument-hint` only when the user needs help knowing what argument to pass.
  - Add `tools` only when the prompt truly needs a narrower or broader tool surface than the selected agent would already provide.
  - If the prompt needs a specific agent, set `agent` explicitly. Otherwise leave it unset.
3. Keep the body readable and proportionate to the task.
  - For short prompts, `# Task` plus a concise bullet list is enough.
  - For longer prompts, add short `##` sections such as `## Inputs`, `## Constraints`, and `## Output Contract`.
4. Use active markers only for immediate consumption.
  - Use markdown links for referenced files when the prompt is naming context.
  - Use active `#file:` or `#tool:` markers only when the prompt text expects immediate consumption of that file or tool.

## Step 4 - Review before validation

1. Re-read the generated `.prompt.md` file before validation.
  - Use #tool:read on the finished draft so you validate the actual file rather than memory.
2. Confirm the body stays readable.
  - Ensure the body has one top-level heading and enough `##` sections to avoid becoming visually flat.
3. Confirm the routing text is explicit.
  - Ensure `description` includes both `What:` and `Use when:` and that one example invocation would obviously route to the prompt.
4. Confirm tool scope is intentional.
  - If `tools` is present, confirm every listed tool is intentional.

## Step 5 - Validate

1. Run the prompt validator.
  - Use #tool:execute to run #file:./scripts/validate_prompt.py with the repository interpreter: `./.venv/bin/python .github/skills/create-prompt/scripts/validate_prompt.py --prompt-file <prompt_file>`.
2. Refresh the repository environment if validation prerequisites are missing.
  - If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root before validating.
3. Load the fix guide only when the output needs interpretation.
  - If validation reports structural or routing warnings you need help interpreting, use #tool:read on #file:./references/validation.md and apply the matching fix.
4. Fix the full validation surface before you proceed.
  - Fix **ALL** ERRORs before proceeding.
  - Address WARNINGs when they point to weak routing text, flat structure, or overly broad tools.

## Step 6 - Finalize

1. Summarize the finished prompt.
  - State what the prompt does.
  - State where the file lives.
  - State which tools or agent it pins.
  - Give one example invocation.

</workflow>
