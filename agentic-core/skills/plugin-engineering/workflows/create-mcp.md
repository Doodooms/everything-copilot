---
id: create-mcp
description: Implement or repair MCP server code using a verified SDK and exact registered tools.
invoke_for:
- Implement or repair MCP server tools, resources, prompts, or transport entrypoints
- Choose an MCP SDK language or transport based on approved constraints
- Validate tool names against actual registrations or tools/list
avoid_for:
- Install or deploy an MCP server, manage host configuration, or implement unrelated product features
references: []
---

## Step 1 - Inspect MCP entrypoints

1. Use #tool:search to locate MCP server entrypoints and stale server-code references when the repository already contains MCP code or was recently renamed.
2. If the relevant files are already known, inspect those files directly.

## Step 2 - Inspect the current MCP state

1. If the repository already contains MCP code or was recently renamed, use #tool:search to locate current server entrypoints and stale references.
2. If the exact files are already known, use #tool:read on those files directly.

## Step 3 - Clarify constraints

1. If the language, runtime compatibility, or transport is not clear from the request and repository state, use #tool:vscode/askQuestions before choosing an implementation path.

## Step 4 - Choose the language

1. Use #tool:read on #file:../references/create-mcp/assets/language-selection-checklist.md to apply the [language selection checklist](../references/create-mcp/assets/language-selection-checklist.md).

## Step 5 - Choose the transport

1. Use #tool:read on #file:../references/create-mcp/references/manage_mcp.md to apply the transport guidance for [MCP servers in VS Code](../references/create-mcp/references/manage_mcp.md).

## Step 6 - Implement the smallest working server

1. Use #tool:read on #file:../references/create-mcp/references/URIs.md ([official SDK references](../references/create-mcp/references/URIs.md)) when selecting SDK APIs or package paths.
2. Register a single tool first, validate it over `stdio`, then expand to resources, prompts, and HTTP transport.

## Step 7 - Validate

1. Use #tool:execute to run the narrowest build, install, or smoke-test command for the touched implementation.
2. If host integration is required, return the server's exact transport, command, arguments, and published tool names to DevOps; do not edit host configuration.
3. Check this method's scaffold using `bash agentic-core/skills/plugin-engineering/references/create-mcp/scripts/validate_mcp.sh` and the [validator script](../references/create-mcp/scripts/validate_mcp.sh); this scaffold check does not replace testing the generated server.
