# Latest MCP Docs

## Purpose

- Use this file when the repository examples or your memory might be older than the current MCP or VS Code surface.

## When to use this file

- The chosen SDK API seems newer than the examples in this skill.
- The task touches Streamable HTTP, apps, sandboxing, trust, or VS Code registration details.
- You need the official documentation index before drilling into a specific SDK or host reference.

## Current official sources

- MCP docs index: https://modelcontextprotocol.io/llms.txt
- MCP intro: https://modelcontextprotocol.io/docs/getting-started/intro
- MCP architecture: https://modelcontextprotocol.io/docs/learn/architecture
- VS Code "Add and manage MCP servers": https://code.visualstudio.com/docs/copilot/customization/mcp-servers
- VS Code MCP configuration reference: https://code.visualstudio.com/docs/copilot/reference/mcp-configuration
- VS Code agent tools: https://code.visualstudio.com/docs/copilot/agents/agent-tools
- SDK repositories live in [URIs](./URIs.md).

## Notes confirmed while editing this skill

- The MCP website publishes `llms.txt` as the documentation index for current pages.
- VS Code documents tools, resources, prompts, and MCP apps as distinct client-facing capabilities.
- VS Code documents sandboxing for local stdio servers on macOS and Linux.
- VS Code local server examples may omit `type` when `command` is present, even though this repository usually keeps `type: stdio` explicit for readability.

## Re-check triggers

- Re-check before copying SDK code verbatim.
- Re-check when the client surface mentions a capability not covered by the examples in this skill.
- Re-check when a remote transport or auth flow looks different from local stdio examples.