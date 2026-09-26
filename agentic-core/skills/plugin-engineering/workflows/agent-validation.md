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

## Step 1 - Inspect the exact agent.

1. Read the `.agent.md` and compare its description, routing, critical/general rules, risk assessment, tool allowlist, invocation fields, delegation, skill policy, workflow, and output contract.
2. Confirm it is a single self-contained runtime file and that referenced delegates and skills exist.

## Step 2 - Run deterministic validation.

1. From the repository root, run `PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python agentic-core/skills/plugin-engineering/references/create-agent/scripts/validate_agent.py --agent-file [agent_file]` using the [agent validator](../references/create-agent/scripts/validate_agent.py).
2. Fix no artifacts in validate-only mode; report diagnostics and consult [validation guidance](../references/create-agent/references/validation.md) only when their meaning is unclear.
   - Inspect the [lint core](../references/create-agent/scripts/agent_lint_core.py) only when the validator's behavior needs diagnosis.

## Step 3 - Report the result.

1. Complete the [final checklist](../references/create-agent/references/final-checklist.md) and return the exact path, validator result, findings, and residual risks.
