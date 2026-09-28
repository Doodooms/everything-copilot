# Common MCP transport and security rules

Used by the `create-mcp` workflow. Keep transport and security rules here so they remain independent of implementation language and SDK. Confirm the exact protocol and SDK revision through the [official source index](./references/URIs.md).

## Keep the server surface bounded

- Implement only the tools, resources, and prompts approved for the use case. Preserve the caller's authorization boundary and expose the minimum required capability.
- Validate input at the protocol boundary. Bound payload size, execution time, and concurrency; handle cancellation and expected failures without exposing secrets or internal details.
- Keep credentials out of source, command arguments, results, and logs. Use the host's approved secret delivery mechanism and grant only the required account or installation permissions.
- Enable a server's read-only mode when the requested use case requires read-only access, and verify its advertised tool list reflects that boundary.

## Select and secure one transport

- Use `stdio` when the client starts a local child process. Read protocol messages from stdin and write protocol frames to stdout; write diagnostics to stderr.
- Use Streamable HTTP only when clients need a network transport. Validate each supplied `Origin` header and reject invalid origins with HTTP 403. When the server runs locally, bind to loopback. Implement authentication appropriate to the trust boundary and require it for non-local deployments, following the MCP authorization specification.
- Do not expose a local server on all network interfaces or enable additional transports without an approved use case.

## Match protocol lifecycle to the supported version

- MCP `2026-07-28` uses per-request metadata and has no `initialize`/`initialized` handshake or transport-level session. `server/discover` is an optional discovery request, not a required startup handshake.
- Earlier protocol versions may require `initialize` and define different Streamable HTTP session behavior. Support those only when compatibility is an explicit requirement.
- Tests and implementation instructions MUST name the supported protocol version(s). Do not require `initialize` for every server or apply the modern lifecycle to a legacy version.

For 2026-07-28 Streamable HTTP, the server has a single MCP endpoint and each client request is a POST; responses may be JSON or request-scoped SSE. For a request that receives an SSE response, closing that request-scoped SSE response stream signals cancellation. Do not copy the older standalone GET stream, session, `Last-Event-ID`, or HTTP+SSE behavior into a modern transport implementation.

## Primary sources

- [MCP 2026-07-28 transport specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports)
- [MCP 2026-07-28 Streamable HTTP specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)
- [MCP 2026-07-28 authorization specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)
