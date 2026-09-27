# MCP Language Selection Checklist

Use this checklist before selecting a language or SDK:

- Preserve the repository's existing language, toolchain, and operational model when they meet the request; avoid a cross-language rewrite without a concrete need.
- Compare maintained MCP SDKs against the required protocol version, transport, runtime, host, packaging, and team support. Verify those capabilities in the exact SDK version before choosing.
- Apply user-stated latency, memory, deployment, and security constraints to the implementation. A language choice alone does not establish performance or security.
- Prefer a language the team can maintain when no stronger constraint decides the choice. Ask the user or Orchestrator only when an unresolved choice materially changes the implementation.
- Select the transport separately using `../common-transport-security.md`.
- Pin the SDK version and consult its matching official documentation and examples before writing implementation code.
