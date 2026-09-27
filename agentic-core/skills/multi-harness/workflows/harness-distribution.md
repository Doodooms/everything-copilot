---
id: harness-distribution
description: Assign bounded work across harnesses from fresh usage evidence and task fit.
invoke_for:
- distributing task slices across Codex, Copilot, or another explicitly supported harness
- checking provider usage before a costly cross-harness dispatch
avoid_for:
- checking live context-window occupancy (use smart-compact)
- inferring quota from prior sessions, provider comparison, or token estimates
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
## Step 1 - Capture separate, fresh provider snapshots.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Check at task start, before each expensive or cross-harness dispatch, and at meaningful phase boundaries. Do not claim a timer or periodic monitor exists.
2. Query only an authorized, documented surface for the named harness. For Codex CLI, `/status` and the account usage dashboard may expose plan limits, including rolling five-hour and weekly windows depending on plan. For Copilot CLI, `/usage` reports session totals; account settings report plan-cycle AI-credit usage. Do not project Codex windows onto Copilot.
3. For each provider/window record `used`, `remaining`, `limit`, `reset_at`, unit, source, and `observed_at`. Mark unavailable fields `unknown`; context tokens, allowance units, and AI credits are different measures.
4. If a status surface is unavailable in this session, use only a fresh user-provided observation or leave the snapshot unknown. Never inspect private databases, credentials, or another session's history.

## Step 2 - Match work to task fit and observed capacity.

1. Keep the user's routing preference as the default: Codex for large/heavy implementation and analysis; use Copilot sparingly for bounded orchestration or work where it offers a clear fit.
2. Override that default only when a fresh snapshot and task-affinity evidence support it. Do not equate token-window size with remaining plan allowance or assume provider cost ratios.
3. Before dispatch to another session or a one-shot provider call, check that the selected harness is authorized, available, and has enough observed budget for the bounded task. If remaining allowance is zero, stale, or unknown, do not launch that external call; split or defer it, continue work inside the already-authorized active session when appropriate, or ask for a fresh observation.
4. Never switch accounts, create credentials, raise limits, or route around a quota/authentication failure. A queued message or successful CLI exit is not proof that the target ran or replied.

## Step 3 - Recheck and preserve the decision.

1. Refresh observations before changing the planned workload after a long phase, quota warning, model change, or provider error. Use current evidence rather than carrying old remaining counts forward.
2. Record the selected harness, task slice, observation source/time, knowledge state, reason, and any blocked/deferred work. Omit personal allowance amounts from long-lived records unless needed for the immediate handoff.
3. Return unknowns and the exact next check point. Never claim that automatic cross-harness balancing is active unless the host actually performed it.
   - Host references:
     - [Codex plan usage](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan)
     - [Copilot CLI usage](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
     - [Copilot AI-credit usage](https://docs.github.com/en/copilot/how-tos/manage-and-track-spending/monitor-ai-usage)
</workflow>
