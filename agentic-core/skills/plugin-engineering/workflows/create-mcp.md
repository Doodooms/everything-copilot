---
id: create-mcp
description: Implement or repair MCP server code using a verified SDK and exact registered tools.
invoke_for:
- Implement or repair MCP server tools, resources, prompts, or transport entrypoints
- Choose an MCP SDK language or transport based on approved constraints
- Validate tool names against actual registrations or tools/list
avoid_for:
- Install or deploy an MCP server, manage host configuration, or implement unrelated product features
references:
- ../references/create-mcp/assets/language-selection-checklist.md
- ../references/create-mcp/common-transport-security.md
- ../references/create-mcp/scripts/validate_mcp.sh
- ../references/create-mcp/references/URIs.md
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
## Step 1 - Inspect MCP entrypoints and repository state

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Use #tool:search to locate MCP server entrypoints and stale server-code references when the repository already contains MCP code or was recently renamed.
2. Read the relevant server entrypoints, dependency lockfile, registered names, host requirements, and existing tests directly.

## Step 2 - Confirm the required contract

1. Confirm the requested tools, resources, prompts, input/output contracts, authority, runtime constraints, host, and transport from the request and repository evidence.
2. Ask the user or Orchestrator only for an unresolved decision that materially changes the implementation; do not start dependent code until it is resolved.

## Step 3 - Choose the language and SDK

1. Apply the [language selection checklist](../references/create-mcp/assets/language-selection-checklist.md); consult [official SDK references](../references/create-mcp/references/URIs.md) and verify the exact pinned SDK version.
2. If Rust is selected after this workflow was loaded, stop before writing Rust code and route to the sibling workflow at `workflows/create-mcp-rust.md` for its version-specific `rmcp` procedure.

## Step 4 - Choose one transport

1. Apply [the shared transport and security rules](../references/create-mcp/common-transport-security.md) and select the transport required by the client and deployment boundary.

## Step 5 - Implement the approved server surface

1. Use the selected SDK's official documentation and examples for the pinned version; do not copy an API from a different version.
2. Implement only the requested tools, resources, prompts, and one transport. Derive published tool names from registrations or `tools/list`; do not invent aliases or expand the protocol surface without approval.
3. Keep capability logic separate from transport-specific wiring where the SDK permits; start with the smallest implementation that proves the required behavior, then add only the remaining approved capabilities.

## Step 6 - Validate protocol behavior

1. Build and lint with the repository's pinned toolchain; verify initialization, `tools/list`, valid and invalid calls, serialization, expected failures, and clean shutdown over the selected transport.
2. Validate the parent package's workflow metadata and contained references with `references/create-skill/scripts/validate.py`; run the [MCP-specific scaffold check](../references/create-mcp/scripts/validate_mcp.sh) with `bash agentic-core/skills/plugin-engineering/references/create-mcp/scripts/validate_mcp.sh`. Neither check replaces tests of the generated server.
3. If host integration is required, return the exact transport, command, arguments, environment needs, and published tool names to `operations`; do not edit host configuration.

## Step 7 - Return the implementation handoff

1. Report the SDK version, transport, registered names, commands, test evidence, changed files, security boundary, and any unverified runtime behavior.
</workflow>
