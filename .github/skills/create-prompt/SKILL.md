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

If the name, scope, or overlap is unclear, use #tool:search under #file:../../prompts/ to inspect the workspace `.github/prompts/` directory and avoid duplicates.
If the target prompt already exists and you know its path, use #tool:read on that `.prompt.md` file first.
Use the current [prompt template](./assets/prompt-template.md) as the canonical scaffold when you need to confirm the expected body shape.

## Step 2 - Capture the missing prompt contract

If the conversation already establishes the task, inputs, and expected output, extract them directly and do not ask redundant questions.
Otherwise, use #tool:read on #file:./references/ask_questions.md and #file:./assets/ask_questions.json and then use #tool:vscode/askQuestions to collect only the missing structured answers.
Ask only for fields that change behavior: prompt slug, unique job, routing triggers, required inputs, required tools, target agent if any, and output contract.
Do **NOT** ask for `model` unless the user explicitly needs a model preference.

## Step 3 - Draft the prompt file

Use #tool:read on #file:./assets/prompt-template.md when writing the target prompt.
Use #tool:edit to create or update `.github/prompts/<slug>.prompt.md`.
Set `description` so it clearly states the prompt's job and includes `Use when:` trigger phrases.
Set `argument-hint` only when the user needs help knowing what argument to pass.
Add `tools` only when the prompt truly needs a narrower or broader tool surface than the selected agent would already provide.
If the prompt needs a specific agent, set `agent` explicitly. Otherwise leave it unset.
Keep the body direct and readable. For short prompts, `# Task` plus a concise bullet list is enough. For longer prompts, add short `##` sections such as `## Inputs`, `## Constraints`, and `## Output Contract`.
Use markdown links for referenced files when the prompt is naming context. Use active `#file:` or `#tool:` markers only when the prompt text expects immediate consumption of that file or tool.

## Step 4 - Review before validation

Re-read the generated `.prompt.md` file with #tool:read before validation.
Ensure the body has one top-level heading and enough `##` sections to avoid becoming visually flat.
Ensure `description` includes both `What:` and `Use when:` and that one example invocation would obviously route to the prompt.
If `tools` is present, confirm every listed tool is intentional.

## Step 5 - Validate

Use #tool:execute to run #file:./scripts/validate_prompt.py with the repository interpreter: `./.venv/bin/python .github/skills/create-prompt/scripts/validate_prompt.py --prompt-file <prompt_file>`.
If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root before validating.
If validation reports structural or routing warnings you need help interpreting, use #tool:read on #file:./references/validation.md and apply the matching fix.
Fix **ALL** ERRORs before proceeding. Address WARNINGs when they point to weak routing text, flat structure, or overly broad tools.

## Step 6 - Finalize

Summarize what the prompt does, where the file lives, which tools or agent it pins, and one example invocation.

</workflow>
