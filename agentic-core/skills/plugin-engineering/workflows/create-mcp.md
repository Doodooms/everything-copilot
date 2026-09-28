---
id: create-mcp
description: Implement or repair MCP server code with Rust and the official rmcp SDK.
invoke_for:
- Implement or repair MCP server tools, resources, prompts, or transport entrypoints
- Validate tool names against actual registrations or tools/list
avoid_for:
- Install or deploy an MCP server, manage host configuration, or implement unrelated product features
references:
- ../references/create-mcp/common-transport-security.md
- ../references/create-mcp/scripts/validate_mcp.sh
- ../references/create-mcp/references/URIs.md
---
<critical_rules>
- MUST keep work within this workflow's declared scope and its specific safety or authority constraints.
- MUST implement every new standalone MCP server in Rust using the official `rmcp` SDK.
- MAY use another language only when MCP must execute inside an existing non-Rust process/runtime and a separate Rust service would violate an explicit product or deployment constraint. Record the constraint and justification, then obtain a human checkpoint before implementation; this is an architectural exception, not a language-selection path.
- MUST NOT claim Rust performance advantages quantitatively without a representative measured comparison.
- MUST NOT replace the parent domain skill's admission, global routing, or authority boundaries.
</critical_rules>

<general_rules>
- SHOULD load listed references only at the procedure step that needs them.
- MAY report unavailable evidence or unresolved decisions as unknown.
</general_rules>

<risk_assessment>
Consume the Orchestrator-assigned `risk_level` through the parent domain skill; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases risk. Scale evidence depth, not authority or approvals.
</risk_assessment>

<rules>
- MUST follow this workflow only within its declared procedure and scope.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>

## Step 1 - Inspect the repository and MCP contract

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then locate relevant MCP entrypoints, dependency manifests and lockfiles, tool registrations, host requirements, and existing tests.
2. Preserve the repository's MSRV, Rust toolchain, dependency, and operational policies. For an existing non-Rust server, establish whether it is an approved architectural exception before changing its implementation language.

## Step 2 - Confirm capabilities and authority

1. Confirm the requested tools, resources, prompts, typed input/output shapes, error behavior, state lifecycle, caller authority, runtime constraints, host, and deployment boundary from the request and repository evidence.
2. Derive published tool names from actual registrations or `tools/list`; do not invent aliases or expand protocol capabilities without approval.
3. Ask the user or Orchestrator only for an unresolved decision that materially changes the implementation; do not begin dependent work until it is resolved.

## Step 3 - Establish the Rust and `rmcp` contract

1. Before implementation, select and pin an exact published `rmcp` version compatible with the repository toolchain and dependency policy.
2. Read the official crate documentation, feature list, and server examples matching that exact version. The current upstream branch or documentation for another version is not evidence of API compatibility. Use [the official source index](../references/create-mcp/references/URIs.md) to locate matching versioned material.
3. Record the exact `rmcp` version and the matching documentation/example references used. Do not present uncompiled pseudocode as a verified `rmcp` API.

## Step 4 - Choose exactly one transport

1. Apply [the shared transport and security rules](../references/create-mcp/common-transport-security.md). Select `stdio` when the client starts a local child process, or Streamable HTTP when clients require a network transport and the deployment boundary supports it.
2. Do not enable another transport or protocol extension without an approved use case.

## Step 5 - Select only required `rmcp` features

1. Inspect the feature table for the pinned version. Enable server support and only the feature set needed by the chosen transport and approved capabilities; verify defaults instead of assuming them.
2. Start from the closest official server example for that exact version. Remove unused transports, macros, protocol extensions, and optional integrations.

## Step 6 - Implement the smallest typed MCP server

1. Register only the approved tools, resources, and prompts. Prefer the pinned SDK's typed parameter and schema mechanism; derive or publish schemas from the same Rust types where supported.
2. Validate constraints at the protocol boundary. Return protocol errors for expected failures; do not panic on malformed input, unavailable state, cancellation, or I/O errors.
3. Keep state in the narrowest lifetime that satisfies the request. Do not add a database, cache, background task, or shared mutable state until the use case and consistency rules require it.
4. Bound input size, output size, execution time, and concurrency. Restrict filesystem, process, and network capabilities to the documented operation. Keep credentials out of source, results, command arguments, and logs.
5. Make startup, cancellation, and graceful shutdown explicit. Use the runtime's documented blocking facility for CPU-heavy or blocking work while preserving cancellation and deadlines.

## Step 7 - Apply shared security and capability boundaries

1. Follow the shared reference for the minimum capability surface, secret handling, and transport-specific security. Security requirements remain independent of Rust and `rmcp`.
2. For Streamable HTTP, verify authentication and origin protections against the selected deployment boundary. For `stdio`, keep protocol frames on stdout and diagnostics on stderr.

## Step 8 - Validate protocol behavior and failure paths

1. Build and lint with the repository's pinned toolchain. Exercise `initialize`, `tools/list`, valid and invalid `tools/call`, serialization, expected protocol errors, concurrent requests, and clean shutdown over the selected transport.
2. Test boundary sizes, cancellation, and relevant failure paths. For stateful tools, check isolation, ordering, and cleanup. For HTTP, validate authorization and origin protections.
3. Validate this workflow package with `references/create-skill/scripts/validate.py --skill-dir agentic-core/skills/plugin-engineering` and run `bash agentic-core/skills/plugin-engineering/references/create-mcp/scripts/validate_mcp.sh`. These checks do not replace tests of the generated server.

## Step 9 - Measure performance only when a performance claim matters

1. If performance is a requirement or a quantitative claim will be made, record a representative workload and baseline. Measure cold startup, steady-state latency, throughput, memory, and payload size as applicable.
2. Report hardware, toolchain, pinned `rmcp` version and features, and comparison method. Rust alone is not evidence of superior performance. Keep optimization bounded to measured bottlenecks; do not broaden authority or drop validation to improve a metric.

## Step 10 - Return the exact host and deployment handoff

1. Report the selected language (including any approved exception), exact `rmcp` version, enabled features, transport, registered MCP names and schemas, run/build commands, tests and results, security boundary, measured performance evidence if requested, limitations, and official references used.
2. If host integration is required, give `operations` the exact executable, arguments, environment needs, and published tool names. Do not edit host configuration or install/deploy the server from this workflow.
</workflow>
