---
id: smart-compact
description: Observe active-harness context use and choose a safe, evidence-based compaction point.
invoke_for:
- deciding whether the active context window needs compaction before another major phase
- preserving a validated task handoff before a supported session boundary
avoid_for:
- measuring provider allowance, billing credits, or another private session
- claiming a local file projection is the active conversation token count
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
## Step 1 - Read the active host's context surface.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Query only the current harness through its documented status interface:
   - Codex CLI: `/status`; use `/compact` only when compaction is the chosen action.
   - Copilot CLI: `/context` for the active context window. `/usage` is per-session usage, not the context-window reading.
2. Record the harness, exact command/surface, observation time, used tokens, total capacity, and any host-reported remaining space or buffer. Mark each unavailable value `unknown`; do not inspect private session databases or target a different session.
3. If the host status surface cannot be queried from this execution context, ask the caller for its output or continue with `unknown`. `context-management`'s `token-optimization` workflow measures selected local files only.

## Step 2 - Estimate the next safe unit of work.

1. Identify the next phase or bounded task that can be completed before another check. Estimate only the files and instructions likely to be loaded using `context-management`'s `token-optimization` workflow; label it `local_estimate` and name its estimator and coverage.
2. Include the durable handoff and expected response/output in the reserve. Prefer a host-published low-space threshold or native compaction behavior when one is exposed. Do not invent a universal token or percentage threshold.
3. If exact remaining capacity is unknown, rely on the host's native context management and set compaction timing to `unknown`; do not derive live occupancy from repository size or characters processed.

## Step 3 - Choose the action at a safe boundary.

1. Continue when the host-reported remaining capacity covers the next bounded phase plus the handoff/output reserve.
2. If it does not, finish or stop at the earliest safe boundary and compact before starting the next phase. Update Control Plane task state only when connected and required by the workflow; otherwise preserve the exact files, decisions, validation, blockers, and next action in the active handoff/session. Do not create local task-history files to prepare for compaction; never compact away state needed to continue safely.
3. Use the host's supported compaction command or native behavior. A successful compact command means the host acted; it does not prove that a new session inherited state.

## Step 4 - Return the observation and decision.

1. Report the source, timestamp, knowledge state (`host_reported`, `local_estimate`, or `unknown`), used/capacity/remaining values when observed, next-phase estimate and method, reserve basis, selected action, and Control Plane handoff reference when one exists. Keep context-window occupancy separate from plan allowance, weekly/rolling usage, and billed credits.
   - Host references:
     - [Codex CLI status and compaction](https://developers.openai.com/codex/cli/slash-commands/)
     - [Copilot CLI context management](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/context-management)
     - [Copilot CLI command reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
</workflow>
