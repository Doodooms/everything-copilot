---
id: copilot
description: Use Copilot CLI to send a bounded request to a Codex session.
invoke_for:
- request a concise status or response from a known Codex session
- perform an authorized Copilot-to-Codex workflow check
avoid_for:
- resume or modify a Codex session without explicit authorization
- broad delegation or copying full conversation history
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
## Step 1 - Read both harness procedures

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then DO read `./codex.md` first; this cross-read is required before using Codex CLI.
2. Choose either a verified existing Codex session or a new, independent one-shot consultation; never imply the latter continues an existing session.
3. For an existing session, DO verify its exact name or UUID from the caller's handoff or `codex agents`. `codex agents` is an interactive TUI; if the host has no TTY, request a terminal or exact session identity and do not send automated keypresses to an unverified UI.

## Step 2 - Contact Codex once

1. Before invoking Codex, follow the `harness-distribution` procedure in `./harness-distribution.md` and capture a fresh Codex budget snapshot for the call. If its allowance is exhausted, stale, or unknown, do not invoke the CLI; report `blocked before contact` and defer until a fresh observation is available.
2. Use #tool:bash for one verified Codex CLI command. For an existing session, DO use `codex queue --thread "<exact session name or UUID>" --message "<bounded request>"`. If a prior request is still pending, DO NOT queue a duplicate.
3. For a new isolated consultation, DO use `codex exec --ephemeral --ignore-user-config --sandbox read-only --json -C "<working root>" "<bounded request>"`; limit the prompt to the named task and necessary files.
4. For a status-only request, explicitly forbid file changes and additional work.
5. DO NOT use `codex resume` as a messaging shortcut; it continues the target session and may affect ongoing work.
6. If the budget check, Copilot's tool policy, or Codex CLI blocks the call, report `blocked before contact`; DO NOT broaden permissions or retry through another shell path.
7. Record the exact command/result. A queue acknowledgement is `queued`, not `answered`; a one-shot response is independent and not evidence of another session's status.

## Step 3 - Verify and report

1. For a queued request, DO inspect the target with `codex agents` only when an interactive terminal is available and only to verify status/response.
2. If the session is inactive or no reply is visible, report that the message is pending; do not queue duplicates automatically.
3. Return the exact target or one-shot mode, command/result, reply evidence, and any remaining uncertainty to the caller.
</workflow>
