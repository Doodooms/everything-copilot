---
id: codex
description: Use Codex CLI to make a bounded request to Copilot.
invoke_for:
- request a concise Copilot answer through a new non-interactive invocation
- perform an authorized Codex-to-Copilot workflow check
avoid_for:
- resume or modify a Copilot session without explicit authorization
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

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then DO read `./copilot.md` first; this cross-read is required before using Copilot CLI.
2. Inspect `copilot --help` only when the installed CLI version or option support is unknown.
3. Copilot CLI's `sessions` command currently exposes `import`, not session listing. DO NOT claim `copilot sessions list` works or infer an active session from an open editor file.

## Step 2 - Choose a safe Copilot contact mode

1. Before invoking Copilot, follow the `harness-distribution` procedure in `./harness-distribution.md` and capture a fresh Copilot allowance snapshot for the call. If its allowance is exhausted, stale, or unknown, do not invoke the CLI; report `blocked before contact` and defer until a fresh observation is available.
2. Use #tool:execute for one bounded CLI invocation. For an independent answer, DO use `copilot --prompt "<request>"` with the necessary plugin and the narrowest available tools.
3. Treat the result as a new Copilot response, not a continuation of the user's active Copilot session.
4. Resume an existing Copilot session only when the user explicitly authorizes it and supplies or confirms its exact session ID; `--resume` continues that session and can change its state.
5. DO NOT guess a session ID, inspect local session databases, or use `--continue` to select a session implicitly.
6. If the budget check, Copilot CLI, authentication, or tool policy blocks the call, report `blocked before contact`; DO NOT change accounts/providers or broaden permissions to force delivery.

## Step 3 - Verify and report

1. DO record the exact Copilot CLI options, result, session ID if explicitly provided, and whether the response came from a new or resumed session.
2. If no existing-session contact method is available or authorized, report the limitation and use a shared handoff artifact only as a reference, not as proof of receipt.
3. Return the response and its origin to the Codex caller; do not automatically create a recursive Copilot-to-Codex call.
</workflow>
