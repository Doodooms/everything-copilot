---
name: create-mcp
description: "WHAT: Create or update MCP servers and their VS Code registration with a one-shot workflow that chooses the right language, transport, capability set, and validation path. USE FOR: creating a new MCP server for a specific purpose, choosing between Go, Rust, Python, or an explicit Node.js path, implementing tools, resources, prompts, or apps, configuring mcp.json, or repairing MCP setup drift after a rename or refactor. DO NOT USE FOR: general backend services unrelated to MCP, prompt or agent authoring, or speculative architecture work with no MCP server change."
user-invocable: false
context: fork
compatibility: vscode 1.119.0+, github-copilot 1.119.0+
metadata:
  creation-date: 2026-05-14
  creator: Doodooms
license: MIT
---

<definitions>

- **MCP server** : A local or remote server that exposes tools, resources, prompts, or MCP apps through the Model Context Protocol.
- **MCP contract** : The minimum set of decisions that must be explicit before implementation: purpose, target clients, transport, capability set, security boundary, configuration target, and validation command.
- **capability set** : The exact MCP surface the server must expose now, such as tools, resources, prompts, apps, and any related auth or hosting requirements.
- **tool catalog snapshot** : The workspace export in `.vscode/copilot-tools.snapshot.json` that reflects currently available Copilot tools and toolsets. It complements the chat `Configure Tools...` button.
- **transport boundary** : The separation between MCP business logic and the transport layer so `stdio` and Streamable HTTP can be swapped without rewriting tool, resource, or prompt handlers.

</definitions>

<workflow>

## Step 0 - **CONFIRMATION**

1. USE #tool:read **IMMEDIATELY** on #file:./references/USEFOR.md and **IMMEDIATELY** on #file:./references/DONOTUSEFOR.md to confirm with certainty if this skill should be used.
2. Now read the following rules and workflow steps to understand how the skill works and what it requires for execution.

<rules>

- Use only skill-facing `#tool:` names such as `read`, `agent`, `execute`, and `vscode/askQuestions`.
- If exact tool names are unclear, use #tool:read on #file:../../../tools/copilot-tool-snapshot/README.md and then use the Command Palette commands `Agentic Workflow: Export Copilot Tool Snapshot` or `Agentic Workflow: Check Copilot Tool Name`. The chat `Configure Tools...` button provides the same live discovery from the UI side.
- Reference support files only at the workflow step that consumes them. Do **NOT** front-load them in a global runtime-inputs list.
- Reuse a complete MCP contract from the conversation when it already exists. Use structured questions only for the missing fields.
- Do **NOT** default to Node.js. Choose Node.js only when the user explicitly asks for it or the surrounding host ecosystem makes that choice mandatory.
- Keep tools, resources, prompts, and apps aligned to the requested capability set. Do **NOT** promise capabilities and leave them as TODOs.
- Keep tool, resource, prompt, and app logic independent from transport so `stdio` and Streamable HTTP can be swapped at the entrypoint.
- Keep secrets out of source code and `mcp.json`. Use environment variables, VS Code input variables, or equivalent indirection instead.
- Prefer official SDKs and pin versions. MCP SDK APIs evolve quickly; verify the installed version's docs before copying examples verbatim.
- Start validation with the smallest executable slice that can falsify the current implementation, then widen only if the task changed workspace-wide MCP surfaces.

</rules>

## Step 1 - Inspect the current MCP surface

1. Inspect the current MCP implementation and registration surface before you choose an edit path.
  - If the repository already contains MCP code or was recently renamed, use #tool:agent with a read-only exploration agent to locate current entrypoints, `.vscode/mcp.json`, and stale references.
  - If the exact files are already known, use #tool:read on those files directly.
2. Load current host guidance only when it matters.
  - Use #tool:read on #file:./references/latest-docs.md before drafting when the current MCP or VS Code behavior is unclear.
  - Use #tool:read on #file:./references/manage_mcp.md only when the task touches VS Code registration, trust, sandboxing, configuration location, or server lifecycle behavior.

## Step 2 - Capture the missing MCP contract

1. Reuse the contract that is already explicit in the conversation when it is complete.
  - If the request already names the server purpose, target clients, transport, capability set, constraints, and validation goal, extract those fields directly and do not ask redundant questions.
2. Ask structured questions only for the missing fields.
  - Otherwise, use #tool:read on #file:./references/ask_questions.md and #file:./assets/ask_questions.json and then use #tool:vscode/askQuestions to collect only the missing structured answers.
3. Ask only for behavior-changing fields.
  - Server slug and user-facing purpose.
  - Target clients and transport target.
  - Required capability set.
  - External systems, auth, secrets, and sandbox constraints.
  - Language preference, forbidden languages, and non-negotiable performance or deployment constraints.
  - Configuration target and validation goal.
4. Keep the input path singular.
  - Do **NOT** both derive the full contract from the conversation and run the full questionnaire.

## Step 3 - Choose the implementation path

1. Select the language deliberately.
  - Use #tool:read on #file:./assets/language-selection-checklist.md when you are choosing between Go, Rust, Python, or the explicit Node.js exception.
2. Map the requested capability set before coding.
  - Use #tool:read on #file:./references/server-capabilities.md when the server needs more than one MCP capability or when the request says the server should be complete, full-featured, or one-shot.
3. Resolve uncertain APIs from canonical docs.
  - Use #tool:read on #file:./references/URIs.md when you need the official MCP, SDK, or VS Code documentation links for the chosen target.
  - Re-read #file:./references/latest-docs.md when the required client behavior or SDK API looks newer than the examples in this skill.
4. Decide the build slice before editing.
  - Map purpose to the server name and user-facing tool, resource, prompt, or app names.
  - Map target clients and transport to `stdio`, Streamable HTTP, or both.
  - Map the configuration target to workspace `mcp.json`, user profile `mcp.json`, remote user config, dev container settings, or no VS Code registration change.
  - Map the capability set, auth boundary, and validation goal to concrete files, handlers, and executable checks.

## Step 4 - Implement the MCP server package

1. Start from canonical examples, not memory.
  - Use #tool:read on #file:./assets/minimal-server-examples.md when you need starter code for the selected SDK.
  - Use #tool:read on #file:./assets/server-good-bad-examples.md when you need to sanity-check capability scope, transport separation, secret handling, or `mcp.json` hygiene before writing code.
2. Build the requested server in one coherent package.
  - Create or update the server entrypoint, handler modules, dependency manifest, and registration or configuration files required by the chosen language and host.
  - Implement each declared capability from the captured contract in this edit slice.
  - Keep transport wiring thin so `stdio` and Streamable HTTP can be swapped without rewriting the business logic.
3. Keep configuration and secrets production-safe.
  - Use environment variables or VS Code input variables instead of hardcoding secrets.
  - If VS Code registration is required, add only the narrowest `mcp.json` or dev container changes needed for the task.

## Step 5 - Review before validation

1. Re-read the edited surface before validating.
  - Read the finished entrypoint, any touched handler files, and `.vscode/mcp.json` when registration changed.
2. Confirm the implementation still matches the request.
  - Ensure the implemented capability set matches the declared one.
  - Ensure the chosen language and transport still match the explicit constraints.
  - Ensure promised resources, prompts, apps, auth, or remote transport are actually wired, not left as TODOs.
3. Confirm configuration safety.
  - Ensure secrets are not hardcoded.
  - Ensure local servers use trust and sandbox settings deliberately when the host and task require them.
  - Ensure Node.js was chosen only because the request or host ecosystem required it.

## Step 6 - Validate

1. Run the narrowest executable validation for the touched implementation.
  - Use #tool:execute to run install, build, typecheck, test, or smoke-test commands for the chosen SDK.
2. Validate VS Code MCP registration when touched.
  - If `.vscode/mcp.json` changed, use #tool:execute on #file:./scripts/validate_mcp.py with the narrowest relevant `--server` target before you finish.
  - Re-read #file:./references/manage_mcp.md only when validation output suggests a VS Code registration issue.
3. Widen validation only when repository integration changed.
  - If the task changed workspace-wide MCP surfaces, run the repository's broader health or verification command after the narrow server-specific checks.
4. Fix all executable validation failures before finishing.

## Step 7 - Finalize

1. Summarize the finished server package.
  - State the chosen language and transport.
  - State the implemented capability set.
  - State where the server is registered.
  - State which validation commands were run.
  - Give one example prompt or invocation that should exercise the server.

</workflow>
