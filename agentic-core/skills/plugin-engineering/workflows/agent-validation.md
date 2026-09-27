---
id: agent-validation
description: Review or validate an existing agent without changing its role or artifacts.
invoke_for:
- validate an agent file
- review agent routing, invocation, tools, skill policy, or structure
avoid_for:
- creating or repairing agent content
references:
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
## Step 1 - Inspect the exact agent.

1. Read the `.agent.md` and compare its description, routing, critical/general rules, risk assessment, tool allowlist, invocation fields, delegation, skill policy, workflow, and output contract.
2. Confirm it is a single self-contained runtime file and that referenced delegates and skills exist.

## Step 2 - Run deterministic validation.

1. From the repository root, run `PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python agentic-core/skills/plugin-engineering/references/create-agent/scripts/validate_agent.py --agent-file [agent_file]` using the [agent validator](../references/create-agent/scripts/validate_agent.py).
2. Fix no artifacts in validate-only mode; report diagnostics and consult [validation guidance](../references/create-agent/references/validation.md) only when their meaning is unclear.
   - Inspect the [lint core](../references/create-agent/scripts/agent_lint_core.py) only when the validator's behavior needs diagnosis.

## Step 3 - Report the result.

1. Complete the [final checklist](../references/create-agent/references/final-checklist.md) and return the exact path, validator result, findings, and residual risks.
</workflow>
