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

## Step 1 - Confirm a deterministic hook is the right primitive.

1. DO consume the assigned `risk_level`; identify the lifecycle event, trigger condition, desired deterministic action, input source, failure behavior, and exact scope.
2. Use a hook only for supported lifecycle enforcement or automation; route reusable model guidance to a skill and new server capability to MCP.
3. Consult the current host hook schema only when the supported event or configuration is uncertain.

## Step 2 - Author the hook and its smallest companion.

1. Write the hook JSON with the documented event, command, timeout, and platform fields; add a self-contained companion script only when required.
2. Make allow/block behavior explicit, keep permissions narrow, and surface actionable errors; MUST NOT add secrets or broad unrelated automation.

## Step 3 - Validate and hand off.

1. Validate JSON/schema and exercise the relevant event or a faithful harness; report actual results and any host-specific behavior not exercised.
2. Return paths, event/action contract, tests, blockers, and residual risk; do not install or enable hooks without authorization.
