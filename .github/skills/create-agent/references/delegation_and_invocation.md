# Delegation And Invocation Guidance

Use this guide when `agent`, `agents:`, `user-invocable`, or `disable-model-invocation` still feel ambiguous.

Rules of thumb:

- If the agent does not delegate, omit `agents:` and remove `agent` from `tools`.
- If the agent delegates, include `agent` in `tools` and keep `agents:` as narrow as possible.
- Use `user-invocable: false` for helper agents that should stay out of the picker but remain callable by other agents.
- Use `disable-model-invocation: true` only when the agent must never be called as a subagent.
- Avoid `agents: [*]` unless broad delegation is intentional and defensible.

Common decisions:

- Single-purpose worker with no handoff: no `agent`, no `agents:`.
- Coordinator that calls specific helpers: include `agent` plus an explicit allowlist in `agents:`.
- Hidden worker used only by orchestrators: `user-invocable: false`.
- User-only specialist that must not be auto-invoked: `disable-model-invocation: true`.# Delegation and invocation guidance

Use this file only when the agent delegates work or when its picker visibility and subagent eligibility are still unclear.

## When to use it

- You are deciding whether to add the `agent` tool.
- You are deciding whether to add `agents:` or whether broad delegation is intentional.
- You are deciding `user-invocable` or `disable-model-invocation`.
- The questionnaire answers mention helper agents, internal-only behavior, or picker visibility.

## Invocation mode mapping

- Visible in picker and invocable as subagent -> usually omit both `user-invocable` and `disable-model-invocation` unless explicit values are required.
- Hidden from picker, subagent only -> set `user-invocable: false`.
- Visible in picker, not invocable as subagent -> set `disable-model-invocation: true`.
- Internal helper: hidden from picker and blocked from subagent use -> set `user-invocable: false` and `disable-model-invocation: true`.

## Delegation mapping

- If the agent does not delegate -> omit `agents:` and remove `agent` from `tools`.
- If the agent delegates to specific helpers -> include `agent` in `tools` and set `agents:` to the explicit allowlist.
- If broad delegation is intentionally required -> use `agents: *`, but treat it as a broad-permission choice that needs explicit justification.
- Never list the current agent in `agents:`.
- Verify each named subagent already exists under `.github/agents/` before you finalize the draft.

## Handoffs

- Use `handoffs` only when the caller benefits from a UI-level transition to another agent.
- A handoff target should refer to an existing agent name.
- Do not add `handoffs` when a short explanation in the output contract is enough.