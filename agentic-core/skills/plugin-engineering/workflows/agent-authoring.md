---
id: agent-authoring
description: Draft or repair one self-contained VS Code agent from an approved role
  contract.
invoke_for:
- create or repair an agent persona
- define an agent's routing, tools, skills, delegation, or output contract
avoid_for:
- validate-only review of an existing agent
references:
  - ../references/create-agent/references/primitive-selection.md
  - ../references/create-agent/references/ask_questions.md
  - ../references/create-agent/references/delegation_and_invocation.md
  - ../references/create-agent/references/latest-docs.md
  - ../references/create-agent/references/custom_agent.md
  - ../references/create-agent/references/sub_agent.md
  - ../references/create-agent/references/agent-ontology.md
  - ../references/create-agent/references/authoring-patterns.md
  - ../references/create-agent/references/validation.md
  - ../references/create-agent/references/final-checklist.md
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
## Step 1 - Establish the contract.

1. DO consume the assigned `risk_level`; inspect the approved role request and target. Consult `primitive-selection` only for artifact ambiguity and `latest-docs` only when relevant.
2. Resolve material gaps with `ask_questions` and the [question payload](../references/create-agent/assets/ask_questions.json). Consult `delegation_and_invocation`, `custom_agent`, or `sub_agent` only if needed.
   - Capture non-negotiable invariants separately from preferences; use the assigned risk level without reclassifying it.

## Step 2 - Draft one self-contained agent.

1. Fill the [agent template](../references/create-agent/assets/agent-template.md) and optional [workflow fragment](../references/create-agent/assets/workflow.md); replace every square-bracketed value.
   - Keep `<critical_rules>`, `<general_rules>`, and `<risk_assessment>` separate. Use `MUST`/`MUST NOT` for invariants, `SHOULD`/`SHOULD NOT` for preferences, `MAY` for optional behavior, and `DO`/`DO NOT` for local actions.
   - Step 1 consumes the assigned risk level; risk scales evidence, never authority or required approvals.
   - If delegation is needed, include the `agent` tool and only verified, explicit recipients; MUST NOT use wildcard recipients. Omit `agents:` and the `agent` tool when the persona does not delegate.
   - Use exact host-facing MCP `server/tool` names from the available catalog; MUST NOT infer a tool name from a server, capability, or documentation example.
   - Consult [authoring patterns](../references/create-agent/references/authoring-patterns.md) only when discovery, delegation, or output-contract choices remain unclear.
2. Keep the package contract in one `.agent.md`; use `agent-ontology` only for decisions or handoffs.

## Step 3 - Validate and return.

1. Resolve `[agent_file]` to an absolute path. From the repository root, run `PYTHONDONTWRITEBYTECODE=1 python agentic-core/skills/plugin-engineering/references/create-agent/scripts/validate_agent.py --agent-file [agent_file]`.
2. Fix errors; use `validation` and `final-checklist` as needed. Inspect [lint core](../references/create-agent/scripts/agent_lint_core.py) only to diagnose validator behavior.
3. Return the path, role, tools/delegates, one route example, validation result, and unresolved risks.
</workflow>
