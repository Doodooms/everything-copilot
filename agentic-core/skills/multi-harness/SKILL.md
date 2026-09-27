---
name: multi-harness
description: "WHAT: Coordinate context-aware compaction, budget-aware work distribution, and bounded session communication. USE FOR: live context checks, Copilot/Codex budget snapshots, and authorized same- or cross-harness handoffs. DO NOT USE FOR: general delegation, implementation ownership, quota scraping, or silently resuming another agent."
user-invocable: false
metadata:
  creation-date: "2026-09-27"
  creator: "Doodooms"
license: MIT
---

<definitions>

- **harness handoff** : A concise, explicit request sent from one agent harness to another without assuming shared prompts, memory, or runtime state.
- **queue acknowledgement** : Confirmation that a message was accepted for delivery; it does not prove that the target harness consumed or answered it.
- **one-shot consultation** : A new bounded CLI invocation that returns an independent answer and does not resume an existing session.

</definitions>

<critical_rules>

- MUST treat Copilot and Codex as separate sessions; share only explicit requests, references, deltas, and observed responses.
- MUST identify the exact target session before queueing a message; do not guess names or IDs.
- MUST obtain explicit user authorization before contacting, resuming, interrupting, cancelling, or otherwise mutating an existing session.
- MUST NOT resume, interrupt, cancel, or mutate an existing session without explicit user authorization.
- MUST distinguish identified, queued, consumed, and answered states; a successful CLI exit or queue acknowledgement alone is not proof of consumption or a reply.
- MUST NOT copy entire private prompts or history, expose credentials, or use cross-harness communication to bypass role, repository, or approval boundaries.
- MUST NOT bypass quota, authentication, or tool-policy failures by switching accounts/providers or broadening permissions; report the handoff as blocked before contact.
- MUST keep context-window occupancy, rolling/weekly provider allowance, and billed credits as separate observations with their own units and sources.
- MUST label unavailable or stale host telemetry `unknown`; MUST NOT invent a timer, infer remaining allowance from a previous session, or present a local file estimate as live context use.

</critical_rules>

<general_rules>

- SHOULD send the smallest request that can establish the target task and next action.
- SHOULD prefer an asynchronous queue for an existing Codex session and a separate bounded `copilot -p` invocation when no Copilot session ID was provided.
- SHOULD use a new ephemeral, read-only Codex invocation when no safe existing-session target is available or a prior message is still pending; never report its answer as a reply from that existing session.
- MAY use a shared task artifact as a handoff record, but it is not evidence that another harness read or accepted it.
- A future harness MAY add one matching workflow after its CLI session and messaging capabilities are verified; do not assume the Copilot/Codex procedures generalize automatically.

</general_rules>

<risk_assessment>

Consume the caller-assigned `risk_level`; MUST NOT reclassify or downgrade it. MAY escalate based on evidence of greater impact, uncertainty, or irreversibility. If no risk level was supplied, classify the communication before any stateful contact. A status request is low impact, while resuming a session or issuing a request that can modify files requires explicit authorization. Risk never expands authority.

</risk_assessment>

<rules>

- This skill owns communication mechanics only; the caller retains task ownership and the receiving agent retains its own role and approval constraints.
- Every handoff MUST identify the target harness/session, objective, requested response, applicable no-change constraints, and what counts as completion.
- DO run CLI commands through the selected host's command tool (#tool:bash in Copilot CLI or #tool:execute in Codex); return the actual command result.
- MUST read the receiving harness workflow and then the paired workflow named by that workflow before sending a cross-harness message.
- Copilot → Codex uses [the Copilot workflow](./workflows/copilot.md); Codex → Copilot uses [the Codex workflow](./workflows/codex.md).
- Same-harness Codex status and message coordination uses [same-harness session coordination](./workflows/same-harness-session-coordination.md); it does not resume a thread or contact Copilot.
- When authoring or materially repairing this package, consult the [original specification](./references/original-spec.md) as provenance, not as current task state.
- DO report any unavailable CLI, TTY requirement, ambiguous session, or missing reply as a limitation; DO NOT infer success from a file being open or a message merely being queued.

</rules>

<workflow>

## Step 1 - Select the matching workflow.

1. DO consume the caller-assigned `risk_level`; if none was supplied, classify the communication before any stateful contact. MAY escalate when new evidence warrants it; MUST NOT downgrade.
2. Select only the procedure that matches the request:
   - [smart-compact](./workflows/smart-compact.md) for live context observations and safe compaction timing.
   - [harness-distribution](./workflows/harness-distribution.md) for evidence-based work assignment across providers.
   - [same-harness session coordination](./workflows/same-harness-session-coordination.md) for read-only status checks or an explicitly authorized Codex-to-Codex request.
   - [Copilot](./workflows/copilot.md) or [Codex](./workflows/codex.md) for cross-harness communication; each reads its paired workflow before contact.
3. If the required CLI, exact session identity, or user authorization is missing, stop and report the blocker; do not discover private context through unrelated files.

## Step 2 - Follow the selected procedure.

1. Follow only the selected workflow's verified procedure. If it contacts a session, require explicit user authorization and keep the request bounded.
2. DO state whether file changes are forbidden and ask for a falsifiable response when another session is contacted.
3. DO NOT automatically call back into the origin harness or create a recursive communication loop.

## Step 3 - Verify and return.

1. Check the receiving harness's status/response surface when available.
2. Distinguish `queued`, `in progress`, `answered`, `blocked`, and `unknown`; do not wait or poll indefinitely.
3. Return the exact command/result, target session, evidence of a reply (if any), changed files, and remaining uncertainty.

</workflow>
