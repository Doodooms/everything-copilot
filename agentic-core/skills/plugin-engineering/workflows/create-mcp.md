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
- ../references/create-mcp/rust-server-patterns.md
- ../references/create-mcp/references/URIs.md
- ../references/create-mcp/scripts/validate_mcp.sh
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
- MUST return the implementation or repair, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Inspect the repository and deployment boundary
1. DO consume the assigned `risk_level`; locate MCP entrypoints, manifests and lockfiles, registrations, host constraints, existing tests, Rust toolchain, and MSRV policy.
2. For an existing non-Rust server, establish whether the approved architectural exception applies before changing its language.

## Step 2 - Define the approved MCP surface
1. Confirm requested tools, resources, prompts, schemas, error behavior, caller authority, state lifetime, runtime limits, host, and deployment boundary from the request and repository evidence.
2. Derive published names from actual registrations or `tools/list`; stop for a human decision when an unresolved choice materially changes authority or deployment.

## Step 3 - Pin the SDK and protocol contract
1. Select an exact published `rmcp` version compatible with the repository toolchain and dependency policy. Consult [the official source index](../references/create-mcp/references/URIs.md) for matching versioned docs, features, and server examples.
2. Record the crate version, required features, and target MCP protocol versions. Do not use `latest`, another release's examples, or uncompiled pseudocode as proof of API compatibility.

## Step 4 - Select transport and implementation patterns
1. Choose one transport: `stdio` for a client-launched local process, or Streamable HTTP when network access is required and its trust boundary is supported.
2. Apply [the shared transport and security rules](../references/create-mcp/common-transport-security.md) and load [Rust server patterns](../references/create-mcp/rust-server-patterns.md) for capability selection, typed boundaries, state, errors, and test coverage.

## Step 5 - Implement the smallest bounded server
1. Register only approved tools, resources, and prompts using the pinned SDK's documented typed/schema mechanism. Keep state at the narrowest lifecycle that satisfies the contract.
2. Bound input/output size, execution time, and concurrency; constrain filesystem, process, and network access to the approved operation. Handle expected failures and cancellation without panics or secret/internal-detail leakage.
3. Make startup, graceful shutdown, and transport framing explicit. Keep protocol frames on stdout and diagnostics on stderr for `stdio`.

## Step 6 - Validate and hand off
1. Run the repository's pinned Rust formatting, lint, build, and test commands. Test actual registrations, valid and invalid requests, expected errors, and applicable limits, cancellation, state isolation, and cleanup.
2. Exercise protocol lifecycle only for the versions supported: the `2026-07-28` revision has no `initialize` handshake or transport session; `server/discover` is optional. Test `initialize` only when supporting a legacy revision that requires it.
3. For Streamable HTTP, verify authentication, Origin rejection, and loopback binding where local. From the repository root, run `bash agentic-core/skills/plugin-engineering/references/create-mcp/scripts/validate_mcp.sh`; this package check does not replace server tests.
4. Return the language and any approved exception, exact crate version/features, protocol versions, transport, registered names/schemas, run/build commands, validation evidence, trust boundary, measured performance only when required, and unresolved risks. Route host configuration or deployment to `operations`.
</workflow>
