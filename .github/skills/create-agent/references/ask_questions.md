# askQuestions Guidance

Use [ask_questions.json](../assets/ask_questions.json) only when the conversation does not already contain a usable agent contract.

When to use it

- The user wants a new agent, but the role, routing triggers, or tool boundaries are still ambiguous.
- The user described a persona informally and you need to turn it into deterministic frontmatter and body instructions.
- Delegation or invocation mode matters and cannot be inferred safely from context.

How to use it

- Load [ask_questions.json](../assets/ask_questions.json).
- Use the structured question tool `vscode/askQuestions` with only the fields that are still missing.
- Ask for required tools and forbidden work before you ask for optional fields such as model or handoffs.
- Skip the questionnaire entirely when the conversation already defines the role, tools, boundaries, and expected output.

Minimum contract to capture

- Agent slug and unique purpose
- Trigger phrases for routing
- Required and forbidden tools or actions
- Invocation mode and any subagent allowlist
- Output contract