---
id: create-mcp-rust
description: Implement a small, transport-appropriate Rust MCP server using the pinned official rmcp API.
invoke_for:
- creating or repairing an MCP server in Rust
- choosing rmcp features and transport for a Rust MCP server
avoid_for:
- deploying the server or editing host MCP configuration
- writing a benchmark claim without a measured baseline
references:
- ../references/create-mcp/common-transport-security.md
---
<critical_rules>
- MUST keep work within this subskill’s declared scope and its specific safety or authority constraints.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
</critical_rules>

<general_rules>
- SHOULD load listed references only at the procedure step that needs them.
- MAY report unavailable evidence or unresolved decisions as unknown.
</general_rules>

<risk_assessment>
Consume the Orchestrator-assigned `risk_level` through the parent domain skill; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases risk. Scale evidence depth, not authority or approvals.
</risk_assessment>

<rules>
- MUST follow this selected subskill only within its declared procedure and scope.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Establish the Rust and SDK contract.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Inspect `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`, existing server code, and the target host. Preserve the repo's MSRV and dependency policy.
2. Pin or select the `rmcp` version before writing code. Read that version's official crate docs and matching official server examples; upstream `main` or a different published version is not evidence that an API matches the crate lock.
3. Confirm the tool/resource/prompt names, typed input/output shape, error behavior, state lifecycle, and transport with the caller. Keep the existing product specification authoritative.

## Step 2 - Choose one transport and its minimum features.

1. Choose one transport using [the shared transport and security rules](../references/create-mcp/common-transport-security.md).
2. Inspect the feature table for the pinned `rmcp` version and enable the server plus only the feature set required by that transport. Do not assume feature names or enable defaults without checking.
3. Start from the closest official example for that exact version and remove unused transports, macros, protocol extensions, and optional integrations.
4. Treat transport APIs, feature names, and macro syntax as version-dependent. Link the exact source/version used in the implementation notes and do not present uncompiled pseudocode as an `rmcp` API.

## Step 3 - Implement the smallest typed server.

1. Register only the tools/resources/prompts required by the approved scope. Prefer the SDK's typed parameter and schema mechanism for tool inputs; derive or publish schemas from the same Rust types where supported by the pinned version.
2. Validate constraints at the boundary, return protocol errors for expected failures, and avoid panics for malformed input, unavailable state, cancellation, or I/O errors.
3. Keep state in the narrowest lifetime that satisfies the request. Do not add a database, cache, background task, or shared mutable state until the use case and consistency rules require it.
4. Bound input size, output size, time, and concurrency. Restrict filesystem, process, and network capabilities to the documented operation; never expose secrets in tool results or logs.
5. Make startup, cancellation, and graceful shutdown explicit. For CPU-heavy or blocking work, use the runtime's documented blocking facility and preserve cancellation/deadline behavior.

## Step 4 - Verify protocol behavior and performance claims.

1. Build and lint with the repository's pinned toolchain. Run focused checks for `initialize`, `tools/list`, valid and invalid `tools/call`, serialization, protocol errors, concurrent requests, and clean shutdown over the selected transport.
2. Test boundary sizes and failure paths. For stateful tools, check isolation, ordering, and cleanup; for HTTP, verify the common authorization and origin protections as well.
3. If performance matters, record a representative workload and baseline, then measure cold startup, steady-state latency, throughput, memory, and payload size. Report hardware, toolchain, `rmcp` version/features, and comparison method. Rust alone is not proof of superior performance.
4. Keep performance work bounded to a measured bottleneck. Do not optimize by broadening authority, dropping validation, or adding an unneeded protocol surface.

## Step 5 - Return the host handoff.

1. Return exact `rmcp` version, enabled features, transport, registered MCP names and schemas, run/build commands, test evidence, measured performance data if requested, known limitations, and links to the official sources used.
   - [Official Rust MCP SDK repository and feature list](https://github.com/modelcontextprotocol/rust-sdk/tree/main/crates/rmcp)
   - [Official MCP Rust server guide](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/docs/2026-07-28/develop/build-server.mdx)
   - [Official Rust SDK server examples](https://github.com/modelcontextprotocol/rust-sdk/tree/main/examples/servers)
2. Give `operations` the exact executable/arguments/environment needs for approved host wiring. Do not edit host configuration or install/deploy the server from this workflow.
</workflow>
