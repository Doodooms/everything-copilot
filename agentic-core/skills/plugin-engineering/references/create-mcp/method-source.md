---
name: create-mcp
description: "WHAT: Implement or repair MCP server code with Go, Rust, or Python as the primary implementation targets. WHEN TO USE: registering server tools, resources, or prompts; choosing an SDK or transport; or repairing server-code drift. DO NOT USE FOR: host configuration, installation, deployment, or unrelated product behavior."
user-invocable: false
disable-model-invocation: false
---

# Implement MCP Servers

<rules>

- Only reference `#tool:` names available in the workspace tool catalog. Use exact names such as `read`, `search`, `execute`, and `vscode/askQuestions`; do not copy tool names from another host.
- Do not place punctuation immediately after a `#file:` reference.
- Node.js must only be used if the user formally requests it, due to its heaviness.
- If implementation constraints are unclear, use #tool:vscode/askQuestions to clarify runtime compatibility, performance envelope, security sensitivity, and iteration speed before recommending a language.
- Prefer official SDKs and pin versions. MCP SDK APIs evolve quickly; always verify the installed version's docs before coding.
- Derive MCP tool names from actual registrations or the server's `tools/list` response. MUST NOT invent client aliases or infer names from a server ID; pack manifests should record exact published names.
- Keep tool, resource, and prompt logic independent from transport so `stdio` and Streamable HTTP can be swapped at the entrypoint.
- Start from the smallest tool registration that proves the SDK wiring works before adding resources, auth, or business logic.
- Use #tool:execute to run language-specific install, build, or validation commands after the first edit.

</rules>

<workflow>

## Step 1 - Inspect MCP entrypoints

1. Use #tool:search to locate MCP server entrypoints and stale server-code references when the repository already contains MCP code or was recently renamed.
2. If the relevant files are already known, inspect those files directly.

## Step 2 - Inspect the current MCP state

1. If the repository already contains MCP code or was recently renamed, use #tool:search to locate current server entrypoints and stale references.
2. If the exact files are already known, use #tool:read on those files directly.

## Step 3 - Clarify constraints

1. If the language, runtime compatibility, or transport is not clear from the request and repository state, use #tool:vscode/askQuestions before choosing an implementation path.

## Step 4 - Choose the language

1. Use #tool:read on #file:./assets/language-selection-checklist.md to apply the [language selection checklist](./assets/language-selection-checklist.md).

## Step 5 - Choose the transport

1. Use #tool:read on #file:./references/manage_mcp.md to apply the transport guidance for [MCP servers in VS Code](./references/manage_mcp.md).

## Step 6 - Implement the smallest working server

1. Use #tool:read on #file:./references/URIs.md ([official SDK references](./references/URIs.md)) when selecting SDK APIs or package paths.
2. Register a single tool first, validate it over `stdio`, then expand to resources, prompts, and HTTP transport.

## Step 7 - Validate

1. Use #tool:execute to run the narrowest build, install, or smoke-test command for the touched implementation.
2. If host integration is required, return the server's exact transport, command, arguments, and published tool names to DevOps; do not edit host configuration.
3. Check this method's scaffold using `bash agentic-core/skills/plugin-engineering/references/create-mcp/scripts/validate_mcp.sh` and the [validator script](./scripts/validate_mcp.sh); this scaffold check does not replace testing the generated server.

</workflow>
