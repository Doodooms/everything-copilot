# askQuestions guidance

Use [ask_questions.json](../assets/ask_questions.json) only when the conversation does not already define a usable prompt contract.

## When to use it

- The user wants a new prompt, but the task, routing triggers, or expected output are still ambiguous.
- The conversation implies a reusable prompt pattern, but the required input or output shape is still unclear.
- The prompt may need a specific agent, tool surface, or argument hint that cannot be inferred safely.

## How to use it

- Load [ask_questions.json](../assets/ask_questions.json).
- Use the structured question tool `vscode/askQuestions` with only the fields that are still missing.
- Ask for the task, routing triggers, and output contract before optional runtime fields such as model.
- Skip the questionnaire entirely when the conversation already defines the task and output shape clearly.

## How answers map to the prompt file

- Prompt slug -> filename `.github/prompts/<slug>.prompt.md`.
- Purpose + routing triggers -> frontmatter `description` using `What:` and `Use when:`.
- Expected inputs -> body text and optional `## Inputs` section.
- Required tools -> frontmatter `tools` only when the prompt truly needs them.
- Target agent -> frontmatter `agent` when pinning the agent materially improves execution.
- Output contract -> `## Output Contract`.

## Minimum contract to capture

- Prompt slug and unique task
- Trigger phrases for routing
- Expected inputs or argument shape
- Required tools or agent pinning only if needed
- Output contract