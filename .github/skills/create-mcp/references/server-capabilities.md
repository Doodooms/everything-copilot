# MCP Server Capabilities

## Purpose

- Use this file when you need to decide which MCP features the server should expose, or when the request says the server should be complete, full-featured, or one-shot.

## Capability selection

- Use a **tool** for actions, mutations, or parameterized queries the client must invoke.
- Use a **resource** for read-only context the user should attach to chat without executing a tool.
- Use a **prompt** for repeatable workflows or reusable instructions triggered as `/server.prompt`.
- Use an **app** when the client experience benefits from interactive UI rather than plain text.

## Client surface in VS Code

- Tools appear in chat tool selection and may require confirmation.
- Resources are attached through **Add Context** > **MCP Resources** or the **MCP: Browse Resources** flow.
- Prompts are invoked as `/server.prompt`.
- Apps render inline only when the client supports MCP apps.

## Good selection patterns

- Read-only docs, tables, or configuration snapshots -> resource.
- Safe reusable operations with clear inputs -> tool.
- Standardized analyst or operator playbooks -> prompt.
- Forms, visualizers, or guided workflows -> app.

## Bad selection patterns

- Do not expose a write-capable tool when a read-only resource satisfies the request.
- Do not add prompts when the workflow is not reusable.
- Do not promise apps for clients that do not render them.
- Do not treat auth or transport as a capability; they are cross-cutting constraints that shape implementation.

## Output checklist

- Name the exact capability set the server will expose now.
- Name the user-facing tool, resource, prompt, or app identifiers.
- State any read-only versus mutating boundaries.
- State whether the chosen client can actually surface each selected capability.