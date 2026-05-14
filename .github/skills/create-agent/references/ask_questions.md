# askQuestions Guidance

Use [ask_questions.json](../assets/ask_questions.json) only when the conversation does not already contain a usable agent contract.

## When to use it

- The user wants a new agent, but the role, routing triggers, or tool boundaries are still ambiguous.
- The user described a persona informally and you need to turn it into deterministic frontmatter and body instructions.
- Delegation or invocation mode matters and cannot be inferred safely from context.

## How to use it

- Load [ask_questions.json](../assets/ask_questions.json).
- Use the structured question tool `vscode/askQuestions` with only the fields that are still missing.
- Ask for required tools and forbidden work before you ask for optional fields such as model or handoffs.
- If invocation mode or delegation is still fuzzy, review [delegation and invocation guidance](./delegation_and_invocation.md) before you finalize the answers.
- Skip the questionnaire entirely when the conversation already defines the role, tools, boundaries, and expected output.

## How answers map to the agent file

- Agent slug -> filename `.github/agents/<slug>.agent.md` and frontmatter `name`.
- Purpose + routing triggers -> frontmatter `description` using `What:` and `Use when:`.
- Required tools -> frontmatter `tools`.
- Forbidden work -> `## Constraints`.
- Invocation mode -> `user-invocable` and `disable-model-invocation`.
- Allowed subagents -> `agents:` and the `agent` tool only when delegation is genuinely required.
- Output contract -> `## Output Contract`.
- `none` for allowed subagents -> omit `agents:` and remove `agent` from `tools`.
- Named subagents -> verify they already exist under `.github/agents/` before you commit the draft.

## Minimum contract to capture

- Agent slug and unique purpose
- Trigger phrases for routing
- Required and forbidden tools or actions
- Invocation mode and any subagent allowlist
- Output contract