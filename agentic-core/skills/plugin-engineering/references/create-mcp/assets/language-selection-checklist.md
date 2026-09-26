# MCP Language Selection Checklist

Use this quick checklist before proposing an implementation language:

- Choose Go when the user needs a reliable default, strong performance, and a single deployable binary.
- Choose Rust when performance, memory control, or security guarantees are critical to the outcome.
- Choose Python when the user wants the fastest path to a working prototype.
- Only choose Node.js when the user explicitly asks for Node.js or must stay inside an existing Node-only ecosystem.
- Clarify transport separately: `stdio` for local clients, Streamable HTTP for remote deployments.
- Pin the SDK version before writing examples because MCP APIs evolve quickly.