# Rust MCP server patterns

Load this reference from the selected implementation step in `create-mcp`. It records implementation choices and failure modes without prescribing an `rmcp` API; use the exact pinned crate documentation and example for code.

## Choose only the required MCP surface

| Primitive | Use when | Keep the contract narrow |
| --- | --- | --- |
| Tool | The client asks the server to perform an operation | Typed arguments, explicit side effects, bounded result and execution |
| Resource | The client needs to read content by URI | Stable URI meaning, access checks, bounded content and freshness |
| Prompt | The client needs a reusable message template | Explicit arguments and predictable rendered messages |

Names and schemas must come from the implemented registration. Do not add aliases or capabilities merely because an SDK can expose them. Derive input schemas from the same types used by handlers where the pinned SDK supports that pattern; validate semantic constraints and authority at the request boundary as well.

**GOOD:** expose `read_report` as a bounded read tool with an explicit report identifier and caller authorization.

**BAD:** expose a generic `run_anything` tool whose arguments select arbitrary paths, processes, or network destinations.

## Keep state at the lifecycle the contract requires

- Prefer stateless request handling when no cross-request state is required.
- Make resource ownership explicit: request-local, process-local, durable storage, or caller-provided handle. A process-local object is not a durable task/session store.
- Add shared mutation, a database, cache, queue, or background worker only when a concrete consistency and lifecycle requirement needs it.
- Define ordering, isolation, cleanup, and behavior after restart for any state that crosses a request boundary.

**GOOD:** copy a small snapshot under a lock, release the guard, then await filesystem or network work using the snapshot.

**BAD:** hold a shared lock across an unbounded network operation, or use an in-memory session map as durable state without restart and cleanup semantics.

## Bound asynchronous work and errors

- Use the runtime and handler types documented by the pinned `rmcp` release. Keep blocking CPU or I/O work off an async executor thread when it can block other requests.
- Apply explicit deadlines, cancellation propagation, input/output limits, and a concurrency bound to expensive operations.
- Separate expected protocol-level failures (invalid arguments, missing resource, denied operation) from internal or infrastructure failures. Preserve diagnostic context in private logs; return only the protocol error suitable for the caller.
- Never panic on malformed input, missing state, cancellation, or ordinary I/O failure. Avoid returning raw exception/error strings that may expose paths, credentials, or internals.

**GOOD:** reject a missing or unauthorized resource with the corresponding documented error and keep the internal lookup detail in protected diagnostics.

**BAD:** unwrap user-controlled parsing, return a storage error verbatim, or report every failure as a successful result containing an error string.

## Test the published contract over the selected transport

Exercise only protocol versions the server claims to support. For MCP `2026-07-28`, test requests with per-request metadata; `server/discover` is optional. Exercise `initialize` only for a supported legacy version that requires it. Do not use an older handshake as a universal server test.

Cover the relevant behaviors:

- actual registered tool, resource, and prompt names and schemas;
- valid input, malformed/invalid input, unknown names or URIs, authorization denial, and expected error mapping;
- result serialization and payload limits;
- cancellation, deadlines, concurrent calls, and state isolation when applicable;
- startup, clean shutdown, and restart behavior for any process or durable state;
- `stdio`: frames remain on stdout and diagnostics go to stderr;
- Streamable HTTP: authentication, invalid-Origin rejection, local loopback binding, and request cancellation when the client closes an SSE response stream.

Do not claim a test passed merely because a handler unit test passed; test the protocol surface when integration behavior is part of the contract.

## Keep host and performance claims evidence-based

The server workflow owns server code and contract tests. Host registration, packaging, and deployment instructions belong to the host's operations workflow. Return exact executable, arguments, environment needs, and advertised names when handing off integration.

Measure performance only when it is a requirement or a quantitative claim is requested. Use a representative workload and record toolchain, `rmcp` version/features, transport, hardware, cold startup, steady-state latency, throughput, memory, and payload size as relevant. The language choice alone is not performance evidence.
