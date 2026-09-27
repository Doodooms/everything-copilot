# Common MCP transport and security rules

Used by the `create-mcp` and `create-mcp-rust` workflow subskills. Keep these shared rules here; each workflow should add only language- or SDK-specific details.

## Keep the server surface bounded

- Implement only the tools, resources, and prompts approved for the use case. Preserve the caller's authorization boundary and expose the minimum required capability.
- Validate input at the protocol boundary. Bound payload size, execution time, and concurrency; handle cancellation and expected failures without exposing secrets or internal details.
- Keep credentials out of source, command arguments, results, and logs. Use the host's approved secret delivery mechanism and grant only the required account or installation permissions.
- Enable a server's read-only mode when the requested use case requires read-only access, and verify its advertised tool list reflects that boundary.

## Select and secure one transport

- Use `stdio` when the client starts a local child process. Read protocol messages from stdin and write protocol frames to stdout; write diagnostics to stderr.
- Use Streamable HTTP only when clients need a network transport. Validate each supplied `Origin` header and reject invalid origins with HTTP 403. When the server runs locally, bind to loopback. Implement authentication appropriate to the trust boundary and require it for non-local deployments, following the MCP authorization specification.
- Do not expose a local server on all network interfaces or enable additional transports without an approved use case.

## Primary sources

- [MCP 2025-11-25 transport specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)
- [MCP 2025-11-25 authorization specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)
