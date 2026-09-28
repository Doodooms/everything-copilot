# Official MCP and Rust SDK sources

Use these primary sources to confirm protocol requirements and the official Rust SDK implementation. Before coding, replace `<PINNED_VERSION>` with the exact selected `rmcp` release and use its matching docs and examples; `latest` and the upstream default branch can describe a different API.

- [MCP specification and documentation](https://modelcontextprotocol.io/specification/)
- [Official Model Context Protocol Rust SDK (`rmcp`) repository](https://github.com/modelcontextprotocol/rust-sdk)
- [Official `rmcp` crate documentation](https://docs.rs/rmcp/)
- [Official Rust SDK releases and tags](https://github.com/modelcontextprotocol/rust-sdk/releases)
- [Official Rust SDK server examples](https://github.com/modelcontextprotocol/rust-sdk/tree/main/examples/servers)

For exact-version API documentation, use `https://docs.rs/rmcp/VERSION/rmcp/` with `VERSION` replaced by the selected crate version. Verify that the selected feature flags, transport APIs, macros, schema types, and example code match the pinned release. When the release provides a matching tag, inspect that tag's examples rather than assuming the current `main` examples apply. Preserve the repository's Rust toolchain and MSRV policy.
