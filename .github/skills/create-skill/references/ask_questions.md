# askQuestions Guidance

Use [ask_questions.json](../assets/ask_questions.json) **ONLY** at the workflow step where structured input is still missing and the process cannot be derived safely from existing context.

When to use it:

- The task is to create a new skill and the workflow is not already visible in the conversation.
- The trigger phrases, purpose, or expected outputs are still ambiguous.
- The skill needs consistent inputs that are easier to capture with a small fixed questionnaire.

How to use it:

- Load [ask_questions.json](../assets/ask_questions.json).
- Use the structured question tool `vscode/askQuestions` with that JSON structure.
- Ask **ONLY** the minimum questions needed to make the workflow deterministic.
- **DO NOT** ask questions if the conversation history already contains a clear repeatable process.

Example:

- Skill name -> from the `Skill Name` prompt
- Discovery text -> from `Purpose` plus `When To Use`
- Output mode -> from `Output Format`

Anti-pattern:

- Asking open-ended questions when the asset already provides a structured prompt.