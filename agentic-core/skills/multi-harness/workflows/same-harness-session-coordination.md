---
id: same-harness-session-coordination
description: Inspect or contact a known Codex CLI session through the local Codex daemon with bounded, explicit authorization.
invoke_for:
- inspect the status of a known Codex CLI session through the shared local daemon
- send one explicitly authorized, bounded request to a known Codex CLI session
avoid_for:
- communicate with Copilot or another harness
- resume, interrupt, cancel, or modify a session without explicit user authorization
- inspect private session databases or infer that a queued message was consumed
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
## Step 1 - Classify the request and contact boundary.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Use this workflow only for sessions managed by the same local Codex CLI daemon. For Copilot or another harness, select that harness's paired workflow instead.
2. Consume the caller-assigned `risk_level`; if none was supplied, classify the communication before any stateful contact. Do not downgrade the assigned level.
3. Read-only status inspection does not authorize a message. Queueing, resuming, interrupting, or cancelling a session requires explicit user authorization; a task note or old authorization is not current approval.

## Step 2 - Identify the exact target session.

1. Check the installed Codex CLI help when command support is unknown. In the locally verified Codex CLI 0.157.1, `codex agents` opens an interactive TUI for sessions on the shared local app-server daemon; `codex queue --thread` accepts a session UUID or exact session name.
2. Use `codex agents` only when an interactive terminal is available. It can show the session name, state, project, and last-message preview. Do not automate keystrokes, resume the session to inspect it, or search private session databases.
3. Prefer a UUID after confirming the target project and session. If the target is ambiguous or cannot be observed safely, stop and ask for the exact session identity or a fresh status observation.

## Step 3 - Prepare one bounded request.

1. State the target session, objective, expected response, task scope, and any allowed or forbidden file changes. Share only the minimum task identifiers, evidence paths, and deltas needed for that response.
2. For a status-only request, forbid file changes and new work and request a concise response. Do not copy the full conversation, hidden prompts, credentials, or unrelated repository state.
3. Check that no equivalent request is already pending. Do not queue a duplicate to make a response arrive sooner.

## Step 4 - Queue only after authorization.

1. After the user explicitly authorizes contact and the exact target is verified, send one message with the locally verified command:

   ```bash
   codex queue --thread "<exact-session-UUID>" --message "<bounded request with scope and response format>"
   ```

2. Preserve the command result and its timestamp. A successful exit or `Queued message` acknowledgement means only `queued`; it does not prove the session consumed or answered the request.
3. If authorization, target identity, CLI support, or the no-pending check is missing, do not send. Return `blocked before contact` with the missing evidence.

## Step 5 - Verify the message state.

1. When an interactive terminal is available, inspect the exact target with `codex agents` for a later state or response. Do not use `codex resume` as a status check.
2. Record `queued`, `in progress`, `consumed`, or `answered` only when the host visibly supports that conclusion. If the UI shows no reply or consumption signal, preserve `queued` or `unknown`; do not infer a state from elapsed time.
3. Do not poll indefinitely or queue again while the request is pending. If status cannot be checked without a TTY, report that limitation and leave the state `unknown` or `queued` as last observed.

## Step 6 - Return the coordination record.

1. Report the target UUID/name and project, authorization basis, command/result, sent time, last observed state, evidence of any actual reply, changes made by the target if visible, and remaining uncertainty.
2. A shared task artifact may preserve the handoff and resume point, but it is not proof that another session read, accepted, or answered it. Keep task ownership and approval decisions with the caller.
</workflow>
