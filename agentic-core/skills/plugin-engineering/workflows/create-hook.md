---
id: create-hook
description: Author a deterministic hook for agent lifecycle policy or automation.
invoke_for:
- Block or gate specific tool calls with a lifecycle hook
- Inject approved context at session start or automate a deterministic action
- Configure a companion script for an approved hook event
avoid_for:
- Ordinary model instructions, skills, MCP tools, or product runtime hooks
references: []
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
## Step 1 - Confirm a deterministic hook is the right primitive.

1. DO consume the assigned `risk_level`; identify the target host/harness and version, lifecycle event, trigger condition, deterministic action, input source, failure behavior, and exact scope.
2. Use a hook only for supported lifecycle enforcement or automation; route reusable model guidance to a skill and new server capability to MCP.
3. Check the target host's current official hook documentation for event availability, configuration location, version/preview status, command environment, stdin/stdout contract, and supported output fields. For VS Code, use the [agent hooks documentation](https://code.visualstudio.com/docs/agent-customization/hooks); do not assume its schema applies to another harness.

## Step 2 - Author the hook and its smallest companion.

1. Write the hook JSON with only the fields documented for the selected host and event; add a self-contained companion script only when required.
2. Read event data only through the documented input channel and emit only supported output fields. Make allow/block behavior and timeout behavior explicit; account for a remote extension host when choosing platform-specific commands.
3. Keep permissions narrow, avoid secrets and broad unrelated automation, and make repeated execution safe when the event can fire more than once.

## Step 3 - Validate and hand off.

1. Validate JSON against the selected host's current schema. When a companion script exists, test its allow, block, and timeout paths; also test malformed input when the script accepts input.
2. Exercise the actual lifecycle event when a supported host is available; otherwise report the exact substitute harness and what remains unverified.
3. Return paths, target host/version, event and input/output contract, validation evidence, blockers, and residual risk; do not install or enable hooks without authorization.
</workflow>
