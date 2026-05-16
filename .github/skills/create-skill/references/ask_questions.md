# askQuestions guidance

Use [ask_questions.json](../assets/ask_questions.json) **ONLY** at the workflow step where structured input is still missing and the process cannot be derived safely from existing context.

When to use it:

- The task is to create a new skill and the workflow is not already visible in the conversation.
- The `WHAT`, `USE FOR`, or `DO NOT USE FOR` boundaries are still ambiguous.
- The scope or access mode is still unclear after reviewing the conversation.
- Required MCP servers, special tool dependencies, or local automation scripts are still unclear.

How to use it:

- Load [ask_questions.json](../assets/ask_questions.json).
- Use the structured question tool `vscode/askQuestions` with that JSON structure.
- Ask **ONLY** the minimum questions needed to make the workflow deterministic.
- **DO NOT** ask questions if the conversation history already contains a clear repeatable process.
- **DO NOT** ask whether the package should include `assets/`, `references/`, or `scripts/`; that package shape is mandatory here.

Example mapping:

- Skill name -> from `Skill Name`
- Description -> assemble from `WHAT`, `USE FOR`, and `DO NOT USE FOR`
- Location -> from `Scope`
- Access flags -> from `Access Mode`
- Dependency notes -> from `Dependencies`
- Output mode -> from `Output Format`

Anti-pattern:

- Asking open-ended questions when the asset already provides a structured prompt.