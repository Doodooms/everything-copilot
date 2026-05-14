# askQuestions Guidance

## Purpose

- Use [ask_questions.json](../assets/ask_questions.json) only when the conversation does not already contain a usable MCP contract.

## When to use it

- The user wants a new MCP server, but the purpose, clients, capability set, or transport is still ambiguous.
- The task says "build the whole MCP server" or similar, but does not specify whether that means tools, resources, prompts, apps, or only one of them.
- The implementation language, auth boundary, or VS Code registration target is still unclear.

## How to use it

- Load [ask_questions.json](../assets/ask_questions.json).
- Use `vscode/askQuestions` with only the fields that are still missing.
- Ask for capability set, transport, and auth before you ask for optional host details.
- Skip the questionnaire entirely when the conversation already defines the purpose, clients, transport, capabilities, constraints, and validation path.

## How answers map to the implementation

- Server slug -> server name, package or module names, and the `mcp.json` server key.
- Purpose -> user-facing tool, resource, prompt, and app naming.
- Target clients + transport -> `stdio`, Streamable HTTP, or both, plus configuration location.
- Required capabilities -> the exact handler surface to implement now.
- External systems + auth -> client wrappers, secret loading, and sandbox decisions.
- Language preference + constraints -> the language decision in [language-selection-checklist](../assets/language-selection-checklist.md).
- Configuration target -> workspace `mcp.json`, user profile, remote user config, dev container config, or no VS Code change.
- Validation goal -> the Step 6 command that must pass before the task is complete.

## Minimum contract to capture

- Server purpose and slug.
- Required client or host targets.
- Transport target.
- Required capability set.
- Auth or secret handling constraints.
- Language preference or forbidden languages.
- Validation goal.