# Official MCP and Rust SDK sources

Use primary, version-matched sources to verify protocol requirements and the Rust SDK API. The source URLs below locate evidence; they do not select a dependency version for a project.

## MCP protocol

- [Current stable MCP specification index](https://modelcontextprotocol.io/specification/)
- [MCP 2026-07-28 transport specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports)
- [MCP 2026-07-28 Streamable HTTP specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)
- [MCP 2026-07-28 authorization specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)
- [MCP 2026-07-28 release notes](https://blog.modelcontextprotocol.io/posts/2026-07-28/)

The 2026-07-28 revision is stateless at the transport layer: it retires the `initialize`/`initialized` handshake and `Mcp-Session-Id`; `server/discover` is optional. Earlier protocol revisions retain their own compatibility behavior. Check the protocol version and behavior the project actually supports instead of requiring one lifecycle for every implementation.

## Official Rust SDK (`rmcp`)

- [Official Model Context Protocol Rust SDK repository](https://github.com/modelcontextprotocol/rust-sdk)
- [Official Rust SDK releases and tags](https://github.com/modelcontextprotocol/rust-sdk/releases)
- [Official Rust SDK server examples](https://github.com/modelcontextprotocol/rust-sdk/tree/main/examples/servers)
- Exact-version API form: `https://docs.rs/rmcp/<PINNED_VERSION>/rmcp/`

At the audit date (2026-09-28), docs.rs listed `rmcp` 3.4.1, published 2026-09-23. Its exact-version docs are [here](https://docs.rs/rmcp/3.4.1/rmcp/), including the [feature table](https://docs.rs/crate/rmcp/3.4.1/features). This is an observation for revalidation, not a default version for future projects.

Before implementation:

1. Select the exact published crate version allowed by the repository's Rust toolchain, MSRV, and dependency policy.
2. Read that version's crate docs, feature table, changelog/migration notes, and server example. Prefer an example from the matching SDK tag; use `main` only to locate concepts, never to establish API compatibility.
3. Verify every feature flag, macro, schema type, transport, lifecycle, and code sample against the pinned version and project lockfile.
4. Record the source version and references used. If the matching API cannot be verified, report the uncertainty instead of providing plausible-looking pseudocode.
