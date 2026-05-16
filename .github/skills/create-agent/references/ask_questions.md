# askQuestions Guidance

Use [ask_questions.json](../assets/ask_questions.json) only when the conversation does not already contain a usable agent contract.

## When to use it

- The user wants a new agent, but the focused role, routing triggers, or refusal boundary are still ambiguous.
- The user described a persona informally and you need to turn it into deterministic frontmatter plus a self-contained workflow.
- Tool access, delegation, or invocation mode still changes the contract materially.
- The output contract is not explicit enough to draft `## Output Contract` directly.

## How to use it

- Load [ask_questions.json](../assets/ask_questions.json).
- Use the structured question tool `vscode/askQuestions` with only the fields that are still missing.
- Ask for required tools and forbidden work before optional fields the request did not ask for.
- If invocation mode or delegation is still fuzzy, review [delegation and invocation guidance](./delegation_and_invocation.md) before you finalize the answers.
- Skip the questionnaire entirely when the conversation already defines the role, routing, tools, delegation boundary, and expected output.

## How answers map to the agent file

- Agent slug -> path `.github/agents/<slug>.agent.md` and frontmatter `name`.
- Focused role + routing triggers + routing exclusions -> frontmatter `description` using `WHAT:`, `USE FOR:`, and `DO NOT USE FOR:`.
- Routing triggers -> Step 0 `### USE FOR`.
- Routing exclusions -> Step 0 `### DO **NOT** USE FOR`.
- Required tools -> frontmatter `tools`.
- Forbidden work -> `<rules>` -> `## Constraints`.
- Invocation mode -> `user-invocable` and `disable-model-invocation`.
- Allowed subagents -> `agents:` and the `agent` tool only when delegation is genuinely required.
- Output contract -> `<rules>` -> `## Output Contract`.
- `none` for allowed subagents -> omit `agents:` and remove `agent` from `tools`.
- Named subagents -> verify they already exist under `.github/agents/` before you commit the draft.

## Minimum contract to capture

- Agent slug and focused role.
- Trigger phrases for routing.
- Routing exclusions or nearby tasks the agent must refuse.
- Required and forbidden tools or actions.
- Invocation mode and any subagent allowlist.
- Output contract.